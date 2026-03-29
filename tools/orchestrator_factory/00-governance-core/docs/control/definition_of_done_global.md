# Global Definition of Done

A package is not done because it produced text. It is done only when:
1. ownership is explicit
2. dependencies are explicit
3. outputs are consumable by downstream packages
4. non-goals are explicit
5. acceptance gates exist
6. canonical terminology is used
7. traceability back to project and run context is possible
8. no hidden tribal knowledge is required to execute the package
9. reviewers can tell where the package ends and another begins

## Extra done criteria for bounded execution tasks
- task is narrow enough for one run or round
- files are pre-authorized
- success is externally verifiable
- rollback is documented
- change budget is respected
- output references the canonical sources it followed
