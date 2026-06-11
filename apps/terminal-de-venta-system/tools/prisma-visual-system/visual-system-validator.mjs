import { execFileSync } from 'node:child_process';
import { existsSync, mkdirSync, readFileSync, readdirSync, statSync, writeFileSync } from 'node:fs';
import { createRequire } from 'node:module';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const appRoot = path.resolve(scriptDir, '..', '..');
const repoRoot = path.resolve(appRoot, '..', '..');
const configRoot = path.join(appRoot, 'config', 'prisma-visual-system');
const requireFromRepo = createRequire(path.join(repoRoot, 'package.json'));

const requiredDocs = [
  'docs/design/prisma-visual-system/PRISMA_VISUAL_SYSTEM_MASTER.md',
  'docs/design/prisma-visual-system/PRISMA_COMPONENT_CATALOG.md',
  'docs/design/prisma-visual-system/PRISMA_SURFACE_ADAPTERS.md',
  'docs/design/prisma-visual-system/PRISMA_TOKENS_AND_RECIPES.md',
  'docs/design/prisma-visual-system/PRISMA_INJECTION_TEMPLATES.md',
  'docs/design/prisma-visual-system/PRISMA_MIGRATION_PLAYBOOK.md',
  'docs/design/prisma-visual-system/PRISMA_VISUAL_QA_MATRIX.md',
  'docs/design/prisma-visual-system/PRISMA_DONE_DEFINITION.md',
];

const requiredRegistries = [
  'components.registry.json',
  'surface-adapters.registry.json',
  'tokens.registry.json',
  'recipes.registry.json',
  'route-bindings.registry.json',
  'future-components.registry.json',
  'no-touch.registry.json',
  'migration-candidates.registry.json',
];

const requiredSchemas = [
  'component.schema.json',
  'surface-adapter.schema.json',
  'token.schema.json',
  'recipe.schema.json',
  'route-binding.schema.json',
  'migration-candidate.schema.json',
  'visual-qa.schema.json',
  'result-fail.schema.json',
];

const requiredTemplates = [
  'new-tablet-screen.template.md',
  'new-pc-screen.template.md',
  'new-mobile-screen.template.md',
  'new-shell.template.md',
  'new-card.template.md',
  'new-panel.template.md',
  'new-state.template.md',
  'new-data-display.template.md',
  'migrate-legacy-css.template.md',
  'split-choncho-css.template.md',
  'add-future-component-family.template.md',
];

const allowedTouchedPrefixes = [
  'apps/terminal-de-venta-system/docs/design/prisma-visual-system/',
  'apps/terminal-de-venta-system/config/prisma-visual-system/',
  'apps/terminal-de-venta-system/products/shared-ui/prisma/adapters/',
  'apps/terminal-de-venta-system/products/shared-ui/prisma/templates/',
  'apps/terminal-de-venta-system/tools/prisma-visual-system/',
];

function parseArgs(argv) {
  const args = { outDir: path.join('F:', 'descargasf', 'visualcat-validation'), resultManifest: '', resultZip: '' };
  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i];
    if (arg === '--out-dir') {
      args.outDir = argv[i + 1];
      i += 1;
    } else if (arg === '--result-manifest') {
      args.resultManifest = argv[i + 1];
      i += 1;
    } else if (arg === '--result-zip') {
      args.resultZip = argv[i + 1];
      i += 1;
    }
  }
  return args;
}

function appPath(relativePath) {
  return path.join(appRoot, relativePath);
}

function repoRelative(filePath) {
  return path.relative(repoRoot, filePath).replaceAll(path.sep, '/');
}

function readJson(relativePath) {
  return JSON.parse(readFileSync(appPath(relativePath), 'utf8'));
}

function listJsonFiles(dir) {
  const files = [];
  for (const entry of readdirSync(dir, { withFileTypes: true })) {
    const fullPath = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      files.push(...listJsonFiles(fullPath));
    } else if (entry.isFile() && entry.name.endsWith('.json')) {
      files.push(fullPath);
    }
  }
  return files;
}

function loadAjvConstructor() {
  const tryLoad = (specifier) => {
    try {
      const mod = requireFromRepo(specifier);
      return mod?.default ?? mod;
    } catch {
      return null;
    }
  };

  // Draft 2020-12 schemas require the Ajv 2020 entrypoint. The default
  // Ajv export is draft-07 oriented in common Ajv v8 installs and can fail with:
  // no schema with key or ref "https://json-schema.org/draft/2020-12/schema"
  return (
    tryLoad('ajv/dist/2020') ??
    tryLoad('ajv/dist/2019') ??
    tryLoad('ajv')
  );
}

function schemaDeclares202012(schema) {
  return String(schema?.$schema ?? '').includes('2020-12');
}

function createSchemaValidator(checks) {
  const AjvCtor = loadAjvConstructor();

  if (!AjvCtor) {
    pushCheck(checks, 'schema_engine:ajv', 'SKIPPED', 'Ajv is not available from repo dependencies; falling back to required-field validation.');
    return (id, schema, items) => checkRequiredFields(checks, `schema_validate:${id}`, items, schema.required ?? []);
  }

  let ajv;
  try {
    ajv = new AjvCtor({ allErrors: true, strict: false });
    pushCheck(checks, 'schema_engine:ajv', 'PASS', 'ajv loaded from repo dependencies with 2020-12 capable entrypoint when available');
  } catch (error) {
    pushCheck(checks, 'schema_engine:ajv', 'SKIPPED', `Ajv constructor failed: ${error instanceof Error ? error.message : String(error)}`);
    return (id, schema, items) => checkRequiredFields(checks, `schema_validate:${id}`, items, schema.required ?? []);
  }

  return (id, schema, items) => {
    let validate;
    try {
      validate = ajv.compile(schema);
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error);
      if (schemaDeclares202012(schema) && message.includes('draft/2020-12')) {
        pushCheck(
          checks,
          `schema_validate:${id}`,
          'FAIL',
          `Ajv 2020-12 meta-schema unavailable even after 2020 entrypoint attempt: ${message}`,
        );
        return;
      }
      pushCheck(checks, `schema_validate:${id}`, 'FAIL', `schema compile failed: ${message}`);
      return;
    }

    const errors = [];
    for (const [index, item] of items.entries()) {
      if (!validate(item)) {
        errors.push(`${index}:${ajv.errorsText(validate.errors, { separator: '; ' })}`);
      }
    }
    pushCheck(checks, `schema_validate:${id}`, errors.length === 0 ? 'PASS' : 'FAIL', errors.join(' | '));
  };
}

function uniqueValues(items, key) {
  const seen = new Set();
  const duplicates = new Set();
  for (const item of items) {
    const value = item?.[key];
    if (seen.has(value)) duplicates.add(value);
    seen.add(value);
  }
  return [...duplicates];
}

function gitStatusFiles() {
  const output = execFileSync('git', ['-C', repoRoot, 'status', '--porcelain=v1', '--untracked-files=all', '--', 'apps/terminal-de-venta-system'], {
    encoding: 'utf8',
  });
  return output
    .split(/\r?\n/)
    .map((line) => line.trimEnd())
    .filter(Boolean)
    .map((line) => {
      const rawPath = line.slice(3);
      return rawPath.includes(' -> ') ? rawPath.split(' -> ').at(-1) : rawPath;
    })
    .map((file) => file.replaceAll('\\', '/'));
}

function fileLooksText(filePath) {
  const ext = path.extname(filePath).toLowerCase();
  return ['.css', '.scss', '.sass', '.ts', '.tsx', '.js', '.mjs', '.json', '.md'].includes(ext) || ext === '';
}

function fileLooksRuntime(filePath) {
  const ext = path.extname(filePath).toLowerCase();
  return ['.css', '.scss', '.sass', '.ts', '.tsx', '.js', '.mjs'].includes(ext);
}

function pushCheck(checks, id, status, details = '') {
  checks.push({ id, status, details });
}

function checkRequiredFields(checks, id, items, requiredFields) {
  const missing = [];
  for (const [index, item] of items.entries()) {
    for (const field of requiredFields) {
      if (!(field in item)) missing.push(`${index}:${field}`);
    }
  }
  pushCheck(checks, id, missing.length === 0 ? 'PASS' : 'FAIL', missing.join(', '));
}

function validateResultManifest(manifestPath, zipPath, checks) {
  if (!manifestPath && !zipPath) {
    pushCheck(checks, 'result_zip_contract', 'SKIPPED', 'Run again with --result-manifest and --result-zip after packaging.');
    return;
  }

  if (!manifestPath || !existsSync(manifestPath)) {
    pushCheck(checks, 'result_manifest_exists', 'FAIL', manifestPath || 'missing --result-manifest');
    return;
  }

  if (!zipPath || !existsSync(zipPath)) {
    pushCheck(checks, 'result_zip_exists', 'FAIL', zipPath || 'missing --result-zip');
    return;
  }

  const manifest = JSON.parse(readFileSync(manifestPath, 'utf8'));
  const required = readJson('config/prisma-visual-system/schemas/result-fail.schema.json').required ?? [];
  const missing = required.filter((field) => !(field in manifest));
  pushCheck(checks, 'result_zip_contract', missing.length === 0 ? 'PASS' : 'FAIL', missing.join(', '));
}

function runValidation(mode, args) {
  const checks = [];
  const validateSchema = createSchemaValidator(checks);

  for (const file of requiredDocs) {
    pushCheck(checks, `doc_exists:${file}`, existsSync(appPath(file)) ? 'PASS' : 'FAIL');
  }

  for (const file of requiredRegistries) {
    pushCheck(checks, `registry_exists:${file}`, existsSync(path.join(configRoot, file)) ? 'PASS' : 'FAIL');
  }

  for (const file of requiredSchemas) {
    pushCheck(checks, `schema_exists:${file}`, existsSync(path.join(configRoot, 'schemas', file)) ? 'PASS' : 'FAIL');
  }

  for (const file of listJsonFiles(configRoot)) {
    try {
      JSON.parse(readFileSync(file, 'utf8'));
      pushCheck(checks, `json_parse:${repoRelative(file)}`, 'PASS');
    } catch (error) {
      pushCheck(checks, `json_parse:${repoRelative(file)}`, 'FAIL', error.message);
    }
  }

  const componentRegistry = readJson('config/prisma-visual-system/components.registry.json');
  const componentSchema = readJson('config/prisma-visual-system/schemas/component.schema.json');
  const components = componentRegistry.components ?? [];
  checkRequiredFields(checks, 'components_required_fields', components, componentSchema.required ?? []);
  validateSchema('components', componentSchema, components);
  pushCheck(checks, 'component_ids_unique', uniqueValues(components, 'id').length === 0 ? 'PASS' : 'FAIL', uniqueValues(components, 'id').join(', '));
  const liveWithoutEvidence = components.filter((component) => component.status === 'live' && !Array.isArray(component.evidencePaths));
  pushCheck(checks, 'live_components_have_evidence', liveWithoutEvidence.length === 0 ? 'PASS' : 'FAIL', liveWithoutEvidence.map((component) => component.id).join(', '));

  const adaptersRegistry = readJson('config/prisma-visual-system/surface-adapters.registry.json');
  const adapterSchema = readJson('config/prisma-visual-system/schemas/surface-adapter.schema.json');
  const adapters = adaptersRegistry.adapters ?? [];
  checkRequiredFields(checks, 'adapters_required_fields', adapters, adapterSchema.required ?? []);
  validateSchema('surface-adapters', adapterSchema, adapters);
  pushCheck(checks, 'adapter_ids_unique', uniqueValues(adapters, 'surfaceId').length === 0 ? 'PASS' : 'FAIL', uniqueValues(adapters, 'surfaceId').join(', '));
  const unsafePrefixes = adapters.filter((adapter) => String(adapter.runtimeBackgroundPrefix ?? '').includes('products/0.backgrounds'));
  pushCheck(checks, 'runtime_background_prefixes_public_safe', unsafePrefixes.length === 0 ? 'PASS' : 'FAIL', unsafePrefixes.map((adapter) => adapter.surfaceId).join(', '));

  const adapterDocsMissing = adapters
    .map((adapter) => {
      const suffix = adapter.status === 'reserved' ? '.reserved.adapter.md' : '.adapter.md';
      return `products/shared-ui/prisma/adapters/${adapter.surfaceId}${suffix}`;
    })
    .filter((file) => !existsSync(appPath(file)));
  pushCheck(checks, 'adapter_docs_exist', adapterDocsMissing.length === 0 ? 'PASS' : 'FAIL', adapterDocsMissing.join(', '));

  const tokens = readJson('config/prisma-visual-system/tokens.registry.json').tokens ?? [];
  const tokenSchema = readJson('config/prisma-visual-system/schemas/token.schema.json');
  checkRequiredFields(checks, 'tokens_required_fields', tokens, tokenSchema.required ?? []);
  validateSchema('tokens', tokenSchema, tokens);
  pushCheck(checks, 'token_ids_unique', uniqueValues(tokens, 'id').length === 0 ? 'PASS' : 'FAIL', uniqueValues(tokens, 'id').join(', '));

  const recipes = readJson('config/prisma-visual-system/recipes.registry.json').recipes ?? [];
  const recipeSchema = readJson('config/prisma-visual-system/schemas/recipe.schema.json');
  checkRequiredFields(checks, 'recipes_required_fields', recipes, recipeSchema.required ?? []);
  validateSchema('recipes', recipeSchema, recipes);
  pushCheck(checks, 'recipe_ids_unique', uniqueValues(recipes, 'id').length === 0 ? 'PASS' : 'FAIL', uniqueValues(recipes, 'id').join(', '));

  const routeBindings = readJson('config/prisma-visual-system/route-bindings.registry.json').bindings ?? [];
  const routeSchema = readJson('config/prisma-visual-system/schemas/route-binding.schema.json');
  checkRequiredFields(checks, 'route_bindings_required_fields', routeBindings, routeSchema.required ?? []);
  validateSchema('route-bindings', routeSchema, routeBindings);
  const adapterStatus = new Map(adapters.map((adapter) => [adapter.surfaceId, adapter.status]));
  const activeReservedBindings = routeBindings.filter((binding) => adapterStatus.get(binding.surface) === 'reserved' && ['mapped', 'live', 'active'].includes(binding.status));
  pushCheck(checks, 'reserved_surfaces_not_active_route_bindings', activeReservedBindings.length === 0 ? 'PASS' : 'FAIL', activeReservedBindings.map((binding) => `${binding.surface}:${binding.route}`).join(', '));

  const futureComponents = readJson('config/prisma-visual-system/future-components.registry.json').future ?? [];
  const activeFuture = futureComponents.filter((component) => ['live', 'mapped', 'active'].includes(component.status));
  pushCheck(checks, 'future_components_not_live', activeFuture.length === 0 ? 'PASS' : 'FAIL', activeFuture.map((component) => component.id).join(', '));

  const migrationCandidates = readJson('config/prisma-visual-system/migration-candidates.registry.json').candidates ?? [];
  const migrationSchema = readJson('config/prisma-visual-system/schemas/migration-candidate.schema.json');
  checkRequiredFields(checks, 'migration_candidates_required_fields', migrationCandidates, migrationSchema.required ?? []);
  validateSchema('migration-candidates', migrationSchema, migrationCandidates);

  for (const file of requiredTemplates) {
    pushCheck(checks, `template_exists:${file}`, existsSync(appPath(`products/shared-ui/prisma/templates/${file}`)) ? 'PASS' : 'FAIL');
  }

  const changedFiles = gitStatusFiles();
  const outOfScope = changedFiles.filter((file) => !allowedTouchedPrefixes.some((prefix) => file.startsWith(prefix)));
  pushCheck(checks, 'touched_files_within_allowed_scope', outOfScope.length === 0 ? 'PASS' : 'FAIL', outOfScope.join(', '));

  const forbiddenHits = [];
  for (const file of changedFiles) {
    const fullPath = path.join(repoRoot, file);
    if (!existsSync(fullPath) || !statSync(fullPath).isFile() || !fileLooksText(fullPath)) continue;
    const ext = path.extname(fullPath).toLowerCase();
    const text = readFileSync(fullPath, 'utf8');
    if (['.css', '.scss', '.sass'].includes(ext) && text.includes('!important')) {
      forbiddenHits.push(`${file}: final-important`);
    }
    if (fileLooksRuntime(fullPath) && !file.includes('/tools/prisma-visual-system/') && text.includes('products/0.backgrounds')) {
      forbiddenHits.push(`${file}: private-background-runtime-path`);
    }
  }
  pushCheck(checks, 'forbidden_pattern_scan_changed_files', forbiddenHits.length === 0 ? 'PASS' : 'FAIL', forbiddenHits.join(', '));

  validateResultManifest(args.resultManifest, args.resultZip, checks);

  const failures = checks.filter((check) => check.status === 'FAIL');
  const skipped = checks.filter((check) => check.status === 'SKIPPED');
  const summary = {
    mode,
    generated_at: new Date().toISOString(),
    classification: failures.length === 0 ? 'PASS_STRUCTURAL_ONLY' : 'FAIL',
    visual_qa: 'SKIPPED_NO_LIVE_SERVER',
    repo_root: repoRoot,
    app_root: appRoot,
    checks,
    totals: {
      pass: checks.filter((check) => check.status === 'PASS').length,
      fail: failures.length,
      skipped: skipped.length,
    },
  };

  mkdirSync(args.outDir, { recursive: true });
  const jsonPath = path.join(args.outDir, `visual-system-validation.${mode}.json`);
  const mdPath = path.join(args.outDir, `visual-system-validation.${mode}.md`);
  writeFileSync(jsonPath, `${JSON.stringify(summary, null, 2)}\n`);
  writeFileSync(
    mdPath,
    [
      `# PRISMA Visual System Validation (${mode})`,
      '',
      `- Classification: ${summary.classification}`,
      `- Visual QA: ${summary.visual_qa}`,
      `- PASS: ${summary.totals.pass}`,
      `- FAIL: ${summary.totals.fail}`,
      `- SKIPPED: ${summary.totals.skipped}`,
      '',
      '| Check | Status | Details |',
      '|---|---|---|',
      ...checks.map((check) => `| \`${check.id}\` | ${check.status} | ${String(check.details ?? '').replaceAll('|', '\\|')} |`),
      '',
    ].join('\n'),
  );

  return { summary, jsonPath, mdPath };
}

export function runCli(mode = 'all') {
  const args = parseArgs(process.argv.slice(2));
  try {
    const result = runValidation(mode, args);
    console.log(JSON.stringify({ classification: result.summary.classification, json: result.jsonPath, md: result.mdPath }, null, 2));
    if (result.summary.totals.fail > 0) process.exitCode = 1;
  } catch (error) {
    console.error(error instanceof Error ? error.message : String(error));
    process.exitCode = 1;
  }
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  runCli('all');
}
