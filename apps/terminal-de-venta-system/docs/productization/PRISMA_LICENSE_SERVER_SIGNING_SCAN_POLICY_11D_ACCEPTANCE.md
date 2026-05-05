# PRISMA License Server Signing Scan Policy 11D - Acceptance

## Gates

1. `py_compile` del motor 11D.
2. JSON valido en contrato y politica.
3. `terminal_de_venta.cmd` enruta comandos server-signing al motor 11D.
4. `license-server-signing-smoke` retorna `FINAL READY`.
5. `license-server-signing-scan` no bloquea corpus aprobados.
6. Cualquier PEM privado fuera de allowlist bloquea.
7. Tamper de payload, firma y keyId se rechaza.

## Comandos

```powershell
terminal_de_venta.cmd license-server-signing-smoke
terminal_de_venta.cmd license-server-signing-scan
terminal_de_venta.cmd license-server-signing-fixture-audit
```

## Rollback

El instalador conserva backup de `terminal_de_venta.cmd` y de los archivos tocados bajo `.prisma_license_server_signing_scan_policy_11d_backups`.
