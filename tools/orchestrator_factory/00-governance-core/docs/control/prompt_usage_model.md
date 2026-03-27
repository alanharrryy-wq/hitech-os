
# Prompt Usage Model

## Prompt classes
1. governance prompts
2. package chat prompts
3. mission-control prompts
4. package worker prompts
5. retry prompts
6. end-of-round integration prompts

## Rule of derivation
Prompts are generated from higher-order artifacts:
- constitution
- project baseline
- run and round manifests
- active work packets

If the generated prompt diverges from those artifacts, regenerate the prompt. Do not patch policy manually inside the prompt and call it done.

## Prompt minimum fields
Every operational prompt should name:
- `project_id`
- `run_id`
- `round_id` when applicable
- `package_id` or role
- allowed paths
- forbidden paths
- consumed inputs
- required outputs
- explicit stop conditions

## What prompts may do
- restate authority
- focus scope
- embed the active work packet
- remind the worker of bundle or report requirements
- reference the active communication and waiver rules

## What prompts may not do
- create new canonical terms
- grant wider ownership than the active path policy
- override frozen contracts
- silently change success criteria
- act as informal chat-to-chat relay messages outside the artifact trail
