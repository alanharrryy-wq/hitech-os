# Playbook suspension y grace

## Suspension suave

1. Marcar licencia `past_due_external` o `suspended`.
2. Mostrar aviso a owner/admin.
3. Conservar exportacion, backup y soporte.
4. Bloquear activacion de nuevos plugins premium.
5. No borrar datos.

## Grace offline

1. Si no hay validacion remota, entrar a `offline_grace`.
2. Conservar venta local basica.
3. Mostrar banner administrativo.
4. Reintentar refresh despues.
5. Si vence grace, aplicar politica gradual.

## Revocacion

1. Requiere razon auditable.
2. Debe permitir exportacion y soporte.
3. No debe eliminar DB.
4. No debe ocultar historial del cliente.
