# DIFF_OUTPUT_POLICY

## Purpose
Codex responses must be reviewable in plain text, including terminal logs, copied chat logs, and offline artifacts. Color-only UI diffs are not sufficient evidence.

## Mandatory Output Format
Every Codex change response MUST include, in plaintext:
1. `CHANGED FILES` list.
2. Unified diff patch (`git diff --no-color --patch`) inside a fenced code block.
3. Full contents of each created/modified file (or changed regions with explicit omission markers for very large files).

## Artifact Requirement
When scripts generate changes, they MUST also write a no-color patch artifact to disk (for example `.tmp/.../*.patch`) and print it to stdout when feasible.

## Do / Don't
- Do: use `git diff --no-color --patch`.
- Do: include explicit file paths and exact commands.
- Do: treat missing plaintext diff as incomplete output.
- Don't: rely only on IDE/UI color diffs.
- Don't: omit changed file contents from the final response.
