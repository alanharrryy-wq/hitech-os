# Installer source resolver guard

This package fixes the previous installer layout bug where `INSTALL.ps1` searched for:

```text
<stage>\Plawright Mamastrophic\Plawright Mamastrophic
```

The installer now detects the source folder safely from any of these layouts:

```text
<stage>\Plawright Mamastrophic\INSTALL.ps1
<stage>\INSTALL.ps1 + nested Plawright Mamastrophic folder
<stage>\nested child that contains RUN.ps1/MENU.ps1/core/tests
```

Validation happens before target replacement. If the script is accidentally run from the already-installed target, it performs validate-only and does not move its own folder.
