"""
Command System for encapsulating application actions.

Provides a command architecture where actions are represented as independent
command classes that can be executed through a central dispatcher.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, Optional


class Command(ABC):
    """
    Base class for all commands.

    Commands encapsulate an action and its execution logic. They receive
    all dependencies through the constructor.

    Example:
        class OpenFileCommand(Command):
            def __init__(self, preview_controller: PreviewController):
                self.preview_controller = preview_controller

            def execute(self, relpath: str, line: int = 0) -> Any:
                self.preview_controller.show_preview_for_relpath(relpath, line)
    """

    @abstractmethod
    def execute(self, *args: Any, **kwargs: Any) -> Any:
        """
        Execute the command.

        Returns:
            Optional result from command execution
        """
        pass

    def can_execute(self) -> bool:
        """
        Check if command can be executed in current state.

        Override to add validation logic.

        Returns:
            True if command can execute, False otherwise
        """
        return True

    def on_execute_error(self, error: Exception) -> None:
        """
        Handle execution errors.

        Override to add custom error handling.

        Args:
            error: The exception that occurred
        """
        print(f"Command execution failed: {error}")


class CommandDispatcher:
    """
    Central command dispatcher.

    Manages command registration and execution. Allows commands to be
    executed by name or by class reference.

    Example:
        dispatcher = CommandDispatcher()
        dispatcher.register('open_file', OpenFileCommand(preview_controller))
        result = dispatcher.execute('open_file', relpath='src/main.py', line=10)
    """

    def __init__(self) -> None:
        """Initialize the command dispatcher."""
        self._commands: Dict[str, Command] = {}
        self._command_history: list[tuple[str, Any, Any]] = []
        self._history_max_size = 100
        self._before_execute_handlers: list[Callable] = []
        self._after_execute_handlers: list[Callable] = []

    def register(self, name: str, command: Command) -> None:
        """
        Register a command.

        Args:
            name: Command identifier
            command: Command instance

        Raises:
            ValueError: If command name already registered
        """
        if name in self._commands:
            raise ValueError(f"Command '{name}' already registered")
        self._commands[name] = command

    def unregister(self, name: str) -> None:
        """
        Unregister a command.

        Args:
            name: Command identifier
        """
        if name in self._commands:
            del self._commands[name]

    def has(self, name: str) -> bool:
        """
        Check if command exists.

        Args:
            name: Command identifier

        Returns:
            True if command is registered
        """
        return name in self._commands

    def execute(self, name: str, *args: Any, **kwargs: Any) -> Any:
        """
        Execute a registered command.

        Args:
            name: Command identifier
            *args: Positional arguments to pass to command
            **kwargs: Keyword arguments to pass to command

        Returns:
            Result from command execution

        Raises:
            ValueError: If command not found
            Exception: Any exception raised by command execution
        """
        if name not in self._commands:
            raise ValueError(f"Command '{name}' not registered")

        command = self._commands[name]

        if not command.can_execute():
            raise RuntimeError(f"Command '{name}' cannot execute in current state")

        # Call before handlers
        for handler in self._before_execute_handlers:
            handler(name, args, kwargs)

        try:
            result = command.execute(*args, **kwargs)
            self._command_history.append((name, (args, kwargs), result))
            if len(self._command_history) > self._history_max_size:
                self._command_history.pop(0)

            # Call after handlers
            for handler in self._after_execute_handlers:
                handler(name, result)

            return result

        except Exception as e:
            command.on_execute_error(e)
            raise

    def on_before_execute(self, handler: Callable) -> Callable:
        """
        Register a handler to run before command execution.

        Args:
            handler: Callable(command_name, args, kwargs)

        Returns:
            Unregister function
        """
        self._before_execute_handlers.append(handler)

        def unregister() -> None:
            if handler in self._before_execute_handlers:
                self._before_execute_handlers.remove(handler)

        return unregister

    def on_after_execute(self, handler: Callable) -> Callable:
        """
        Register a handler to run after command execution.

        Args:
            handler: Callable(command_name, result)

        Returns:
            Unregister function
        """
        self._after_execute_handlers.append(handler)

        def unregister() -> None:
            if handler in self._after_execute_handlers:
                self._after_execute_handlers.remove(handler)

        return unregister

    def get_command(self, name: str) -> Optional[Command]:
        """
        Get a command instance.

        Args:
            name: Command identifier

        Returns:
            Command instance or None if not found
        """
        return self._commands.get(name)

    def get_history(self, name: str | None = None) -> list[tuple[str, Any, Any]]:
        """
        Get command execution history.

        Args:
            name: Optional command name to filter by

        Returns:
            List of (command_name, (args, kwargs), result) tuples
        """
        if name is None:
            return self._command_history.copy()
        return [(n, a, r) for n, a, r in self._command_history if n == name]

    def clear(self) -> None:
        """Clear all registered commands and history."""
        self._commands.clear()
        self._command_history.clear()
        self._before_execute_handlers.clear()
        self._after_execute_handlers.clear()
