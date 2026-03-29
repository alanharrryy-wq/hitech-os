# Shared Acceptance Gates

Every package-local deliverable must pass these baseline gates:
1. ownership is explicit
2. dependencies are explicit
3. consumers are named
4. non-goals are explicit
5. canonical terminology is used
6. acceptance criteria are externally verifiable
7. traceability back to project and run context is possible
8. no contradiction exists with higher-order canonical sources

## Bundle-specific gate
No bundle is integration-ready unless it has:
- valid structure
- valid manifest and report
- ownership-compliant payload paths
- no undeclared or missing payload files
- no exact-path conflict with accepted peers
- acceptance status other than reject

## Prompt-specific gate
No prompt may be used if it:
- grants wider ownership than the active packet
- contradicts frozen docs
- omits stop conditions
- hides consumed inputs
