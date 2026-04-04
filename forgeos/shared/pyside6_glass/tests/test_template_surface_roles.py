from PySide6.QtWidgets import QApplication

from pyside6_glass.template import GlassPanelTemplate


def _app():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_template_assigns_surface_roles_to_core_cards():
    _app()
    template = GlassPanelTemplate()
    assert template.cards.shell.property('visualRole') == 'shell'
    assert template.cards.hero.property('visualRole') == 'hero'
    assert template.cards.main.property('visualVariant') == 'panel'
    assert template.cards.side.property('visualVariant') == 'panel'
    assert template.cards.footer.property('visualEmphasis') == 'subtle'
    assert template.cards.footer.property('visualFxLevel') == 'soft'
    assert template.cards.status.property('visualFxLevel') == 'soft'
