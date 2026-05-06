import {
  TWIN_AUDIT_LEVELS,
  TWIN_CAPABILITY_DOMAINS,
  TWIN_CAPABILITY_STATUSES,
  TWIN_OFFLINE_MODES,
  TWIN_PARITY_MODES,
  TWIN_SURFACES,
  TWIN_SYNC_DIRECTIONS,
  type TwinCapabilityManifest,
  type TwinCapabilityValidationIssue,
  type TwinCapabilityValidationResult,
  type TwinSurface
} from "../types/capability";

const ID_PATTERN = /^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$/;
const PARITY_KEY_PATTERN = /^[a-z][a-z0-9]*(?:\.[a-z0-9]+)+$/;

function hasValue(value: unknown): value is string {
  return typeof value === "string" && value.trim().length > 0;
}

function includesValue<T extends readonly string[]>(allowed: T, value: unknown): value is T[number] {
  return typeof value === "string" && allowed.includes(value);
}

function issue(
  capabilityId: string,
  severity: "error" | "warning",
  code: string,
  message: string,
  path?: string
): TwinCapabilityValidationIssue {
  return { capabilityId, severity, code, message, path };
}

export function validateTwinCapability(capability: TwinCapabilityManifest): TwinCapabilityValidationResult {
  const id = hasValue(capability?.id) ? capability.id : "<unknown>";
  const errors: TwinCapabilityValidationIssue[] = [];
  const warnings: TwinCapabilityValidationIssue[] = [];

  if (!ID_PATTERN.test(id)) {
    errors.push(issue(id, "error", "capability.id.invalid", "Capability id must be kebab-case and stable.", "id"));
  }

  if (capability.version !== "1.0.0") {
    errors.push(issue(id, "error", "capability.version.unsupported", "Capability version must be 1.0.0.", "version"));
  }

  if (!includesValue(TWIN_CAPABILITY_DOMAINS, capability.domain)) {
    errors.push(issue(id, "error", "capability.domain.invalid", "Domain is not part of the canonical twin domain set.", "domain"));
  }

  if (!includesValue(TWIN_CAPABILITY_STATUSES, capability.status)) {
    errors.push(issue(id, "error", "capability.status.invalid", "Status is not allowed.", "status"));
  }

  if (!includesValue(TWIN_PARITY_MODES, capability.mode)) {
    errors.push(issue(id, "error", "capability.mode.invalid", "Parity mode is not allowed.", "mode"));
  }

  if (!includesValue(TWIN_SYNC_DIRECTIONS, capability.syncDirection)) {
    errors.push(issue(id, "error", "capability.syncDirection.invalid", "Sync direction is not allowed.", "syncDirection"));
  }

  if (!includesValue(TWIN_SURFACES, capability.owner)) {
    errors.push(issue(id, "error", "capability.owner.invalid", "Owner must be pc or tablet.", "owner"));
  }

  if (!PARITY_KEY_PATTERN.test(capability.parityKey ?? "")) {
    errors.push(issue(id, "error", "capability.parityKey.invalid", "Parity key must look like domain.feature or domain.feature.variant.", "parityKey"));
  }

  for (const [field, value] of Object.entries({
    title: capability.title,
    businessOutcome: capability.businessOutcome,
    updatedAt: capability.updatedAt
  })) {
    if (!hasValue(value)) {
      errors.push(issue(id, "error", `capability.${field}.missing`, `${field} is required.`, field));
    }
  }

  if (!Array.isArray(capability.surfaces) || capability.surfaces.length < 2) {
    errors.push(issue(id, "error", "surfaces.too_few", "A twin capability must declare both PC and tablet bindings.", "surfaces"));
  }

  const seenSurfaces = new Set<TwinSurface>();
  const allowedEventNames = new Set<string>();

  capability.surfaces?.forEach((surface, index) => {
    const path = `surfaces[${index}]`;
    if (!includesValue(TWIN_SURFACES, surface.surface)) {
      errors.push(issue(id, "error", "surface.invalid", "Surface must be pc or tablet.", `${path}.surface`));
      return;
    }

    if (seenSurfaces.has(surface.surface)) {
      errors.push(issue(id, "error", "surface.duplicate", `Duplicate surface binding for ${surface.surface}.`, `${path}.surface`));
    }
    seenSurfaces.add(surface.surface);

    if (!hasValue(surface.moduleKey)) {
      errors.push(issue(id, "error", "surface.moduleKey.missing", "Surface binding requires a moduleKey.", `${path}.moduleKey`));
    }
    if (!hasValue(surface.route) || !surface.route.startsWith("/")) {
      errors.push(issue(id, "error", "surface.route.invalid", "Route must be an absolute app route.", `${path}.route`));
    }
    if (!includesValue(TWIN_OFFLINE_MODES, surface.offlineMode)) {
      errors.push(issue(id, "error", "surface.offlineMode.invalid", "Offline mode is not allowed.", `${path}.offlineMode`));
    }
    if (!includesValue(TWIN_AUDIT_LEVELS, surface.auditLevel)) {
      errors.push(issue(id, "error", "surface.auditLevel.invalid", "Audit level is not allowed.", `${path}.auditLevel`));
    }
    if (!Array.isArray(surface.requiredScreens) || surface.requiredScreens.length === 0) {
      warnings.push(issue(id, "warning", "surface.requiredScreens.empty", "Surface has no required screens declared.", `${path}.requiredScreens`));
    }
    if (!Array.isArray(surface.allowedEvents)) {
      errors.push(issue(id, "error", "surface.allowedEvents.invalid", "allowedEvents must be an array.", `${path}.allowedEvents`));
    } else {
      surface.allowedEvents.forEach((eventName) => allowedEventNames.add(eventName));
    }
  });

  for (const requiredSurface of TWIN_SURFACES) {
    if (!seenSurfaces.has(requiredSurface)) {
      errors.push(issue(id, "error", "surface.missing", `Missing ${requiredSurface} surface binding.`, "surfaces"));
    }
  }

  if (!Array.isArray(capability.invariants) || capability.invariants.length < 2) {
    warnings.push(issue(id, "warning", "invariants.too_few", "Declare at least two invariants so parity does not become folklore.", "invariants"));
  }

  if (!Array.isArray(capability.acceptance) || capability.acceptance.length < 2) {
    warnings.push(issue(id, "warning", "acceptance.too_few", "Declare acceptance gates for both surfaces.", "acceptance"));
  }

  if (capability.syncDirection !== "none" && (!Array.isArray(capability.events) || capability.events.length === 0)) {
    errors.push(issue(id, "error", "events.required", "Capabilities with sync must declare at least one event.", "events"));
  }

  capability.events?.forEach((eventRef, index) => {
    const path = `events[${index}]`;
    if (!hasValue(eventRef.name)) {
      errors.push(issue(id, "error", "event.name.missing", "Event name is required.", `${path}.name`));
      return;
    }
    if (!allowedEventNames.has(eventRef.name)) {
      warnings.push(issue(id, "warning", "event.not_allowed_by_surface", `Event ${eventRef.name} is not listed in any surface allowedEvents.`, `${path}.name`));
    }
    if (!Array.isArray(eventRef.producedBy) || eventRef.producedBy.length === 0) {
      errors.push(issue(id, "error", "event.producedBy.empty", "Event must have at least one producer.", `${path}.producedBy`));
    }
    if (!Array.isArray(eventRef.consumedBy) || eventRef.consumedBy.length === 0) {
      errors.push(issue(id, "error", "event.consumedBy.empty", "Event must have at least one consumer.", `${path}.consumedBy`));
    }
  });

  return { ok: errors.length === 0, errors, warnings };
}

export function validateTwinCapabilityRegistry(capabilities: TwinCapabilityManifest[]): TwinCapabilityValidationResult {
  const errors: TwinCapabilityValidationIssue[] = [];
  const warnings: TwinCapabilityValidationIssue[] = [];
  const ids = new Set<string>();
  const parityKeys = new Set<string>();

  capabilities.forEach((capability) => {
    const result = validateTwinCapability(capability);
    errors.push(...result.errors);
    warnings.push(...result.warnings);

    if (ids.has(capability.id)) {
      errors.push(issue(capability.id, "error", "registry.id.duplicate", "Capability id appears more than once.", "id"));
    }
    ids.add(capability.id);

    if (parityKeys.has(capability.parityKey)) {
      errors.push(issue(capability.id, "error", "registry.parityKey.duplicate", "Parity key appears more than once.", "parityKey"));
    }
    parityKeys.add(capability.parityKey);
  });

  return { ok: errors.length === 0, errors, warnings };
}

export function assertTwinCapabilityRegistry(capabilities: TwinCapabilityManifest[]): TwinCapabilityManifest[] {
  const result = validateTwinCapabilityRegistry(capabilities);
  if (!result.ok) {
    const details = result.errors.map((entry) => `${entry.code}: ${entry.capabilityId} ${entry.message}`).join("; ");
    throw new Error(`Invalid twin capability registry: ${details}`);
  }
  return capabilities;
}
