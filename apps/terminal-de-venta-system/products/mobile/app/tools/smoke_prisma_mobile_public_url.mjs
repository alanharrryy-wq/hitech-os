const args = process.argv.slice(2);
let url = "https://prisma.hitechrts.com/prisma-app";
for (const arg of args) if (arg.startsWith("--url=")) url = arg.slice("--url=".length);
if (!/^https:\/\//.test(url)) { console.error("Expected https URL for public PWA smoke."); process.exit(2); }
try { const res = await fetch(url, { headers: { "user-agent": "prisma-mobile-pwa-smoke/1.0" } }); console.log(JSON.stringify({ ok: res.ok, status: res.status, url }, null, 2)); process.exit(res.ok ? 0 : 2); } catch (error) { console.error(JSON.stringify({ ok: false, url, error: String(error?.message || error) }, null, 2)); process.exit(2); }
