# CODE_ATLAS_UI_MODULE_V03
"""Neutral default UI exports for Code Atlas.

Product-specific dialogs remain available only through their explicit module or
an adapter selected by the active product profile. Importing ``code_atlas.ui``
never selects a product adapter implicitly.
"""

from .generic_motor_hub import MotorHubDialog

__all__ = ["MotorHubDialog"]
