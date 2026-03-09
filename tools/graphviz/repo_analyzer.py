from pathlib import Path
import re

REPO = Path("F:/repos/hitech-os")

FILE_TYPES = (".ts",".tsx",".js",".jsx")

def scan_repo():

    files = []

    for p in REPO.rglob("*"):

        if p.suffix in FILE_TYPES:
            files.append(p)

    return files


def find_component(name):

    files = scan_repo()

    matches = []

    for f in files:

        try:
            text = f.read_text(encoding="utf-8")
        except:
            continue

        if name in text:
            matches.append(f)

    print(f"\nComponent '{name}' encontrado en:\n")

    for m in matches:
        print(m.relative_to(REPO))


def find_imports(file):

    pattern = r'import\s+.*?\s+from\s+[\'"](.*?)[\'"]'

    text = file.read_text(encoding="utf-8")

    return re.findall(pattern, text)


# consola interactiva

print("\nHITECH Repo Analyzer\n")

while True:

    cmd = input("\ncomando > ")

    if cmd.startswith("find "):

        name = cmd.replace("find ","")

        find_component(name)

    if cmd == "exit":
        break