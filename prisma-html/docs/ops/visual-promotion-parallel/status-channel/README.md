# PRISMA Visual Promotion Status Channel

Status: `CANONICAL_COORDINATION_CHANNEL`

This folder defines the shared reporting protocol for Chats 1–6.

## Architecture

Static contract:
`prisma-html/docs/ops/visual-promotion-parallel/status-channel/`

Writable mailboxes:
`apps/terminal-de-venta-system/docs/ops/visual-promotion-parallel-status/`

Writable mailboxes intentionally live outside `prisma-html` so frequent status updates do not invalidate the global hash-sensitive `FILES_MANIFEST.json`.

## Chat mapping

| Chat | Lane | Status branch | Mailbox |
|---|---|---|---|
| 1 | Tablet Promotion | `status/vp-chat-01-tablet` | `chat-01-tablet/` |
| 2 | PC Promotion | `status/vp-chat-02-pc` | `chat-02-pc/` |
| 3 | Mobile Promotion | `status/vp-chat-03-mobile` | `chat-03-mobile/` |
| 4 | Shared UI Promotion | `status/vp-chat-04-shared-ui` | `chat-04-shared-ui/` |
| 5 | Atlasfin Bridge | `status/vp-chat-05-atlasfin` | `chat-05-atlasfin/` |
| 6 | Visual Promotion Control Plane | `status/vp-chat-06-control-plane` | `chat-06-control-plane/` |

The branch and mailbox identify the Chat unambiguously.

## Worker writes

Each Chat updates only its own:

- `STATUS.json`: current machine-readable snapshot.
- `LOG.md`: append-only human timeline.

Do not edit another Chat, `STATUS_INDEX.json`, this static contract or global authority.

## Reporting cadence

Publish:
1. immediately when receiving the reporting instruction;
2. when work starts/resumes;
3. when a blocker appears, clears or changes;
4. after a material finding, decision or milestone;
5. before requesting user action;
6. at completion.

States are exactly:
`NOT_STARTED`, `IN_PROGRESS`, `BLOCKED`, `WAITING_EXTERNAL`, `READY_FOR_INTEGRATION`, `DONE`, `FAILED`.

`READY_FOR_INTEGRATION` is lane handoff readiness, not product/runtime READY.

## STATUS.json content

Keep current: chat/lane identity, status branch/mailbox, base HEAD, work branch/head, state, timestamp, summary, blockers, findings, decisions, changed paths, validations, unresolved items, user-action need, next action and handoff.

Never store secrets or sensitive customer data.

## LOG.md

Append timestamped events. Do not rewrite prior facts to prettify history. If something was wrong, append a correction.

Event vocabulary:
`START`, `PROGRESS`, `FINDING`, `DECISION`, `BLOCKER`, `BLOCKER_CLEARED`, `VALIDATION`, `HANDOFF`, `COMPLETE`.

## Authority boundary

Status files are coordination evidence only. They are not NDC, Identity, RIFAT, Atlasfin authority, binding resolution, Work Entry authorization, GVAE receipt, runtime certification or Factory Ledger maturity truth.

A coordinator can inspect all six deterministic status branches directly. Missing branch/status remains missing; never infer hidden progress.
