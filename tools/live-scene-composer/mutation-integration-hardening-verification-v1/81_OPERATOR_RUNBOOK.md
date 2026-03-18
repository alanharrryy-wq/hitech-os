# 81_OPERATOR_RUNBOOK

## Fast operator loop

- run launcher from zip
- collect generated summary folder
- if verification failed, read `verification_report.txt` first
- if smoke failed, read `smoke_report.txt` next
- only then decide whether the issue is installer, repo layout, or expected gap in the repo
