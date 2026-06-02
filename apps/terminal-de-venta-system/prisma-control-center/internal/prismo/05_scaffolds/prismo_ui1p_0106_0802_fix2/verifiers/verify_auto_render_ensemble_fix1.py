from pathlib import Path
import json, sys, re
ROOT = Path(__file__).resolve().parents[1]
required = [
 'docs/codex/CODEX_MASTER_PROMPT.md',
 'contracts/render_blocks/render_block_registry.json',
 'contracts/render_blocks/auto_render_ensemble.json',
 'contracts/composer/dependent_crystal_composer.json',
 'contracts/visual/refrigerant_cloudglass_presets.json',
 'contracts/memory/memory_taxonomy.json',
 'contracts/codex/codex_150_improvements.json',
 'src-candidates/components/PrismoQueryComposer.tsx',
 'src-candidates/components/PrismoAutoRenderEnsemble.tsx',
 'src-candidates/styles/prismo-theater-cloudglass-pro.css',
 'fixtures/qa/qa_scenario_corpus.json'
]
missing=[x for x in required if not (ROOT/x).exists()]
if missing:
    print({'ok':False,'missing':missing}); sys.exit(1)
composer=json.loads((ROOT/'contracts/composer/dependent_crystal_composer.json').read_text(encoding='utf-8'))
if len(composer.get('dropdowns',[])) != 3:
    print({'ok':False,'error':'composer must have exactly 3 dropdowns'}); sys.exit(1)
for forbidden in ['scene','output_format']:
    if forbidden in json.dumps(composer).lower():
        # permitted only in forbidden control explanations, not dropdown ids
        ids=[d.get('id') for d in composer.get('dropdowns',[])]
        if forbidden in ids:
            print({'ok':False,'error':f'forbidden dropdown id present: {forbidden}'}); sys.exit(1)
if not composer.get('auto_render_ensemble',{}):
    print({'ok':False,'error':'missing auto_render_ensemble'}); sys.exit(1)
reg=json.loads((ROOT/'contracts/render_blocks/render_block_registry.json').read_text(encoding='utf-8'))
if 'raw_html' not in reg.get('forbidden_types',[]):
    print({'ok':False,'error':'raw_html not forbidden'}); sys.exit(1)
visual=json.loads((ROOT/'contracts/visual/refrigerant_cloudglass_presets.json').read_text(encoding='utf-8'))
if len(visual.get('presets',{})) < 7:
    print({'ok':False,'error':'expected at least 7 visual presets'}); sys.exit(1)
imps=json.loads((ROOT/'contracts/codex/codex_150_improvements.json').read_text(encoding='utf-8'))
if imps.get('count',0) < 100:
    print({'ok':False,'error':'expected at least 100 improvements'}); sys.exit(1)
composer_tsx=(ROOT/'src-candidates/components/PrismoQueryComposer.tsx').read_text(encoding='utf-8')
if 'setScene' in composer_tsx or 'Escena' in composer_tsx:
    print({'ok':False,'error':'query composer still contains scene dropdown logic'}); sys.exit(1)
css=(ROOT/'src-candidates/styles/prismo-theater-cloudglass-pro.css').read_text(encoding='utf-8')
if '--prismo-glass-fill-g4' not in css or 'Anti-opacity' not in css:
    print({'ok':False,'error':'missing anti-opacity CSS guard'}); sys.exit(1)
print({'ok':True,'status':'PASS','file_count':len([p for p in ROOT.rglob('*') if p.is_file()]), 'dropdowns':3, 'visual_presets':len(visual.get('presets',{})), 'improvements':imps.get('count')})
