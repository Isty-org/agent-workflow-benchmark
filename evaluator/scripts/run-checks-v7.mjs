import { createHash } from "node:crypto";
import { spawnSync } from "node:child_process";
import { existsSync } from "node:fs";
import { copyFile, cp, mkdir, mkdtemp, readFile, rm, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { basename, dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const evaluatorRoot = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const harnessRoot = join(evaluatorRoot, "harness-v7");
const hiddenIds = {
  new: Array.from({ length: 8 }, (_, index) => `N3-A${String(index + 1).padStart(2, "0")}`),
  small: Array.from({ length: 10 }, (_, index) => `S3-A${String(index + 1).padStart(2, "0")}`),
  large: Array.from({ length: 10 }, (_, index) => `L3-A${String(index + 1).padStart(2, "0")}`)
};

function fail(message) { throw new Error(message); }
function sha256(value) { return createHash("sha256").update(value).digest("hex"); }
function tail(value, maximum = 5000) { const text = value.replace(/\r\n/gu, "\n"); return text.length <= maximum ? text : text.slice(-maximum); }
function parseArgs(argv) {
  const args = {};
  for (let index = 0; index < argv.length; index += 2) {
    if (!argv[index]?.startsWith("--") || argv[index + 1] === undefined) fail(`Invalid argument: ${argv[index] ?? "<missing>"}`);
    args[argv[index].slice(2)] = argv[index + 1];
  }
  return args;
}
function safeStructuredOutput(stdout) {
  for (const line of stdout.trim().split(/\r?\n/u).reverse()) {
    try {
      const value = JSON.parse(line);
      if (value?.schemaVersion !== 3 || !Array.isArray(value.checks)) continue;
      return {
        scenario: value.scenario,
        passed: value.passed === true,
        smoke: value.smoke ? { passed: value.smoke.passed === true, browserErrors: Number(value.smoke.browserErrors ?? 0) } : null,
        checks: value.checks.map((item) => ({ id: item.id, passed: item.passed === true, evidence: String(item.evidence ?? ""), ...(item.error ? { error: String(item.error).slice(0, 1000) } : {}) }))
      };
    } catch {
    }
  }
  return null;
}
function run(executable, args, cwd, env = {}) {
  const startedAt = new Date().toISOString(); const started = performance.now();
  let actualExecutable = executable; let actualArgs = args;
  if (process.platform === "win32" && basename(executable).toLowerCase() === "npm.cmd") {
    const candidates = [process.env.npm_execpath, join(dirname(process.execPath), "node_modules", "npm", "bin", "npm-cli.js")].filter(Boolean);
    const npmCli = candidates.find((candidate) => existsSync(candidate));
    if (!npmCli) fail("npm-cli.js was not found next to the active Node.js runtime.");
    actualExecutable = process.execPath; actualArgs = [npmCli, ...args];
  }
  const result = spawnSync(actualExecutable, actualArgs, {
    cwd,
    encoding: "utf8",
    env: { ...process.env, ...env },
    shell: false,
    timeout: 30 * 60 * 1000,
    maxBuffer: 128 * 1024 * 1024
  });
  const stdout = result.stdout ?? ""; const stderr = result.stderr ?? "";
  return {
    command: [basename(executable), ...args.map((item) => item.startsWith(cwd) ? `<scratch>${item.slice(cwd.length)}` : item.startsWith(harnessRoot) ? `<harness>${item.slice(harnessRoot.length)}` : item)],
    startedAt,
    completedAt: new Date().toISOString(),
    durationMs: Math.round(performance.now() - started),
    exitCode: result.status,
    signal: result.signal,
    timedOut: result.error?.code === "ETIMEDOUT",
    spawnError: result.error ? { code: result.error.code ?? null, message: result.error.message } : null,
    stdoutSha256: sha256(stdout),
    stderrSha256: sha256(stderr),
    stdoutTail: tail(stdout),
    stderrTail: tail(stderr),
    structuredOutput: safeStructuredOutput(stdout),
    _combinedForParser: `${stdout}\n${stderr}`
  };
}
function git(cwd, args) {
  const result = run("git", args, cwd);
  if (result.exitCode !== 0) fail(`git ${args.join(" ")} failed: ${result.stderrTail}`);
  return result.stdoutTail.trim();
}
function missing(name, reason) { return { name, required: true, missing: true, reason }; }
async function copyWorkspace(source, destination) {
  const excluded = new Set([".git", "node_modules", "bin", "obj", "artifacts", ".benchmark-hidden-v3"]);
  await cp(source, destination, { recursive: true, force: false, filter: (path) => path === source || !excluded.has(basename(path)) });
}
function databasePort(blindId) { return 32000 + (Number.parseInt(blindId.slice(3), 16) % 20000); }
async function prepareHarness(scenario, scratch, blindId) {
  if (scenario === "small") {
    const composePath = join(scratch, "docker-compose.integration.yml");
    let compose = await readFile(composePath, "utf8");
    compose = compose
      .replace("container_name: telegram-gateway-integration-postgres", `container_name: benchmark-v3-${blindId}-postgres`)
      .replace('"55432:5432"', `"${databasePort(blindId)}:5432"`);
    if (compose.includes("telegram-gateway-integration-postgres") || compose.includes('"55432:5432"')) fail("Small-project Docker isolation projection failed.");
    await writeFile(composePath, compose, "utf8");
    return ["docker-compose.integration.yml (scratch-only port/name isolation)"];
  }
  if (scenario !== "large") return [];
  const rootMarker = join(scratch, "specs", "BOARD.md");
  await mkdir(dirname(rootMarker), { recursive: true });
  await writeFile(rootMarker, "# Evaluator repository-root marker\n", "utf8");
  const target = join(scratch, "tests", "IsTranscribe.Desktop.Tests", "BenchmarkHiddenSearchTests.cs");
  if (!existsSync(dirname(target))) fail("Large-project desktop test assembly is missing.");
  await copyFile(join(harnessRoot, "large-search.hidden.cs"), target);
  return ["specs/BOARD.md (scratch-only neutral repository-root marker)", "tests/IsTranscribe.Desktop.Tests/BenchmarkHiddenSearchTests.cs"];
}
async function recipe(scenario, scratch, temporary, blindId) {
  const npm = process.platform === "win32" ? "npm.cmd" : "npm";
  if (scenario === "small") {
    const port = databasePort(blindId);
    const projectName = `benchmark-v7-${blindId}`;
    const db = `postgresql://postgres:postgres@localhost:${port}/telegram_gateway_integration?schema=public`;
    return [
      { name: "unit-tests", executable: npm, args: ["test"], required: true },
      { name: "build", executable: npm, args: ["run", "build"], required: true },
      { name: "integration-db-up", executable: "docker", args: ["compose", "-p", projectName, "-f", "docker-compose.integration.yml", "up", "-d", "--wait"], required: true },
      { name: "integration-migrate", executable: npm, args: ["exec", "--", "prisma", "migrate", "deploy"], env: { DATABASE_URL: db, INTEGRATION_DATABASE_URL: db }, requires: ["integration-db-up"], required: true },
      { name: "integration-tests", executable: npm, args: ["run", "test:integration"], env: { INTEGRATION_DATABASE_URL: db }, requires: ["integration-migrate"], required: true },
      { name: "hidden-api", executable: npm, args: ["exec", "--", "tsx", join(harnessRoot, "small-api.hidden.ts")], env: { BENCHMARK_WORKSPACE: scratch, DATABASE_URL: db, INTEGRATION_DATABASE_URL: db }, requires: ["integration-migrate"], required: true },
      { name: "integration-db-down", executable: "docker", args: ["compose", "-p", projectName, "-f", "docker-compose.integration.yml", "down", "-v"], alwaysRun: true, required: true }
    ];
  }
  if (scenario === "large") return [
    { name: "desktop-tests", executable: "dotnet", args: ["test", "tests/IsTranscribe.Desktop.Tests/IsTranscribe.Desktop.Tests.csproj", "--configuration", "Release", "--nologo", "--filter", "FullyQualifiedName!~BenchmarkHiddenSearchTests"], required: true },
    { name: "desktop-build", executable: "dotnet", args: ["build", "src/IsTranscribe.Desktop/IsTranscribe.Desktop.csproj", "--configuration", "Release", "--nologo"], required: true },
    { name: "hidden-search", executable: "dotnet", args: ["test", "tests/IsTranscribe.Desktop.Tests/IsTranscribe.Desktop.Tests.csproj", "--configuration", "Release", "--nologo", "--filter", "FullyQualifiedName~BenchmarkHiddenSearchTests", "--logger", "console;verbosity=normal"], required: true },
    { name: "visual-smoke", executable: "dotnet", args: ["run", "--project", "tools/IsTranscribe.VisualReview/IsTranscribe.VisualReview.csproj", "--configuration", "Release", "--", "--output", join(temporary, "visual-review")], required: true },
    { name: "dotnet-build-server-shutdown", executable: "dotnet", args: ["build-server", "shutdown"], alwaysRun: true, required: false }
  ];
  const packagePath = join(scratch, "package.json");
  if (existsSync(packagePath)) {
    const pkg = JSON.parse(await readFile(packagePath, "utf8"));
    const tests = pkg.scripts?.test ? { name: "tests", executable: npm, args: ["test"], required: true } : missing("tests", "package.json has no test script");
    const build = pkg.scripts?.build ? { name: "build", executable: npm, args: ["run", "build"], required: true }
      : pkg.scripts?.typecheck ? { name: "typecheck", executable: npm, args: ["run", "typecheck"], required: true }
        : missing("build", "package.json has neither build nor typecheck script");
    return [tests, build, { name: "hidden-browser", executable: process.execPath, args: [join(harnessRoot, "new-ui.hidden.mjs")], env: { BENCHMARK_WORKSPACE: scratch }, required: true }];
  }
  if (existsSync(join(scratch, "pyproject.toml"))) return [
    { name: "tests", executable: "uv", args: ["run", "pytest"], required: true },
    { name: "build", executable: "uv", args: ["build"], required: true },
    { name: "hidden-browser", executable: process.execPath, args: [join(harnessRoot, "new-ui.hidden.mjs")], env: { BENCHMARK_WORKSPACE: scratch }, required: true }
  ];
  if (existsSync(join(scratch, "index.html"))) return [missing("tests", "static project has no direct test command"), missing("build", "static project has no build command"), { name: "hidden-browser", executable: process.execPath, args: [join(harnessRoot, "new-ui.hidden.mjs")], env: { BENCHMARK_WORKSPACE: scratch }, required: true }];
  return [missing("tests", "no test recipe discovered"), missing("build", "no build recipe discovered"), missing("hidden-browser", "no runnable web application discovered")];
}
function executeRecipe(items, scratch) {
  const results = []; const status = new Map();
  for (const item of items) {
    const unavailable = item.requires?.find((dependency) => status.get(dependency) !== true);
    let result;
    if (item.missing) result = { name: item.name, missing: true, required: item.required, reason: item.reason, exitCode: null };
    else if (unavailable && !item.alwaysRun) result = { name: item.name, skipped: true, required: item.required, reason: `required step failed: ${unavailable}`, exitCode: null };
    else result = { name: item.name, required: item.required, ...run(item.executable, item.args, scratch, item.env) };
    results.push(result); status.set(item.name, !result.missing && !result.skipped && result.exitCode === 0);
  }
  return results;
}
function largeFunctional(results) {
  const command = results.find((item) => item.name === "hidden-search"); const output = command?._combinedForParser ?? "";
  return hiddenIds.large.map((id) => {
    const token = id.replaceAll("-", "_");
    const passed = new RegExp(`(?:Passed|Пройден)\\s+[^\\r\\n]*${token}_`, "iu").test(output);
    const failed = new RegExp(`(?:Failed|Не пройден|\\[FAIL\\])[^\\r\\n]*${token}_`, "iu").test(output);
    return { id, passed: passed && !failed, evidence: passed ? "harness-owned xUnit behavior check passed" : failed ? "harness-owned xUnit behavior check failed" : "harness-owned xUnit result was not emitted" };
  });
}
function resultPassed(results, name) {
  const item = results.find((candidate) => candidate.name === name);
  return Boolean(item && !item.missing && !item.skipped && item.exitCode === 0);
}
function objectiveChecks(scenario, results) {
  const hidden = results.find((item) => ["hidden-browser", "hidden-api"].includes(item.name))?.structuredOutput;
  const functional = scenario === "large" ? largeFunctional(results)
    : hiddenIds[scenario].map((id) => hidden?.checks.find((item) => item.id === id) ?? { id, passed: false, evidence: "harness did not emit this check" });
  const regression = scenario === "new" ? [
    { id: "N3-B01", passed: resultPassed(results, "tests"), evidence: "direct project test command" },
    { id: "N3-B02", passed: resultPassed(results, "build") || resultPassed(results, "typecheck"), evidence: "documented build or type/package check" },
    { id: "N3-B03", passed: resultPassed(results, "hidden-browser") && hidden?.smoke?.passed === true, evidence: "real local start and Chromium smoke" }
  ] : scenario === "small" ? [
    { id: "S3-B01", passed: resultPassed(results, "unit-tests"), evidence: "npm test" },
    { id: "S3-B02", passed: resultPassed(results, "build"), evidence: "npm run build" },
    { id: "S3-B03", passed: resultPassed(results, "integration-tests") && resultPassed(results, "hidden-api"), evidence: "real PostgreSQL integration and hidden API harness" }
  ] : [
    { id: "L3-B01", passed: resultPassed(results, "desktop-tests") && resultPassed(results, "hidden-search"), evidence: "desktop tests plus harness-owned search tests" },
    { id: "L3-B02", passed: resultPassed(results, "desktop-build"), evidence: "desktop project build" },
    { id: "L3-B03", passed: resultPassed(results, "visual-smoke"), evidence: "Avalonia headless render/load smoke" }
  ];
  return [...functional, ...regression];
}
function sanitizeResults(results) { return results.map(({ _combinedForParser, ...item }) => item); }
async function setupCommands(scenario, scratch) {
  const npm = process.platform === "win32" ? "npm.cmd" : "npm";
  if ((scenario === "small" || scenario === "new") && existsSync(join(scratch, "package-lock.json"))) {
    const install = { name: "dependency-install", ...run(npm, ["ci"], scratch) }; const values = [install];
    if (scenario === "small" && install.exitCode === 0) values.push({ name: "prisma-generate", ...run(npm, ["run", "prisma:generate"], scratch) });
    return values;
  }
  return [];
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  if (!/^vz-[0-9a-f]{6}$/u.test(args.blind ?? "")) fail("--blind vz-xxxxxx is required.");
  if (!["new", "small", "large"].includes(args.scenario)) fail("--scenario new|small|large is required.");
  const workspace = resolve(args.workspace ?? ""); const output = resolve(args.output ?? "");
  if (!existsSync(join(workspace, ".git"))) fail("Workspace is not a Git worktree.");
  if (git(workspace, ["remote"])) fail("Blind workspace has an unexpected remote.");
  const head = git(workspace, ["rev-parse", "HEAD"]); const tree = git(workspace, ["rev-parse", "HEAD^{tree}"]); const status = git(workspace, ["status", "--porcelain=v1"]);
  const stateFingerprint = sha256(JSON.stringify({ head, tree, status }));
  const temporary = await mkdtemp(join(tmpdir(), "benchmark-v7-checks-")); const scratch = join(temporary, "workspace");
  try {
    await copyWorkspace(workspace, scratch);
    const projectedHarnessFiles = await prepareHarness(args.scenario, scratch, args.blind);
    const setup = await setupCommands(args.scenario, scratch);
    const commands = await recipe(args.scenario, scratch, temporary, args.blind); const repetitions = [];
    for (let repetition = 1; repetition <= 3; repetition += 1) {
      const rawResults = executeRecipe(commands, scratch); const checks = objectiveChecks(args.scenario, rawResults);
      repetitions.push({ repetition, stateFingerprint, results: sanitizeResults(rawResults), checks, passed: checks.every((item) => item.passed) && rawResults.filter((item) => item.required).every((item) => !item.missing && !item.skipped && item.exitCode === 0) });
    }
    const after = { head: git(workspace, ["rev-parse", "HEAD"]), tree: git(workspace, ["rev-parse", "HEAD^{tree}"]), status: git(workspace, ["status", "--porcelain=v1"]) };
    const statePreserved = after.head === head && after.tree === tree && after.status === status;
    const record = { schemaVersion: 3, blindId: args.blind, scenario: args.scenario, checkedAt: new Date().toISOString(), workspaceCommit: head, workspaceTree: tree, stateFingerprint, scratchIsolated: true, projectedHarnessFiles, setup: sanitizeResults(setup), repetitions, passed: setup.every((item) => item.exitCode === 0) && repetitions.every((item) => item.passed) && statePreserved, statePreserved };
    await mkdir(dirname(output), { recursive: true }); await writeFile(output, `${JSON.stringify(record, null, 2)}\n`, "utf8");
    console.log(JSON.stringify({ output, passed: record.passed, repetitions: repetitions.length, statePreserved, scratchIsolated: true })); if (!record.passed) process.exitCode = 1;
  } finally {
    const normalized = resolve(temporary);
    if (dirname(normalized) !== resolve(tmpdir()) || !normalized.startsWith(join(resolve(tmpdir()), "benchmark-v7-checks-"))) fail("Unsafe checker scratch cleanup target.");
    await rm(normalized, { recursive: true, force: true, maxRetries: 20, retryDelay: 250 });
  }
}

main().catch((error) => { console.error(error.message); process.exitCode = 1; });
