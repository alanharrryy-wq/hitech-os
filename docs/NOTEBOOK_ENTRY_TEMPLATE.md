# Notebook Entry Template

Use this template for new entries in `docs/NOTEBOOK.md` or nearby governance debt logs.

## Template

```md
## [ENTRY_ID] short-title

- date: YYYY-MM-DD
- owner: <team-or-person>
- status: proposed | active | retired
- scope: <paths, systems, or contracts affected>
- reason: <why this exception / debt / temporary note exists>
- evidence: <links or paths to proofs, reports, or artifacts>
- risk: <what can go wrong if this stays unresolved>
- rollback: <how to undo or retire the exception>
- expiry_or_review_date: YYYY-MM-DD

### Details
<freeform details>

### Next action
<single next action or explicit "none yet">
```

## Rules

- avoid anonymous debt
- include a rollback note
- include either an expiry date or a review date
- prefer concrete paths and artifacts over vague prose
- do not use the notebook to silently legalize a broken state forever

## Why this file exists

The repo already had a notebook/debt mechanism, but the format was easy to drift. A template gives contributors a repeatable structure without changing the authority model.
