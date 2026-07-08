# AutoGit Learning Ledger

## AG100 learning package

This ledger captures durable rules learned from the PR #171 closure and the mid-flight fixes that were needed to close it safely.

1. Large JSON evidence registers must be validated through a JSON-specific reader, not through capped evidence snapshot readers.
2. Staged whitespace and EOF blockers are safe to self-heal only for allowlisted text extensions and only after the files are staged for the active commit group.
3. Mid-flight apply-plan failures must preserve enough evidence to continue without reset, clean, or guesswork.
4. Runtime noise such as SQLite WAL/SHM files should be excluded from commit planning and reported as cleanup guidance, not committed.
5. Fail ZIPs must include branch, HEAD, main..HEAD, staged files, cached diff check, current staged files when safe, and continuation guidance.
6. Post-run reports must classify remaining local changes as runtime noise, AutoGit tooling, likely intentional product work, runtime overrides, or requires decision.
7. No-fake-green applies across every stage: local fix, apply-plan, PR creation, checks, merge, and post-merge hygiene are different gates.

## Implementation

AG100 adds:

- `autogit_engine/ag100_learning.py`
- larger JSON validation lane
- staged text self-heal for trailing whitespace and extra blank EOF
- group checkpoints during apply-plan
- enhanced fail ZIP context
- post-run hygiene reports
- expanded selftests
