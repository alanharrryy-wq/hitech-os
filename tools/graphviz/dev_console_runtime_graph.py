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

# solo estas zonas del repo
TARGET_FOLDERS = [
    "components/dev-console",
    "components/pitch/debug",
    "components/scene-studio",
    "lib/scene-studio",
]

FILE_TYPES = (".ts", ".tsx", ".js", ".jsx")

IMPORT_PATTERN = r'import\s+.*?\s+from\s+[\'"](.*?)[\'"]'

# ==============================
# UTIL
# ==============================

def should_include(path: Path):

    rel = path.relative_to(REPO).as_posix()

    for folder in TARGET_FOLDERS:
        if rel.startswith(folder):
            return True

    return False


def extract_imports(text):

    return re.findall(IMPORT_PATTERN, text)


# ==============================
# SCAN
# ==============================

files = []

for root, dirs, filenames in os.walk(REPO):

    for name in filenames:

        if not name.endswith(FILE_TYPES):
            continue

        path = Path(root) / name

        if should_include(path):
            files.append(path)

print("Files considered:", len(files))


# ==============================
# BUILD GRAPH
# ==============================

g = Digraph("DevConsoleRuntime")
g.attr(rankdir="LR")


for file in files:

    rel_file = file.relative_to(REPO).as_posix()

    g.node(rel_file)

    try:
        text = file.read_text(encoding="utf-8")
    except:
        continue

    imports = extract_imports(text)

    for imp in imports:

        if imp.startswith("."):

            try:
                resolved = (file.parent / imp).resolve()

                if resolved.exists():

                    rel_target = resolved.relative_to(REPO).as_posix()

                    g.edge(rel_file, rel_target)

            except:
                pass


# ==============================
# OUTPUT
# ==============================

out_file = OUT / "dev_console_runtime_graph"

g.render(out_file.as_posix(), format="svg", cleanup=True)

print("\nGraph generado:")
print(out_file.with_suffix(".svg"))

input("\nENTER para cerrar")