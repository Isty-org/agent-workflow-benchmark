import { spawn, spawnSync } from "node:child_process";
import { createServer } from "node:http";
import { readFile, stat } from "node:fs/promises";
import { createReadStream, existsSync } from "node:fs";
import { extname, join, normalize, resolve } from "node:path";
import { createConnection, createServer as createNetServer } from "node:net";
import { chromium } from "@playwright/test";

const workspace = resolve(process.env.BENCHMARK_WORKSPACE ?? process.argv[2] ?? "");
if (!workspace || !existsSync(workspace)) throw new Error("BENCHMARK_WORKSPACE is required.");

const outcomes = [];
const browserErrors = [];
let page;
let application;

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

async function check(id, evidence, procedure) {
  try {
    await procedure();
    outcomes.push({ id, passed: true, evidence });
  } catch (error) {
    outcomes.push({ id, passed: false, evidence, error: error instanceof Error ? error.message : String(error) });
  }
}

function getFreePort() {
  return new Promise((resolvePort, reject) => {
    const server = createNetServer();
    server.unref();
    server.on("error", reject);
    server.listen(0, "127.0.0.1", () => {
      const address = server.address();
      const port = typeof address === "object" && address ? address.port : null;
      server.close((error) => error ? reject(error) : resolvePort(port));
    });
  });
}

async function waitForUrl(candidates, output, timeoutMs = 45_000) {
  const deadline = Date.now() + timeoutMs;
  while (Date.now() < deadline) {
    const discovered = [...output.join("\n").matchAll(/https?:\/\/(?:127\.0\.0\.1|localhost):\d+/gu)].map((item) => item[0].replace("localhost", "127.0.0.1"));
    for (const url of [...new Set([...candidates, ...discovered])]) {
      try {
        const response = await fetch(url, { signal: AbortSignal.timeout(1000) });
        if (response.ok) return url;
      } catch {
      }
    }
    await new Promise((resolveWait) => setTimeout(resolveWait, 250));
  }
  throw new Error(`Application did not become ready; outputSha=${Buffer.from(output.join("\n")).toString("base64url").slice(0, 24)}`);
}

function npmInvocation(script, port) {
  const npmArgs = ["run", script, "--", "--host", "127.0.0.1", "--port", String(port)];
  if (process.platform === "win32") return { command: process.env.ComSpec ?? "cmd.exe", args: ["/d", "/s", "/c", "npm", ...npmArgs] };
  return { command: "npm", args: npmArgs };
}

async function startChild(script, port) {
  const output = [];
  const invocation = npmInvocation(script, port);
  const child = spawn(invocation.command, invocation.args, {
    cwd: workspace,
    env: { ...process.env, HOST: "127.0.0.1", PORT: String(port), BROWSER: "none", NODE_ENV: "production" },
    windowsHide: true,
    stdio: ["ignore", "pipe", "pipe"]
  });
  for (const stream of [child.stdout, child.stderr]) stream.on("data", (chunk) => {
    output.push(String(chunk));
    if (output.length > 200) output.splice(0, output.length - 200);
  });
  const exitPromise = new Promise((resolveExit) => child.once("exit", (code, signal) => resolveExit({ code, signal })));
  const ready = await Promise.race([
    waitForUrl([`http://127.0.0.1:${port}`], output),
    exitPromise.then(({ code, signal }) => { throw new Error(`Application exited before readiness (${code ?? signal}).`); })
  ]);
  return {
    url: ready,
    async stop() {
      if (child.exitCode !== null) return;
      if (process.platform === "win32") spawnSync("taskkill.exe", ["/pid", String(child.pid), "/t", "/f"], { windowsHide: true, stdio: "ignore" });
      else child.kill("SIGTERM");
      await Promise.race([exitPromise, new Promise((resolveWait) => setTimeout(resolveWait, 5000))]);
    }
  };
}

function contentType(path) {
  return ({ ".html": "text/html; charset=utf-8", ".js": "text/javascript; charset=utf-8", ".css": "text/css; charset=utf-8", ".json": "application/json; charset=utf-8", ".svg": "image/svg+xml", ".png": "image/png" })[extname(path).toLowerCase()] ?? "application/octet-stream";
}

async function startStatic(root, port) {
  const absoluteRoot = resolve(root);
  const server = createServer(async (request, response) => {
    try {
      const pathname = decodeURIComponent(new URL(request.url ?? "/", `http://127.0.0.1:${port}`).pathname);
      const candidate = resolve(absoluteRoot, `.${normalize(pathname)}`);
      if (!candidate.toLowerCase().startsWith(absoluteRoot.toLowerCase())) throw new Error("unsafe path");
      let path = candidate;
      if (!existsSync(path) || (await stat(path)).isDirectory()) path = join(path, "index.html");
      if (!existsSync(path)) path = join(absoluteRoot, "index.html");
      response.writeHead(200, { "content-type": contentType(path), "cache-control": "no-store" });
      createReadStream(path).pipe(response);
    } catch {
      response.writeHead(404).end("Not found");
    }
  });
  await new Promise((resolveListen, reject) => { server.once("error", reject); server.listen(port, "127.0.0.1", resolveListen); });
  return { url: `http://127.0.0.1:${port}`, stop: () => new Promise((resolveClose, reject) => server.close((error) => error ? reject(error) : resolveClose())) };
}

async function startApplication(preferredPort) {
  const port = preferredPort ?? await getFreePort();
  const packagePath = join(workspace, "package.json");
  if (existsSync(packagePath)) {
    const pkg = JSON.parse(await readFile(packagePath, "utf8"));
    const script = ["preview", "start", "dev"].find((candidate) => pkg.scripts?.[candidate]);
    if (script) return { ...(await startChild(script, port)), port };
  }
  const staticRoot = [join(workspace, "dist"), join(workspace, "build"), workspace].find((candidate) => existsSync(join(candidate, "index.html")));
  if (staticRoot) return { ...(await startStatic(staticRoot, port)), port };
  throw new Error("No reproducible local web start could be discovered.");
}

async function firstVisible(candidates, role) {
  for (const candidate of candidates) {
    if (await candidate.count() > 0 && await candidate.first().isVisible()) return candidate.first();
  }
  throw new Error(`${role} control was not found by accessible name or placeholder.`);
}

async function controls() {
  const title = await firstVisible([
    page.getByLabel(/назван(?:ие|ия)/iu),
    page.getByPlaceholder(/назван(?:ие|ия)/iu),
    page.locator('input[name*="title" i]')
  ], "title");
  const author = await firstVisible([
    page.getByLabel(/автор/iu),
    page.getByPlaceholder(/автор/iu),
    page.locator('input[name*="author" i]')
  ], "author");
  const submit = await firstVisible([
    page.getByRole("button", { name: /добавить|сохранить/iu }),
    page.locator('button[type="submit"],input[type="submit"]')
  ], "submit");
  return { title, author, submit };
}

async function addBook(titleValue, authorValue) {
  const form = await controls();
  await form.title.fill(titleValue);
  await form.author.fill(authorValue);
  await form.submit.click();
  await page.getByText(titleValue, { exact: true }).first().waitFor({ state: "visible", timeout: 5000 });
}

async function bookContainer(titleValue) {
  let candidate = page.getByText(titleValue, { exact: true }).first();
  await candidate.waitFor({ state: "visible" });
  for (let depth = 0; depth < 7; depth += 1) {
    const controlsCount = await candidate.locator("button,select,[draggable=true]").count();
    const text = await candidate.innerText().catch(() => "");
    if (controlsCount > 0 && text.includes(titleValue)) return candidate;
    candidate = candidate.locator("..");
  }
  return page.getByText(titleValue, { exact: true }).first().locator("..");
}

async function appearsUnderStatus(titleValue, status) {
  const headings = page.getByRole("heading", { name: new RegExp(`^${status}$`, "iu") });
  for (let index = 0; index < await headings.count(); index += 1) {
    let region = headings.nth(index);
    for (let depth = 0; depth < 6; depth += 1) {
      region = region.locator("..");
      if (await region.getByText(titleValue, { exact: true }).count() > 0) return true;
    }
  }
  const card = await bookContainer(titleValue);
  return (await card.innerText()).toLocaleLowerCase("ru-RU").includes(status.toLocaleLowerCase("ru-RU"));
}

async function moveBook(titleValue, status) {
  let card = await bookContainer(titleValue);
  const selects = card.locator("select");
  for (let index = 0; index < await selects.count(); index += 1) {
    const select = selects.nth(index);
    const options = await select.locator("option").allTextContents();
    const optionIndex = options.findIndex((item) => item.trim().toLocaleLowerCase("ru-RU") === status.toLocaleLowerCase("ru-RU"));
    if (optionIndex >= 0) {
      const value = await select.locator("option").nth(optionIndex).getAttribute("value");
      await select.selectOption(value ?? { label: options[optionIndex] });
      await page.waitForTimeout(150);
      assert(await appearsUnderStatus(titleValue, status), `book did not move to ${status}`);
      return;
    }
  }
  const direct = card.getByRole("button", { name: new RegExp(`^(?:${status}|начать читать|завершить|далее)$`, "iu") });
  if (await direct.count() > 0) {
    await direct.first().click();
    await page.waitForTimeout(150);
    assert(await appearsUnderStatus(titleValue, status), `book did not move to ${status}`);
    return;
  }
  const opener = card.getByRole("button", { name: /статус|переместить|изменить/iu });
  if (await opener.count() > 0) {
    await opener.first().click();
    const option = page.getByRole("menuitem", { name: new RegExp(`^${status}$`, "iu") }).or(page.getByRole("option", { name: new RegExp(`^${status}$`, "iu") }));
    if (await option.count() > 0) {
      await option.first().click();
      await page.waitForTimeout(150);
      assert(await appearsUnderStatus(titleValue, status), `book did not move to ${status}`);
      return;
    }
  }
  const draggable = card.locator("[draggable=true]").first().or(card);
  const target = page.getByRole("heading", { name: new RegExp(`^${status}$`, "iu") }).first().locator("..");
  if (await target.count() > 0) {
    await draggable.dragTo(target);
    await page.waitForTimeout(250);
    assert(await appearsUnderStatus(titleValue, status), `book did not move to ${status}`);
    return;
  }
  throw new Error(`No usable state transition control for ${status}.`);
}

const browser = await chromium.launch({ headless: true });
try {
  application = await startApplication();
  const context = await browser.newContext({ locale: "ru-RU" });
  page = await context.newPage();
  page.on("pageerror", (error) => browserErrors.push(error.message));
  await page.goto(application.url, { waitUntil: "domcontentloaded" });

  await check("N3-A02", "three requested Russian states are visible", async () => {
    for (const state of ["Хочу прочитать", "Читаю", "Прочитано"]) await page.getByText(state, { exact: true }).first().waitFor({ state: "visible" });
  });

  await check("N3-A01", "accessible title/author form adds a visible book", async () => {
    await addBook("Мастер и Маргарита", "Михаил Булгаков");
    await page.getByText("Михаил Булгаков", { exact: true }).first().waitFor({ state: "visible" });
  });

  await check("N3-A03", "one book moves through reading and completed states immediately", async () => {
    await moveBook("Мастер и Маргарита", "Читаю");
    await moveBook("Мастер и Маргарита", "Прочитано");
  });

  await check("N3-A04", "book and status survive browser reload", async () => {
    await page.reload({ waitUntil: "domcontentloaded" });
    await page.getByText("Мастер и Маргарита", { exact: true }).first().waitFor({ state: "visible" });
    assert(await appearsUnderStatus("Мастер и Маргарита", "Прочитано"), "status did not survive reload");
  });

  await check("N3-A05", "book and status survive full application stop and restart", async () => {
    const previousUrl = application.url;
    const restartPort = application.port;
    await application.stop();
    application = await startApplication(restartPort);
    await page.goto(application.url ?? previousUrl, { waitUntil: "domcontentloaded" });
    await page.getByText("Мастер и Маргарита", { exact: true }).first().waitFor({ state: "visible" });
    assert(await appearsUnderStatus("Мастер и Маргарита", "Прочитано"), "status did not survive application restart");
  });

  await check("N3-A06", "multiple books remain independent after one state change", async () => {
    await addBook("Пикник на обочине", "Аркадий и Борис Стругацкие");
    await moveBook("Пикник на обочине", "Читаю");
    assert(await appearsUnderStatus("Пикник на обочине", "Читаю"), "second book state is wrong");
    assert(await appearsUnderStatus("Мастер и Маргарита", "Прочитано"), "first book state changed unexpectedly");
  });

  await check("N3-A07", "empty required values create no book and expose validation", async () => {
    const before = await page.getByText("Мастер и Маргарита", { exact: true }).count() + await page.getByText("Пикник на обочине", { exact: true }).count();
    const form = await controls();
    await form.title.fill("");
    await form.author.fill("");
    await form.submit.click();
    const after = await page.getByText("Мастер и Маргарита", { exact: true }).count() + await page.getByText("Пикник на обочине", { exact: true }).count();
    const invalid = await form.title.evaluate((element) => !element.checkValidity()) || await form.author.evaluate((element) => !element.checkValidity());
    const feedback = await page.getByText(/обязател|укажите|заполните|нужно/iu).count() > 0;
    assert(before === after && (invalid || feedback), "invalid submission lacked understandable validation");
  });

  await check("N3-A08", "primary product copy and controls are Russian", async () => {
    const body = await page.locator("body").innerText();
    for (const value of ["Хочу прочитать", "Читаю", "Прочитано"]) assert(body.includes(value), `missing Russian copy: ${value}`);
    await controls();
  });

  await context.close();
} finally {
  if (application) await application.stop().catch(() => {});
  await browser.close();
}

console.log(JSON.stringify({
  schemaVersion: 3,
  scenario: "new",
  checks: outcomes,
  smoke: { passed: outcomes.some((item) => item.id === "N3-A01" && item.passed) && browserErrors.length === 0, browserErrors: browserErrors.length },
  passed: outcomes.every((item) => item.passed) && browserErrors.length === 0
}));
