from __future__ import annotations

import argparse
import sys
from pathlib import Path

def _bootstrap_repo_root() -> None:
    current = Path(__file__).resolve()
    for candidate in current.parents:
        if (candidate / "forgeos" / "shared" / "pyside6_glass").exists():
            value = str(candidate)
            if value not in sys.path:
                sys.path.insert(0, value)
            return

_bootstrap_repo_root()

from forgeos.shared.pyside6_glass.ui_baseline.builder.generator import generate_screen
from forgeos.shared.pyside6_glass.ui_baseline.builder.recipe import ScreenRecipe



def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Genera una screen gobernada para ui_baseline.")
    parser.add_argument("screen_name", help="Nombre lógico del screen.")
    parser.add_argument("--class-name", default="", help="Nombre explícito de la clase Python.")
    parser.add_argument("--output-dir", default=".", help="Directorio de salida para el archivo generado.")
    parser.add_argument("--preset", default="glass-default")
    parser.add_argument("--visual-level", default="standard")
    parser.add_argument("--role", dest="visual_role", default="workspace")
    parser.add_argument("--variant", dest="visual_variant", default="default")
    parser.add_argument("--emphasis", dest="visual_emphasis", default="medium")
    parser.add_argument("--fx", dest="visual_fx_level", default="subtle")
    parser.add_argument("--data-state", default="ready")
    parser.add_argument("--ingredient", action="append", default=[], help="Ingrediente a incluir. Repetible.")
    parser.add_argument("--no-hero", action="store_true")
    parser.add_argument("--no-main", action="store_true")
    parser.add_argument("--no-side", action="store_true")
    parser.add_argument("--no-footer", action="store_true")
    parser.add_argument("--no-status", action="store_true")
    parser.add_argument("--overwrite", action="store_true")
    return parser



def main() -> int:
    args = build_parser().parse_args()

    recipe = ScreenRecipe(
        screen_name=args.screen_name,
        class_name=args.class_name,
        output_dir=args.output_dir,
        preset=args.preset,
        visual_level=args.visual_level,
        visual_role=args.visual_role,
        visual_variant=args.visual_variant,
        visual_emphasis=args.visual_emphasis,
        visual_fx_level=args.visual_fx_level,
        data_state=args.data_state,
        include_hero=not args.no_hero,
        include_main=not args.no_main,
        include_side=not args.no_side,
        include_footer=not args.no_footer,
        include_status=not args.no_status,
        ingredients=args.ingredient,
    )

    path = generate_screen(recipe, overwrite=args.overwrite)
    print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
