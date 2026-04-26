# Manifest PRISMA UI Docs v3

| Campo | Valor |
|---|---|
| Version | 3.0.0 |
| Fecha | 2026-04-25 |
| Raiz esperada | docs/prisma/ui |
| App PC | blueprints/pc/master.md |
| App Tablet | blueprints/tablet/master.md |
| Contrato principal | shared/contracts/plugin-contract.md |
| Estado | listo para instalacion modular |

## Archivos generados

Este manifest se acompana con un `_package/MANIFEST_CHECKSUMS.txt` generado al cerrar el paquete.

## Politica de actualizacion

- Cambios pequenos: agregar contenido dentro del doc correspondiente.
- Cambios medianos: crear archivo nuevo bajo el modulo, pantalla o plugin afectado.
- Cambios grandes: nuevo ZIP gobernado con instalador o script de colocacion.

## No negociables

- No poner documentacion PRISMA UI en la raiz del proyecto.
- No duplicar el mismo contrato en PC y Tablet sin referencia compartida.
- No meter verticales completas dentro de una pantalla base.
- No crear plugin sin rollback.
