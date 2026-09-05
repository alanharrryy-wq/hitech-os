# PRISMA Visual Promotion Parallel Status Mailboxes

Writable coordination mailboxes for Chats 1–6.

Canonical rules: `prisma-html/docs/ops/visual-promotion-parallel/status-channel/`

Each Chat owns exactly one mailbox and one dedicated status branch. It updates only `STATUS.json` and `LOG.md`. The coordinator reads all six branches; there is no shared mutable index to collide on.
