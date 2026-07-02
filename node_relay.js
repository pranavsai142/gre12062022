/**
 * Simple TCP relay (no dependencies).
 * Listens on 0.0.0.0:5000 (public/LAN) and forwards to 127.0.0.1:5001 (gunicorn).
 *
 * Why: macOS firewall is happy with Node binaries (your npx already works),
 * but very flaky with Python/gunicorn. This way the "public" listener is Node.
 *
 * Usage:
 *   node node_relay.js
 *   # or with custom ports:
 *   RELAY_PORT=5000 TARGET_PORT=5001 node node_relay.js
 */

const net = require('net');

const RELAY_PORT = process.env.RELAY_PORT || 5000;
const TARGET_HOST = process.env.TARGET_HOST || '127.0.0.1';
const TARGET_PORT = process.env.TARGET_PORT || 5001;

const server = net.createServer((clientSocket) => {
  const remoteAddr = `${clientSocket.remoteAddress}:${clientSocket.remotePort}`;
  console.log(`[relay] Connection from ${remoteAddr}`);

  const targetSocket = net.connect(TARGET_PORT, TARGET_HOST, () => {
    console.log(`[relay] Connected to ${TARGET_HOST}:${TARGET_PORT}`);
    clientSocket.pipe(targetSocket);
    targetSocket.pipe(clientSocket);
  });

  targetSocket.on('error', (err) => {
    if (err.code === 'ECONNREFUSED') {
      console.error(`[relay] Target error: connect ${err.code} ${TARGET_HOST}:${TARGET_PORT} — is gunicorn running on the internal port?`);
    } else {
      console.error(`[relay] Target error:`, err.message);
    }
    clientSocket.destroy();
  });

  clientSocket.on('error', (err) => {
    console.error(`[relay] Client error from ${remoteAddr}:`, err.message);
    targetSocket.destroy();
  });

  clientSocket.on('close', () => {
    targetSocket.destroy();
  });

  targetSocket.on('close', () => {
    clientSocket.destroy();
  });
});

server.on('error', (err) => {
  console.error('[relay] Server error:', err);
  process.exit(1);
});

server.listen(RELAY_PORT, '0.0.0.0', () => {
  console.log(`[relay] Node relay listening on 0.0.0.0:${RELAY_PORT}`);
  console.log(`[relay] Forwarding to ${TARGET_HOST}:${TARGET_PORT}`);
  console.log(`[relay] Firewall should see Node (not Python).`);
});
