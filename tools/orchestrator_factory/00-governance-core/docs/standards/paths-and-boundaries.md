# Paths and Boundaries

## Why boundaries matter
Parallel chats fail when responsibility is implied instead of written down. The framework therefore distinguishes three boundary classes.

## Boundary classes

### Constitutional paths
Governance-owned files and operational framework files.

### Package-local paths
Each package's own folder and docs.

### Project runtime paths
Real application or repository paths assigned during homologation and activated through work packets.

## Boundary rules
- a package may write only inside its owned package folder and active runtime paths
- reading from upstream packages is allowed when needed
- writing to another package folder is prohibited
- requesting a new runtime path assignment goes through governance
- cross-package summaries live in governance or run-control artifacts, not in private notes

## Tactical rule
The tactical subsystem may enforce path ownership, but it may not invent it.
