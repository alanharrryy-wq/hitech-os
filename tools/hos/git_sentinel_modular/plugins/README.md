# Plugin seam

This directory is intentionally small.

## What it does

- registers external integration descriptors
- lists enabled or disabled plugins cleanly
- lets the control plane ask for health-check status without owning the external integration itself

## What it does not do

- it does not implement Cloudflare
- it does not implement Keystone
- it does not implement engine_guardian
- it does not mutate scheduled tasks

A plugin is just metadata plus optional hooks. The package can stay coherent even when the registry is empty.
