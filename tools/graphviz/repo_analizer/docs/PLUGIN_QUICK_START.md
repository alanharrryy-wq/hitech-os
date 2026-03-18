# Quick Start: Extending Repo Analyzer

## Quick Overview

The Repo Analyzer now supports three ways to extend functionality:

1. **Events** - React to what's happening
2. **Commands** - Encapsulate actions
3. **Plugins** - Package extensions independently

## Creating Your First Plugin

### Step 1: Create Plugin File

Create `app/gui_qt/plugins/my_plugin.py`:

```python
from PySide6.QtWidgets import QMessageBox
from app.gui_qt.plugins import Plugin, PluginContext
from app.gui_qt.event_bus import Events


class MyPlugin(Plugin):
    """My first plugin."""
    
    name = 'my_plugin'
    version = '1.0.0'
    description = 'Shows a message when files are selected'
    author = 'Your Name'
    
    def initialize(self, context: PluginContext) -> None:
        """Initialize the plugin."""
        # Listen for file selections
        self.subscribe_event(context, Events.FILE_SELECTED, self._on_file_selected)
        print(f"✓ {self.name} loaded")
    
    def _on_file_selected(self, payload):
        """Handle file selection."""
        relpath = payload.get('relpath', 'unknown')
        line = payload.get('line', 0)
        print(f"File selected: {relpath} (line {line})")


# That's it! The plugin manager will find MyPlugin automatically.
```

### Step 2: Plugin is Automatically Loaded

When the app starts, the plugin manager:
1. Finds all Python files in `plugins/` directory
2. Looks for `Plugin` subclasses
3. Initializes them with access to event bus, commands, and services

### Step 3: Access Application Services

```python
class MyPlugin(Plugin):
    def initialize(self, context: PluginContext) -> None:
        # Get any registered service
        settings = context.get_service('settings')
        backend = context.get_service('backend')
        main_window = context.get_service('main_window')
        
        # Register a command so others can call it
        self.register_command(context, 'my_action', MyCommand())
```

## Creating Custom Commands

### Simple Command

```python
from app.gui_qt.command_dispatcher import Command


class ShowStatsCommand(Command):
    def __init__(self, plugin):
        self.plugin = plugin
    
    def execute(self) -> dict:
        return self.plugin.get_statistics()


# In your plugin:
def initialize(self, context):
    cmd = ShowStatsCommand(self)
    self.register_command(context, 'show_stats', cmd)
    
# Users can execute it:
# context.dispatcher.execute('show_stats')
```

### Command with Dependencies

```python
class MyCommand(Command):
    def __init__(self, main_window, backend):
        self.main_window = main_window
        self.backend = backend
    
    def can_execute(self) -> bool:
        # Add validation
        return self.backend.has_index
    
    def execute(self, arg1, arg2) -> str:
        # Do something
        result = self.backend.process(arg1, arg2)
        return result


# In plugin:
def initialize(self, context):
    main_win = context.get_service('main_window')
    backend = context.get_service('backend')
    cmd = MyCommand(main_win, backend)
    self.register_command(context, 'my_command', cmd)
```

## Listening to Events

### Subscribe to Events

```python
def initialize(self, context: PluginContext) -> None:
    from app.gui_qt.event_bus import Events
    
    # Listen to built-in events
    self.subscribe_event(context, Events.FILE_SELECTED, self._on_file)
    self.subscribe_event(context, Events.SEARCH_COMPLETED, self._on_search)
    self.subscribe_event(context, Events.PREVIEW_OPENED, self._on_preview)

def _on_file(self, payload):
    relpath = payload.get('relpath')
    line = payload.get('line')
    print(f"File: {relpath} line {line}")

def _on_search(self, payload):
    results = payload.get('results', [])
    print(f"Found {len(results)} results")

def _on_preview(self, payload):
    file_path = payload.get('relpath')
    print(f"Previewing: {file_path}")
```

### Available Events

```
INDEX_STARTED, INDEX_COMPLETED, INDEX_FAILED
TREE_REBUILT, FILE_SELECTED, TREE_FILTER_CHANGED
SEARCH_STARTED, SEARCH_COMPLETED, SEARCH_FAILED, SEARCH_CLEARED
PREVIEW_OPENED, PREVIEW_CLOSED
NAVIGATION_CHANGED, NAVIGATION_BACK, NAVIGATION_FORWARD
LAYOUT_CHANGED, LAYOUT_SAVED
SKIN_CHANGED
BOOKMARK_ADDED, BOOKMARK_REMOVED, BOOKMARKS_REFRESHED
ERROR_OCCURRED, STATUS_CHANGED
```

## Executing Commands

### From Your Plugin

```python
def _on_search(self, context, payload):
    # Execute a built-in command
    try:
        context.dispatcher.execute('export_results')
    except Exception as e:
        print(f"Command failed: {e}")
```

### Before Execution Hooks

```python
def initialize(self, context):
    # Hook that runs before any command executes
    unsub = context.dispatcher.on_before_execute(self._before_cmd)
    
    # Keep track for cleanup
    self._unsubscribe_handlers.append(unsub)

def _before_cmd(self, command_name, args, kwargs):
    print(f"About to execute: {command_name}")
```

### After Execution Hooks

```python
def initialize(self, context):
    # Hook that runs after any command executes
    unsub = context.dispatcher.on_after_execute(self._after_cmd)
    self._unsubscribe_handlers.append(unsub)

def _after_cmd(self, command_name, result):
    print(f"Command '{command_name}' returned: {result}")
```

## File Statistics Plugin (Example)

The included `file_statistics_plugin.py` shows a real example:

```python
class FileStatisticsPlugin(Plugin):
    """Track file operations and statistics."""
    
    name = 'file_statistics'
    version = '1.0.0'
    
    def __init__(self):
        super().__init__()
        self.stats = {
            'files_opened': 0,
            'searches_executed': 0,
            'previews_shown': 0,
        }
    
    def initialize(self, context):
        # Subscribe to events
        self.subscribe_event(context, Events.FILE_SELECTED, self._on_file)
        self.subscribe_event(context, Events.SEARCH_COMPLETED, self._on_search)
        self.subscribe_event(context, Events.PREVIEW_OPENED, self._on_preview)
        
        # Register command to show stats
        cmd = DisplayStatisticsCommand(self)
        self.register_command(context, 'show_stats', cmd)
    
    def _on_file(self, payload):
        self.stats['files_opened'] += 1
    
    def _on_search(self, payload):
        self.stats['searches_executed'] += 1
    
    def _on_preview(self, payload):
        self.stats['previews_shown'] += 1
    
    def get_statistics(self):
        return self.stats.copy()
```

## Plugin Lifecycle

### Initialization
```python
def initialize(self, context):
    # Called when plugin is loaded
    # Register commands, services, subscriptions
    # This is required - must be implemented
    pass
```

### Shutdown
```python
def shutdown(self):
    # Called when plugin is unloaded
    # Clean up resources, close connections
    # Parent class auto-unsubscribes from events
    super().shutdown()
```

### Enable/Disable
```python
# In main app:
plugin_manager.disable_plugin('my_plugin')
plugin_manager.enable_plugin('my_plugin')

# In plugin:
if self.enabled:
    # Do something only if enabled
```

## Common Patterns

### Pattern 1: Track Everything

```python
class AuditPlugin(Plugin):
    def initialize(self, context):
        from app.gui_qt.event_bus import Events
        
        # Get all event names
        event_attrs = [attr for attr in dir(Events) 
                      if not attr.startswith('_')]
        
        # Subscribe to all
        for event_name in event_attrs:
            event = getattr(Events, event_name)
            self.subscribe_event(context, event, self._log_event)
    
    def _log_event(self, payload):
        print(f"Event: {payload}")
```

### Pattern 2: Enhance Command

```python
class LoggingPlugin(Plugin):
    def initialize(self, context):
        # Hook into command execution
        context.dispatcher.on_before_execute(self._before)
        context.dispatcher.on_after_execute(self._after)
    
    def _before(self, cmd_name, args, kwargs):
        print(f"→ {cmd_name}")
    
    def _after(self, cmd_name, result):
        print(f"← {cmd_name}: {result}")
```

### Pattern 3: Transform Data

```python
class TransformPlugin(Plugin):
    def initialize(self, context):
        self.subscribe_event(context, Events.SEARCH_COMPLETED, self._transform)
        
        # Register new command that uses transformed data
        cmd = ShowTransformedCommand(self)
        self.register_command(context, 'show_transformed', cmd)
    
    def _transform(self, payload):
        results = payload.get('results', [])
        self.last_results = self._group_by_type(results)
        self.last_payload = payload
    
    def _group_by_type(self, results):
        # Transform data
        return results
```

## Testing Your Plugin

### Standalone Testing

```python
from app.gui_qt.event_bus import EventBus
from app.gui_qt.command_dispatcher import CommandDispatcher
from app.gui_qt.services import ServiceContainer
from app.gui_qt.plugins import PluginContext
from my_plugin import MyPlugin


def test_my_plugin():
    # Create infrastructure
    bus = EventBus()
    dispatcher = CommandDispatcher()
    container = ServiceContainer()
    
    # Create plugin
    plugin = MyPlugin()
    
    # Initialize
    context = PluginContext(bus, dispatcher, container)
    plugin.initialize(context)
    
    # Test it
    bus.publish('file_selected', {'relpath': 'test.py'})
    
    # Assert behavior
    assert plugin.file_count == 1
```

## Troubleshooting

### Plugin Not Loading
1. File is in `plugins/` directory? ✓
2. Class inherits from `Plugin`? ✓
3. Class has `name`, `version`, `description`? ✓
4. `initialize()` method defined? ✓

### Plugin Not Seeing Events
1. Using `self.subscribe_event(context, eventname, handler)`? ✓
2. Handler is callable and takes one argument? ✓
3. Event name matches (check `Events` enum)? ✓
4. Plugin is enabled? `plugin.enabled == True` ✓

### Command Not Found
1. Registered in `initialize()`? ✓
2. Used correct registration method? ✓
3. Command name is correct? ✓
4. Plugin initialized successfully? ✓

## Resources

- [Full Architecture Guide](EXTENSIBLE_ARCHITECTURE.md)
- [Event Bus API](../event_bus.py)
- [Command System API](../command_dispatcher.py)
- [Plugin Base Class](../plugins/plugin_base.py)
- [File Statistics Example](../plugins/file_statistics_plugin.py)
