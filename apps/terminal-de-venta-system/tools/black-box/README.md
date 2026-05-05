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
