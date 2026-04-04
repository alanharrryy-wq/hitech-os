from PySide6.QtWidgets import QApplication, QWidget

from pyside6_glass.visual_contracts import (
    VISUAL_EMPHASIS,
    VISUAL_FX_LEVELS,
    VISUAL_VARIANTS,
    VisualNodeSpec,
    normalize_visual_role,
    set_visual_properties,
    visual_signature,
)


def _app():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_visual_contract_enums_are_stable():
    assert 'panel' in VISUAL_VARIANTS
    assert 'high' in VISUAL_EMPHASIS
    assert 'rich' in VISUAL_FX_LEVELS


def test_visual_node_spec_normalizes_role_aliases():
    spec = VisualNodeSpec(role='metrics', variant='panel', emphasis='HIGH', fx_level='RICH').normalized()
    assert spec.role == 'panel_metrics'
    assert spec.variant == 'panel'
    assert spec.emphasis == 'high'
    assert spec.fx_level == 'rich'


def test_set_visual_properties_sets_widget_properties():
    _app()
    widget = QWidget()
    set_visual_properties(widget, role='summary', variant='panel', emphasis='critical', fx_level='soft')
    sig = visual_signature(widget)
    assert sig['role'] == 'panel_summary'
    assert sig['variant'] == 'panel'
    assert sig['emphasis'] == 'critical'
    assert sig['fx_level'] == 'soft'
    assert normalize_visual_role('workspace') == 'panel_workspace'
