# PRISMA Control Center - Launchers mínimos v2

Esta versión deja la raíz con solo 4 botones operativos:

```txt
00_KILL_ALL_LOCAL.cmd
01_LEVANTAR_TODO_LOCAL.cmd
02_LEVANTAR_TODO_LOCAL_CLOUDFLARE.cmd
03_LEVANTAR_SOLO_UN_MODULO.cmd
```

## Contrato operativo

- Si un puerto PRISMA está ocupado, el launcher lo libera sin preguntar.
- `00_KILL_ALL_LOCAL.cmd` mata puertos PRISMA y detiene `cloudflared` local si está vivo.
- `01_LEVANTAR_TODO_LOCAL.cmd` levanta local completo y abre Control Center.
- `02_LEVANTAR_TODO_LOCAL_CLOUDFLARE.cmd` levanta local completo, reinicia Cloudflare y valida público.
- `03_LEVANTAR_SOLO_UN_MODULO.cmd` abre un menú para levantar solo un módulo + Cloudflare.

## Puertos tratados como PRISMA

```txt
3000  Chart Lab
3100  reservado/legacy local
3110  Web / EIT
3120  Tablet
3130  PC
3140  Mobile
3150  Control Center
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
```

Cada opción libera su puerto, levanta ese módulo y después reinicia/valida Cloudflare.

## Evidencia

Cada corrida genera ZIP de evidencia en:

```txt
F:\descargasf
```

Los launchers viejos se conservaron fuera de la raíz en:

```txt
internal\legacy_launchers_disabled
```

La raíz queda limpia para que la operación diaria no parezca tablero de nave soviética.
