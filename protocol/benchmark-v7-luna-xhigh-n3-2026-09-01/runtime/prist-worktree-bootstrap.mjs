#!/usr/bin/env node
/* global process */

import { chmod, mkdir, readFile, stat, writeFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { spawn } from "node:child_process";

const MAX_CONNECTION_BYTES = 64 * 1024;
const REQUIRED_ORIGIN = "https://prist.isty.ist";

function fail(message) {
  throw new Error(message);
}

function object(value) {
  return value !== null && typeof value === "object" && !Array.isArray(value);
}

async function readRegularFile(path, maximumBytes, label) {
  const metadata = await stat(path).catch(() => null);
  if (!metadata?.isFile() || metadata.size > maximumBytes) fail(`${label} is unavailable.`);
  return readFile(path, "utf8");
}

function validateConnection(source) {
  let connection;
  try {
    connection = JSON.parse(source);
  } catch {
    fail("Prist connection source is invalid.");
  }
  if (!object(connection)
    || connection.origin !== REQUIRED_ORIGIN
    || typeof connection.projectId !== "string"
    || !connection.projectId.startsWith("project_")
    || typeof connection.credential !== "string"
    || connection.credential.length < 1
    || connection.credential.length > 4096
    || /\s|[^\x21-\x7e]/u.test(connection.credential)) {
    fail("Prist connection source is invalid.");
  }
  return connection;
}

async function writePrivate(path, source) {
  await mkdir(dirname(path), { recursive: true });
  await writeFile(path, source, { encoding: "utf8", mode: 0o600 });
  if (process.platform !== "win32") await chmod(path, 0o600);
}

export async function materializeConnectionState({
  projectRoot = process.env.PRIST_PROJECT_ROOT || process.cwd(),
  connectionSource = process.env.PRIST_CONNECTION_SOURCE,
  workflowSource = process.env.PRIST_WORKFLOW_SOURCE
} = {}) {
  if (!connectionSource) fail("Prist connection source is unavailable.");
  const root = resolve(projectRoot);
  const connectionText = await readRegularFile(resolve(connectionSource), MAX_CONNECTION_BYTES, "Prist connection source");
  const connection = validateConnection(connectionText);
  const localConnection = resolve(root, ".prist", "connection.json");
  await writePrivate(localConnection, connectionText);

  let localWorkflow = null;
  if (workflowSource) {
    const workflowText = await readRegularFile(resolve(workflowSource), 4 * 1024 * 1024, "Prist workflow source");
    try {
      if (!object(JSON.parse(workflowText))) fail("Prist workflow source is invalid.");
    } catch {
      fail("Prist workflow source is invalid.");
    }
    localWorkflow = resolve(root, ".prist", "workflow.json");
    await writePrivate(localWorkflow, workflowText);
  }
  return { projectRoot: root, projectId: connection.projectId, origin: connection.origin, localConnection, localWorkflow };
}

async function main() {
  const state = await materializeConnectionState();
  const bridge = resolve(dirname(fileURLToPath(import.meta.url)), "prist-mcp-stdio.mjs");
  const child = spawn(process.execPath, [bridge], {
    cwd: state.projectRoot,
    env: { ...process.env, PRIST_PROJECT_ROOT: state.projectRoot },
    stdio: "inherit",
    windowsHide: true
  });
  child.once("error", () => {
    process.stderr.write("Prist MCP bridge failed to start.\n");
    process.exitCode = 1;
  });
  child.once("exit", (code, signal) => {
    if (signal) process.kill(process.pid, signal);
    else process.exitCode = code ?? 1;
  });
}

if (resolve(process.argv[1] ?? "") === fileURLToPath(import.meta.url)) {
  main().catch((error) => {
    process.stderr.write(`${error.message}\n`);
    process.exitCode = 1;
  });
}
