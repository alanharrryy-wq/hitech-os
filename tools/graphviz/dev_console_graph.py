import os
from graphviz import Digraph

# ==============================
# CONFIG
# ==============================

REPO = r"F:\repos\hitech-os"
OUT = r"F:\repos\hitech-os\tools\graphviz\graphs\dev_console"

os.makedirs(OUT, exist_ok=True)

# ==============================
# DEV CONSOLE ARCHITECTURE
# ==============================

routes = [
    "app/pitch/page.tsx",
    "app/pitch/01-double-engine/page.tsx",
    "app/pitch/02-industrial-flow/page.tsx",
    "app/pitch/03-hitech-os/page.tsx",
    "app/pitch/04-valuation/page.tsx",
]

shell = "components/pitch/shell/pitch-shell.tsx"

mount = "components/pitch/debug/pitch-dev-console-mount.tsx"

tools = "components/pitch/debug/pitch-layer-dev-tools.tsx"

console_core = [
    "components/dev-console/DevConsole.tsx",
    "components/dev-console/DevConsoleContext.tsx",
    "components/dev-console/use-dev-console-runtime.ts",
    "components/dev-console/DevConsoleRegistry.tsx",
]

panels = [
    "panels/ConsoleHomePanel.tsx",
    "panels/PitchLayerDebugPanel.tsx",
    "panels/PitchRuntimeBridgePanel.tsx",
    "panels/PitchVisualOverlayPanel.tsx",
    "panels/PitchShareLookPanel.tsx",
]

# ==============================
# GRAPH
# ==============================

g = Digraph("DevConsoleArchitecture")
g.attr(rankdir="LR")

# routes
for r in routes:
    g.node(r, shape="box", color="lightgrey")

# shell
g.node(shell, shape="box", color="lightblue")

# mount
g.node(mount, shape="box", color="lightblue")

# tools
g.node(tools, shape="box", color="lightyellow")

# console core
for c in console_core:
    g.node(c, shape="box", color="lightgreen")

# panels
for p in panels:
    g.node(p, shape="box", color="mistyrose")

# edges

for r in routes:
    g.edge(r, shell)

g.edge(shell, mount)
g.edge(mount, tools)

for c in console_core:
    g.edge(tools, c)

for p in panels:
    g.edge("components/dev-console/DevConsoleRegistry.tsx", p)

# ==============================
# OUTPUT
# ==============================

out_file = os.path.join(OUT, "dev_console_architecture")

g.render(out_file, format="svg", cleanup=True)

print("Dev Console graph generado en:")
print(out_file + ".svg")

input("\nEnter para cerrar...")