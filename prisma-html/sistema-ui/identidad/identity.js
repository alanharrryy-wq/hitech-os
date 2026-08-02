(() => {
  const bundle = window.PRISMA_IDENTITY_BUNDLE;
  const ARTIFACT_SCHEMA = 'prisma.identity.portable-element-export.v1';
  const ARTIFACT_VERSION = '1.0.0';
  const CANONICALIZATION = 'json-sort-keys-compact-utf8-v1';
  const EXTENSION = '.prisma-visual.json';
  const excludedIntegrityFields = new Set(['exportId', 'integrity']);

  if (!bundle) {
    document.getElementById('compileStatus').textContent = 'Bundle no disponible';
    return;
  }

  const $ = (id) => document.getElementById(id);
  const escapeHtml = (value) => String(value)
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#039;');
  const profiles = new Map(bundle.profiles.map((profile) => [profile.id, profile]));
  const definitions = new Map(bundle.tokenDefinitions.map((token) => [token.id, token]));
  const exportRegistry = bundle.portableExportRegistry;
  const viewerComponents = new Map(
    (exportRegistry?.viewerComponents || []).map((component) => [component.id, component])
  );
  const active = bundle.manifest.selectedProfileId;
  const profileSelect = $('profileSelect');
  const surfaceSelect = $('surfaceSelect');

  if (!exportRegistry || exportRegistry.artifactSchema !== ARTIFACT_SCHEMA) {
    $('compileStatus').textContent = 'Export registry no disponible';
    return;
  }

  bundle.profiles.forEach((profile) => {
    const option = document.createElement('option');
    option.value = profile.id;
    option.textContent = profile.name;
    option.selected = profile.id === active;
    profileSelect.appendChild(option);
  });
  Object.keys(bundle.projections).forEach((surface) => {
    const option = document.createElement('option');
    option.value = surface;
    option.textContent = surface;
    surfaceSelect.appendChild(option);
  });

  $('compileStatus').textContent = bundle.manifest.status;
  $('readyCount').textContent = `${bundle.manifest.bindingReadyCount}/${bundle.manifest.surfaceCount}`;
  $('blockedCount').textContent = bundle.manifest.blockedSurfaceCount;

  function merged(profile, surface) {
    const tokens = Object.fromEntries(bundle.tokenDefinitions.map((token) => [token.id, token.default]));
    Object.assign(tokens, profile.tokenOverrides || {});
    Object.assign(tokens, bundle.surfaceAdapters?.[surface]?.tokenOverrides || {});
    return tokens;
  }

  function sortedClone(value) {
    if (Array.isArray(value)) return value.map(sortedClone);
    if (value && typeof value === 'object') {
      return Object.fromEntries(
        Object.keys(value).sort().map((key) => [key, sortedClone(value[key])])
      );
    }
    return value;
  }

  function canonicalJson(value) {
    return JSON.stringify(sortedClone(value));
  }

  async function sha256Hex(text) {
    if (!globalThis.crypto?.subtle) {
      throw new Error('Web Crypto SHA-256 no está disponible en este navegador.');
    }
    const bytes = new TextEncoder().encode(text);
    const hash = await globalThis.crypto.subtle.digest('SHA-256', bytes);
    return Array.from(new Uint8Array(hash), (byte) => byte.toString(16).padStart(2, '0')).join('');
  }

  function coveredPayload(artifact) {
    return Object.fromEntries(
      Object.entries(artifact).filter(([key]) => !excludedIntegrityFields.has(key))
    );
  }

  function safeSlug(value) {
    return String(value).replace(/[^a-zA-Z0-9._-]+/g, '-').replace(/^-+|-+$/g, '').toLowerCase();
  }

  function selectedProfile() {
    return profiles.get(profileSelect.value);
  }

  function targetEnvelope(surface, componentUiId = null) {
    const projection = bundle.projections[surface];
    const binding = projection?.binding || {};
    const target = {
      surfaceId: surface || null,
      ownerId: null,
      routeId: null,
      regionId: null,
      slotId: null,
    };
    const missingBindings = Object.entries(target)
      .filter(([, value]) => value === null)
      .map(([key]) => key);
    if (!componentUiId) missingBindings.push('componentUiId');
    let bindingStatus = 'BLOCKED_BY_MISSING_BINDING';
    if (binding.readiness === 'CERTIFIED_BINDING_SOURCE') {
      bindingStatus = 'BLOCKED_BY_MISSING_ELEMENT_BINDING';
    }
    return {
      ...target,
      bindingStatus,
      surfaceReadiness: binding.readiness || null,
      surfaceBindingSources: {
        routeSource: binding.routeSource || null,
        ownerSource: binding.ownerSource || null,
        slotSource: binding.slotSource || null,
        layerSource: binding.layerSource || null,
      },
      missingBindings: [...new Set(missingBindings)].sort(),
    };
  }

  function applicationPolicy() {
    return {
      mode: 'INSTRUCTION_ONLY',
      productApplicationAllowed: false,
      runtimeMutationAllowed: false,
      requiresFutureGovernedApplicationGate: true,
      requiredFutureEvidence: [
        'fresh Authority Mesh for the exact target',
        'concrete owner/route/region/slot binding',
        'pre-change hashes',
        'transactional backup and rollback',
        'surface-specific static validation',
        'visual evidence',
        'no fake green',
      ],
    };
  }

  function origin(sourcePath, sourceRegistry, profileId) {
    return {
      authority: 'prisma-html/authority/rifat/identity',
      sourcePath,
      sourceRegistry,
      selectedProfileId: profileId,
      generatedBy: 'sistema-ui/identidad/identity.js',
    };
  }

  async function finalizeArtifact(artifact) {
    const checksum = await sha256Hex(canonicalJson(coveredPayload(artifact)));
    artifact.exportId = `PEX.${safeSlug(`${artifact.kind}-${artifact.element.objectId}`)}.${checksum.slice(0, 12)}`;
    artifact.integrity = {
      algorithm: 'SHA-256',
      canonicalization: CANONICALIZATION,
      coveredTopLevelFields: Object.keys(coveredPayload(artifact)).sort(),
      canonicalPayloadSha256: checksum,
    };
    return artifact;
  }

  async function buildPortableArtifact(kind, objectId, surfaceOverride = null) {
    const profile = selectedProfile();
    const surface = surfaceOverride || surfaceSelect.value;
    const createdAt = new Date().toISOString();
    let recipePresetId = profile.id;
    let neutralMeaningId;
    let componentUiId = null;
    let values;
    let artifactOrigin;
    let compatibility;
    let preview = null;
    let target = targetEnvelope(surface);

    if (kind === 'identity-profile') {
      neutralMeaningId = 'VIS.identity.profile';
      values = { profile: structuredClone(profile) };
      artifactOrigin = origin(
        `profiles/${profile.id}.identity.json`,
        'registries/identity.registry.json',
        profile.id
      );
      compatibility = {
        supportedSurfaces: Object.keys(bundle.projections),
        selectedSurface: surface,
        surfaceRuntimeProjectionAllowed: false,
        artifactSchema: ARTIFACT_SCHEMA,
      };
      preview = {
        traits: profile.traits || [],
        tokenOverrideCount: Object.keys(profile.tokenOverrides || {}).length,
      };
    } else if (kind === 'semantic-token') {
      const definition = definitions.get(objectId);
      if (!definition) throw new Error(`Token desconocido: ${objectId}`);
      const tokens = merged(profile, surface);
      const adapterOverrides = bundle.surfaceAdapters?.[surface]?.tokenOverrides || {};
      let overrideSource = 'default';
      if (Object.prototype.hasOwnProperty.call(profile.tokenOverrides || {}, objectId)) {
        overrideSource = 'identity-profile';
      }
      if (Object.prototype.hasOwnProperty.call(adapterOverrides, objectId)
          && adapterOverrides[objectId] !== definition.default) {
        overrideSource = 'surface-adapter-or-compiled-projection';
      }
      neutralMeaningId = `TOK.${objectId}`;
      values = {
        definition: structuredClone(definition),
        resolvedValue: tokens[objectId],
        defaultValue: definition.default,
        overrideSource,
        cssVariable: `--prisma-identity-${objectId.replaceAll('.', '-')}`,
      };
      artifactOrigin = origin(
        'registries/semantic-tokens.registry.json',
        'registries/semantic-tokens.registry.json',
        profile.id
      );
      compatibility = {
        supportedSurfaces: Object.keys(bundle.projections),
        selectedSurface: surface,
        surfaceRuntimeProjectionAllowed: false,
        valueType: definition.type,
      };
      preview = { type: definition.type, value: tokens[objectId] };
    } else if (kind === 'surface-adapter') {
      const projection = bundle.projections[objectId];
      if (!projection) throw new Error(`Adaptador desconocido: ${objectId}`);
      recipePresetId = projection.adapterId;
      neutralMeaningId = 'VIS.surface.adapter';
      target = targetEnvelope(objectId);
      values = {
        adapterId: projection.adapterId,
        adapter: structuredClone(bundle.surfaceAdapters?.[objectId] || {}),
        projectionRules: structuredClone(projection.projectionRules),
        forbiddenMutations: structuredClone(projection.forbiddenMutations),
        resolvedTokenCount: Object.keys(projection.tokens || {}).length,
        surfaceBinding: structuredClone(projection.binding),
      };
      artifactOrigin = origin(
        `adapters/${objectId}.adapter.json`,
        'registries/surface-adapters.registry.json',
        profile.id
      );
      compatibility = {
        supportedSurfaces: [objectId],
        selectedSurface: objectId,
        surfaceRuntimeProjectionAllowed: false,
      };
      preview = {
        surfaceIntent: profile.surfaceIntent?.[objectId] || null,
        projectionStatus: projection.status,
      };
    } else if (kind === 'preview-component-recipe') {
      const component = viewerComponents.get(objectId);
      if (!component) throw new Error(`Componente de vista previa desconocido: ${objectId}`);
      componentUiId = component.id;
      recipePresetId = component.recipePresetId;
      neutralMeaningId = component.neutralMeaningId;
      const componentSurface = component.surfaceId || 'shared-ui';
      const tokens = merged(profile, componentSurface);
      const resolvedTokens = Object.fromEntries(
        component.tokenRefs.map((tokenId) => [tokenId, tokens[tokenId]])
      );
      target = targetEnvelope(componentSurface, component.id);
      target.bindingStatus = component.productBindingStatus || 'BLOCKED_BY_MISSING_BINDING';
      values = {
        componentName: component.name,
        tokenRefs: structuredClone(component.tokenRefs),
        resolvedTokens,
      };
      artifactOrigin = origin(
        'registries/portable-export.registry.json',
        'registries/portable-export.registry.json',
        profile.id
      );
      compatibility = {
        supportedSurfaces: [componentSurface],
        selectedSurface: componentSurface,
        surfaceRuntimeProjectionAllowed: false,
        productBindingResolved: false,
      };
      preview = { resolvedTokens };
    } else {
      throw new Error(`Tipo de exportación no soportado: ${kind}`);
    }

    const artifact = {
      schema: ARTIFACT_SCHEMA,
      artifactVersion: ARTIFACT_VERSION,
      kind,
      createdAt,
      instructionOnly: true,
      runtimeMutationAllowed: false,
      identity: {
        identityProfileId: profile.id,
        identityProfileVersion: profile.version || '1.0.0',
        recipePresetId,
      },
      element: {
        neutralMeaningId,
        objectId,
        componentUiId,
        version: ARTIFACT_VERSION,
      },
      target,
      values,
      origin: artifactOrigin,
      compatibility,
      preview,
      applicationPolicy: applicationPolicy(),
      manifest: {
        recordCount: 1,
        records: [{ recordId: objectId, recordKind: kind, instructionOnly: true }],
      },
    };
    return finalizeArtifact(artifact);
  }

  function downloadArtifact(artifact) {
    const blob = new Blob(
      [JSON.stringify(sortedClone(artifact), null, 2) + '\n'],
      { type: 'application/json' }
    );
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement('a');
    anchor.href = url;
    anchor.download = `${safeSlug(artifact.kind)}_${safeSlug(artifact.element.objectId)}${EXTENSION}`;
    anchor.click();
    URL.revokeObjectURL(url);
  }

  function toast(message) {
    document.querySelector('.toast')?.remove();
    const node = document.createElement('div');
    node.className = 'toast';
    node.textContent = message;
    document.body.appendChild(node);
    setTimeout(() => node.remove(), 2200);
  }

  async function exportObject(kind, objectId, surface = null) {
    const artifact = await buildPortableArtifact(kind, objectId, surface);
    downloadArtifact(artifact);
    toast(`Guardado: ${artifact.exportId}`);
  }

  function render(profileId) {
    const profile = profiles.get(profileId);
    const surface = surfaceSelect.value;
    const tokens = merged(profile, surface);
    $('selectedProfile').textContent = profile.id;
    $('profileName').textContent = profile.name;
    $('profileIntent').textContent = profile.intent;
    $('traitList').innerHTML = profile.traits.map((trait) => `<span>${escapeHtml(trait)}</span>`).join('');
    const preview = document.querySelector('.preview');
    preview.style.setProperty('--accent', tokens['color.accent']);
    preview.style.setProperty('--surface-fill', tokens['material.surfaceFill']);
    preview.style.setProperty('--surface-border', tokens['material.surfaceBorder']);
    preview.style.setProperty('--surface-shadow', tokens['material.surfaceShadow']);
    preview.style.setProperty('--surface-backdrop', tokens['material.backdropFilter']);
    preview.style.setProperty('--panel-radius', tokens['border.radiusPanel']);
    document.body.style.color = tokens['color.textPrimary'];
    renderTokens(tokens, $('tokenSearch').value);
    renderSurfaces(profile);
  }

  function renderTokens(tokens, query = '') {
    const needle = query.trim().toLowerCase();
    const html = Object.entries(tokens)
      .filter(([id, value]) => `${id} ${value}`.toLowerCase().includes(needle))
      .map(([id, value]) => {
        const definition = definitions.get(id);
        const swatch = definition?.type === 'color'
          ? `<span class="swatch" style="background:${escapeHtml(value)}"></span>`
          : '';
        return `<article class="token">
          <div class="token-copy">
            <small>${escapeHtml(definition?.group || 'token')} · ${escapeHtml(definition?.type || '')}</small>
            <code title="${escapeHtml(value)}">${swatch}${escapeHtml(id)}: ${escapeHtml(value)}</code>
          </div>
          <button class="element-export-button" type="button"
            data-export-kind="semantic-token" data-export-id="${escapeHtml(id)}">
            Guardar
          </button>
        </article>`;
      }).join('');
    $('tokenGrid').innerHTML = html;
  }

  function renderSurfaces(profile) {
    $('surfaceTable').innerHTML = Object.values(bundle.projections).map((projection) => {
      const status = projection.status;
      const cls = status.includes('BINDING_READY') ? 'ready' : status.includes('NEUTRAL') ? 'neutral' : '';
      const intent = profile.surfaceIntent?.[projection.surface] || 'surface adaptation';
      return `<article class="surface-row">
        <strong>${escapeHtml(projection.surface)}</strong>
        <p>${escapeHtml(intent)}</p>
        <span class="pill ${cls}">${escapeHtml(status)}</span>
        <button class="element-export-button" type="button"
          data-export-kind="surface-adapter" data-export-id="${escapeHtml(projection.surface)}">
          Guardar adaptador
        </button>
      </article>`;
    }).join('');
  }

  async function verifyPortableArtifact(artifact) {
    const errors = [];
    const warnings = [];
    if (artifact?.schema !== ARTIFACT_SCHEMA) errors.push('Schema no soportado.');
    if (artifact?.instructionOnly !== true) errors.push('instructionOnly debe ser true.');
    if (artifact?.runtimeMutationAllowed !== false) errors.push('runtimeMutationAllowed debe ser false.');
    if (artifact?.applicationPolicy?.mode !== 'INSTRUCTION_ONLY') {
      errors.push('La política de aplicación no es INSTRUCTION_ONLY.');
    }
    if (artifact?.applicationPolicy?.productApplicationAllowed !== false) {
      errors.push('El artefacto pretende permitir aplicación de producto.');
    }
    if (artifact?.integrity?.algorithm !== 'SHA-256') errors.push('Algoritmo de integridad inválido.');
    if (artifact?.integrity?.canonicalization !== CANONICALIZATION) {
      errors.push('Canonización no soportada.');
    }
    const expected = await sha256Hex(canonicalJson(coveredPayload(artifact)));
    if (artifact?.integrity?.canonicalPayloadSha256 !== expected) {
      errors.push(`SHA-256 no coincide. Esperado ${expected}.`);
    }
    const target = artifact?.target || {};
    const traceFields = ['surfaceId', 'ownerId', 'routeId', 'regionId', 'slotId'];
    const missing = traceFields.filter((field) => target[field] == null);
    const declared = new Set(target.missingBindings || []);
    const undeclared = missing.filter((field) => !declared.has(field));
    if (undeclared.length) errors.push(`Bindings nulos no declarados: ${undeclared.join(', ')}.`);
    if (missing.length && !String(target.bindingStatus || '').includes('BLOCKED')) {
      errors.push('Hay bindings ausentes sin estado BLOCKED.');
    }
    if (target.surfaceReadiness === 'CERTIFIED_BINDING_SOURCE' && missing.length) {
      warnings.push('La superficie tiene fuentes certificadas, pero este elemento no posee binding concreto.');
    }
    return { errors, warnings, expectedChecksum: expected };
  }

  async function inspectFile(file) {
    const output = $('importResult');
    output.className = 'import-result';
    output.textContent = 'Verificando estructura y SHA-256…';
    try {
      const artifact = JSON.parse(await file.text());
      const verification = await verifyPortableArtifact(artifact);
      const status = verification.errors.length ? 'FAIL' : 'PASS';
      output.classList.add(status === 'PASS' ? 'pass' : 'fail');
      output.textContent = JSON.stringify({
        status,
        file: file.name,
        exportId: artifact.exportId || null,
        kind: artifact.kind || null,
        objectId: artifact.element?.objectId || null,
        neutralMeaningId: artifact.element?.neutralMeaningId || null,
        identityProfileId: artifact.identity?.identityProfileId || null,
        surfaceId: artifact.target?.surfaceId || null,
        bindingStatus: artifact.target?.bindingStatus || null,
        missingBindings: artifact.target?.missingBindings || [],
        instructionOnly: artifact.instructionOnly,
        runtimeMutationAllowed: artifact.runtimeMutationAllowed,
        checksum: artifact.integrity?.canonicalPayloadSha256 || null,
        errors: verification.errors,
        warnings: verification.warnings,
        actionTaken: 'INSPECTION_ONLY_NO_PRODUCT_MUTATION',
      }, null, 2);
    } catch (error) {
      output.classList.add('fail');
      output.textContent = JSON.stringify({
        status: 'FAIL',
        file: file.name,
        error: error.message,
        actionTaken: 'NONE',
      }, null, 2);
    }
  }

  profileSelect.addEventListener('change', () => render(profileSelect.value));
  surfaceSelect.addEventListener('change', () => render(profileSelect.value));
  $('tokenSearch').addEventListener('input', () => render(profileSelect.value));
  $('copyCommand').addEventListener('click', async () => {
    const command = `python tools/identity_dictionary.py activate ${profileSelect.value}`;
    await navigator.clipboard.writeText(command);
    $('copyCommand').textContent = 'Comando copiado';
    setTimeout(() => $('copyCommand').textContent = 'Copiar comando de activación', 1400);
  });
  $('exportProfile').addEventListener('click', () => {
    exportObject('identity-profile', profileSelect.value).catch((error) => toast(error.message));
  });
  document.addEventListener('click', (event) => {
    const button = event.target.closest('.element-export-button');
    if (!button) return;
    exportObject(button.dataset.exportKind, button.dataset.exportId)
      .catch((error) => toast(error.message));
  });
  $('importArtifact').addEventListener('change', (event) => {
    const [file] = event.target.files || [];
    if (file) inspectFile(file);
  });

  render(active);
})();
