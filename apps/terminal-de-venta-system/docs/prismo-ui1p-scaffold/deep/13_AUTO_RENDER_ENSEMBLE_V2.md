# Auto Render Ensemble V2

The removed format selector is gone. PRISMO chooses visual surfaces automatically.

## Input
- objective
- domain
- lens
- freeText
- contextNote

## Planner output
- hero_response always
- executive_brief when summary needed
- next_best_action always when action exists
- protocol_ladder/procedural_steps when procedural memory/protocols apply
- evidence_board when evidence exists
- timeline when episodic/history exists
- risk_matrix when diagnostic/audit/risk applies
- flow_diagram when architecture/sequence applies
- comparison_board when compare applies
- chart_spec_preview when chart is useful
- technical_drawer always available but closed

## UI rule
Render all useful blocks. Hide empty blocks. Overflow into drawer. Never ask the user to choose output format first.
