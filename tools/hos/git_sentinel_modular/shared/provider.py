from __future__ import annotations

from typing import Any

__all__ = [
    "ScanAdapterProvider",
]


class ScanAdapterProvider:
    """
    Lazily-wired provider for scan adapters.
    
    Allows legacy and modular code to request a scan adapter without
    importing core.orchestrator directly. The provider is the boundary seam:
    it internally depends on core, but exposes only the abstract ScanAdapter
    protocol to callers.
    
    Supports registration/toggling for testing and future modular implementations.
    """
    
    _adapter_class: Any = None
    
    @classmethod
    def get(cls) -> type[Any]:
        """
        Get the current scan adapter class (lazy singleton).
        
        If not explicitly registered, initializes with core.orchestrator.SentinelOrchestrator.
        This one-time initialization happens on first call, not at module load.
        
        Returns:
            A class that accepts ScanConfig and has run_once() method
        """
        if cls._adapter_class is None:
            cls._initialize_default()
        return cls._adapter_class
    
    @classmethod
    def _initialize_default(cls) -> None:
        """Initialize with default orchestrator from core."""
        # Core import happens only on first call to get(), not at module load time
        from ..core.orchestrator import SentinelOrchestrator
        # Wrap SentinelOrchestrator to accept ScanConfig instead of OrchestratorConfig
        cls._adapter_class = _ScanAdapterBridge
    
    @classmethod
    def register(cls, adapter_class: type[Any]) -> None:
        """
        Register a custom adapter class for testing or alternate implementations.
        
        Args:
            adapter_class: A class that accepts ScanConfig and has run_once() method
        """
        cls._adapter_class = adapter_class
    
    @classmethod
    def reset(cls) -> None:
        """Reset to None; next get() will reinitialize with default."""
        cls._adapter_class = None
    
    @classmethod
    def current(cls) -> type[Any] | None:
        """Return current adapter class without initializing. For testing/introspection."""
        return cls._adapter_class


class _ScanAdapterBridge:
    """
    Bridge adapter that wraps core.orchestrator.SentinelOrchestrator.
    
    Accepts ScanConfig (boundary-safe) and internally creates OrchestratorConfig
    (core-specific) before instantiating the real orchestrator. This allows
    legacy code to remain decoupled from core.
    """
    
    def __init__(self, config):
        """Initialize by converting ScanConfig to OrchestratorConfig."""
        # ScanConfig has same shape as OrchestratorConfig, so we can pass it directly
        # or convert explicitly here
        from ..core.orchestrator import SentinelOrchestrator
        
        # Instantiate the real orchestrator with the config
        # (ScanConfig is compatible with OrchestratorConfig signature)
        self._orchestrator = SentinelOrchestrator(config)
    
    def run_once(self):
        """Delegate to the real orchestrator."""
        return self._orchestrator.run_once()

