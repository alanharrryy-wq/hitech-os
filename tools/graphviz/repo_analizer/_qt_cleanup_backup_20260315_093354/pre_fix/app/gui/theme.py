from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText

from app.gui.palette import DEFAULT_THEME, ThemePalette


UI_FONT = ('Segoe UI', 10)
UI_FONT_BOLD = ('Segoe UI', 10, 'bold')
TITLE_FONT = ('Segoe UI', 11, 'bold')
CODE_FONT = ('Consolas', 10)


def apply_theme(root: tk.Misc, palette: ThemePalette = DEFAULT_THEME) -> ttk.Style:
    style = ttk.Style(root)

    try:
        style.theme_use('clam')
    except tk.TclError:
        pass

    try:
        root.configure(bg=palette.bg)
    except tk.TclError:
        pass

    style.configure('.',
        background=palette.bg,
        foreground=palette.text,
        fieldbackground=palette.input_bg,
        bordercolor=palette.border,
        darkcolor=palette.panel_alt,
        lightcolor=palette.panel_alt,
        troughcolor=palette.scrollbar_trough,
        insertcolor=palette.text,
        font=UI_FONT,
    )

    style.configure('TFrame', background=palette.bg)
    style.configure('Card.TFrame', background=palette.panel)
    style.configure('Surface.TFrame', background=palette.panel_alt)
    style.configure('TLabel', background=palette.bg, foreground=palette.text, font=UI_FONT)
    style.configure('Muted.TLabel', background=palette.bg, foreground=palette.text_muted, font=UI_FONT)
    style.configure('Header.TLabel', background=palette.bg, foreground=palette.text, font=TITLE_FONT)

    style.configure('TLabelFrame', background=palette.bg, bordercolor=palette.border, relief='solid', borderwidth=1)
    style.configure('TLabelFrame.Label', background=palette.bg, foreground=palette.text, font=UI_FONT_BOLD)

    style.configure('TPanedwindow', background=palette.bg)
    style.configure('Sash', background=palette.border)

    style.configure('TButton',
        background=palette.panel_alt,
        foreground=palette.text,
        bordercolor=palette.border,
        relief='flat',
        padding=(10, 6),
        focusthickness=1,
        focuscolor=palette.accent,
    )
    style.map('TButton',
        background=[('active', palette.accent), ('pressed', palette.accent_hover), ('disabled', palette.panel)],
        foreground=[('active', '#ffffff'), ('pressed', '#ffffff'), ('disabled', palette.text_muted)],
        bordercolor=[('focus', palette.accent), ('active', palette.accent)],
    )

    style.configure('TCheckbutton', background=palette.bg, foreground=palette.text, font=UI_FONT)
    style.map('TCheckbutton',
        background=[('active', palette.bg)],
        foreground=[('disabled', palette.text_muted)],
    )

    style.configure('TCombobox',
        padding=6,
        arrowsize=16,
        fieldbackground=palette.input_bg,
        background=palette.input_bg,
        foreground=palette.input_fg,
        bordercolor=palette.input_border,
        lightcolor=palette.input_border,
        darkcolor=palette.input_border,
        arrowcolor=palette.text,
        insertcolor=palette.input_fg,
    )
    style.map('TCombobox',
        fieldbackground=[('readonly', palette.input_bg), ('focus', palette.input_bg)],
        background=[('readonly', palette.input_bg), ('active', palette.panel_alt)],
        foreground=[('readonly', palette.input_fg)],
        bordercolor=[('focus', palette.accent), ('readonly', palette.input_border)],
        arrowcolor=[('active', palette.accent_hover), ('readonly', palette.text)],
    )

    style.configure('TSpinbox',
        padding=6,
        arrowsize=14,
        fieldbackground=palette.input_bg,
        background=palette.input_bg,
        foreground=palette.input_fg,
        bordercolor=palette.input_border,
        lightcolor=palette.input_border,
        darkcolor=palette.input_border,
        arrowcolor=palette.text,
    )
    style.map('TSpinbox',
        bordercolor=[('focus', palette.accent)],
        arrowcolor=[('active', palette.accent_hover)],
    )

    style.configure('Horizontal.TScrollbar',
        background=palette.panel_alt,
        troughcolor=palette.scrollbar_trough,
        bordercolor=palette.border,
        arrowcolor=palette.text,
    )
    style.configure('Vertical.TScrollbar',
        background=palette.panel_alt,
        troughcolor=palette.scrollbar_trough,
        bordercolor=palette.border,
        arrowcolor=palette.text,
    )
    style.map('Horizontal.TScrollbar', background=[('active', palette.accent)])
    style.map('Vertical.TScrollbar', background=[('active', palette.accent)])

    style.configure('TNotebook', background=palette.bg, borderwidth=0)
    style.configure('TNotebook.Tab',
        background=palette.panel_alt,
        foreground=palette.text_muted,
        padding=(14, 7),
        font=UI_FONT_BOLD,
    )
    style.map('TNotebook.Tab',
        background=[('selected', palette.panel), ('active', palette.panel_alt)],
        foreground=[('selected', palette.text), ('active', palette.text)],
    )

    _configure_tree_styles(style, palette)
    _configure_progress_style(style, palette)

    return style


def _configure_tree_styles(style: ttk.Style, palette: ThemePalette) -> None:
    common = dict(
        background=palette.panel,
        fieldbackground=palette.panel,
        foreground=palette.text,
        bordercolor=palette.border,
        lightcolor=palette.border,
        darkcolor=palette.border,
        rowheight=28,
        relief='flat',
        font=UI_FONT,
    )

    style.configure('RepoTree.Treeview', **common)
    style.configure('RepoTree.Treeview.Heading',
        background=palette.panel_alt,
        foreground=palette.text,
        bordercolor=palette.border,
        relief='flat',
        font=UI_FONT_BOLD,
        padding=(8, 8),
    )
    style.map('RepoTree.Treeview',
        background=[('selected', palette.selection)],
        foreground=[('selected', '#ffffff')],
    )
    style.map('RepoTree.Treeview.Heading',
        background=[('active', palette.accent_soft)],
        foreground=[('active', palette.text)],
    )

    style.configure('Results.Treeview', **common)
    style.configure('Results.Treeview.Heading',
        background=palette.panel_alt,
        foreground=palette.text,
        bordercolor=palette.border,
        relief='flat',
        font=UI_FONT_BOLD,
        padding=(8, 8),
    )
    style.map('Results.Treeview',
        background=[('selected', palette.selection)],
        foreground=[('selected', '#ffffff')],
    )

    style.configure('Data.Treeview', **common)
    style.configure('Data.Treeview.Heading',
        background=palette.panel_alt,
        foreground=palette.text,
        bordercolor=palette.border,
        relief='flat',
        font=UI_FONT_BOLD,
        padding=(8, 8),
    )
    style.map('Data.Treeview',
        background=[('selected', palette.selection)],
        foreground=[('selected', '#ffffff')],
    )


def _configure_progress_style(style: ttk.Style, palette: ThemePalette) -> None:
    style.configure('Repo.Horizontal.TProgressbar',
        troughcolor=palette.panel_deep,
        background=palette.accent,
        bordercolor=palette.border,
        lightcolor=palette.accent,
        darkcolor=palette.accent,
    )


def apply_widget_theme(
    root: tk.Misc,
    *,
    preview_text: ScrolledText | None = None,
    stats_text: ScrolledText | None = None,
    log_text: ScrolledText | None = None,
    bookmarks_list: tk.Listbox | None = None,
    tree_menu: tk.Menu | None = None,
    results_menu: tk.Menu | None = None,
    imports_menu: tk.Menu | None = None,
    palette: ThemePalette = DEFAULT_THEME,
) -> None:
    text_widgets = [w for w in (preview_text, stats_text, log_text) if w is not None]
    for widget in text_widgets:
        _style_scrolled_text(widget, palette)

    if preview_text is not None:
        try:
            preview_text.tag_configure('active_line', background=palette.code_line_active, foreground='#ffffff')
            preview_text.tag_configure('match', background=palette.code_match_bg, foreground=palette.code_match_fg)
        except tk.TclError:
            pass

    if bookmarks_list is not None:
        try:
            bookmarks_list.configure(
                bg=palette.list_bg,
                fg=palette.list_fg,
                selectbackground=palette.selection,
                selectforeground='#ffffff',
                highlightbackground=palette.border,
                highlightcolor=palette.accent,
                relief='flat',
                bd=1,
                font=UI_FONT,
            )
        except tk.TclError:
            pass

    for menu in (tree_menu, results_menu, imports_menu):
        if menu is not None:
            _style_menu(menu, palette)

    _apply_option_database(root, palette)


def _style_scrolled_text(widget: ScrolledText, palette: ThemePalette) -> None:
    try:
        widget.configure(
            bg=palette.code_bg,
            fg=palette.code_fg,
            insertbackground=palette.code_fg,
            selectbackground=palette.selection,
            selectforeground='#ffffff',
            highlightbackground=palette.border,
            highlightcolor=palette.accent,
            relief='flat',
            bd=1,
            padx=12,
            pady=10,
            font=CODE_FONT,
            undo=False,
        )
    except tk.TclError:
        pass


def _style_menu(menu: tk.Menu, palette: ThemePalette) -> None:
    try:
        menu.configure(
            bg=palette.menu_bg,
            fg=palette.menu_fg,
            activebackground=palette.menu_active_bg,
            activeforeground=palette.menu_active_fg,
            selectcolor=palette.accent,
            relief='flat',
            bd=1,
            tearoff=False,
            font=UI_FONT,
        )
    except tk.TclError:
        pass


def _apply_option_database(root: tk.Misc, palette: ThemePalette) -> None:
    try:
        root.option_add('*TCombobox*Listbox*Background', palette.input_bg)
        root.option_add('*TCombobox*Listbox*Foreground', palette.input_fg)
        root.option_add('*TCombobox*Listbox*selectBackground', palette.selection)
        root.option_add('*TCombobox*Listbox*selectForeground', '#ffffff')
        root.option_add('*Menu.background', palette.menu_bg)
        root.option_add('*Menu.foreground', palette.menu_fg)
        root.option_add('*Menu.activeBackground', palette.menu_active_bg)
        root.option_add('*Menu.activeForeground', palette.menu_active_fg)
    except tk.TclError:
        pass
