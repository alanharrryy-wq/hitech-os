# TEARDOWN

Required teardown sequence:

1. Suspend product if active.
2. Unregister host contribution.
3. Clear cached summary/index data.
4. Transition runtime to disposed.

Evidence:

- lifecycle transition to `disposed` and empty host contribution snapshot.