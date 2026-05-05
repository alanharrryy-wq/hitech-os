# PRISMA Show POS AI Doctor Offline 00Y

## Propósito

00Y convierte reportes del Doctor Smart 00X en diagnóstico accionable sin usar APIs externas.

No modifica runtime, no toca POS, no cobra dinero y no necesita internet. Su trabajo es leer evidencia y producir:

- veredicto offline;
- resumen ejecutivo;
- bloqueos;
- riesgos;
- fortalezas;
- siguiente paquete recomendado;
- salida Markdown y JSON en `F:\descargasf`.

## Regla madre

La IA no vende, no cobra, no mueve layout y no aplica cambios.

El POS sigue siendo autónomo. 00Y solamente interpreta reportes.

## Entrada principal

Por defecto busca el reporte más reciente:

```text
F:\descargasf\prisma_show_pos_doctor_smart_00x_*.json
```

También acepta `--input-json` para analizar un reporte específico.

## Comando canónico

```powershell
F:\repos\hitech-os\apps\terminal-de-venta-system\tools\prisma-visual-os\run_prisma_show_pos_ai_doctor.cmd
```

## Salidas

```text
F:\descargasf\prisma_show_pos_ai_doctor_00y_YYMMDD_HHMM.log
F:\descargasf\prisma_show_pos_ai_doctor_00y_YYMMDD_HHMM.json
F:\descargasf\prisma_show_pos_ai_doctor_00y_YYMMDD_HHMM.md
```

## Política de costo

`defaultProvider = none`.

00Y v01 no usa OpenAI ni servicios externos. Si más adelante se agrega proveedor remoto, debe ser opt-in y nunca bloquear venta POS.
