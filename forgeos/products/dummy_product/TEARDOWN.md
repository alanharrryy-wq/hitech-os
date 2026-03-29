# TEARDOWN

Required teardown steps:

1. Suspend active surface if visible.
2. Unregister contribution from host slot.
3. Clear runtime state.
4. Mark runtime disposed.

Evidence requirement:

- Teardown result must be captured by lifecycle/dispose contract outcome.