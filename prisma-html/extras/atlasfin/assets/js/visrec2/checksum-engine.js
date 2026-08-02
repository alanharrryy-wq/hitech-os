(() => {
  "use strict";
  const modules = (window.__PRISMA_VISREC2_MODULES__ ||= {});

  const canonicalize = (value) => {
    if (Array.isArray(value)) return value.map(canonicalize);
    if (value && typeof value === "object") {
      return Object.fromEntries(
        Object.keys(value)
          .sort()
          .map((key) => [key, canonicalize(value[key])])
      );
    }
    return value;
  };

  const stableJson = (value) => JSON.stringify(canonicalize(value));

  const fnv = (text) => {
    let hash = 0x811c9dc5;
    for (let index = 0; index < text.length; index += 1) {
      hash ^= text.charCodeAt(index);
      hash = Math.imul(hash, 0x01000193);
    }
    return (hash >>> 0).toString(16).padStart(8, "0").toUpperCase();
  };

  const calculate = async (payload, preferred = "SHA-256") => {
    const canonical = stableJson(payload);
    if (preferred === "SHA-256" && window.crypto?.subtle && window.TextEncoder) {
      const bytes = new TextEncoder().encode(canonical);
      const digest = await window.crypto.subtle.digest("SHA-256", bytes);
      return {
        algorithm: "SHA-256",
        canonicalization: "RFC8785-compatible-sorted-json-v1",
        value: Array.from(new Uint8Array(digest))
          .map((byte) => byte.toString(16).padStart(2, "0"))
          .join("")
          .toUpperCase(),
      };
    }
    return {
      algorithm: "FNV-1A-32",
      canonicalization: "RFC8785-compatible-sorted-json-v1",
      value: fnv(canonical),
    };
  };

  const verify = async (payload) => {
    const expected = payload?.integrity?.checksum || payload?.checksum;
    if (!expected?.algorithm || !expected?.value) {
      return {
        ok: false,
        status: "INVALID_CHECKSUM",
        code: "CHECKSUM_MISSING",
        expected: expected || null,
        actual: null,
      };
    }
    const unsigned = structuredClone(payload);
    if (unsigned.integrity?.checksum) delete unsigned.integrity.checksum;
    delete unsigned.checksum;
    const actual = await calculate(unsigned, expected.algorithm);
    return {
      ok: actual.value === String(expected.value).toUpperCase(),
      status:
        actual.value === String(expected.value).toUpperCase()
          ? "SOURCE_READY"
          : "INVALID_CHECKSUM",
      code:
        actual.value === String(expected.value).toUpperCase()
          ? "CHECKSUM_VALID"
          : "CHECKSUM_MISMATCH",
      expected,
      actual,
    };
  };

  modules["checksum-engine"] = Object.freeze({
    canonicalize,
    stableJson,
    fnv,
    calculate,
    verify,
  });
})();
