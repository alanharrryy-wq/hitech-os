# Operator Improvements 200
OP-001 [DONE] Added top-level operator command group in factory CLI
OP-002 [DONE] Added operator bootstrap subcommand with deterministic defaults
OP-003 [DONE] Added operator watch subcommand with polling controls
OP-004 [DONE] Added operator phase1-extract one-command orchestration
OP-005 [DONE] Added deterministic phase spec structure for phase1-extract
OP-006 [DONE] Defined scoped worker missions for A_worker/B_worker/C_worker/D_worker
OP-007 [DONE] Added deterministic worker parsing with sorted unique ordering
OP-008 [DONE] Added prompt generation for tools/codex/prompts/<RUN_ID>
OP-009 [DONE] Added worktree prompt generation for PROMPT_WORKER.txt targets
OP-010 [DONE] Added deterministic RUNBOARD.md generation per run
OP-011 [DONE] Added collision detection for mismatched existing prompt content
OP-012 [DONE] Added run-id mismatch detection in existing prompt files
OP-013 [DONE] Added repository root identification guard for operator outputs
OP-014 [DONE] Added protected-path enforcement for operator-generated files
OP-015 [DONE] Added deterministic prompt content hashing in generation payloads
OP-016 [DONE] Added dry-run planning mode for bootstrap prompt generation
OP-017 [DONE] Added dry-run bundle-init planning path in bootstrap
OP-018 [DONE] Added dry-run worktree verify planning path in bootstrap
OP-019 [DONE] Enhanced worktrees open command with --new-window support
OP-020 [DONE] Enhanced worktrees open command with --goto support
OP-021 [DONE] Added deterministic worker ordering in worktree operations
OP-022 [DONE] Added code command builder for deterministic VS Code open args
OP-023 [DONE] Added operator JSON summary builder with stable sorted arrays
OP-024 [DONE] Added operator action tracking across bootstrap stages
OP-025 [DONE] Added operator path-open tracking for runboard/worktrees/report
OP-026 [DONE] Added operator next-step tracking in final summaries
OP-027 [DONE] Added init-run reuse behavior when RUN_MANIFEST.json already exists
OP-028 [DONE] Added bootstrap stage details payload for diagnostics
OP-029 [DONE] Added watch progress logging with present/missing worker sets
OP-030 [DONE] Added graceful missing STATUS.json handling in watch scan
OP-031 [DONE] Added watch timeout semantics with BLOCKED status
OP-032 [DONE] Added watch dry-run planning mode without blocking polling
OP-033 [DONE] Added watch-triggered bundle-validate execution
OP-034 [DONE] Added watch-triggered integrate execution
OP-035 [DONE] Added optional final report opening workflow after integrate
OP-036 [DONE] Added optional run-folder reveal workflow after integrate
OP-037 [DONE] Added phase1-extract bootstrap+watch orchestration wiring
OP-038 [DONE] Added required agent action instruction emission for phase1-extract
OP-039 [DONE] Added worktrees parser flags for --new-window and --goto
OP-040 [DONE] Added operator CLI flags for sleep-sec and timeout-min
OP-041 [DONE] Added operator CLI flags for open-vscode/open-runboard/open-final-report
OP-042 [DONE] Added operator CLI flags for goto-prompt and phase selection
OP-043 [DONE] Added operator defaults aligned to A/B/C/D worker set
OP-044 [DONE] Updated _parse_workers to deterministic sorted unique output
OP-045 [DONE] Added root CONTRACT.md stub pointing to canonical docs
OP-046 [DONE] Added root STATE.md stub pointing to canonical docs
OP-047 [DONE] Added root NEXT.md stub pointing to canonical docs
OP-048 [DONE] Updated OPERATOR_COMMANDS.md with bootstrap/watch/phase1 usage
OP-049 [DONE] Updated RUNBOOK.md with operator orchestration reference
OP-050 [DONE] Added operator orchestrator unit test coverage module
OP-051 [DONE] Added unit test for deterministic prompt generation output
OP-052 [DONE] Added unit test for stable worker sorting behavior
OP-053 [DONE] Added unit test for watch missing-status resilience
OP-054 [DONE] Added unit test for worktrees open code args in dry-run
OP-055 [DONE] Patched isolated test support to include operator path constants
OP-056 [DONE] Kept existing stage commands backward compatible and additive
OP-057 [DONE] Preserved machine-readable JSON output formatting with sort_keys
OP-058 [DONE] Preserved status-to-exit-code semantics PASS/BLOCKED/FAIL
OP-059 [DONE] Kept operator flow independent from any Z_integrator worktree path
OP-060 [DONE] Added deterministic action/path/next-step sorting in summaries
OP-061 [TODO] Backlog operator improvement item OP-061
OP-062 [TODO] Backlog operator improvement item OP-062
OP-063 [TODO] Backlog operator improvement item OP-063
OP-064 [TODO] Backlog operator improvement item OP-064
OP-065 [TODO] Backlog operator improvement item OP-065
OP-066 [TODO] Backlog operator improvement item OP-066
OP-067 [TODO] Backlog operator improvement item OP-067
OP-068 [TODO] Backlog operator improvement item OP-068
OP-069 [TODO] Backlog operator improvement item OP-069
OP-070 [TODO] Backlog operator improvement item OP-070
OP-071 [TODO] Backlog operator improvement item OP-071
OP-072 [TODO] Backlog operator improvement item OP-072
OP-073 [TODO] Backlog operator improvement item OP-073
OP-074 [TODO] Backlog operator improvement item OP-074
OP-075 [TODO] Backlog operator improvement item OP-075
OP-076 [TODO] Backlog operator improvement item OP-076
OP-077 [TODO] Backlog operator improvement item OP-077
OP-078 [TODO] Backlog operator improvement item OP-078
OP-079 [TODO] Backlog operator improvement item OP-079
OP-080 [TODO] Backlog operator improvement item OP-080
OP-081 [TODO] Backlog operator improvement item OP-081
OP-082 [TODO] Backlog operator improvement item OP-082
OP-083 [TODO] Backlog operator improvement item OP-083
OP-084 [TODO] Backlog operator improvement item OP-084
OP-085 [TODO] Backlog operator improvement item OP-085
OP-086 [TODO] Backlog operator improvement item OP-086
OP-087 [TODO] Backlog operator improvement item OP-087
OP-088 [TODO] Backlog operator improvement item OP-088
OP-089 [TODO] Backlog operator improvement item OP-089
OP-090 [TODO] Backlog operator improvement item OP-090
OP-091 [TODO] Backlog operator improvement item OP-091
OP-092 [TODO] Backlog operator improvement item OP-092
OP-093 [TODO] Backlog operator improvement item OP-093
OP-094 [TODO] Backlog operator improvement item OP-094
OP-095 [TODO] Backlog operator improvement item OP-095
OP-096 [TODO] Backlog operator improvement item OP-096
OP-097 [TODO] Backlog operator improvement item OP-097
OP-098 [TODO] Backlog operator improvement item OP-098
OP-099 [TODO] Backlog operator improvement item OP-099
OP-100 [TODO] Backlog operator improvement item OP-100
OP-101 [TODO] Backlog operator improvement item OP-101
OP-102 [TODO] Backlog operator improvement item OP-102
OP-103 [TODO] Backlog operator improvement item OP-103
OP-104 [TODO] Backlog operator improvement item OP-104
OP-105 [TODO] Backlog operator improvement item OP-105
OP-106 [TODO] Backlog operator improvement item OP-106
OP-107 [TODO] Backlog operator improvement item OP-107
OP-108 [TODO] Backlog operator improvement item OP-108
OP-109 [TODO] Backlog operator improvement item OP-109
OP-110 [TODO] Backlog operator improvement item OP-110
OP-111 [TODO] Backlog operator improvement item OP-111
OP-112 [TODO] Backlog operator improvement item OP-112
OP-113 [TODO] Backlog operator improvement item OP-113
OP-114 [TODO] Backlog operator improvement item OP-114
OP-115 [TODO] Backlog operator improvement item OP-115
OP-116 [TODO] Backlog operator improvement item OP-116
OP-117 [TODO] Backlog operator improvement item OP-117
OP-118 [TODO] Backlog operator improvement item OP-118
OP-119 [TODO] Backlog operator improvement item OP-119
OP-120 [TODO] Backlog operator improvement item OP-120
OP-121 [TODO] Backlog operator improvement item OP-121
OP-122 [TODO] Backlog operator improvement item OP-122
OP-123 [TODO] Backlog operator improvement item OP-123
OP-124 [TODO] Backlog operator improvement item OP-124
OP-125 [TODO] Backlog operator improvement item OP-125
OP-126 [TODO] Backlog operator improvement item OP-126
OP-127 [TODO] Backlog operator improvement item OP-127
OP-128 [TODO] Backlog operator improvement item OP-128
OP-129 [TODO] Backlog operator improvement item OP-129
OP-130 [TODO] Backlog operator improvement item OP-130
OP-131 [TODO] Backlog operator improvement item OP-131
OP-132 [TODO] Backlog operator improvement item OP-132
OP-133 [TODO] Backlog operator improvement item OP-133
OP-134 [TODO] Backlog operator improvement item OP-134
OP-135 [TODO] Backlog operator improvement item OP-135
OP-136 [TODO] Backlog operator improvement item OP-136
OP-137 [TODO] Backlog operator improvement item OP-137
OP-138 [TODO] Backlog operator improvement item OP-138
OP-139 [TODO] Backlog operator improvement item OP-139
OP-140 [TODO] Backlog operator improvement item OP-140
OP-141 [TODO] Backlog operator improvement item OP-141
OP-142 [TODO] Backlog operator improvement item OP-142
OP-143 [TODO] Backlog operator improvement item OP-143
OP-144 [TODO] Backlog operator improvement item OP-144
OP-145 [TODO] Backlog operator improvement item OP-145
OP-146 [TODO] Backlog operator improvement item OP-146
OP-147 [TODO] Backlog operator improvement item OP-147
OP-148 [TODO] Backlog operator improvement item OP-148
OP-149 [TODO] Backlog operator improvement item OP-149
OP-150 [TODO] Backlog operator improvement item OP-150
OP-151 [TODO] Backlog operator improvement item OP-151
OP-152 [TODO] Backlog operator improvement item OP-152
OP-153 [TODO] Backlog operator improvement item OP-153
OP-154 [TODO] Backlog operator improvement item OP-154
OP-155 [TODO] Backlog operator improvement item OP-155
OP-156 [TODO] Backlog operator improvement item OP-156
OP-157 [TODO] Backlog operator improvement item OP-157
OP-158 [TODO] Backlog operator improvement item OP-158
OP-159 [TODO] Backlog operator improvement item OP-159
OP-160 [TODO] Backlog operator improvement item OP-160
OP-161 [TODO] Backlog operator improvement item OP-161
OP-162 [TODO] Backlog operator improvement item OP-162
OP-163 [TODO] Backlog operator improvement item OP-163
OP-164 [TODO] Backlog operator improvement item OP-164
OP-165 [TODO] Backlog operator improvement item OP-165
OP-166 [TODO] Backlog operator improvement item OP-166
OP-167 [TODO] Backlog operator improvement item OP-167
OP-168 [TODO] Backlog operator improvement item OP-168
OP-169 [TODO] Backlog operator improvement item OP-169
OP-170 [TODO] Backlog operator improvement item OP-170
OP-171 [TODO] Backlog operator improvement item OP-171
OP-172 [TODO] Backlog operator improvement item OP-172
OP-173 [TODO] Backlog operator improvement item OP-173
OP-174 [TODO] Backlog operator improvement item OP-174
OP-175 [TODO] Backlog operator improvement item OP-175
OP-176 [TODO] Backlog operator improvement item OP-176
OP-177 [TODO] Backlog operator improvement item OP-177
OP-178 [TODO] Backlog operator improvement item OP-178
OP-179 [TODO] Backlog operator improvement item OP-179
OP-180 [TODO] Backlog operator improvement item OP-180
OP-181 [TODO] Backlog operator improvement item OP-181
OP-182 [TODO] Backlog operator improvement item OP-182
OP-183 [TODO] Backlog operator improvement item OP-183
OP-184 [TODO] Backlog operator improvement item OP-184
OP-185 [TODO] Backlog operator improvement item OP-185
OP-186 [TODO] Backlog operator improvement item OP-186
OP-187 [TODO] Backlog operator improvement item OP-187
OP-188 [TODO] Backlog operator improvement item OP-188
OP-189 [TODO] Backlog operator improvement item OP-189
OP-190 [TODO] Backlog operator improvement item OP-190
OP-191 [TODO] Backlog operator improvement item OP-191
OP-192 [TODO] Backlog operator improvement item OP-192
OP-193 [TODO] Backlog operator improvement item OP-193
OP-194 [TODO] Backlog operator improvement item OP-194
OP-195 [TODO] Backlog operator improvement item OP-195
OP-196 [TODO] Backlog operator improvement item OP-196
OP-197 [TODO] Backlog operator improvement item OP-197
OP-198 [TODO] Backlog operator improvement item OP-198
OP-199 [TODO] Backlog operator improvement item OP-199
OP-200 [TODO] Backlog operator improvement item OP-200
