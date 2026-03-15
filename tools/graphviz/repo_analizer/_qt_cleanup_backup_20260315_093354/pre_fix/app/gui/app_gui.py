#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import csv
import json
import os
import platform
import queue as queue_mod
import re
import subprocess
import threading
import time
from collections import Counter, defaultdict
from itertools import islice
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinter.scrolledtext import ScrolledText

from app.config import (
    APP_TITLE,
    APP_VERSION,
    DEFAULT_MAX_RESULTS,
    DEFAULT_SEARCH_EXTS,
    EXCLUDED_DIRS,
    IMPORT_SCAN_EXTS,
    MAX_PREVIEW_FILE_SIZE,
    SETTINGS_FILE,
)
from app.helpers import extract_imports, human_size, now_str, read_text_safe, resolve_import
from app.gui.theme import apply_theme, apply_widget_theme


@dataclass
class SearchResult:
    relpath: str
    abspath: str
    display_path: str
    modified: str
    modified_ts: float
    size: int
    ext: str
    line: int
    matches: int
    snippet: str

class RepoAnalyzerApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title(f"{APP_TITLE} {APP_VERSION}")
        self.root.geometry("1520x960")
        self.root.minsize(1100, 700)

        self.queue: queue_mod.Queue = queue_mod.Queue()
        self.index_thread: threading.Thread | None = None
        self.search_thread: threading.Thread | None = None

        self.index_data: dict[str, Any] = {
            "root": "",
            "files": {},              # relpath -> FileEntry dict
            "folder_counts": {},      # folder -> count
            "top_level_counts": {},   # top folder -> count
            "ext_counts": {},         # .ext -> count
            "dependents": {},         # relpath -> list[relpath]
            "stats": {},              # misc stats
        }

        self.current_preview_path: str | None = None
        self.current_preview_rel: str | None = None
        self.search_results: list[SearchResult] = []

        self.script_dir = Path(__file__).resolve().parents[2]
        self.settings_path = self.script_dir / SETTINGS_FILE
        self.settings = self.load_settings()

        self.node_to_relpath: dict[str, str] = {}
        self.node_to_abspath: dict[str, str] = {}
        self.quick_filter_map: dict[str, str] = {}
        self.quick_filter_all_label = "(todas las carpetas)"
        self.quick_filter_manual_label = "(filtro manual)"
        self._tree_select_after_id: str | None = None
        self._suspend_tree_selection = False
        self._preview_text_exts = {
            ".py", ".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs",
            ".json", ".md", ".mdx", ".txt", ".csv", ".tsv", ".log", ".svg", ".xml",
            ".html", ".htm", ".css", ".scss", ".yml", ".yaml", ".toml", ".ini", ".cfg",
            ".sql", ".sh", ".bat", ".ps1", ".java", ".kt", ".go", ".rs", ".c", ".cpp", ".h", ".hpp"
        }

        self._build_vars()
        apply_theme(self.root)
        self._build_ui()
        apply_widget_theme(
            self.root,
            preview_text=self.preview_text,
            stats_text=self.stats_text,
            log_text=self.log_text,
            bookmarks_list=self.bookmarks_list,
            tree_menu=self.tree_menu,
            results_menu=self.results_menu,
            imports_menu=self.imports_menu,
        )
        self._bind_shortcuts()
        self._restore_settings_to_ui()
        self._poll_queue()

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.log("Listo. Elige un repo o usa el último guardado.")

        if self.repo_var.get() and Path(self.repo_var.get()).exists():
            self.start_indexing(auto=True)

    # -------------------------
    # Settings
    # -------------------------
    def load_settings(self) -> dict[str, Any]:
        defaults = {
            "recent_repos": [],
            "recent_searches": [],
            "window_geometry": "",
            "last_repo": "",
            "last_folder_filter": "(todo)",
            "last_ext_filter": "(todas)",
            "bookmarks": {},  # repo_path -> [relpaths]
        }
        if not self.settings_path.exists():
            return defaults
        try:
            data = json.loads(self.settings_path.read_text(encoding="utf-8"))
            defaults.update(data)
        except Exception:
            pass
        return defaults

    def save_settings(self) -> None:
        try:
            self.settings["recent_repos"] = self._dedupe_keep_order(
                [self.repo_var.get().strip(), *self.settings.get("recent_repos", [])]
            )[:20]
            if self.search_var.get().strip():
                self.settings["recent_searches"] = self._dedupe_keep_order(
                    [self.search_var.get().strip(), *self.settings.get("recent_searches", [])]
                )[:50]
            self.settings["last_repo"] = self.repo_var.get().strip()
            self.settings["last_folder_filter"] = self.folder_filter_var.get()
            self.settings["last_ext_filter"] = self.ext_filter_var.get()
            self.settings["window_geometry"] = self.root.winfo_geometry()
            self.settings_path.write_text(
                json.dumps(self.settings, indent=2, ensure_ascii=False),
                encoding="utf-8"
            )
        except Exception as e:
            self.log(f"No se pudo guardar settings: {e}")

    def _restore_settings_to_ui(self) -> None:
        if self.settings.get("window_geometry"):
            try:
                self.root.geometry(self.settings["window_geometry"])
            except Exception:
                pass

        self.repo_combo["values"] = self.settings.get("recent_repos", [])
        self.search_combo["values"] = self.settings.get("recent_searches", [])
        self.repo_var.set(self.settings.get("last_repo", ""))
        self.folder_filter_var.set(self.settings.get("last_folder_filter", "(todo)"))
        self.ext_filter_var.set(self.settings.get("last_ext_filter", "(todas)"))

    def _dedupe_keep_order(self, items: list[str]) -> list[str]:
        out = []
        seen = set()
        for item in items:
            x = (item or "").strip()
            if not x:
                continue
            if x not in seen:
                seen.add(x)
                out.append(x)
        return out

    # -------------------------
    # Variables
    # -------------------------
    def _build_vars(self) -> None:
        self.repo_var = tk.StringVar()
        self.search_var = tk.StringVar()
        self.quick_filter_var = tk.StringVar(value=self.quick_filter_all_label)
        self.folder_filter_var = tk.StringVar(value="(todo)")
        self.ext_filter_var = tk.StringVar(value="(todas)")
        self.sort_var = tk.StringVar(value="path")
        self.case_var = tk.BooleanVar(value=False)
        self.regex_var = tk.BooleanVar(value=False)
        self.word_var = tk.BooleanVar(value=False)
        self.names_only_var = tk.BooleanVar(value=False)
        self.include_hidden_var = tk.BooleanVar(value=False)
        self.max_results_var = tk.IntVar(value=DEFAULT_MAX_RESULTS)
        self.status_var = tk.StringVar(value="Sin repo indexado.")
        self.preview_title_var = tk.StringVar(value="Sin archivo seleccionado")
        self.stats_summary_var = tk.StringVar(value="0 archivos")

    # -------------------------
    # UI
    # -------------------------
    def _build_ui(self) -> None:
        self._build_toolbar()
        self._build_search_bar()
        self._build_main_area()
        self._build_status_bar()

    def _build_toolbar(self) -> None:
        top = ttk.Frame(self.root, padding=(10, 10, 10, 6))
        top.pack(fill="x")

        ttk.Label(top, text="Repo:", font=("Segoe UI", 10, "bold")).pack(side="left")

        self.repo_combo = ttk.Combobox(
            top, textvariable=self.repo_var, width=90
        )
        self.repo_combo.pack(side="left", fill="x", expand=True, padx=(8, 8))
        self.repo_combo.bind("<<ComboboxSelected>>", lambda e: self.start_indexing())

        ttk.Button(top, text="Examinar…", command=self.choose_repo).pack(side="left", padx=(0, 6))
        ttk.Button(top, text="Reindexar", command=self.start_indexing).pack(side="left", padx=(0, 6))
        ttk.Button(top, text="Abrir carpeta", command=self.open_current_repo_folder).pack(side="left", padx=(0, 6))
        ttk.Button(top, text="Usar último", command=self.use_last_repo).pack(side="left")

    def _build_search_bar(self) -> None:
        search_frame = ttk.Frame(self.root, padding=(10, 0, 10, 6))
        search_frame.pack(fill="x")

        ttk.Label(search_frame, text="Buscar:", font=("Segoe UI", 10, "bold")).grid(row=0, column=0, sticky="w")

        self.search_combo = ttk.Combobox(search_frame, textvariable=self.search_var)
        self.search_combo.grid(row=0, column=1, sticky="ew", padx=(8, 8))
        self.search_combo.bind("<Return>", lambda e: self.start_search())
        self.search_combo.bind("<Escape>", lambda e: self.clear_search())

        ttk.Button(search_frame, text="Buscar", command=self.start_search).grid(row=0, column=2, padx=(0, 6))
        ttk.Button(search_frame, text="Limpiar", command=self.clear_search).grid(row=0, column=3, padx=(0, 8))
        ttk.Button(search_frame, text="Exportar", command=self.export_results).grid(row=0, column=4)

        ttk.Label(search_frame, text="Carpeta:").grid(row=1, column=0, sticky="w", pady=(8, 0))
        self.folder_combo = ttk.Combobox(
            search_frame,
            textvariable=self.folder_filter_var,
            width=42,
            state="readonly",
            values=["(todo)"],
        )
        self.folder_combo.grid(row=1, column=1, sticky="w", padx=(8, 8), pady=(8, 0))
        self.folder_combo.bind("<<ComboboxSelected>>", lambda e: self.refresh_tree_filter_hint())

        ttk.Label(search_frame, text="Extensión:").grid(row=1, column=2, sticky="e", pady=(8, 0))
        self.ext_combo = ttk.Combobox(
            search_frame,
            textvariable=self.ext_filter_var,
            width=20,
            state="readonly",
            values=["(todas)", "TS/JS", "(sin extensión)"],
        )
        self.ext_combo.grid(row=1, column=3, sticky="w", pady=(8, 0), padx=(8, 8))

        ttk.Label(search_frame, text="Orden:").grid(row=1, column=4, sticky="e", pady=(8, 0))
        self.sort_combo = ttk.Combobox(
            search_frame,
            textvariable=self.sort_var,
            width=14,
            state="readonly",
            values=["path", "modified", "size", "ext"],
        )
        self.sort_combo.grid(row=1, column=5, sticky="w", pady=(8, 0), padx=(8, 0))

        opts = ttk.Frame(search_frame)
        opts.grid(row=2, column=0, columnspan=6, sticky="w", pady=(8, 0))

        ttk.Checkbutton(opts, text="Case sensitive", variable=self.case_var).pack(side="left", padx=(0, 8))
        ttk.Checkbutton(opts, text="Regex", variable=self.regex_var).pack(side="left", padx=(0, 8))
        ttk.Checkbutton(opts, text="Whole word", variable=self.word_var).pack(side="left", padx=(0, 8))
        ttk.Checkbutton(opts, text="Solo nombres", variable=self.names_only_var).pack(side="left", padx=(0, 8))
        ttk.Checkbutton(opts, text="Incluir ocultos", variable=self.include_hidden_var).pack(side="left", padx=(0, 8))

        ttk.Label(opts, text="Máx. resultados:").pack(side="left", padx=(16, 6))
        self.max_results_spin = ttk.Spinbox(
            opts,
            from_=50,
            to=10000,
            increment=50,
            textvariable=self.max_results_var,
            width=8,
        )
        self.max_results_spin.pack(side="left")

        search_frame.columnconfigure(1, weight=1)

    def _build_main_area(self) -> None:
        main = ttk.PanedWindow(self.root, orient="horizontal")
        main.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        left_wrap = ttk.Frame(main)
        right_wrap = ttk.Frame(main)
        main.add(left_wrap, weight=4)
        main.add(right_wrap, weight=6)

        self._build_left_panel(left_wrap)
        self._build_right_panel(right_wrap)

    def _build_left_panel(self, parent: ttk.Frame) -> None:
        left_nb = ttk.Notebook(parent)
        left_nb.pack(fill="both", expand=True)

        explorer_tab = ttk.Frame(left_nb, padding=8)
        bookmarks_tab = ttk.Frame(left_nb, padding=8)

        left_nb.add(explorer_tab, text="Explorador")
        left_nb.add(bookmarks_tab, text="Bookmarks")

        quick_frame = ttk.LabelFrame(explorer_tab, text="Quick filters")
        quick_frame.pack(fill="x", pady=(0, 8))

        quick_row = ttk.Frame(quick_frame)
        quick_row.pack(fill="x", padx=8, pady=8)
        ttk.Label(quick_row, text="Top folders:").pack(side="left")
        self.quick_filter_combo = ttk.Combobox(
            quick_row,
            textvariable=self.quick_filter_var,
            state="readonly",
            values=[self.quick_filter_all_label],
            width=36,
        )
        self.quick_filter_combo.pack(side="left", fill="x", expand=True, padx=(8, 8))
        self.quick_filter_combo.bind("<<ComboboxSelected>>", lambda e: self.on_quick_filter_selected())
        ttk.Button(quick_row, text="Aplicar", command=self.on_quick_filter_selected).pack(side="left")

        tree_frame = ttk.Frame(explorer_tab)
        tree_frame.pack(fill="both", expand=True)

        self.repo_tree = ttk.Treeview(tree_frame, show="tree", selectmode="browse", style="RepoTree.Treeview")
        self.repo_tree.heading("#0", text="Repositorio", anchor="w")
        self.repo_tree.column("#0", width=560, minwidth=320, stretch=True, anchor="w")
        self.repo_tree.pack(side="left", fill="both", expand=True)

        tree_scroll_y = ttk.Scrollbar(tree_frame, orient="vertical", command=self.repo_tree.yview)
        tree_scroll_y.pack(side="right", fill="y")
        tree_scroll_x = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.repo_tree.xview)
        tree_scroll_x.pack(side="bottom", fill="x")
        self.repo_tree.configure(yscrollcommand=tree_scroll_y.set, xscrollcommand=tree_scroll_x.set)

        self.repo_tree.bind("<<TreeviewSelect>>", self.on_tree_select)
        self.repo_tree.bind("<Double-1>", self.on_tree_double_click)
        self.repo_tree.bind("<Button-3>", self.show_tree_menu)

        bm_toolbar = ttk.Frame(bookmarks_tab)
        bm_toolbar.pack(fill="x", pady=(0, 6))
        ttk.Button(bm_toolbar, text="Abrir", command=self.open_selected_bookmark).pack(side="left", padx=(0, 6))
        ttk.Button(bm_toolbar, text="Quitar", command=self.remove_selected_bookmark).pack(side="left", padx=(0, 6))
        ttk.Button(bm_toolbar, text="Refrescar", command=self.refresh_bookmarks_view).pack(side="left")

        self.bookmarks_list = tk.Listbox(bookmarks_tab, activestyle="dotbox")
        self.bookmarks_list.pack(fill="both", expand=True)
        self.bookmarks_list.bind("<Double-1>", lambda e: self.open_selected_bookmark())

        self.tree_menu = tk.Menu(self.root, tearoff=0)
        self.tree_menu.add_command(label="Abrir preview", command=self.tree_menu_open_preview)
        self.tree_menu.add_command(label="Abrir con sistema", command=self.tree_menu_open_system)
        self.tree_menu.add_command(label="Copiar ruta", command=self.tree_menu_copy_path)
        self.tree_menu.add_command(label="Bookmark", command=self.tree_menu_add_bookmark)
        self.tree_menu.add_separator()
        self.tree_menu.add_command(label="Filtrar por esta carpeta", command=self.tree_menu_filter_folder)

    def _build_right_panel(self, parent: ttk.Frame) -> None:
        right_paned = ttk.PanedWindow(parent, orient="vertical")
        right_paned.pack(fill="both", expand=True)

        top = ttk.Frame(right_paned)
        bottom = ttk.Frame(right_paned)

        right_paned.add(top, weight=2)
        right_paned.add(bottom, weight=1)

        self._build_preview_notebook(top)
        self._build_results_panel(bottom)

    def _build_preview_notebook(self, parent: ttk.Frame) -> None:
        nb = ttk.Notebook(parent)
        nb.pack(fill="both", expand=True)

        preview_tab = ttk.Frame(nb, padding=6)
        imports_tab = ttk.Frame(nb, padding=6)
        dependents_tab = ttk.Frame(nb, padding=6)
        stats_tab = ttk.Frame(nb, padding=6)
        log_tab = ttk.Frame(nb, padding=6)

        nb.add(preview_tab, text="Preview")
        nb.add(imports_tab, text="Imports")
        nb.add(dependents_tab, text="Dependents")
        nb.add(stats_tab, text="Stats")
        nb.add(log_tab, text="Log")

        # Preview
        preview_toolbar = ttk.Frame(preview_tab)
        preview_toolbar.pack(fill="x", pady=(0, 6))

        ttk.Label(preview_toolbar, textvariable=self.preview_title_var, font=("Segoe UI", 10, "bold")).pack(side="left")
        ttk.Button(preview_toolbar, text="Abrir con sistema", command=self.open_current_preview_with_system).pack(side="right", padx=(6, 0))
        ttk.Button(preview_toolbar, text="Copiar ruta", command=self.copy_current_preview_path).pack(side="right", padx=(6, 0))
        ttk.Button(preview_toolbar, text="Bookmark", command=self.add_current_preview_bookmark).pack(side="right", padx=(6, 0))
        ttk.Button(preview_toolbar, text="Imports", command=self.populate_imports_for_current).pack(side="right", padx=(6, 0))

        self.preview_text = ScrolledText(preview_tab, wrap="none", font=("Consolas", 10))
        self.preview_text.pack(fill="both", expand=True)
        self.preview_text.config(state="disabled")

        self.preview_text.tag_configure("active_line", background="#2d4f7d", foreground="white")
        self.preview_text.tag_configure("match", background="#f7e08a", foreground="black")

        # Imports
        self.imports_tree = ttk.Treeview(imports_tab, columns=("raw", "resolved"), show="headings", style="Data.Treeview")
        self.imports_tree.heading("raw", text="Import")
        self.imports_tree.heading("resolved", text="Resuelto")
        self.imports_tree.column("raw", width=300, anchor="w")
        self.imports_tree.column("resolved", width=500, anchor="w")
        self.imports_tree.pack(fill="both", expand=True)
        self.imports_tree.bind("<Double-1>", self.on_imports_double_click)
        self.imports_tree.bind("<Button-3>", self.show_imports_menu)

        self.imports_menu = tk.Menu(self.root, tearoff=0)
        self.imports_menu.add_command(label="Abrir target", command=self.open_selected_import_target)
        self.imports_menu.add_command(label="Copiar import", command=self.copy_selected_import_raw)

        # Dependents
        self.dependents_tree = ttk.Treeview(dependents_tab, columns=("path",), show="headings", style="Data.Treeview")
        self.dependents_tree.heading("path", text="Archivo dependiente")
        self.dependents_tree.column("path", width=800, anchor="w")
        self.dependents_tree.pack(fill="both", expand=True)
        self.dependents_tree.bind("<Double-1>", self.on_dependents_double_click)

        # Stats
        self.stats_text = ScrolledText(stats_tab, wrap="word", font=("Consolas", 10), height=10)
        self.stats_text.pack(fill="both", expand=True)
        self.stats_text.config(state="disabled")

        # Log
        self.log_text = ScrolledText(log_tab, wrap="word", font=("Consolas", 10), height=10)
        self.log_text.pack(fill="both", expand=True)
        self.log_text.config(state="disabled")

    def _build_results_panel(self, parent: ttk.Frame) -> None:
        frame = ttk.LabelFrame(parent, text="Resultados")
        frame.pack(fill="both", expand=True, padx=6, pady=6)

        self.results_tree = ttk.Treeview(
            frame,
            columns=("display_path", "modified", "size", "ext"),
            show="headings",
            style="Results.Treeview",
        )
        self.results_tree.heading("display_path", text="Ruta completa sin extensión")
        self.results_tree.heading("modified", text="Modificado")
        self.results_tree.heading("size", text="Tamaño")
        self.results_tree.heading("ext", text="Ext.")

        self.results_tree.column("display_path", width=760, anchor="w")
        self.results_tree.column("modified", width=160, anchor="center")
        self.results_tree.column("size", width=110, anchor="e")
        self.results_tree.column("ext", width=110, anchor="center")

        self.results_tree.pack(side="left", fill="both", expand=True)
        scroll_y = ttk.Scrollbar(frame, orient="vertical", command=self.results_tree.yview)
        scroll_y.pack(side="right", fill="y")
        scroll_x = ttk.Scrollbar(frame, orient="horizontal", command=self.results_tree.xview)
        scroll_x.pack(side="bottom", fill="x")
        self.results_tree.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)

        self.results_tree.bind("<Double-1>", self.on_result_double_click)
        self.results_tree.bind("<Button-3>", self.show_results_menu)

        self.results_menu = tk.Menu(self.root, tearoff=0)
        self.results_menu.add_command(label="Abrir preview", command=self.open_selected_result)
        self.results_menu.add_command(label="Abrir con sistema", command=self.open_selected_result_system)
        self.results_menu.add_command(label="Copiar ruta", command=self.copy_selected_result_path)
        self.results_menu.add_command(label="Revelar en árbol", command=self.reveal_selected_result_in_tree)

    def _build_status_bar(self) -> None:
        status = ttk.Frame(self.root, padding=(10, 0, 10, 10))
        status.pack(fill="x")

        self.progress = ttk.Progressbar(status, mode="indeterminate", length=180, style="Repo.Horizontal.TProgressbar")
        self.progress.pack(side="left")

        ttk.Label(status, textvariable=self.status_var).pack(side="left", padx=(10, 14))
        ttk.Label(status, textvariable=self.stats_summary_var, font=("Segoe UI", 9, "bold")).pack(side="right")

    # -------------------------
    # Logging
    # -------------------------
    def log(self, msg: str) -> None:
        stamp = now_str()
        line = f"[{stamp}] {msg}\n"
        self.log_text.config(state="normal")
        self.log_text.insert("end", line)
        self.log_text.see("end")
        self.log_text.config(state="disabled")
        self.status_var.set(msg)

    # -------------------------
    # Shortcuts
    # -------------------------
    def _bind_shortcuts(self) -> None:
        self.root.bind("<Control-l>", lambda e: self.repo_combo.focus_set())
        self.root.bind("<Control-f>", lambda e: self.search_combo.focus_set())
        self.root.bind("<Control-o>", lambda e: self.choose_repo())
        self.root.bind("<Control-r>", lambda e: self.start_indexing())
        self.root.bind("<Control-e>", lambda e: self.export_results())
        self.root.bind("<F5>", lambda e: self.start_indexing())
        self.root.bind("<Escape>", lambda e: self.clear_search())

    # -------------------------
    # Repo selection / indexing
    # -------------------------
    def choose_repo(self) -> None:
        initial = self.repo_var.get().strip() or str(Path.home())
        folder = filedialog.askdirectory(title="Selecciona el repo", initialdir=initial)
        if not folder:
            return
        self.repo_var.set(folder)
        self.start_indexing()

    def use_last_repo(self) -> None:
        last_repo = self.settings.get("last_repo", "")
        if last_repo and Path(last_repo).exists():
            self.repo_var.set(last_repo)
            self.start_indexing()
        else:
            messagebox.showinfo(APP_TITLE, "No hay último repo válido guardado.")

    def open_current_repo_folder(self) -> None:
        repo = self.repo_var.get().strip()
        if repo and Path(repo).exists():
            self.open_with_system(repo)

    def start_indexing(self, auto: bool = False) -> None:
        repo = self.repo_var.get().strip()
        if not repo:
            if not auto:
                messagebox.showwarning(APP_TITLE, "Primero elige una carpeta de repo.")
            return
        repo_path = Path(repo)
        if not repo_path.exists() or not repo_path.is_dir():
            messagebox.showerror(APP_TITLE, "La ruta del repo no existe o no es una carpeta.")
            return

        if self.index_thread and self.index_thread.is_alive():
            messagebox.showinfo(APP_TITLE, "Ya hay un indexado en progreso.")
            return

        self.progress.start(10)
        self.status_var.set("Indexando repo…")
        self.log(f"Indexando: {repo_path}")
        self.clear_trees_for_reindex()

        include_hidden = self.include_hidden_var.get()

        self.index_thread = threading.Thread(
            target=self._index_worker,
            args=(repo_path, include_hidden),
            daemon=True
        )
        self.index_thread.start()

    def clear_trees_for_reindex(self) -> None:
        self.repo_tree.delete(*self.repo_tree.get_children())
        self.results_tree.delete(*self.results_tree.get_children())
        self.imports_tree.delete(*self.imports_tree.get_children())
        self.dependents_tree.delete(*self.dependents_tree.get_children())
        self.quick_filter_map.clear()
        if hasattr(self, "quick_filter_combo"):
            self.quick_filter_combo["values"] = [self.quick_filter_all_label]
        self.quick_filter_var.set(self.quick_filter_all_label)
        self.node_to_relpath.clear()
        self.node_to_abspath.clear()
        self.preview_title_var.set("Sin archivo seleccionado")
        self.search_results = []

    def _index_worker(self, repo_path: Path, include_hidden: bool) -> None:
        try:
            t0 = time.time()
            files: dict[str, dict[str, Any]] = {}
            folder_counts: Counter = Counter()
            top_level_counts: Counter = Counter()
            ext_counts: Counter = Counter()
            dependents: dict[str, list[str]] = defaultdict(list)
            skipped = 0
            total_scanned = 0

            all_paths: list[Path] = []

            for dirpath, dirnames, filenames in os.walk(repo_path):
                dir_path = Path(dirpath)

                filtered = []
                for d in dirnames:
                    if d in EXCLUDED_DIRS:
                        continue
                    if not include_hidden and d.startswith('.'):
                        continue
                    filtered.append(d)
                dirnames[:] = filtered

                for fn in filenames:
                    if not include_hidden and fn.startswith('.'):
                        continue
                    path = dir_path / fn
                    total_scanned += 1
                    all_paths.append(path)

            total_candidates = len(all_paths)
            self.queue.put(("index_progress", f"Escaneando {total_candidates} archivos candidatos…"))

            for idx, path in enumerate(all_paths, start=1):
                try:
                    rel = path.relative_to(repo_path).as_posix()
                    ext = path.suffix.lower()
                    stat = path.stat()
                    size = stat.st_size
                    mtime = stat.st_mtime
                    modified = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(mtime))
                    is_text = path.suffix.lower() in DEFAULT_SEARCH_EXTS

                    imports: list[str] = []
                    if path.suffix.lower() in IMPORT_SCAN_EXTS and size <= MAX_PREVIEW_FILE_SIZE:
                        try:
                            txt = read_text_safe(path)
                            imports = extract_imports(txt)
                        except Exception:
                            imports = []

                    files[rel] = {
                        'relpath': rel,
                        'abspath': str(path),
                        'ext': ext,
                        'size': size,
                        'mtime': mtime,
                        'modified': modified,
                        'imports': imports,
                        'is_text': is_text,
                    }

                    ext_counts[ext] += 1

                    parts = rel.split('/')
                    if len(parts) > 1:
                        for i in range(1, len(parts)):
                            folder = '/'.join(parts[:i])
                            folder_counts[folder] += 1
                        top_level_counts[parts[0]] += 1
                    else:
                        folder_counts['(root)'] += 1
                        top_level_counts['(root)'] += 1

                    if idx % 100 == 0 or idx == total_candidates:
                        self.queue.put(("index_progress", f"Indexando {idx}/{total_candidates}…"))

                except Exception:
                    skipped += 1
                    continue

            for rel, info in files.items():
                src_path = Path(info['abspath'])
                for raw_imp in info['imports']:
                    resolved = resolve_import(repo_path, src_path, raw_imp)
                    if resolved and resolved in files:
                        dependents[resolved].append(rel)

            elapsed = time.time() - t0

            stats = {
                'total_candidates': total_candidates,
                'total_files': len(files),
                'skipped': skipped,
                'elapsed_sec': round(elapsed, 2),
                'largest_files': sorted(
                    [{'relpath': r, 'size': f['size']} for r, f in files.items()],
                    key=lambda x: x['size'],
                    reverse=True,
                )[:15],
            }

            payload = {
                'root': str(repo_path),
                'files': files,
                'folder_counts': dict(sorted(folder_counts.items())),
                'top_level_counts': dict(sorted(top_level_counts.items(), key=lambda x: (-x[1], x[0]))),
                'ext_counts': dict(sorted(ext_counts.items(), key=lambda x: (-x[1], x[0]))),
                'dependents': {k: sorted(set(v)) for k, v in dependents.items()},
                'stats': stats,
            }

            self.queue.put(("index_done", payload))

        except Exception as e:
            self.queue.put(("error", f"Error indexando repo: {e}"))

    # -------------------------
    # Queue polling
    # -------------------------
    def _poll_queue(self) -> None:
        try:
            while True:
                item = self.queue.get_nowait()
                kind = item[0]

                if kind == "index_progress":
                    self.status_var.set(item[1])

                elif kind == "index_done":
                    self.progress.stop()
                    self.index_data = item[1]
                    self.on_index_ready()

                elif kind == "search_progress":
                    self.status_var.set(item[1])

                elif kind == "search_done":
                    self.progress.stop()
                    self.search_results = item[1]
                    self.on_search_ready()

                elif kind == "error":
                    self.progress.stop()
                    self.log(item[1])
                    messagebox.showerror(APP_TITLE, item[1])

        except queue_mod.Empty:
            pass

        self.root.after(120, self._poll_queue)

    def on_index_ready(self) -> None:
        root_path = self.index_data["root"]
        total_files = len(self.index_data["files"])
        ext_counts = self.index_data["ext_counts"]
        elapsed = self.index_data["stats"].get("elapsed_sec", 0)

        self.log(f"Index listo: {total_files} archivos en {elapsed}s")
        self.stats_summary_var.set(f"{total_files} archivos | {len(ext_counts)} extensiones")
        self.save_settings()

        self.rebuild_repo_tree()
        self.rebuild_filter_values()
        self.rebuild_quick_filters()
        self.refresh_bookmarks_view()
        self.render_stats()
        if total_files == 0:
            self.log("Indexado terminó pero no encontró archivos válidos. Revisa app/models.py o filtros de extensiones si sigue vacío.")
        self.status_var.set(f"Repo indexado: {root_path}")

    # -------------------------
    # Tree building
    # -------------------------
    def rebuild_repo_tree(self) -> None:
        self.repo_tree.delete(*self.repo_tree.get_children())
        self.node_to_relpath.clear()
        self.node_to_abspath.clear()

        repo_root = self.index_data.get('root', '')
        if not repo_root:
            return

        root_label = Path(repo_root).name or repo_root
        root_id = self.repo_tree.insert('', 'end', text=root_label, open=True)

        folder_children: dict[str, set[str]] = defaultdict(set)
        file_children: dict[str, list[str]] = defaultdict(list)

        for rel in self.index_data['files'].keys():
            parts = rel.split('/')
            if len(parts) == 1:
                file_children[''].append(rel)
                continue

            for depth in range(1, len(parts)):
                folder_rel = '/'.join(parts[:depth])
                parent_rel = '/'.join(parts[:depth - 1]) if depth > 1 else ''
                folder_children[parent_rel].add(folder_rel)

            file_children['/'.join(parts[:-1])].append(rel)

        def insert_branch(parent_node: str, parent_rel: str, depth: int) -> None:
            child_folders = sorted(folder_children.get(parent_rel, set()), key=lambda x: Path(x).name.lower())
            child_files = sorted(file_children.get(parent_rel, []), key=lambda x: Path(x).name.lower())

            for folder_rel in child_folders:
                node = self.repo_tree.insert(parent_node, 'end', text=Path(folder_rel).name, open=(depth < 1))
                self.node_to_relpath[node] = folder_rel
                insert_branch(node, folder_rel, depth + 1)

            for file_rel in child_files:
                node = self.repo_tree.insert(parent_node, 'end', text=Path(file_rel).name, open=False)
                self.node_to_relpath[node] = file_rel
                self.node_to_abspath[node] = self.index_data['files'][file_rel]['abspath']

        insert_branch(root_id, '', 0)
        self.repo_tree.item(root_id, open=True)

        longest = max([len(root_label)] + [len(p) for p in self.index_data['files'].keys()], default=40)
        self.repo_tree.column('#0', width=max(680, min(2600, longest * 7)))

    def rebuild_filter_values(self) -> None:
        folders = ['(todo)'] + sorted(self.index_data['folder_counts'].keys())
        self.folder_combo['values'] = folders

        existing = self.folder_filter_var.get()
        self.folder_filter_var.set(existing if existing in folders else '(todo)')

        detected_exts = sorted([ext for ext in self.index_data['ext_counts'].keys() if ext], key=str.lower)
        exts = ['(todas)', 'TS/JS', '(sin extensión)', *detected_exts]
        self.ext_combo['values'] = exts

        current_ext = self.ext_filter_var.get().strip()
        self.ext_filter_var.set(current_ext if current_ext in exts else '(todas)')

    def rebuild_quick_filters(self) -> None:
        counts = self.index_data.get('top_level_counts', {})
        values = [self.quick_filter_all_label]
        self.quick_filter_map = {self.quick_filter_all_label: '(todo)'}

        for folder, count in list(counts.items())[:30]:
            label = f"{folder} ({count})"
            values.append(label)
            self.quick_filter_map[label] = folder

        self.quick_filter_combo['values'] = values
        self._sync_quick_filter_combo()

    def _sync_quick_filter_combo(self) -> None:
        current_folder = self.folder_filter_var.get()
        for label, folder in self.quick_filter_map.items():
            if folder == current_folder:
                self.quick_filter_var.set(label)
                return

        values = list(self.quick_filter_combo.cget('values'))
        if current_folder not in ('', '(todo)'):
            if self.quick_filter_manual_label not in values:
                values = [self.quick_filter_all_label, self.quick_filter_manual_label, *[v for v in values if v not in {self.quick_filter_all_label, self.quick_filter_manual_label}]]
                self.quick_filter_combo['values'] = values
            self.quick_filter_var.set(self.quick_filter_manual_label)
        else:
            self.quick_filter_var.set(self.quick_filter_all_label)

    def on_quick_filter_selected(self) -> None:
        label = self.quick_filter_var.get().strip() or self.quick_filter_all_label
        folder = self.quick_filter_map.get(label, '(todo)')
        self.set_folder_filter(folder)

    def set_folder_filter(self, folder: str) -> None:
        self.folder_filter_var.set(folder)
        self._sync_quick_filter_combo()
        self.refresh_tree_filter_hint()

    def refresh_tree_filter_hint(self) -> None:
        folder = self.folder_filter_var.get()
        if folder == "(todo)":
            self.status_var.set("Filtro de carpeta: todo el repo")
        else:
            self.status_var.set(f"Filtro de carpeta activo: {folder}")

    # -------------------------
    # Search
    # -------------------------
    def clear_search(self) -> None:
        self.search_var.set("")
        self.results_tree.delete(*self.results_tree.get_children())
        self.search_results = []
        self.status_var.set("Búsqueda limpia.")
        self.preview_text.config(state="normal")
        self.preview_text.tag_remove("match", "1.0", "end")
        self.preview_text.config(state="disabled")

    def start_search(self) -> None:
        if not self.index_data.get("files"):
            messagebox.showwarning(APP_TITLE, "Primero indexa un repo.")
            return

        if self.search_thread and self.search_thread.is_alive():
            messagebox.showinfo(APP_TITLE, "Ya hay una búsqueda en progreso.")
            return

        query = self.search_var.get().strip()
        folder = self.folder_filter_var.get()
        ext_filter = self.ext_filter_var.get()
        sort_mode = self.sort_var.get()
        case_sensitive = self.case_var.get()
        is_regex = self.regex_var.get()
        whole_word = self.word_var.get()
        names_only = self.names_only_var.get()
        max_results = max(1, int(self.max_results_var.get() or DEFAULT_MAX_RESULTS))

        repo_root = self.index_data["root"]
        files_snapshot = dict(self.index_data["files"])

        self.progress.start(10)
        self.status_var.set("Buscando…")
        self.log(
            f"Buscar: '{query or '(vacío)'}' | folder={folder} | ext={ext_filter} | "
            f"regex={is_regex} | names_only={names_only}"
        )

        self.search_thread = threading.Thread(
            target=self._search_worker,
            args=(
                repo_root, files_snapshot, query, folder, ext_filter, sort_mode,
                case_sensitive, is_regex, whole_word, names_only, max_results
            ),
            daemon=True
        )
        self.search_thread.start()

    def _search_worker(
        self,
        repo_root: str,
        files_snapshot: dict[str, dict[str, Any]],
        query: str,
        folder: str,
        ext_filter: str,
        sort_mode: str,
        case_sensitive: bool,
        is_regex: bool,
        whole_word: bool,
        names_only: bool,
        max_results: int,
    ) -> None:
        try:
            results: list[SearchResult] = []

            def file_allowed(rel: str, ext: str) -> bool:
                normalized_ext_filter = ext_filter.strip() or '(todas)'
                if folder != '(todo)':
                    if rel != folder and not rel.startswith(folder + '/'):
                        return False
                if normalized_ext_filter == 'TS/JS':
                    return ext in {'.ts', '.tsx', '.js', '.jsx'}
                if normalized_ext_filter == '(todas)':
                    return True
                if normalized_ext_filter == '(sin extensión)':
                    return not ext
                return ext == normalized_ext_filter

            compiled = None
            if query:
                if is_regex:
                    flags = 0 if case_sensitive else re.IGNORECASE
                    compiled = re.compile(query, flags)
                else:
                    q = re.escape(query)
                    if whole_word:
                        q = rf"\b{q}\b"
                    flags = 0 if case_sensitive else re.IGNORECASE
                    compiled = re.compile(q, flags)

            candidates = [(rel, info) for rel, info in files_snapshot.items() if file_allowed(rel, info.get('ext', ''))]
            total = len(candidates)

            for idx, (rel, info) in enumerate(candidates, start=1):
                abspath = info['abspath']
                ext = info.get('ext', '')
                display_path = os.path.splitext(abspath)[0]
                modified = info.get('modified', '')
                modified_ts = float(info.get('mtime', 0.0) or 0.0)
                size = int(info.get('size', 0) or 0)

                if idx % 75 == 0 or idx == total:
                    self.queue.put(('search_progress', f'Buscando {idx}/{total}…'))

                if names_only:
                    haystack = rel if case_sensitive else rel.lower()
                    needle = query if case_sensitive else query.lower()
                    if not query or (needle in haystack):
                        results.append(SearchResult(
                            relpath=rel,
                            abspath=abspath,
                            display_path=display_path,
                            modified=modified,
                            modified_ts=modified_ts,
                            size=size,
                            ext=ext or '(sin extensión)',
                            line=0,
                            matches=1 if query else 0,
                            snippet=rel,
                        ))
                    if len(results) >= max_results:
                        break
                    continue

                if not query:
                    results.append(SearchResult(
                        relpath=rel,
                        abspath=abspath,
                        display_path=display_path,
                        modified=modified,
                        modified_ts=modified_ts,
                        size=size,
                        ext=ext or '(sin extensión)',
                        line=0,
                        matches=0,
                        snippet=rel,
                    ))
                    if len(results) >= max_results:
                        break
                    continue

                path = Path(abspath)
                try:
                    if not info.get('is_text', False):
                        continue
                    if path.stat().st_size > MAX_PREVIEW_FILE_SIZE:
                        continue
                    text = read_text_safe(path)
                except Exception:
                    continue

                first_line = 0
                first_snippet = ''
                total_hits = 0
                for line_no, line in enumerate(text.splitlines(), start=1):
                    if compiled is None:
                        continue
                    line_hits = compiled.findall(line)
                    if line_hits:
                        hits_count = len(line_hits) if isinstance(line_hits, list) else 1
                        total_hits += hits_count
                        if first_line == 0:
                            first_line = line_no
                            first_snippet = line.strip()

                if total_hits:
                    results.append(SearchResult(
                        relpath=rel,
                        abspath=abspath,
                        display_path=display_path,
                        modified=modified,
                        modified_ts=modified_ts,
                        size=size,
                        ext=ext or '(sin extensión)',
                        line=first_line,
                        matches=total_hits,
                        snippet=first_snippet,
                    ))
                    if len(results) >= max_results:
                        break

            if sort_mode == 'path':
                results.sort(key=lambda r: (r.display_path.lower(), r.line, r.relpath.lower()))
            elif sort_mode == 'modified':
                results.sort(key=lambda r: (-r.modified_ts, r.display_path.lower()))
            elif sort_mode == 'size':
                results.sort(key=lambda r: (-r.size, r.display_path.lower()))
            elif sort_mode == 'ext':
                results.sort(key=lambda r: (r.ext.lower(), r.display_path.lower()))

            self.queue.put(('search_done', results))

        except Exception as e:
            self.queue.put(('error', f'Error en búsqueda: {e}'))

    def on_search_ready(self) -> None:
        self.results_tree.delete(*self.results_tree.get_children())

        for i, r in enumerate(self.search_results):
            self.results_tree.insert(
                '',
                'end',
                iid=f'res_{i}',
                values=(r.display_path, r.modified, human_size(r.size), r.ext),
            )

        if self.search_results:
            self.status_var.set(f'{len(self.search_results)} resultados')
            self.log(f'Búsqueda terminada: {len(self.search_results)} resultados')
            self.save_settings()
        else:
            self.status_var.set('Sin resultados')
            self.log('Búsqueda sin resultados')

        self.search_combo['values'] = self.settings.get('recent_searches', [])

    def _selected_search_result(self) -> SearchResult | None:
        sel = self.results_tree.selection()
        if not sel:
            return None
        iid = sel[0]
        if not iid.startswith('res_'):
            return None
        try:
            idx = int(iid.split('_', 1)[1])
            return self.search_results[idx]
        except Exception:
            return None

    def _is_probably_binary(self, path: Path) -> bool:
        try:
            with path.open('rb') as f:
                chunk = f.read(8192)
            return b'\x00' in chunk
        except Exception:
            return False

    def _build_file_fact_sheet(self, relpath: str, path: Path, size: int, reason: str) -> str:
        ext = path.suffix.lower() or '(sin extensión)'
        return '\n'.join([
            '[Preview no cargado]',
            f'Relpath: {relpath}',
            f'Ruta: {path}',
            f'Extensión: {ext}',
            f'Tamaño: {human_size(size)}',
            f'Motivo: {reason}',
            '',
            'Usa "Abrir con sistema" si quieres verlo completo.'
        ])

    # -------------------------
    # Preview
    # -------------------------
    def open_preview(self, relpath: str, abspath: str, line: int = 0) -> None:
        path = Path(abspath)
        if not path.exists():
            messagebox.showerror(APP_TITLE, f"El archivo ya no existe:\n{abspath}")
            return

        try:
            size = path.stat().st_size
            ext = path.suffix.lower()

            if self._is_probably_binary(path):
                text = self._build_file_fact_sheet(relpath, path, size, 'archivo binario')
            elif size > MAX_PREVIEW_FILE_SIZE:
                text = self._build_file_fact_sheet(relpath, path, size, 'archivo demasiado grande para preview completo')
            elif ext and ext not in self._preview_text_exts and size > 250_000:
                text = self._build_file_fact_sheet(relpath, path, size, 'tipo no textual grande')
            else:
                raw_text = read_text_safe(path)
                if len(raw_text) > 300_000:
                    raw_text = raw_text[:300_000] + '\n\n[Preview truncado: archivo muy grande]'
                lines = raw_text.splitlines()
                if len(lines) > 2000:
                    raw_text = '\n'.join(lines[:2000]) + '\n\n[Preview truncado: demasiadas líneas]'
                text = raw_text

            self.current_preview_path = abspath
            self.current_preview_rel = relpath
            self.preview_title_var.set(f"{relpath}   ({human_size(size)})")

            rendered = self._render_with_line_numbers(text)

            self.preview_text.config(state="normal")
            self.preview_text.delete("1.0", "end")
            self.preview_text.insert("1.0", rendered)
            self.preview_text.tag_remove("active_line", "1.0", "end")
            self.preview_text.tag_remove("match", "1.0", "end")

            if line > 0:
                self.preview_text.tag_add("active_line", f"{line}.0", f"{line}.end")
                self.preview_text.see(f"{max(1, line - 3)}.0")
            else:
                self.preview_text.see("1.0")

            query = self.search_var.get().strip()
            if query and not self.names_only_var.get() and len(text) < 350_000:
                self._highlight_matches_in_preview(query)

            self.preview_text.config(state="disabled")

            self.populate_imports_for_current()
            self.populate_dependents_for_current()
            self.select_tree_node_by_relpath(relpath)

        except Exception as e:
            messagebox.showerror(APP_TITLE, f"No se pudo abrir preview:\n{e}")

    def _render_with_line_numbers(self, text: str) -> str:
        lines = text.splitlines()
        if not lines:
            return "    1 | \n"
        width = max(4, len(str(len(lines))))
        return "\n".join(f"{str(i).rjust(width)} | {line}" for i, line in enumerate(lines, start=1)) + "\n"

    def _highlight_matches_in_preview(self, query: str) -> None:
        if self.regex_var.get():
            # Para no complicar mapping exacto con line numbers + regex compleja, resaltamos con búsqueda textual simple si se puede.
            try:
                pattern = re.compile(query, 0 if self.case_var.get() else re.IGNORECASE)
            except re.error:
                return
            content = self.preview_text.get("1.0", "end-1c")
            for match in pattern.finditer(content):
                start = f"1.0+{match.start()}c"
                end = f"1.0+{match.end()}c"
                self.preview_text.tag_add("match", start, end)
            return

        needle = query if self.case_var.get() else query.lower()
        content = self.preview_text.get("1.0", "end-1c")
        haystack = content if self.case_var.get() else content.lower()

        start_idx = 0
        while True:
            pos = haystack.find(needle, start_idx)
            if pos == -1:
                break
            end_pos = pos + len(needle)
            self.preview_text.tag_add("match", f"1.0+{pos}c", f"1.0+{end_pos}c")
            start_idx = end_pos

    # -------------------------
    # Imports / dependents
    # -------------------------
    def populate_imports_for_current(self) -> None:
        self.imports_tree.delete(*self.imports_tree.get_children())

        if not self.current_preview_rel:
            return

        info = self.index_data["files"].get(self.current_preview_rel)
        if not info:
            return

        repo_root = Path(self.index_data["root"])
        src = Path(info["abspath"])

        for i, raw_imp in enumerate(info.get("imports", [])):
            resolved = resolve_import(repo_root, src, raw_imp) or ""
            self.imports_tree.insert("", "end", iid=f"imp_{i}", values=(raw_imp, resolved))

    def populate_dependents_for_current(self) -> None:
        self.dependents_tree.delete(*self.dependents_tree.get_children())

        if not self.current_preview_rel:
            return

        items = self.index_data.get("dependents", {}).get(self.current_preview_rel, [])
        for i, rel in enumerate(items):
            self.dependents_tree.insert("", "end", iid=f"dep_{i}", values=(rel,))

    # -------------------------
    # Stats rendering
    # -------------------------
    def render_stats(self) -> None:
        data = self.index_data
        if not data.get("files"):
            return

        lines = []
        stats = data.get("stats", {})
        lines.append(f"Repo: {data['root']}")
        lines.append(f"Archivos indexados: {len(data['files'])}")
        lines.append(f"Tiempo de indexado: {stats.get('elapsed_sec', 0)} s")
        lines.append("")

        lines.append("Extensiones:")
        for ext, count in data.get("ext_counts", {}).items():
            lines.append(f"  {ext:<8} {count}")

        lines.append("")
        lines.append("Top-level folders:")
        for folder, count in data.get("top_level_counts", {}).items():
            lines.append(f"  {folder:<24} {count}")

        lines.append("")
        lines.append("Archivos más grandes:")
        for item in stats.get("largest_files", []):
            lines.append(f"  {human_size(item['size']).rjust(8)}   {item['relpath']}")

        self.stats_text.config(state="normal")
        self.stats_text.delete("1.0", "end")
        self.stats_text.insert("1.0", "\n".join(lines))
        self.stats_text.config(state="disabled")

    # -------------------------
    # Bookmarks
    # -------------------------
    def get_repo_bookmarks(self) -> list[str]:
        repo = self.repo_var.get().strip()
        all_bm = self.settings.setdefault("bookmarks", {})
        return list(all_bm.get(repo, []))

    def save_repo_bookmarks(self, bookmarks: list[str]) -> None:
        repo = self.repo_var.get().strip()
        self.settings.setdefault("bookmarks", {})
        self.settings["bookmarks"][repo] = sorted(set(bookmarks))
        self.save_settings()

    def refresh_bookmarks_view(self) -> None:
        self.bookmarks_list.delete(0, "end")
        for rel in self.get_repo_bookmarks():
            self.bookmarks_list.insert("end", rel)

    def add_current_preview_bookmark(self) -> None:
        if not self.current_preview_rel:
            return
        bookmarks = self.get_repo_bookmarks()
        bookmarks.append(self.current_preview_rel)
        self.save_repo_bookmarks(bookmarks)
        self.refresh_bookmarks_view()
        self.log(f"Bookmark agregado: {self.current_preview_rel}")

    def open_selected_bookmark(self) -> None:
        sel = self.bookmarks_list.curselection()
        if not sel:
            return
        rel = self.bookmarks_list.get(sel[0])
        info = self.index_data["files"].get(rel)
        if info:
            self.open_preview(rel, info["abspath"])

    def remove_selected_bookmark(self) -> None:
        sel = self.bookmarks_list.curselection()
        if not sel:
            return
        rel = self.bookmarks_list.get(sel[0])
        bookmarks = [x for x in self.get_repo_bookmarks() if x != rel]
        self.save_repo_bookmarks(bookmarks)
        self.refresh_bookmarks_view()
        self.log(f"Bookmark removido: {rel}")

    # -------------------------
    # Context menus
    # -------------------------
    def show_tree_menu(self, event: tk.Event) -> None:
        row = self.repo_tree.identify_row(event.y)
        if row:
            self.repo_tree.selection_set(row)
            self.tree_menu.tk_popup(event.x_root, event.y_root)

    def tree_menu_open_preview(self) -> None:
        node = self._get_selected_tree_node()
        if not node:
            return
        if node in self.node_to_abspath:
            rel = self.node_to_relpath.get(node, "")
            abspath = self.node_to_abspath[node]
            if Path(abspath).is_file():
                self.open_preview(rel, abspath)

    def tree_menu_open_system(self) -> None:
        node = self._get_selected_tree_node()
        if not node:
            return
        path = self.node_to_abspath.get(node)
        if path:
            self.open_with_system(path)
        else:
            rel = self.node_to_relpath.get(node)
            if rel and self.index_data.get("root"):
                folder = Path(self.index_data["root"]) / rel
                self.open_with_system(str(folder))

    def tree_menu_copy_path(self) -> None:
        node = self._get_selected_tree_node()
        if not node:
            return
        path = self.node_to_abspath.get(node)
        if path:
            self.copy_to_clipboard(path)
        else:
            rel = self.node_to_relpath.get(node, "")
            if rel:
                self.copy_to_clipboard(rel)

    def tree_menu_add_bookmark(self) -> None:
        node = self._get_selected_tree_node()
        if not node:
            return
        rel = self.node_to_relpath.get(node)
        if rel and rel in self.index_data["files"]:
            bookmarks = self.get_repo_bookmarks()
            bookmarks.append(rel)
            self.save_repo_bookmarks(bookmarks)
            self.refresh_bookmarks_view()

    def tree_menu_filter_folder(self) -> None:
        node = self._get_selected_tree_node()
        if not node:
            return
        rel = self.node_to_relpath.get(node)
        if rel:
            if rel in self.index_data["files"]:
                folder = "/".join(rel.split("/")[:-1]) or "(root)"
                self.set_folder_filter(folder if folder != "(root)" else "(todo)")
            else:
                self.set_folder_filter(rel)

    def show_results_menu(self, event: tk.Event) -> None:
        row = self.results_tree.identify_row(event.y)
        if row:
            self.results_tree.selection_set(row)
            self.results_menu.tk_popup(event.x_root, event.y_root)

    def show_imports_menu(self, event: tk.Event) -> None:
        row = self.imports_tree.identify_row(event.y)
        if row:
            self.imports_tree.selection_set(row)
            self.imports_menu.tk_popup(event.x_root, event.y_root)

    # -------------------------
    # Event handlers
    # -------------------------
    def _get_selected_tree_node(self) -> str | None:
        sel = self.repo_tree.selection()
        return sel[0] if sel else None

    def on_tree_select(self, event: tk.Event | None = None) -> None:
        if self._suspend_tree_selection:
            return
        node = self._get_selected_tree_node()
        if not node:
            return
        abspath = self.node_to_abspath.get(node)
        rel = self.node_to_relpath.get(node)
        if not abspath or not rel or not Path(abspath).is_file():
            return

        if self._tree_select_after_id is not None:
            try:
                self.root.after_cancel(self._tree_select_after_id)
            except Exception:
                pass
            self._tree_select_after_id = None

        self._tree_select_after_id = self.root.after(25, lambda r=rel, a=abspath: self.open_preview(r, a))

    def on_tree_double_click(self, event: tk.Event | None = None) -> None:
        node = self._get_selected_tree_node()
        if not node:
            return
        abspath = self.node_to_abspath.get(node)
        if abspath and Path(abspath).is_file():
            self.open_with_system(abspath)

    def on_result_double_click(self, event: tk.Event | None = None) -> None:
        self.open_selected_result()

    def on_imports_double_click(self, event: tk.Event | None = None) -> None:
        self.open_selected_import_target()

    def on_dependents_double_click(self, event: tk.Event | None = None) -> None:
        sel = self.dependents_tree.selection()
        if not sel:
            return
        rel = self.dependents_tree.item(sel[0], "values")[0]
        info = self.index_data["files"].get(rel)
        if info:
            self.open_preview(rel, info["abspath"])

    # -------------------------
    # Selection helpers
    # -------------------------
    def open_selected_result(self) -> None:
        result = self._selected_search_result()
        if not result:
            return
        self.open_preview(result.relpath, result.abspath, line=result.line)

    def open_selected_result_system(self) -> None:
        result = self._selected_search_result()
        if not result:
            return
        self.open_with_system(result.abspath)

    def copy_selected_result_path(self) -> None:
        result = self._selected_search_result()
        if not result:
            return
        self.copy_to_clipboard(result.abspath)

    def reveal_selected_result_in_tree(self) -> None:
        result = self._selected_search_result()
        if not result:
            return
        self.select_tree_node_by_relpath(result.relpath)

    def open_selected_import_target(self) -> None:
        sel = self.imports_tree.selection()
        if not sel:
            return
        raw, resolved = self.imports_tree.item(sel[0], "values")
        if resolved:
            info = self.index_data["files"].get(resolved)
            if info:
                self.open_preview(resolved, info["abspath"])
        else:
            messagebox.showinfo(APP_TITLE, f"No se pudo resolver este import:\n{raw}")

    def copy_selected_import_raw(self) -> None:
        sel = self.imports_tree.selection()
        if not sel:
            return
        raw, _resolved = self.imports_tree.item(sel[0], "values")
        self.copy_to_clipboard(raw)

    def open_current_preview_with_system(self) -> None:
        if self.current_preview_path:
            self.open_with_system(self.current_preview_path)

    def copy_current_preview_path(self) -> None:
        if self.current_preview_path:
            self.copy_to_clipboard(self.current_preview_path)

    def select_tree_node_by_relpath(self, relpath: str) -> None:
        current = self._get_selected_tree_node()
        if current and self.node_to_relpath.get(current) == relpath:
            return

        for node, rel in self.node_to_relpath.items():
            if rel == relpath:
                try:
                    self._suspend_tree_selection = True
                    self.repo_tree.selection_set(node)
                    self.repo_tree.focus(node)
                    self.repo_tree.see(node)
                finally:
                    self._suspend_tree_selection = False
                return

    # -------------------------
    # Utility actions
    # -------------------------
    def open_with_system(self, path: str) -> None:
        try:
            system = platform.system().lower()
            if system == "windows":
                os.startfile(path)  # type: ignore[attr-defined]
            elif system == "darwin":
                subprocess.Popen(["open", path])
            else:
                subprocess.Popen(["xdg-open", path])
        except Exception as e:
            messagebox.showerror(APP_TITLE, f"No se pudo abrir con el sistema:\n{e}")

    def copy_to_clipboard(self, text: str) -> None:
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        self.status_var.set("Ruta copiada al portapapeles")

    def export_results(self) -> None:
        if not self.search_results:
            messagebox.showinfo(APP_TITLE, "No hay resultados para exportar.")
            return

        path = filedialog.asksaveasfilename(
            title="Exportar resultados",
            defaultextension=".csv",
            filetypes=[
                ("CSV", "*.csv"),
                ("JSON", "*.json"),
                ("TXT", "*.txt"),
                ("Todos", "*.*"),
            ],
        )
        if not path:
            return

        out = Path(path)
        try:
            if out.suffix.lower() == ".csv":
                with out.open("w", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerow([
                        "display_path",
                        "modified",
                        "size_bytes",
                        "size_human",
                        "ext",
                        "relpath",
                        "abspath",
                        "line",
                        "matches",
                        "snippet",
                    ])
                    for r in self.search_results:
                        writer.writerow([
                            r.display_path,
                            r.modified,
                            r.size,
                            human_size(r.size),
                            r.ext,
                            r.relpath,
                            r.abspath,
                            r.line,
                            r.matches,
                            r.snippet,
                        ])
            elif out.suffix.lower() == ".json":
                payload = [asdict(r) for r in self.search_results]
                out.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
            else:
                lines = []
                for r in self.search_results:
                    lines.append(
                        f"{r.display_path} | {r.modified} | {human_size(r.size)} | {r.ext} | line={r.line} | hits={r.matches}"
                    )
                out.write_text("\n".join(lines), encoding="utf-8")

            self.log(f"Resultados exportados: {out}")
            messagebox.showinfo(APP_TITLE, f"Exportado correctamente:\n{out}")

        except Exception as e:
            messagebox.showerror(APP_TITLE, f"No se pudo exportar:\n{e}")

    # -------------------------
    # Close
    # -------------------------
    def on_close(self) -> None:
        self.save_settings()
        self.root.destroy()
