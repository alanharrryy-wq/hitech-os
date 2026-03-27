# Tactical Architecture Overview

## Objective
Enable six package chats to work in parallel without direct cross-editing, then evaluate their outputs through deterministic validation before integration.

## Core idea
Parallel package work is coordinated through:
- active work packets
- path policies
- deterministic bundles
- manifests and reports
- overlap detection
- acceptance decisions
- integration readiness summaries

## Roles
- Governance chat, acting as mission control by default
- Six package chats, one per package
- Optional delegated integration judge if governance chooses to split the role

## Tactical flow
1. initialize run
2. initialize round
3. generate work packets
4. generate prompts
5. collect bundles
6. validate structure and ownership
7. compute overlap
8. emit acceptance decisions
9. integrate in dependency order
10. prepare retries or next round
