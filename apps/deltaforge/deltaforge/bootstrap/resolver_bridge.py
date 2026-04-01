from __future__ import annotations

import inspect
from typing import Any



def resolve_workspace_facade(resolver: Any) -> Any:
    factory = getattr(resolver, 'create_workspace_facade', None)
    if callable(factory):
        return invoke_factory(factory)
    facade = getattr(resolver, 'workspace_facade', None)
    if facade is not None:
        return facade
    raise AttributeError('resolver must expose create_workspace_facade() or workspace_facade')



def resolve_command_controller(resolver: Any, workspace_facade: Any) -> Any:
    factory = getattr(resolver, 'create_command_controller', None)
    if callable(factory):
        return invoke_factory(factory, workspace_facade)
    controller = getattr(resolver, 'command_controller', None)
    if controller is not None:
        return controller
    raise AttributeError('resolver must expose create_command_controller(...) or command_controller')



def resolve_optional(resolver: Any, *names: str) -> Any | None:
    for name in names:
        member = getattr(resolver, name, None)
        if callable(member):
            return invoke_factory(member)
        if member is not None:
            return member
    return None



def invoke_factory(factory: Any, *preferred_args: Any) -> Any:
    try:
        signature = inspect.signature(factory)
    except (TypeError, ValueError):
        return factory(*preferred_args)

    parameters = tuple(signature.parameters.values())
    if not parameters:
        return factory()
    if any(parameter.kind is inspect.Parameter.VAR_POSITIONAL for parameter in parameters):
        return factory(*preferred_args)

    positional = [
        parameter
        for parameter in parameters
        if parameter.kind in (inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD)
    ]
    if not positional:
        return factory()
    return factory(*preferred_args[: len(positional)])
