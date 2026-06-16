# -*- coding: utf-8 -*-
from pathlib import Path
import json, sys
VALID = {"live","mapped","planned","reserved","deprecated"}
REQUIRED = ["id","canonicalName","family","layer","status","surfaces","allowedTokens","recipe","allowedLibraries","forbiddenPatterns","usedByRoutes","sourceFiles","migrationNotes","accessibilityNotes"]
MAPS = ["tablet-usage-map.json","pc-usage-map.json","mobile-usage-map.json","chart-lab-usage-map.json"]
class E(Exception): pass
def load(repo, rel):
    p=repo/rel
    if not p.exists(): raise E(f"Missing {rel}")
    return json.loads(p.read_text(encoding="utf-8"))
def ok(n,d=None): return {"name":n,"status":"PASS","details":d or {}}
def fail(n,e): return {"name":n,"status":"FAIL","error":str(e)}
def catalog(repo):
    data=load(repo,"config/prisma-visual/component-catalog.json"); ids=set()
    for c in data.get("components",[]):
        miss=[f for f in REQUIRED if f not in c]
        if miss: raise E(f"{c.get('id')} missing {miss}")
        if c["status"] not in VALID: raise E(f"{c['id']} invalid status")
        if c["id"] in ids: raise E(f"duplicate {c['id']}")
        ids.add(c["id"])
        if c["status"]=="live":
            if not c.get("sourceFiles"): raise E(f"live {c['id']} lacks sourceFiles")
            for f in c["sourceFiles"]:
                if not (repo/f).exists(): raise E(f"live source missing {f}")
        if c["status"]=="mapped" and not c.get("sourceFiles"): raise E(f"mapped {c['id']} lacks sourceFiles")
        if c["status"]=="deprecated" and not (c.get("replacement") or c.get("reason")): raise E(f"deprecated {c['id']} lacks replacement/reason")
    if not ids: raise E("catalog empty")
    return ok("validate-catalog", {"components":len(ids)})
def surfaces(repo):
    data=load(repo,"config/prisma-visual/surface-adapters.json"); got={a.get("surfaceId") for a in data.get("adapters",[])}
    req={"tablet","pc","mobile","chart-lab","kiosk","customer-display","warehouse-scanner","manager-console","training-mode","demo-mode"}
    if req-got: raise E(f"missing adapters {sorted(req-got)}")
    fields=["surfaceId","role","density","defaultTheme","backgroundContract","shellContract","layerBudget","allowedRecipes","allowedLibraries","forbiddenPatterns","accessibilityConstraints","runtimeBoundaries"]
    for a in data.get("adapters",[]):
        for f in fields:
            if f not in a: raise E(f"adapter {a.get('surfaceId')} missing {f}")
    return ok("validate-surfaces", {"adapters":len(got)})
def usage(repo):
    ids={c["id"] for c in load(repo,"config/prisma-visual/component-catalog.json")["components"]}; total=0
    for m in MAPS:
        d=load(repo,f"config/prisma-visual/{m}")
        if d.get("skipped"): continue
        for r in d.get("routes",[]):
            total += 1
            for cid in r.get("canonicalComponents",[]):
                if cid not in ids: raise E(f"{m} unknown component {cid}")
    return ok("validate-usage-maps", {"routes":total})
def imports(repo):
    idx=repo/"products/shared-ui/prisma/components/index.ts"
    if not idx.exists(): raise E("index.ts missing")
    text=idx.read_text(encoding="utf-8", errors="replace")
    names=["PrismaSurfacePanel","PrismaGlassCard","PrismaActionButton","PrismaStateBanner","PrismaRouteFrame","PrismaShellFrame","PrismaBackgroundLayer","PrismaProductCard","PrismaCartPanel","PrismaCheckoutPanel","PrismaDataPanel","PrismaMetricCard","PrismaCommandPanel"]
    for n in names:
        if n not in text or not (repo/f"products/shared-ui/prisma/components/{n}.tsx").exists(): raise E(f"missing {n}")
    pilot=repo/"products/tablet/app/app/prisma-visual-catalog/page.tsx"
    if not pilot.exists() or "shared-ui/prisma/components" not in pilot.read_text(encoding="utf-8", errors="replace"): raise E("pilot route shared import missing")
    return ok("validate-component-imports", {"required":len(names)})
def layer(repo):
    d=load(repo,"config/prisma-visual/layer-budget.json")
    if not isinstance(d.get("visualCatalog",{}).get("routeBudgets"), list): raise E("missing visualCatalog.routeBudgets")
    return ok("validate-layer-budget", {"routeBudgets":len(d["visualCatalog"]["routeBudgets"])})
def bg(repo):
    a=load(repo,"config/prisma-visual/surface-adapters.json")["adapters"]
    tab=next(x for x in a if x["surfaceId"]=="tablet")
    if tab["backgroundContract"]["runtimePublicUrl"] != "/visual-backgrounds/tablet/assets/tablet-cloudglass-default.jpg": raise E("tablet bg contract wrong")
    roots=[repo/"products/shared-ui/prisma/components",repo/"products/shared-ui/prisma/recipes",repo/"products/shared-ui/prisma/tokens",repo/"products/tablet/app/app/prisma-visual-catalog"]
    for root in roots:
        if root.exists():
            for p in root.rglob("*"):
                if not (p.is_file() and p.suffix.lower() in {".tsx",".ts",".css",".json",".md"}):
                    continue
                generated_names = {"PrismaComponents.module.css","types.ts","index.ts","PrismaSurfacePanel.tsx","PrismaGlassCard.tsx","PrismaActionButton.tsx","PrismaStateBanner.tsx","PrismaRouteFrame.tsx","PrismaShellFrame.tsx","PrismaBackgroundLayer.tsx","PrismaProductCard.tsx","PrismaCartPanel.tsx","PrismaCheckoutPanel.tsx","PrismaDataPanel.tsx","PrismaMetricCard.tsx","PrismaCommandPanel.tsx","prisma-theme.css","prisma-recipes.css","tablet-recipes.css","pc-recipes.css","mobile-recipes.css","chart-lab-recipes.css","page.tsx"}
                if p.name not in generated_names:
                    continue
                t=p.read_text(encoding="utf-8", errors="replace")
                for pat in ["!"+"important","products/0.backgrounds","soft-gray-clouds","Fuji"]:
                    if pat in t: raise E(f"forbidden {pat} in {p}")
    return ok("validate-background-contracts", {"tabletBackground":tab["backgroundContract"]["runtimePublicUrl"]})
def authority(repo):
    for rel in ["config/prisma-visual/archive-map.json","config/prisma-visual/recipe-map.json","config/prisma-visual/library-map.json"]: load(repo, rel)
    return ok("validate-visual-authority")
VALIDATORS={"catalog":catalog,"surfaces":surfaces,"usage-maps":usage,"component-imports":imports,"layer-budget":layer,"background-contracts":bg,"visual-authority":authority}
def run_named(repo, name):
    try: return VALIDATORS[name](repo)
    except Exception as e: return fail("validate-"+name, e)
def run_all(repo): return [run_named(repo,n) for n in VALIDATORS]
def main(argv=None):
    argv=argv or sys.argv[1:]; repo=Path(argv[0]) if argv else Path.cwd(); name=argv[1] if len(argv)>1 else "all"
    res=run_all(repo) if name=="all" else run_named(repo,name)
    print(json.dumps(res, indent=2, ensure_ascii=False))
    flat=res if isinstance(res,list) else [res]
    return 0 if all(x.get("status")=="PASS" for x in flat) else 1
if __name__=="__main__": raise SystemExit(main())
