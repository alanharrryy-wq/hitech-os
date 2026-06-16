# Capatch Cartridge Model

Capatch cartridges work like Nintendo 64 cartridges: the core console stays generic and each task/surface plugs in extra rules. A cartridge never owns the whole tool forever. It only declares what applies to one context.

## Cartridge responsibilities

- detect or declare allowed surfaces
- define excluded surfaces
- add verifier requirements
- add evidence requirements
- set visual or structural risk gates
- describe operation families that are appropriate for the task

## Composition

A single job may load many cartridges:

```text
prisma-tablet + react-ui + visual-premium + external-output
```

Another job may load a different stack:

```text
generic-code + docs-config + external-output
```

The core stays open. Cartridges are additive and declarative.
