---
title: PRISMA Commercial Billing & CFDI Contract
project: PRISMA Terminal de Venta
status: productization-contract
reviewed: 2026-08-14
scope: commercial-collections-and-fiscal-orchestration
---

# PRISMA Commercial Billing & CFDI Contract

## 1. Decision

PRISMA incorpora una capa comercial local para **cuentas por cobrar, vencimientos, registro de pagos externos, recibos internos, reconciliacion, borradores fiscales y trazabilidad de CFDI**.

Esta capacidad vive en **Prisma Cloud Center** como administracion comercial. No convierte licensing, Tablet POS, PC, Mobile ni Customer Setup en procesadores financieros.

La cadena canonica es:

```text
CommercialContract
  -> CommercialCharge
  -> CommercialPayment
  -> CommercialPaymentAllocation
  -> CommercialReceipt (NO FISCAL)
  -> CommercialFiscalDocument
       -> CFDI_INGRESO draft / external stamp record
       -> CFDI_PAGO 2.0 draft / external stamp record
       -> cancellation request / external result
  -> CommercialBillingEvent
```

## 2. Clasificacion Factory Ledger

Tarea: `BUILD`.

No se reconstruyen estas capacidades existentes:

- licensing source contract alignment;
- plan-based Customer Setup;
- LICFLOW3 / Cloudflare-D1 licensing;
- License Admin Bridge;
- plan catalog y precios canonicos;
- `CommercialContract` creado por la homologacion de pricing.

La cobranza deriva del contrato comercial. No modifica la autoridad de pricing.

## 3. Autoridades

### 3.1 Precio y contrato

La autoridad de precio de lista sigue siendo:

```text
shared/licensing/plan-catalog.canonical.json
```

`CommercialContract` conserva el precio contractual acordado y su version. Un cargo se crea desde esa foto contractual; no recalcula ni inventa precios.

### 3.2 Frontera de no procesamiento financiero

Sigue vigente:

```text
docs/productization/PRISMA_LICENSE_NO_PAYMENT_PROCESSING_ADDENDUM.md
```

Por lo tanto PRISMA **no**:

- recibe tarjetas;
- inicia transferencias;
- valida SPEI;
- consulta cuentas bancarias;
- almacena PAN/CVV/cuentas/CLABE;
- liquida pagos;
- custodia dinero;
- concilia bancos automaticamente;
- emite autorizaciones bancarias.

El verbo correcto en Cloud Center es **Registrar pago externo**. No `Pagar ahora`.

## 4. Fuente fiscal SAT revisada

Revision documental: 2026-08-14.

Base oficial utilizada:

- Portal SAT, Factura electronica, CFDI version 4.0;
- Portal SAT, Complemento de pagos version 2.0;
- Guia/preguntas SAT de pagos diferidos y en parcialidades;
- reglas de cancelacion CFDI con motivos 01/02/03/04;
- Ley del IVA, tasa general del articulo 1 y existencia de tratamientos distintos.

### 4.1 Receptor CFDI 4.0

PRISMA exige capturar y confirmar al menos:

- RFC;
- nombre/razon social;
- codigo postal fiscal;
- regimen fiscal;
- uso CFDI.

El sistema valida estructura minima, pero el SAT/PAC externo sigue siendo autoridad final de catalogos y compatibilidades fiscales.

### 4.2 Emisor

Para preparar un CFDI se requiere perfil emisor confirmado con:

- RFC;
- nombre/razon social;
- codigo postal de expedicion;
- regimen fiscal;
- ClaveProdServ del servicio PRISMA confirmada por el emisor;
- ClaveUnidad confirmada;
- ObjetoImp;
- clave de impuesto;
- clave de exportacion;
- referencia de la fuente utilizada para confirmar esos datos.

PRISMA no guarda CSD, llave privada, contrasena de llave, e.firma ni token PAC.

### 4.3 PUE y PPD

Regla de preparacion local:

```text
si el cargo ya esta totalmente pagado por un unico pago registrado
antes de preparar el CFDI de ingreso
=> PUE + forma de pago realmente registrada

si no
=> PPD + forma 99 Por definir
```

Esta regla es conservadora. No intenta reconstruir acuerdos fiscales historicos.

### 4.4 Complemento de Pagos 2.0

Cuando exista CFDI de ingreso PPD y posteriormente se registre pago, PRISMA puede preparar un borrador conceptual de Complemento de Pagos 2.0.

Debe conservar por asignacion:

- UUID del CFDI relacionado;
- moneda;
- numero de parcialidad;
- saldo anterior;
- importe pagado;
- saldo insoluto;
- objeto de impuesto;
- base/impuesto proporcional cuando corresponda.

El borrador no se declara XML fiscal valido. El XSD, catalogos, reglas de negocio y timbrado final pertenecen al SAT/PAC autorizado.

## 5. IVA y tratamiento de impuestos

`1600` puntos base = 16% es el **default operativo inicial** para una operacion gravada a tasa general en Mexico.

No es universal.

Por eso:

- cada cargo guarda `taxRateBps`;
- cada cargo guarda `taxRateSource`;
- `taxConfirmed=true` es obligatorio antes de crear el cargo;
- tasa 0 u otro tratamiento no se infiere desde la vertical;
- la responsabilidad de confirmar tratamiento fiscal queda en el operador/emisor y, en produccion fiscal, en su asesoria/PAC.

El sistema usa centavos enteros para evitar errores binarios de punto flotante.

## 6. Politica de vencimiento

Version inicial:

```text
PREPAID_PERIOD_START
```

Por default:

```text
dueOn = CommercialContract.validFrom
```

El operador puede definir otra fecha contractual al crear el cargo, pero la fecha queda auditada.

La politica puede evolucionar en versiones futuras sin alterar el precio canonico.

## 7. Estados de cargo

```text
open
partially_paid
paid
past_due
void
```

Reglas:

- `paid` se deriva de asignaciones activas, no de un checkbox;
- `past_due` significa saldo > 0 y `asOf > dueOn`;
- `void` requiere confirmacion y motivo;
- no se anula un cargo con pago activo;
- no se anula un cargo si existe CFDI timbrado/no cancelado;
- un cargo vencido **NO suspende automaticamente la licencia**.

La cobranza es una dimension administrativa. Entitlements siguen bajo licensing.

## 8. Registro de pago externo

`CommercialPayment` representa un hecho reportado/confirmado por el operador, no una transaccion bancaria ejecutada por PRISMA.

Campos esenciales:

- cliente;
- fecha/hora recibida;
- moneda;
- importe;
- forma de pago SAT;
- referencia externa o evidencia;
- `idempotencyKey`;
- digest canonico de la solicitud;
- importe aplicado;
- saldo no aplicado;
- estado.

### 8.1 Idempotencia

Misma `idempotencyKey` + mismo digest:

```text
return existing payment
no duplicate
```

Misma key + datos diferentes:

```text
BILLING_IDEMPOTENCY_CONFLICT
HTTP 409 semantics
```

### 8.2 Pagos parciales

Cada `CommercialPaymentAllocation` conserva:

- `partialityNumber`;
- `balanceBeforeCents`;
- `amountCents`;
- `balanceAfterCents`.

Estos datos alimentan el Complemento de Pagos sin reconstruir saldos a ojo despues.

### 8.3 Sobrepago / saldo no aplicado

Si el pago registrado excede el saldo del cargo:

- se aplica hasta el saldo;
- el resto queda en `unappliedCents`;
- no se inventa otro cargo;
- no se prepara Complemento de Pagos como `ready_to_stamp` mientras exista importe no aplicado que impida relacion completa.

## 9. Recibo interno

Cada pago registrado genera un `CommercialReceipt`.

El recibo debe contener permanentemente:

```text
RECIBO INTERNO NO FISCAL
```

Y debe expresar que PRISMA:

- registra un pago externo informado;
- no procesa ni valida fondos;
- no sustituye CFDI.

Al revertir el registro de pago, el recibo se marca `void`; no se elimina.

## 10. Reversion de pago

La reversion es administrativa y auditable.

Requiere:

- confirmacion explicita;
- motivo;
- pago en estado `posted`.

Si existe `CFDI_PAGO` timbrado y no cancelado:

```text
BILLING_PAYMENT_REVERSE_BLOCKED_BY_CFDI
```

Primero debe resolverse la cancelacion fiscal externa.

Las asignaciones se marcan `reversed`; no se borran.

## 11. CFDI de ingreso

`CommercialFiscalDocument.kind = CFDI_INGRESO`.

Estados:

```text
draft_blocked
ready_to_stamp
external_stamped
cancel_requested
cancellation_rejected
cancelled
```

`ready_to_stamp` significa solamente:

> Los prerequisitos locales de PRISMA estan completos para entregar el borrador a una integracion SAT/PAC.

No significa:

- XML validado por XSD;
- CSD valido;
- sello generado;
- PAC acepto;
- SAT acepto;
- UUID existente.

## 12. Registro de timbrado externo

PRISMA no llama al PAC en esta fase.

Cuando una emision se realice por SAT/PAC externo, el operador/integracion autorizada puede registrar:

- UUID;
- proveedor;
- referencia de evidencia;
- fecha de timbrado;
- SHA-256 del XML si se desea;
- referencia al PDF si existe.

El XML fiscal completo y las llaves privadas no se guardan en este ledger.

## 13. Complemento de Pagos

`CommercialFiscalDocument.kind = CFDI_PAGO`.

Prerequisitos minimos locales:

- pago `posted`;
- asignaciones activas;
- receptor confirmado;
- emisor confirmado;
- CFDI de ingreso relacionado con UUID externo registrado;
- sin inconsistencias de scope cliente;
- sin importe no aplicado que vuelva incompleta la relacion.

El documento preserva version CFDI 4.0 y Complemento de Pagos 2.0.

## 14. Cancelacion

Motivos SAT modelados:

```text
01 Comprobantes emitidos con errores con relacion
02 Comprobantes emitidos con errores sin relacion
03 No se llevo a cabo la operacion
04 Operacion nominativa relacionada en una factura global
```

Para motivo `01`, PRISMA exige UUID sustituto.

La accion `request-cancellation`:

- registra intencion y motivo;
- NO llama a SAT/PAC;
- deja `liveCancellationAllowed=false`.

Luego `register-cancellation-result` registra la evidencia externa de aceptacion/rechazo.

Un CFDI cancelado permanece historico. Una sustitucion es un nuevo documento/folio interno, nunca una reescritura del registro cancelado.

## 15. Aging y reconciliacion

PRISMA calcula:

```text
current
1_30
31_60
61_90
90_plus
```

Y totales:

- outstanding;
- overdue;
- collected;
- allocated;
- unapplied.

La reconciliacion usa cargos y asignaciones del ledger local.

No es conciliacion bancaria.

## 16. Primer cliente

`Prisma Original Customer` no recibe automaticamente:

- RFC;
- regimen;
- CP fiscal;
- uso CFDI;
- cargo historico;
- pago historico;
- CFDI;
- UUID;
- evidencia fiscal.

Todo dato historico requiere entrada/evidencia explicita.

## 17. Cloud Center

La superficie `Cobranza & CFDI` puede:

- capturar/confirmar perfil receptor;
- capturar/confirmar perfil emisor sin secretos;
- crear cargo desde CTR;
- registrar pago externo;
- mostrar recibo interno;
- preparar CFDI ingreso;
- registrar UUID timbrado externo;
- preparar Complemento de Pagos;
- solicitar cancelacion externa;
- registrar resultado externo;
- mostrar aging/reconciliacion;
- mostrar auditoria.

La UI reutiliza componentes/clases existentes. Este contrato no autoriza CSS ni Visual OS.

## 18. Gateway SAT/PAC

Estado inicial:

```text
EXTERNAL_SAT_OR_AUTHORIZED_PAC_REQUIRED
liveStampingAllowed=false
liveCancellationAllowed=false
secretsExposed=false
```

Provider modes:

```text
not_configured
manual_sat
pac_external
```

`csdState` es solamente estado de presencia/gestion:

```text
not_configured
presence_only
externally_managed
```

Nunca contiene certificado, llave o password.

## 19. Seguridad y privacidad

Prohibido persistir en Commercial Billing:

- CSD `.key`;
- password de llave;
- e.firma;
- token PAC;
- tarjetas;
- CVV;
- numero de cuenta ordenante/beneficiaria;
- CLABE;
- secretos de banco.

Una referencia documental puede apuntar a evidencia gestionada fuera del ledger, pero no debe incrustar secretos.

## 20. Pruebas

Las pruebas destructivas se ejecutan exclusivamente contra SQLite temporal/sandbox.

El verificador debe cubrir como minimo:

- schema;
- ausencia de datos fiscales inferidos;
- cargo desde contrato;
- IVA por centavos;
- due date;
- aging;
- parcialidades;
- idempotencia;
- recibo no fiscal;
- PUE/PPD;
- bloqueo por perfiles faltantes;
- registro UUID externo;
- Complemento de Pagos;
- cancelacion 01/02/03/04;
- reversion bloqueada si existe complemento timbrado;
- ausencia de mutacion de licencia;
- ausencia de secretos;
- scope Cloud Center solamente.

## 21. Evidence ladder

Estados defendibles:

```text
SOURCE_READY
LOCAL_VERIFIED
RUNTIME_VERIFIED
EXTERNAL_PAC_CONFIGURED
LIVE_FISCAL_CERTIFIED
```

Este trabajo puede alcanzar `LOCAL_VERIFIED` con pruebas de sandbox.

No puede declarar `LIVE_FISCAL_CERTIFIED` sin:

- identidad fiscal real del emisor;
- CSD/e.firma gestionados de forma segura fuera del repo;
- PAC/SAT configurado;
- operacion de timbrado autorizada;
- UUID real;
- cancelacion real si se certifica esa ruta;
- evidencia sin secretos.

## 22. No fake green

Nunca traducir:

```text
borrador valido localmente
```

a:

```text
factura emitida
```

Nunca traducir:

```text
UUID capturado por operador
```

a:

```text
PRISMA timbro
```

Nunca traducir:

```text
cancel_requested
```

a:

```text
cancelled
```

La diferencia entre esos estados es parte del producto.
