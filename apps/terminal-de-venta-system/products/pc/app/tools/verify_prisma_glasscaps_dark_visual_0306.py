from __future__ import annotations
import json, os, re, shutil, subprocess, sys
from pathlib import Path
from datetime import datetime

ROOT = Path.cwd()
OUT = Path(os.environ.get('PRISMA_VISUAL_OUT', ROOT / 'visual-glasscaps-dark'))
OUT.mkdir(parents=True, exist_ok=True)

def read(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(path)
    return path.read_text(encoding='utf-8')

def find_browser() -> str | None:
    env = os.environ.get('PRISMA_CHROMIUM') or os.environ.get('CHROME') or os.environ.get('EDGE')
    candidates = []
    if env: candidates.append(env)
    candidates += [
        shutil.which('chromium') or '',
        shutil.which('chromium-browser') or '',
        shutil.which('google-chrome') or '',
        shutil.which('google-chrome-stable') or '',
        shutil.which('chrome') or '',
        shutil.which('msedge') or '',
        r'C:\Program Files\Google\Chrome\Application\chrome.exe',
        r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe',
        r'C:\Program Files\Microsoft\Edge\Application\msedge.exe',
        r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',
    ]
    for c in candidates:
        if c and Path(c).exists():
            return str(Path(c))
    return None

def css_safe(css: str) -> str:
    # Keep CSS intact, but neutralize CSS module import expectations are unnecessary in a static HTML fixture.
    return css

component_css = css_safe(read(ROOT / 'components/prisma-glass-capsule/prisma-glass-capsule.module.css'))
page_css = css_safe(read(ROOT / 'referencia-visual/liquid-glass-capsules/liquid-glass-capsules.module.css'))

html = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>PRISMA Dark Liquid Glass Visual Fixture</title>
<style>{component_css}\n{page_css}\nbody{{margin:0;background:#05070d;font-family:Inter,Arial,sans-serif;}}.visualHarness{{min-height:960px;padding:40px;position:relative;isolation:isolate;color:#fff;}}.visualRail{{position:absolute;left:70px;right:70px;top:360px;display:flex;gap:16px;align-items:center;z-index:4;}}.visualPill{{min-width:150px;}}.visualLabel{{position:absolute;left:70px;top:120px;font-size:88px;font-weight:1000;letter-spacing:-.08em;color:rgba(255,255,255,.23);text-transform:uppercase;}}.visualText2{{position:absolute;left:110px;top:510px;font-size:56px;font-weight:1000;letter-spacing:-.06em;color:rgba(110,231,255,.18);text-transform:uppercase;}}</style>
</head>
<body>
<main class="page visualHarness">
  <div aria-hidden="true" class="motionBackplate"><div class="fixedGeometryField">
    <div class="geoPair geoPairA"><span class="geoShape geoCircle red"></span><span class="geoShape geoSquare rose"></span></div>
    <div class="geoPair geoPairB"><span class="geoShape geoDot cyan"></span><span class="geoShape geoRect blue"></span></div>
    <div class="geoPair geoPairC"><span class="geoShape geoDiamond violet"></span><span class="geoShape geoCapsule magenta"></span></div>
    <div class="geoPair geoPairD"><span class="geoShape geoTriangle amber"></span><span class="geoShape geoDot lime"></span></div>
    <div class="geoPair geoPairE"><span class="geoShape geoSlash emerald"></span><span class="geoShape geoCircle mint"></span></div>
  </div></div>
  <div class="visualLabel">DARK BACKDROP · SOLID TEXT</div>
  <div class="visualText2">NO GLOBAL BLUE · LOCAL EDGE</div>
  <div class="visualRail">
    {''.join([f'''<div class="root visualPill" data-variant="{v}" data-shape="pill" data-tone="{t}" data-density="regular" data-floating="true"><span aria-hidden="true" class="refraction"></span><span aria-hidden="true" class="lobeLens"></span><span aria-hidden="true" class="edgeFrame"></span><span aria-hidden="true" class="volumeFrame"></span><span aria-hidden="true" class="innerFrame"></span><span aria-hidden="true" class="specular"></span><span aria-hidden="true" class="liquidSheen"></span><span class="content">{label}</span></div>''' for label,t,v in [('backdrop','graphite','neutral'),('Dark optics','rose','danger'),('Thinking','blue','thinking'),('Lensing','violet','active'),('Color edge','adaptive','tinted'),('No blue','graphite','neutral')]])}
  </div>
</main>
</body>
</html>'''
html_path = OUT / 'glasscaps_dark_visual_bench.html'
html_path.write_text(html, encoding='utf-8')
report = {'status': 'RUNNING', 'created': datetime.now().isoformat(timespec='seconds'), 'html': str(html_path), 'checks': []}

browser = find_browser()
if not browser:
    report['status'] = 'FAIL'
    report['error'] = 'No Chromium/Chrome/Edge executable found for visual screenshot.'
    (OUT / 'visual_report.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    raise SystemExit('No Chromium/Chrome/Edge executable found for visual screenshot.')

png = OUT / 'glasscaps_dark_visual_bench.png'
cmd = [browser, '--headless=new', '--no-sandbox', '--disable-gpu', '--disable-dev-shm-usage', '--disable-background-networking', '--disable-extensions', '--hide-scrollbars', '--window-size=1440,960', f'--screenshot={png}', html_path.as_uri()]
try:
    proc = subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=35)
except subprocess.TimeoutExpired as exc:
    report['status'] = 'FAIL'
    report['error'] = 'Browser screenshot timed out after 35 seconds.'
    report['browser'] = browser
    report['browser_output_tail'] = (exc.stdout or '')[-2000:] if isinstance(exc.stdout, str) else ''
    (OUT / 'visual_report.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    raise SystemExit(report['error'])
report['browser'] = browser
report['browser_returncode'] = proc.returncode
report['browser_output_tail'] = proc.stdout[-2000:]
if proc.returncode != 0 or not png.exists():
    report['status'] = 'FAIL'
    report['error'] = 'Browser screenshot failed.'
    (OUT / 'visual_report.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    raise SystemExit('Browser screenshot failed: ' + proc.stdout[-1000:])

try:
    from PIL import Image, ImageStat, ImageFilter
except Exception as exc:
    report['status'] = 'FAIL'
    report['error'] = 'Pillow/PIL is required for pixel analysis: ' + repr(exc)
    (OUT / 'visual_report.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    raise

img = Image.open(png).convert('RGB')
# Neutral crop around the last pill, expected to stay dark/neutral without cyan bath.
neutral_crop = img.crop((1070, 350, 1275, 430))
neutral_crop.save(OUT / 'crop_neutral_no_global_blue.png')
stat = ImageStat.Stat(neutral_crop)
r, g, b = stat.mean
blue_excess = b - max(r, g)
report['checks'].append({'name': 'neutral_blue_excess', 'mean_rgb': [r, g, b], 'blue_excess': blue_excess, 'threshold': 34})
if blue_excess > 34:
    report['status'] = 'FAIL'
    report['error'] = f'Neutral pill is too blue globally: excess {blue_excess:.2f}'
    (OUT / 'visual_report.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    raise SystemExit(report['error'])

# Edge contrast on the lobe area: should have visible optical edge, not a flat plate.
lobe_crop = img.crop((70, 350, 245, 430))
lobe_crop.save(OUT / 'crop_lobe_edge.png')
gray = lobe_crop.convert('L')
edges = gray.filter(ImageFilter.FIND_EDGES)
edge_stat = ImageStat.Stat(edges).mean[0]
report['checks'].append({'name': 'lobe_edge_energy', 'edge_energy': edge_stat, 'threshold': 8.0})
if edge_stat < 8.0:
    report['status'] = 'FAIL'
    report['error'] = f'Lobe edge is too flat: edge energy {edge_stat:.2f}'
    (OUT / 'visual_report.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    raise SystemExit(report['error'])

# Ensure screenshot contains enough non-dark solid geometry colors.
small = img.resize((180, 120))
pixels = list(small.getdata())
colorful = sum(1 for rr,gg,bb in pixels if max(rr,gg,bb) > 110 and max(rr,gg,bb) - min(rr,gg,bb) > 45)
ratio = colorful / len(pixels)
report['checks'].append({'name': 'solid_geometry_color_presence', 'ratio': ratio, 'threshold': 0.018})
if ratio < 0.018:
    report['status'] = 'FAIL'
    report['error'] = f'Visual fixture lacks solid color geometry: ratio {ratio:.4f}'
    (OUT / 'visual_report.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    raise SystemExit(report['error'])

report['status'] = 'PASS'
report['screenshot'] = str(png)
report['crops'] = [str(OUT / 'crop_neutral_no_global_blue.png'), str(OUT / 'crop_lobe_edge.png')]
(OUT / 'visual_report.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps(report, indent=2))
