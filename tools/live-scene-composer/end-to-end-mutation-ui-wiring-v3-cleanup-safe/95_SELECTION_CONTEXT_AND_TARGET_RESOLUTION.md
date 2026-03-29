# 95 Selection Context and Target Resolution

Selection is transient UI state.

Target resolution derives a stable mutation target from selection plus current scene lineage.

Important distinctions:
- selected widget != widget props mutation yet
- selected slot != slot mutation until an action is chosen
- selected scene != scene look update until a specific field changes
