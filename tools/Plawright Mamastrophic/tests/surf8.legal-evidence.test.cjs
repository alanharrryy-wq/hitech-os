const assert = require("assert");
const {
  legalEvidenceEnabled,
  sanitizeText,
  sanitizeUrl,
  sanitizeObject,
  sha256Text
} = require("./surf8.legal-evidence.cjs");

process.env.PRISMA_MAM_LEGAL_EVIDENCE = "1";
assert.strictEqual(legalEvidenceEnabled(), true);

const sample = "email alan@example.com token=secretvalue123 Bearer abcdefghijklmnop";
const clean = sanitizeText(sample);
assert(!clean.includes("alan@example.com"));
assert(!clean.includes("secretvalue123"));
assert(!clean.includes("abcdefghijklmnop"));

const url = sanitizeUrl("https://example.test/path?token=abc123456789&safe=yes&email=alan%40example.com#frag");
assert(!url.includes("abc123456789"));
assert(!url.includes("alan%40example.com"));
assert(!url.includes("#frag"));
assert(url.includes("safe=yes"));

const obj = sanitizeObject({
  url: "https://x.test/?secret=topsecret123",
  password: "never-store-me",
  nested: { email: "person@example.com", ok: 1 }
});
assert.strictEqual(obj.password, "[REDACTED]");
assert(!JSON.stringify(obj).includes("topsecret123"));
assert(!JSON.stringify(obj).includes("person@example.com"));

assert(/^[A-F0-9]{64}$/.test(sha256Text("mamlegal1")));
console.log("PASS_MAM_LEGAL_HELPER");
