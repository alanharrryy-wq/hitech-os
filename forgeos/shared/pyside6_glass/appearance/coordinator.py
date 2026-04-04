from __future__ import annotations

from dataclasses import replace
from typing import Any

from PySide6.QtCore import QObject, Signal

from ..config import GlassTemplateConfig
from .presets import get_appearance_preset
from .profile import AppearanceBundle, AppearanceProfile, AppearanceSnapshot, EffectsProfile


class AppearanceCoordinator(QObject):
    """State owner for runtime visual preferences.

    The coordinator is deliberately UI-agnostic in round 1. It owns the
    visual state, exposes deterministic update methods, and emits snapshots
    whenever the appearance changes. Template and runtime wiring are handled
    in later rounds so the foundation can land without destabilizing the
    existing behavior.
    """

    profileChanged = Signal(object)
    effectsChanged = Signal(object)
    appearanceChanged = Signal(object)
    presetApplied = Signal(str)

    def __init__(
        self,
        *,
        profile: AppearanceProfile | None = None,
        effects: EffectsProfile | None = None,
        preset_name: str | None = None,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._default_profile = (profile or AppearanceProfile()).normalized()
        self._default_effects = (effects or EffectsProfile.from_appearance(self._default_profile)).normalized()
        self._profile = self._default_profile
        self._effects = self._default_effects
        self._preset_name: str | None = None
        self._last_source = 'manual'
        if preset_name:
            self.apply_preset(preset_name, emit=False)

    @classmethod
    def from_template_config(
        cls,
        config: GlassTemplateConfig,
        *,
        preset_name: str | None = None,
        parent: QObject | None = None,
    ) -> AppearanceCoordinator:
        profile = AppearanceProfile.from_template_config(config)
        effects = EffectsProfile.from_appearance(profile)
        return cls(profile=profile, effects=effects, preset_name=preset_name, parent=parent)

    @property
    def preset_name(self) -> str | None:
        return self._preset_name

    def profile(self) -> AppearanceProfile:
        return self._profile

    def effects(self) -> EffectsProfile:
        return self._effects

    def bundle(self) -> AppearanceBundle:
        return AppearanceBundle(profile=self._profile, effects=self._effects)

    def snapshot(self, *, source: str | None = None) -> AppearanceSnapshot:
        return AppearanceSnapshot(
            profile=self._profile,
            effects=self._effects,
            preset_name=self._preset_name,
            source=str(source or self._last_source or 'manual'),
        )

    def replace(
        self,
        *,
        profile: AppearanceProfile,
        effects: EffectsProfile | None = None,
        preset_name: str | None = None,
        source: str = 'replace',
        emit: bool = True,
    ) -> AppearanceSnapshot:
        self._profile = profile.normalized()
        self._effects = (effects or EffectsProfile.from_appearance(self._profile)).normalized()
        self._preset_name = str(preset_name).strip().lower() if preset_name else None
        self._last_source = source
        snapshot = self.snapshot(source=source)
        if emit:
            self.profileChanged.emit(self._profile)
            self.effectsChanged.emit(self._effects)
            self.appearanceChanged.emit(snapshot)
        return snapshot

    def _sync_effects_from_profile(self, profile: AppearanceProfile) -> EffectsProfile:
        derived = EffectsProfile.from_appearance(profile)
        current = self._effects.normalized()
        return derived.with_updates(
            glow_intensity=current.glow_intensity,
            highlight_strength=current.highlight_strength,
            neon_intensity=current.neon_intensity,
            gaussian_softness=current.gaussian_softness,
            noise_strength=current.noise_strength,
            use_accent_for_glow=current.use_accent_for_glow,
        )

    def update_profile(
        self,
        source: str = 'profile_update',
        *,
        synchronize_effects: bool = True,
        **changes: Any,
    ) -> AppearanceSnapshot:
        self._profile = replace(self._profile, **changes).normalized()
        self._effects = (
            self._sync_effects_from_profile(self._profile)
            if synchronize_effects
            else self._effects.normalized()
        )
        self._preset_name = None
        self._last_source = source
        snapshot = self.snapshot(source=source)
        self.profileChanged.emit(self._profile)
        self.effectsChanged.emit(self._effects)
        self.appearanceChanged.emit(snapshot)
        return snapshot

    def update_effects(self, source: str = 'effects_update', **changes: Any) -> AppearanceSnapshot:
        self._effects = replace(self._effects, **changes).normalized()
        self._preset_name = None
        self._last_source = source
        snapshot = self.snapshot(source=source)
        self.effectsChanged.emit(self._effects)
        self.appearanceChanged.emit(snapshot)
        return snapshot

    def apply_preset(self, name: str, *, emit: bool = True) -> AppearanceSnapshot:
        preset = get_appearance_preset(name)
        snapshot = self.replace(
            profile=preset.profile,
            effects=preset.effects,
            preset_name=preset.name,
            source=f'preset:{preset.name}',
            emit=emit,
        )
        if emit:
            self.presetApplied.emit(preset.name)
        return snapshot

    def reset(self, *, emit: bool = True) -> AppearanceSnapshot:
        return self.replace(
            profile=self._default_profile,
            effects=self._default_effects,
            preset_name=None,
            source='reset',
            emit=emit,
        )

    def as_dict(self) -> dict[str, Any]:
        return self.snapshot().to_dict()


__all__ = ['AppearanceCoordinator']
