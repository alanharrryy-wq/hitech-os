# PC Interface Compiler Tool

Run:

```powershell
$ErrorActionPreference='Stop'; $Root='F:\repos\hitech-os\apps\terminal-de-venta-system'; $OutRoot='F:\descargasf'; & (Join-Path $Root 'tools\prisma-visual-os\pc-interface-compiler\run-pc-interface-compiler.ps1') -Root $Root -OutRoot $OutRoot
```

Strict mode:

```powershell
$ErrorActionPreference='Stop'; $Root='F:\repos\hitech-os\apps\terminal-de-venta-system'; $OutRoot='F:\descargasf'; & (Join-Path $Root 'tools\prisma-visual-os\pc-interface-compiler\run-pc-interface-compiler.ps1') -Root $Root -OutRoot $OutRoot -Strict
```
