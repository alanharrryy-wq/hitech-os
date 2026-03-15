#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class SearchResult:
    relpath: str
    abspath: str
    line: int
    matches: int
    snippet: str


@dataclass
class FileEntry:
    relpath: str
    abspath: str
    ext: str
    size: int
    imports: list[str]
