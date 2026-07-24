param(
  [ValidateSet('Build','Status','Preview','Production')]
  [string]$Action = 'Build',
  [string]$ProjectRoot = '',
  [string]$ProjectName = 'prisma-html',
  [string]$ProductionBranch = 'main',
  [string]$OutputDir = 'F:\descargasf'
)
$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'
if (-not $ProjectRoot) {
  $ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
}
$utf8 = [System.Text.UTF8Encoding]::new($false)
[Console]::OutputEncoding = $utf8
$OutputEncoding = $utf8
$env:PYTHONUTF8 = '1'
$env:PYTHONIOENCODING = 'utf-8'
$engine = Join-Path $env:TEMP ('prisma_html_cf_' + [guid]::NewGuid().ToString('N') + '.py')
$engineCode = @'
from __future__ import annotations
import argparse, hashlib, json, os, re, shutil, sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

PUBLIC_DIRS = ["assets", "paginas", "sistema-ui"]
ATLAS_PUBLIC_FILES = {
    "index.html", "a-fundamentos.html", "b-materiales.html", "c-acciones.html",
    "d-entrada-texto.html", "e-seleccion-filtros.html", "f-navegacion.html",
    "g-tablas.html", "h-listas.html", "i-paneles-cards.html", "j-expansion.html",
    "k-estados-feedback.html", "l-carga-progreso.html", "m-overlays.html",
    "n-operativos.html", "o-patrones-pantalla.html", "p-movimiento.html",
    "q-responsive-accesibilidad.html", "r-contenido.html", "s-analitica.html",
    "t-archivos-medios.html", "u-calendario.html", "v-comercio-pagos.html",
    "w-identidad-seguridad.html", "x-sistema-diagnostico.html",
    "y-i18n-impresion-offline.html", "z-gobierno.html",
}
FORBIDDEN_EXT = {".ps1", ".py", ".md", ".db", ".sqlite", ".zip", ".log", ".env", ".toml"}
SECRET_RE = re.compile(r"(?i)(api[_-]?token|api[_-]?key|client[_-]?secret|bearer\s+[A-Za-z0-9._~+/=-]{12,})")
LOCAL_RE = re.compile(r"(?i)([A-Z]:\\\\|C:\\Users\\|F:\\)")

class RefParser(HTMLParser):
    def __init__(self):
        super().__init__(); self.refs=[]
    def handle_starttag(self, tag, attrs):
        d=dict(attrs)
        for key in ("href","src"):
            if d.get(key): self.refs.append(d[key])

def sha(path: Path):
    h=hashlib.sha256();
    with path.open('rb') as f:
        for c in iter(lambda:f.read(1024*1024),b''): h.update(c)
    return h.hexdigest().upper()

def copy_tree(src: Path, dst: Path):
    for p in src.rglob('*'):
        if p.is_dir() or p.suffix.lower() in FORBIDDEN_EXT: continue
        rel=p.relative_to(src)
        out=dst/rel; out.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(p,out)

def build(root: Path, out: Path):
    if out.exists(): shutil.rmtree(out)
    out.mkdir(parents=True)
    for name in ("index.html","index.css"):
        shutil.copy2(root/name,out/name)
    for name in PUBLIC_DIRS:
        copy_tree(root/name,out/name)
    atlas_src=root/'extras'/'atlasfin'; atlas_dst=out/'extras'/'atlasfin'
    atlas_dst.mkdir(parents=True,exist_ok=True)
    for name in ATLAS_PUBLIC_FILES:
        shutil.copy2(atlas_src/name,atlas_dst/name)
    for sub in ('assets/css','assets/js','assets/data','assets/media'):
        copy_tree(atlas_src/sub,atlas_dst/sub)
    return verify(out)

def verify(out: Path):
    issues=[]; files=[]
    for p in sorted(out.rglob('*')):
        if not p.is_file(): continue
        rel=p.relative_to(out).as_posix(); files.append({'path':rel,'size':p.stat().st_size,'sha256':sha(p)})
        if p.suffix.lower() in FORBIDDEN_EXT: issues.append({'code':'FORBIDDEN_EXTENSION','path':rel})
        if p.stat().st_size <= 5*1024*1024 and p.suffix.lower() in {'.html','.css','.js','.json','.svg','.txt'}:
            text=p.read_text(encoding='utf-8',errors='replace')
            if LOCAL_RE.search(text): issues.append({'code':'LOCAL_PATH_LEAK','path':rel})
            if SECRET_RE.search(text): issues.append({'code':'SECRET_PATTERN','path':rel})
    for html in sorted(out.rglob('*.html')):
        parser=RefParser(); parser.feed(html.read_text(encoding='utf-8',errors='replace'))
        for ref in parser.refs:
            if ref.startswith(('#','data:','mailto:','tel:','javascript:')) or urlparse(ref).scheme in {'http','https'}: continue
            clean=ref.split('#',1)[0].split('?',1)[0]
            if not clean: continue
            target=(html.parent/clean).resolve()
            try: target.relative_to(out.resolve())
            except ValueError:
                issues.append({'code':'PATH_ESCAPE','page':html.relative_to(out).as_posix(),'ref':ref}); continue
            if clean.endswith('/'):
                target=target/'index.html'
            if not target.exists(): issues.append({'code':'BROKEN_REFERENCE','page':html.relative_to(out).as_posix(),'ref':ref})
    report={'status':'PASS' if not issues else 'FAIL','file_count':len(files),'issues':issues,'files':files}
    (out/'PUBLIC_BUILD_MANIFEST.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
    return report

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--root',required=True); ap.add_argument('--out',required=True); ap.add_argument('--action',choices=['build','verify'],default='build')
    a=ap.parse_args(); root=Path(a.root).resolve(); out=Path(a.out).resolve()
    report=build(root,out) if a.action=='build' else verify(out)
    print(json.dumps(report,indent=2,ensure_ascii=False)); return 0 if report['status']=='PASS' else 2
if __name__=='__main__': raise SystemExit(main())

'@
try {
  [System.IO.File]::WriteAllText($engine, $engineCode, $utf8)
  $python = Get-Command python -ErrorAction SilentlyContinue
  if (-not $python) { $python = Get-Command py -ErrorAction Stop }
  $pythonArgs = @('-X','utf8',$engine,'--root',$ProjectRoot,'--out',(Join-Path $ProjectRoot 'dist'),'--action','build')
  if ($python.Name -in @('py', 'py.exe')) { $pythonArgs = @('-3') + $pythonArgs }
  if ($Action -in @('Build','Preview','Production')) {
    & $python.Source @pythonArgs
    if ($LASTEXITCODE -ne 0) { throw "Public build verification failed: $LASTEXITCODE" }
  }
  if ($Action -eq 'Build') {
    Write-Host "PASS: dist built and verified." -ForegroundColor Green
    exit 0
  }
  $npx = Get-Command npx -ErrorAction Stop
  $wrangler = @('--yes','wrangler@4.93.0')
  if ($Action -eq 'Status') {
    & $npx.Source @wrangler pages project list --json
    & $npx.Source @wrangler pages deployment list --project-name $ProjectName --json
    exit $LASTEXITCODE
  }
  $projectsRaw = & $npx.Source @wrangler pages project list --json 2>&1
  if ($LASTEXITCODE -ne 0) { throw "Wrangler auth/project listing failed: $projectsRaw" }
  if (($projectsRaw -join "`n") -notmatch ('"name"\s*:\s*"' + [regex]::Escape($ProjectName) + '"')) {
    throw "Pages project '$ProjectName' does not exist. Create/connect it deliberately first; this script will not create a Direct Upload project by surprise."
  }
  $branch = if ($Action -eq 'Production') { $ProductionBranch } else { 'preview-' + (Get-Date -Format 'yyyyMMdd-HHmmss') }
  if ($Action -eq 'Production') {
    Write-Host 'PRODUCTION DEPLOY explicitly requested.' -ForegroundColor Yellow
  }
  New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null
  $log = Join-Path $OutputDir ('prisma-html-cf-' + $Action.ToLowerInvariant() + '-' + (Get-Date -Format 'yyyyMMdd-HHmmss') + '.log')
  & $npx.Source @wrangler pages deploy (Join-Path $ProjectRoot 'dist') --project-name $ProjectName --branch $branch 2>&1 | Tee-Object -FilePath $log
  if ($LASTEXITCODE -ne 0) { throw "Cloudflare Pages deploy failed. Log: $log" }
  Write-Host "Deploy command completed. Log: $log" -ForegroundColor Green
}
finally {
  Remove-Item -LiteralPath $engine -Force -ErrorAction SilentlyContinue
}
