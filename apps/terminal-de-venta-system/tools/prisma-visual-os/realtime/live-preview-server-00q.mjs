#!/usr/bin/env node
import http from 'node:http';
import { randomUUID } from 'node:crypto';

const args = process.argv.slice(2);
function arg(name, fallback) { const i = args.indexOf(name); return i >= 0 && args[i + 1] ? args[i + 1] : fallback; }
const port = Number(arg('--port', process.env.PRISMA_VISUAL_REALTIME_PORT || '4177'));
const clients = new Map();
let lastPayload = null;

function send(res, event, data) { res.write(`event: ${event}\n`); res.write(`data: ${JSON.stringify(data)}\n\n`); }
function cors(res) { res.setHeader('Access-Control-Allow-Origin', '*'); res.setHeader('Access-Control-Allow-Methods', 'GET,POST,OPTIONS'); res.setHeader('Access-Control-Allow-Headers', 'content-type'); }

const server = http.createServer((req, res) => {
  cors(res);
  if (req.method === 'OPTIONS') { res.writeHead(204); res.end(); return; }
  const url = new URL(req.url || '/', `http://${req.headers.host || '127.0.0.1'}`);
  if (req.method === 'GET' && url.pathname === '/health') { res.writeHead(200, { 'content-type': 'application/json' }); res.end(JSON.stringify({ ok: true, service: 'prisma-visual-realtime', version: '00R_00S', clients: clients.size, hasLastPayload: Boolean(lastPayload) })); return; }
  if (req.method === 'GET' && url.pathname === '/state') { res.writeHead(200, { 'content-type': 'application/json' }); res.end(JSON.stringify({ ok: true, clients: clients.size, lastPayload })); return; }
  if (req.method === 'GET' && url.pathname === '/events') {
    const id = url.searchParams.get('clientId') || randomUUID();
    res.writeHead(200, { 'content-type': 'text/event-stream', 'cache-control': 'no-cache', connection: 'keep-alive' });
    clients.set(id, res);
    send(res, 'prisma.visual.status', { ok: true, id, clients: clients.size });
    if (lastPayload) send(res, 'prisma.visual.controls', lastPayload);
    req.on('close', () => clients.delete(id));
    return;
  }
  if (req.method === 'POST' && url.pathname === '/broadcast') {
    let raw = '';
    req.on('data', (chunk) => { raw += chunk; if (raw.length > 1024 * 512) req.destroy(); });
    req.on('end', () => {
      try {
        const payload = JSON.parse(raw || '{}');
        if (payload.type !== 'prisma.visual.controls') throw new Error('Invalid payload type');
        lastPayload = { ...payload, receivedAt: new Date().toISOString() };
        for (const client of clients.values()) send(client, 'prisma.visual.controls', lastPayload);
        res.writeHead(200, { 'content-type': 'application/json' });
        res.end(JSON.stringify({ ok: true, clients: clients.size }));
      } catch (error) {
        res.writeHead(400, { 'content-type': 'application/json' });
        res.end(JSON.stringify({ ok: false, error: error.message }));
      }
    });
    return;
  }
  res.writeHead(404, { 'content-type': 'application/json' });
  res.end(JSON.stringify({ ok: false, error: 'not_found' }));
});
server.listen(port, '127.0.0.1', () => console.log(`[PRISMA 00R/00S] realtime server on http://127.0.0.1:${port}`));
