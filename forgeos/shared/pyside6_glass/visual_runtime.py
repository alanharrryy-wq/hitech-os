from __future__ import annotations

from dataclasses import dataclass

from .appearance import AppearanceCoordinator, VisualIntelligenceContext
from .config import GlassTemplateConfig
from .runtime import GlassVisibilityPolicy, GlassWorkspaceRuntime
from .template import GlassPanelTemplate


@dataclass(frozen=True, slots=True)
class GlassVisualRuntimeBundle:
    template: GlassPanelTemplate
    runtime: GlassWorkspaceRuntime
    appearance: AppearanceCoordinator


def create_visual_runtime(
    template: GlassPanelTemplate,
    *,
    appearance_coordinator: AppearanceCoordinator | None = None,
    appearance_preset: str | None = None,
    framework_defaults: GlassTemplateConfig | None = None,
    preset: str | None = None,
    app_overrides: GlassTemplateConfig | None = None,
    workspace_overrides: GlassTemplateConfig | None = None,
    runtime_overrides: GlassTemplateConfig | None = None,
    explicit_config: GlassTemplateConfig | None = None,
    visibility_policy: GlassVisibilityPolicy | None = None,
    visual_context: VisualIntelligenceContext | None = None,
    visual_level: str | None = None,
    data_state: str | None = None,
    performance_sensitive: bool = False,
    apply_now: bool = True,
) -> GlassVisualRuntimeBundle:
    resolved_visual_context = visual_context
    if resolved_visual_context is None and (visual_level is not None or data_state is not None or performance_sensitive):
        resolved_visual_context = VisualIntelligenceContext(
            requested_visual_level=visual_level or 'standard',
            data_state=data_state or 'ready',
            performance_sensitive=bool(performance_sensitive),
            source='create_visual_runtime',
        )
    runtime = GlassWorkspaceRuntime(
        template,
        framework_defaults=framework_defaults,
        preset=preset,
        app_overrides=app_overrides,
        workspace_overrides=workspace_overrides,
        runtime_overrides=runtime_overrides,
        explicit_config=explicit_config,
        visibility_policy=visibility_policy,
        appearance_coordinator=appearance_coordinator,
        visual_context=resolved_visual_context,
    )
    coordinator = runtime.appearance_coordinator
    if apply_now:
        runtime.apply_resolved_config()
    if appearance_preset:
        coordinator.apply_preset(appearance_preset)
    return GlassVisualRuntimeBundle(template=template, runtime=runtime, appearance=coordinator)


__all__ = [
    'GlassVisualRuntimeBundle',
    'create_visual_runtime',
]
