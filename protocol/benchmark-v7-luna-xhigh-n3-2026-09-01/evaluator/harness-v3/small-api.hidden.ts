import crypto from "node:crypto";
import { join } from "node:path";
import { pathToFileURL } from "node:url";
import { isDeepStrictEqual } from "node:util";

const workspace = process.env.BENCHMARK_WORKSPACE;
const databaseUrl = process.env.INTEGRATION_DATABASE_URL ?? process.env.DATABASE_URL;
if (!workspace || !databaseUrl) throw new Error("BENCHMARK_WORKSPACE and INTEGRATION_DATABASE_URL are required.");

const tokenEncryptionKey = Buffer.alloc(32, 11);
const serviceTokenHashKey = Buffer.alloc(32, 23);
process.env.NODE_ENV = "test";
process.env.DATABASE_URL = databaseUrl;
process.env.PUBLIC_BASE_URL = "https://gateway.example.test";
process.env.ADMIN_API_TOKEN = "admin-token-admin-token-admin-token";
process.env.TOKEN_ENCRYPTION_KEY = tokenEncryptionKey.toString("base64");
process.env.SERVICE_TOKEN_HASH_KEY = serviceTokenHashKey.toString("base64");
delete process.env.OUTBOUND_METHOD_ALLOWLIST;

const importFromWorkspace = (relativePath: string) => import(pathToFileURL(join(workspace, relativePath)).href);
const { buildApp } = await importFromWorkspace("src/app.ts");
const { loadConfig } = await importFromWorkspace("src/config.ts");
const { encryptString, hashServiceToken } = await importFromWorkspace("src/lib/crypto.ts");
const { processOutboundDeliveryById } = await importFromWorkspace("src/services/delivery-service.ts");

const supportedMethods = ["sendMessage", "editMessageText", "deleteMessage"];
const productionDefaults = loadConfig();
const config = {
  ...productionDefaults,
  host: "127.0.0.1",
  telegramTimeoutMs: 500,
  callbackTimeoutMs: 500,
  workerIntervalMs: 25,
  processingLockTtlMs: 50,
  retryBaseDelayMs: 10,
  retryMaxDelayMs: 50,
  maxCallbackRetries: 3,
  maxTelegramRetries: 3,
  telegramDispatchMinIntervalMs: 0
};

const app = await buildApp({ config, startWorkers: false });
await app.ready();

type Seed = { serviceToken: string; registrationId: string };
type CheckOutcome = { id: string; passed: boolean; evidence: string; error?: string };
const outcomes: CheckOutcome[] = [];
const telegramCalls: Array<{ url: string; body: unknown }> = [];
const originalFetch = globalThis.fetch;

function assert(condition: unknown, message: string): asserts condition {
  if (!condition) throw new Error(message);
}

async function resetDatabase() {
  await app.prisma.$executeRawUnsafe(`
    TRUNCATE TABLE
      "AuditLog",
      "InboundUpdateLog",
      "OutboundDeliveryLog",
      "BotRegistration",
      "Application",
      "Tenant"
    RESTART IDENTITY CASCADE
  `);
  telegramCalls.length = 0;
}

async function seed(code = "hidden-app"): Promise<Seed> {
  const tenantId = crypto.randomUUID();
  const applicationId = crypto.randomUUID();
  const registrationId = crypto.randomUUID();
  const serviceToken = `tgw_hidden_${crypto.randomUUID()}`;
  await app.prisma.tenant.create({ data: { id: tenantId, displayName: "Hidden Tenant" } });
  await app.prisma.application.create({
    data: {
      id: applicationId,
      tenantId,
      code,
      displayName: "Hidden App",
      environment: "TEST",
      serviceTokenHash: hashServiceToken(serviceToken, serviceTokenHashKey),
      outboundAllowlist: supportedMethods
    }
  });
  await app.prisma.botRegistration.create({
    data: {
      id: registrationId,
      tenantId,
      applicationId,
      provider: "telegram",
      tokenEncrypted: encryptString("123456:hidden-bot-token", tokenEncryptionKey),
      callbackSecretEncrypted: encryptString("hidden-callback-secret", tokenEncryptionKey),
      telegramSecretTokenEncrypted: encryptString("hidden-telegram-secret", tokenEncryptionKey),
      webhookPathSecret: `webhook-${crypto.randomUUID()}`,
      gatewayWebhookPath: `/ingress/telegram/hidden-${crypto.randomUUID()}`,
      botId: BigInt(4004),
      botUsername: "hidden_bot",
      botName: "Hidden Bot",
      status: "CONNECTED",
      webhookMode: "OWNED",
      telegramWebhookUrl: "https://gateway.example.test/ingress/telegram/hidden",
      clientCallbackUrl: "https://client.example.test/callback"
    }
  });
  return { serviceToken, registrationId };
}

function payload(method: string) {
  if (method === "sendMessage") return { chat_id: 42, text: "hello" };
  if (method === "editMessageText") return { chat_id: 42, message_id: 7, text: "updated" };
  if (method === "deleteMessage") return { chat_id: 42, message_id: 7 };
  return {};
}

async function submit(seedValue: Seed, method: string, requestPayload: unknown, idempotencyKey?: string, token = seedValue.serviceToken) {
  return app.inject({
    method: "POST",
    url: `/v1/bots/${seedValue.registrationId}/actions/${method}`,
    headers: {
      authorization: `Bearer ${token}`,
      ...(idempotencyKey ? { "idempotency-key": idempotencyKey } : {})
    },
    payload: requestPayload
  });
}

function assertMachineError(response: { statusCode: number; json(): any }, expectedCode?: string) {
  assert(response.statusCode >= 400 && response.statusCode < 500, `expected 4xx, got ${response.statusCode}`);
  const body = response.json();
  assert(typeof body?.error?.code === "string" && body.error.code.length > 0, "error.code is missing");
  assert(typeof body?.error?.message === "string" && body.error.message.length > 0, "error.message is missing");
  if (expectedCode) assert(body.error.code === expectedCode, `expected ${expectedCode}, got ${body.error.code}`);
}

async function check(id: string, evidence: string, procedure: () => Promise<void>) {
  await resetDatabase();
  try {
    await procedure();
    outcomes.push({ id, passed: true, evidence });
  } catch (error) {
    outcomes.push({ id, passed: false, evidence, error: error instanceof Error ? error.message : String(error) });
  }
}

globalThis.fetch = async (input: string | URL | Request, init?: RequestInit) => {
  const url = String(input);
  const body = init?.body ? JSON.parse(String(init.body)) : null;
  telegramCalls.push({ url, body });
  if (url.endsWith("/editMessageText")) return new Response(JSON.stringify({ ok: true, result: { message_id: body.message_id, text: body.text } }), { status: 200, headers: { "content-type": "application/json" } });
  if (url.endsWith("/deleteMessage")) return new Response(JSON.stringify({ ok: true, result: true }), { status: 200, headers: { "content-type": "application/json" } });
  if (url.endsWith("/sendMessage")) return new Response(JSON.stringify({ ok: true, result: { message_id: 8, text: body.text } }), { status: 200, headers: { "content-type": "application/json" } });
  throw new Error(`Unexpected external call: ${url}`);
};

await check("S3-A01", "three explicit methods accepted; unknown method keeps machine error", async () => {
  for (const method of supportedMethods) {
    assert(config.outboundMethodAllowlist.includes(method), `${method} is absent from the production default allowlist`);
  }
  const seeded = await seed();
  for (const method of supportedMethods) {
    const response = await submit(seeded, method, payload(method), `allow-${method}`);
    assert(response.statusCode === 202, `${method} returned ${response.statusCode}`);
  }
  const unknown = await submit(seeded, "forwardMessage", { chat_id: 42 }, "unknown-method");
  assertMachineError(unknown, "OUTBOUND_METHOD_NOT_ALLOWED");
});

await check("S3-A02", "invalid payload rejected for each supported method before persistence", async () => {
  const seeded = await seed();
  const invalid = [
    ["sendMessage", { chat_id: 42 }],
    ["editMessageText", { chat_id: 42, message_id: 7 }],
    ["deleteMessage", { chat_id: 42 }]
  ] as const;
  for (const [method, requestPayload] of invalid) {
    const response = await submit(seeded, method, requestPayload, `invalid-${method}`);
    assertMachineError(response, "VALIDATION_ERROR");
  }
  assert(await app.prisma.outboundDeliveryLog.count() === 0, "invalid requests created deliveries");
});

await check("S3-A03", "sendMessage remains queue-first 202/PENDING", async () => {
  const seeded = await seed();
  const response = await submit(seeded, "sendMessage", payload("sendMessage"), "send-existing");
  const body = response.json();
  assert(response.statusCode === 202 && body.delivery?.status === "PENDING" && body.duplicate === false, "sendMessage queue contract changed");
});

await check("S3-A04", "editMessageText is queued and dispatched with unchanged method/payload", async () => {
  const seeded = await seed();
  const requestPayload = payload("editMessageText");
  const response = await submit(seeded, "editMessageText", requestPayload, "edit-dispatch");
  const body = response.json();
  assert(response.statusCode === 202 && body.delivery?.status === "PENDING", "edit was not queued");
  await processOutboundDeliveryById(app, body.delivery.id);
  const call = telegramCalls.find((item) => item.url.endsWith("/editMessageText"));
  assert(call && isDeepStrictEqual(call.body, requestPayload), "edit method/payload changed before Telegram");
});

await check("S3-A05", "deleteMessage is queued and dispatched with unchanged method/payload", async () => {
  const seeded = await seed();
  const requestPayload = payload("deleteMessage");
  const response = await submit(seeded, "deleteMessage", requestPayload, "delete-dispatch");
  const body = response.json();
  assert(response.statusCode === 202 && body.delivery?.status === "PENDING", "delete was not queued");
  await processOutboundDeliveryById(app, body.delivery.id);
  const call = telegramCalls.find((item) => item.url.endsWith("/deleteMessage"));
  assert(call && isDeepStrictEqual(call.body, requestPayload), "delete method/payload changed before Telegram");
});

await check("S3-A06", "missing Idempotency-Key keeps stable error and persists nothing", async () => {
  const seeded = await seed();
  const response = await submit(seeded, "editMessageText", payload("editMessageText"));
  assertMachineError(response, "IDEMPOTENCY_KEY_REQUIRED");
  assert(await app.prisma.outboundDeliveryLog.count() === 0, "missing key created a delivery");
});

await check("S3-A07", "identical retry returns the existing delivery", async () => {
  const seeded = await seed();
  const requestPayload = payload("editMessageText");
  const first = await submit(seeded, "editMessageText", requestPayload, "same-key");
  const second = await submit(seeded, "editMessageText", requestPayload, "same-key");
  assert(first.statusCode === 202 && second.statusCode === 200, "duplicate status contract changed");
  assert(second.json().duplicate === true && second.json().delivery.id === first.json().delivery.id, "duplicate did not return the original delivery");
});

await check("S3-A08", "conflicting reuse of an idempotency key is rejected without mutation", async () => {
  const seeded = await seed();
  const first = await submit(seeded, "editMessageText", payload("editMessageText"), "conflict-key");
  const conflict = await submit(seeded, "editMessageText", { chat_id: 42, message_id: 7, text: "different" }, "conflict-key");
  assert(first.statusCode === 202, "initial delivery failed");
  assertMachineError(conflict, "IDEMPOTENCY_CONFLICT");
  const stored = await app.prisma.outboundDeliveryLog.findUniqueOrThrow({ where: { id: first.json().delivery.id } });
  assert((stored.requestPayload as any).text === "updated", "conflict mutated the original delivery");
});

await check("S3-A09", "authentication and registration isolation cover new methods", async () => {
  const first = await seed("first-app");
  const second = await seed("second-app");
  const unauthenticated = await submit(first, "deleteMessage", payload("deleteMessage"), "bad-auth", "invalid-token");
  assertMachineError(unauthenticated, "UNAUTHORIZED_APPLICATION");
  const crossTenant = await submit({ serviceToken: first.serviceToken, registrationId: second.registrationId }, "deleteMessage", payload("deleteMessage"), "cross-tenant");
  assertMachineError(crossTenant, "REGISTRATION_NOT_FOUND");
  assert(await app.prisma.outboundDeliveryLog.count() === 0, "unauthorized requests created deliveries");
});

await check("S3-A10", "new methods use the existing retry and retry-after policy", async () => {
  const seeded = await seed();
  const accepted = await submit(seeded, "editMessageText", payload("editMessageText"), "retry-edit");
  globalThis.fetch = async () => new Response(JSON.stringify({ ok: false, error_code: 429, description: "Too Many Requests", parameters: { retry_after: 1 } }), { status: 429, headers: { "content-type": "application/json" } });
  await processOutboundDeliveryById(app, accepted.json().delivery.id);
  const delivery = await app.prisma.outboundDeliveryLog.findUniqueOrThrow({ where: { id: accepted.json().delivery.id } });
  assert(delivery.status === "RETRY" && delivery.attempts === 1 && delivery.nextRetryAt instanceof Date, "retry state was not scheduled");
});

globalThis.fetch = originalFetch;
await app.close();
console.log(JSON.stringify({ schemaVersion: 3, scenario: "small", checks: outcomes, passed: outcomes.every((item) => item.passed) }));
