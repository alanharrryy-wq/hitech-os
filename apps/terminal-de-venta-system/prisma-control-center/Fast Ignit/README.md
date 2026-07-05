# PRISMA Fast Ignit

Sandbox paralelo para arrancar puertos PRISMA con orquestacion rapida, sin reemplazar los launchers actuales.

## Alcance

- Se instala en `prisma-control-center\Fast Ignit`.
- No reemplaza `01_LEVANTAR_TODO_LOCAL.cmd`, wrappers actuales ni `services.json`.
- Agrega tareas opcionales/aditivas de VS Code para probarlo desde terminal integrada.
- Usa los comandos actuales de `services.json` para 3110, 3120, 3130 y 3140.
- Usa wrappers existentes para 3000, 3150 y 3160.
- El 3160 conserva su comportamiento deseado: reset/liberacion del puerto antes de iniciar.

## Modo recomendado

```powershell
.\prisma-control-center\Fast Ignit\00_FAST_IGNIT_LOCAL.cmd
```

O desde VS Code Tasks:

```text
PRISMA FAST IGNIT: Todo Local Paralelo
```

## Evidencia

Cada corrida genera carpeta y ZIP en `F:\descargasf`:

```text
fastignit run <DDMM HHMMSS>\
fastignit run <DDMM HHMMSS> result.zip
fastignit run <DDMM HHMMSS> fail.zip
latest_FAST_IGNIT_RUN.json
```


## 0407 2045

- Normaliza comandos `pnpm -C "..." run dev` a `cwd + pnpm run dev` para evitar el error de pnpm `Failed parsing JSON config key dir`.
- Detecta procesos que salen en menos de un segundo y reporta cola del log, evitando esperar todo el timeout a lo güey.
