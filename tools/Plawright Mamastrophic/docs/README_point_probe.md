# Mamastrophic point-probe

Modo nuevo para capturar el stack visual exacto bajo una coordenada usando `document.elementsFromPoint(x, y)`.

## Ejemplo Tablet POS rail derecho

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "F:\repos\hitech-os\tools\Plawright Mamastrophic\RUN.ps1" -Mode point-probe -Surface tablet -Route /pos -PointX 1160 -PointY 420 -AllowPartial
```

Si no pasas `PointX/PointY`, Tablet usa un default en el rail derecho de `/pos`.

## Salidas

- `reports/point-stack.json`
- `reports/point-stack.md`
- `reports/point-summary.json`
- `screens/<surface>.point.png` si no usas `-NoScreenshots`

## Política

- No modifica repo.
- No mata procesos.
- No levanta dev server.
- No regenera Prisma.
