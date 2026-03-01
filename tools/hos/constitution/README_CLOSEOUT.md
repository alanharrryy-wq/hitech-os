# Constitution Closeout Additions

This pack adds:
- `CONSTITUTION_v1.md` (draft)
- Activation plan
- Registry JSON
- Renderer: JSON -> Markdown for human review
- Improved check script (optional auto-deps)
- Publish script (render + optional validate)

Commands:
```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\constitution_publish.ps1 -RepoRoot "F:\repos\hitech-os" -Validate
```
