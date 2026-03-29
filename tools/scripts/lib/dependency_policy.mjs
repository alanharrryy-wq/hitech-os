#!/usr/bin/env node
import { existsSync, readdirSync, readFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

export const WORKSPACE_DEP_SECTIONS = [
  "dependencies",
  "devDependencies",
  "peerDependencies",
  "optionalDependencies"
];

export function toPosix(value) {
  return value.replace(/\\/g, "/");
}

export function resolveRepoRoot(importMetaUrl) {
  const thisFile = fileURLToPath(importMetaUrl);
  const thisDir = path.dirname(thisFile);
  let cursor = thisDir;
  for (let depth = 0; depth < 8; depth += 1) {
    const hasWorkspace = existsSync(path.join(cursor, "pnpm-workspace.yaml"));
    const hasRootManifest = existsSync(path.join(cursor, "package.json"));
    if (hasWorkspace && hasRootManifest) {
      return cursor;
    }

    const parent = path.dirname(cursor);
    if (parent === cursor) {
      break;
    }
    cursor = parent;
  }

  return path.resolve(thisDir, "../..");
}

export function readJsonAt(repoRoot, relativePath) {
  const absolutePath = path.resolve(repoRoot, relativePath);
  return JSON.parse(readFileSync(absolutePath, "utf8"));
}

function normalizePattern(rawPattern) {
  return toPosix(String(rawPattern ?? "").trim().replace(/^["']|["']$/g, ""));
}

function uniqueSorted(values) {
  return [...new Set(values)].sort((left, right) => left.localeCompare(right));
}

export function parsePnpmWorkspacePatterns(repoRoot, workspaceFile = "pnpm-workspace.yaml") {
  const workspacePath = path.resolve(repoRoot, workspaceFile);
  if (!existsSync(workspacePath)) {
    return [];
  }

  const text = readFileSync(workspacePath, "utf8");
  const lines = text.split(/\r?\n/);
  const patterns = [];
  let inPackagesBlock = false;

  for (const rawLine of lines) {
    const line = rawLine.trim();
    if (!line || line.startsWith("#")) {
      continue;
    }

    if (!inPackagesBlock) {
      if (line === "packages:" || line.startsWith("packages:")) {
        inPackagesBlock = true;
      }
      continue;
    }

    if (!line.startsWith("-")) {
      if (!rawLine.startsWith(" ") && !rawLine.startsWith("\t")) {
        break;
      }
      continue;
    }

    const value = normalizePattern(line.slice(1).trim());
    if (value) {
      patterns.push(value);
    }
  }

  return uniqueSorted(patterns);
}

export function workspaceRootsFromPatterns(patterns) {
  const roots = [];
  for (const rawPattern of patterns) {
    const pattern = normalizePattern(rawPattern);
    if (!pattern) {
      continue;
    }

    if (pattern.endsWith("/*")) {
      const root = pattern.slice(0, -2).replace(/\/+$/, "");
      if (root) {
        roots.push(root);
      }
      continue;
    }

    if (!pattern.includes("*")) {
      roots.push(pattern.replace(/\/+$/, ""));
      continue;
    }

    const first = pattern.split("/", 1)[0];
    if (first && !first.includes("*")) {
      roots.push(first);
    }
  }

  return uniqueSorted(roots.filter((value) => value.length > 0));
}

export function validateDependenciesPolicy(policy) {
  const errors = [];
  const warnings = [];

  if (!policy || typeof policy !== "object") {
    return {
      errors: ["policy is missing or not a JSON object"],
      warnings
    };
  }

  if (policy.policy_id !== "dependencies") {
    errors.push("policy_id must equal 'dependencies'");
  }

  const workspaceRoots = Array.isArray(policy.workspace_roots)
    ? policy.workspace_roots.map((value) => normalizePattern(value)).filter(Boolean)
    : [];

  if (workspaceRoots.length === 0) {
    errors.push("workspace_roots must be a non-empty array");
  }

  if (
    Object.prototype.hasOwnProperty.call(policy, "no_new_cycles") &&
    typeof policy.no_new_cycles !== "boolean"
  ) {
    errors.push("no_new_cycles must be boolean when present");
  }

  const boundaryModel = policy.boundary_model;
  if (!boundaryModel || typeof boundaryModel !== "object" || Array.isArray(boundaryModel)) {
    errors.push("boundary_model must be an object keyed by workspace root");
  } else {
    for (const root of workspaceRoots) {
      const allowed = boundaryModel[root];
      if (!Array.isArray(allowed) || allowed.length === 0) {
        errors.push(`boundary_model.${root} must be a non-empty array`);
        continue;
      }

      for (const candidate of allowed) {
        if (typeof candidate !== "string" || normalizePattern(candidate).length === 0) {
          errors.push(`boundary_model.${root} contains a non-string/empty entry`);
        }
      }
    }

    for (const root of Object.keys(boundaryModel)) {
      if (!workspaceRoots.includes(root)) {
        warnings.push(`boundary_model has root '${root}' missing from workspace_roots`);
      }
    }
  }

  const allowedCycles = policy.allowed_workspace_cycles;
  if (allowedCycles !== undefined) {
    if (!Array.isArray(allowedCycles)) {
      errors.push("allowed_workspace_cycles must be an array");
    } else {
      for (const cycle of allowedCycles) {
        const isValid =
          typeof cycle === "string" ||
          (Array.isArray(cycle) &&
            cycle.length > 0 &&
            cycle.every((item) => typeof item === "string" && item.length > 0));
        if (!isValid) {
          errors.push("allowed_workspace_cycles entries must be strings or string arrays");
          break;
        }
      }
    }
  }

  const policyPatterns = Array.isArray(policy.workspace_patterns)
    ? policy.workspace_patterns.map((value) => normalizePattern(value)).filter(Boolean)
    : [];
  if (policyPatterns.length > 0) {
    const derivedRoots = workspaceRootsFromPatterns(policyPatterns);
    for (const root of workspaceRoots) {
      if (!derivedRoots.includes(root)) {
        warnings.push(`workspace_patterns do not include workspace root '${root}'`);
      }
    }
  }

  const retiredEntries = Array.isArray(policy.retired_workspace_entries)
    ? policy.retired_workspace_entries
    : [];
  for (const entry of retiredEntries) {
    if (typeof entry !== "string" || normalizePattern(entry).length === 0) {
      errors.push("retired_workspace_entries entries must be non-empty strings");
      break;
    }
  }

  if (Object.prototype.hasOwnProperty.call(policy, "boundary_source_scan_roots")) {
    if (!Array.isArray(policy.boundary_source_scan_roots)) {
      errors.push("boundary_source_scan_roots must be an array when present");
    } else {
      for (const root of policy.boundary_source_scan_roots) {
        if (typeof root !== "string" || normalizePattern(root).length === 0) {
          errors.push("boundary_source_scan_roots entries must be non-empty strings");
          break;
        }
      }
    }
  }

  return { errors, warnings };
}

function discoverFromPattern(repoRoot, pattern, projects, packageNameToProject, anomalies) {
  const normalized = normalizePattern(pattern);
  if (!normalized) {
    return;
  }

  if (normalized.endsWith("/*")) {
    const baseRelative = normalized.slice(0, -2).replace(/\/+$/, "");
    const absoluteBase = path.resolve(repoRoot, baseRelative);
    if (!existsSync(absoluteBase)) {
      anomalies.missing_patterns.push(normalized);
      return;
    }

    for (const entry of readdirSync(absoluteBase, { withFileTypes: true })) {
      if (!entry.isDirectory()) {
        continue;
      }

      const absoluteProject = path.join(absoluteBase, entry.name);
      const manifestPath = path.join(absoluteProject, "package.json");
      if (!existsSync(manifestPath)) {
        continue;
      }

      const manifest = JSON.parse(readFileSync(manifestPath, "utf8"));
      const projectPath = toPosix(path.relative(repoRoot, absoluteProject));
      const packageName = String(manifest.name ?? projectPath);
      projects.set(projectPath, {
        path: projectPath,
        root: projectPath.split("/", 1)[0] ?? "unknown",
        packageName,
        manifestPath: toPosix(path.relative(repoRoot, manifestPath)),
        manifest
      });
      packageNameToProject.set(packageName, projectPath);
    }
    return;
  }

  const absoluteEntry = path.resolve(repoRoot, normalized);
  if (!existsSync(absoluteEntry)) {
    anomalies.missing_patterns.push(normalized);
    return;
  }

  const manifestPath = path.join(absoluteEntry, "package.json");
  if (!existsSync(manifestPath)) {
    anomalies.entries_without_manifest.push(normalized);
    return;
  }

  const manifest = JSON.parse(readFileSync(manifestPath, "utf8"));
  const projectPath = toPosix(path.relative(repoRoot, absoluteEntry));
  const packageName = String(manifest.name ?? projectPath);
  projects.set(projectPath, {
    path: projectPath,
    root: projectPath.split("/", 1)[0] ?? "unknown",
    packageName,
    manifestPath: toPosix(path.relative(repoRoot, manifestPath)),
    manifest
  });
  packageNameToProject.set(packageName, projectPath);
}

export function discoverWorkspaceProjects(repoRoot, workspacePatterns) {
  const projects = new Map();
  const packageNameToProject = new Map();
  const anomalies = {
    missing_patterns: [],
    entries_without_manifest: []
  };

  for (const pattern of workspacePatterns) {
    discoverFromPattern(repoRoot, pattern, projects, packageNameToProject, anomalies);
  }

  return {
    projects,
    packageNameToProject,
    anomalies: {
      missing_patterns: uniqueSorted(anomalies.missing_patterns),
      entries_without_manifest: uniqueSorted(anomalies.entries_without_manifest)
    }
  };
}

export function buildWorkspaceDependencyGraph(projects, packageNameToProject) {
  const forward = new Map();
  const reverse = new Map();

  for (const projectPath of projects.keys()) {
    forward.set(projectPath, new Set());
    reverse.set(projectPath, new Set());
  }

  for (const [projectPath, project] of projects.entries()) {
    for (const section of WORKSPACE_DEP_SECTIONS) {
      const deps = project.manifest?.[section];
      if (!deps || typeof deps !== "object") {
        continue;
      }

      for (const [depName, depVersion] of Object.entries(deps)) {
        if (typeof depVersion !== "string" || !depVersion.startsWith("workspace:")) {
          continue;
        }

        const targetProject = packageNameToProject.get(depName);
        if (!targetProject || targetProject === projectPath) {
          continue;
        }

        forward.get(projectPath)?.add(targetProject);
        reverse.get(targetProject)?.add(projectPath);
      }
    }
  }

  return { forward, reverse };
}

export function canonicalCycle(nodes) {
  return [...nodes].sort((left, right) => left.localeCompare(right)).join(" -> ");
}

export function collectCycles(graph) {
  let index = 0;
  const nodeIndex = new Map();
  const lowLink = new Map();
  const stack = [];
  const onStack = new Set();
  const cycles = [];

  function strongConnect(node) {
    nodeIndex.set(node, index);
    lowLink.set(node, index);
    index += 1;
    stack.push(node);
    onStack.add(node);

    for (const neighbor of graph.get(node) ?? []) {
      if (!nodeIndex.has(neighbor)) {
        strongConnect(neighbor);
        lowLink.set(node, Math.min(lowLink.get(node), lowLink.get(neighbor)));
      } else if (onStack.has(neighbor)) {
        lowLink.set(node, Math.min(lowLink.get(node), nodeIndex.get(neighbor)));
      }
    }

    if (lowLink.get(node) === nodeIndex.get(node)) {
      const scc = [];
      while (stack.length > 0) {
        const current = stack.pop();
        onStack.delete(current);
        scc.push(current);
        if (current === node) {
          break;
        }
      }

      const hasSelfLoop = scc.length === 1 && (graph.get(scc[0]) ?? new Set()).has(scc[0]);
      if (scc.length > 1 || hasSelfLoop) {
        cycles.push([...scc].sort((a, b) => a.localeCompare(b)));
      }
    }
  }

  for (const node of graph.keys()) {
    if (!nodeIndex.has(node)) {
      strongConnect(node);
    }
  }

  cycles.sort((left, right) => canonicalCycle(left).localeCompare(canonicalCycle(right)));
  return cycles;
}

export function summarizeHubs(graph, reverse, limit = 10) {
  const hubs = [];
  for (const node of graph.keys()) {
    const fanOut = (graph.get(node) ?? new Set()).size;
    const fanIn = (reverse.get(node) ?? new Set()).size;
    hubs.push({
      project: node,
      fan_in: fanIn,
      fan_out: fanOut,
      total_degree: fanIn + fanOut
    });
  }

  const fanInHubs = [...hubs]
    .sort((left, right) => {
      const byFanIn = right.fan_in - left.fan_in;
      if (byFanIn !== 0) {
        return byFanIn;
      }
      return left.project.localeCompare(right.project);
    })
    .slice(0, limit);

  const fanOutHubs = [...hubs]
    .sort((left, right) => {
      const byFanOut = right.fan_out - left.fan_out;
      if (byFanOut !== 0) {
        return byFanOut;
      }
      return left.project.localeCompare(right.project);
    })
    .slice(0, limit);

  return { fanInHubs, fanOutHubs };
}

function comparePatternSets(left, right) {
  const leftSet = new Set(left);
  const rightSet = new Set(right);

  const onlyInLeft = [...leftSet].filter((value) => !rightSet.has(value)).sort((a, b) =>
    a.localeCompare(b)
  );
  const onlyInRight = [...rightSet].filter((value) => !leftSet.has(value)).sort((a, b) =>
    a.localeCompare(b)
  );

  return {
    in_sync: onlyInLeft.length === 0 && onlyInRight.length === 0,
    only_in_policy: onlyInLeft,
    only_in_pnpm_workspace: onlyInRight
  };
}

export function loadDependencyPolicyModel({
  repoRoot,
  policyPath = "policies/dependencies.json",
  workspacePath = "pnpm-workspace.yaml"
}) {
  const policy = readJsonAt(repoRoot, policyPath);
  const validation = validateDependenciesPolicy(policy);
  const pnpmPatterns = parsePnpmWorkspacePatterns(repoRoot, workspacePath);
  const policyPatterns = Array.isArray(policy.workspace_patterns)
    ? policy.workspace_patterns.map((value) => normalizePattern(value)).filter(Boolean)
    : [];

  const policyWorkspaceRoots = Array.isArray(policy.workspace_roots)
    ? policy.workspace_roots.map((value) => normalizePattern(value)).filter(Boolean)
    : [];

  const effectivePatterns =
    policyPatterns.length > 0
      ? uniqueSorted(policyPatterns)
      : pnpmPatterns.length > 0
        ? pnpmPatterns
        : policyWorkspaceRoots.map((root) => `${root}/*`);

  const workspaceRoots = uniqueSorted(
    policyWorkspaceRoots.length > 0 ? policyWorkspaceRoots : workspaceRootsFromPatterns(effectivePatterns)
  );
  const patternSync = comparePatternSets(policyPatterns, pnpmPatterns);

  const workspaceDiscovery = discoverWorkspaceProjects(repoRoot, effectivePatterns);

  const retiredEntries = Array.isArray(policy.retired_workspace_entries)
    ? policy.retired_workspace_entries.map((value) => normalizePattern(value)).filter(Boolean)
    : [];
  const retiredEntriesPresent = retiredEntries.filter((entry) => existsSync(path.resolve(repoRoot, entry)));

  return {
    policy,
    validation,
    workspace: {
      roots: workspaceRoots,
      effective_patterns: effectivePatterns,
      policy_patterns: policyPatterns,
      pnpm_workspace_patterns: pnpmPatterns,
      pattern_sync: patternSync,
      retired_entries: retiredEntries,
      retired_entries_present: retiredEntriesPresent,
      discovery_anomalies: workspaceDiscovery.anomalies
    },
    projects: workspaceDiscovery.projects,
    packageNameToProject: workspaceDiscovery.packageNameToProject
  };
}

export function rootOfProjectPath(projectPath) {
  return projectPath.split("/", 1)[0] ?? "unknown";
}
