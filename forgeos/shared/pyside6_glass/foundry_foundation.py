from __future__ import annotations

"""
Foundry Foundation Core for PySide6 Glass.

This module establishes the first heavy layer of the recipe-driven UI platform:
- premium recipe schema
- registry for recipes, variants, beauty/color/motion tokens
- governed page host and surface host primitives
- layout contracts with safe splitter ratios and restore fallbacks
- state-aware surfaces so empty/loading/error/deferred are first-class
- preset and theme registration helpers
- preview builders for gallery/catalog integration

The bias is intentional:
- beautiful by default
- structured instead of improvised
- hard to break through resize/layout drift
- hard to make ugly by accident
- easier to compose than to hand-assemble
"""

from copy import deepcopy
from dataclasses import dataclass, field
import json
from typing import Any, Callable, Iterable, Mapping, Sequence

from PySide6.QtCore import QObject, Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QScrollArea,
    QSizePolicy,
    QSplitter,
    QStackedWidget,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from .assets import CompactToolbar, HeroPanel, SearchCommandBar
from .catalog import GlassCatalogEntry, register_catalog_entry
from .config import (
    GlassAnimationConfig,
    GlassLayoutConfig,
    GlassRegionConfig,
    GlassTabConfig,
    GlassTemplateConfig,
    GlassThemeConfig,
    GlassTypographyConfig,
    GlassVisualScaleConfig,
    get_template_preset,
    register_template_preset,
)
from .diagnostics import config_snapshot, template_runtime_snapshot
from .primitives import DashboardWidgetShell, EmptyStateCard, ErrorStateCard, LoadingStateCard, PanelHeader, QuickActionsStrip, StatCard, MetricValue
from .template import GlassPanelTemplate
from .theme import GlassPalette, GlassThemeManifest, get_palette, list_theme_ids, register_theme

FOUNDATION_SCHEMA_VERSION = "foundry.foundation.v1"
FOUNDATION_CATALOG_CATEGORY = "Foundry Foundation"

BEAUTY_PROFILES: dict[str, dict[str, Any]] = {'premium_focus': {'description': 'Balanced premium operational shell with high hierarchy clarity, measured '
                                  'depth, and restrained ornament.',
                   'density': 'comfortable',
                   'layering': 0.82,
                   'shadow': 0.42,
                   'blur': 0.14,
                   'glow': 0.06,
                   'spacing_scale': 1.0,
                   'corner_roundness': 0.88,
                   'contrast': 'high',
                   'ornament': 'restrained'},
 'cinematic_glass': {'description': 'Lusher glass, deeper surfaces, softer gradients, and slightly more '
                                    'expressive transitions without crossing into dashboard cosplay.',
                     'density': 'comfortable',
                     'layering': 0.91,
                     'shadow': 0.58,
                     'blur': 0.28,
                     'glow': 0.17,
                     'spacing_scale': 1.04,
                     'corner_roundness': 0.92,
                     'contrast': 'high',
                     'ornament': 'selective'},
 'industrial_precision': {'description': 'Sharper, denser and more technical. Great for inspection, control '
                                         'and high-information workstations.',
                          'density': 'compact',
                          'layering': 0.72,
                          'shadow': 0.24,
                          'blur': 0.04,
                          'glow': 0.02,
                          'spacing_scale': 0.94,
                          'corner_roundness': 0.72,
                          'contrast': 'high',
                          'ornament': 'minimal'},
 'executive_signal': {'description': 'Summary-first metrics wall for decision making. Premium, restrained '
                                     'and easy to scan in five seconds.',
                      'density': 'comfortable',
                      'layering': 0.76,
                      'shadow': 0.35,
                      'blur': 0.1,
                      'glow': 0.03,
                      'spacing_scale': 1.03,
                      'corner_roundness': 0.84,
                      'contrast': 'medium_high',
                      'ornament': 'restrained'},
 'editorial_dashboard': {'description': 'Calmer rhythm, airier typography and more whitespace. Useful when '
                                        'information should feel premium but not aggressively technical.',
                         'density': 'comfortable',
                         'layering': 0.68,
                         'shadow': 0.22,
                         'blur': 0.07,
                         'glow': 0.0,
                         'spacing_scale': 1.1,
                         'corner_roundness': 0.86,
                         'contrast': 'medium_high',
                         'ornament': 'minimal'},
 'neon_command': {'description': 'High-energy command room language with luminous accents, disciplined '
                                 'contrast and obvious focus zones.',
                  'density': 'comfortable',
                  'layering': 0.86,
                  'shadow': 0.51,
                  'blur': 0.12,
                  'glow': 0.22,
                  'spacing_scale': 0.99,
                  'corner_roundness': 0.8,
                  'contrast': 'high',
                  'ornament': 'selective'},
 'warm_editorial': {'description': 'Warmer premium tone with softer hierarchy edges. Good for review, '
                                   'storytelling and human-facing internal tools.',
                    'density': 'comfortable',
                    'layering': 0.7,
                    'shadow': 0.18,
                    'blur': 0.05,
                    'glow': 0.01,
                    'spacing_scale': 1.08,
                    'corner_roundness': 0.9,
                    'contrast': 'medium',
                    'ornament': 'low'}}

COLOR_STORIES: dict[str, dict[str, Any]] = {'graphite_cyan': {'description': 'Dark graphite shell with cyan signal accents and icy highlights.',
                   'theme_id': 'foundation_graphite_cyan',
                   'accent': '#53dfff',
                   'accent_secondary': '#8fb8ff',
                   'success': '#78f2b2',
                   'warning': '#ffc66d',
                   'danger': '#ff7d8f'},
 'obsidian_violet': {'description': 'Near-black shell with violet premium accents and subtle blue bounce '
                                    'light.',
                     'theme_id': 'foundation_obsidian_violet',
                     'accent': '#b193ff',
                     'accent_secondary': '#74dcff',
                     'success': '#77e0ab',
                     'warning': '#ffcc73',
                     'danger': '#ff8ca5'},
 'frosted_emerald': {'description': 'Cool slate glass with emerald status accents and low-noise surfaces.',
                     'theme_id': 'foundation_frosted_emerald',
                     'accent': '#61ffba',
                     'accent_secondary': '#8fd3ff',
                     'success': '#6bffbc',
                     'warning': '#ffd17c',
                     'danger': '#ff8a97'},
 'ember_gold': {'description': 'Warm dark shell with amber/gold decision accents, good for leadership or '
                               'high-trust execution tools.',
                'theme_id': 'foundation_ember_gold',
                'accent': '#ffc86d',
                'accent_secondary': '#ff916f',
                'success': '#8ae2a4',
                'warning': '#ffd46b',
                'danger': '#ff8d79'},
 'carbon_ruby': {'description': 'Charcoal shell with ruby urgency accents for alert-oriented interfaces.',
                 'theme_id': 'foundation_carbon_ruby',
                 'accent': '#ff6d95',
                 'accent_secondary': '#ffb46e',
                 'success': '#89e1aa',
                 'warning': '#f3c166',
                 'danger': '#ff5f70'},
 'pearl_azure': {'description': 'Bright editorial light shell with azure accents for premium light-mode '
                                'variants.',
                 'theme_id': 'foundation_pearl_azure',
                 'accent': '#2f78f4',
                 'accent_secondary': '#44c4ff',
                 'success': '#2da86b',
                 'warning': '#b37b09',
                 'danger': '#c74d59'},
 'moonstone_teal': {'description': 'Muted dark teal sophistication with slightly calmer signal accents.',
                    'theme_id': 'foundation_moonstone_teal',
                    'accent': '#66e7de',
                    'accent_secondary': '#82a8ff',
                    'success': '#6fe2b0',
                    'warning': '#f2c76a',
                    'danger': '#ff8a8f'},
 'paper_plum': {'description': 'Soft light paper shell with plum accents and boutique editorial energy.',
                'theme_id': 'foundation_paper_plum',
                'accent': '#8a62f5',
                'accent_secondary': '#3fbad4',
                'success': '#1f9b66',
                'warning': '#b37514',
                'danger': '#b84c63'}}

MOTION_PROFILES: dict[str, dict[str, Any]] = {'none': {'animation_level': 'none',
          'transition_ms': 0,
          'hover_ms': 0,
          'panel_toggle_ms': 0,
          'tab_switch_ms': 0},
 'subtle': {'animation_level': 'subtle',
            'transition_ms': 120,
            'hover_ms': 90,
            'panel_toggle_ms': 110,
            'tab_switch_ms': 120},
 'snappy_deluxe': {'animation_level': 'standard',
                   'transition_ms': 170,
                   'hover_ms': 95,
                   'panel_toggle_ms': 140,
                   'tab_switch_ms': 145},
 'soft_cinematic': {'animation_level': 'standard',
                    'transition_ms': 240,
                    'hover_ms': 130,
                    'panel_toggle_ms': 175,
                    'tab_switch_ms': 190},
 'operator_tight': {'animation_level': 'subtle',
                    'transition_ms': 85,
                    'hover_ms': 60,
                    'panel_toggle_ms': 90,
                    'tab_switch_ms': 95},
 'expressive_glass': {'animation_level': 'standard',
                      'transition_ms': 220,
                      'hover_ms': 120,
                      'panel_toggle_ms': 160,
                      'tab_switch_ms': 180}}

LAYOUT_PACKS: dict[str, dict[str, Any]] = {'balanced_split': {'main_min': 480,
                    'side_min': 300,
                    'hero_height': 120,
                    'status_height': 32,
                    'split_ratio': [68, 32],
                    'notes': 'Balanced default for most workstations.'},
 'operator_dense': {'main_min': 520,
                    'side_min': 260,
                    'hero_height': 104,
                    'status_height': 28,
                    'split_ratio': [72, 28],
                    'notes': 'Dense operator layout for keyboard-first productivity.'},
 'analyst_focus': {'main_min': 560,
                   'side_min': 340,
                   'hero_height': 128,
                   'status_height': 34,
                   'split_ratio': [64, 36],
                   'notes': 'Large inspector and more breathing room for detail work.'},
 'wallboard': {'main_min': 760,
               'side_min': 240,
               'hero_height': 140,
               'status_height': 30,
               'split_ratio': [80, 20],
               'notes': 'Summary-dominant layout for monitoring walls and executive boards.'},
 'inspector_heavy': {'main_min': 420,
                     'side_min': 380,
                     'hero_height': 110,
                     'status_height': 32,
                     'split_ratio': [58, 42],
                     'notes': 'When side detail deserves serious width.'},
 'editorial_dual': {'main_min': 520,
                    'side_min': 320,
                    'hero_height': 136,
                    'status_height': 32,
                    'split_ratio': [62, 38],
                    'notes': 'Airier dual-column rhythm for editorial or review screens.'}}

SHELL_PACKS: dict[str, dict[str, Any]] = {'frameless_glass': {'frameless': True,
                     'translucent': True,
                     'chrome': 'soft_glass',
                     'toolbar': 'integrated',
                     'window_radius': 18},
 'framed_productive': {'frameless': False,
                       'translucent': False,
                       'chrome': 'native',
                       'toolbar': 'elevated',
                       'window_radius': 12},
 'ops_console': {'frameless': True,
                 'translucent': True,
                 'chrome': 'control_room',
                 'toolbar': 'dense',
                 'window_radius': 14},
 'editorial_light': {'frameless': False,
                     'translucent': False,
                     'chrome': 'paper',
                     'toolbar': 'airy',
                     'window_radius': 14}}

SURFACE_VARIANTS: dict[str, dict[str, Any]] = {'glass_metric': {'chrome': 'glass',
                  'padding': 'comfortable',
                  'accent_mode': 'adaptive',
                  'description': 'Metric-led hero surface.'},
 'premium_table': {'chrome': 'muted',
                   'padding': 'compact',
                   'accent_mode': 'edge',
                   'description': 'Dense but polished grid host.'},
 'layered_form': {'chrome': 'card',
                  'padding': 'comfortable',
                  'accent_mode': 'section',
                  'description': 'Sectional inspector and property-sheet style.'},
 'signal_chart': {'chrome': 'card',
                  'padding': 'comfortable',
                  'accent_mode': 'plot',
                  'description': 'Runtime signal chart surface.'},
 'hero_banner': {'chrome': 'glass',
                 'padding': 'comfortable',
                 'accent_mode': 'headline',
                 'description': 'Large summary header.'},
 'activity_stream': {'chrome': 'muted',
                     'padding': 'compact',
                     'accent_mode': 'status',
                     'description': 'Feed/log/timeline style surface.'},
 'segmented_lux': {'chrome': 'minimal',
                   'padding': 'compact',
                   'accent_mode': 'selection',
                   'description': 'Premium tab switcher group.'},
 'command_sheet': {'chrome': 'glass',
                   'padding': 'comfortable',
                   'accent_mode': 'command',
                   'description': 'Launcher/palette style surface.'}}

QUALITY_PROFILES: dict[str, dict[str, Any]] = {'strict': {'no_inline_colors': True,
            'no_unstyled_widgets': True,
            'spacing_scale_enforced': True,
            'icon_family_enforced': True,
            'motion_profile_enforced': True,
            'layout_contract_required': True,
            'states_required': True},
 'balanced': {'no_inline_colors': True,
              'no_unstyled_widgets': True,
              'spacing_scale_enforced': True,
              'icon_family_enforced': False,
              'motion_profile_enforced': True,
              'layout_contract_required': True,
              'states_required': True}}

SURFACE_TYPES: tuple[str, ...] = ('hero_banner',
 'metric_strip',
 'data_grid',
 'chart',
 'inspector_panel',
 'activity_feed',
 'control_stack',
 'diagnostics',
 'state_gallery',
 'text_block',
 'tab_group',
 'command_palette',
 'property_sheet',
 'entity_summary',
 'timeline',
 'toolbar_strip',
 'badge_grid',
 'gallery',
 'form_stack',
 'split_workspace')
REGION_IDS: tuple[str, ...] = ('hero', 'main', 'side', 'status', 'overlay')
SURFACE_STATES: tuple[str, ...] = ('ready', 'loading', 'empty', 'error', 'deferred', 'disabled')
OVERLAY_ROLES: tuple[str, ...] = ('palette', 'dialog', 'toast', 'sheet', 'context', 'notice')
QUALITY_CHECKS: tuple[str, ...] = ('theme_switch_test',
 'compact_mode_test',
 'empty_state_test',
 'error_state_test',
 'layout_restore_test',
 'screenshot_baselines')

RECIPE_SCHEMA: dict[str, Any] = {'schema_version': 'foundry.foundation.v1',
 'title': 'Foundry Premium Recipe Schema',
 'type': 'object',
 'required': ['meta', 'experience', 'surfaces'],
 'additionalProperties': False,
 'properties': {'meta': {'type': 'object',
                         'description': 'Identity and catalog metadata for the recipe.',
                         'required': ['id', 'title'],
                         'properties': {'id': {'type': 'string', 'description': 'Stable recipe id.'},
                                        'title': {'type': 'string',
                                                  'description': 'Human title shown in catalog, previews and '
                                                                 'docs.'},
                                        'subtitle': {'type': 'string',
                                                     'description': 'Secondary title text.'},
                                        'description': {'type': 'string',
                                                        'description': 'Long-form description of purpose and '
                                                                       'visual stance.'},
                                        'category': {'type': 'string', 'description': 'Catalog grouping.'},
                                        'status': {'type': 'string',
                                                   'description': 'Draft, experimental, stable or '
                                                                  'deprecated.'},
                                        'tags': {'type': 'array', 'items': {'type': 'string'}},
                                        'best_for': {'type': 'string'},
                                        'use_when': {'type': 'string'},
                                        'sort_order': {'type': 'integer'},
                                        'icon_name': {'type': 'string'},
                                        'mood': {'type': 'string',
                                                 'description': 'Cinematic, premium, industrial, calm, etc.'},
                                        'audience': {'type': 'string',
                                                     'description': 'Operator, analyst, reviewer, exec, '
                                                                    'general.'}}},
                'experience': {'type': 'object',
                               'description': 'Beauty and interaction language. This is what turns recipes '
                                              'into premium experiences instead of generic widget dumps.',
                               'required': ['beauty_profile', 'color_story', 'motion_profile'],
                               'properties': {'beauty_profile': {'type': 'string',
                                                                 'enum': ['cinematic_glass',
                                                                          'editorial_dashboard',
                                                                          'executive_signal',
                                                                          'industrial_precision',
                                                                          'neon_command',
                                                                          'premium_focus',
                                                                          'warm_editorial']},
                                              'color_story': {'type': 'string',
                                                              'enum': ['carbon_ruby',
                                                                       'ember_gold',
                                                                       'frosted_emerald',
                                                                       'graphite_cyan',
                                                                       'moonstone_teal',
                                                                       'obsidian_violet',
                                                                       'paper_plum',
                                                                       'pearl_azure']},
                                              'motion_profile': {'type': 'string',
                                                                 'enum': ['expressive_glass',
                                                                          'none',
                                                                          'operator_tight',
                                                                          'snappy_deluxe',
                                                                          'soft_cinematic',
                                                                          'subtle']},
                                              'layout_pack': {'type': 'string',
                                                              'enum': ['analyst_focus',
                                                                       'balanced_split',
                                                                       'editorial_dual',
                                                                       'inspector_heavy',
                                                                       'operator_dense',
                                                                       'wallboard']},
                                              'shell_pack': {'type': 'string',
                                                             'enum': ['editorial_light',
                                                                      'framed_productive',
                                                                      'frameless_glass',
                                                                      'ops_console']},
                                              'density': {'type': 'string',
                                                          'enum': ['compact', 'comfortable', 'spacious']},
                                              'visual_language': {'type': 'string',
                                                                  'description': 'Neo control room, '
                                                                                 'editorial premium, '
                                                                                 'industrial operator, etc.'},
                                              'ornament': {'type': 'string',
                                                           'description': 'Restrained, selective, minimal, '
                                                                          'off.'},
                                              'contrast': {'type': 'string',
                                                           'description': 'Low, medium, medium_high, high.'},
                                              'notes': {'type': 'string'}}},
                'shell': {'type': 'object',
                          'description': 'Window chrome and global shell behavior.',
                          'properties': {'frameless': {'type': 'boolean'},
                                         'translucent': {'type': 'boolean'},
                                         'show_status_bar': {'type': 'boolean'},
                                         'show_footer': {'type': 'boolean'},
                                         'show_side': {'type': 'boolean'},
                                         'window_radius': {'type': 'integer'},
                                         'chrome_mode': {'type': 'string'},
                                         'navigation_model': {'type': 'string'},
                                         'header_style': {'type': 'string'},
                                         'search_mode': {'type': 'string'}}},
                'regions': {'type': 'object',
                            'description': 'Optional per-region overrides and constraints.',
                            'properties': {'hero': {'type': 'object',
                                                    'properties': {'visible': {'type': 'boolean'},
                                                                   'role': {'type': 'string'},
                                                                   'width': {'type': 'integer'},
                                                                   'height': {'type': 'integer'},
                                                                   'deferred': {'type': 'boolean'},
                                                                   'notes': {'type': 'string'}}},
                                           'main': {'type': 'object',
                                                    'properties': {'visible': {'type': 'boolean'},
                                                                   'role': {'type': 'string'},
                                                                   'width': {'type': 'integer'},
                                                                   'height': {'type': 'integer'},
                                                                   'deferred': {'type': 'boolean'},
                                                                   'notes': {'type': 'string'}}},
                                           'side': {'type': 'object',
                                                    'properties': {'visible': {'type': 'boolean'},
                                                                   'role': {'type': 'string'},
                                                                   'width': {'type': 'integer'},
                                                                   'height': {'type': 'integer'},
                                                                   'deferred': {'type': 'boolean'},
                                                                   'notes': {'type': 'string'}}},
                                           'status': {'type': 'object',
                                                      'properties': {'visible': {'type': 'boolean'},
                                                                     'role': {'type': 'string'},
                                                                     'width': {'type': 'integer'},
                                                                     'height': {'type': 'integer'},
                                                                     'deferred': {'type': 'boolean'},
                                                                     'notes': {'type': 'string'}}},
                                           'overlay': {'type': 'object',
                                                       'properties': {'visible': {'type': 'boolean'},
                                                                      'role': {'type': 'string'},
                                                                      'width': {'type': 'integer'},
                                                                      'height': {'type': 'integer'},
                                                                      'deferred': {'type': 'boolean'},
                                                                      'notes': {'type': 'string'}}}}},
                'surfaces': {'type': 'array',
                             'description': 'Composable surfaces that inhabit the shell. This is the most '
                                            'important section after experience.',
                             'items': {'type': 'object',
                                       'required': ['id', 'type', 'region', 'title'],
                                       'properties': {'id': {'type': 'string'},
                                                      'type': {'type': 'string',
                                                               'enum': ['hero_banner',
                                                                        'metric_strip',
                                                                        'data_grid',
                                                                        'chart',
                                                                        'inspector_panel',
                                                                        'activity_feed',
                                                                        'control_stack',
                                                                        'diagnostics',
                                                                        'state_gallery',
                                                                        'text_block',
                                                                        'tab_group',
                                                                        'command_palette',
                                                                        'property_sheet',
                                                                        'entity_summary',
                                                                        'timeline',
                                                                        'toolbar_strip',
                                                                        'badge_grid',
                                                                        'gallery',
                                                                        'form_stack',
                                                                        'split_workspace']},
                                                      'region': {'type': 'string',
                                                                 'enum': ['hero',
                                                                          'main',
                                                                          'side',
                                                                          'status',
                                                                          'overlay']},
                                                      'title': {'type': 'string'},
                                                      'subtitle': {'type': 'string'},
                                                      'variant': {'type': 'string',
                                                                  'enum': ['activity_stream',
                                                                           'command_sheet',
                                                                           'glass_metric',
                                                                           'hero_banner',
                                                                           'layered_form',
                                                                           'premium_table',
                                                                           'segmented_lux',
                                                                           'signal_chart']},
                                                      'priority': {'type': 'integer'},
                                                      'lazy': {'type': 'boolean'},
                                                      'deferred': {'type': 'boolean'},
                                                      'min_width': {'type': 'integer'},
                                                      'min_height': {'type': 'integer'},
                                                      'stretch': {'type': 'integer'},
                                                      'allow_collapse': {'type': 'boolean'},
                                                      'preferred_ratio': {'type': 'number'},
                                                      'role': {'type': 'string'},
                                                      'states': {'type': 'object',
                                                                 'properties': {'ready': {'type': 'string'},
                                                                                'loading': {'type': 'string'},
                                                                                'empty': {'type': 'string'},
                                                                                'error': {'type': 'string'},
                                                                                'deferred': {'type': 'string'},
                                                                                'disabled': {'type': 'string'}}},
                                                      'tabs': {'type': 'array',
                                                               'items': {'type': 'object',
                                                                         'required': ['id', 'title'],
                                                                         'properties': {'id': {'type': 'string'},
                                                                                        'title': {'type': 'string'},
                                                                                        'content': {'type': 'string'},
                                                                                        'lazy': {'type': 'boolean'},
                                                                                        'status': {'type': 'string'}}}},
                                                      'items': {'type': 'array', 'items': {'type': 'string'}},
                                                      'metadata': {'type': 'object'}}}},
                'behavior': {'type': 'object',
                             'description': 'Navigation, layout persistence, visibility policies and runtime '
                                            'ergonomics.',
                             'properties': {'layouts': {'type': 'object',
                                                        'properties': {'default': {'type': 'string'},
                                                                       'presets': {'type': 'array',
                                                                                   'items': {'type': 'string'}},
                                                                       'persistent': {'type': 'boolean'}}},
                                            'visibility': {'type': 'object',
                                                           'properties': {'by_role': {'type': 'boolean'},
                                                                          'by_mode': {'type': 'boolean'},
                                                                          'by_flags': {'type': 'boolean'}}},
                                            'performance': {'type': 'object',
                                                            'properties': {'lazy_tabs': {'type': 'boolean'},
                                                                           'deferred_panels': {'type': 'boolean'},
                                                                           'chart_throttle_ms': {'type': 'integer'}}},
                                            'shortcuts': {'type': 'array', 'items': {'type': 'string'}},
                                            'command_palette': {'type': 'boolean'}}},
                'data': {'type': 'object',
                         'description': 'Data source hints and explicit UI-state treatments so '
                                        'loading/error/empty are part of design, not afterthoughts.',
                         'properties': {'sources': {'type': 'array',
                                                    'items': {'type': 'object',
                                                              'properties': {'id': {'type': 'string'},
                                                                             'kind': {'type': 'string'},
                                                                             'notes': {'type': 'string'}}}},
                                        'ui_states': {'type': 'object',
                                                      'properties': {'loading': {'type': 'object',
                                                                                 'properties': {'treatment': {'type': 'string'},
                                                                                                'blocking': {'type': 'boolean'}}},
                                                                     'empty': {'type': 'object',
                                                                               'properties': {'treatment': {'type': 'string'},
                                                                                              'tone': {'type': 'string'}}},
                                                                     'error': {'type': 'object',
                                                                               'properties': {'treatment': {'type': 'string'},
                                                                                              'recover_actions': {'type': 'array',
                                                                                                                  'items': {'type': 'string'}}}},
                                                                     'stale': {'type': 'object',
                                                                               'properties': {'treatment': {'type': 'string'}}}}}}},
                'quality': {'type': 'object',
                            'description': 'Rules the doctor and validators can enforce.',
                            'properties': {'profile': {'type': 'string', 'enum': ['balanced', 'strict']},
                                           'beauty_checks': {'type': 'object',
                                                             'properties': {'no_inline_colors': {'type': 'boolean'},
                                                                            'no_unstyled_widgets': {'type': 'boolean'},
                                                                            'spacing_scale_enforced': {'type': 'boolean'},
                                                                            'icon_family_enforced': {'type': 'boolean'},
                                                                            'motion_profile_enforced': {'type': 'boolean'},
                                                                            'layout_contract_required': {'type': 'boolean'},
                                                                            'states_required': {'type': 'boolean'}}},
                                           'render_checks': {'type': 'object',
                                                             'properties': {'theme_switch_test': {'type': 'boolean'},
                                                                            'compact_mode_test': {'type': 'boolean'},
                                                                            'empty_state_test': {'type': 'boolean'},
                                                                            'error_state_test': {'type': 'boolean'},
                                                                            'layout_restore_test': {'type': 'boolean'},
                                                                            'screenshot_baselines': {'type': 'boolean'}}},
                                           'notes': {'type': 'string'}}},
                'variants': {'type': 'array',
                             'description': 'Named overrides for the same structural recipe.',
                             'items': {'type': 'object',
                                       'required': ['id', 'label'],
                                       'properties': {'id': {'type': 'string'},
                                                      'label': {'type': 'string'},
                                                      'description': {'type': 'string'},
                                                      'overrides': {'type': 'object'}}}}}}


def _slug(value: str, default: str = "item") -> str:
    normalized = "".join(ch.lower() if ch.isalnum() else "_" for ch in str(value or "").strip())
    normalized = "_".join(part for part in normalized.split("_") if part)
    return normalized or default


def _clone(payload: Mapping[str, Any] | Sequence[Any] | Any) -> Any:
    return deepcopy(payload)


def _merge_dict(base: Mapping[str, Any], override: Mapping[str, Any]) -> dict[str, Any]:
    result = dict(base)
    for key, value in (override or {}).items():
        if isinstance(result.get(key), Mapping) and isinstance(value, Mapping):
            result[key] = _merge_dict(result[key], value)
        else:
            result[key] = deepcopy(value)
    return result


def _choice(value: str | None, allowed: Iterable[str], default: str) -> str:
    normalized = str(value or "").strip().lower()
    allowed_set = {str(item).strip().lower() for item in allowed}
    return normalized if normalized in allowed_set else default


def _positive_int(value: Any, default: int, minimum: int = 0) -> int:
    try:
        parsed = int(value)
    except Exception:
        return max(minimum, int(default))
    return max(minimum, parsed)


def _positive_float(value: Any, default: float, minimum: float = 0.0) -> float:
    try:
        parsed = float(value)
    except Exception:
        return max(minimum, float(default))
    return max(minimum, parsed)


def get_foundry_schema() -> dict[str, Any]:
    return deepcopy(RECIPE_SCHEMA)


@dataclass(frozen=True, slots=True)
class LayoutContract:
    min_width: int = 260
    min_height: int = 120
    stretch: int = 1
    allow_collapse: bool = False
    preferred_ratio: float = 0.5

    def normalized(self) -> "LayoutContract":
        return LayoutContract(
            min_width=_positive_int(self.min_width, 260, minimum=120),
            min_height=_positive_int(self.min_height, 120, minimum=64),
            stretch=_positive_int(self.stretch, 1, minimum=0),
            allow_collapse=bool(self.allow_collapse),
            preferred_ratio=min(0.95, max(0.05, _positive_float(self.preferred_ratio, 0.5, minimum=0.05))),
        )


@dataclass(frozen=True, slots=True)
class SurfaceStatePolicy:
    loading: str = "shimmer_soft"
    empty: str = "illustration_message"
    error: str = "inline_panel"
    deferred: str = "deferred_notice"
    disabled: str = "soft_lock"

    @classmethod
    def from_payload(cls, payload: Mapping[str, Any] | None) -> "SurfaceStatePolicy":
        payload = payload or {}
        return cls(
            loading=str(payload.get("loading", "shimmer_soft")),
            empty=str(payload.get("empty", "illustration_message")),
            error=str(payload.get("error", "inline_panel")),
            deferred=str(payload.get("deferred", "deferred_notice")),
            disabled=str(payload.get("disabled", "soft_lock")),
        )


@dataclass(frozen=True, slots=True)
class FoundryTabDefinition:
    tab_id: str
    title: str
    content_id: str
    lazy: bool = False
    status: str = ""

    @classmethod
    def from_payload(cls, payload: Mapping[str, Any]) -> "FoundryTabDefinition":
        return cls(
            tab_id=_slug(str(payload.get("id", "tab"))),
            title=str(payload.get("title", "Tab")),
            content_id=_slug(str(payload.get("content", "content"))),
            lazy=bool(payload.get("lazy", False)),
            status=str(payload.get("status", "")),
        )


@dataclass(frozen=True, slots=True)
class FoundrySurfaceDefinition:
    surface_id: str
    surface_type: str
    region: str
    title: str
    subtitle: str = ""
    variant: str = "glass_metric"
    priority: int = 50
    lazy: bool = False
    deferred: bool = False
    layout: LayoutContract = field(default_factory=LayoutContract)
    states: SurfaceStatePolicy = field(default_factory=SurfaceStatePolicy)
    tabs: tuple[FoundryTabDefinition, ...] = ()
    items: tuple[str, ...] = ()
    role: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_payload(cls, payload: Mapping[str, Any]) -> "FoundrySurfaceDefinition":
        tabs_payload = payload.get("tabs") or []
        return cls(
            surface_id=_slug(str(payload.get("id", "surface"))),
            surface_type=_choice(str(payload.get("type", "text_block")), SURFACE_TYPES, "text_block"),
            region=_choice(str(payload.get("region", "main")), REGION_IDS, "main"),
            title=str(payload.get("title", "Untitled surface")),
            subtitle=str(payload.get("subtitle", "")),
            variant=_choice(str(payload.get("variant", "glass_metric")), SURFACE_VARIANTS.keys(), "glass_metric"),
            priority=_positive_int(payload.get("priority", 50), 50, minimum=0),
            lazy=bool(payload.get("lazy", False)),
            deferred=bool(payload.get("deferred", False)),
            layout=LayoutContract(
                min_width=_positive_int(payload.get("min_width", 260), 260, minimum=120),
                min_height=_positive_int(payload.get("min_height", 120), 120, minimum=64),
                stretch=_positive_int(payload.get("stretch", 1), 1, minimum=0),
                allow_collapse=bool(payload.get("allow_collapse", False)),
                preferred_ratio=_positive_float(payload.get("preferred_ratio", 0.5), 0.5, minimum=0.05),
            ).normalized(),
            states=SurfaceStatePolicy.from_payload(payload.get("states")),
            tabs=tuple(FoundryTabDefinition.from_payload(item) for item in tabs_payload if isinstance(item, Mapping)),
            items=tuple(str(item) for item in (payload.get("items") or [])),
            role=str(payload.get("role", "")),
            metadata=dict(payload.get("metadata") or {}),
        )


@dataclass(frozen=True, slots=True)
class GlassFoundryVariant:
    variant_id: str
    label: str
    description: str = ""
    overrides: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_payload(cls, payload: Mapping[str, Any]) -> "GlassFoundryVariant":
        return cls(
            variant_id=_slug(str(payload.get("id", "variant"))),
            label=str(payload.get("label", "Variant")),
            description=str(payload.get("description", "")),
            overrides=dict(payload.get("overrides") or {}),
        )


@dataclass(frozen=True, slots=True)
class GlassFoundryRecipe:
    recipe_id: str
    title: str
    subtitle: str = ""
    description: str = ""
    category: str = FOUNDATION_CATALOG_CATEGORY
    status: str = "stable"
    tags: tuple[str, ...] = ()
    best_for: str = ""
    use_when: str = ""
    sort_order: int = 1000
    icon_name: str | None = None
    payload: dict[str, Any] = field(default_factory=dict)
    surfaces: tuple[FoundrySurfaceDefinition, ...] = ()
    variants: tuple[GlassFoundryVariant, ...] = ()

    @classmethod
    def from_payload(cls, payload: Mapping[str, Any]) -> "GlassFoundryRecipe":
        normalized = validate_foundry_recipe(payload)
        meta = normalized["meta"]
        surfaces = tuple(FoundrySurfaceDefinition.from_payload(item) for item in normalized["surfaces"])
        variants = tuple(GlassFoundryVariant.from_payload(item) for item in normalized.get("variants", []))
        return cls(
            recipe_id=str(meta["id"]),
            title=str(meta["title"]),
            subtitle=str(meta.get("subtitle", "")),
            description=str(meta.get("description", "")),
            category=str(meta.get("category", FOUNDATION_CATALOG_CATEGORY)),
            status=str(meta.get("status", "stable")),
            tags=tuple(str(item) for item in meta.get("tags", [])),
            best_for=str(meta.get("best_for", "")),
            use_when=str(meta.get("use_when", "")),
            sort_order=_positive_int(meta.get("sort_order", 1000), 1000, minimum=0),
            icon_name=str(meta.get("icon_name")) if meta.get("icon_name") else None,
            payload=normalized,
            surfaces=surfaces,
            variants=variants,
        )


@dataclass(frozen=True, slots=True)
class GlassFoundryRegistrySnapshot:
    recipes: tuple[str, ...]
    themes: tuple[str, ...]
    beauty_profiles: tuple[str, ...]
    color_stories: tuple[str, ...]
    motion_profiles: tuple[str, ...]
    layout_packs: tuple[str, ...]
    shell_packs: tuple[str, ...]
    schema_version: str = FOUNDATION_SCHEMA_VERSION

    def as_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "recipes": list(self.recipes),
            "themes": list(self.themes),
            "beauty_profiles": list(self.beauty_profiles),
            "color_stories": list(self.color_stories),
            "motion_profiles": list(self.motion_profiles),
            "layout_packs": list(self.layout_packs),
            "shell_packs": list(self.shell_packs),
        }


class FoundrySurfaceHost(QFrame):
    """A governed host for content, states and chrome metadata."""

    def __init__(self, surface: FoundrySurfaceDefinition, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.surface = surface
        self.setObjectName(f"FoundrySurfaceHost__{surface.surface_id}")
        self.setProperty("card", "true")
        self.setProperty("surfaceVariant", surface.variant)
        self.setProperty("surfaceType", surface.surface_type)
        self.setMinimumWidth(surface.layout.min_width)
        self.setMinimumHeight(surface.layout.min_height)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        root = QVBoxLayout(self)
        root.setContentsMargins(10, 10, 10, 10)
        root.setSpacing(8)
        self.header = PanelHeader(surface.title, subtitle=surface.subtitle, icon_name=surface.metadata.get("icon_name"), parent=self)
        root.addWidget(self.header)
        self.stack = QStackedWidget(self)
        root.addWidget(self.stack, max(1, surface.layout.stretch))
        self.ready_page = QWidget(self)
        self.ready_layout = QVBoxLayout(self.ready_page)
        self.ready_layout.setContentsMargins(0, 0, 0, 0)
        self.ready_layout.setSpacing(8)
        self.stack.addWidget(self.ready_page)
        self.loading_page = LoadingStateCard(title="Loading", message=f"Preparing {surface.title.lower()}...", parent=self)
        self.stack.addWidget(self.loading_page)
        self.empty_page = EmptyStateCard(surface.title, "Nothing to show yet.", parent=self)
        self.stack.addWidget(self.empty_page)
        self.error_page = ErrorStateCard("Error", f"{surface.title} failed to render.", parent=self)
        self.stack.addWidget(self.error_page)
        self.deferred_page = EmptyStateCard("Deferred", "Content will be created on demand.", parent=self)
        self.stack.addWidget(self.deferred_page)
        self._index_map = {"ready": 0, "loading": 1, "empty": 2, "error": 3, "deferred": 4, "disabled": 4}
        self.set_state("deferred" if surface.deferred else "ready")

    def add_ready_widget(self, widget: QWidget, stretch: int = 0) -> None:
        self.ready_layout.addWidget(widget, stretch)

    def set_state(self, state: str) -> None:
        normalized = str(state or "ready").strip().lower()
        index = self._index_map.get(normalized, 0)
        self.stack.setCurrentIndex(index)
        self.setProperty("surfaceState", normalized)


class FoundryPageHost(QFrame):
    """Page host for safe single-active-page composition."""

    current_page_changed = Signal(str)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._pages: dict[str, QWidget] = {}
        self._order: list[str] = []
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.stack = QStackedWidget(self)
        layout.addWidget(self.stack, 1)
        self.stack.currentChanged.connect(self._emit_current)

    def add_page(self, page_id: str, widget: QWidget) -> None:
        normalized = _slug(page_id, "page")
        if normalized in self._pages:
            return
        self._pages[normalized] = widget
        self._order.append(normalized)
        self.stack.addWidget(widget)
        if self.stack.count() == 1:
            self.set_current_page(normalized)

    def set_current_page(self, page_id: str) -> bool:
        normalized = _slug(page_id, "page")
        widget = self._pages.get(normalized)
        if widget is None:
            return False
        self.stack.setCurrentWidget(widget)
        self.current_page_changed.emit(normalized)
        return True

    def page_ids(self) -> tuple[str, ...]:
        return tuple(self._order)

    def _emit_current(self, index: int) -> None:
        if index < 0 or index >= len(self._order):
            return
        self.current_page_changed.emit(self._order[index])


class FoundryContractSplitter(QSplitter):
    """Splitter with ratio helpers and restore fallback guardrails."""

    def __init__(self, orientation: Qt.Orientation = Qt.Horizontal, parent: QWidget | None = None) -> None:
        super().__init__(orientation, parent)
        self.setChildrenCollapsible(False)
        self.setOpaqueResize(False)

    def apply_ratio(self, left_ratio: int, right_ratio: int) -> None:
        total = max(1, int(left_ratio) + int(right_ratio))
        left = max(1, int((left_ratio / total) * 1000))
        right = max(1, 1000 - left)
        self.setSizes([left, right])

    def restore_or_ratio(self, payload: list[int] | tuple[int, ...] | None, fallback_ratio: tuple[int, int]) -> None:
        if payload and len(payload) >= 2 and sum(int(item) for item in payload[:2]) > 0:
            self.setSizes([max(0, int(payload[0])), max(0, int(payload[1]))])
            return
        self.apply_ratio(fallback_ratio[0], fallback_ratio[1])


class FoundryRuntimeState(QObject):
    """Small state registry for recipe modes without scattering booleans everywhere."""

    state_changed = Signal(str, object)

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._state: dict[str, Any] = {
            "mode": "ready",
            "selection": None,
            "density": "comfortable",
            "theme_id": "",
            "layout": "inspect",
        }

    def get(self, key: str, default: Any = None) -> Any:
        return self._state.get(key, default)

    def set(self, key: str, value: Any) -> None:
        if self._state.get(key) == value:
            return
        self._state[key] = value
        self.state_changed.emit(str(key), value)

    def snapshot(self) -> dict[str, Any]:
        return dict(self._state)


_FOUNDATION_THEMES_REGISTERED = False
_FOUNDATION_PRESETS_REGISTERED = False
_FOUNDATION_RECIPES_REGISTERED = False
_RECIPE_REGISTRY: dict[str, GlassFoundryRecipe] = {}


def list_beauty_profiles() -> tuple[str, ...]:
    return tuple(sorted(BEAUTY_PROFILES.keys()))


def list_color_stories() -> tuple[str, ...]:
    return tuple(sorted(COLOR_STORIES.keys()))


def list_motion_profiles() -> tuple[str, ...]:
    return tuple(sorted(MOTION_PROFILES.keys()))


def list_layout_packs() -> tuple[str, ...]:
    return tuple(sorted(LAYOUT_PACKS.keys()))


def list_shell_packs() -> tuple[str, ...]:
    return tuple(sorted(SHELL_PACKS.keys()))


def list_foundry_recipes() -> tuple[str, ...]:
    return tuple(sorted(_RECIPE_REGISTRY.keys()))


def get_foundry_recipe(recipe_id: str) -> GlassFoundryRecipe:
    register_builtin_foundry_foundation()
    normalized = str(recipe_id or "").strip()
    if normalized not in _RECIPE_REGISTRY:
        raise KeyError(f"Unknown foundry recipe: {recipe_id}")
    return _RECIPE_REGISTRY[normalized]


def foundry_registry_snapshot() -> GlassFoundryRegistrySnapshot:
    register_builtin_foundry_foundation()
    return GlassFoundryRegistrySnapshot(
        recipes=tuple(sorted(_RECIPE_REGISTRY.keys())),
        themes=tuple(sorted(list_theme_ids())),
        beauty_profiles=tuple(sorted(BEAUTY_PROFILES.keys())),
        color_stories=tuple(sorted(COLOR_STORIES.keys())),
        motion_profiles=tuple(sorted(MOTION_PROFILES.keys())),
        layout_packs=tuple(sorted(LAYOUT_PACKS.keys())),
        shell_packs=tuple(sorted(SHELL_PACKS.keys())),
    )


def validate_foundry_recipe(payload: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, Mapping):
        raise TypeError("recipe payload must be a mapping")
    meta = dict(payload.get("meta") or {})
    if not str(meta.get("id", "")).strip():
        raise ValueError("recipe.meta.id is required")
    if not str(meta.get("title", "")).strip():
        raise ValueError("recipe.meta.title is required")
    normalized: dict[str, Any] = {
        "meta": {
            "id": str(meta["id"]).strip(),
            "title": str(meta["title"]).strip(),
            "subtitle": str(meta.get("subtitle", "")),
            "description": str(meta.get("description", "")),
            "category": str(meta.get("category", FOUNDATION_CATALOG_CATEGORY)),
            "status": str(meta.get("status", "stable")),
            "tags": [str(item) for item in meta.get("tags", [])],
            "best_for": str(meta.get("best_for", "")),
            "use_when": str(meta.get("use_when", "")),
            "sort_order": _positive_int(meta.get("sort_order", 1000), 1000, minimum=0),
            "icon_name": str(meta.get("icon_name", "")) or None,
            "mood": str(meta.get("mood", "")),
            "audience": str(meta.get("audience", "")),
        },
        "experience": {
            "beauty_profile": _choice((payload.get("experience") or {}).get("beauty_profile"), BEAUTY_PROFILES.keys(), "premium_focus"),
            "color_story": _choice((payload.get("experience") or {}).get("color_story"), COLOR_STORIES.keys(), "graphite_cyan"),
            "motion_profile": _choice((payload.get("experience") or {}).get("motion_profile"), MOTION_PROFILES.keys(), "subtle"),
            "layout_pack": _choice((payload.get("experience") or {}).get("layout_pack"), LAYOUT_PACKS.keys(), "balanced_split"),
            "shell_pack": _choice((payload.get("experience") or {}).get("shell_pack"), SHELL_PACKS.keys(), "frameless_glass"),
            "density": _choice((payload.get("experience") or {}).get("density"), ("compact", "comfortable", "spacious"), "comfortable"),
            "visual_language": str((payload.get("experience") or {}).get("visual_language", "")),
            "ornament": str((payload.get("experience") or {}).get("ornament", "")),
            "contrast": str((payload.get("experience") or {}).get("contrast", "")),
            "notes": str((payload.get("experience") or {}).get("notes", "")),
        },
        "shell": _merge_dict({
            "frameless": True, "translucent": True, "show_status_bar": True, "show_footer": False, "show_side": True,
            "window_radius": 14, "chrome_mode": "soft_glass", "navigation_model": "left_rail", "header_style": "elevated", "search_mode": "floating_command_bar",
        }, dict(payload.get("shell") or {})),
        "regions": {},
        "surfaces": [],
        "behavior": _merge_dict({
            "layouts": {"default": "inspect", "presets": ["focus", "inspect", "wallboard"], "persistent": True},
            "visibility": {"by_role": True, "by_mode": True, "by_flags": True},
            "performance": {"lazy_tabs": True, "deferred_panels": True, "chart_throttle_ms": 120},
            "shortcuts": [],
            "command_palette": True,
        }, dict(payload.get("behavior") or {})),
        "data": _merge_dict({
            "sources": [],
            "ui_states": {
                "loading": {"treatment": "shimmer_soft", "blocking": False},
                "empty": {"treatment": "illustration_message", "tone": "elegant"},
                "error": {"treatment": "inline_diagnostic", "recover_actions": ["retry", "inspect"]},
                "stale": {"treatment": "subtle_badge"},
            },
        }, dict(payload.get("data") or {})),
        "quality": _merge_dict({
            "profile": "strict",
            "beauty_checks": deepcopy(QUALITY_PROFILES["strict"]),
            "render_checks": {name: True for name in QUALITY_CHECKS},
            "notes": "",
        }, dict(payload.get("quality") or {})),
        "variants": [dict(item) for item in (payload.get("variants") or []) if isinstance(item, Mapping)],
    }
    for region_id in REGION_IDS:
        normalized["regions"][region_id] = _merge_dict({"visible": region_id != "overlay", "role": region_id, "width": 0, "height": 0, "deferred": False, "notes": ""}, dict((payload.get("regions") or {}).get(region_id) or {}))
    surfaces = payload.get("surfaces") or []
    if not isinstance(surfaces, Sequence) or not surfaces:
        raise ValueError("recipe.surfaces must contain at least one surface")
    for item in surfaces:
        if not isinstance(item, Mapping):
            continue
        normalized["surfaces"].append({
            "id": _slug(str(item.get("id", "surface"))),
            "type": _choice(item.get("type"), SURFACE_TYPES, "text_block"),
            "region": _choice(item.get("region"), REGION_IDS, "main"),
            "title": str(item.get("title", "Untitled surface")),
            "subtitle": str(item.get("subtitle", "")),
            "variant": _choice(item.get("variant"), SURFACE_VARIANTS.keys(), "glass_metric"),
            "priority": _positive_int(item.get("priority", 50), 50, minimum=0),
            "lazy": bool(item.get("lazy", False)),
            "deferred": bool(item.get("deferred", False)),
            "min_width": _positive_int(item.get("min_width", 260), 260, minimum=120),
            "min_height": _positive_int(item.get("min_height", 120), 120, minimum=64),
            "stretch": _positive_int(item.get("stretch", 1), 1, minimum=0),
            "allow_collapse": bool(item.get("allow_collapse", False)),
            "preferred_ratio": min(0.95, max(0.05, _positive_float(item.get("preferred_ratio", 0.5), 0.5, minimum=0.05))),
            "role": str(item.get("role", "")),
            "states": _merge_dict({"loading": "shimmer_soft", "empty": "illustration_message", "error": "inline_panel", "deferred": "deferred_notice", "disabled": "soft_lock"}, dict(item.get("states") or {})),
            "tabs": [dict(tab) for tab in (item.get("tabs") or []) if isinstance(tab, Mapping)],
            "items": [str(x) for x in item.get("items", [])],
            "metadata": dict(item.get("metadata") or {}),
        })
    normalized["surfaces"].sort(key=lambda item: (item["region"], int(item.get("priority", 50)), item["id"]))
    return normalized


def register_foundry_recipe(payload: Mapping[str, Any], *, override: bool = False) -> GlassFoundryRecipe:
    recipe = GlassFoundryRecipe.from_payload(payload)
    if not override and recipe.recipe_id in _RECIPE_REGISTRY:
        raise ValueError(f"recipe {recipe.recipe_id!r} already registered")
    _RECIPE_REGISTRY[recipe.recipe_id] = recipe
    return recipe


def _build_palette_for_story(story_id: str) -> GlassPalette:
    base = get_palette("silver_frost_cyan")
    story = COLOR_STORIES[story_id]
    accent = story["accent"]
    accent_secondary = story["accent_secondary"]
    success = story["success"]
    warning = story["warning"]
    danger = story["danger"]
    return base.with_overrides({
        "accent": accent,
        "accent_soft": "rgba(120, 190, 255, 0.25)",
        "text_primary": "#eef5ff" if story_id not in {"pearl_azure", "paper_plum"} else "#132130",
        "text_muted": "#bbccde" if story_id not in {"pearl_azure", "paper_plum"} else "#506176",
        "button_top": accent,
        "button_bottom": accent_secondary,
        "success_top": success,
        "success_bottom": success,
        "warning_top": warning,
        "warning_bottom": warning,
        "danger_top": danger,
        "danger_bottom": danger,
        "progress_chunk_top": accent,
        "progress_chunk_bottom": accent_secondary,
    })


def register_foundry_theme_pack(*, force: bool = False) -> None:
    global _FOUNDATION_THEMES_REGISTERED
    if _FOUNDATION_THEMES_REGISTERED and not force:
        return
    for story_id, story in COLOR_STORIES.items():
        theme_id = str(story["theme_id"])
        palette = _build_palette_for_story(story_id)
        try:
            register_theme(theme_id, palette, description=story["description"], override=True)
        except Exception:
            register_theme(theme_id, palette, description=story["description"], override=True)
    _FOUNDATION_THEMES_REGISTERED = True


def register_foundry_presets(*, force: bool = False) -> None:
    global _FOUNDATION_PRESETS_REGISTERED
    if _FOUNDATION_PRESETS_REGISTERED and not force:
        return
    register_foundry_theme_pack(force=force)
    for story_id, story in COLOR_STORIES.items():
        for beauty_id, beauty in BEAUTY_PROFILES.items():
            preset_name = f"foundation_{story_id}_{beauty_id}"
            layout_pack = next(iter(LAYOUT_PACKS.keys()))
            config = GlassTemplateConfig(
                title=f"{beauty_id.replace("_", " ").title()} Workspace",
                subtitle=story["description"],
                eyebrow="FOUNDATION",
                variant="selector",
                theme=GlassThemeConfig(
                    theme_id=story["theme_id"],
                    density=beauty["density"],
                    experience_mode="default",
                    visual_scale=GlassVisualScaleConfig(
                        spacing_scale=beauty["spacing_scale"],
                        corner_radius_scale=beauty["corner_roundness"],
                        blur_intensity_scale=max(0.2, beauty["blur"] * 4.0),
                        surface_opacity_scale=max(0.8, 1.0 - (beauty["layering"] - 0.5) * 0.15),
                    ),
                    typography=GlassTypographyConfig(scale="md"),
                    animation=GlassAnimationConfig(
                        level=MOTION_PROFILES["subtle"]["animation_level"],
                        transition_ms=MOTION_PROFILES["subtle"]["transition_ms"],
                        hover_ms=MOTION_PROFILES["subtle"]["hover_ms"],
                        panel_toggle_ms=MOTION_PROFILES["subtle"]["panel_toggle_ms"],
                        tab_switch_ms=MOTION_PROFILES["subtle"]["tab_switch_ms"],
                    ),
                ),
                regions=GlassRegionConfig(
                    show_side=True,
                    show_footer=False,
                    show_status=True,
                    min_main_width=LAYOUT_PACKS[layout_pack]["main_min"],
                    min_side_width=LAYOUT_PACKS[layout_pack]["side_min"],
                    main_side_sizes=tuple(LAYOUT_PACKS[layout_pack]["split_ratio"]),
                ),
                tabs=GlassTabConfig(enabled=True, default_tab_id="work", default_tab_title="Work", hide_if_single_visible=False),
                layout=GlassLayoutConfig(
                    active_layout="main_side",
                    allow_runtime_switch=True,
                    allow_user_layout_save=True,
                    named_layouts={
                        "focus": {"main_side": [78, 22]},
                        "inspect": {"main_side": [66, 34]},
                        "wallboard": {"main_side": [82, 18]},
                    },
                ),
            )
            register_template_preset(preset_name, config=config, base_preset="neutral", override=True)
    _FOUNDATION_PRESETS_REGISTERED = True


def register_builtin_foundry_foundation(*, force: bool = False) -> None:
    global _FOUNDATION_RECIPES_REGISTERED
    register_foundry_theme_pack(force=force)
    register_foundry_presets(force=force)
    if _FOUNDATION_RECIPES_REGISTERED and not force:
        return
    for payload in BUILTIN_FOUNDATION_RECIPES:
        register_foundry_recipe(payload, override=True)
    _FOUNDATION_RECIPES_REGISTERED = True


def _sample_metrics(title: str) -> tuple[MetricValue, ...]:
    return (
        MetricValue("Focus", "92%", "stable"),
        MetricValue("Latency", "38ms", "down"),
        MetricValue("Healthy", "99.96%", "up"),
    )


def _make_text_block(lines: Sequence[str], parent: QWidget | None = None) -> QTextEdit:
    editor = QTextEdit(parent)
    editor.setReadOnly(True)
    editor.setPlainText("\n".join(str(line) for line in lines))
    return editor


def _build_surface_body(surface: FoundrySurfaceDefinition, parent: QWidget | None = None) -> QWidget:
    surface_type = surface.surface_type
    if surface_type == "hero_banner":
        hero = HeroPanel(surface.title, subtitle=surface.subtitle, parent=parent)
        for metric in _sample_metrics(surface.title):
            hero.content.addWidget(StatCard(metric=metric, parent=hero))
        return hero
    if surface_type in {"data_grid", "entity_summary", "badge_grid"}:
        shell = DashboardWidgetShell(surface.title, subtitle=surface.subtitle, parent=parent)
        for item in surface.items or ("Name · Healthy · Owner · Updated", "Queue A · Healthy · Ops · now", "Queue B · Pending · Sync · 2m"):
            label = QLabel(str(item), shell)
            label.setProperty("role", "panel_subtitle")
            shell.content.addWidget(label)
        return shell
    if surface_type in {"chart", "metric_strip"}:
        shell = DashboardWidgetShell(surface.title, subtitle=surface.subtitle, parent=parent)
        for metric in _sample_metrics(surface.title):
            shell.content.addWidget(StatCard(metric=metric, parent=shell))
        shell.content.addWidget(_make_text_block(["Chart engine: " + str(surface.metadata.get("engine", "pyqtgraph")), "Kind: " + str(surface.metadata.get("kind", "line")), "Grid: " + str(surface.metadata.get("grid_visibility", "low"))], shell))
        return shell
    if surface_type in {"inspector_panel", "property_sheet", "form_stack"}:
        shell = DashboardWidgetShell(surface.title, subtitle=surface.subtitle, parent=parent)
        header = PanelHeader("Sections", subtitle=", ".join(surface.metadata.get("sections", ["Summary", "Attributes", "Actions"])), parent=shell)
        shell.content.addWidget(header)
        shell.content.addWidget(_make_text_block(["Inspector content remains inside a governed surface host.", "Sticky actions: " + str(surface.metadata.get("sticky_actions", False)), "Deferred: " + str(surface.deferred)], shell))
        return shell
    if surface_type in {"activity_feed", "timeline", "diagnostics"}:
        shell = DashboardWidgetShell(surface.title, subtitle=surface.subtitle, parent=parent)
        shell.content.addWidget(_make_text_block(surface.items or ("Health stable", "Filters updated", "Layout restored", "No anomalies"), shell))
        return shell
    if surface_type == "tab_group":
        tabs = QTabWidget(parent)
        for tab in surface.tabs:
            tab_widget = _make_text_block([
                f"Content id: {tab.content_id}",
                f"Lazy: {tab.lazy}",
                f"Status: {tab.status or '(none)'}",
                "This tab remains inside the recipe system.",
            ], tabs)
            tabs.addTab(tab_widget, tab.title)
        return tabs
    if surface_type in {"command_palette", "toolbar_strip"}:
        toolbar = CompactToolbar(surface.title, parent=parent)
        toolbar.add_action("Refresh", icon_name="refresh-cw")
        toolbar.add_action("Focus", icon_name="target")
        toolbar.add_action("Inspect", icon_name="search")
        return toolbar
    if surface_type == "gallery":
        list_widget = QListWidget(parent)
        for item in surface.items or ("Variant A", "Variant B", "Variant C"):
            QListWidgetItem(str(item), list_widget)
        return list_widget
    return _make_text_block([
        surface.title,
        surface.subtitle,
        "Surface type: " + surface.surface_type,
        "Variant: " + surface.variant,
        "Metadata: " + json.dumps(surface.metadata, indent=2, ensure_ascii=False),
    ], parent)


def build_foundry_foundation(recipe_id: str, *, parent: QWidget | None = None, variant_id: str | None = None) -> GlassPanelTemplate:
    register_builtin_foundry_foundation()
    recipe = get_foundry_recipe(recipe_id)
    payload = deepcopy(recipe.payload)
    if variant_id:
        variant_map = {item.variant_id: item for item in recipe.variants}
        variant = variant_map.get(_slug(variant_id, "variant"))
        if variant is not None:
            payload = _merge_dict(payload, variant.overrides)
            payload = validate_foundry_recipe(payload)
    experience = payload["experience"]
    layout_pack = LAYOUT_PACKS[experience["layout_pack"]]
    color_story = COLOR_STORIES[experience["color_story"]]
    motion = MOTION_PROFILES[experience["motion_profile"]]
    theme_id = color_story["theme_id"]
    preset_name = f"foundation_{experience['color_story']}_{experience['beauty_profile']}"
    template = GlassPanelTemplate(
        parent,
        config=GlassTemplateConfig(
            title=payload["meta"]["title"],
            subtitle=payload["meta"].get("subtitle", ""),
            eyebrow="FOUNDATION",
            variant="selector",
            theme=GlassThemeConfig(
                theme_id=theme_id,
                density=experience["density"],
                visual_scale=GlassVisualScaleConfig(
                    spacing_scale=BEAUTY_PROFILES[experience["beauty_profile"]]["spacing_scale"],
                    corner_radius_scale=BEAUTY_PROFILES[experience["beauty_profile"]]["corner_roundness"],
                    blur_intensity_scale=max(0.2, BEAUTY_PROFILES[experience["beauty_profile"]]["blur"] * 4.0),
                    surface_opacity_scale=max(0.75, 1.0 - BEAUTY_PROFILES[experience["beauty_profile"]]["glow"] * 0.10),
                ),
                typography=GlassTypographyConfig(scale="md"),
                animation=GlassAnimationConfig(
                    level=motion["animation_level"],
                    transition_ms=motion["transition_ms"],
                    hover_ms=motion["hover_ms"],
                    panel_toggle_ms=motion["panel_toggle_ms"],
                    tab_switch_ms=motion["tab_switch_ms"],
                ),
            ),
            regions=GlassRegionConfig(
                show_side=bool(payload["shell"].get("show_side", True)),
                show_footer=bool(payload["shell"].get("show_footer", False)),
                show_status=bool(payload["shell"].get("show_status_bar", True)),
                min_main_width=layout_pack["main_min"],
                min_side_width=layout_pack["side_min"],
                main_side_sizes=tuple(layout_pack["split_ratio"]),
            ),
            tabs=GlassTabConfig(enabled=True, default_tab_id="work", default_tab_title="Work"),
            layout=GlassLayoutConfig(
                active_layout="main_side",
                allow_runtime_switch=True,
                allow_user_layout_save=True,
                named_layouts={
                    "focus": {"main_side": [78, 22]},
                    "inspect": {"main_side": [layout_pack["split_ratio"][0], layout_pack["split_ratio"][1]]},
                    "wallboard": {"main_side": [82, 18]},
                },
            ),
        ),
        title=payload["meta"]["title"],
        subtitle=payload["meta"].get("subtitle", ""),
        eyebrow="FOUNDATION",
        theme_id=theme_id,
    )
    runtime_state = FoundryRuntimeState(template)
    runtime_state.set("theme_id", theme_id)
    runtime_state.set("density", experience["density"])
    runtime_state.set("layout", payload["behavior"]["layouts"].get("default", "inspect"))
    template.set_status_text(f"{payload['meta']['title']} ready · {experience['beauty_profile']} · {experience['color_story']}")
    template.register_layout_preset("focus", {"main_side": [78, 22]})
    template.register_layout_preset("inspect", {"main_side": [layout_pack["split_ratio"][0], layout_pack["split_ratio"][1]]})
    template.register_layout_preset("wallboard", {"main_side": [82, 18]})
    page_host = FoundryPageHost(template)
    main_scroll = QScrollArea(template)
    main_scroll.setWidgetResizable(True)
    main_body = QWidget(main_scroll)
    main_layout = QVBoxLayout(main_body)
    main_layout.setContentsMargins(0, 0, 0, 0)
    main_layout.setSpacing(8)
    main_scroll.setWidget(main_body)
    side_scroll = QScrollArea(template)
    side_scroll.setWidgetResizable(True)
    side_body = QWidget(side_scroll)
    side_layout = QVBoxLayout(side_body)
    side_layout.setContentsMargins(0, 0, 0, 0)
    side_layout.setSpacing(8)
    side_scroll.setWidget(side_body)
    for surface in sorted((FoundrySurfaceDefinition.from_payload(item) for item in payload["surfaces"] if item["region"] == "hero"), key=lambda item: item.priority):
        host = FoundrySurfaceHost(surface, template)
        host.add_ready_widget(_build_surface_body(surface, host), 1)
        host.set_state("ready")
        template.slots.hero_slot.addWidget(host, surface.layout.stretch)
    for surface in sorted((FoundrySurfaceDefinition.from_payload(item) for item in payload["surfaces"] if item["region"] == "main"), key=lambda item: item.priority):
        host = FoundrySurfaceHost(surface, template)
        host.add_ready_widget(_build_surface_body(surface, host), 1)
        host.set_state("deferred" if surface.deferred else "ready")
        main_layout.addWidget(host, surface.layout.stretch)
    for surface in sorted((FoundrySurfaceDefinition.from_payload(item) for item in payload["surfaces"] if item["region"] == "side"), key=lambda item: item.priority):
        host = FoundrySurfaceHost(surface, template)
        host.add_ready_widget(_build_surface_body(surface, host), 1)
        host.set_state("deferred" if surface.deferred else "ready")
        side_layout.addWidget(host, surface.layout.stretch)
    for surface in sorted((FoundrySurfaceDefinition.from_payload(item) for item in payload["surfaces"] if item["region"] == "status"), key=lambda item: item.priority):
        host = FoundrySurfaceHost(surface, template)
        host.add_ready_widget(_build_surface_body(surface, host), 1)
        host.set_state("ready")
        template.slots.status_slot.addWidget(host, surface.layout.stretch)
    page_host.add_page("workspace", main_scroll)
    template.slots.main_slot.addWidget(page_host, 1)
    if payload["shell"].get("show_side", True):
        template.slots.side_slot.addWidget(side_scroll, 1)
    toolbar = QuickActionsStrip(template)
    toolbar.add_action("Focus", icon_name="target", on_click=lambda: template.apply_layout_preset("focus"))
    toolbar.add_action("Inspect", icon_name="search", on_click=lambda: template.apply_layout_preset("inspect"))
    toolbar.add_action("Wallboard", icon_name="monitor", on_click=lambda: template.apply_layout_preset("wallboard"))
    toolbar.add_action("Compact", icon_name="minimize-2", on_click=lambda: template.set_density("compact"))
    toolbar.add_action("Comfortable", icon_name="square", on_click=lambda: template.set_density("comfortable"))
    template.slots.side_slot.insertWidget(0, toolbar)
    search = SearchCommandBar(placeholder="Search recipe surfaces", parent=template)
    template.slots.hero_slot.insertWidget(0, search)
    diagnostics = QTextEdit(template)
    diagnostics.setReadOnly(True)
    diagnostics.setPlainText(json.dumps({"recipe": payload["meta"]["id"], "runtime": runtime_state.snapshot(), "config": config_snapshot(template._config if hasattr(template, "_config") else get_template_preset("neutral")), "template": template_runtime_snapshot(template)}, indent=2, ensure_ascii=False))
    template.slots.side_slot.addWidget(diagnostics, 1)
    template.apply_layout_preset(payload["behavior"]["layouts"].get("default", "inspect"))
    return template


def build_foundry_preview(recipe_id: str, parent: QWidget | None = None, *, variant_id: str | None = None) -> GlassPanelTemplate:
    return build_foundry_foundation(recipe_id, parent=parent, variant_id=variant_id)


BUILTIN_FOUNDATION_RECIPES: tuple[dict[str, Any], ...] = ({'meta': {'id': 'foundation.ops_console_premium',
           'title': 'Operations Console Premium',
           'subtitle': 'Dense but beautiful command surface',
           'description': 'A high-trust operational console with governed tabs, strong hero summary, dense '
                          'data grid, and side inspector that can stay deferred until selection exists.',
           'category': 'Foundation Recipes',
           'status': 'stable',
           'tags': ['foundation', 'ops', 'console', 'premium'],
           'best_for': 'Operational consoles, execution desks and command stations.',
           'use_when': 'you need a premium default for work-first internal tools.',
           'sort_order': 700,
           'icon_name': 'activity',
           'mood': 'focused',
           'audience': 'operator'},
  'experience': {'beauty_profile': 'premium_focus',
                 'color_story': 'graphite_cyan',
                 'motion_profile': 'snappy_deluxe',
                 'layout_pack': 'operator_dense',
                 'shell_pack': 'ops_console',
                 'density': 'comfortable',
                 'visual_language': 'neo_control_room',
                 'ornament': 'restrained',
                 'contrast': 'high',
                 'notes': 'Operations Console Premium is tuned for operator work with premium focus presence '
                          'and the graphite cyan story.'},
  'shell': {'frameless': True,
            'translucent': True,
            'show_status_bar': True,
            'show_footer': False,
            'show_side': True,
            'window_radius': 14,
            'chrome_mode': 'control_room',
            'navigation_model': 'left_rail',
            'header_style': 'elevated',
            'search_mode': 'floating_command_bar'},
  'regions': {'hero': {'visible': True,
                       'role': 'contextual_banner',
                       'height': 104,
                       'notes': 'Top summary context with strong hierarchy.'},
              'main': {'visible': True,
                       'role': 'primary_workspace',
                       'notes': 'Primary task surface and main data density.'},
              'side': {'visible': True,
                       'role': 'contextual_inspector',
                       'width': 260,
                       'deferred': True,
                       'notes': 'Inspector, secondary controls or commentary.'},
              'status': {'visible': True,
                         'role': 'runtime_feedback',
                         'height': 28,
                         'notes': 'Low-noise runtime hints and health.'},
              'overlay': {'visible': True,
                          'role': 'command_palette',
                          'notes': 'Reserved for structured overlays and palette interactions.'}},
  'surfaces': [{'id': 'hero_summary',
                'type': 'hero_banner',
                'region': 'hero',
                'title': 'Operations Console Premium',
                'subtitle': 'Dense but beautiful command surface',
                'variant': 'hero_banner',
                'priority': 10,
                'stretch': 0,
                'min_height': 104,
                'states': {'loading': 'shimmer_soft',
                           'empty': 'illustration_message',
                           'error': 'inline_panel'},
                'items': ['Latency 38ms', 'Healthy 99.96%', 'Focus lane active', 'Policy clean'],
                'metadata': {'eyebrow': 'FOUNDATION RECIPES',
                             'description': 'A high-trust operational console with governed tabs, strong '
                                            'hero summary, dense data grid, and side inspector that can stay '
                                            'deferred until selection exists.',
                             'hero_metrics': ['throughput', 'health', 'focus', 'flags']}},
               {'id': 'primary_tabs',
                'type': 'tab_group',
                'region': 'main',
                'title': 'Workspace contexts',
                'subtitle': 'Primary contexts switch without changing shell ownership.',
                'variant': 'segmented_lux',
                'priority': 20,
                'stretch': 1,
                'tabs': [{'id': 'work',
                          'title': 'Work',
                          'content': 'main_grid',
                          'lazy': False,
                          'status': 'active'},
                         {'id': 'metrics',
                          'title': 'Metrics',
                          'content': 'signal_chart',
                          'lazy': True,
                          'status': 'standby'},
                         {'id': 'notes',
                          'title': 'Notes',
                          'content': 'activity_surface',
                          'lazy': True,
                          'status': 'standby'},
                         {'id': 'alerts',
                          'title': 'Alerts',
                          'content': 'activity_surface',
                          'lazy': True,
                          'status': 'standby'}],
                'metadata': {'tab_density': 'comfortable', 'tab_variant': 'glass'}},
               {'id': 'main_grid',
                'type': 'data_grid',
                'region': 'main',
                'title': 'Work queue',
                'subtitle': 'Main working surface with strong hierarchy and safe resize behavior.',
                'variant': 'premium_table',
                'priority': 30,
                'stretch': 3,
                'min_width': 520,
                'min_height': 260,
                'preferred_ratio': 0.72,
                'states': {'loading': 'skeleton_rows',
                           'empty': 'illustration_minimal',
                           'error': 'inline_diagnostic',
                           'deferred': 'deferred_notice'},
                'metadata': {'columns': ['Name', 'State', 'Owner', 'Latency', 'Updated'],
                             'sample_rows': 12,
                             'row_hover': 'glow_soft',
                             'header_tone': 'muted_raised'}},
               {'id': 'signal_chart',
                'type': 'chart',
                'region': 'main',
                'title': 'Throughput and latency',
                'subtitle': 'Signal visualization kept inside a governed surface host.',
                'variant': 'signal_chart',
                'priority': 40,
                'stretch': 2,
                'lazy': True,
                'min_height': 220,
                'states': {'loading': 'line_skeleton',
                           'empty': 'chart_empty_notice',
                           'error': 'inline_diagnostic'},
                'metadata': {'engine': 'pyqtgraph',
                             'kind': 'line_area',
                             'legend': True,
                             'grid_visibility': 'low'}},
               {'id': 'activity_surface',
                'type': 'activity_feed',
                'region': 'main',
                'title': 'Activity and notes',
                'subtitle': 'Event stream, notes or narrative trace without escaping the recipe system.',
                'variant': 'activity_stream',
                'priority': 50,
                'stretch': 1,
                'lazy': True,
                'states': {'loading': 'skeleton_lines', 'empty': 'quiet_zero_state', 'error': 'inline_panel'},
                'items': ['Health stable',
                          'Filter changed',
                          'Layout restored',
                          'Pinned selection updated',
                          'Policy re-evaluated']},
               {'id': 'side_inspector',
                'type': 'inspector_panel',
                'region': 'side',
                'title': 'Selection inspector',
                'subtitle': 'Detail panel with structured sections and sticky actions.',
                'variant': 'layered_form',
                'priority': 25,
                'stretch': 2,
                'deferred': True,
                'min_width': 260,
                'states': {'loading': 'skeleton_form',
                           'empty': 'selection_zero_state',
                           'error': 'inline_panel',
                           'deferred': 'deferred_notice'},
                'metadata': {'sections': ['Summary', 'Attributes', 'Actions', 'Diagnostics'],
                             'sticky_actions': True,
                             'section_dividers': 'soft'}},
               {'id': 'status_surface',
                'type': 'entity_summary',
                'region': 'status',
                'title': 'Runtime health',
                'subtitle': 'Low-noise health bar for layout, theme, motion and state.',
                'variant': 'glass_metric',
                'priority': 80,
                'stretch': 0,
                'states': {'ready': 'status_inline'},
                'items': ['Theme locked', 'Motion synced', 'Layout contract ok', 'State clean']}],
  'behavior': {'layouts': {'default': 'inspect',
                           'presets': ['focus', 'inspect', 'wallboard'],
                           'persistent': True},
               'visibility': {'by_role': True, 'by_mode': True, 'by_flags': True},
               'performance': {'lazy_tabs': True, 'deferred_panels': True, 'chart_throttle_ms': 120},
               'shortcuts': ['Ctrl+K command palette',
                             'Ctrl+1 work',
                             'Ctrl+2 metrics',
                             'Ctrl+Shift+I inspector'],
               'command_palette': True},
  'data': {'sources': [{'id': 'primary_table', 'kind': 'table', 'notes': 'Main operational rows.'},
                       {'id': 'selected_entity', 'kind': 'entity', 'notes': 'Inspector detail.'},
                       {'id': 'signal_series', 'kind': 'timeseries', 'notes': 'Metrics and trend line.'}],
           'ui_states': {'loading': {'treatment': 'shimmer_soft', 'blocking': False},
                         'empty': {'treatment': 'illustration_message', 'tone': 'elegant'},
                         'error': {'treatment': 'inline_diagnostic', 'recover_actions': ['retry', 'inspect']},
                         'stale': {'treatment': 'subtle_badge'}}},
  'quality': {'profile': 'strict',
              'beauty_checks': {'no_inline_colors': True,
                                'no_unstyled_widgets': True,
                                'spacing_scale_enforced': True,
                                'icon_family_enforced': True,
                                'motion_profile_enforced': True,
                                'layout_contract_required': True,
                                'states_required': True},
              'render_checks': {'theme_switch_test': True,
                                'compact_mode_test': True,
                                'empty_state_test': True,
                                'error_state_test': True,
                                'layout_restore_test': True,
                                'screenshot_baselines': True},
              'notes': 'Foundation recipes are expected to stay premium while preserving deterministic '
                       'layout behavior.'},
  'variants': [{'id': 'compact_shift',
                'label': 'Compact shift',
                'description': 'Tighter density and lower ornament for long sessions.',
                'overrides': {'experience': {'density': 'compact', 'motion_profile': 'operator_tight'},
                              'behavior': {'layouts': {'default': 'focus'}}}},
               {'id': 'review_mode',
                'label': 'Review mode',
                'description': 'Airier review stance with larger hero, calmer chart, and more side detail.',
                'overrides': {'experience': {'density': 'comfortable', 'motion_profile': 'subtle'},
                              'regions': {'side': {'width': 340}},
                              'behavior': {'layouts': {'default': 'inspect'}}}}]},
 {'meta': {'id': 'foundation.analytics_cinematic',
           'title': 'Analytics Cinematic',
           'subtitle': 'Summary-first monitoring wall',
           'description': 'A more cinematic dashboard with deeper hero, richer glass, and chart-first rhythm '
                          'without sacrificing shell governance or state handling.',
           'category': 'Foundation Recipes',
           'status': 'stable',
           'tags': ['foundation', 'analytics', 'dashboard', 'cinematic'],
           'best_for': 'Monitoring walls, KPI surfaces and richer visual storytelling.',
           'use_when': 'you want analytics to feel premium and alive without turning into RGB soup.',
           'sort_order': 710,
           'icon_name': 'bar-chart-2',
           'mood': 'cinematic',
           'audience': 'analyst'},
  'experience': {'beauty_profile': 'cinematic_glass',
                 'color_story': 'obsidian_violet',
                 'motion_profile': 'soft_cinematic',
                 'layout_pack': 'balanced_split',
                 'shell_pack': 'frameless_glass',
                 'density': 'comfortable',
                 'visual_language': 'cinematic_glass_shell',
                 'ornament': 'selective',
                 'contrast': 'high',
                 'notes': 'Analytics Cinematic is tuned for analyst work with cinematic glass presence and '
                          'the obsidian violet story.'},
  'shell': {'frameless': True,
            'translucent': True,
            'show_status_bar': True,
            'show_footer': False,
            'show_side': True,
            'window_radius': 18,
            'chrome_mode': 'soft_glass',
            'navigation_model': 'left_rail',
            'header_style': 'elevated',
            'search_mode': 'floating_command_bar'},
  'regions': {'hero': {'visible': True,
                       'role': 'contextual_banner',
                       'height': 120,
                       'notes': 'Top summary context with strong hierarchy.'},
              'main': {'visible': True,
                       'role': 'primary_workspace',
                       'notes': 'Primary task surface and main data density.'},
              'side': {'visible': True,
                       'role': 'contextual_inspector',
                       'width': 300,
                       'deferred': True,
                       'notes': 'Inspector, secondary controls or commentary.'},
              'status': {'visible': True,
                         'role': 'runtime_feedback',
                         'height': 32,
                         'notes': 'Low-noise runtime hints and health.'},
              'overlay': {'visible': True,
                          'role': 'command_palette',
                          'notes': 'Reserved for structured overlays and palette interactions.'}},
  'surfaces': [{'id': 'hero_summary',
                'type': 'hero_banner',
                'region': 'hero',
                'title': 'Analytics Cinematic',
                'subtitle': 'Summary-first monitoring wall',
                'variant': 'hero_banner',
                'priority': 10,
                'stretch': 0,
                'min_height': 120,
                'states': {'loading': 'shimmer_soft',
                           'empty': 'illustration_message',
                           'error': 'inline_panel'},
                'items': ['Latency 38ms', 'Healthy 99.96%', 'Focus lane active', 'Policy clean'],
                'metadata': {'eyebrow': 'FOUNDATION RECIPES',
                             'description': 'A more cinematic dashboard with deeper hero, richer glass, and '
                                            'chart-first rhythm without sacrificing shell governance or '
                                            'state handling.',
                             'hero_metrics': ['throughput', 'health', 'focus', 'flags']}},
               {'id': 'primary_tabs',
                'type': 'tab_group',
                'region': 'main',
                'title': 'Workspace contexts',
                'subtitle': 'Primary contexts switch without changing shell ownership.',
                'variant': 'segmented_lux',
                'priority': 20,
                'stretch': 1,
                'tabs': [{'id': 'work',
                          'title': 'Work',
                          'content': 'main_grid',
                          'lazy': False,
                          'status': 'active'},
                         {'id': 'metrics',
                          'title': 'Metrics',
                          'content': 'signal_chart',
                          'lazy': True,
                          'status': 'standby'},
                         {'id': 'notes',
                          'title': 'Notes',
                          'content': 'activity_surface',
                          'lazy': True,
                          'status': 'standby'},
                         {'id': 'benchmarks',
                          'title': 'Benchmarks',
                          'content': 'signal_chart',
                          'lazy': True,
                          'status': 'standby'}],
                'metadata': {'tab_density': 'comfortable', 'tab_variant': 'glass'}},
               {'id': 'main_grid',
                'type': 'data_grid',
                'region': 'main',
                'title': 'KPI grid',
                'subtitle': 'Main working surface with strong hierarchy and safe resize behavior.',
                'variant': 'premium_table',
                'priority': 30,
                'stretch': 3,
                'min_width': 480,
                'min_height': 260,
                'preferred_ratio': 0.68,
                'states': {'loading': 'skeleton_rows',
                           'empty': 'illustration_minimal',
                           'error': 'inline_diagnostic',
                           'deferred': 'deferred_notice'},
                'metadata': {'columns': ['Name', 'State', 'Owner', 'Latency', 'Updated'],
                             'sample_rows': 12,
                             'row_hover': 'glow_soft',
                             'header_tone': 'muted_raised'}},
               {'id': 'signal_chart',
                'type': 'chart',
                'region': 'main',
                'title': 'Signal horizon',
                'subtitle': 'Signal visualization kept inside a governed surface host.',
                'variant': 'signal_chart',
                'priority': 40,
                'stretch': 2,
                'lazy': True,
                'min_height': 220,
                'states': {'loading': 'line_skeleton',
                           'empty': 'chart_empty_notice',
                           'error': 'inline_diagnostic'},
                'metadata': {'engine': 'pyqtgraph',
                             'kind': 'line_area',
                             'legend': True,
                             'grid_visibility': 'low'}},
               {'id': 'activity_surface',
                'type': 'activity_feed',
                'region': 'main',
                'title': 'Activity and notes',
                'subtitle': 'Event stream, notes or narrative trace without escaping the recipe system.',
                'variant': 'activity_stream',
                'priority': 50,
                'stretch': 1,
                'lazy': True,
                'states': {'loading': 'skeleton_lines', 'empty': 'quiet_zero_state', 'error': 'inline_panel'},
                'items': ['Health stable',
                          'Filter changed',
                          'Layout restored',
                          'Pinned selection updated',
                          'Policy re-evaluated']},
               {'id': 'side_inspector',
                'type': 'inspector_panel',
                'region': 'side',
                'title': 'Context panel',
                'subtitle': 'Detail panel with structured sections and sticky actions.',
                'variant': 'layered_form',
                'priority': 25,
                'stretch': 2,
                'deferred': True,
                'min_width': 300,
                'states': {'loading': 'skeleton_form',
                           'empty': 'selection_zero_state',
                           'error': 'inline_panel',
                           'deferred': 'deferred_notice'},
                'metadata': {'sections': ['Summary', 'Attributes', 'Actions', 'Diagnostics'],
                             'sticky_actions': True,
                             'section_dividers': 'soft'}},
               {'id': 'status_surface',
                'type': 'entity_summary',
                'region': 'status',
                'title': 'Runtime health',
                'subtitle': 'Low-noise health bar for layout, theme, motion and state.',
                'variant': 'glass_metric',
                'priority': 80,
                'stretch': 0,
                'states': {'ready': 'status_inline'},
                'items': ['Theme locked', 'Motion synced', 'Layout contract ok', 'State clean']}],
  'behavior': {'layouts': {'default': 'inspect',
                           'presets': ['focus', 'inspect', 'wallboard'],
                           'persistent': True},
               'visibility': {'by_role': True, 'by_mode': True, 'by_flags': True},
               'performance': {'lazy_tabs': True, 'deferred_panels': True, 'chart_throttle_ms': 120},
               'shortcuts': ['Ctrl+K command palette',
                             'Ctrl+1 work',
                             'Ctrl+2 metrics',
                             'Ctrl+Shift+I inspector'],
               'command_palette': True},
  'data': {'sources': [{'id': 'primary_table', 'kind': 'table', 'notes': 'Main operational rows.'},
                       {'id': 'selected_entity', 'kind': 'entity', 'notes': 'Inspector detail.'},
                       {'id': 'signal_series', 'kind': 'timeseries', 'notes': 'Metrics and trend line.'}],
           'ui_states': {'loading': {'treatment': 'shimmer_soft', 'blocking': False},
                         'empty': {'treatment': 'illustration_message', 'tone': 'elegant'},
                         'error': {'treatment': 'inline_diagnostic', 'recover_actions': ['retry', 'inspect']},
                         'stale': {'treatment': 'subtle_badge'}}},
  'quality': {'profile': 'strict',
              'beauty_checks': {'no_inline_colors': True,
                                'no_unstyled_widgets': True,
                                'spacing_scale_enforced': True,
                                'icon_family_enforced': True,
                                'motion_profile_enforced': True,
                                'layout_contract_required': True,
                                'states_required': True},
              'render_checks': {'theme_switch_test': True,
                                'compact_mode_test': True,
                                'empty_state_test': True,
                                'error_state_test': True,
                                'layout_restore_test': True,
                                'screenshot_baselines': True},
              'notes': 'Foundation recipes are expected to stay premium while preserving deterministic '
                       'layout behavior.'},
  'variants': [{'id': 'compact_shift',
                'label': 'Compact shift',
                'description': 'Tighter density and lower ornament for long sessions.',
                'overrides': {'experience': {'density': 'compact', 'motion_profile': 'operator_tight'},
                              'behavior': {'layouts': {'default': 'focus'}}}},
               {'id': 'review_mode',
                'label': 'Review mode',
                'description': 'Airier review stance with larger hero, calmer chart, and more side detail.',
                'overrides': {'experience': {'density': 'comfortable', 'motion_profile': 'subtle'},
                              'regions': {'side': {'width': 340}},
                              'behavior': {'layouts': {'default': 'inspect'}}}}]},
 {'meta': {'id': 'foundation.inspector_precision',
           'title': 'Inspector Precision',
           'subtitle': 'Detail-heavy inspection workstation',
           'description': 'An inspection-first shell with wider side context, technical rhythm, compact '
                          'spacing and clear state affordances for event, entity and payload review.',
           'category': 'Foundation Recipes',
           'status': 'stable',
           'tags': ['foundation', 'inspector', 'precision', 'review'],
           'best_for': 'Entity inspection, event review and debugging surfaces.',
           'use_when': 'you need detail to dominate without layout drama.',
           'sort_order': 720,
           'icon_name': 'search',
           'mood': 'technical',
           'audience': 'reviewer'},
  'experience': {'beauty_profile': 'industrial_precision',
                 'color_story': 'moonstone_teal',
                 'motion_profile': 'operator_tight',
                 'layout_pack': 'inspector_heavy',
                 'shell_pack': 'framed_productive',
                 'density': 'compact',
                 'visual_language': 'industrial_operator',
                 'ornament': 'minimal',
                 'contrast': 'high',
                 'notes': 'Inspector Precision is tuned for reviewer work with industrial precision presence '
                          'and the moonstone teal story.'},
  'shell': {'frameless': False,
            'translucent': False,
            'show_status_bar': True,
            'show_footer': False,
            'show_side': True,
            'window_radius': 12,
            'chrome_mode': 'native',
            'navigation_model': 'left_rail',
            'header_style': 'elevated',
            'search_mode': 'floating_command_bar'},
  'regions': {'hero': {'visible': True,
                       'role': 'contextual_banner',
                       'height': 110,
                       'notes': 'Top summary context with strong hierarchy.'},
              'main': {'visible': True,
                       'role': 'primary_workspace',
                       'notes': 'Primary task surface and main data density.'},
              'side': {'visible': True,
                       'role': 'contextual_inspector',
                       'width': 380,
                       'deferred': True,
                       'notes': 'Inspector, secondary controls or commentary.'},
              'status': {'visible': True,
                         'role': 'runtime_feedback',
                         'height': 32,
                         'notes': 'Low-noise runtime hints and health.'},
              'overlay': {'visible': True,
                          'role': 'command_palette',
                          'notes': 'Reserved for structured overlays and palette interactions.'}},
  'surfaces': [{'id': 'hero_summary',
                'type': 'hero_banner',
                'region': 'hero',
                'title': 'Inspector Precision',
                'subtitle': 'Detail-heavy inspection workstation',
                'variant': 'hero_banner',
                'priority': 10,
                'stretch': 0,
                'min_height': 110,
                'states': {'loading': 'shimmer_soft',
                           'empty': 'illustration_message',
                           'error': 'inline_panel'},
                'items': ['Latency 38ms', 'Healthy 99.96%', 'Focus lane active', 'Policy clean'],
                'metadata': {'eyebrow': 'FOUNDATION RECIPES',
                             'description': 'An inspection-first shell with wider side context, technical '
                                            'rhythm, compact spacing and clear state affordances for event, '
                                            'entity and payload review.',
                             'hero_metrics': ['throughput', 'health', 'focus', 'flags']}},
               {'id': 'primary_tabs',
                'type': 'tab_group',
                'region': 'main',
                'title': 'Workspace contexts',
                'subtitle': 'Primary contexts switch without changing shell ownership.',
                'variant': 'segmented_lux',
                'priority': 20,
                'stretch': 1,
                'tabs': [{'id': 'work',
                          'title': 'Work',
                          'content': 'main_grid',
                          'lazy': False,
                          'status': 'active'},
                         {'id': 'metrics',
                          'title': 'Metrics',
                          'content': 'signal_chart',
                          'lazy': True,
                          'status': 'standby'},
                         {'id': 'notes',
                          'title': 'Notes',
                          'content': 'activity_surface',
                          'lazy': True,
                          'status': 'standby'},
                         {'id': 'raw',
                          'title': 'Raw',
                          'content': 'activity_surface',
                          'lazy': True,
                          'status': 'standby'}],
                'metadata': {'tab_density': 'comfortable', 'tab_variant': 'glass'}},
               {'id': 'main_grid',
                'type': 'data_grid',
                'region': 'main',
                'title': 'Inspection results',
                'subtitle': 'Main working surface with strong hierarchy and safe resize behavior.',
                'variant': 'premium_table',
                'priority': 30,
                'stretch': 3,
                'min_width': 420,
                'min_height': 260,
                'preferred_ratio': 0.58,
                'states': {'loading': 'skeleton_rows',
                           'empty': 'illustration_minimal',
                           'error': 'inline_diagnostic',
                           'deferred': 'deferred_notice'},
                'metadata': {'columns': ['Name', 'State', 'Owner', 'Latency', 'Updated'],
                             'sample_rows': 12,
                             'row_hover': 'glow_soft',
                             'header_tone': 'muted_raised'}},
               {'id': 'signal_chart',
                'type': 'chart',
                'region': 'main',
                'title': 'Anomaly trace',
                'subtitle': 'Signal visualization kept inside a governed surface host.',
                'variant': 'signal_chart',
                'priority': 40,
                'stretch': 2,
                'lazy': True,
                'min_height': 220,
                'states': {'loading': 'line_skeleton',
                           'empty': 'chart_empty_notice',
                           'error': 'inline_diagnostic'},
                'metadata': {'engine': 'pyqtgraph',
                             'kind': 'line_area',
                             'legend': True,
                             'grid_visibility': 'low'}},
               {'id': 'activity_surface',
                'type': 'activity_feed',
                'region': 'main',
                'title': 'Activity and notes',
                'subtitle': 'Event stream, notes or narrative trace without escaping the recipe system.',
                'variant': 'activity_stream',
                'priority': 50,
                'stretch': 1,
                'lazy': True,
                'states': {'loading': 'skeleton_lines', 'empty': 'quiet_zero_state', 'error': 'inline_panel'},
                'items': ['Health stable',
                          'Filter changed',
                          'Layout restored',
                          'Pinned selection updated',
                          'Policy re-evaluated']},
               {'id': 'side_inspector',
                'type': 'inspector_panel',
                'region': 'side',
                'title': 'Payload and actions',
                'subtitle': 'Detail panel with structured sections and sticky actions.',
                'variant': 'layered_form',
                'priority': 25,
                'stretch': 2,
                'deferred': True,
                'min_width': 380,
                'states': {'loading': 'skeleton_form',
                           'empty': 'selection_zero_state',
                           'error': 'inline_panel',
                           'deferred': 'deferred_notice'},
                'metadata': {'sections': ['Summary', 'Attributes', 'Actions', 'Diagnostics'],
                             'sticky_actions': True,
                             'section_dividers': 'soft'}},
               {'id': 'status_surface',
                'type': 'entity_summary',
                'region': 'status',
                'title': 'Runtime health',
                'subtitle': 'Low-noise health bar for layout, theme, motion and state.',
                'variant': 'glass_metric',
                'priority': 80,
                'stretch': 0,
                'states': {'ready': 'status_inline'},
                'items': ['Theme locked', 'Motion synced', 'Layout contract ok', 'State clean']}],
  'behavior': {'layouts': {'default': 'inspect',
                           'presets': ['focus', 'inspect', 'wallboard'],
                           'persistent': True},
               'visibility': {'by_role': True, 'by_mode': True, 'by_flags': True},
               'performance': {'lazy_tabs': True, 'deferred_panels': True, 'chart_throttle_ms': 120},
               'shortcuts': ['Ctrl+K command palette',
                             'Ctrl+1 work',
                             'Ctrl+2 metrics',
                             'Ctrl+Shift+I inspector'],
               'command_palette': True},
  'data': {'sources': [{'id': 'primary_table', 'kind': 'table', 'notes': 'Main operational rows.'},
                       {'id': 'selected_entity', 'kind': 'entity', 'notes': 'Inspector detail.'},
                       {'id': 'signal_series', 'kind': 'timeseries', 'notes': 'Metrics and trend line.'}],
           'ui_states': {'loading': {'treatment': 'shimmer_soft', 'blocking': False},
                         'empty': {'treatment': 'illustration_message', 'tone': 'elegant'},
                         'error': {'treatment': 'inline_diagnostic', 'recover_actions': ['retry', 'inspect']},
                         'stale': {'treatment': 'subtle_badge'}}},
  'quality': {'profile': 'strict',
              'beauty_checks': {'no_inline_colors': True,
                                'no_unstyled_widgets': True,
                                'spacing_scale_enforced': True,
                                'icon_family_enforced': True,
                                'motion_profile_enforced': True,
                                'layout_contract_required': True,
                                'states_required': True},
              'render_checks': {'theme_switch_test': True,
                                'compact_mode_test': True,
                                'empty_state_test': True,
                                'error_state_test': True,
                                'layout_restore_test': True,
                                'screenshot_baselines': True},
              'notes': 'Foundation recipes are expected to stay premium while preserving deterministic '
                       'layout behavior.'},
  'variants': [{'id': 'compact_shift',
                'label': 'Compact shift',
                'description': 'Tighter density and lower ornament for long sessions.',
                'overrides': {'experience': {'density': 'compact', 'motion_profile': 'operator_tight'},
                              'behavior': {'layouts': {'default': 'focus'}}}},
               {'id': 'review_mode',
                'label': 'Review mode',
                'description': 'Airier review stance with larger hero, calmer chart, and more side detail.',
                'overrides': {'experience': {'density': 'comfortable', 'motion_profile': 'subtle'},
                              'regions': {'side': {'width': 380}},
                              'behavior': {'layouts': {'default': 'inspect'}}}}]},
 {'meta': {'id': 'foundation.executive_signal',
           'title': 'Executive Signal',
           'subtitle': 'Decision board with calm authority',
           'description': 'A restrained executive dashboard focused on signal, confidence and clean '
                          'takeaways, with less noise and more immediate legibility.',
           'category': 'Foundation Recipes',
           'status': 'stable',
           'tags': ['foundation', 'executive', 'signal', 'board'],
           'best_for': 'Leadership views, reviews and summary rooms.',
           'use_when': 'you want metrics to read like answers, not like punishment.',
           'sort_order': 730,
           'icon_name': 'trending-up',
           'mood': 'calm_confident',
           'audience': 'executive'},
  'experience': {'beauty_profile': 'executive_signal',
                 'color_story': 'ember_gold',
                 'motion_profile': 'subtle',
                 'layout_pack': 'wallboard',
                 'shell_pack': 'editorial_light',
                 'density': 'comfortable',
                 'visual_language': 'summary_wall',
                 'ornament': 'restrained',
                 'contrast': 'medium_high',
                 'notes': 'Executive Signal is tuned for executive work with executive signal presence and '
                          'the ember gold story.'},
  'shell': {'frameless': False,
            'translucent': False,
            'show_status_bar': True,
            'show_footer': False,
            'show_side': True,
            'window_radius': 14,
            'chrome_mode': 'paper',
            'navigation_model': 'left_rail',
            'header_style': 'elevated',
            'search_mode': 'floating_command_bar'},
  'regions': {'hero': {'visible': True,
                       'role': 'contextual_banner',
                       'height': 140,
                       'notes': 'Top summary context with strong hierarchy.'},
              'main': {'visible': True,
                       'role': 'primary_workspace',
                       'notes': 'Primary task surface and main data density.'},
              'side': {'visible': True,
                       'role': 'contextual_inspector',
                       'width': 240,
                       'deferred': True,
                       'notes': 'Inspector, secondary controls or commentary.'},
              'status': {'visible': True,
                         'role': 'runtime_feedback',
                         'height': 30,
                         'notes': 'Low-noise runtime hints and health.'},
              'overlay': {'visible': True,
                          'role': 'command_palette',
                          'notes': 'Reserved for structured overlays and palette interactions.'}},
  'surfaces': [{'id': 'hero_summary',
                'type': 'hero_banner',
                'region': 'hero',
                'title': 'Executive Signal',
                'subtitle': 'Decision board with calm authority',
                'variant': 'hero_banner',
                'priority': 10,
                'stretch': 0,
                'min_height': 140,
                'states': {'loading': 'shimmer_soft',
                           'empty': 'illustration_message',
                           'error': 'inline_panel'},
                'items': ['Latency 38ms', 'Healthy 99.96%', 'Focus lane active', 'Policy clean'],
                'metadata': {'eyebrow': 'FOUNDATION RECIPES',
                             'description': 'A restrained executive dashboard focused on signal, confidence '
                                            'and clean takeaways, with less noise and more immediate '
                                            'legibility.',
                             'hero_metrics': ['throughput', 'health', 'focus', 'flags']}},
               {'id': 'primary_tabs',
                'type': 'tab_group',
                'region': 'main',
                'title': 'Workspace contexts',
                'subtitle': 'Primary contexts switch without changing shell ownership.',
                'variant': 'segmented_lux',
                'priority': 20,
                'stretch': 1,
                'tabs': [{'id': 'work',
                          'title': 'Work',
                          'content': 'main_grid',
                          'lazy': False,
                          'status': 'active'},
                         {'id': 'metrics',
                          'title': 'Metrics',
                          'content': 'signal_chart',
                          'lazy': True,
                          'status': 'standby'},
                         {'id': 'notes',
                          'title': 'Notes',
                          'content': 'activity_surface',
                          'lazy': True,
                          'status': 'standby'},
                         {'id': 'risks',
                          'title': 'Risks',
                          'content': 'activity_surface',
                          'lazy': True,
                          'status': 'standby'}],
                'metadata': {'tab_density': 'comfortable', 'tab_variant': 'glass'}},
               {'id': 'main_grid',
                'type': 'data_grid',
                'region': 'main',
                'title': 'Decision matrix',
                'subtitle': 'Main working surface with strong hierarchy and safe resize behavior.',
                'variant': 'premium_table',
                'priority': 30,
                'stretch': 3,
                'min_width': 760,
                'min_height': 260,
                'preferred_ratio': 0.8,
                'states': {'loading': 'skeleton_rows',
                           'empty': 'illustration_minimal',
                           'error': 'inline_diagnostic',
                           'deferred': 'deferred_notice'},
                'metadata': {'columns': ['Name', 'State', 'Owner', 'Latency', 'Updated'],
                             'sample_rows': 12,
                             'row_hover': 'glow_soft',
                             'header_tone': 'muted_raised'}},
               {'id': 'signal_chart',
                'type': 'chart',
                'region': 'main',
                'title': 'Confidence trend',
                'subtitle': 'Signal visualization kept inside a governed surface host.',
                'variant': 'signal_chart',
                'priority': 40,
                'stretch': 2,
                'lazy': True,
                'min_height': 220,
                'states': {'loading': 'line_skeleton',
                           'empty': 'chart_empty_notice',
                           'error': 'inline_diagnostic'},
                'metadata': {'engine': 'pyqtgraph',
                             'kind': 'line_area',
                             'legend': True,
                             'grid_visibility': 'low'}},
               {'id': 'activity_surface',
                'type': 'activity_feed',
                'region': 'main',
                'title': 'Activity and notes',
                'subtitle': 'Event stream, notes or narrative trace without escaping the recipe system.',
                'variant': 'activity_stream',
                'priority': 50,
                'stretch': 1,
                'lazy': True,
                'states': {'loading': 'skeleton_lines', 'empty': 'quiet_zero_state', 'error': 'inline_panel'},
                'items': ['Health stable',
                          'Filter changed',
                          'Layout restored',
                          'Pinned selection updated',
                          'Policy re-evaluated']},
               {'id': 'side_inspector',
                'type': 'inspector_panel',
                'region': 'side',
                'title': 'Narrative context',
                'subtitle': 'Detail panel with structured sections and sticky actions.',
                'variant': 'layered_form',
                'priority': 25,
                'stretch': 2,
                'deferred': True,
                'min_width': 240,
                'states': {'loading': 'skeleton_form',
                           'empty': 'selection_zero_state',
                           'error': 'inline_panel',
                           'deferred': 'deferred_notice'},
                'metadata': {'sections': ['Summary', 'Attributes', 'Actions', 'Diagnostics'],
                             'sticky_actions': True,
                             'section_dividers': 'soft'}},
               {'id': 'status_surface',
                'type': 'entity_summary',
                'region': 'status',
                'title': 'Runtime health',
                'subtitle': 'Low-noise health bar for layout, theme, motion and state.',
                'variant': 'glass_metric',
                'priority': 80,
                'stretch': 0,
                'states': {'ready': 'status_inline'},
                'items': ['Theme locked', 'Motion synced', 'Layout contract ok', 'State clean']}],
  'behavior': {'layouts': {'default': 'inspect',
                           'presets': ['focus', 'inspect', 'wallboard'],
                           'persistent': True},
               'visibility': {'by_role': True, 'by_mode': True, 'by_flags': True},
               'performance': {'lazy_tabs': True, 'deferred_panels': True, 'chart_throttle_ms': 120},
               'shortcuts': ['Ctrl+K command palette',
                             'Ctrl+1 work',
                             'Ctrl+2 metrics',
                             'Ctrl+Shift+I inspector'],
               'command_palette': True},
  'data': {'sources': [{'id': 'primary_table', 'kind': 'table', 'notes': 'Main operational rows.'},
                       {'id': 'selected_entity', 'kind': 'entity', 'notes': 'Inspector detail.'},
                       {'id': 'signal_series', 'kind': 'timeseries', 'notes': 'Metrics and trend line.'}],
           'ui_states': {'loading': {'treatment': 'shimmer_soft', 'blocking': False},
                         'empty': {'treatment': 'illustration_message', 'tone': 'elegant'},
                         'error': {'treatment': 'inline_diagnostic', 'recover_actions': ['retry', 'inspect']},
                         'stale': {'treatment': 'subtle_badge'}}},
  'quality': {'profile': 'strict',
              'beauty_checks': {'no_inline_colors': True,
                                'no_unstyled_widgets': True,
                                'spacing_scale_enforced': True,
                                'icon_family_enforced': True,
                                'motion_profile_enforced': True,
                                'layout_contract_required': True,
                                'states_required': True},
              'render_checks': {'theme_switch_test': True,
                                'compact_mode_test': True,
                                'empty_state_test': True,
                                'error_state_test': True,
                                'layout_restore_test': True,
                                'screenshot_baselines': True},
              'notes': 'Foundation recipes are expected to stay premium while preserving deterministic '
                       'layout behavior.'},
  'variants': [{'id': 'compact_shift',
                'label': 'Compact shift',
                'description': 'Tighter density and lower ornament for long sessions.',
                'overrides': {'experience': {'density': 'compact', 'motion_profile': 'operator_tight'},
                              'behavior': {'layouts': {'default': 'focus'}}}},
               {'id': 'review_mode',
                'label': 'Review mode',
                'description': 'Airier review stance with larger hero, calmer chart, and more side detail.',
                'overrides': {'experience': {'density': 'comfortable', 'motion_profile': 'subtle'},
                              'regions': {'side': {'width': 340}},
                              'behavior': {'layouts': {'default': 'inspect'}}}}]},
 {'meta': {'id': 'foundation.form_workbench',
           'title': 'Form Workbench',
           'subtitle': 'Structured entry without looking municipal',
           'description': 'A recipe for capture-heavy tools that still feel premium: hero for context, '
                          'governed main workspace, soft inspector and explicit empty/error/loading states.',
           'category': 'Foundation Recipes',
           'status': 'stable',
           'tags': ['foundation', 'form', 'capture', 'workbench'],
           'best_for': 'Form-first tools, editors and structured workflows.',
           'use_when': 'you need entry screens that feel expensive instead of bureaucratic.',
           'sort_order': 740,
           'icon_name': 'file-text',
           'mood': 'warm_precise',
           'audience': 'general'},
  'experience': {'beauty_profile': 'warm_editorial',
                 'color_story': 'paper_plum',
                 'motion_profile': 'subtle',
                 'layout_pack': 'editorial_dual',
                 'shell_pack': 'editorial_light',
                 'density': 'comfortable',
                 'visual_language': 'warm_premium_review',
                 'ornament': 'low',
                 'contrast': 'medium',
                 'notes': 'Form Workbench is tuned for general work with warm editorial presence and the '
                          'paper plum story.'},
  'shell': {'frameless': False,
            'translucent': False,
            'show_status_bar': True,
            'show_footer': False,
            'show_side': True,
            'window_radius': 14,
            'chrome_mode': 'paper',
            'navigation_model': 'left_rail',
            'header_style': 'elevated',
            'search_mode': 'floating_command_bar'},
  'regions': {'hero': {'visible': True,
                       'role': 'contextual_banner',
                       'height': 136,
                       'notes': 'Top summary context with strong hierarchy.'},
              'main': {'visible': True,
                       'role': 'primary_workspace',
                       'notes': 'Primary task surface and main data density.'},
              'side': {'visible': True,
                       'role': 'contextual_inspector',
                       'width': 320,
                       'deferred': True,
                       'notes': 'Inspector, secondary controls or commentary.'},
              'status': {'visible': True,
                         'role': 'runtime_feedback',
                         'height': 32,
                         'notes': 'Low-noise runtime hints and health.'},
              'overlay': {'visible': True,
                          'role': 'command_palette',
                          'notes': 'Reserved for structured overlays and palette interactions.'}},
  'surfaces': [{'id': 'hero_summary',
                'type': 'hero_banner',
                'region': 'hero',
                'title': 'Form Workbench',
                'subtitle': 'Structured entry without looking municipal',
                'variant': 'hero_banner',
                'priority': 10,
                'stretch': 0,
                'min_height': 136,
                'states': {'loading': 'shimmer_soft',
                           'empty': 'illustration_message',
                           'error': 'inline_panel'},
                'items': ['Latency 38ms', 'Healthy 99.96%', 'Focus lane active', 'Policy clean'],
                'metadata': {'eyebrow': 'FOUNDATION RECIPES',
                             'description': 'A recipe for capture-heavy tools that still feel premium: hero '
                                            'for context, governed main workspace, soft inspector and '
                                            'explicit empty/error/loading states.',
                             'hero_metrics': ['throughput', 'health', 'focus', 'flags']}},
               {'id': 'primary_tabs',
                'type': 'tab_group',
                'region': 'main',
                'title': 'Workspace contexts',
                'subtitle': 'Primary contexts switch without changing shell ownership.',
                'variant': 'segmented_lux',
                'priority': 20,
                'stretch': 1,
                'tabs': [{'id': 'work',
                          'title': 'Work',
                          'content': 'main_grid',
                          'lazy': False,
                          'status': 'active'},
                         {'id': 'metrics',
                          'title': 'Metrics',
                          'content': 'signal_chart',
                          'lazy': True,
                          'status': 'standby'},
                         {'id': 'notes',
                          'title': 'Notes',
                          'content': 'activity_surface',
                          'lazy': True,
                          'status': 'standby'},
                         {'id': 'history',
                          'title': 'History',
                          'content': 'activity_surface',
                          'lazy': True,
                          'status': 'standby'}],
                'metadata': {'tab_density': 'comfortable', 'tab_variant': 'glass'}},
               {'id': 'main_grid',
                'type': 'data_grid',
                'region': 'main',
                'title': 'Entry workspace',
                'subtitle': 'Main working surface with strong hierarchy and safe resize behavior.',
                'variant': 'premium_table',
                'priority': 30,
                'stretch': 3,
                'min_width': 520,
                'min_height': 260,
                'preferred_ratio': 0.62,
                'states': {'loading': 'skeleton_rows',
                           'empty': 'illustration_minimal',
                           'error': 'inline_diagnostic',
                           'deferred': 'deferred_notice'},
                'metadata': {'columns': ['Name', 'State', 'Owner', 'Latency', 'Updated'],
                             'sample_rows': 12,
                             'row_hover': 'glow_soft',
                             'header_tone': 'muted_raised'}},
               {'id': 'signal_chart',
                'type': 'chart',
                'region': 'main',
                'title': 'Completion trend',
                'subtitle': 'Signal visualization kept inside a governed surface host.',
                'variant': 'signal_chart',
                'priority': 40,
                'stretch': 2,
                'lazy': True,
                'min_height': 220,
                'states': {'loading': 'line_skeleton',
                           'empty': 'chart_empty_notice',
                           'error': 'inline_diagnostic'},
                'metadata': {'engine': 'pyqtgraph',
                             'kind': 'line_area',
                             'legend': True,
                             'grid_visibility': 'low'}},
               {'id': 'activity_surface',
                'type': 'activity_feed',
                'region': 'main',
                'title': 'Activity and notes',
                'subtitle': 'Event stream, notes or narrative trace without escaping the recipe system.',
                'variant': 'activity_stream',
                'priority': 50,
                'stretch': 1,
                'lazy': True,
                'states': {'loading': 'skeleton_lines', 'empty': 'quiet_zero_state', 'error': 'inline_panel'},
                'items': ['Health stable',
                          'Filter changed',
                          'Layout restored',
                          'Pinned selection updated',
                          'Policy re-evaluated']},
               {'id': 'side_inspector',
                'type': 'inspector_panel',
                'region': 'side',
                'title': 'Validation and guidance',
                'subtitle': 'Detail panel with structured sections and sticky actions.',
                'variant': 'layered_form',
                'priority': 25,
                'stretch': 2,
                'deferred': True,
                'min_width': 320,
                'states': {'loading': 'skeleton_form',
                           'empty': 'selection_zero_state',
                           'error': 'inline_panel',
                           'deferred': 'deferred_notice'},
                'metadata': {'sections': ['Summary', 'Attributes', 'Actions', 'Diagnostics'],
                             'sticky_actions': True,
                             'section_dividers': 'soft'}},
               {'id': 'status_surface',
                'type': 'entity_summary',
                'region': 'status',
                'title': 'Runtime health',
                'subtitle': 'Low-noise health bar for layout, theme, motion and state.',
                'variant': 'glass_metric',
                'priority': 80,
                'stretch': 0,
                'states': {'ready': 'status_inline'},
                'items': ['Theme locked', 'Motion synced', 'Layout contract ok', 'State clean']}],
  'behavior': {'layouts': {'default': 'inspect',
                           'presets': ['focus', 'inspect', 'wallboard'],
                           'persistent': True},
               'visibility': {'by_role': True, 'by_mode': True, 'by_flags': True},
               'performance': {'lazy_tabs': True, 'deferred_panels': True, 'chart_throttle_ms': 120},
               'shortcuts': ['Ctrl+K command palette',
                             'Ctrl+1 work',
                             'Ctrl+2 metrics',
                             'Ctrl+Shift+I inspector'],
               'command_palette': True},
  'data': {'sources': [{'id': 'primary_table', 'kind': 'table', 'notes': 'Main operational rows.'},
                       {'id': 'selected_entity', 'kind': 'entity', 'notes': 'Inspector detail.'},
                       {'id': 'signal_series', 'kind': 'timeseries', 'notes': 'Metrics and trend line.'}],
           'ui_states': {'loading': {'treatment': 'shimmer_soft', 'blocking': False},
                         'empty': {'treatment': 'illustration_message', 'tone': 'elegant'},
                         'error': {'treatment': 'inline_diagnostic', 'recover_actions': ['retry', 'inspect']},
                         'stale': {'treatment': 'subtle_badge'}}},
  'quality': {'profile': 'strict',
              'beauty_checks': {'no_inline_colors': True,
                                'no_unstyled_widgets': True,
                                'spacing_scale_enforced': True,
                                'icon_family_enforced': True,
                                'motion_profile_enforced': True,
                                'layout_contract_required': True,
                                'states_required': True},
              'render_checks': {'theme_switch_test': True,
                                'compact_mode_test': True,
                                'empty_state_test': True,
                                'error_state_test': True,
                                'layout_restore_test': True,
                                'screenshot_baselines': True},
              'notes': 'Foundation recipes are expected to stay premium while preserving deterministic '
                       'layout behavior.'},
  'variants': [{'id': 'compact_shift',
                'label': 'Compact shift',
                'description': 'Tighter density and lower ornament for long sessions.',
                'overrides': {'experience': {'density': 'compact', 'motion_profile': 'operator_tight'},
                              'behavior': {'layouts': {'default': 'focus'}}}},
               {'id': 'review_mode',
                'label': 'Review mode',
                'description': 'Airier review stance with larger hero, calmer chart, and more side detail.',
                'overrides': {'experience': {'density': 'comfortable', 'motion_profile': 'subtle'},
                              'regions': {'side': {'width': 340}},
                              'behavior': {'layouts': {'default': 'inspect'}}}}]},
 {'meta': {'id': 'foundation.asset_browser_glass',
           'title': 'Asset Browser Glass',
           'subtitle': 'Gallery and metadata browser',
           'description': 'A premium asset browser recipe for browsing, previewing and inspecting media, '
                          'resources or entities with a gallery-ready main surface and clean side metadata.',
           'category': 'Foundation Recipes',
           'status': 'stable',
           'tags': ['foundation', 'browser', 'gallery', 'assets'],
           'best_for': 'Asset libraries, media browsers and resource explorers.',
           'use_when': 'you need browse-first workflows that still obey the shell.',
           'sort_order': 750,
           'icon_name': 'image',
           'mood': 'slick',
           'audience': 'analyst'},
  'experience': {'beauty_profile': 'premium_focus',
                 'color_story': 'frosted_emerald',
                 'motion_profile': 'snappy_deluxe',
                 'layout_pack': 'balanced_split',
                 'shell_pack': 'frameless_glass',
                 'density': 'comfortable',
                 'visual_language': 'neo_control_room',
                 'ornament': 'restrained',
                 'contrast': 'high',
                 'notes': 'Asset Browser Glass is tuned for analyst work with premium focus presence and the '
                          'frosted emerald story.'},
  'shell': {'frameless': True,
            'translucent': True,
            'show_status_bar': True,
            'show_footer': False,
            'show_side': True,
            'window_radius': 18,
            'chrome_mode': 'soft_glass',
            'navigation_model': 'left_rail',
            'header_style': 'elevated',
            'search_mode': 'floating_command_bar'},
  'regions': {'hero': {'visible': True,
                       'role': 'contextual_banner',
                       'height': 120,
                       'notes': 'Top summary context with strong hierarchy.'},
              'main': {'visible': True,
                       'role': 'primary_workspace',
                       'notes': 'Primary task surface and main data density.'},
              'side': {'visible': True,
                       'role': 'contextual_inspector',
                       'width': 300,
                       'deferred': True,
                       'notes': 'Inspector, secondary controls or commentary.'},
              'status': {'visible': True,
                         'role': 'runtime_feedback',
                         'height': 32,
                         'notes': 'Low-noise runtime hints and health.'},
              'overlay': {'visible': True,
                          'role': 'command_palette',
                          'notes': 'Reserved for structured overlays and palette interactions.'}},
  'surfaces': [{'id': 'hero_summary',
                'type': 'hero_banner',
                'region': 'hero',
                'title': 'Asset Browser Glass',
                'subtitle': 'Gallery and metadata browser',
                'variant': 'hero_banner',
                'priority': 10,
                'stretch': 0,
                'min_height': 120,
                'states': {'loading': 'shimmer_soft',
                           'empty': 'illustration_message',
                           'error': 'inline_panel'},
                'items': ['Latency 38ms', 'Healthy 99.96%', 'Focus lane active', 'Policy clean'],
                'metadata': {'eyebrow': 'FOUNDATION RECIPES',
                             'description': 'A premium asset browser recipe for browsing, previewing and '
                                            'inspecting media, resources or entities with a gallery-ready '
                                            'main surface and clean side metadata.',
                             'hero_metrics': ['throughput', 'health', 'focus', 'flags']}},
               {'id': 'primary_tabs',
                'type': 'tab_group',
                'region': 'main',
                'title': 'Workspace contexts',
                'subtitle': 'Primary contexts switch without changing shell ownership.',
                'variant': 'segmented_lux',
                'priority': 20,
                'stretch': 1,
                'tabs': [{'id': 'work',
                          'title': 'Work',
                          'content': 'main_grid',
                          'lazy': False,
                          'status': 'active'},
                         {'id': 'metrics',
                          'title': 'Metrics',
                          'content': 'signal_chart',
                          'lazy': True,
                          'status': 'standby'},
                         {'id': 'notes',
                          'title': 'Notes',
                          'content': 'activity_surface',
                          'lazy': True,
                          'status': 'standby'},
                         {'id': 'collections',
                          'title': 'Collections',
                          'content': 'activity_surface',
                          'lazy': True,
                          'status': 'standby'}],
                'metadata': {'tab_density': 'comfortable', 'tab_variant': 'glass'}},
               {'id': 'main_grid',
                'type': 'data_grid',
                'region': 'main',
                'title': 'Asset gallery',
                'subtitle': 'Main working surface with strong hierarchy and safe resize behavior.',
                'variant': 'premium_table',
                'priority': 30,
                'stretch': 3,
                'min_width': 480,
                'min_height': 260,
                'preferred_ratio': 0.68,
                'states': {'loading': 'skeleton_rows',
                           'empty': 'illustration_minimal',
                           'error': 'inline_diagnostic',
                           'deferred': 'deferred_notice'},
                'metadata': {'columns': ['Name', 'State', 'Owner', 'Latency', 'Updated'],
                             'sample_rows': 12,
                             'row_hover': 'glow_soft',
                             'header_tone': 'muted_raised'}},
               {'id': 'signal_chart',
                'type': 'chart',
                'region': 'main',
                'title': 'Distribution by type',
                'subtitle': 'Signal visualization kept inside a governed surface host.',
                'variant': 'signal_chart',
                'priority': 40,
                'stretch': 2,
                'lazy': True,
                'min_height': 220,
                'states': {'loading': 'line_skeleton',
                           'empty': 'chart_empty_notice',
                           'error': 'inline_diagnostic'},
                'metadata': {'engine': 'pyqtgraph',
                             'kind': 'line_area',
                             'legend': True,
                             'grid_visibility': 'low'}},
               {'id': 'activity_surface',
                'type': 'activity_feed',
                'region': 'main',
                'title': 'Activity and notes',
                'subtitle': 'Event stream, notes or narrative trace without escaping the recipe system.',
                'variant': 'activity_stream',
                'priority': 50,
                'stretch': 1,
                'lazy': True,
                'states': {'loading': 'skeleton_lines', 'empty': 'quiet_zero_state', 'error': 'inline_panel'},
                'items': ['Health stable',
                          'Filter changed',
                          'Layout restored',
                          'Pinned selection updated',
                          'Policy re-evaluated']},
               {'id': 'side_inspector',
                'type': 'inspector_panel',
                'region': 'side',
                'title': 'Asset metadata',
                'subtitle': 'Detail panel with structured sections and sticky actions.',
                'variant': 'layered_form',
                'priority': 25,
                'stretch': 2,
                'deferred': True,
                'min_width': 300,
                'states': {'loading': 'skeleton_form',
                           'empty': 'selection_zero_state',
                           'error': 'inline_panel',
                           'deferred': 'deferred_notice'},
                'metadata': {'sections': ['Summary', 'Attributes', 'Actions', 'Diagnostics'],
                             'sticky_actions': True,
                             'section_dividers': 'soft'}},
               {'id': 'status_surface',
                'type': 'entity_summary',
                'region': 'status',
                'title': 'Runtime health',
                'subtitle': 'Low-noise health bar for layout, theme, motion and state.',
                'variant': 'glass_metric',
                'priority': 80,
                'stretch': 0,
                'states': {'ready': 'status_inline'},
                'items': ['Theme locked', 'Motion synced', 'Layout contract ok', 'State clean']}],
  'behavior': {'layouts': {'default': 'inspect',
                           'presets': ['focus', 'inspect', 'wallboard'],
                           'persistent': True},
               'visibility': {'by_role': True, 'by_mode': True, 'by_flags': True},
               'performance': {'lazy_tabs': True, 'deferred_panels': True, 'chart_throttle_ms': 120},
               'shortcuts': ['Ctrl+K command palette',
                             'Ctrl+1 work',
                             'Ctrl+2 metrics',
                             'Ctrl+Shift+I inspector'],
               'command_palette': True},
  'data': {'sources': [{'id': 'primary_table', 'kind': 'table', 'notes': 'Main operational rows.'},
                       {'id': 'selected_entity', 'kind': 'entity', 'notes': 'Inspector detail.'},
                       {'id': 'signal_series', 'kind': 'timeseries', 'notes': 'Metrics and trend line.'}],
           'ui_states': {'loading': {'treatment': 'shimmer_soft', 'blocking': False},
                         'empty': {'treatment': 'illustration_message', 'tone': 'elegant'},
                         'error': {'treatment': 'inline_diagnostic', 'recover_actions': ['retry', 'inspect']},
                         'stale': {'treatment': 'subtle_badge'}}},
  'quality': {'profile': 'strict',
              'beauty_checks': {'no_inline_colors': True,
                                'no_unstyled_widgets': True,
                                'spacing_scale_enforced': True,
                                'icon_family_enforced': True,
                                'motion_profile_enforced': True,
                                'layout_contract_required': True,
                                'states_required': True},
              'render_checks': {'theme_switch_test': True,
                                'compact_mode_test': True,
                                'empty_state_test': True,
                                'error_state_test': True,
                                'layout_restore_test': True,
                                'screenshot_baselines': True},
              'notes': 'Foundation recipes are expected to stay premium while preserving deterministic '
                       'layout behavior.'},
  'variants': [{'id': 'compact_shift',
                'label': 'Compact shift',
                'description': 'Tighter density and lower ornament for long sessions.',
                'overrides': {'experience': {'density': 'compact', 'motion_profile': 'operator_tight'},
                              'behavior': {'layouts': {'default': 'focus'}}}},
               {'id': 'review_mode',
                'label': 'Review mode',
                'description': 'Airier review stance with larger hero, calmer chart, and more side detail.',
                'overrides': {'experience': {'density': 'comfortable', 'motion_profile': 'subtle'},
                              'regions': {'side': {'width': 340}},
                              'behavior': {'layouts': {'default': 'inspect'}}}}]},
 {'meta': {'id': 'foundation.timeline_review',
           'title': 'Timeline Review',
           'subtitle': 'Narrative event review shell',
           'description': 'An editorial timeline review recipe that keeps logs, notes and event detail '
                          'elegant while preserving deterministic layout behavior and safe tab/page '
                          'ownership.',
           'category': 'Foundation Recipes',
           'status': 'stable',
           'tags': ['foundation', 'timeline', 'review', 'editorial'],
           'best_for': 'Timelines, audits and activity narrative reviews.',
           'use_when': 'you want something readable, premium and less harsh than operator mode.',
           'sort_order': 760,
           'icon_name': 'clock',
           'mood': 'editorial',
           'audience': 'reviewer'},
  'experience': {'beauty_profile': 'editorial_dashboard',
                 'color_story': 'pearl_azure',
                 'motion_profile': 'subtle',
                 'layout_pack': 'editorial_dual',
                 'shell_pack': 'editorial_light',
                 'density': 'comfortable',
                 'visual_language': 'editorial_workstation',
                 'ornament': 'minimal',
                 'contrast': 'medium_high',
                 'notes': 'Timeline Review is tuned for reviewer work with editorial dashboard presence and '
                          'the pearl azure story.'},
  'shell': {'frameless': False,
            'translucent': False,
            'show_status_bar': True,
            'show_footer': False,
            'show_side': True,
            'window_radius': 14,
            'chrome_mode': 'paper',
            'navigation_model': 'left_rail',
            'header_style': 'elevated',
            'search_mode': 'floating_command_bar'},
  'regions': {'hero': {'visible': True,
                       'role': 'contextual_banner',
                       'height': 136,
                       'notes': 'Top summary context with strong hierarchy.'},
              'main': {'visible': True,
                       'role': 'primary_workspace',
                       'notes': 'Primary task surface and main data density.'},
              'side': {'visible': True,
                       'role': 'contextual_inspector',
                       'width': 320,
                       'deferred': True,
                       'notes': 'Inspector, secondary controls or commentary.'},
              'status': {'visible': True,
                         'role': 'runtime_feedback',
                         'height': 32,
                         'notes': 'Low-noise runtime hints and health.'},
              'overlay': {'visible': True,
                          'role': 'command_palette',
                          'notes': 'Reserved for structured overlays and palette interactions.'}},
  'surfaces': [{'id': 'hero_summary',
                'type': 'hero_banner',
                'region': 'hero',
                'title': 'Timeline Review',
                'subtitle': 'Narrative event review shell',
                'variant': 'hero_banner',
                'priority': 10,
                'stretch': 0,
                'min_height': 136,
                'states': {'loading': 'shimmer_soft',
                           'empty': 'illustration_message',
                           'error': 'inline_panel'},
                'items': ['Latency 38ms', 'Healthy 99.96%', 'Focus lane active', 'Policy clean'],
                'metadata': {'eyebrow': 'FOUNDATION RECIPES',
                             'description': 'An editorial timeline review recipe that keeps logs, notes and '
                                            'event detail elegant while preserving deterministic layout '
                                            'behavior and safe tab/page ownership.',
                             'hero_metrics': ['throughput', 'health', 'focus', 'flags']}},
               {'id': 'primary_tabs',
                'type': 'tab_group',
                'region': 'main',
                'title': 'Workspace contexts',
                'subtitle': 'Primary contexts switch without changing shell ownership.',
                'variant': 'segmented_lux',
                'priority': 20,
                'stretch': 1,
                'tabs': [{'id': 'work',
                          'title': 'Work',
                          'content': 'main_grid',
                          'lazy': False,
                          'status': 'active'},
                         {'id': 'metrics',
                          'title': 'Metrics',
                          'content': 'signal_chart',
                          'lazy': True,
                          'status': 'standby'},
                         {'id': 'notes',
                          'title': 'Notes',
                          'content': 'activity_surface',
                          'lazy': True,
                          'status': 'standby'},
                         {'id': 'annotations',
                          'title': 'Annotations',
                          'content': 'activity_surface',
                          'lazy': True,
                          'status': 'standby'}],
                'metadata': {'tab_density': 'comfortable', 'tab_variant': 'glass'}},
               {'id': 'main_grid',
                'type': 'data_grid',
                'region': 'main',
                'title': 'Event narrative',
                'subtitle': 'Main working surface with strong hierarchy and safe resize behavior.',
                'variant': 'premium_table',
                'priority': 30,
                'stretch': 3,
                'min_width': 520,
                'min_height': 260,
                'preferred_ratio': 0.62,
                'states': {'loading': 'skeleton_rows',
                           'empty': 'illustration_minimal',
                           'error': 'inline_diagnostic',
                           'deferred': 'deferred_notice'},
                'metadata': {'columns': ['Name', 'State', 'Owner', 'Latency', 'Updated'],
                             'sample_rows': 12,
                             'row_hover': 'glow_soft',
                             'header_tone': 'muted_raised'}},
               {'id': 'signal_chart',
                'type': 'chart',
                'region': 'main',
                'title': 'Cadence over time',
                'subtitle': 'Signal visualization kept inside a governed surface host.',
                'variant': 'signal_chart',
                'priority': 40,
                'stretch': 2,
                'lazy': True,
                'min_height': 220,
                'states': {'loading': 'line_skeleton',
                           'empty': 'chart_empty_notice',
                           'error': 'inline_diagnostic'},
                'metadata': {'engine': 'pyqtgraph',
                             'kind': 'line_area',
                             'legend': True,
                             'grid_visibility': 'low'}},
               {'id': 'activity_surface',
                'type': 'activity_feed',
                'region': 'main',
                'title': 'Activity and notes',
                'subtitle': 'Event stream, notes or narrative trace without escaping the recipe system.',
                'variant': 'activity_stream',
                'priority': 50,
                'stretch': 1,
                'lazy': True,
                'states': {'loading': 'skeleton_lines', 'empty': 'quiet_zero_state', 'error': 'inline_panel'},
                'items': ['Health stable',
                          'Filter changed',
                          'Layout restored',
                          'Pinned selection updated',
                          'Policy re-evaluated']},
               {'id': 'side_inspector',
                'type': 'inspector_panel',
                'region': 'side',
                'title': 'Selected moment',
                'subtitle': 'Detail panel with structured sections and sticky actions.',
                'variant': 'layered_form',
                'priority': 25,
                'stretch': 2,
                'deferred': True,
                'min_width': 320,
                'states': {'loading': 'skeleton_form',
                           'empty': 'selection_zero_state',
                           'error': 'inline_panel',
                           'deferred': 'deferred_notice'},
                'metadata': {'sections': ['Summary', 'Attributes', 'Actions', 'Diagnostics'],
                             'sticky_actions': True,
                             'section_dividers': 'soft'}},
               {'id': 'status_surface',
                'type': 'entity_summary',
                'region': 'status',
                'title': 'Runtime health',
                'subtitle': 'Low-noise health bar for layout, theme, motion and state.',
                'variant': 'glass_metric',
                'priority': 80,
                'stretch': 0,
                'states': {'ready': 'status_inline'},
                'items': ['Theme locked', 'Motion synced', 'Layout contract ok', 'State clean']}],
  'behavior': {'layouts': {'default': 'inspect',
                           'presets': ['focus', 'inspect', 'wallboard'],
                           'persistent': True},
               'visibility': {'by_role': True, 'by_mode': True, 'by_flags': True},
               'performance': {'lazy_tabs': True, 'deferred_panels': True, 'chart_throttle_ms': 120},
               'shortcuts': ['Ctrl+K command palette',
                             'Ctrl+1 work',
                             'Ctrl+2 metrics',
                             'Ctrl+Shift+I inspector'],
               'command_palette': True},
  'data': {'sources': [{'id': 'primary_table', 'kind': 'table', 'notes': 'Main operational rows.'},
                       {'id': 'selected_entity', 'kind': 'entity', 'notes': 'Inspector detail.'},
                       {'id': 'signal_series', 'kind': 'timeseries', 'notes': 'Metrics and trend line.'}],
           'ui_states': {'loading': {'treatment': 'shimmer_soft', 'blocking': False},
                         'empty': {'treatment': 'illustration_message', 'tone': 'elegant'},
                         'error': {'treatment': 'inline_diagnostic', 'recover_actions': ['retry', 'inspect']},
                         'stale': {'treatment': 'subtle_badge'}}},
  'quality': {'profile': 'strict',
              'beauty_checks': {'no_inline_colors': True,
                                'no_unstyled_widgets': True,
                                'spacing_scale_enforced': True,
                                'icon_family_enforced': True,
                                'motion_profile_enforced': True,
                                'layout_contract_required': True,
                                'states_required': True},
              'render_checks': {'theme_switch_test': True,
                                'compact_mode_test': True,
                                'empty_state_test': True,
                                'error_state_test': True,
                                'layout_restore_test': True,
                                'screenshot_baselines': True},
              'notes': 'Foundation recipes are expected to stay premium while preserving deterministic '
                       'layout behavior.'},
  'variants': [{'id': 'compact_shift',
                'label': 'Compact shift',
                'description': 'Tighter density and lower ornament for long sessions.',
                'overrides': {'experience': {'density': 'compact', 'motion_profile': 'operator_tight'},
                              'behavior': {'layouts': {'default': 'focus'}}}},
               {'id': 'review_mode',
                'label': 'Review mode',
                'description': 'Airier review stance with larger hero, calmer chart, and more side detail.',
                'overrides': {'experience': {'density': 'comfortable', 'motion_profile': 'subtle'},
                              'regions': {'side': {'width': 340}},
                              'behavior': {'layouts': {'default': 'inspect'}}}}]},
 {'meta': {'id': 'foundation.command_center_neon',
           'title': 'Command Center Neon',
           'subtitle': 'High-energy command room with discipline',
           'description': 'A controlled neon command center recipe that keeps the energy but avoids layout '
                          'chaos, dead buttons and free-floating nonsense.',
           'category': 'Foundation Recipes',
           'status': 'stable',
           'tags': ['foundation', 'command', 'neon', 'signal'],
           'best_for': 'Command centers, NOC-ish experiences and status-heavy live surfaces.',
           'use_when': 'you want drama without losing control of interaction and resize behavior.',
           'sort_order': 770,
           'icon_name': 'cpu',
           'mood': 'energetic',
           'audience': 'operator'},
  'experience': {'beauty_profile': 'neon_command',
                 'color_story': 'carbon_ruby',
                 'motion_profile': 'expressive_glass',
                 'layout_pack': 'balanced_split',
                 'shell_pack': 'ops_console',
                 'density': 'comfortable',
                 'visual_language': 'signal_command_room',
                 'ornament': 'selective',
                 'contrast': 'high',
                 'notes': 'Command Center Neon is tuned for operator work with neon command presence and the '
                          'carbon ruby story.'},
  'shell': {'frameless': True,
            'translucent': True,
            'show_status_bar': True,
            'show_footer': False,
            'show_side': True,
            'window_radius': 14,
            'chrome_mode': 'control_room',
            'navigation_model': 'left_rail',
            'header_style': 'elevated',
            'search_mode': 'floating_command_bar'},
  'regions': {'hero': {'visible': True,
                       'role': 'contextual_banner',
                       'height': 120,
                       'notes': 'Top summary context with strong hierarchy.'},
              'main': {'visible': True,
                       'role': 'primary_workspace',
                       'notes': 'Primary task surface and main data density.'},
              'side': {'visible': True,
                       'role': 'contextual_inspector',
                       'width': 300,
                       'deferred': True,
                       'notes': 'Inspector, secondary controls or commentary.'},
              'status': {'visible': True,
                         'role': 'runtime_feedback',
                         'height': 32,
                         'notes': 'Low-noise runtime hints and health.'},
              'overlay': {'visible': True,
                          'role': 'command_palette',
                          'notes': 'Reserved for structured overlays and palette interactions.'}},
  'surfaces': [{'id': 'hero_summary',
                'type': 'hero_banner',
                'region': 'hero',
                'title': 'Command Center Neon',
                'subtitle': 'High-energy command room with discipline',
                'variant': 'hero_banner',
                'priority': 10,
                'stretch': 0,
                'min_height': 120,
                'states': {'loading': 'shimmer_soft',
                           'empty': 'illustration_message',
                           'error': 'inline_panel'},
                'items': ['Latency 38ms', 'Healthy 99.96%', 'Focus lane active', 'Policy clean'],
                'metadata': {'eyebrow': 'FOUNDATION RECIPES',
                             'description': 'A controlled neon command center recipe that keeps the energy '
                                            'but avoids layout chaos, dead buttons and free-floating '
                                            'nonsense.',
                             'hero_metrics': ['throughput', 'health', 'focus', 'flags']}},
               {'id': 'primary_tabs',
                'type': 'tab_group',
                'region': 'main',
                'title': 'Workspace contexts',
                'subtitle': 'Primary contexts switch without changing shell ownership.',
                'variant': 'segmented_lux',
                'priority': 20,
                'stretch': 1,
                'tabs': [{'id': 'work',
                          'title': 'Work',
                          'content': 'main_grid',
                          'lazy': False,
                          'status': 'active'},
                         {'id': 'metrics',
                          'title': 'Metrics',
                          'content': 'signal_chart',
                          'lazy': True,
                          'status': 'standby'},
                         {'id': 'notes',
                          'title': 'Notes',
                          'content': 'activity_surface',
                          'lazy': True,
                          'status': 'standby'},
                         {'id': 'routes',
                          'title': 'Routes',
                          'content': 'activity_surface',
                          'lazy': True,
                          'status': 'standby'}],
                'metadata': {'tab_density': 'comfortable', 'tab_variant': 'glass'}},
               {'id': 'main_grid',
                'type': 'data_grid',
                'region': 'main',
                'title': 'Live command grid',
                'subtitle': 'Main working surface with strong hierarchy and safe resize behavior.',
                'variant': 'premium_table',
                'priority': 30,
                'stretch': 3,
                'min_width': 480,
                'min_height': 260,
                'preferred_ratio': 0.68,
                'states': {'loading': 'skeleton_rows',
                           'empty': 'illustration_minimal',
                           'error': 'inline_diagnostic',
                           'deferred': 'deferred_notice'},
                'metadata': {'columns': ['Name', 'State', 'Owner', 'Latency', 'Updated'],
                             'sample_rows': 12,
                             'row_hover': 'glow_soft',
                             'header_tone': 'muted_raised'}},
               {'id': 'signal_chart',
                'type': 'chart',
                'region': 'main',
                'title': 'Signal spikes',
                'subtitle': 'Signal visualization kept inside a governed surface host.',
                'variant': 'signal_chart',
                'priority': 40,
                'stretch': 2,
                'lazy': True,
                'min_height': 220,
                'states': {'loading': 'line_skeleton',
                           'empty': 'chart_empty_notice',
                           'error': 'inline_diagnostic'},
                'metadata': {'engine': 'pyqtgraph',
                             'kind': 'line_area',
                             'legend': True,
                             'grid_visibility': 'low'}},
               {'id': 'activity_surface',
                'type': 'activity_feed',
                'region': 'main',
                'title': 'Activity and notes',
                'subtitle': 'Event stream, notes or narrative trace without escaping the recipe system.',
                'variant': 'activity_stream',
                'priority': 50,
                'stretch': 1,
                'lazy': True,
                'states': {'loading': 'skeleton_lines', 'empty': 'quiet_zero_state', 'error': 'inline_panel'},
                'items': ['Health stable',
                          'Filter changed',
                          'Layout restored',
                          'Pinned selection updated',
                          'Policy re-evaluated']},
               {'id': 'side_inspector',
                'type': 'inspector_panel',
                'region': 'side',
                'title': 'Command inspector',
                'subtitle': 'Detail panel with structured sections and sticky actions.',
                'variant': 'layered_form',
                'priority': 25,
                'stretch': 2,
                'deferred': True,
                'min_width': 300,
                'states': {'loading': 'skeleton_form',
                           'empty': 'selection_zero_state',
                           'error': 'inline_panel',
                           'deferred': 'deferred_notice'},
                'metadata': {'sections': ['Summary', 'Attributes', 'Actions', 'Diagnostics'],
                             'sticky_actions': True,
                             'section_dividers': 'soft'}},
               {'id': 'status_surface',
                'type': 'entity_summary',
                'region': 'status',
                'title': 'Runtime health',
                'subtitle': 'Low-noise health bar for layout, theme, motion and state.',
                'variant': 'glass_metric',
                'priority': 80,
                'stretch': 0,
                'states': {'ready': 'status_inline'},
                'items': ['Theme locked', 'Motion synced', 'Layout contract ok', 'State clean']}],
  'behavior': {'layouts': {'default': 'inspect',
                           'presets': ['focus', 'inspect', 'wallboard'],
                           'persistent': True},
               'visibility': {'by_role': True, 'by_mode': True, 'by_flags': True},
               'performance': {'lazy_tabs': True, 'deferred_panels': True, 'chart_throttle_ms': 120},
               'shortcuts': ['Ctrl+K command palette',
                             'Ctrl+1 work',
                             'Ctrl+2 metrics',
                             'Ctrl+Shift+I inspector'],
               'command_palette': True},
  'data': {'sources': [{'id': 'primary_table', 'kind': 'table', 'notes': 'Main operational rows.'},
                       {'id': 'selected_entity', 'kind': 'entity', 'notes': 'Inspector detail.'},
                       {'id': 'signal_series', 'kind': 'timeseries', 'notes': 'Metrics and trend line.'}],
           'ui_states': {'loading': {'treatment': 'shimmer_soft', 'blocking': False},
                         'empty': {'treatment': 'illustration_message', 'tone': 'elegant'},
                         'error': {'treatment': 'inline_diagnostic', 'recover_actions': ['retry', 'inspect']},
                         'stale': {'treatment': 'subtle_badge'}}},
  'quality': {'profile': 'strict',
              'beauty_checks': {'no_inline_colors': True,
                                'no_unstyled_widgets': True,
                                'spacing_scale_enforced': True,
                                'icon_family_enforced': True,
                                'motion_profile_enforced': True,
                                'layout_contract_required': True,
                                'states_required': True},
              'render_checks': {'theme_switch_test': True,
                                'compact_mode_test': True,
                                'empty_state_test': True,
                                'error_state_test': True,
                                'layout_restore_test': True,
                                'screenshot_baselines': True},
              'notes': 'Foundation recipes are expected to stay premium while preserving deterministic '
                       'layout behavior.'},
  'variants': [{'id': 'compact_shift',
                'label': 'Compact shift',
                'description': 'Tighter density and lower ornament for long sessions.',
                'overrides': {'experience': {'density': 'compact', 'motion_profile': 'operator_tight'},
                              'behavior': {'layouts': {'default': 'focus'}}}},
               {'id': 'review_mode',
                'label': 'Review mode',
                'description': 'Airier review stance with larger hero, calmer chart, and more side detail.',
                'overrides': {'experience': {'density': 'comfortable', 'motion_profile': 'subtle'},
                              'regions': {'side': {'width': 340}},
                              'behavior': {'layouts': {'default': 'inspect'}}}}]})


__all__ = [
    "FOUNDATION_SCHEMA_VERSION",
    "FOUNDATION_CATALOG_CATEGORY",
    "BEAUTY_PROFILES",
    "COLOR_STORIES",
    "MOTION_PROFILES",
    "LAYOUT_PACKS",
    "SHELL_PACKS",
    "SURFACE_VARIANTS",
    "QUALITY_PROFILES",
    "RECIPE_SCHEMA",
    "LayoutContract",
    "SurfaceStatePolicy",
    "FoundryTabDefinition",
    "FoundrySurfaceDefinition",
    "GlassFoundryVariant",
    "GlassFoundryRecipe",
    "GlassFoundryRegistrySnapshot",
    "FoundrySurfaceHost",
    "FoundryPageHost",
    "FoundryContractSplitter",
    "FoundryRuntimeState",
    "get_foundry_schema",
    "validate_foundry_recipe",
    "register_foundry_recipe",
    "register_foundry_theme_pack",
    "register_foundry_presets",
    "register_builtin_foundry_foundation",
    "list_beauty_profiles",
    "list_color_stories",
    "list_motion_profiles",
    "list_layout_packs",
    "list_shell_packs",
    "list_foundry_recipes",
    "get_foundry_recipe",
    "foundry_registry_snapshot",
    "build_foundry_foundation",
    "build_foundry_preview",
]
