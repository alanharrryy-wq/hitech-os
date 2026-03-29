# Failure and Retry Playbook

## When one bundle fails
1. do not integrate it partially
2. preserve the failed bundle as evidence
3. generate a retry prompt only for the affected package
4. increment `bundle_version`
5. cite the acceptance report and exact conflicting paths or fields

## When two bundles conflict
- mission control resolves real ownership
- one or both packages receive a retry prompt
- no silent manual patch is applied in place of a recorded resolution

## When a frozen contract is the real problem
- governance records the change
- affected packets are regenerated
- the retry explains which canonical source changed and why
