# 104 Operator Runbook UI Wiring

1. Run the zip wrapper.
2. Read `install_summary.txt`.
3. Read `verification_report.txt`.
4. Read `smoke_report.txt`.
5. If mirror was attempted, inspect mirror status in the summary JSON.
6. Only then decide whether to stack the next wave.
