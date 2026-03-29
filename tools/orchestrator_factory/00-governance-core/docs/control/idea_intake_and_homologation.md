
# Idea Intake and Homologation

## Why homologation exists
Raw ideas arrive full of ambiguity. Homologation converts that ambiguity into a governed project baseline that six package chats can execute without inventing different projects.

## Intake record
Capture the raw input exactly enough to preserve intent:
- problem or opportunity
- desired outcome
- user or business impact
- current repo or system reality
- constraints and deadlines
- known risks
- obvious non-goals
- unknowns that block package launch

## Homologation output
The homologation record turns the raw idea into:
- `project_id`
- initiative type
- project baseline summary
- success conditions
- default package topology or justified override
- runtime path ownership draft
- canonical source register
- contract register
- initial dependency graph
- first `run_id`
- first run objective
- initial open risks and escalation points

## Storage location
Store the homologated project baseline under:
`ops/projects/<project_id>/`

Minimum expected baseline files:
- `project_manifest.json`
- `idea_intake.md`
- `homologation_record.md`
- `canonical_source_register.md`
- `contract_register.md`

## Homologation rules
- do not open package chats before homologation is coherent
- do not let package chats decide package topology independently
- record every topology override and canonical-source exception
- separate facts from assumptions explicitly
- do not leave the project baseline only inside chat memory

## Approval gate
Homologation is approved when:
- the project can be routed into packages without ambiguity
- runtime path ownership is at least draftable
- success and non-goals are clear enough to test
- the first run objective is narrow enough to govern
- contract surfaces likely to matter in `run-001` are registered

## Typical failure modes
- trying to start execution with only a slogan
- hiding repo uncertainty inside prompts
- letting package chats create their own terms
- confusing project scope with run scope
- treating examples as if they were already canonical
