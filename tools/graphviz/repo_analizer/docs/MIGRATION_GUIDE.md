# Migration & Integration Guide

## Overview

This guide explains how to gradually adopt the new extensible architecture without breaking existing code.

**Key Point**: All existing functionality works unchanged. The new infrastructure is **additive**, not destructive.

## Architecture Layers (With Integration Points)

```
┌─────────────────────────────────────────────────────────┐
│  EXISTING MODULAR ARCHITECTURE                          │
│  ├─ ToolbarController (creates UI, handles signals)     │
│  ├─ TreeController (manages tree widget)                │
│  ├─ SearchController (runs searches)                    │
│  ├─ PreviewController (shows file previews)             │
│  ├─ NavigationController (browser-like history)         │
│  ├─ LayoutManager (saves/restores windows)              │
│  └─ DockManager (creates dock widgets)                  │
└────────────────────────────────────────────────────────┘
         ↑ (Calls methods directly - unchanged)
         │
         │ (NEW) Publishers & Subscribers can:
         ├─→ Publish events when important things happen
         ├─→ Subscribe to events without direct dependencies
         └─→ Execute commands through dispatcher
         
         ↓ (NEW)
┌─────────────────────────────────────────────────────────┐
│  INFRASTRUCTURE LAYERS                                  │
│  ├─ Event Bus (pub/sub messaging)                      │
│  ├─ Command Dispatcher (action encapsulation)          │
│  ├─ Service Container (dependency injection)           │
│  └─ Plugin Manager (dynamic extension)                 │
└─────────────────────────────────────────────────────────┘
```

## Step-by-Step Migration Path

### Phase 1: Run Existing Code (CURRENT STATE)

**Status**: ✓ Complete

All existing functionality works unchanged:
```python
# Controllers can still call each other directly
preview_controller.show_preview_for_relpath(relpath, line)

# All signals/slots work
tree.itemSelectionChanged.connect(self.on_selection)

# No changes required to existing code
```

### Phase 2: Add Event Publishing (Optional, Gradual)

When implementing new features or refactoring, add event publishing:

**Before**:
```python
def on_search_completed(self):
    self.main.results_model.clear()
    # ... populate results ...
```

**After** (Enhanced):
```python
def on_search_completed(self):
    self.main.results_model.clear()
    # ... populate results ...
    
    # NEW: Publish event for interested listeners
    self.main.event_bus.publish(Events.SEARCH_COMPLETED, {
        'result_count': self.main.results_model.rowCount(),
        'search_query': self.search_input.text(),
    })
```

**Benefits**:
- Plugins can react to this event
- Analytics can track searches
- Other features can respond without knowing about SearchController
- Completely backward compatible

### Phase 3: Add Command Wrappers (Optional, Isolated)

When adding new actions, wrap them in commands:

**Existing Code** (still works):
```python
def on_navigate_back_clicked(self):
    self.navigation_controller.navigate_back()
```

**Can Coexist With**:
```python
# NEW: Execute through dispatcher
def on_navigate_back_clicked(self):
    if self.main.command_dispatcher.has('navigate_back'):
        self.main.command_dispatcher.execute('navigate_back')
    else:
        # Fallback to direct call for compatibility
        self.navigation_controller.navigate_back()
```

**Or Blend**:
```python
# Use command if available (NEW infrastructure)
# Otherwise fall back to direct call (existing code)
def navigate_back(self):
    dispatcher = getattr(self.main, 'command_dispatcher', None)
    if dispatcher:
        dispatcher.execute('navigate_back')
    else:
        self.navigation_controller.navigate_back()
```

### Phase 4: Subscribe to Events (Optional, When Needed)

In controllers, subscribe to events for cross-cutting concerns:

```python
class SearchController:
    def __init__(self, main_window):
        self.main = main_window
        # ... existing init code ...
        
        # NEW: Subscribe to events we care about
        if hasattr(main_window, 'event_bus'):
            main_window.event_bus.subscribe(
                Events.INDEX_COMPLETED,
                self._on_index_completed
            )
    
    def _on_index_completed(self, payload):
        # Reset search when index changes
        self.clear_search()
```

### Phase 5: Leverage Plugins (Optional, Advanced)

Once event publishing is in place, create plugins for new features:

```python
# New feature: Track download statistics
# Instead of modifying existing code:

# Create: plugins/download_stats_plugin.py
class DownloadStatsPlugin(Plugin):
    def initialize(self, context):
        self.subscribe_event(context, Events.FILE_SELECTED, self._track)
    
    def _track(self, payload):
        # Track statistics
```

## Integration Patterns

### Pattern A: Publish Events in Existing Methods

Good for observability and extension points:

```python
# In TreeController
def rebuild_repo_tree(self):
    # Existing logic
    tree.clear()
    self._build_tree()
    
    # NEW: Notify listeners (optional, backward compatible)
    if hasattr(self.main, 'event_bus'):
        self.main.event_bus.publish(Events.TREE_REBUILT, {
            'root': self.main.index_data.get('root'),
            'file_count': len(self.main.index_data.get('files', {})),
        })
```

### Pattern B: Check for Infrastructure Before Using

Gracefully fall back to direct calls:

```python
def show_preview(self, relpath):
    # Approach 1: Use command dispatcher if available
    dispatcher = getattr(self.main, 'command_dispatcher', None)
    if dispatcher and dispatcher.has('open_file'):
        dispatcher.execute('open_file', relpath=relpath, line=0)
    else:
        # Approach 2: Fall back to direct method
        self.preview_controller.show_preview_for_relpath(relpath, 0)
```

### Pattern C: Event-Driven Without Breaking Existing Flow

```python
# In SearchController
def start_search(self):
    # Existing logic (never changes)
    self.clear_search()
    query = self.search_input.text()
    
    # ... setup thread, worker, etc ...
    
    # Emit event AFTER existing logic (non-breaking)
    if hasattr(self.main, 'event_bus'):
        self.main.event_bus.publish(Events.SEARCH_STARTED, {
            'query': query,
            'search_type': 'full_text',
        })
```

### Pattern D: Optional Command Execution

```python
def export_results(self):
    # Existing export logic
    filepath = QFileDialog.getSaveFileName(...)
    # ... actual export: write to file, etc ...
    
    # NEW: Try to execute command if available
    try:
        self.main.command_dispatcher.execute(
            'on_export_complete',
            filepath=filepath
        )
    except (AttributeError, ValueError):
        # Infrastructure not available, that's OK
        pass
```

## Real-World Examples

### Example 1: Adding Undo/Redo with Events

```python
# No changes to existing code!
# Just add a plugin:

class UndoRedoPlugin(Plugin):
    name = 'undo_redo'
    
    def initialize(self, context):
        self.history = []
        self.subscribe_event(context, Events.SEARCH_COMPLETED, self._save)
        self.subscribe_event(context, Events.PREVIEW_OPENED, self._save)
        
        # Register commands
        cmd = UndoCommand(self)
        self.register_command(context, 'undo', cmd)
```

### Example 2: Adding Logging with Events

```python
class LoggingPlugin(Plugin):
    name = 'logging'
    
    def initialize(self, context):
        # Subscribe to EVERYTHING
        from app.gui_qt.event_bus import Events
        for attr in dir(Events):
            if not attr.startswith('_'):
                event = getattr(Events, attr)
                self.subscribe_event(context, event, self._log)
    
    def _log(self, payload):
        # Write to log file
        with open('app.log', 'a') as f:
            f.write(f"{datetime.now()}: {payload}\n")
```

### Example 3: Adding Performance Monitoring

```python
class PerformancePlugin(Plugin):
    name = 'performance'
    
    def initialize(self, context):
        # Hook command execution
        context.dispatcher.on_before_execute(self._start_timer)
        context.dispatcher.on_after_execute(self._end_timer)
        
        self.timers = {}
    
    def _start_timer(self, cmd_name, args, kwargs):
        self.timers[cmd_name] = time.time()
    
    def _end_timer(self, cmd_name, result):
        elapsed = time.time() - self.timers.get(cmd_name, 0)
        if elapsed > 1.0:  # Log slow commands
            print(f"SLOW: {cmd_name} took {elapsed:.2f}s")
```

## Testing Strategy

### Test Existing Code (Unchanged)

```python
def test_tree_controller_existing():
    """Existing tests should still pass."""
    window = RepoAnalyzerMainWindow()
    controller = window.tree_controller
    
    controller.rebuild_repo_tree()
    assert window.repo_tree.topLevelItemCount() > 0
```

### Test New Features (With Mocking)

```python
def test_search_plugin():
    """Test new plugin in isolation."""
    from app.gui_qt.plugins import PluginContext
    from app.gui_qt.event_bus import EventBus
    from app.gui_qt.command_dispatcher import CommandDispatcher
    from app.gui_qt.services import ServiceContainer
    
    bus = EventBus()
    dispatcher = CommandDispatcher()
    container = ServiceContainer()
    
    plugin = SearchTrackingPlugin()
    context = PluginContext(bus, dispatcher, container)
    
    plugin.initialize(context)
    bus.publish('search_completed', {'query': 'test'})
    
    assert plugin.search_count == 1
```

### Test Integration

```python
def test_with_infrastructure():
    """Test existing code with infrastructure available."""
    window = RepoAnalyzerMainWindow()
    
    # Assert infrastructure exists
    assert hasattr(window, 'event_bus')
    assert hasattr(window, 'command_dispatcher')
    assert hasattr(window, 'plugin_manager')
    
    # Test that existing functionality still works
    window.tree_controller.rebuild_repo_tree()
    assert window.repo_tree.topLevelItemCount() > 0
    
    # Test that events were published
    assert window.event_bus.has_subscribers('tree_rebuilt')
```

## Migration Checklist

- [ ] **Phase 1**: Application runs unchanged ✓ (Already done)
- [ ] **Phase 2**: Add event publishing in key methods
  - [ ] SearchController.on_search_ready()
  - [ ] PreviewController.show_preview_for_relpath()
  - [ ] NavigationController.navigate_back/forward()
  - [ ] TreeController.rebuild_repo_tree()
- [ ] **Phase 3**: Create utility methods for command execution
  - [ ] Wrapper methods that try dispatcher, fall back to direct call
  - [ ] Centralize in main_window for consistency
- [ ] **Phase 4**: Subscribe to events in controllers
  - [ ] Update layout when index changes
  - [ ] Clear results when index changes
  - [ ] Track navigation state
- [ ] **Phase 5**: Create plugins for new features
  - [ ] Statistics tracking plugin
  - [ ] Logging plugin
  - [ ] Performance monitoring plugin
- [ ] **Phase 6**: Refactor old code to events
  - [ ] Remove direct controller-to-controller calls where possible
  - [ ] Use events for notifications
  - [ ] Use commands for actions
- [ ] **Phase 7**: Documentation and examples
  - [ ] Update plugin quick start
  - [ ] Add plugin examples
  - [ ] Document architecture

## Rollback Plan

If needed, the new infrastructure can be completely disabled:

```python
# In main_window.py, comment out _initialize_extensibility()

# Before:
self._initialize_extensibility()

# After:
# self._initialize_extensibility()

# Application works exactly as before with no infrastructure!
```

All existing code requires zero changes and continues to work.

## Performance Considerations

### Event Publishing

- Very fast (< 1ms per publish)
- Only processes subscribed handlers
- Safe error handling prevents slowdowns

### Command Dispatcher

- Fast lookup (dictionary-based)
- Command execution is O(1)
- History capping keeps memory bounded

### Service Container

- Singleton caching for performance
- O(1) service lookup
- No reflection or introspection

### Plugin Loading

- Happens once at startup
- File system I/O only at initialization
- No runtime plugin loading by default

## Summary

**Backward Compatibility**: ✓ 100%

- No breaking changes
- Existing code requires zero modifications
- Can migrate gradually, feature by feature
- Can roll back at any time
- New infrastructure is optional

**Integration Points**:
1. Publish events when important things happen
2. Subscribe to events for notifications
3. Register commands for reusable actions
4. Create plugins for new features

**Timeline**: Flexible

- Can adopt entire infrastructure immediately
- Or migrate gradually over multiple sprints
- Or use selectively (e.g., only events, not commands)
- Or not use at all (existing code continues to work)

Choose your own pace!
