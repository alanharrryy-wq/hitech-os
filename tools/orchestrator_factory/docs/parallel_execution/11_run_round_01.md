# How to Run Round 01

1. initialize the run:
   `python tools/execution_framework/init_run.py --project-id <project_id> --objective "<objective>"`
2. initialize the first round:
   `python tools/execution_framework/init_round.py --run-id <run_id> --round-id rd-001`
3. generate work packets:
   `python tools/execution_framework/generate_work_packets.py --run-id <run_id> --round-id rd-001`
4. generate prompts:
   `python tools/execution_framework/generate_prompt_packets.py --run-id <run_id> --round-id rd-001`
5. distribute prompts to the six package chats
6. receive bundles into `ops/runs/<run_id>/rounds/rd-001/incoming/`
7. validate overlap and acceptance
8. integrate accepted bundles in dependency order
