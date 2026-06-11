# arr8 installer parser guard

Este paquete conserva la reparacion arr7 del motor Playwright y corrige el instalador del bundle.

## Causa del fail anterior

El producto ya habia sido copiado y los checks Node/Python pasaron, pero el validador de PowerShell fallaba falsamente al invocar:

```powershell
powershell -Command "... $args[0] ..." "F:\repos\hitech-os\tools\Plawright Mamastrophic\RUN.ps1"
```

En Windows PowerShell esa forma puede romper rutas con espacios despues de `-Command`.

## Correccion

El installer genera un `parse_powershell_file.ps1` temporal en el directorio de reportes y lo invoca asi:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File parse_powershell_file.ps1 -Path "F:\repos\hitech-os\tools\Plawright Mamastrophic\RUN.ps1"
```

Esto parsea sintaxis sin ejecutar el archivo destino, respeta espacios y evita falsos negativos.
