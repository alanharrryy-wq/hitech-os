# Execution Plane

The kernel uses a light coordinator:
- build runtime context with absolute resolved paths
- load manifests in deterministic order
- enforce stage barriers
- execute engines in canonical stage order
- collect execution summaries
- flush event bus and emit one execution report
