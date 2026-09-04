import { createHash } from "node:crypto";
import { existsSync } from "node:fs";
import { readFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const evaluatorRoot = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const benchmarkRoot = resolve(evaluatorRoot, "..");
const manifestPath = resolve(benchmarkRoot, "..", "..", "manifests", "benchmark-v7-luna-xhigh-n3-2026-09-01.json");
const categoryMaximums = { functional: 50, regression: 20, architecture: 20, scope: 10 };
const forbiddenRecordKeys = ["condition", "usage", "thread", "transcript", "method", "setupMethod", "fidelity", "usability"];

function fail(message) { throw new Error(message); }
async function readJson(path) { return JSON.parse(await readFile(path, "utf8")); }
function canonicalHash(text) { return createHash("sha256").update(text.replace(/\r\n/gu, "\n"), "utf8").digest("hex"); }
function parseArgs(argv) {
  const args = { command: argv[0] };
  for (let index = 1; index < argv.length; index += 2) {
    const key = argv[index];
    if (!key?.startsWith("--") || argv[index + 1] === undefined) fail(`Invalid argument: ${key ?? "<missing>"}`);
    args[key.slice(2)] = argv[index + 1];
  }
  return args;
}

export async function loadV3Contract(scenario) {
  if (!["new", "small", "large"].includes(scenario)) fail(`Unknown scenario: ${scenario}`);
  const path = resolve(evaluatorRoot, "contracts-v3", `${scenario}.json`);
  const text = await readFile(path, "utf8");
  const contract = JSON.parse(text);
  const ids = new Set();
  const totals = { functional: 0, regression: 0, architecture: 0, scope: 0 };
  for (const check of contract.checks ?? []) {
    if (!/^([NSL])3-[ABCD]\d{2}$/u.test(check.id) || ids.has(check.id)) fail(`Invalid or duplicate check ID: ${check.id}`);
    if (!(check.category in totals) || !Number.isInteger(check.maxPoints) || check.maxPoints <= 0) fail(`Invalid check: ${check.id}`);
    if (!['binary', 'review'].includes(check.scoring)) fail(`Invalid scoring in ${check.id}`);
    ids.add(check.id);
    totals[check.category] += check.maxPoints;
  }
  for (const [category, maximum] of Object.entries(categoryMaximums)) if (totals[category] !== maximum) fail(`${scenario}.${category} sums to ${totals[category]}, expected ${maximum}.`);
  return { contract, sha256: canonicalHash(text) };
}

function validateReviewPasses(record, reviewChecks) {
  if (!Array.isArray(record.reviewPasses) || record.reviewPasses.length < 2 || record.reviewPasses.length > 3) fail("Two or three blind review passes are required.");
  const totals = [];
  const pointsByPass = [];
  for (const pass of record.reviewPasses) {
    if (!pass.reviewerId || !Array.isArray(pass.checks) || pass.checks.length !== reviewChecks.length) fail("Review pass is incomplete.");
    const results = new Map(pass.checks.map((item) => [item.id, item]));
    if (results.size !== reviewChecks.length) fail("Review pass has duplicate checks.");
    const points = {};
    let total = 0;
    for (const check of reviewChecks) {
      const item = results.get(check.id);
      if (!Number.isInteger(item?.pointsAwarded) || item.pointsAwarded < 0 || item.pointsAwarded > check.maxPoints) fail(`Invalid review points: ${check.id}`);
      if (!Array.isArray(item.evidence) || item.evidence.length === 0) fail(`Review evidence is missing: ${check.id}`);
      points[check.id] = item.pointsAwarded;
      total += item.pointsAwarded;
    }
    if (pass.total !== total) fail(`Review pass total mismatch: ${pass.reviewerId}`);
    totals.push(total);
    pointsByPass.push(points);
  }
  const needsThird = Math.abs(totals[0] - totals[1]) > 4;
  if (needsThird !== (record.reviewPasses.length === 3)) fail(needsThird ? "A third review pass is required." : "A third review pass is not permitted.");
  return Object.fromEntries(reviewChecks.map((check) => {
    const values = pointsByPass.map((points) => points[check.id]).sort((a, b) => a - b);
    return [check.id, values.length === 2 ? Math.round((values[0] + values[1]) / 2) : values[1]];
  }));
}

export async function validateV3Evaluation(record) {
  if (!record || typeof record !== "object" || Array.isArray(record)) fail("Evaluation must be an object.");
  for (const key of forbiddenRecordKeys) if (key in record) fail(`Blind evaluation contains forbidden field: ${key}`);
  const manifest = await readJson(manifestPath);
  const cell = manifest.cells.find((candidate) => candidate.blindId === record.blindId);
  const scenario = cell?.scenario?.replace("-project", "");
  if (!cell || scenario !== record.scenario) fail("Blind ID/scenario mismatch.");
  if (record.schemaVersion !== 3 || record.benchmarkId !== manifest.benchmarkId) fail("Evaluation version/benchmark mismatch.");
  if (record.phase !== "first_pass" || record.evaluatorVersion !== "3.0.0" || record.blind !== true) fail("Evaluation phase/version/blindness marker is invalid.");
  if (!/^[0-9a-f]{40}$/u.test(record.harnessCommit ?? "") || !/^[0-9a-f]{40}$/u.test(record.workspaceCommit ?? "") || !/^[0-9a-f]{40}$/u.test(record.setupCommit ?? "")) fail("Evaluation commits are invalid.");
  const { contract, sha256 } = await loadV3Contract(record.scenario);
  if (record.contractSha256 !== sha256) fail("Evaluation contract hash mismatch.");
  if (!Array.isArray(record.checkRepetitions) || record.checkRepetitions.length !== 3) fail("Exactly three hidden-check repetitions are required.");
  if (new Set(record.checkRepetitions.map((item) => item.stateFingerprint)).size !== 1) fail("Hidden checks did not use one immutable state.");
  if (!Array.isArray(record.checks) || record.checks.length !== contract.checks.length) fail("Evaluation check count mismatch.");
  const results = new Map(record.checks.map((item) => [item.id, item]));
  if (results.size !== record.checks.length) fail("Duplicate evaluation results.");
  const reviewChecks = contract.checks.filter((check) => check.scoring === "review");
  const expectedReview = validateReviewPasses(record, reviewChecks);
  const categories = { functional: 0, regression: 0, architecture: 0, scope: 0 };
  for (const check of contract.checks) {
    const result = results.get(check.id);
    if (!result || result.maxPoints !== check.maxPoints || !Number.isInteger(result.pointsAwarded)) fail(`Invalid points in ${check.id}`);
    if (result.pointsAwarded < 0 || result.pointsAwarded > check.maxPoints) fail(`Points out of range in ${check.id}`);
    if (check.scoring === "binary" && ![0, check.maxPoints].includes(result.pointsAwarded)) fail(`Binary check has partial score: ${check.id}`);
    if (check.scoring === "review" && result.pointsAwarded !== expectedReview[check.id]) fail(`Review aggregation mismatch: ${check.id}`);
    if (!["pass", "fail", "partial"].includes(result.status)) fail(`Invalid status in ${check.id}`);
    if ((result.status === "pass") !== (result.pointsAwarded === check.maxPoints)) fail(`Status/points mismatch in ${check.id}`);
    if (result.status === "fail" && result.pointsAwarded !== 0) fail(`Failed check has points: ${check.id}`);
    if (!Array.isArray(result.evidence) || result.evidence.length === 0) fail(`Evidence is missing for ${check.id}`);
    categories[check.category] += result.pointsAwarded;
  }
  for (const [category, maximum] of Object.entries(categoryMaximums)) {
    const actual = record.categories?.[category];
    if (!actual || actual.score !== categories[category] || actual.maxPoints !== maximum) fail(`Category total mismatch: ${category}`);
  }
  if (!Array.isArray(record.findings)) fail("Evaluation findings must be an array.");
  const rootCauses = new Set();
  for (const finding of record.findings) {
    if (!["critical", "major", "minor", "note"].includes(finding.severity)) fail("Unknown finding severity.");
    if (!finding.rootCauseId || rootCauses.has(finding.rootCauseId)) fail("Findings must have unique rootCauseId values.");
    rootCauses.add(finding.rootCauseId);
  }
  let total = Object.values(categories).reduce((sum, value) => sum + value, 0);
  const severities = new Set(record.findings.map((finding) => finding.severity));
  if (severities.has("critical")) total = Math.min(total, 49);
  else if (severities.has("major")) total = Math.min(total, 69);
  if (record.totalScore !== total) fail(`Total score mismatch: ${record.totalScore}, expected ${total}.`);
  return { status: "pass", blindId: record.blindId, scenario: record.scenario, totalScore: total, categories };
}

async function selfTest() {
  const manifest = await readJson(manifestPath);
  for (const cell of manifest.cells) {
    const scenario = cell.scenario.replace("-project", "");
    const { contract, sha256 } = await loadV3Contract(scenario);
    const checks = contract.checks.map((check) => ({ id: check.id, status: "pass", pointsAwarded: check.maxPoints, maxPoints: check.maxPoints, evidence: ["self-test"] }));
    const reviewPass = (reviewerId) => ({ reviewerId, total: 30, checks: contract.checks.filter((check) => check.scoring === "review").map((check) => ({ id: check.id, pointsAwarded: check.maxPoints, evidence: ["self-test"] })) });
    const record = {
      schemaVersion: 3, benchmarkId: manifest.benchmarkId, blindId: cell.blindId, scenario, phase: "first_pass", evaluatorVersion: "3.0.0",
      harnessCommit: "a".repeat(40), workspaceCommit: "b".repeat(40), setupCommit: "c".repeat(40), contractSha256: sha256,
      checkRepetitions: [1, 2, 3].map((repetition) => ({ repetition, stateFingerprint: "f".repeat(64), passed: true })),
      checks, reviewPasses: [reviewPass("self-test-a"), reviewPass("self-test-b")],
      categories: Object.fromEntries(Object.entries(categoryMaximums).map(([category, maxPoints]) => [category, { score: maxPoints, maxPoints }])),
      totalScore: 100, findings: [], blind: true
    };
    await validateV3Evaluation(record);
  }
  return { status: "pass", runs: manifest.cells.length, firstSnapshot: manifest.cells.filter((cell) => cell.firstSnapshot).length, maximum: 100, reviewerPolicy: "2+1", repetitions: 3 };
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  if (args.command === "self-test") return console.log(JSON.stringify(await selfTest()));
  if (args.command === "hash") return console.log(JSON.stringify({ scenario: args.scenario, sha256: (await loadV3Contract(args.scenario)).sha256 }));
  if (args.command === "verify") {
    if (!args.input || !existsSync(resolve(args.input))) fail("verify requires an existing --input.");
    return console.log(JSON.stringify(await validateV3Evaluation(await readJson(resolve(args.input)))));
  }
  fail("Usage: evaluate-v3.mjs <self-test|hash|verify> [options]");
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) main().catch((error) => { console.error(error.message); process.exitCode = 1; });
