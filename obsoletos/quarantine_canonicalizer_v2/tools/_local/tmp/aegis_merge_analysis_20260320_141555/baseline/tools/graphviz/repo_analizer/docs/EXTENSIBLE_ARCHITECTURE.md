# Extensible Architecture Guide

## Overview

The Repo Analyzer has been upgraded from a simple modular controller architecture into a professional extensible system with the following layers:

```
┌─────────────────────────────────────────────────────┐
│          Plugins (Dynamic Extensions)                │
├─────────────────────────────────────────────────────┤
│  ┌───────────────────────────────────────────────┐  │
│  │  Command System (Action Encapsulation)        │  │
│  │  - OpenFileCommand, ExecuteSearchCommand, etc │  │
│  ├───────────────────────────────────────────────┤  │
│  │  Event Bus (Loose Coupling)                   │  │
│  │  - FILE_SELECTED, SEARCH_COMPLETED, etc      │  │
│  ├───────────────────────────────────────────────┤  │
│  │  Service Container (Dependency Injection)     │  │
│  │  - Manages all singletons and factories       │  │
│  └───────────────────────────────────────────────┘  │
├─────────────────────────────────────────────────────┤
│     Controllers (Business Logic)                     │
│  - ToolbarController, TreeController, etc.         │
├─────────────────────────────────────────────────────┤
│     PySide6 (UI Framework)                          │
└─────────────────────────────────────────────────────┘
```

## Architecture Components

### 1. Event Bus (`event_bus.py`)

**Purpose**: Enable loosely-coupled communication between components.

**Key Features**:
- Publish-subscribe pattern
- Standard event names (Events class)
- Event history for debugging
- Safe error handling (one handler failure doesn't break others)

**Example**:
```python
from app.gui_qt.event_bus import EventBus, Events

bus = EventBus()

# Subscribe to events
bus.subscribe(Events.FILE_SELECTED, lambda payload: print(payload))

# Publish events
bus.publish(Events.FILE_SELECTED, {'relpath': 'src/main.py', 'line': 10})
```

**Standard Events**:
- `INDEX_STARTED`, `INDEX_COMPLETED`, `INDEX_FAILED` - Indexing lifecycle
- `TREE_REBUILT`, `FILE_SELECTED` - Tree interaction
- `SEARCH_STARTED`, `SEARCH_COMPLETED` - Search operations
- `PREVIEW_OPENED`, `PREVIEW_CLOSED` - Preview management
- `NAVIGATION_CHANGED`, `NAVIGATION_BACK`, `NAVIGATION_FORWARD` - Navigation
- `SKIN_CHANGED` - Theme switching
- `BOOKMARK_ADDED`, `BOOKMARK_REMOVED` - Bookmarks

### 2. Command System (`command_dispatcher.py`, `commands/`)

**Purpose**: Encapsulate actions as independent, injectable command objects.

**Key Features**:
- Base Command class with execute() and can_execute()
- Central CommandDispatcher for registration and execution
- Command history for debugging
- Before/after execution hooks

**Example**:
```python
from app.gui_qt.command_dispatcher import Command, CommandDispatcher
from app.gui_qt.commands import OpenFileCommand

# Create dispatcher
dispatcher = CommandDispatcher()

# Register command
dispatcher.register('open_file', OpenFileCommand(preview_controller))

# Execute by name
dispatcher.execute('open_file', relpath='src/main.py', line=10)

# Check if command can execute
if dispatcher.execute('navigate_back'):
    # Success
```

**Built-in Commands**:
- `open_file` - Open file in preview
- `execute_search` - Run search operation
- `export_results` - Export search results
- `navigate_back` - Go to previous preview
- `navigate_forward` - Go to next preview
- `add_bookmark` - Bookmark current file
- `remove_bookmark` - Remove selected bookmark

### 3. Service Container (`services/service_container.py`)

**Purpose**: Manage dependencies and provide them to components that need them.

**Key Features**:
- Register singletons and factories
- Singleton factories (created once, cached)
- Easy service lookup
- Clear dependency specification

**Example**:
```python
from app.gui_qt.services import ServiceContainer
from app.gui_qt.event_bus import EventBus

container = ServiceContainer()

# Register singleton
container.register('event_bus', EventBus())

# Register factory (creates new instance each time)
container.register_factory('new_worker', lambda: IndexWorker())

# Register singleton factory (creates once, caches)
container.register_singleton_factory('config', load_config)

# Get service
bus = container.get('event_bus')
```

**Registered Services**:
- `event_bus` - Application event bus
- `command_dispatcher` - Command dispatcher
- `backend` - AnalyzerBackend instance
- `settings` - QSettings instance
- `main_window` - Main window reference
- All controllers (toolbar, tree, search, preview, etc.)

### 4. Plugin System (`plugins/`)

**Purpose**: Allow dynamic extension without modifying core code.

**Key Components**:

#### Plugin Base Class
```python
from app.gui_qt.plugins import Plugin, PluginContext

class MyPlugin(Plugin):
    name = 'my_plugin'
    version = '1.0.0'
    description = 'Does something useful'
    author = 'Your Name'
    
    def initialize(self, context: PluginContext) -> None:
        # Register commands
        self.register_command(context, 'my_command', MyCommand())
        
        # Subscribe to events
        self.subscribe_event(context, 'file_selected', self.on_file_selected)
    
    def on_file_selected(self, payload):
        print(f"File selected: {payload}")
    
    def shutdown(self) -> None:
        # Clean up resources
        super().shutdown()
```

#### Plugin Manager
```python
from app.gui_qt.plugins import PluginManager

manager = PluginManager(event_bus, dispatcher, container)

# Load plugins
manager.load_plugins_from_directory('path/to/plugins')
manager.initialize_all()

# Manage plugins
manager.disable_plugin('my_plugin')
manager.get_plugin('my_plugin').get_statistics()
```

**Plugin Capabilities**:
- Register commands
- Subscribe to events
- Access application services
- Manage lifecycle (initialize, shutdown)
- Enable/disable at runtime

## Integration Points

### How Components Work Together

```
User Action (Click button)
    ↓
[UI Signal] 
    ↓
Controller Method (e.g., on_search_clicked)
    ↓
publish() Event to Event Bus
    ↓
[Event: SEARCH_STARTED]
    ↓
├─→ Other Controllers subscribe and update UI
├─→ Plugins subscribe and track statistics
└─→ Analytics subscribe and log
    ↓
Execute Command via Dispatcher
    ↓
[Command: execute_search]
    ↓
Command executes business logic
    ↓
publish() Event to Event Bus
    ↓
[Event: SEARCH_COMPLETED]
```

### Example: File Preview Flow

1. User clicks file in tree
2. TreeController.on_tree_selection_changed() fires
3. Publishes `Events.FILE_SELECTED`
4. PreviewController listens and calls show_preview_for_relpath()
5. Executes 'open_file' command
6. Publishes `Events.PREVIEW_OPENED`
7. NavigationController listens and updates history
8. File statistics plugin listens and increments counter

## Extension Points

### For Plugin Developers

#### Register a Custom Command
```python
class MyCustomCommand(Command):
    def __init__(self, service):
        self.service = service
    
    def execute(self, param1, param2):
        # Your logic here
        return result

def initialize(self, context):
    cmd = MyCustomCommand(context.get_service('my_service'))
    self.register_command(context, 'my_custom_cmd', cmd)
```

#### Listen to Application Events
```python
def initialize(self, context):
    self.subscribe_event(context, Events.SEARCH_COMPLETED, self._on_search)

def _on_search(self, payload):
    results = payload.get('results', [])
    # Process results
```

#### Add a Service
```python
def initialize(self, context):
    my_service = MyService()
    context.container.register('my_service', my_service)
```

#### Execute Commands from Plugin
```python
def initialize(self, context):
    self.subscribe_event(context, 'custom_event', self._on_event)

def _on_event(self, payload):
    context.dispatcher.execute('open_file', relpath=payload['path'])
```

## Best Practices

### For Core Development

1. **Use Events for Notifications**
   - Don't call methods directly on other controllers
   - Publish events so multiple listeners can respond
   - Use Events enum for standard names

2. **Encapsulate Actions as Commands**
   - Each user action = one command
   - Commands receive dependencies via constructor
   - Commands are testable in isolation

3. **Register Services in Container**
   - Makes dependencies explicit
   - Easy to mock for testing
   - Plugins can access them

4. **Keep Controllers Event-Aware**
   - Controllers can publish events
   - Controllers can subscribe to events
   - Controllers remain testable

### For Plugin Development

1. **Initialize Properly**
   - Use initialize() method
   - Register commands and event subscriptions
   - Use context.get_service() to access dependencies

2. **Clean Up on Shutdown**
   - Override shutdown() method
   - Use parent's shutdown() to auto-unsubscribe
   - Close resources properly

3. **Handle Errors Gracefully**
   - Event bus catches handler errors
   - Commands can implement on_execute_error()
   - Log issues for debugging

4. **Name Commands Uniquely**
   - Use plugin namespace: 'my_plugin:my_command'
   - Avoid name conflicts with other plugins
   - Document what commands do

## Backward Compatibility

**Important**: All existing functionality is preserved!

- Controllers work exactly as before
- Existing methods are unchanged
- New infrastructure is additive
- No breaking changes to UI or APIs

The event system and commands are available for use but don't interfere with existing code.

## Files Structure

```
app/gui_qt/
├── event_bus.py              # Event pub/sub system
├── command_dispatcher.py      # Command registration & execution
├── commands/                  # Built-in commands
│   ├── __init__.py
│   ├── open_file.py
│   ├── execute_search.py
│   ├── export_results.py
│   ├── navigate_back.py
│   ├── navigate_forward.py
│   ├── add_bookmark.py
│   └── remove_bookmark.py
├── services/                  # Dependency injection
│   ├── __init__.py
│   └── service_container.py
├── plugins/                   # Plugin system
│   ├── __init__.py
│   ├── plugin_base.py        # Base Plugin class
│   ├── plugin_manager.py     # Plugin manager
│   ├── file_statistics_plugin.py  # Example plugin
│   └── statistics_command.py
├── main_window.py            # Orchestrator (updated with new init)
├── [controllers, widgets, etc.]
└── ...
```

## Debugging & Monitoring

### Check Event History
```python
# Get all published events
history = main_window.event_bus.get_history()

# Get specific event history
file_selected_events = main_window.event_bus.get_history('file_selected')
```

### Check Command History
```python
# Get all executed commands
history = main_window.command_dispatcher.get_history()

# Get specific command executions
search_commands = main_window.command_dispatcher.get_history('execute_search')
```

### List Registered Services
```python
services = main_window.service_container.get_all_names()
print(services)  # ['event_bus', 'command_dispatcher', 'backend', ...]
```

### List Loaded Plugins
```python
plugins = main_window.plugin_manager.get_enabled_plugins()
for name, plugin in plugins.items():
    print(f"{name} v{plugin.version}: {plugin.description}")
```

## Next Steps

1. **Create Custom Plugins**: Build feature-specific plugins
2. **Extend Commands**: Add domain-specific commands
3. **Use Events**: Gradually adopt event system in existing code
4. **Monitor Performance**: Profile event and command dispatch
5. **Document Patterns**: Create plugin templates and examples

## References

- [Event Bus Implementation](event_bus.py)
- [Command System](command_dispatcher.py)
- [Service Container](services/service_container.py)
- [Plugin Base Class](plugins/plugin_base.py)
- [Example Plugin](plugins/file_statistics_plugin.py)
