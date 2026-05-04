#!/usr/bin/env node
/*
  PRISMA Black Visual Governance 01E Checker Hotfix 00A
  Read-only checker. It does not modify files.

  Fixes:
  - Uses native ES module imports because this repository treats .mjs as ESM.
  - Supports --root <path> as originally documented.
*/

import fs from 'node:fs';
import path from 'node:path';
import process from 'node:process';

function parseArgs(argv) {
  const args = argv.slice(2);
  const parsed = {
    root: process.cwd(),
    json: true,
    help: false,
  };

  for (let index = 0; index < args.length; index += 1) {
    const value = args[index];

    if (value === '--help' || value === '-h') {
      parsed.help = true;
      continue;
    }

    if (value === '--root') {
      const next = args[index + 1];
      if (!next || next.startsWith('--')) {
        throw new Error('Falta valor para --root');
      }
      parsed.root = next;
      index += 1;
      continue;
    }

    if (value.startsWith('--root=')) {
      parsed.root = value.slice('--root='.length);
      continue;
    }

    if (value === '--text') {
      parsed.json = false;
      continue;
    }

    if (!value.startsWith('--') && parsed.root === process.cwd()) {
      parsed.root = value;
      continue;
    }

    throw new Error(`Argumento no reconocido: ${value}`);
  }

  parsed.root = path.resolve(parsed.root);
  return parsed;
}

function printHelp() {
  console.log(`PRISMA Black Visual Governance 01E checker\n\nUso:\n  node tools/prisma/verify_prisma_black_visual_governance_01e.mjs --root <terminal-de-venta-system>\n\nOpciones:\n  --root <path>   Raíz del proyecto terminal-de-venta-system\n  --text          Salida resumida para consola\n  --help          Mostrar ayuda\n`);
}

const required = [
  'docs/design/PRISMA_BLACK_VISUAL_GOVERNANCE_BASELINE_01E.md',
  'docs/qa/PRISMA_BLACK_LAYER_QA_CHECKLIST_01E.md',
  'shared/contracts/ui/prisma-black-layer-governance.contract.json',
  'manifests/PRISMA_BLACK_VISUAL_GOVERNANCE_BASELINE_01E.manifest.json',
];

const cssFiles = [
  'products/shared-ui/prisma/tokens/prisma-theme.css',
  'products/shared-ui/prisma/components/prisma-components.css',
  'products/tablet/app/components/tablet-shell/prisma-tablet-shell.module.css',
  'products/tablet/app/components/pos/pos.module.css',
  'products/pc/app/app/globals.css',
  'products/tablet/app/app/globals.css',
];

function exists(root, rel) {
  return fs.existsSync(path.join(root, rel));
}

function read(root, rel) {
  const abs = path.join(root, rel);
  return fs.existsSync(abs) ? fs.readFileSync(abs, 'utf8') : '';
}

function countMatches(text, expression) {
  return (text.match(expression) || []).length;
}

function run() {
  const args = parseArgs(process.argv);
  if (args.help) {
    printHelp();
    return 0;
  }

  const result = {
    checker: 'PRISMA_BLACK_VISUAL_GOVERNANCE_01E_CHECKER_HOTFIX_00A',
    root: args.root,
    ok: true,
    requiredFiles: [],
    cssScan: [],
    warnings: [],
    summary: '',
  };

  if (!fs.existsSync(args.root) || !fs.statSync(args.root).isDirectory()) {
    result.ok = false;
    result.summary = `Root no existe o no es carpeta: ${args.root}`;
    console.log(JSON.stringify(result, null, 2));
    return 1;
  }

  for (const rel of required) {
    const present = exists(args.root, rel);
    result.requiredFiles.push({ file: rel, present });
    if (!present) result.ok = false;
  }

  for (const rel of cssFiles) {
    const text = read(args.root, rel);
    if (!text) {
      result.cssScan.push({ file: rel, present: false });
      continue;
    }

    const metrics = {
      file: rel,
      present: true,
      backdropFilterCount: countMatches(text, /backdrop-filter/g),
      beforePseudoCount: countMatches(text, /::before/g),
      afterPseudoCount: countMatches(text, /::after/g),
      animationCount: countMatches(text, /animation\s*:/g),
      radialGradientCount: countMatches(text, /radial-gradient/g),
      mixBlendModeCount: countMatches(text, /mix-blend-mode/g),
    };

    result.cssScan.push(metrics);

    if (metrics.animationCount > 8) {
      result.warnings.push(`${rel}: muchas animaciones detectadas (${metrics.animationCount}). Revisar presupuesto motion.`);
    }
    if (metrics.mixBlendModeCount > 6) {
      result.warnings.push(`${rel}: muchos mix-blend-mode detectados (${metrics.mixBlendModeCount}). Revisar sopa de capas.`);
    }
    if (metrics.radialGradientCount > 35) {
      result.warnings.push(`${rel}: muchos radial-gradient detectados (${metrics.radialGradientCount}). Revisar duplicación de haze/glow.`);
    }
  }

  result.summary = result.ok
    ? 'PRISMA visual governance baseline está instalado. Warnings son guía, no fallo automático.'
    : 'Faltan archivos de gobierno visual 01E.';

  if (args.json) {
    console.log(JSON.stringify(result, null, 2));
  } else {
    console.log(result.summary);
    console.log(`Root: ${result.root}`);
    console.log(`Required files: ${result.requiredFiles.filter((item) => item.present).length}/${result.requiredFiles.length}`);
    console.log(`CSS scanned: ${result.cssScan.filter((item) => item.present).length}/${result.cssScan.length}`);
    console.log(`Warnings: ${result.warnings.length}`);
    for (const warning of result.warnings) console.log(`- ${warning}`);
  }

  return result.ok ? 0 : 1;
}

try {
  process.exit(run());
} catch (error) {
  console.error(JSON.stringify({
    checker: 'PRISMA_BLACK_VISUAL_GOVERNANCE_01E_CHECKER_HOTFIX_00A',
    ok: false,
    error: error instanceof Error ? error.message : String(error),
  }, null, 2));
  process.exit(1);
}
