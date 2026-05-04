# PRISMA Show POS Doctor 00U

## Propósito

Instalar un doctor permanente dentro del repo para escanear el show visual POS sin depender de scripts sueltos en `F:\descargasf`.

`F:\descargasf` queda reservado para logs, reportes JSON y evidencia de ejecución.

## Herramienta instalada

```text
apps/terminal-de-venta-system/tools/prisma-visual-os/doctor_prisma_show_pos_scan_00u.py
apps/terminal-de-venta-system/tools/prisma-visual-os/run_prisma_show_pos_doctor_00u.cmd
apps/terminal-de-venta-system/tools/prisma-visual-os/verify_prisma_show_pos_doctor_00u.mjs
```

## Qué revisa

- existencia de repo, Tablet, Visual OS y archivos POS clave;
- `pos-live-binding.tsx` en modo 00T safe no-layout;
- `pos.module.css` sin bloques 00T agresivos;
- puertos 3120 y 4177;
- health de realtime;
- rutas `/pos`, `/visual-os`, `/visual-os/pro`, `/visual-os/realtime`;
- verifiers Node 00T, 00R/00S, 00Q, checkout 00R, checkout shift 00S, 04G y 04H;
- score de receta crystal;
- broadcast neutral no-layout;
- señales recientes de logs en `F:\descargasf`.

## Regla de seguridad

El doctor no modifica archivos del repo. Solo puede arrancar servicios si se le pasa `--start-missing`.

## Uso recomendado

Desde el repo:

```powershell
F:\repos\hitech-os\apps\terminal-de-venta-system\tools\prisma-visual-os\run_prisma_show_pos_doctor_00u.cmd
```

O directo:

```powershell
py F:\repos\hitech-os\apps\terminal-de-venta-system\tools\prisma-visual-os\doctor_prisma_show_pos_scan_00u.py --target-root F:\repos\hitech-os --out-dir F:\descargasf --scan --start-missing
```

## Resultado

Genera:

```text
F:\descargasf\prisma_show_pos_doctor_00u_YYMMDD_HHMM.log
F:\descargasf\prisma_show_pos_doctor_00u_YYMMDD_HHMM.json
```

## Interpretación

- `ready`: listo.
- `ready_with_warnings`: operable, pero revisar warnings.
- `blocked`: no avanzar hasta resolver fallas críticas.
- `fatal`: el doctor no pudo completar el scan.
