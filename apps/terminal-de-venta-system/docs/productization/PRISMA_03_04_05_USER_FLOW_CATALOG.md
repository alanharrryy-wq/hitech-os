# PRISMA 03-04-05 — User Flow Catalog


> Paquete: `PRISMA_CENTRO_PRISMA_UI_SHELL_03`  
> Incluye documentación consolidada para iteraciones `03`, `04` y `05`.  
> Alcance: documentación y contratos.  
> Prohibido: runtime, DB, `.env`, comunicación remota, pagos, ejecución de plugins y updates reales.


## Propósito

Flujos de usuario esperados para la futura implementación de Centro PRISMA, Support Bundle y Messaging Mock.

| ID | Flujo | Acción usuario | Resultado esperado | Prohibición | Aceptación |
| --- | --- | --- | --- | --- | --- |
| FLOW-001 | PC revisa Mi Plan | Usuario revisa plan local | Lee fixture/licencia local 02 | No revoca datos | Pasa si respeta mock/read-only y vuelve a venta cuando aplica. |
| FLOW-002 | PC abre Soporte | Usuario prepara solicitud | Crea borrador local mock | No envía remoto | Pasa si respeta mock/read-only y vuelve a venta cuando aplica. |
| FLOW-003 | PC revisa Diagnóstico | Usuario ve allowlist | Muestra consentimiento requerido | No genera bundle real | Pasa si respeta mock/read-only y vuelve a venta cuando aplica. |
| FLOW-004 | PC abre Mensajes | Usuario ve threads mock | Lista local_only | No servidor | Pasa si respeta mock/read-only y vuelve a venta cuando aplica. |
| FLOW-005 | Tablet abre Estado | Cajero consulta estado | Muestra salud ligera | No bloquea venta | Pasa si respeta mock/read-only y vuelve a venta cuando aplica. |
| FLOW-006 | Tablet abre Soporte | Cajero crea borrador | Categoría limitada | No adjunta archivos | Pasa si respeta mock/read-only y vuelve a venta cuando aplica. |
| FLOW-007 | Tablet ve Novedades | Cajero ve aviso | Puede posponer | No popup en checkout | Pasa si respeta mock/read-only y vuelve a venta cuando aplica. |
| FLOW-008 | PC abre Centro | Usuario entra a Centro PRISMA desde backoffice | Muestra cards mock/read-only | No ejecuta acciones | Pasa si respeta mock/read-only y vuelve a venta cuando aplica. |
| FLOW-009 | PC revisa Mi Plan | Usuario revisa plan local | Lee fixture/licencia local 02 | No revoca datos | Pasa si respeta mock/read-only y vuelve a venta cuando aplica. |
| FLOW-010 | PC abre Soporte | Usuario prepara solicitud | Crea borrador local mock | No envía remoto | Pasa si respeta mock/read-only y vuelve a venta cuando aplica. |
| FLOW-011 | PC revisa Diagnóstico | Usuario ve allowlist | Muestra consentimiento requerido | No genera bundle real | Pasa si respeta mock/read-only y vuelve a venta cuando aplica. |
| FLOW-012 | PC abre Mensajes | Usuario ve threads mock | Lista local_only | No servidor | Pasa si respeta mock/read-only y vuelve a venta cuando aplica. |
| FLOW-013 | Tablet abre Estado | Cajero consulta estado | Muestra salud ligera | No bloquea venta | Pasa si respeta mock/read-only y vuelve a venta cuando aplica. |
| FLOW-014 | Tablet abre Soporte | Cajero crea borrador | Categoría limitada | No adjunta archivos | Pasa si respeta mock/read-only y vuelve a venta cuando aplica. |
| FLOW-015 | Tablet ve Novedades | Cajero ve aviso | Puede posponer | No popup en checkout | Pasa si respeta mock/read-only y vuelve a venta cuando aplica. |
| FLOW-016 | PC abre Centro | Usuario entra a Centro PRISMA desde backoffice | Muestra cards mock/read-only | No ejecuta acciones | Pasa si respeta mock/read-only y vuelve a venta cuando aplica. |
| FLOW-017 | PC revisa Mi Plan | Usuario revisa plan local | Lee fixture/licencia local 02 | No revoca datos | Pasa si respeta mock/read-only y vuelve a venta cuando aplica. |
| FLOW-018 | PC abre Soporte | Usuario prepara solicitud | Crea borrador local mock | No envía remoto | Pasa si respeta mock/read-only y vuelve a venta cuando aplica. |
| FLOW-019 | PC revisa Diagnóstico | Usuario ve allowlist | Muestra consentimiento requerido | No genera bundle real | Pasa si respeta mock/read-only y vuelve a venta cuando aplica. |
| FLOW-020 | PC abre Mensajes | Usuario ve threads mock | Lista local_only | No servidor | Pasa si respeta mock/read-only y vuelve a venta cuando aplica. |
| FLOW-021 | Tablet abre Estado | Cajero consulta estado | Muestra salud ligera | No bloquea venta | Pasa si respeta mock/read-only y vuelve a venta cuando aplica. |
| FLOW-022 | Tablet abre Soporte | Cajero crea borrador | Categoría limitada | No adjunta archivos | Pasa si respeta mock/read-only y vuelve a venta cuando aplica. |
| FLOW-023 | Tablet ve Novedades | Cajero ve aviso | Puede posponer | No popup en checkout | Pasa si respeta mock/read-only y vuelve a venta cuando aplica. |
| FLOW-024 | PC abre Centro | Usuario entra a Centro PRISMA desde backoffice | Muestra cards mock/read-only | No ejecuta acciones | Pasa si respeta mock/read-only y vuelve a venta cuando aplica. |
| FLOW-025 | PC revisa Mi Plan | Usuario revisa plan local | Lee fixture/licencia local 02 | No revoca datos | Pasa si respeta mock/read-only y vuelve a venta cuando aplica. |
| FLOW-026 | PC abre Soporte | Usuario prepara solicitud | Crea borrador local mock | No envía remoto | Pasa si respeta mock/read-only y vuelve a venta cuando aplica. |
| FLOW-027 | PC revisa Diagnóstico | Usuario ve allowlist | Muestra consentimiento requerido | No genera bundle real | Pasa si respeta mock/read-only y vuelve a venta cuando aplica. |
| FLOW-028 | PC abre Mensajes | Usuario ve threads mock | Lista local_only | No servidor | Pasa si respeta mock/read-only y vuelve a venta cuando aplica. |
| FLOW-029 | Tablet abre Estado | Cajero consulta estado | Muestra salud ligera | No bloquea venta | Pasa si respeta mock/read-only y vuelve a venta cuando aplica. |
| FLOW-030 | Tablet abre Soporte | Cajero crea borrador | Categoría limitada | No adjunta archivos | Pasa si respeta mock/read-only y vuelve a venta cuando aplica. |
| FLOW-031 | Tablet ve Novedades | Cajero ve aviso | Puede posponer | No popup en checkout | Pasa si respeta mock/read-only y vuelve a venta cuando aplica. |
| FLOW-032 | PC abre Centro | Usuario entra a Centro PRISMA desde backoffice | Muestra cards mock/read-only | No ejecuta acciones | Pasa si respeta mock/read-only y vuelve a venta cuando aplica. |
| FLOW-033 | PC revisa Mi Plan | Usuario revisa plan local | Lee fixture/licencia local 02 | No revoca datos | Pasa si respeta mock/read-only y vuelve a venta cuando aplica. |
| FLOW-034 | PC abre Soporte | Usuario prepara solicitud | Crea borrador local mock | No envía remoto | Pasa si respeta mock/read-only y vuelve a venta cuando aplica. |
| FLOW-035 | PC revisa Diagnóstico | Usuario ve allowlist | Muestra consentimiento requerido | No genera bundle real | Pasa si respeta mock/read-only y vuelve a venta cuando aplica. |
| FLOW-036 | PC abre Mensajes | Usuario ve threads mock | Lista local_only | No servidor | Pasa si respeta mock/read-only y vuelve a venta cuando aplica. |
| FLOW-037 | Tablet abre Estado | Cajero consulta estado | Muestra salud ligera | No bloquea venta | Pasa si respeta mock/read-only y vuelve a venta cuando aplica. |
| FLOW-038 | Tablet abre Soporte | Cajero crea borrador | Categoría limitada | No adjunta archivos | Pasa si respeta mock/read-only y vuelve a venta cuando aplica. |
| FLOW-039 | Tablet ve Novedades | Cajero ve aviso | Puede posponer | No popup en checkout | Pasa si respeta mock/read-only y vuelve a venta cuando aplica. |
| FLOW-040 | PC abre Centro | Usuario entra a Centro PRISMA desde backoffice | Muestra cards mock/read-only | No ejecuta acciones | Pasa si respeta mock/read-only y vuelve a venta cuando aplica. |
| FLOW-041 | PC revisa Mi Plan | Usuario revisa plan local | Lee fixture/licencia local 02 | No revoca datos | Pasa si respeta mock/read-only y vuelve a venta cuando aplica. |
| FLOW-042 | PC abre Soporte | Usuario prepara solicitud | Crea borrador local mock | No envía remoto | Pasa si respeta mock/read-only y vuelve a venta cuando aplica. |
| FLOW-043 | PC revisa Diagnóstico | Usuario ve allowlist | Muestra consentimiento requerido | No genera bundle real | Pasa si respeta mock/read-only y vuelve a venta cuando aplica. |
| FLOW-044 | PC abre Mensajes | Usuario ve threads mock | Lista local_only | No servidor | Pasa si respeta mock/read-only y vuelve a venta cuando aplica. |
| FLOW-045 | Tablet abre Estado | Cajero consulta estado | Muestra salud ligera | No bloquea venta | Pasa si respeta mock/read-only y vuelve a venta cuando aplica. |
| FLOW-046 | Tablet abre Soporte | Cajero crea borrador | Categoría limitada | No adjunta archivos | Pasa si respeta mock/read-only y vuelve a venta cuando aplica. |
| FLOW-047 | Tablet ve Novedades | Cajero ve aviso | Puede posponer | No popup en checkout | Pasa si respeta mock/read-only y vuelve a venta cuando aplica. |
| FLOW-048 | PC abre Centro | Usuario entra a Centro PRISMA desde backoffice | Muestra cards mock/read-only | No ejecuta acciones | Pasa si respeta mock/read-only y vuelve a venta cuando aplica. |
| FLOW-049 | PC revisa Mi Plan | Usuario revisa plan local | Lee fixture/licencia local 02 | No revoca datos | Pasa si respeta mock/read-only y vuelve a venta cuando aplica. |
| FLOW-050 | PC abre Soporte | Usuario prepara solicitud | Crea borrador local mock | No envía remoto | Pasa si respeta mock/read-only y vuelve a venta cuando aplica. |
| FLOW-051 | PC revisa Diagnóstico | Usuario ve allowlist | Muestra consentimiento requerido | No genera bundle real | Pasa si respeta mock/read-only y vuelve a venta cuando aplica. |
| FLOW-052 | PC abre Mensajes | Usuario ve threads mock | Lista local_only | No servidor | Pasa si respeta mock/read-only y vuelve a venta cuando aplica. |
| FLOW-053 | Tablet abre Estado | Cajero consulta estado | Muestra salud ligera | No bloquea venta | Pasa si respeta mock/read-only y vuelve a venta cuando aplica. |
| FLOW-054 | Tablet abre Soporte | Cajero crea borrador | Categoría limitada | No adjunta archivos | Pasa si respeta mock/read-only y vuelve a venta cuando aplica. |
| FLOW-055 | Tablet ve Novedades | Cajero ve aviso | Puede posponer | No popup en checkout | Pasa si respeta mock/read-only y vuelve a venta cuando aplica. |
| FLOW-056 | PC abre Centro | Usuario entra a Centro PRISMA desde backoffice | Muestra cards mock/read-only | No ejecuta acciones | Pasa si respeta mock/read-only y vuelve a venta cuando aplica. |
| FLOW-057 | PC revisa Mi Plan | Usuario revisa plan local | Lee fixture/licencia local 02 | No revoca datos | Pasa si respeta mock/read-only y vuelve a venta cuando aplica. |
| FLOW-058 | PC abre Soporte | Usuario prepara solicitud | Crea borrador local mock | No envía remoto | Pasa si respeta mock/read-only y vuelve a venta cuando aplica. |
| FLOW-059 | PC revisa Diagnóstico | Usuario ve allowlist | Muestra consentimiento requerido | No genera bundle real | Pasa si respeta mock/read-only y vuelve a venta cuando aplica. |
| FLOW-060 | PC abre Mensajes | Usuario ve threads mock | Lista local_only | No servidor | Pasa si respeta mock/read-only y vuelve a venta cuando aplica. |
| FLOW-061 | Tablet abre Estado | Cajero consulta estado | Muestra salud ligera | No bloquea venta | Pasa si respeta mock/read-only y vuelve a venta cuando aplica. |
| FLOW-062 | Tablet abre Soporte | Cajero crea borrador | Categoría limitada | No adjunta archivos | Pasa si respeta mock/read-only y vuelve a venta cuando aplica. |
| FLOW-063 | Tablet ve Novedades | Cajero ve aviso | Puede posponer | No popup en checkout | Pasa si respeta mock/read-only y vuelve a venta cuando aplica. |
| FLOW-064 | PC abre Centro | Usuario entra a Centro PRISMA desde backoffice | Muestra cards mock/read-only | No ejecuta acciones | Pasa si respeta mock/read-only y vuelve a venta cuando aplica. |
| FLOW-065 | PC revisa Mi Plan | Usuario revisa plan local | Lee fixture/licencia local 02 | No revoca datos | Pasa si respeta mock/read-only y vuelve a venta cuando aplica. |
| FLOW-066 | PC abre Soporte | Usuario prepara solicitud | Crea borrador local mock | No envía remoto | Pasa si respeta mock/read-only y vuelve a venta cuando aplica. |
| FLOW-067 | PC revisa Diagnóstico | Usuario ve allowlist | Muestra consentimiento requerido | No genera bundle real | Pasa si respeta mock/read-only y vuelve a venta cuando aplica. |
| FLOW-068 | PC abre Mensajes | Usuario ve threads mock | Lista local_only | No servidor | Pasa si respeta mock/read-only y vuelve a venta cuando aplica. |
| FLOW-069 | Tablet abre Estado | Cajero consulta estado | Muestra salud ligera | No bloquea venta | Pasa si respeta mock/read-only y vuelve a venta cuando aplica. |
| FLOW-070 | Tablet abre Soporte | Cajero crea borrador | Categoría limitada | No adjunta archivos | Pasa si respeta mock/read-only y vuelve a venta cuando aplica. |
| FLOW-071 | Tablet ve Novedades | Cajero ve aviso | Puede posponer | No popup en checkout | Pasa si respeta mock/read-only y vuelve a venta cuando aplica. |
| FLOW-072 | PC abre Centro | Usuario entra a Centro PRISMA desde backoffice | Muestra cards mock/read-only | No ejecuta acciones | Pasa si respeta mock/read-only y vuelve a venta cuando aplica. |
| FLOW-073 | PC revisa Mi Plan | Usuario revisa plan local | Lee fixture/licencia local 02 | No revoca datos | Pasa si respeta mock/read-only y vuelve a venta cuando aplica. |
| FLOW-074 | PC abre Soporte | Usuario prepara solicitud | Crea borrador local mock | No envía remoto | Pasa si respeta mock/read-only y vuelve a venta cuando aplica. |
| FLOW-075 | PC revisa Diagnóstico | Usuario ve allowlist | Muestra consentimiento requerido | No genera bundle real | Pasa si respeta mock/read-only y vuelve a venta cuando aplica. |
| FLOW-076 | PC abre Mensajes | Usuario ve threads mock | Lista local_only | No servidor | Pasa si respeta mock/read-only y vuelve a venta cuando aplica. |
| FLOW-077 | Tablet abre Estado | Cajero consulta estado | Muestra salud ligera | No bloquea venta | Pasa si respeta mock/read-only y vuelve a venta cuando aplica. |
| FLOW-078 | Tablet abre Soporte | Cajero crea borrador | Categoría limitada | No adjunta archivos | Pasa si respeta mock/read-only y vuelve a venta cuando aplica. |
| FLOW-079 | Tablet ve Novedades | Cajero ve aviso | Puede posponer | No popup en checkout | Pasa si respeta mock/read-only y vuelve a venta cuando aplica. |
| FLOW-080 | PC abre Centro | Usuario entra a Centro PRISMA desde backoffice | Muestra cards mock/read-only | No ejecuta acciones | Pasa si respeta mock/read-only y vuelve a venta cuando aplica. |

## Regla de oro

Un flujo de usuario no debe crear una acción que el contrato no soporte. Si el contrato dice mock, la UI dice mock. Si el contrato dice read-only, la UI no saca un botón mágico de la manga.
