from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
from typing import Any


_LITERAL_STYLESHEET_PATTERN = re.compile(r'setStyleSheet\(\s*[fFrRuUbB]*[\'"]')

STYLE_AUTHORITY_FILES = {
    'scene.py',
    '_template_shell_appearance.py',
}

ATLAS_AUTHORITY_FORBIDDEN = (
    r'from\s+\.[\w]*atlas_(?:styles|theme_bridge)\s+import',
    r'import\s+\.[\w]*atlas_(?:styles|theme_bridge)',
    r'build_stylesheet_exact_atlas\s*\(',
)

MICROAUTHORITY_RULES: dict[str, tuple[str, ...]] = {
    'controls.py': (
        r'_SHADOW_ALPHA_BY_VARIANT',
        r'\bshadow_blur\s*=',
        r'\bshadow_alpha\s*=',
    ),
    'icons.py': (
        r'QColor\(\s*246\s*,\s*248\s*,\s*252',
        r'QColor\(\s*255\s*,\s*255\s*,\s*255\s*,\s*108',
    ),
    'scene.py': (
        r'build_stylesheet_exact_atlas',
    ),
}

LOCAL_FINAL_TOKEN_FORBIDDEN_FILES = (
    'controls.py',
    '_template_helpers.py',
    '_template_shell_build.py',
    '_template_shell_appearance.py',
)

LOCAL_FINAL_TOKEN_PATTERN = re.compile(r'(?:#[0-9a-fA-F]{6}\b|rgba\(|QColor\()')


@dataclass(frozen=True, slots=True)
class ValidationIssue:
    code: str
    message: str
    path: str
    line: int | None = None
    severity: str = 'error'

    def to_dict(self) -> dict[str, Any]:
        return {
            'code': self.code,
            'message': self.message,
            'path': self.path,
            'line': self.line,
            'severity': self.severity,
        }


def _is_source_file(path: Path) -> bool:
    if path.suffix != '.py':
        return False
    normalized = str(path).replace('\\', '/').lower()
    for token in ('/__pycache__/', '/artifacts/', '/baselines/', '/tests/'):
        if token in normalized:
            return False
    return True


def _skip_literal_stylesheet_scan(path: Path) -> bool:
    normalized = str(path).replace('\\', '/').lower()
    for token in (
        '/examples_backup/',
        '/examples_backup_',
        '/docs/',
    ):
        if token in normalized:
            return True
    return False


def _scan_literal_stylesheets(package_root: Path) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    scan_excluded = {'validation.py', 'release_gate.py'}
    for path in package_root.rglob('*.py'):
        if not _is_source_file(path):
            continue
        normalized = str(path).replace('\\', '/').lower()
        if '/examples/' in normalized:
            continue
        if _skip_literal_stylesheet_scan(path):
            continue
        if path.name in scan_excluded:
            continue
        lines = path.read_text(encoding='utf-8').splitlines()
        for index, line in enumerate(lines, start=1):
            stripped = line.strip()
            if 'setStyleSheet(' not in stripped:
                continue
            if path.name not in STYLE_AUTHORITY_FILES:
                issues.append(
                    ValidationIssue(
                        code='set_stylesheet_outside_authority',
                        message='setStyleSheet detected outside official style authority modules',
                        path=str(path),
                        line=index,
                    )
                )
                continue
            if 'build_stylesheet(' in stripped:
                continue
            if _LITERAL_STYLESHEET_PATTERN.search(stripped):
                issues.append(
                    ValidationIssue(
                        code='hardcoded_stylesheet',
                        message='setStyleSheet literal detected outside governed stylesheet builders',
                        path=str(path),
                        line=index,
                    )
                )
    return issues


def _check_required_modules(package_root: Path) -> list[ValidationIssue]:
    required = [
        package_root / 'appearance' / 'intelligence.py',
        package_root / 'appearance' / 'levels.py',
        package_root / 'component_governance.py',
        package_root / 'rendering' / 'surface_renderer.py',
        package_root / 'visual_contracts.py',
    ]
    issues: list[ValidationIssue] = []
    for path in required:
        if not path.exists():
            issues.append(
                ValidationIssue(
                    code='missing_module',
                    message='required governance module missing',
                    path=str(path),
                )
            )
    return issues


def _check_visual_contract_markers(package_root: Path) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    template_path = package_root / 'template.py'
    surface_renderer_path = package_root / 'rendering' / 'surface_renderer.py'
    dashboard_path = package_root / 'dashboard.py'
    atlas_styles_path = package_root / 'atlas_styles.py'
    atlas_theme_bridge_path = package_root / 'atlas_theme_bridge.py'

    template_text = template_path.read_text(encoding='utf-8')
    if 'visualFxLevel' not in template_text:
        issues.append(
            ValidationIssue(
                code='missing_visual_fx_contract',
                message='template is missing visualFxLevel contract propagation',
                path=str(template_path),
            )
        )
    if "'low'" in template_text or '"low"' in template_text:
        issues.append(
            ValidationIssue(
                code='invalid_visual_emphasis',
                message="template contains unsupported 'low' emphasis token",
                path=str(template_path),
            )
        )

    renderer_text = surface_renderer_path.read_text(encoding='utf-8')
    if 'fx_level' not in renderer_text:
        issues.append(
            ValidationIssue(
                code='missing_fx_param',
                message='surface renderer is missing fx_level wiring',
                path=str(surface_renderer_path),
            )
        )

    dashboard_text = dashboard_path.read_text(encoding='utf-8')
    if 'resolve_chart_contract' not in dashboard_text:
        issues.append(
            ValidationIssue(
                code='missing_chart_registry_usage',
                message='dashboard surface does not enforce chart registry contract',
                path=str(dashboard_path),
            )
        )
    if 'mark_component(' not in dashboard_text:
        issues.append(
            ValidationIssue(
                code='missing_component_governance',
                message='dashboard surface is missing component governance hooks',
                path=str(dashboard_path),
            )
        )
    for token in ('DataState.LOADING', 'DataState.READY', 'DataState.EMPTY', 'DataState.ERROR', 'DataState.STALE'):
        if token not in dashboard_text:
            issues.append(
                ValidationIssue(
                    code='missing_data_state_rendering',
                    message=f'dashboard surface missing explicit data state handling: {token}',
                    path=str(dashboard_path),
                )
            )
    for legacy_path in (atlas_styles_path, atlas_theme_bridge_path):
        text = legacy_path.read_text(encoding='utf-8')
        if 'GlassWorkspaceRuntime' in text or 'AppearanceCoordinator' in text:
            issues.append(
                ValidationIssue(
                    code='legacy_shim_growth',
                    message='legacy atlas shim contains runtime/appearance authority logic',
                    path=str(legacy_path),
                )
            )
    return issues


def _check_legacy_authority(package_root: Path) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    scan_excluded = {'validation.py', 'release_gate.py'}
    for path in package_root.rglob('*.py'):
        if not _is_source_file(path):
            continue
        normalized = str(path).replace('\\', '/').lower()
        if '/examples/' in normalized or '/docs/' in normalized or '/tests/' in normalized:
            continue
        if path.name in scan_excluded:
            continue
        if path.name in {'atlas_styles.py', 'atlas_theme_bridge.py'}:
            continue
        text = path.read_text(encoding='utf-8', errors='replace')
        for pattern in ATLAS_AUTHORITY_FORBIDDEN:
            match = re.search(pattern, text, flags=re.IGNORECASE | re.MULTILINE)
            if match is None:
                continue
            if path.name == 'theme.py' and 'build_stylesheet_exact_atlas' in pattern:
                continue
            issues.append(
                ValidationIssue(
                    code='legacy_authority_path',
                    message='legacy Atlas authority found in productive path',
                    path=str(path),
                    line=text.count('\n', 0, match.start()) + 1,
                )
            )
    return issues


def _check_micro_authority(package_root: Path) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    for relative_path, patterns in MICROAUTHORITY_RULES.items():
        path = package_root / relative_path
        if not path.exists():
            continue
        text = path.read_text(encoding='utf-8', errors='replace')
        for pattern in patterns:
            match = re.search(pattern, text, flags=re.IGNORECASE | re.MULTILINE)
            if match is None:
                continue
            issues.append(
                ValidationIssue(
                    code='micro_visual_authority',
                    message=f'local visual authority pattern found: {pattern}',
                    path=str(path),
                    line=text.count('\n', 0, match.start()) + 1,
                )
            )
    for relative_path in LOCAL_FINAL_TOKEN_FORBIDDEN_FILES:
        path = package_root / relative_path
        if not path.exists():
            continue
        text = path.read_text(encoding='utf-8', errors='replace')
        match = LOCAL_FINAL_TOKEN_PATTERN.search(text)
        if match is None:
            continue
        issues.append(
            ValidationIssue(
                code='local_final_visual_token',
                message='final visual token found outside official materializers',
                path=str(path),
                line=text.count('\n', 0, match.start()) + 1,
            )
        )
    return issues


def run_validation(*, package_root: Path | None = None) -> dict[str, Any]:
    root = (package_root or Path(__file__).resolve().parent).resolve()
    issues: list[ValidationIssue] = []
    issues.extend(_check_required_modules(root))
    issues.extend(_check_visual_contract_markers(root))
    issues.extend(_check_legacy_authority(root))
    issues.extend(_check_micro_authority(root))
    issues.extend(_scan_literal_stylesheets(root))
    errors = [issue for issue in issues if issue.severity == 'error']
    return {
        'passed': len(errors) == 0,
        'issue_count': len(issues),
        'issues': [issue.to_dict() for issue in issues],
        'package_root': str(root),
    }


__all__ = ['ValidationIssue', 'run_validation']
