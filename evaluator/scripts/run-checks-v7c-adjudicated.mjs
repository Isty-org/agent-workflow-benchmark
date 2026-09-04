import { randomUUID } from "node:crypto";
import { spawnSync } from "node:child_process";
import { mkdir, readFile, rm, writeFile } from "node:fs/promises";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { applyV7cLargeSearchCorrection } from "../harness-v7c-adjudicated/large-search-overlay.mjs";

const scriptsRoot = dirname(fileURLToPath(import.meta.url));
const evaluatorRoot = resolve(scriptsRoot, "..");
const token = randomUUID();
const temporaryHarness = join(evaluatorRoot, `.harness-v7c-adjudicated-${token}`);
const temporaryRunner = join(scriptsRoot, `.run-checks-v7c-adjudicated-${token}.mjs`);

function fail(message) {
  throw new Error(message);
}

const argv = process.argv.slice(2);
const scenarioIndex = argv.indexOf("--scenario");
if (scenarioIndex < 0 || argv[scenarioIndex + 1] !== "large") {
  fail("The V7c supplemental evaluator supports only --scenario large.");
}

try {
  const frozenHarnessPath = join(evaluatorRoot, "harness-v7", "large-search.hidden.cs");
  const frozenHarness = await readFile(frozenHarnessPath, "utf8");
  const correctedHarness = applyV7cLargeSearchCorrection(frozenHarness);
  await mkdir(temporaryHarness, { recursive: false });
  await writeFile(join(temporaryHarness, "large-search.hidden.cs"), correctedHarness, { encoding: "utf8", mode: 0o600 });

  const sourceRunner = await readFile(join(scriptsRoot, "run-checks-v7.mjs"), "utf8");
  const marker = 'const harnessRoot = join(evaluatorRoot, "harness-v7");';
  if (!sourceRunner.includes(marker)) fail("Could not locate the frozen V7 harness-root marker.");
  const projectedRunner = sourceRunner
    .replace(marker, `const harnessRoot = ${JSON.stringify(resolve(temporaryHarness))};`)
    .replace('mkdtemp(join(tmpdir(), "benchmark-v7-checks-"))', 'mkdtemp(join(tmpdir(), "benchmark-v7c-adjudicated-"))')
    .replace('normalized.startsWith(join(resolve(tmpdir()), "benchmark-v7-checks-"))', 'normalized.startsWith(join(resolve(tmpdir()), "benchmark-v7c-adjudicated-"))');
  await writeFile(temporaryRunner, projectedRunner, { encoding: "utf8", mode: 0o600 });

  const result = spawnSync(process.execPath, [temporaryRunner, ...argv], {
    cwd: process.cwd(),
    encoding: "utf8",
    stdio: ["ignore", "pipe", "pipe"],
    maxBuffer: 128 * 1024 * 1024,
  });
  process.stdout.write(result.stdout ?? "");
  process.stderr.write(result.stderr ?? "");
  process.exitCode = result.status ?? 1;
} finally {
  const normalizedHarness = resolve(temporaryHarness);
  const normalizedRunner = resolve(temporaryRunner);
  if (dirname(normalizedHarness) !== evaluatorRoot || !normalizedHarness.startsWith(join(evaluatorRoot, ".harness-v7c-adjudicated-"))) {
    fail(`Unsafe supplemental harness cleanup path: ${normalizedHarness}`);
  }
  if (dirname(normalizedRunner) !== resolve(scriptsRoot) || !normalizedRunner.startsWith(join(resolve(scriptsRoot), ".run-checks-v7c-adjudicated-"))) {
    fail(`Unsafe supplemental runner cleanup path: ${normalizedRunner}`);
  }
  await rm(normalizedHarness, { recursive: true, force: true });
  await rm(normalizedRunner, { force: true });
}

