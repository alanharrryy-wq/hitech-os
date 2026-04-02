from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

from .config import GlassTemplateConfig, register_template_preset
from .icons import register_icon_pack
from .theme import GlassPalette, register_theme, register_theme_overrides


@dataclass(frozen=True, slots=True)
class GlassCapability:
    name: str
    description: str = ""
    owner: str = "framework"
    tags: tuple[str, ...] = ()
    stable: bool = True


@dataclass(slots=True)
class GlassExtensionRegistry:
    """Plugin-style registration hub for themes, presets, icon packs and capabilities."""

    capabilities: dict[str, GlassCapability] = field(default_factory=dict)
    registered_presets: set[str] = field(default_factory=set)
    registered_themes: set[str] = field(default_factory=set)
    registered_icon_packs: set[str] = field(default_factory=set)

    def register_capability(
        self,
        name: str,
        *,
        description: str = "",
        owner: str = "framework",
        tags: tuple[str, ...] = (),
        stable: bool = True,
        override: bool = False,
    ) -> None:
        normalized = str(name or "").strip().lower()
        if not normalized:
            raise ValueError("capability name is required")
        if not override and normalized in self.capabilities:
            raise ValueError(f"capability '{normalized}' already registered")
        self.capabilities[normalized] = GlassCapability(
            name=normalized,
            description=description,
            owner=owner,
            tags=tuple(tags),
            stable=bool(stable),
        )

    def register_preset(
        self,
        name: str,
        *,
        factory: Callable[[], GlassTemplateConfig] | None = None,
        config: GlassTemplateConfig | None = None,
        base_preset: str | None = None,
        override: bool = False,
    ) -> None:
        register_template_preset(
            name,
            factory=factory,
            config=config,
            base_preset=base_preset,
            override=override,
        )
        self.registered_presets.add(str(name).strip().lower())

    def register_theme_palette(
        self,
        theme_id: str,
        palette: GlassPalette,
        *,
        parent_theme_id: str | None = None,
        description: str = "",
        override: bool = False,
    ) -> None:
        register_theme(
            theme_id,
            palette,
            parent_theme_id=parent_theme_id,
            description=description,
            override=override,
        )
        self.registered_themes.add(str(theme_id).strip().lower())

    def register_theme_override(
        self,
        theme_id: str,
        overrides: dict[str, str],
        *,
        base_theme_id: str,
        description: str = "",
        override: bool = False,
    ) -> None:
        register_theme_overrides(
            theme_id,
            overrides,
            base_theme_id=base_theme_id,
            description=description,
            override=override,
        )
        self.registered_themes.add(str(theme_id).strip().lower())

    def register_icon_pack(
        self,
        name: str,
        root: str | Path,
        *,
        aliases: dict[str, str] | None = None,
        metadata: dict[str, str] | None = None,
        override: bool = True,
    ) -> None:
        register_icon_pack(
            name,
            root,
            aliases=aliases,
            metadata=metadata,
            override=override,
        )
        self.registered_icon_packs.add(str(name).strip().lower())

    def list_capabilities(self) -> tuple[GlassCapability, ...]:
        return tuple(sorted(self.capabilities.values(), key=lambda c: c.name))


_EXTENSIONS = GlassExtensionRegistry()


def register_capability(
    name: str,
    *,
    description: str = "",
    owner: str = "framework",
    tags: tuple[str, ...] = (),
    stable: bool = True,
    override: bool = False,
) -> None:
    _EXTENSIONS.register_capability(
        name,
        description=description,
        owner=owner,
        tags=tags,
        stable=stable,
        override=override,
    )


def register_preset_extension(
    name: str,
    *,
    factory: Callable[[], GlassTemplateConfig] | None = None,
    config: GlassTemplateConfig | None = None,
    base_preset: str | None = None,
    override: bool = False,
) -> None:
    _EXTENSIONS.register_preset(
        name,
        factory=factory,
        config=config,
        base_preset=base_preset,
        override=override,
    )


def register_theme_extension(
    theme_id: str,
    palette: GlassPalette,
    *,
    parent_theme_id: str | None = None,
    description: str = "",
    override: bool = False,
) -> None:
    _EXTENSIONS.register_theme_palette(
        theme_id,
        palette,
        parent_theme_id=parent_theme_id,
        description=description,
        override=override,
    )


def register_theme_override_extension(
    theme_id: str,
    overrides: dict[str, str],
    *,
    base_theme_id: str,
    description: str = "",
    override: bool = False,
) -> None:
    _EXTENSIONS.register_theme_override(
        theme_id,
        overrides,
        base_theme_id=base_theme_id,
        description=description,
        override=override,
    )


def register_icon_pack_extension(
    name: str,
    root: str | Path,
    *,
    aliases: dict[str, str] | None = None,
    metadata: dict[str, str] | None = None,
    override: bool = True,
) -> None:
    _EXTENSIONS.register_icon_pack(name, root, aliases=aliases, metadata=metadata, override=override)


def list_registered_capabilities() -> tuple[GlassCapability, ...]:
    return _EXTENSIONS.list_capabilities()


def extension_registry() -> GlassExtensionRegistry:
    return _EXTENSIONS
