from __future__ import annotations


class PyaError(Exception):
    """Base runtime error."""


class AdmissionError(PyaError):
    pass


class ContractError(PyaError):
    pass


class OwnershipError(PyaError):
    pass


class PipelineError(PyaError):
    pass


class EngineExecutionError(PyaError):
    pass
