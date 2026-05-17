import http from 'node:http';
import https from 'node:https';
import net from 'node:net';

export function checkTcpPort({ host = '127.0.0.1', port, timeoutMs = 900 }) {
  return new Promise((resolve) => {
    const startedAt = Date.now();
    const socket = new net.Socket();
    let settled = false;

    function done(result) {
      if (settled) return;
      settled = true;
      socket.destroy();
      resolve({ host, port, latencyMs: Date.now() - startedAt, ...result });
    }

    socket.setTimeout(timeoutMs);
    socket.once('connect', () => done({ reachable: true, error: null }));
    socket.once('timeout', () => done({ reachable: false, error: 'timeout' }));
    socket.once('error', (error) => done({ reachable: false, error: error.code || error.message || String(error) }));

    try {
      socket.connect(port, host);
    } catch (error) {
      done({ reachable: false, error: error.code || error.message || String(error) });
    }
  });
}

export function probeHttp({ url, timeoutMs = 1600, method = 'GET' }) {
  return new Promise((resolve) => {
    const startedAt = Date.now();
    const lib = String(url).startsWith('https:') ? https : http;
    let settled = false;

    function done(result) {
      if (settled) return;
      settled = true;
      resolve(result);
    }

    const request = lib.request(url, { method, timeout: timeoutMs }, (response) => {
      let body = '';
      response.setEncoding('utf8');

      response.on('data', (chunk) => {
        body += chunk;
        if (body.length > 3000) {
          request.destroy(new Error('body_sample_limit'));
        }
      });

      response.on('end', () => {
        done({
          url,
          method,
          reachable: true,
          statusCode: response.statusCode,
          latencyMs: Date.now() - startedAt,
          bodySample: body.slice(0, 1200),
          error: null
        });
      });
    });

    request.on('timeout', () => {
      request.destroy(new Error('timeout'));
    });

    request.on('error', (error) => {
      done({
        url,
        method,
        reachable: false,
        statusCode: null,
        latencyMs: Date.now() - startedAt,
        bodySample: '',
        error: error.code || error.message || String(error)
      });
    });

    request.end();
  });
}
