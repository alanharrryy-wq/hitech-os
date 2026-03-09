import os
import re
from pathlib import Path
from graphviz import Digraph

# ==============================
# CONFIG
# ==============================

REPO = Path(r"F:\repos\hitech-os")

OUT = REPO / "tools" / "graphviz" / "graphs"
OUT.mkdir(parents=True, exist_ok=True)

FILE_TYPES = (".ts", ".tsx", ".js", ".jsx")

IMPORT_PATTERN = r'import\s+.*?\s+from\s+[\'"](.*?)[\'"]'

DEV_CONSOLE_PATTERNS = [
    "DevConsole",
    "PitchLayerDevTools",
    "PitchDevConsoleMount",
    "DevConsoleRegistry",
    "use-dev-console-runtime"
]

VISUAL_PATTERNS = [
    "FloatingWindow",
    "layout",
    "panel",
    "style",
    "position",
]

# ==============================
# SCAN REPO
# ==============================

files = []

for root, dirs, filenames in os.walk(REPO):

    if ".git" in root or "node_modules" in root:
        continue

    for f in filenames:

        if f.endswith(FILE_TYPES):

            files.append(Path(root) / f)

print("Files scanned:", len(files))

# ==============================
# DETECT SYSTEM
# ==============================

dev_console_files = []
visual_files = []

for file in files:

    try:
        text = file.read_text(encoding="utf-8")
    except:
        continue

    for pattern in DEV_CONSOLE_PATTERNS:

        if pattern in text:
            dev_console_files.append(file)
            break

    for pattern in VISUAL_PATTERNS:

        if pattern in text:
            visual_files.append(file)
            break

print("DevConsole related files:", len(dev_console_files))

# ==============================
# BUILD GRAPH
# ==============================

g = Digraph("DevConsoleSystem")
g.attr(rankdir="LR")

for file in dev_console_files:

    rel = file.relative_to(REPO).as_posix()

    g.node(rel)

    try:
        text = file.read_text(encoding="utf-8")
    except:
        continue

    imports = re.findall(IMPORT_PATTERN, text)

    for imp in imports:

        if imp.startswith("."):

            try:

                target = (file.parent / imp).resolve()

                if target.exists():

                    rel_target = target.relative_to(REPO).as_posix()

                    g.edge(rel, rel_target)

            except:
                pass

# ==============================
# OUTPUT
# ==============================

out_file = OUT / "dev_console_system"

g.render(out_file.as_posix(), format="svg", cleanup=True)

print("\nGraph generado:")
print(out_file.with_suffix(".svg"))

# ==============================
# VISUAL CONFIG REPORT
# ==============================

print("\nPossible visual configuration files:\n")

for f in visual_files[:20]:

    print("•", f.relative_to(REPO))

input("\nENTER para cerrar")