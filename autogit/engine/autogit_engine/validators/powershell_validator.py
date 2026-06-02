from __future__ import annotations
from ..paths import repo_path
PS_VALIDATOR = """
param([Parameter(Mandatory=$true)][string]$TargetPath)
$ErrorActionPreference = 'Stop'
$tokens = $null
$errors = $null
[System.Management.Automation.Language.Parser]::ParseFile($TargetPath, [ref]$tokens, [ref]$errors) | Out-Null
if ($errors -and $errors.Count -gt 0) { $errors | ForEach-Object { $_.ToString() }; exit 1 }
Write-Output 'OK'
""".lstrip()
def validate(repo,paths,shell,scratch):
    ps=shell.which("powershell.exe") or shell.which("powershell") or shell.which("pwsh.exe") or shell.which("pwsh"); rows=[]
    if not ps: return [{"skipped":"powershell not found"}]
    scratch.mkdir(parents=True,exist_ok=True); validator=scratch/"_ps_parse_validator.ps1"; validator.write_text(PS_VALIDATOR,encoding="utf-8")
    for rel in paths:
        full=repo_path(repo, rel)
        if full.suffix.lower() in {".ps1",".psm1"} and full.exists():
            r=shell.run([ps,"-NoProfile","-ExecutionPolicy","Bypass","-File",str(validator),str(full)],timeout=120,name="ps_parse_"+full.name)
            if r.code!=0: raise RuntimeError(f"PowerShell parse failed for {rel}")
            rows.append({"path":rel,"ok":True})
    return rows
