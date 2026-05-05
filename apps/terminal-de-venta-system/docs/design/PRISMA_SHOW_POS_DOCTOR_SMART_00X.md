# PRISMA Show POS Doctor Smart 00X

## Propósito

00X reemplaza el chequeo ingenuo de logs por un diagnóstico más inteligente para Visual OS POS.

El problema anterior era simple y ridículo, como báscula de mercado que se asusta con el viento: el doctor encontraba cadenas viejas como `500`, `Build Error` o `VERIFY FAILED` dentro de reportes históricos y las trataba como advertencia viva.

## Qué cambia

- Clasifica señales como activas, históricas o suprimidas.
- Lee JSON de reportes de forma estructural.
- No penaliza reportes `ready` aunque contengan texto histórico embebido.
- Produce `healthScore`, `releaseVerdict`, `criticalFailures`, `warnings`, `fragilePoints`, `historicalSignals` y `suppressedSignals`.
- Mantiene `F:\descargasf` como salida de logs y reportes.
- No modifica archivos del repo durante el scan.

## Comando canónico

```powershell
F:epos\hitech-ospps	erminal-de-venta-system	ools\prisma-visual-osun_prisma_show_pos_doctor.cmd
```

## Gates principales

- `/pos` responde 200 y sin build error.
- Realtime `/health` responde 200.
- 00T safe-no-layout pasa.
- Doctor 00X pasa.
- Touch-only 04H pasa si está instalado.
- Logs históricos no bloquean por sí solos.

## Regla madre

El POS vende. Visual OS observa y ajusta atmósfera segura. Ningún diagnóstico debe confundir basura histórica con falla viva.
