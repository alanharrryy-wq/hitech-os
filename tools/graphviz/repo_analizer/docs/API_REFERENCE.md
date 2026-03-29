# API Reference

## Event Bus

### Class: `EventBus`

**Module**: `app.gui_qt.event_bus`

Lightweight publish-subscribe event system.

#### Methods

```python
def subscribe(event: str, handler: Callable) -> Callable
```
Subscribe to an event.

- **Parameters**:
  - `event` (str): Event name
  - `handler` (Callable): Callback function that takes payload
- **Returns**: Unsubscribe function
- **Example**:
  ```python
  unsub = bus.subscribe('file_selected', on_file)
  unsub()  # Unsubscribe
  ```

```python
def publish(event: str, payload: Any = None) -> None
```
Publish an event to all subscribers.

- **Parameters**:
  - `event` (str): Event name
  - `payload` (Any): Event payload (any type)
- **Example**:
  ```python
  bus.publish('file_selected', {'relpath': 'src/main.py', 'line': 10})
  ```

```python
def has_subscribers(event: str) -> bool
```
Check if event has subscribers.

- **Returns**: True if subscribers exist
- **Example**:
  ```python
  if bus.has_subscribers('my_event'):
      bus.publish('my_event', data)
  ```

```python
def clear() -> None
```
Clear all subscribers and history.

```python
def get_history(event: str | None = None) -> List[Tuple[str, Any]]
```
Get event publication history.

- **Parameters**:
  - `event` (str, optional): Filter by event name
- **Returns**: List of (event_name, payload) tuples
- **Example**:
  ```python
  all_events = bus.get_history()
  file_events = bus.get_history('file_selected')
  ```

### Class: `Events`

Standard event names.

```python
# Index events
Events.INDEX_STARTED
Events.INDEX_COMPLETED
Events.INDEX_FAILED

# Tree events
Events.TREE_REBUILT
Events.FILE_SELECTED
Events.TREE_FILTER_CHANGED

# Search events
Events.SEARCH_STARTED
Events.SEARCH_COMPLETED
Events.SEARCH_FAILED
Events.SEARCH_CLEARED

# Preview events
Events.PREVIEW_OPENED
Events.PREVIEW_CLOSED

# Navigation events
Events.NAVIGATION_CHANGED
Events.NAVIGATION_BACK
Events.NAVIGATION_FORWARD

# Layout events
Events.LAYOUT_CHANGED
Events.LAYOUT_SAVED

# Theme events
Events.SKIN_CHANGED

# Bookmark events
Events.BOOKMARK_ADDED
Events.BOOKMARK_REMOVED
Events.BOOKMARKS_REFRESHED

# Message events
Events.ERROR_OCCURRED
Events.STATUS_CHANGED
```

---

## Command Dispatcher

### Class: `Command` (Abstract)

Base class for all commands.

**Module**: `app.gui_qt.command_dispatcher`

#### Methods

```python
@abstractmethod
def execute(self, *args: Any, **kwargs: Any) -> Any
```
Execute the command.

- **Returns**: Result from command execution
- **Raises**: Exception for errors

```python
def can_execute(self) -> bool
```
Check if command can execute.

- **Returns**: True if executable
- **Default**: True
- **Override**: Add validation logic

```python
def on_execute_error(self, error: Exception) -> None
```
Handle execution errors.

- **Default**: Prints error message
- **Override**: Add custom error handling

#### Example

```python
from app.gui_qt.command_dispatcher import Command

class MyCommand(Command):
    def __init__(self, service):
        self.service = service
    
    def can_execute(self) -> bool:
        return self.service is not None
    
    def execute(self, param) -> str:
        return self.service.process(param)
    
    def on_execute_error(self, error):
        print(f"My error handler: {error}")
```

### Class: `CommandDispatcher`

Central command registration and execution.

**Module**: `app.gui_qt.command_dispatcher`

#### Methods

```python
def register(name: str, command: Command) -> None
```
Register a command.

- **Parameters**:
  - `name` (str): Command identifier
  - `command` (Command): Command instance
- **Raises**: ValueError if already registered
- **Example**:
  ```python
  dispatcher.register('open_file', OpenFileCommand(preview))
  ```

```python
def unregister(name: str) -> None
```
Unregister a command.

```python
def has(name: str) -> bool
```
Check if command exists.

- **Returns**: True if registered

```python
def execute(name: str, *args, **kwargs) -> Any
```
Execute a command.

- **Parameters**:
  - `name` (str): Command identifier
  - `*args`: Positional arguments for command
  - `**kwargs`: Keyword arguments for command
- **Returns**: Command result
- **Raises**: ValueError if not found or cannot execute
- **Example**:
  ```python
  dispatcher.execute('open_file', relpath='src/main.py', line=10)
  ```

```python
def on_before_execute(handler: Callable) -> Callable
```
Register handler before command execution.

- **Parameters**:
  - `handler` (Callable): Called(command_name, args, kwargs)
- **Returns**: Unregister function

```python
def on_after_execute(handler: Callable) -> Callable
```
Register handler after command execution.

- **Parameters**:
  - `handler` (Callable): Called(command_name, result)
- **Returns**: Unregister function

```python
def get_command(name: str) -> Optional[Command]
```
Get a command instance.

- **Returns**: Command or None

```python
def get_history(name: str | None = None) -> List[Tuple[str, Any, Any]]
```
Get execution history.

- **Returns**: List of (command_name, (args, kwargs), result)

```python
def clear() -> None
```
Clear all commands and history.

#### Example

```python
dispatcher = CommandDispatcher()
dispatcher.register('my_cmd', MyCommand())
dispatcher.on_before_execute(print_before)
dispatcher.on_after_execute(print_after)
dispatcher.execute('my_cmd', arg1='value')
```

---

## Service Container

### Class: `ServiceContainer`

Dependency injection container.

**Module**: `app.gui_qt.services.service_container`

#### Methods

```python
def register(name: str, service: Any) -> None
```
Register a singleton service.

- **Parameters**:
  - `name` (str): Service identifier
  - `service` (Any): Service instance
- **Raises**: ValueError if already registered

```python
def register_factory(name: str, factory: Callable) -> None
```
Register a factory function.

- **Creates new instance** each time service is requested
- **Parameters**:
  - `name` (str): Service identifier
  - `factory` (Callable): Factory function

```python
def register_singleton_factory(name: str, factory: Callable) -> None
```
Register a singleton factory.

- **Creates instance once**, then caches it
- **Parameters**:
  - `name` (str): Service identifier
  - `factory` (Callable): Factory function

```python
def get(name: str) -> Optional[Any]
```
Get a service.

- **Returns**: Service instance or None

```python
def has(name: str) -> bool
```
Check if service is registered.

```python
def unregister(name: str) -> None
```
Unregister a service.

```python
def clear() -> None
```
Clear all services.

```python
def get_all_names() -> List[str]
```
Get all registered service names.

#### Example

```python
container = ServiceContainer()

# Singleton
container.register('config', config_obj)

# Factory (new instance each time)
container.register_factory('worker', lambda: Worker())

# Singleton Factory (new instance once, then cached)
container.register_singleton_factory('db', create_database)

# Get service
config = container.get('config')
worker = container.get('worker')
db = container.get('db')
```

---

## Plugin System

### Class: `Plugin` (Abstract)

Base class for plugins.

**Module**: `app.gui_qt.plugins.plugin_base`

#### Attributes

```python
name: str = 'unknown'        # Unique plugin identifier
version: str = '0.1.0'       # Plugin version
description: str = ''        # Plugin description
author: str = ''             # Plugin author
enabled: bool = True         # Whether plugin is enabled
```

#### Methods

```python
@abstractmethod
def initialize(self, context: PluginContext) -> None
```
Initialize the plugin.

- **Required**: Must be implemented
- **Called**: When plugin is loaded
- **Parameters**:
  - `context` (PluginContext): Access to infrastructure

```python
def shutdown(self) -> None
```
Clean up when plugin unloads.

- **Default**: Auto-unsubscribe from events
- **Override**: Add custom cleanup

```python
def register_command(context, name: str, command: Command) -> None
```
Register a command.

```python
def subscribe_event(context, event: str, handler: Callable) -> None
```
Subscribe to an event.

```python
def emit_event(context, event: str, payload: Any = None) -> None
```
Emit an event.

#### Example

```python
from app.gui_qt.plugins import Plugin, PluginContext

class MyPlugin(Plugin):
    name = 'my_plugin'
    version = '1.0.0'
    description = 'Does something useful'
    author = 'Your Name'
    
    def initialize(self, context: PluginContext) -> None:
        self.register_command(context, 'my_cmd', MyCommand())
        self.subscribe_event(context, 'file_selected', self.on_file)
    
    def on_file(self, payload):
        print(payload)
    
    def shutdown(self):
        super().shutdown()  # Auto-unsubscribe
        # Custom cleanup
```

### Class: `PluginContext`

Context passed to plugins.

**Module**: `app.gui_qt.plugins.plugin_base`

#### Attributes

```python
event_bus: EventBus           # Event bus
dispatcher: CommandDispatcher # Command dispatcher
container: ServiceContainer   # Service container
```

#### Methods

```python
def get_service(name: str) -> Optional[Any]
```
Get a service from the container.

#### Example

```python
def initialize(self, context: PluginContext):
    # Access services
    main_window = context.get_service('main_window')
    backend = context.get_service('backend')
    settings = context.get_service('settings')
    
    # Access infrastructure
    context.event_bus.publish('my_event', data)
    context.dispatcher.execute('my_command', arg=value)
```

### Class: `PluginManager`

Loads and manages plugins.

**Module**: `app.gui_qt.plugins.plugin_manager`

#### Methods

```python
def load_plugin_from_file(filepath: str) -> Optional[str]
```
Load plugin from Python file.

- **Returns**: Plugin name if successful
- **Raises**: Exception if invalid

```python
def load_plugins_from_directory(directory: str) -> List[str]
```
Load all plugins from directory.

- **Returns**: List of loaded plugin names

```python
def initialize_plugin(name: str) -> bool
```
Initialize a plugin.

```python
def initialize_all() -> List[str]
```
Initialize all loaded plugins.

```python
def get_plugin(name: str) -> Optional[Plugin]
```
Get a plugin instance.

```python
def has_plugin(name: str) -> bool
```
Check if plugin is loaded.

```python
def shutdown_plugin(name: str) -> bool
```
Shutdown a plugin.

```python
def shutdown_all() -> None
```
Shutdown all plugins.

```python
def get_all_plugins() -> Dict[str, Plugin]
```
Get all loaded plugins.

```python
def get_enabled_plugins() -> Dict[str, Plugin]
```
Get all enabled plugins.

```python
def enable_plugin(name: str) -> bool
```
Enable a plugin.

```python
def disable_plugin(name: str) -> bool
```
Disable a plugin.

#### Example

```python
manager = PluginManager(bus, dispatcher, container)

# Load and initialize
manager.load_plugins_from_directory('plugins/')
manager.initialize_all()

# Manage
manager.disable_plugin('my_plugin')
manager.enable_plugin('my_plugin')

# Inspect
for name, plugin in manager.get_enabled_plugins().items():
    print(f"{name} v{plugin.version}")
```

---

## Built-in Commands

### `OpenFileCommand`

Open file for preview.

**Module**: `app.gui_qt.commands.open_file`

```python
dispatcher.execute('open_file', relpath='src/main.py', line=10)
```

### `ExecuteSearchCommand`

Run search operation.

**Module**: `app.gui_qt.commands.execute_search`

```python
dispatcher.execute('execute_search')
```

### `ExportResultsCommand`

Export search results.

**Module**: `app.gui_qt.commands.export_results`

```python
dispatcher.execute('export_results')
```

### `NavigateBackCommand`

Navigate to previous preview.

**Module**: `app.gui_qt.commands.navigate_back`

```python
dispatcher.execute('navigate_back')
```

### `NavigateForwardCommand`

Navigate to next preview.

**Module**: `app.gui_qt.commands.navigate_forward`

```python
dispatcher.execute('navigate_forward')
```

### `AddBookmarkCommand`

Add bookmark for current file.

**Module**: `app.gui_qt.commands.add_bookmark`

```python
dispatcher.execute('add_bookmark')
```

### `RemoveBookmarkCommand`

Remove selected bookmark.

**Module**: `app.gui_qt.commands.remove_bookmark`

```python
dispatcher.execute('remove_bookmark')
```

---

## Integration with Main Window

### Main Window Attributes

```python
class RepoAnalyzerMainWindow(QMainWindow):
    # Core infrastructure
    event_bus: EventBus
    command_dispatcher: CommandDispatcher
    service_container: ServiceContainer
    plugin_manager: PluginManager
    
    # Controllers
    toolbar_controller: ToolbarController
    tree_controller: TreeController
    search_controller: SearchController
    preview_controller: PreviewController
    navigation_controller: NavigationController
    layout_manager: LayoutManager
    dock_manager: DockManager
    
    # UI state
    index_data: dict
    search_results: list
```

### Usage

```python
app = QApplication([])
window = RepoAnalyzerMainWindow()

# Access infrastructure
window.event_bus.subscribe('file_selected', handler)
window.command_dispatcher.execute('open_file', relpath='src/main.py')
window.plugin_manager.get_enabled_plugins()

# All controllers available
window.tree_controller.rebuild_repo_tree()
window.search_controller.start_search()
```

---

## Error Handling

### EventBus

```python
# Errors in handlers don't break other handlers
bus.subscribe('event', handler_that_raises)  # OK, error is caught
bus.subscribe('event', handler_normal)       # Still called
```

### CommandDispatcher

```python
try:
    dispatcher.execute('command')
except ValueError as e:
    # Command not found or cannot execute
except Exception as e:
    # Command execution failed
```

### PluginManager

```python
# Plugin loading errors are logged
manager.load_plugins_from_directory('path')  # Continues on failure

# Plugin initialization errors are logged
manager.initialize_all()  # Continues on failure
```

---

## Configuration & Debugging

### Check Event Subscribers

```python
if window.event_bus.has_subscribers('file_selected'):
    print('File selected event has subscribers')
```

### Get Event History

```python
events = window.event_bus.get_history('search_completed')
for event_name, payload in events:
    print(f"{event_name}: {payload}")
```

### Get Command History

```python
commands = window.command_dispatcher.get_history('open_file')
for cmd_name, (args, kwargs), result in commands:
    print(f"{cmd_name}({args}, {kwargs}) = {result}")
```

### List Services

```python
services = window.service_container.get_all_names()
print("Available services:", services)
```

### List Plugins

```python
for name, plugin in window.plugin_manager.get_enabled_plugins().items():
    print(f"{name} v{plugin.version}: {plugin.description}")
```

---

## Performance Considerations

### Event Publishing: O(n)
- n = number of subscribers
- Typical: < 1ms for 10 subscribers

### Command Execution: O(1)
- Dictionary lookup
- Typical: < 1μs

### Service Lookup: O(1)
- Dictionary lookup
- Typical: < 1μs

### Plugin Loading: O(n)
- n = number of files in plugins directory
- Happens once at startup
- Typical: < 100ms for 50 plugins

---

## Compatibility

- **Python**: 3.10+
- **PySide6**: 6.0+
- **Existing Code**: 100% compatible, zero breaking changes
