# PRISMA Control Center - Launchers mínimos v2

Esta versión deja la raíz con botones operativos mínimos:

```txt
00_KILL_ALL_LOCAL.cmd
01_LEVANTAR_TODO_LOCAL.cmd
02_LEVANTAR_TODO_LOCAL_CLOUDFLARE.cmd
03_LEVANTAR_SOLO_UN_MODULO.cmd
04_ABRIR_ATLAS_DEPENDENCIAS.cmd
09_KILL_EVERYTHING_PRISMA.cmd
12_ABRIR_PRISMA_CLOUD_COMMAND_CENTER_3160.cmd
```

## Contrato operativo

- Si un puerto PRISMA está ocupado, el launcher lo libera sin preguntar.
- `00_KILL_ALL_LOCAL.cmd` mata puertos PRISMA y detiene `cloudflared` local si está vivo.
- `01_LEVANTAR_TODO_LOCAL.cmd` levanta local completo y abre Control Center.
- `02_LEVANTAR_TODO_LOCAL_CLOUDFLARE.cmd` levanta local completo, reinicia Cloudflare y valida público.
- `03_LEVANTAR_SOLO_UN_MODULO.cmd` abre un menú para levantar solo un módulo + Cloudflare.
- `04_ABRIR_ATLAS_DEPENDENCIAS.cmd` abre el atlas de dependencias.
- `09_KILL_EVERYTHING_PRISMA.cmd` ejecuta kill completo de puertos PRISMA.
- `12_ABRIR_PRISMA_CLOUD_COMMAND_CENTER_3160.cmd` abre el cockpit privado PRISMA Cloud Command Center en `http://127.0.0.1:3160/unified-shell.html` sin tocar 3150 ni levantar el stack completo; deja `latest_CLOUD_COMMAND_CENTER_3160.zip`.

## Puertos tratados como PRISMA

```txt
3000  Chart Lab
3100  reservado/legacy local
3110  Web / EIT
3120  Tablet
3130  PC
3140  Mobile
3150  Control Center
3160  PRISMA Cloud Command Center
3200  reservado/legacy local
```

## Menú de módulo individual

El launcher `03_LEVANTAR_SOLO_UN_MODULO.cmd` permite elegir:

```txt
Chart Lab
Web / EIT
Tablet
PC
Mobile
Control Center
PRISMA Cloud Command Center
```

Cada opción libera su puerto y levanta ese módulo. Los módulos con hostname público reinician/validan Cloudflare; `PRISMA Cloud Command Center` queda privado local en 3160.

## Evidencia

Cada corrida genera ZIP de evidencia en:

```txt
F:\descargasf
```

Los launchers viejos se preservan fuera del repositorio activo en `F:\Trash-old` cuando se ejecuta limpieza de reparación.

La raíz queda limpia para que la operación diaria no parezca tablero de nave soviética.
