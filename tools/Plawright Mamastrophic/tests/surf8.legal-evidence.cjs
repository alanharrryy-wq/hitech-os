const crypto = require("crypto");

const LEGAL_ENV = "PRISMA_MAM_LEGAL_EVIDENCE";

function legalEvidenceEnabled() {
  return String(process.env[LEGAL_ENV] || "").trim() === "1";
}

function sanitizeText(value) {
  let text = value === undefined || value === null ? "" : String(value);
  const patterns = [
    [/\bBearer\s+[A-Za-z0-9._~+/=-]{8,}\b/gi, "Bearer [REDACTED_TOKEN]"],
    [/\b(?:ghp_|github_pat_|sk-|prisma_)[A-Za-z0-9._-]{12,}\b/gi, "[REDACTED_TOKEN]"],
    [/\beyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\b/g, "[REDACTED_JWT]"],
    [/\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b/gi, "[REDACTED_EMAIL]"],
    [/(?<!\d)(?:\+?\d[\d\s().-]{7,}\d)(?!\d)/g, "[REDACTED_PHONE]"],
    [/(?<!\d)(?:\d[ -]*?){13,19}(?!\d)/g, "[REDACTED_PAYMENT_NUMBER]"],
    [/\b(api[_-]?key|token|secret|password|passwd|authorization|session|cookie)\b(\s*[:=]\s*)(["']?)[^,\s"'<>;&]{6,}\3/gi, "$1$2[REDACTED]"],
  ];
  for (const [pattern, replacement] of patterns) text = text.replace(pattern, replacement);
  return text;
}

function sanitizeUrl(value) {
  const raw = value === undefined || value === null ? "" : String(value);
  if (!raw) return raw;
  try {
    const parsed = new URL(raw);
    if (parsed.username) parsed.username = "[REDACTED]";
    if (parsed.password) parsed.password = "[REDACTED]";
    const sensitive = /(token|secret|password|passwd|key|auth|session|cookie|email|phone|customer|client|device|license|setup|pin|code)/i;
    for (const key of Array.from(parsed.searchParams.keys())) {
      if (sensitive.test(key)) parsed.searchParams.set(key, "[REDACTED]");
    }
    parsed.hash = "";
    return sanitizeText(parsed.toString());
  } catch (_) {
    return sanitizeText(raw.replace(/([?&](?:token|secret|password|passwd|key|auth|session|cookie|email|phone|customer|client|device|license|setup|pin|code)=)[^&#\s]+/gi, "$1[REDACTED]"));
  }
}

function sanitizeObject(value, depth = 0) {
  if (depth > 24) return "[REDACTED_DEPTH_LIMIT]";
  if (value === null || value === undefined) return value;
  if (typeof value === "string") {
    if (/^https?:\/\//i.test(value)) return sanitizeUrl(value);
    return sanitizeText(value);
  }
  if (typeof value === "number" || typeof value === "boolean") return value;
  if (Array.isArray(value)) return value.map(item => sanitizeObject(item, depth + 1));
  if (typeof value === "object") {
    const out = {};
    const sensitiveKey = /(token|secret|password|passwd|authorization|cookie|session|api[_-]?key|private[_-]?key)/i;
    for (const [key, item] of Object.entries(value)) {
      if (sensitiveKey.test(key)) out[key] = "[REDACTED]";
      else if (/url|href|location/i.test(key) && typeof item === "string") out[key] = sanitizeUrl(item);
      else out[key] = sanitizeObject(item, depth + 1);
    }
    return out;
  }
  return sanitizeText(value);
}

function sanitizeConsoleEntry(entry) {
  return sanitizeObject(entry);
}

function sanitizeNetworkEntry(entry) {
  return sanitizeObject(entry);
}

async function applyLegalRedaction(page) {
  if (!legalEvidenceEnabled()) {
    return { enabled: false, status: "NOT_REQUIRED", maskedElements: 0, redactedTextNodes: 0 };
  }
  const result = await page.evaluate(() => {
    const explicitSelectors = [
      "[data-legal-sensitive]",
      "[data-pii]",
      "[data-sensitive]",
      "[data-private]",
      "[data-secret]",
      "input[type='password']",
      "input[type='email']",
      "input[type='tel']",
      "input[autocomplete*='cc-']",
      "input[autocomplete='one-time-code']",
      "input[name*='password' i]",
      "input[name*='secret' i]",
      "input[name*='token' i]",
      "input[name*='email' i]",
      "input[name*='phone' i]",
      "input[name*='address' i]",
      "textarea[name*='address' i]",
      "[class*='customer-email' i]",
      "[class*='customer-phone' i]",
      "[class*='personal-data' i]"
    ];
    const styleId = "__mam_legal_redaction_style__";
    if (!document.getElementById(styleId)) {
      const style = document.createElement("style");
      style.id = styleId;
      style.textContent = `
        [data-mam-legal-redacted="1"] {
          color: transparent !important;
          text-shadow: 0 0 9px rgba(0,0,0,.88) !important;
          caret-color: transparent !important;
          user-select: none !important;
        }
        input[data-mam-legal-redacted="1"],
        textarea[data-mam-legal-redacted="1"] {
          -webkit-text-security: disc !important;
          color: transparent !important;
          background-image: linear-gradient(90deg,#777 0 72%,transparent 72%) !important;
          background-size: 10px 2px !important;
          background-repeat: repeat-x !important;
          background-position: center !important;
        }
      `;
      (document.head || document.documentElement).appendChild(style);
    }

    let maskedElements = 0;
    const matchedSelectors = [];
    const seen = new Set();
    for (const selector of explicitSelectors) {
      let nodes = [];
      try { nodes = Array.from(document.querySelectorAll(selector)); } catch (_) { nodes = []; }
      if (nodes.length) matchedSelectors.push({ selector, count: nodes.length });
      for (const element of nodes) {
        if (seen.has(element)) continue;
        seen.add(element);
        maskedElements += 1;
        element.setAttribute("data-mam-legal-redacted", "1");
        if ("value" in element) {
          try { element.value = "[REDACTED]"; } catch (_) {}
          try { element.setAttribute("value", "[REDACTED]"); } catch (_) {}
        }
        if (element.isContentEditable) element.textContent = "[REDACTED]";
        else if (!["INPUT","TEXTAREA","SELECT","OPTION"].includes(element.tagName)) element.textContent = "[REDACTED]";
      }
    }

    const replacements = [
      [/\bBearer\s+[A-Za-z0-9._~+/=-]{8,}\b/gi, "Bearer [REDACTED_TOKEN]"],
      [/\b(?:ghp_|github_pat_|sk-|prisma_)[A-Za-z0-9._-]{12,}\b/gi, "[REDACTED_TOKEN]"],
      [/\beyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\b/g, "[REDACTED_JWT]"],
      [/\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b/gi, "[REDACTED_EMAIL]"],
      [/(?<!\d)(?:\+?\d[\d\s().-]{7,}\d)(?!\d)/g, "[REDACTED_PHONE]"],
      [/(?<!\d)(?:\d[ -]*?){13,19}(?!\d)/g, "[REDACTED_PAYMENT_NUMBER]"]
    ];

    let redactedTextNodes = 0;
    if (document.body && document.createTreeWalker) {
      const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
      const nodes = [];
      let node;
      while ((node = walker.nextNode()) && nodes.length < 12000) nodes.push(node);
      for (const textNode of nodes) {
        const parent = textNode.parentElement;
        if (!parent || parent.closest("script,style,noscript")) continue;
        const original = String(textNode.nodeValue || "");
        let next = original;
        for (const [pattern, replacement] of replacements) next = next.replace(pattern, replacement);
        if (next !== original) {
          textNode.nodeValue = next;
          redactedTextNodes += 1;
          parent.setAttribute("data-mam-legal-redacted", "1");
        }
      }
    }

    return {
      enabled: true,
      status: "PASS_REDACTED",
      maskedElements,
      redactedTextNodes,
      matchedSelectors,
      policy: "mamlegal1-strict-v1",
      appliedAt: new Date().toISOString()
    };
  });
  return sanitizeObject(result);
}

function sha256Text(value) {
  return crypto.createHash("sha256").update(String(value || ""), "utf8").digest("hex").toUpperCase();
}

module.exports = {
  legalEvidenceEnabled,
  sanitizeText,
  sanitizeUrl,
  sanitizeObject,
  sanitizeConsoleEntry,
  sanitizeNetworkEntry,
  applyLegalRedaction,
  sha256Text
};
