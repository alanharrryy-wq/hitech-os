from pathlib import Path
import json
root=Path.cwd()
checks={"product_card_hook":("components/pos/pos-product-list.tsx",'data-prisma-component="ProductCard"'),"product_grid_hook":("components/pos/pos-product-list.tsx",'data-prisma-component="ProductGrid"'),"image_stage_hook":("components/pos/pos-product-list.tsx",'data-prisma-component="ProductImageStage"'),"search_hook":("components/pos/pos-product-search.tsx",'data-prisma-component="SearchBar"'),"cart_hook":("components/pos/pos-ticket-panel.tsx",'data-prisma-component="CartPanel"'),"checkout_hook":("components/pos/pos-ticket-panel.tsx",'data-prisma-component="CheckoutButton"'),"shell_hook":("components/tablet-shell/prisma-tablet-shell.tsx",'data-prisma-component="AppShell"'),"pos_css_lock":("components/pos/pos.module.css","PRISMA_POS_VISUAL_DOM_BINDING_LOCK_260503_V02_BEGIN"),"shell_css_lock":("components/tablet-shell/prisma-tablet-shell.module.css","PRISMA_POS_VISUAL_DOM_BINDING_LOCK_260503_V02_BEGIN")}
report={"ok":True,"checks":{}}
for name,(rel,needle) in checks.items():
    p=root/rel; text=p.read_text(encoding="utf-8",errors="replace") if p.exists() else ""; ok=needle in text; report["checks"][name]={"file":rel,"contains":ok}; report["ok"]=report["ok"] and ok
print(json.dumps(report,ensure_ascii=False,indent=2))
raise SystemExit(0 if report["ok"] else 1)
