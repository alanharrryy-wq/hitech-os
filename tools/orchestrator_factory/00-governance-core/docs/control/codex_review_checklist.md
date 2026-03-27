# Codex Review Checklist

## Boundary review
- Were only allowed files touched?
- Did the task stay inside the package and change budget?
- Were sibling package folders left untouched?

## Canonical-source review
- Did the work follow the correct authority chain?
- Did any prompt attempt to outrank frozen docs?
- Were decision records consulted when needed?

## Contract review
- Were consumed contracts cited correctly?
- Was new behavior smuggled in without a contract change?
- Did naming and dictionary terms remain canonical?

## Traceability review
- Are `project_id`, `run_id`, `round_id`, and `package_id` obvious where relevant?
- Is the changed-file list complete?
- Are assumptions and unresolved issues visible?

## Risk review
- Did the task widen scope?
- Did it introduce hidden coupling?
- Did it create merge ambiguity or overlap risk?

## Rejection triggers
Reject immediately if the work:
- changes a forbidden file
- widens ownership without authorization
- redefines a frozen interface without a decision record
- invents a canonical term or path family
- hides contradictions behind vague language
