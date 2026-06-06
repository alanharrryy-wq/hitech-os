#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import process from "node:process";

const root = process.cwd();
const checks = [
  {
    id: "local_admin_service",
    file: "src/server/pos-api/local-admin.prisma.ts",
    must: [
      "sell:create",
      "users:permissions",
      "support:evidence",
      "support_internal",
      "createLocalUser",
      "updateLocalUser",
      "setLocalUserStatus",
      "tablet.user.soft_deleted",
      "secretStoredAsHash"
    ]
  },
  {
    id: "local_admin_api",
    file: "app/api/pos/admin/local-users/route.ts",
    must: [
      "create_user",
      "update_user",
      "deactivate_user",
      "reactivate_user",
      "soft_delete_user",
      "LOCAL_USER_PIN_INVALID"
    ]
  },
  {
    id: "local_admin_ui",
    file: "components/settings/local-users-roles-panel.tsx",
    must: [
      "Administración local operativa",
      "PIN de 6 dígitos",
      "Crear usuario",
      "Editar",
      "Baja suave",
      "Permisos por rol"
    ]
  },
    {
    id: "secure_reset_no_phrase",
    file: "components/settings/sales-reset-panel.tsx",
    must: ["Pregunta de seguridad", "PIN admin", "alerta silenciosa"]
  }
];

const results = checks.map((check) => {
  const abs = path.join(root, check.file);
  const text = fs.existsSync(abs) ? fs.readFileSync(abs, "utf8") : "";
  const missing = check.must.filter((needle) => !text.includes(needle));
  return { ...check, abs, exists: Boolean(text), missing, ok: text.length > 0 && missing.length === 0 };
});

const ok = results.every((item) => item.ok);
console.log(JSON.stringify({
  verifier: "verify_tablet_local_admin_security_01",
  state: ok ? "PASS" : "FAIL",
  ok,
  results,
  checkedAt: new Date().toISOString()
}, null, 2));
process.exit(ok ? 0 : 1);
