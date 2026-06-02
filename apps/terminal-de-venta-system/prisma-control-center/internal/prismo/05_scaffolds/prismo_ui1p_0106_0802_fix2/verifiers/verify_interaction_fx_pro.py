from pathlib import Path
import json, sys, re
ROOT = Path(__file__).resolve().parents[1]
required = [
 'contracts/interaction/interaction_effect_matrix.json',
 'contracts/interaction/dependent_composer_state_machine.json',
 'contracts/visual/cloudglass_refrigerant_effects_v2.json',
 'contracts/render_blocks/interactive_render_blocks_v2.json',
 'contracts/codex/codex_250_interaction_improvements.json',
 'src-candidates/components/PrismoLiquidSelect.tsx',
 'src-candidates/components/PrismoCrystalCommandPalette.tsx',
 'src-candidates/components/PrismoFeedbackDock.tsx',
 'src-candidates/components/PrismoEvidenceDrawerVaul.tsx',
 'src-candidates/components/PrismoEChartsMiniPreview.tsx',
 'src-candidates/styles/prismo-interaction-fx-pro.css',
 'fixtures/interaction/interaction_scenario_corpus.json',
 'fixtures/qa/interaction_fx_qa_probes.json'
]
missing=[r for r in required if not (ROOT/r).exists()]
if missing:
    print({'ok':False,'error':'missing required FX2 files','missing':missing}); sys.exit(1)
composer=json.loads((ROOT/'contracts/composer/dependent_crystal_composer.json').read_text(encoding='utf-8'))
if len(composer.get('dropdowns',[])) != 3:
    print({'ok':False,'error':'composer must have exactly 3 dropdowns'}); sys.exit(1)
for d in composer.get('dropdowns',[]):
    if d.get('id') in {'scene','output_format','format','surface_format'}:
        print({'ok':False,'error':'fourth/output dropdown present'}); sys.exit(1)
inter=json.loads((ROOT/'contracts/interaction/interaction_effect_matrix.json').read_text(encoding='utf-8'))
if len(inter.get('libraries',[])) < 20:
    print({'ok':False,'error':'expected 20+ library effect mappings'}); sys.exit(1)
visual=json.loads((ROOT/'contracts/visual/cloudglass_refrigerant_effects_v2.json').read_text(encoding='utf-8'))
if len(visual.get('presets',{})) < 10:
    print({'ok':False,'error':'expected 10+ FX presets'}); sys.exit(1)
blocks=json.loads((ROOT/'contracts/render_blocks/interactive_render_blocks_v2.json').read_text(encoding='utf-8'))
if len(blocks.get('blocks',[])) < 18:
    print({'ok':False,'error':'expected 18+ interactive block specs'}); sys.exit(1)
tasks=json.loads((ROOT/'contracts/codex/codex_250_interaction_improvements.json').read_text(encoding='utf-8'))
if tasks.get('count',0) < 200:
    print({'ok':False,'error':'expected at least 200 Codex tasks'}); sys.exit(1)
css=(ROOT/'src-candidates/styles/prismo-interaction-fx-pro.css').read_text(encoding='utf-8')
for token in ['--prismo-glass-fill-g4','--prismo-anti-opacity-ceiling','prismo-command-palette','prismo-evidence-drawer']:
    if token not in css:
        print({'ok':False,'error':f'missing css token/class {token}'}); sys.exit(1)
forbidden_text = '\n'.join(p.read_text(encoding='utf-8', errors='ignore') for p in (ROOT/'src-candidates/components').glob('*.tsx'))
if re.search(r'output\s*format|scene\s*dropdown|próximamente|coming soon|preview only|safe mode', forbidden_text, re.I):
    print({'ok':False,'error':'forbidden UX label or output-format wording in component candidates'}); sys.exit(1)
print({'ok':True,'status':'PASS','libraries':len(inter.get('libraries',[])),'visual_presets':len(visual.get('presets',{})),'block_specs':len(blocks.get('blocks',[])),'codex_tasks':tasks.get('count')})
