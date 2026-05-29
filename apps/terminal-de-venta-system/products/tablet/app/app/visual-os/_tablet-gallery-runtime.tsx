import "server-only";
import fs from "node:fs";
import path from "node:path";
import type { CSSProperties } from "react";

export type TabletGalleryLoadConfig = {
  title: string;
  description: string;
  routePath: string;
  htmlFiles: string[];
  requiredJsonFiles: string[];
};

export type TabletGallerySource = {
  title: string;
  description: string;
  routePath: string;
  htmlFile: string;
  sourceDir: string;
  sourceKind: "repo-docs" | "public-fallback" | "missing";
  srcDoc: string;
  warnings: string[];
  parsedJson: Array<{ file: string; ok: boolean; detail: string }>;
};

function fileExists(filePath: string) {
  try {
    return fs.existsSync(filePath) && fs.statSync(filePath).isFile();
  } catch {
    return false;
  }
}

function dirExists(filePath: string) {
  try {
    return fs.existsSync(filePath) && fs.statSync(filePath).isDirectory();
  } catch {
    return false;
  }
}

function findTabletAppRoot() {
  const cwd = process.cwd();
  const directCandidates = [
    cwd,
    path.resolve(cwd, "products/tablet/app"),
    path.resolve(cwd, "..", "products/tablet/app"),
    path.resolve(cwd, "..", "..", "products/tablet/app")
  ];

  for (const candidate of directCandidates) {
    if (fileExists(path.join(candidate, "package.json")) && fileExists(path.join(candidate, "app", "layout.tsx"))) {
      return candidate;
    }
  }

  let cursor = cwd;
  for (let guard = 0; guard < 8; guard += 1) {
    if (fileExists(path.join(cursor, "package.json")) && fileExists(path.join(cursor, "app", "layout.tsx"))) {
      return cursor;
    }
    const next = path.dirname(cursor);
    if (next === cursor) break;
    cursor = next;
  }

  return cwd;
}

function findProjectRoot(appRoot: string) {
  const canonical = path.resolve(appRoot, "..", "..", "..");
  if (dirExists(path.join(canonical, "products", "tablet", "app"))) {
    return canonical;
  }

  let cursor = appRoot;
  for (let guard = 0; guard < 10; guard += 1) {
    if (dirExists(path.join(cursor, "products", "tablet", "app"))) {
      return cursor;
    }
    const next = path.dirname(cursor);
    if (next === cursor) break;
    cursor = next;
  }

  return canonical;
}

function readUtf8(filePath: string) {
  return fs.readFileSync(filePath, "utf8");
}

function escapeInlineTag(text: string, tag: "style" | "script") {
  const close = new RegExp(`</${tag}`, "gi");
  return text.replace(close, `<\\/${tag}`);
}

const TABLET_VISUAL_OS_PUBLIC_BASE = "/visual-os/tablet-light-visual-preset-engine/";

function normalizeVisualAssetReference(reference: string) {
  const trimmed = reference.trim();
  if (!trimmed) return trimmed;
  if (/^(?:data:|blob:|https?:|mailto:|tel:|#)/i.test(trimmed)) return trimmed;
  if (trimmed.startsWith(TABLET_VISUAL_OS_PUBLIC_BASE)) return trimmed;

  const withoutLeadingDot = trimmed.replace(/^\.\//, "");
  if (withoutLeadingDot.startsWith("assets/")) {
    return `${TABLET_VISUAL_OS_PUBLIC_BASE}${withoutLeadingDot}`;
  }

  return trimmed;
}

function rewriteSrcDocRelativeAssetUrls(text: string) {
  let output = text;

  output = output.replace(/url\(\s*(["']?)(\.\/assets\/|assets\/)([^"')]+)\1\s*\)/gi, (_match, quote, prefix, rest) => {
    const next = normalizeVisualAssetReference(`${prefix}${rest}`);
    return `url("${next}")`;
  });

  output = output.replace(/\b(src|href)=(["'])(\.\/assets\/|assets\/)([^"']+)\2/gi, (_match, attr, quote, prefix, rest) => {
    const next = normalizeVisualAssetReference(`${prefix}${rest}`);
    return `${attr}=${quote}${next}${quote}`;
  });

  output = output.replace(/(["'`])(\.\/assets\/|assets\/)(backgrounds\/[^"'`]+)\1/gi, (_match, quote, prefix, rest) => {
    const next = normalizeVisualAssetReference(`${prefix}${rest}`);
    return `${quote}${next}${quote}`;
  });

  return output;
}

function ensureSrcDocBaseHref(html: string) {
  if (/<base\b/i.test(html)) {
    return html.replace(/<base\b([^>]*)>/i, (_match, attrs) => {
      const attrsText = String(attrs || "");
      const withoutHref = attrsText.replace(/\s+href=(?:"[^"]*"|'[^']*'|[^\s>]+)/i, "");
      const withTarget = /\starget=/i.test(withoutHref) ? withoutHref : `${withoutHref} target="_self"`;
      return `<base href="${TABLET_VISUAL_OS_PUBLIC_BASE}"${withTarget}>`;
    });
  }

  return html.replace(/<head([^>]*)>/i, `<head$1><base href="${TABLET_VISUAL_OS_PUBLIC_BASE}" target="_self" />`);
}

function inlineGalleryAssets(html: string, sourceDir: string, warnings: string[]) {
  let output = rewriteSrcDocRelativeAssetUrls(html);

  output = output.replace(/<link\b([^>]*?)href=["']\.\/([^"']+\.css)["']([^>]*?)>/gi, (_match, before, assetName, after) => {
    const assetPath = path.join(sourceDir, assetName);
    if (!fileExists(assetPath)) {
      warnings.push(`CSS faltante para inline: ${assetName}`);
      return `<!-- PRISMA missing CSS: ${assetName} -->`;
    }
    const css = escapeInlineTag(rewriteSrcDocRelativeAssetUrls(readUtf8(assetPath)), "style");
    return `<style data-prisma-inlined-css="${assetName}">\n${css}\n</style>`;
  });

  output = output.replace(/<script\b([^>]*?)src=["']\.\/([^"']+\.js)["']([^>]*)>\s*<\/script>/gi, (_match, before, assetName, after) => {
    const assetPath = path.join(sourceDir, assetName);
    if (!fileExists(assetPath)) {
      warnings.push(`JS faltante para inline: ${assetName}`);
      return `<!-- PRISMA missing JS: ${assetName} -->`;
    }
    const js = escapeInlineTag(rewriteSrcDocRelativeAssetUrls(readUtf8(assetPath)), "script");
    return `<script data-prisma-inlined-js="${assetName}">\n${js}\n</script>`;
  });

  output = ensureSrcDocBaseHref(rewriteSrcDocRelativeAssetUrls(output));

  if (output.includes('url("./assets/') || output.includes("url('./assets/") || output.includes('url(./assets/')) {
    warnings.push("Aún quedaron referencias CSS relativas ./assets dentro de srcDoc después de reescritura.");
  }

  return output;
}

function parseRequiredJson(sourceDir: string, files: string[]) {
  return files.map((file) => {
    const filePath = path.join(sourceDir, file);
    if (!fileExists(filePath)) {
      return { file, ok: false, detail: "missing" };
    }
    try {
      const parsed = JSON.parse(readUtf8(filePath)) as unknown;
      const kind = Array.isArray(parsed) ? `array:${parsed.length}` : typeof parsed;
      return { file, ok: true, detail: kind };
    } catch (error) {
      return { file, ok: false, detail: error instanceof Error ? error.message : String(error) };
    }
  });
}

function buildMissingGallery(config: TabletGalleryLoadConfig, warnings: string[]) {
  const warningItems = warnings.map((warning) => `<li>${warning.replace(/[<>&]/g, (ch) => ({ "<": "&lt;", ">": "&gt;", "&": "&amp;" }[ch] || ch))}</li>`).join("");
  return `<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>${config.title}</title>
  <style>
    body{margin:0;min-height:100vh;display:grid;place-items:center;font-family:ui-sans-serif,system-ui,-apple-system,Segoe UI,Roboto,Arial,sans-serif;color:#223746;background:linear-gradient(135deg,#f7fafc,#e9eef3)}
    main{max-width:760px;margin:24px;padding:28px;border:1px solid rgba(90,110,128,.18);border-radius:28px;background:rgba(255,255,255,.72);box-shadow:0 24px 70px rgba(67,86,103,.14)}
    h1{margin:0 0 12px;font-size:28px}
    p,li{line-height:1.55;color:#5f7382}
    code{font-weight:800;color:#2f6f9f}
  </style>
</head>
<body>
  <main>
    <h1>${config.title}</h1>
    <p>No se encontró el HTML fuente para esta galería. La ruta existe, pero necesita el paquete visual fuente.</p>
    <p>Archivos buscados: <code>${config.htmlFiles.join(", ")}</code></p>
    <ul>${warningItems}</ul>
  </main>
</body>
</html>`;
}

export function loadTabletGallerySource(config: TabletGalleryLoadConfig): TabletGallerySource {
  const appRoot = findTabletAppRoot();
  const projectRoot = findProjectRoot(appRoot);
  const materialityCandidates = config.routePath.includes("materiality-catalog")
    ? [
        {
          kind: "public-fallback" as const,
          dir: path.join(appRoot, "public", "visual-os", "materiality-catalog")
        },
        {
          kind: "repo-docs" as const,
          dir: path.join(projectRoot, "docs", "design", "materiality-catalog")
        }
      ]
    : [];

  const candidates = [
    ...materialityCandidates,
    {
      kind: "repo-docs" as const,
      dir: path.join(projectRoot, "docs", "design", "tablet-light-visual-preset-engine")
    },
    {
      kind: "public-fallback" as const,
      dir: path.join(appRoot, "public", "visual-os", "tablet-light-visual-preset-engine")
    }
  ];

  const warnings: string[] = [];
  for (const candidate of candidates) {
    for (const htmlFile of config.htmlFiles) {
      const htmlPath = path.join(candidate.dir, htmlFile);
      if (!fileExists(htmlPath)) {
        warnings.push(`No encontrado: ${htmlPath}`);
        continue;
      }

      const html = readUtf8(htmlPath);
      const srcDoc = inlineGalleryAssets(html, candidate.dir, warnings);
      return {
        title: config.title,
        description: config.description,
        routePath: config.routePath,
        htmlFile,
        sourceDir: candidate.dir,
        sourceKind: candidate.kind,
        srcDoc,
        warnings,
        parsedJson: parseRequiredJson(candidate.dir, config.requiredJsonFiles)
      };
    }
  }

  const srcDoc = buildMissingGallery(config, warnings);
  return {
    title: config.title,
    description: config.description,
    routePath: config.routePath,
    htmlFile: config.htmlFiles[0] || "missing",
    sourceDir: "",
    sourceKind: "missing",
    srcDoc,
    warnings,
    parsedJson: []
  };
}

export function GalleryChrome({ gallery }: { gallery: TabletGallerySource }) {
  const status = gallery.sourceKind === "missing" ? "Fuente faltante" : "Fuente activa";
  const isBackgroundGallery = gallery.routePath.includes("tablet-background-gallery");
  const mainStyle: CSSProperties = isBackgroundGallery ? {
    minHeight: "100dvh",
    padding: "18px",
    color: "#edf8fb",
    background: "radial-gradient(circle at 14% 12%, rgba(255,109,83,.18), transparent 30%), radial-gradient(circle at 86% 82%, rgba(90,232,245,.15), transparent 35%), linear-gradient(135deg, #07090b 0%, #10191d 48%, #05070a 100%)",
    fontFamily: "ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif"
  } : {
    minHeight: "100dvh",
    padding: "18px",
    color: "#213443",
    background: "linear-gradient(135deg, #f7fafc 0%, #e9eef3 46%, #f9fbfd 100%)",
    fontFamily: "ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif"
  };
  const headerStyle: CSSProperties = isBackgroundGallery ? {
    display: "flex", alignItems: "center", justifyContent: "space-between", gap: "12px", flexWrap: "wrap", minHeight: "56px", padding: "14px 16px", border: "1px solid rgba(230,246,250,.16)", borderRadius: "24px", background: "linear-gradient(145deg, rgba(255,255,255,.10), rgba(255,255,255,.035)), rgba(16,26,30,.58)", boxShadow: "0 26px 80px rgba(0,0,0,.42)", backdropFilter: "blur(20px) saturate(132%)"
  } : {
    display: "flex", alignItems: "center", justifyContent: "space-between", gap: "12px", flexWrap: "wrap", minHeight: "56px", padding: "14px 16px", border: "1px solid rgba(90,110,128,.16)", borderRadius: "24px", background: "rgba(255,255,255,.76)", boxShadow: "0 18px 50px rgba(67,86,103,.12)", backdropFilter: "blur(18px) saturate(125%)"
  };
  const jsonPanelStyle: CSSProperties = isBackgroundGallery ? {
    display: "flex", gap: "8px", flexWrap: "wrap", padding: "12px", border: "1px solid rgba(230,246,250,.14)", borderRadius: "20px", background: "rgba(16,26,30,.48)", boxShadow: "0 18px 60px rgba(0,0,0,.30)", backdropFilter: "blur(16px) saturate(128%)"
  } : {
    display: "flex", gap: "8px", flexWrap: "wrap", padding: "12px", border: "1px solid rgba(90,110,128,.14)", borderRadius: "20px", background: "rgba(255,255,255,.55)"
  };
  const pill = makePillStyle(isBackgroundGallery);
  return (
    <main style={mainStyle} data-prisma-visual-gallery={gallery.routePath} data-prisma-theme={isBackgroundGallery ? "visual-os-liquid-dark" : "light-only"}>
      <section style={{ display: "grid", gap: "14px", maxWidth: "1480px", margin: "0 auto" }}>
        <header style={headerStyle}>
          <div>
            <p style={{ margin: "0 0 4px", textTransform: "uppercase", letterSpacing: ".12em", fontSize: "12px", fontWeight: 850, color: isBackgroundGallery ? "#69f2ff" : "#3975b5" }}>PRISMA Tablet · Visual OS · {isBackgroundGallery ? "Storm Glass" : "Light-only"}</p>
            <h1 style={{ margin: 0, fontSize: "clamp(24px, 3vw, 38px)", lineHeight: 1.04, color: isBackgroundGallery ? "#f3fbfd" : "#213443" }}>{gallery.title}</h1>
            <p style={{ margin: "8px 0 0", color: isBackgroundGallery ? "rgba(214,230,235,.76)" : "#637684", maxWidth: "920px" }}>{gallery.description}</p>
          </div>
          <nav style={{ display: "flex", gap: "10px", flexWrap: "wrap" }} aria-label="Visual OS gallery navigation">
            <a style={pill} href="/visual-os">Visual OS</a>
            <a style={pill} href="/visual-os/materiality-catalog">Materiality Catalog</a>
            <a style={pill} href="/visual-os/tablet-codex-gallery">Codex Gallery</a>
            <a style={pill} href="/visual-os/tablet-background-gallery">Background Gallery</a>
          </nav>
        </header>
        <section style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: "10px" }}>
          <InfoChip dark={isBackgroundGallery} label="Ruta" value={gallery.routePath} />
          <InfoChip dark={isBackgroundGallery} label="Estado" value={status} />
          <InfoChip dark={isBackgroundGallery} label="HTML" value={gallery.htmlFile} />
          <InfoChip dark={isBackgroundGallery} label="Origen" value={gallery.sourceKind} />
        </section>
        {gallery.parsedJson.length > 0 ? (
          <section style={jsonPanelStyle}>
            {gallery.parsedJson.map((item) => (
              <span key={item.file} style={{ display: "inline-flex", alignItems: "center", minHeight: "40px", borderRadius: "999px", padding: "0 12px", border: `1px solid ${item.ok ? (isBackgroundGallery ? "rgba(105,242,255,.22)" : "rgba(35,129,92,.22)") : "rgba(190,91,72,.24)"}`, color: item.ok ? (isBackgroundGallery ? "#bdf8ff" : "#1f6f52") : "#ffb1a2", background: item.ok ? (isBackgroundGallery ? "rgba(105,242,255,.10)" : "rgba(220,247,235,.62)") : "rgba(255,105,80,.14)", fontSize: "12px", fontWeight: 800 }}>{item.ok ? "JSON OK" : "JSON FAIL"} · {item.file}</span>
            ))}
          </section>
        ) : null}
        {gallery.warnings.length > 0 ? (
          <details style={{ border: "1px solid rgba(255,197,109,.24)", borderRadius: "18px", padding: "12px 14px", background: isBackgroundGallery ? "rgba(255,197,109,.08)" : "rgba(255,248,232,.68)", color: isBackgroundGallery ? "#ffe1a7" : "#6f5520" }}>
            <summary style={{ cursor: "pointer", minHeight: "32px", fontWeight: 850 }}>Advertencias de fuente detectadas</summary>
            <ul>{gallery.warnings.slice(0, 8).map((warning) => <li key={warning}>{warning}</li>)}</ul>
          </details>
        ) : null}
        <iframe title={gallery.title} srcDoc={gallery.srcDoc} sandbox="allow-scripts allow-same-origin" style={{ width: "100%", minHeight: "calc(100dvh - 260px)", height: "78dvh", border: isBackgroundGallery ? "1px solid rgba(230,246,250,.16)" : "1px solid rgba(90,110,128,.18)", borderRadius: "28px", background: isBackgroundGallery ? "#07090b" : "#f7fafc", boxShadow: isBackgroundGallery ? "0 32px 100px rgba(0,0,0,.48)" : "0 28px 80px rgba(67,86,103,.16)" }} />
      </section>
    </main>
  );
}

function InfoChip({ label, value, dark = false }: { label: string; value: string; dark?: boolean }) {
  return (
    <div style={{ minHeight: "54px", padding: "10px 12px", border: dark ? "1px solid rgba(230,246,250,.14)" : "1px solid rgba(90,110,128,.14)", borderRadius: "18px", background: dark ? "rgba(16,26,30,.50)" : "rgba(255,255,255,.62)", boxShadow: dark ? "0 18px 60px rgba(0,0,0,.28)" : undefined, backdropFilter: dark ? "blur(16px) saturate(128%)" : undefined }}>
      <div style={{ fontSize: "11px", letterSpacing: ".1em", textTransform: "uppercase", color: dark ? "rgba(189,248,255,.70)" : "#71909f", fontWeight: 850 }}>{label}</div>
      <div style={{ marginTop: "4px", fontSize: "13px", color: dark ? "#edf8fb" : "#274253", fontWeight: 780, wordBreak: "break-word" }}>{value}</div>
    </div>
  );
}

function makePillStyle(dark: boolean): CSSProperties {
  return { display: "inline-flex", alignItems: "center", justifyContent: "center", minHeight: "48px", borderRadius: "999px", padding: "0 15px", border: dark ? "1px solid rgba(105,242,255,.24)" : "1px solid rgba(57,117,181,.22)", background: dark ? "rgba(105,242,255,.09)" : "rgba(241,248,253,.80)", color: dark ? "#bdf8ff" : "#2b628f", fontSize: "13px", fontWeight: 850, textDecoration: "none", boxShadow: dark ? "inset 0 1px 0 rgba(255,255,255,.14)" : undefined };
}
