# SYNAPSE-X: Guia Para Usar La Interfaz (Sin Rollos Tecnicos)

Esta guia es para usar la app desde la ventana, no desde comandos.

## 1) Abrir la app
Forma mas simple:
1. Ve a esta carpeta:
`F:\repos\hitech-os\apps\synapse-x\scripts\ops`
2. Doble clic en:
`open-ui.ps1`

Se abrira una ventana llamada `SYNAPSE-X Studio`.

## 2) Donde esta lo importante
En la parte de arriba veras:
1. Botones rapidos.
2. Un dropdown llamado `Funciones:`.
3. Boton `Ejecutar Funcion`.

Ese dropdown es para correr cosas sin usar `.ps1` ni terminal.

## 3) Funciones del dropdown (que hace cada una)
1. `Ver estado del sistema`
Te muestra si la base esta bien y cuantos datos hay.

2. `Ingerir fuentes configuradas`
Lee las carpetas ya configuradas por defecto.

3. `Ingerir carpeta seleccionada...`
Abre selector de carpeta para que elijas una (por ejemplo `C:\Users\alanh\.codex`).

4. `Reprocesar todo (Full Ingest)`
Vuelve a procesar todo desde cero.

5. `Reprocesar carpeta seleccionada...`
Lo mismo que full ingest, pero solo para la carpeta que elijas.

6. `Actualizar metricas`
Refresca estadisticas.

7. `Reparar base e indices`
Repara inconsistencias si algo salio mal.

8. `Activar monitoreo continuo (Watch ON)`
Deja monitoreo automatico activo.

9. `Desactivar monitoreo continuo (Watch OFF)`
Detiene el monitoreo automatico.

10. `Exportar sesion seleccionada`
Guarda reporte de la sesion que tengas seleccionada en resultados.

## 4) Flujo recomendado (paso a paso)
1. En dropdown elige `Ingerir carpeta seleccionada...`.
2. Selecciona tu carpeta, ejemplo: `C:\Users\alanh\.codex`.
3. Espera a que termine.
4. En `Query` escribe algo como `error` o `failed`.
5. Clic en `Search`.
6. Clic en un resultado.
7. Si quieres reporte, en dropdown usa `Exportar sesion seleccionada`.

## 5) Si no ves resultados
1. Ejecuta `Reprocesar carpeta seleccionada...` sobre tu carpeta.
2. Luego `Actualizar metricas`.
3. Busca de nuevo con palabras mas generales (`error`, `warning`, `exception`).

## 6) Tipos de archivo que si lee
1. `.json`
2. `.jsonl`
3. `.log`
4. `.txt`
5. `.md`
6. `.report`
