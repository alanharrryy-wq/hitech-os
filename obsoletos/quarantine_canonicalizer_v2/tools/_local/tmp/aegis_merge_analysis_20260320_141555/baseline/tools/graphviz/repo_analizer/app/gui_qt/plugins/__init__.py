"""Plugins package - extensible plugin system."""

from .plugin_base import Plugin, PluginContext
from .plugin_manager import PluginManager

__all__ = ['Plugin', 'PluginContext', 'PluginManager']
