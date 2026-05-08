<!-- agent-workbench-rescue-managed -->
# State Transitions

## Allowed States

NOT_STARTED, IN_PROGRESS, DELIVERED_NOT_PUSHED, NEEDS_UPDATE, READY_FOR_REVIEW, BLOCKED, DO_NOT_MERGE, CLOSED

## Allowed Risk Levels

LOW, MEDIUM, HIGH, CRITICAL

## Allowed Coordinator Decisions

CONTINUE, UPDATE_REQUIRED, WAIT, STOP, ESCALATE_TO_USER, READY_FOR_PR, DO_NOT_MERGE

## Transition Guidance

- NOT_STARTED -> IN_PROGRESS
- IN_PROGRESS -> DELIVERED_NOT_PUSHED
- DELIVERED_NOT_PUSHED -> NEEDS_UPDATE or READY_FOR_REVIEW
- NEEDS_UPDATE -> READY_FOR_REVIEW after scoped report is complete
- READY_FOR_REVIEW -> READY_FOR_PR only by Coordinator
- Any state -> BLOCKED when evidence or dependency is missing
- Any unsafe merge, branch deletion, force-push, product-code edit, or CAPATCH active dependency issue -> DO_NOT_MERGE
- CAPATCH remains CLOSED / DISCARDED_FOR_SAFETY / NO_PUSH / NO_PR / DO_NOT_MERGE.
