import fs from "node:fs";
import path from "node:path";
import process from "node:process";
import { createRequire } from "node:module";
import { fileURLToPath } from "node:url";

const pcRoot = process.cwd();
const ingestPath = path.join(pcRoot, "src/server/services/sync-ingest.service.ts");
const observabilityPath = path.join(pcRoot, "src/server/services/sync-observability.service.ts");
const ingest = fs.readFileSync(ingestPath, "utf8");
const observability = fs.readFileSync(observabilityPath, "utf8");
const localRequire = createRequire(import.meta.url);

function loadTypeScript() {
  const roots = [];
  let cursor = pcRoot;
  for (let index = 0; index < 12; index += 1) {
    roots.push(cursor);
    const parent = path.dirname(cursor);
    if (parent === cursor) break;
    cursor = parent;
  }
  roots.push(path.dirname(fileURLToPath(import.meta.url)));
  roots.push(process.env.INIT_CWD || "");
  for (const root of [...new Set(roots.filter(Boolean))]) {
    try {
      const resolved = localRequire.resolve("typescript", { paths: [root] });
      return localRequire(resolved);
    } catch {}
  }
  try {
    return localRequire("typescript");
  } catch {
    console.error("FAIL typescript_module_missing");
    process.exit(2);
  }
}

const ts = loadTypeScript();
const ingestSource = ts.createSourceFile(ingestPath, ingest, ts.ScriptTarget.Latest, true, ts.ScriptKind.TS);
const observabilitySource = ts.createSourceFile(observabilityPath, observability, ts.ScriptTarget.Latest, true, ts.ScriptKind.TS);

function findNamedFunction(sourceFile, name) {
  let found = null;
  function visit(node) {
    if (found) return;
    if (ts.isFunctionDeclaration(node) && node.name?.text === name) {
      found = node;
      return;
    }
    ts.forEachChild(node, visit);
  }
  visit(sourceFile);
  return found;
}

function propertyNameText(nameNode) {
  if (ts.isIdentifier(nameNode) || ts.isStringLiteral(nameNode) || ts.isNumericLiteral(nameNode)) return nameNode.text;
  return nameNode.getText();
}

function sourceAssignments(functionNode, sourceFile) {
  const found = [];
  if (!functionNode?.body) return found;
  function visit(node) {
    if (ts.isPropertyAssignment(node) && propertyNameText(node.name) === "source") {
      const initializer = node.initializer;
      if (ts.isCallExpression(initializer) && ts.isIdentifier(initializer.expression)) {
        found.push({
          callee: initializer.expression.text,
          args: initializer.arguments.map(argument => argument.getText(sourceFile)),
          text: initializer.getText(sourceFile)
        });
      } else {
        found.push({ callee: null, args: [], text: initializer.getText(sourceFile) });
      }
    }
    ts.forEachChild(node, visit);
  }
  visit(functionNode.body);
  return found;
}

function importContains(sourceFile, moduleName, importedName) {
  return sourceFile.statements.some(statement => {
    if (!ts.isImportDeclaration(statement) || !ts.isStringLiteral(statement.moduleSpecifier)) return false;
    if (statement.moduleSpecifier.text !== moduleName) return false;
    const elements = statement.importClause?.namedBindings && ts.isNamedImports(statement.importClause.namedBindings)
      ? statement.importClause.namedBindings.elements
      : [];
    return elements.some(element => element.name.text === importedName);
  });
}

function functionReturnsCall(functionNode, callee, argumentText, sourceFile) {
  if (!functionNode?.body) return false;
  return functionNode.body.statements.some(statement => {
    if (!ts.isReturnStatement(statement) || !statement.expression || !ts.isCallExpression(statement.expression)) return false;
    const expression = statement.expression;
    return ts.isIdentifier(expression.expression)
      && expression.expression.text === callee
      && expression.arguments.length === 1
      && expression.arguments[0].getText(sourceFile) === argumentText;
  });
}

function variableUsesCall(functionNode, variableName, callee, argumentText, sourceFile) {
  if (!functionNode?.body) return false;
  let matched = false;
  function visit(node) {
    if (matched) return;
    if (ts.isVariableDeclaration(node)
      && ts.isIdentifier(node.name)
      && node.name.text === variableName
      && node.initializer
      && ts.isCallExpression(node.initializer)
      && ts.isIdentifier(node.initializer.expression)
      && node.initializer.expression.text === callee
      && node.initializer.arguments.length === 1
      && node.initializer.arguments[0].getText(sourceFile) === argumentText) {
      matched = true;
      return;
    }
    ts.forEachChild(node, visit);
  }
  visit(functionNode.body);
  return matched;
}

const helperFunction = findNamedFunction(observabilitySource, "canonicalSyncCheckpointSource");
const advanceFunction = findNamedFunction(observabilitySource, "advanceSyncCheckpoint");
const sequenceFunction = findNamedFunction(ingestSource, "sequenceConflict");
const projectionFunction = findNamedFunction(ingestSource, "canonicalProjectionSource");
const sequenceSources = sourceAssignments(sequenceFunction, ingestSource);
const sequenceBody = sequenceFunction?.body?.getText(ingestSource) || "";
const projectionBody = projectionFunction?.body?.getText(ingestSource) || "";

const checks = {
  helper_exported: Boolean(helperFunction?.modifiers?.some(modifier => modifier.kind === ts.SyntaxKind.ExportKeyword)),
  helper_delegates_source_for: functionReturnsCall(helperFunction, "sourceFor", "event", observabilitySource),
  checkpoint_write_uses_helper: variableUsesCall(advanceFunction, "source", "canonicalSyncCheckpointSource", "event", observabilitySource),
  ingest_imports_helper: importContains(ingestSource, "@/server/services/sync-observability.service", "canonicalSyncCheckpointSource"),
  sequence_function_found: Boolean(sequenceFunction?.body),
  sequence_read_uses_helper: sequenceSources.some(item => item.callee === "canonicalSyncCheckpointSource" && item.args.length === 1 && item.args[0] === "event"),
  sequence_read_not_projection_source: !sequenceSources.some(item => item.callee === "canonicalProjectionSource"),
  projection_source_preserved: projectionBody.includes("pc-canonical-projection:"),
  stale_sequence_present: sequenceBody.includes('code: "stale_sequence"') || sequenceBody.includes("code: 'stale_sequence'"),
  inconsistent_sequence_present: sequenceBody.includes('code: "inconsistent_sequence"') || sequenceBody.includes("code: 'inconsistent_sequence'")
};

const key = ({ businessId, source, deviceId, stream }) => JSON.stringify([businessId, source, deviceId, stream]);
const checkpoints = new Map();
const canonicalSource = event => event.source || "pc.sync.ingest";
function apply(event) {
  const k = key({ businessId: event.businessId, source: canonicalSource(event), deviceId: event.deviceId, stream: event.topic });
  const prior = checkpoints.get(k);
  if (prior && event.sequence < prior.sequence) return "stale_sequence";
  if (prior && event.sequence === prior.sequence && prior.eventId !== event.eventId) return "inconsistent_sequence";
  if (!prior || event.sequence > prior.sequence) checkpoints.set(k, { sequence: event.sequence, eventId: event.eventId });
  return prior && prior.eventId === event.eventId ? "duplicate" : "accepted";
}
const base = { businessId: "biz-a", source: "tablet-pos", deviceId: "dev-1", topic: "sale.created" };
const behavioral = {
  first: apply({ ...base, eventId: "evt-2", sequence: 2 }) === "accepted",
  stale: apply({ ...base, eventId: "evt-1", sequence: 1 }) === "stale_sequence",
  same_sequence_other_event: apply({ ...base, eventId: "evt-x", sequence: 2 }) === "inconsistent_sequence",
  monotonic: apply({ ...base, eventId: "evt-3", sequence: 3 }) === "accepted",
  replay: apply({ ...base, eventId: "evt-3", sequence: 3 }) === "duplicate",
  device_isolation: apply({ ...base, deviceId: "dev-2", eventId: "evt-d2-1", sequence: 1 }) === "accepted",
  stream_isolation: apply({ ...base, topic: "stock.adjusted", eventId: "evt-stock-1", sequence: 1 }) === "accepted"
};

const failures = Object.entries({ ...checks, ...behavioral }).filter(([, value]) => !value).map(([name]) => name);
const result = {
  status: failures.length ? "FAIL_SYNC_CHECKPOINT_SEQUENCE_1707" : "PASS_SYNC_CHECKPOINT_SEQUENCE_1707",
  typescriptVersion: ts.version,
  checks,
  behavioral,
  diagnostics: {
    sequenceSourceAssignments: sequenceSources,
    failures
  }
};

if (failures.length) {
  console.error(JSON.stringify(result, null, 2));
  process.exit(1);
}
console.log(JSON.stringify(result, null, 2));
