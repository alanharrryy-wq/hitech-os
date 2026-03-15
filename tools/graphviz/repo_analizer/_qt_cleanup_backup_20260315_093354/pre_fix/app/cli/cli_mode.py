#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import os
from pathlib import Path

from app.config import APP_TITLE, EXCLUDED_DIRS
from app.helpers import read_text_safe

def run_cli() -> None:
    print(f"{APP_TITLE} - Modo CLI")
    print("Comandos:")
    print("  repo <ruta>       -> define el repo")
    print("  find <texto>      -> busca en archivos TS/JS")
    print("  files             -> cuenta archivos")
    print("  exit              -> salir")
    print()

    repo: Path | None = None

    while True:
        try:
            cmd = input("comando > ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not cmd:
            continue
        if cmd.lower() in {"exit", "quit"}:
            break

        if cmd.startswith("repo "):
            p = Path(cmd[5:].strip().strip('"'))
            if p.exists() and p.is_dir():
                repo = p
                print(f"Repo = {repo}")
            else:
                print("Ruta inválida.")
            continue

        if cmd == "files":
            if not repo:
                print("Primero: repo <ruta>")
                continue
            count = 0
            for dirpath, dirnames, filenames in os.walk(repo):
                dirnames[:] = [d for d in dirnames if d not in EXCLUDED_DIRS]
                for fn in filenames:
                    if Path(fn).suffix.lower() in {".ts", ".tsx", ".js", ".jsx"}:
                        count += 1
            print(f"Archivos TS/JS: {count}")
            continue

        if cmd.startswith("find "):
            if not repo:
                print("Primero: repo <ruta>")
                continue
            q = cmd[5:].strip()
            if not q:
                print("Escribe algo para buscar.")
                continue
            hits = 0
            for dirpath, dirnames, filenames in os.walk(repo):
                dirnames[:] = [d for d in dirnames if d not in EXCLUDED_DIRS]
                for fn in filenames:
                    path = Path(dirpath) / fn
                    if path.suffix.lower() not in {".ts", ".tsx", ".js", ".jsx"}:
                        continue
                    try:
                        txt = read_text_safe(path)
                    except Exception:
                        continue
                    for i, line in enumerate(txt.splitlines(), start=1):
                        if q.lower() in line.lower():
                            rel = path.relative_to(repo).as_posix()
                            print(f"{rel}:{i}: {line.strip()}")
                            hits += 1
                            if hits >= 200:
                                print("Límite de 200 hits alcanzado.")
                                break
                    if hits >= 200:
                        break
                if hits >= 200:
                    break
            if hits == 0:
                print("Sin resultados.")
            continue

        print("Comando no reconocido.")
