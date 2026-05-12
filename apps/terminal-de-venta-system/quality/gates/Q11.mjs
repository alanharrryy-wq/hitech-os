import fs from 'node:fs';
import path from 'node:path';
import { createEvidence } from '../core/evidence-writer.mjs';
import { finding } from '../core/result-types.mjs';
import { checkTcpPort, probeHttp } from '../core/http-probe.mjs';

function readJsonSafe(p) {
  try {
    return JSON.parse(fs.readFileSync(p, 'utf8'));
  } catch (error) {
    return { __error: error.message || String(error) };
  }
}

function isRequired(service, profile) {
  return Array.isArray(service.requiredInProfiles) && service.requiredInProfiles.includes(profile);
}

const FORBIDDEN_PORTS = new Set([3000, 3001, 3002, 3003]);

export async function run(ctx) {
  const manifestPath = path.join(ctx.qualityRoot, 'runtime', 'runtime-port-manifest.json');
  const manifest = readJsonSafe(manifestPath);
  const services = Array.isArray(manifest.services) ? manifest.services : [];
  const disabledUntilDiscovered = Array.isArray(manifest.disabledUntilDiscovered) ? manifest.disabledUntilDiscovered : [];
  const host = manifest.host || '127.0.0.1';

  const probes = [];
  const findings = [];
  const portPolicy = {
    forbiddenGenericNextPorts: [...FORBIDDEN_PORTS],
    forbiddenPresent: [],
    noInventedPorts: Boolean(manifest.noInventedPorts),
    doNotChangePorts: Boolean(manifest.doNotChangePorts),
    disabledUntilDiscovered
  };

  for (const service of services) {
    const port = Number(service.defaultPort);

    if (FORBIDDEN_PORTS.has(port)) {
      portPolicy.forbiddenPresent.push({ serviceId: service.id, port });
      findings.push(finding({
        id: `Q11_FORBIDDEN_GENERIC_PORT_${service.id}`,
        severity: 'S1',
        layer: 'Runtime',
        title: 'Forbidden generic Next.js port in runtime manifest',
        detail: `${service.id} uses forbidden generic port ${port}. PRISMA must use real local ports.`,
        file: 'quality/runtime/runtime-port-manifest.json',
        recommendation: 'Use PRISMA real ports: 3100, 3110, 3120, 3130, 3140, 3150, 3200.'
      }));
      continue;
    }

    const tcp = await checkTcpPort({ host, port, timeoutMs: 800 });
    const serviceProbe = {
      serviceId: service.id,
      layer: service.layer,
      host,
      port,
      workspace: service.workspace,
      required: isRequired(service, ctx.profile),
      tcp,
      http: []
    };

    if (tcp.reachable) {
      for (const healthPath of service.healthPaths || ['/']) {
        const url = `http://${host}:${port}${healthPath}`;
        const http = await probeHttp({ url, timeoutMs: 1600 });
        serviceProbe.http.push(http);
      }
    }

    probes.push(serviceProbe);
  }

  const evidence = [createEvidence(ctx, 'Q11', 'runtime_health_probes', 'Local PRISMA runtime port and HTTP health probes. PQOS does not start services.', {
    manifestPath: 'quality/runtime/runtime-port-manifest.json',
    portPolicy,
    probes
  })];

  for (const p of probes) {
    if (!p.tcp.reachable) {
      findings.push(finding({
        id: `Q11_SERVICE_NOT_RUNNING_${p.serviceId}`,
        severity: p.required ? 'S1' : 'S3',
        layer: p.layer,
        title: p.required ? 'Required runtime service not reachable' : 'Optional runtime service not running',
        detail: `${p.serviceId} was not reachable on ${p.host}:${p.port}. Error: ${p.tcp.error}.`,
        evidence,
        recommendation: p.required ? 'Start required service or update runtime manifest.' : 'Start service before runtime smoke if you want live HTTP evidence.'
      }));
      continue;
    }

    for (const h of p.http) {
      if (h.statusCode >= 500) {
        findings.push(finding({
          id: `Q11_HTTP_5XX_${p.serviceId}_${h.statusCode}`,
          severity: 'S2',
          layer: p.layer,
          title: 'Runtime health endpoint returned 5xx',
          detail: `${h.url} returned ${h.statusCode}.`,
          evidence,
          recommendation: 'Inspect service logs and route handler.'
        }));
      } else if (h.statusCode >= 400) {
        findings.push(finding({
          id: `Q11_HTTP_4XX_${p.serviceId}_${h.statusCode}`,
          severity: 'S3',
          layer: p.layer,
          title: 'Runtime health endpoint returned 4xx',
          detail: `${h.url} returned ${h.statusCode}.`,
          evidence,
          recommendation: 'Confirm health path is correct or update runtime manifest.'
        }));
      }
    }
  }

  return {
    gateId: 'Q11',
    title: 'Runtime Health Probes V6',
    status: findings.some(f => ['S0', 'S1'].includes(f.severity)) ? 'BLOCKED' : 'READY',
    summary: `${probes.filter(p => p.tcp.reachable).length}/${probes.length} PRISMA local services reachable on real ports.`,
    findings,
    evidence
  };
}
