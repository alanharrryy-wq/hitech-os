# HOST_CONTRIBUTIONS

## Propósito

Declarar exactamente cómo este producto se integra al host sin contaminarlo.

## Contributions solicitadas

| Contribution id | Tipo | Extension point / slot | Entry point del producto | Owner | Policy gate requerido |
| --- | --- | --- | --- | --- | --- |
| `forge.product.<product_id>.surface.primary.v1` | `surface` | `<slot-id>` | `views/surfaces/<entrypoint>` | `<owner>` | host surface review |
| `forge.product.<product_id>.action.primary.v1` | `action` | `<menu|toolbar|command palette>` | `application/<handler>` | `<owner>` | action policy review |
| `forge.product.<product_id>.status.segment.v1` | `status` | `<status-slot>` | `host_integration/contributions/<entrypoint>` | `<owner>` | status policy review |

## Published context al host

| Context id | Descripción | Campos permitidos | Frecuencia | Consumidor | Retiro en teardown |
| --- | --- | --- | --- | --- | --- |
| `forge.product.<product_id>.summary.v1` | resumen del estado visible | status, label, counters, severity | on-change | kernel host shell | sí |

## Command routing desde el host

| Command contract | Originador posible | Consumidor | Timeout | Error boundary |
| --- | --- | --- | --- | --- |
| `forge.product.<product_id>.command.primary_action.v1` | host action o command palette | producto | `<segundos>` | `ERROR_BOUNDARIES` |

## Lo que este producto no puede hacer

- mutar el layout del host sin contract;
- leer widgets del host;
- registrar shortcuts fuera de policy;
- publicar objetos ricos o handles en el context;
- decidir slots por string hacks;
- inyectar lógica de dominio en servicios del kernel.

## Revisión requerida

- compatibilidad de contribution id;
- seguridad/permisos;
- slot ownership;
- aislamiento de error;
- costo de activación;
- costo de teardown.
