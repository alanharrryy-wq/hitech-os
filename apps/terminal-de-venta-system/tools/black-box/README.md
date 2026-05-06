# PRISMA black-box i02 supervisor

Esta entrega instala black-box i02: runtime doctor + supervisor local.

Comandos principales despues de instalar:

```powershell
python F:\repos\hitech-os\apps\terminal-de-venta-system\tools\black-box\black_box.py status --root F:\repos\hitech-os\apps\terminal-de-venta-system --allow-blocked
python F:\repos\hitech-os\apps\terminal-de-venta-system\tools\black-box\black_box.py start all --root F:\repos\hitech-os\apps\terminal-de-venta-system --watch
python F:\repos\hitech-os\apps\terminal-de-venta-system\tools\black-box\black_box.py stop owned --root F:\repos\hitech-os\apps\terminal-de-venta-system
```

No mata procesos ajenos. Solo `stop owned` usa PIDs registrados por black-box.


## i02 R2 watch output

Salida principal recomendada:

```text
F:\Black-box
```

Watch sin spam de reportes:

```powershell
python "F:\repos\hitech-os\apps\terminal-de-venta-system\tools\black-box\black_box.py" watch --root "F:\repos\hitech-os\apps\terminal-de-venta-system" --out "F:\Black-box" --interval 5
```

Forzar reporte por ciclo solo cuando se necesite:

```powershell
python "F:\repos\hitech-os\apps\terminal-de-venta-system\tools\black-box\black_box.py" watch --root "F:\repos\hitech-os\apps\terminal-de-venta-system" --out "F:\Black-box" --interval 5 --emit-report
```

Limpiar reportes viejos:

```powershell
python "F:\repos\hitech-os\apps\terminal-de-venta-system\tools\black-box\black_box.py" cleanup reports --root "F:\repos\hitech-os\apps\terminal-de-venta-system" --out "F:\Black-box" --days 7 --keep-last 200
```


## i02 R3 log scope

R3 evita falsos `BLOCKED` por logs viejos o externos. Por default, black-box solo considera activos los logs relevantes al runtime PRISMA/Terminal de Venta y dentro de una ventana fresca.

Comando recomendado:

```powershell
python "F:\repos\hitech-os\apps\terminal-de-venta-system\tools\black-box\black_box.py" status --root "F:\repos\hitech-os\apps\terminal-de-venta-system" --out "F:\Black-box" --allow-blocked
```

Si necesitas incluir ruido externo del monorepo para investigación manual, usa reportes/collect y revisa logs externos fuera del estado principal. La vigilancia normal no debe bloquear Tablet/PC/Mobile por `eit-*` o builds viejos.
