import os
import unittest

from PySide6.QtWidgets import QApplication, QFrame, QVBoxLayout

from forgeos.shared.pyside6_glass.component_governance import mark_component, validate_widget_tree
from forgeos.shared.pyside6_glass.dashboard import DashboardDataSurface, DashboardQuerySpec


class ComponentGovernanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
        cls.app = QApplication.instance() or QApplication([])

    def test_validate_widget_tree_flags_unapproved_raw_data_widgets(self) -> None:
        from PySide6.QtWidgets import QTableWidget

        root = QFrame()
        layout = QVBoxLayout(root)
        table = QTableWidget(1, 1, root)
        layout.addWidget(table)
        issues = validate_widget_tree(root)
        self.assertTrue(any(item.code == 'raw_qt_surface' for item in issues))
        root.deleteLater()

    def test_dashboard_data_surface_marks_governed_components(self) -> None:
        surface = DashboardDataSurface(DashboardQuerySpec(provider_id='demo_status'))
        mark_component(surface, component_key='dashboard_data_surface')
        issues = validate_widget_tree(surface)
        self.assertEqual(issues, [])
        surface.deleteLater()


if __name__ == '__main__':
    unittest.main()
