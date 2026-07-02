# AutoGit Flight Control v2

AutoGit v2 agrega un flujo seguro de **plan -> apply-plan -> PR -> merge** sin reemplazar el motor clásico.

## Principios

- No `git reset --hard`.
- No `git clean`.
- No force push.
- No sanitización de source code.
- Gate anti-downgrade para `package.json`.
- Secret scan sobre archivos cambiados.
- Commits separados por tema.
- Merge sólo con bandera explícita.

## Uso recomendado

```powershell
F:\repos\hitech-os\autogit\AutoGit.cmd plan --task "cerrar cambios PRISMA control center 3160"
```

Luego, si el plan no tiene blockers:

```powershell
F:\repos\hitech-os\autogit\AutoGit.cmd apply-plan --plan "F:\descargasf\autogit plan <DDMM HHMMSS>\AUTOGIT_PLAN.lock.json" --allow-commit --allow-push --allow-pr --wait-checks
```

Merge explícito:

```powershell
F:\repos\hitech-os\autogit\AutoGit.cmd merge --pr <PR_URL_OR_NUMBER> --allow-merge --wait-checks
```
