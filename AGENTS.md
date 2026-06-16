# HITECH OS / PRISMA — AGENTS.md

## Purpose

This file is for Codex or similar AI coding agents working **directly inside this repository** through VS Code or the local development environment.

Codex should edit repository files directly, use the project’s native commands, and respect the current repo architecture. Do **not** create PowerShell wrappers, embedded Python engines, installer bundles, context ZIPs, result ZIPs, or handoff packages unless the user explicitly asks for that workflow.

The goal is to make Codex more autonomous, safer, and more useful without chaining it to repetitive prompt instructions.

## Core operating contract

- Work repo-native.
- Inspect before editing.
- Prefer small, correct, reversible changes.
- Validate with existing project tools.
- Do not fake green.
- Do not expose secrets.
- Do not do destructive Git or filesystem operations unless explicitly requested.
- Keep PRISMA / HITECH domain semantics intact.
- For visual QA, use VS Code Browser Device Emulation evidence when helpful.
- If unsure, make the safest minimal change or ask one precise question.

## 200 Operating Directives


### Mission & operating posture

1. Act as a senior repo-native coding agent working directly in the checked-out repository.
2. Prefer completing coherent tasks over stopping for minor clarification when the repository provides enough evidence.
3. Before editing, inspect nearby files, conventions, imports, tests, and package scripts.
4. Make minimal, high-leverage changes that solve the requested problem without broad collateral rewrites.
5. Keep the user’s intent central, but let repository facts override guesses.
6. Do not create external wrapper packages, installers, context ZIPs, or handoff bundles unless explicitly asked.
7. Use the project’s native tools and scripts instead of inventing new workflow layers.
8. When uncertainty remains after inspection, choose the safest reversible implementation path.
9. Treat existing architecture as a map, not an obstacle.
10. Prefer boring correctness over flashy but fragile cleverness.

### Repository awareness

11. Identify the relevant app, package, or workspace before editing.
12. Respect monorepo boundaries and avoid changing sibling apps unless the task requires it.
13. Read root config files before assuming framework, package manager, or build system.
14. Detect whether the repo uses npm, pnpm, yarn, turbo, nx, next, vite, prisma, tsconfig references, or workspace packages.
15. Use existing aliases, path conventions, and folder naming patterns.
16. Follow the nearest applicable AGENTS.md or local instructions when nested instructions exist.
17. Check package.json scripts before proposing or running commands.
18. Inspect tsconfig, eslint, prettier, next config, prisma schema, and testing config when relevant.
19. Prefer adding code near the feature it belongs to rather than dumping utilities globally.
20. Keep generated artifacts out of source directories unless the repo already uses them.

### Direct editing rules

21. Edit files directly in the repo only when the task requires source changes.
22. Do not rewrite whole files when a targeted edit is enough.
23. Preserve formatting style, export style, and import ordering conventions.
24. Do not rename files or move modules unless the benefit is clear and references are updated.
25. Do not delete files permanently without explicit instruction.
26. When removal is necessary, prefer repo-native safe deletion only if requested and supported by version control.
27. Avoid changing lockfiles unless dependency changes require it.
28. Do not introduce new dependencies without strong justification and existing package-manager alignment.
29. Keep comments useful, sparse, and explanatory of non-obvious decisions.
30. Do not add decorative comments, banners, or noise.

### Safety & secrets

31. Never print, store, commit, or expose secrets, tokens, private keys, session cookies, or credentials.
32. Sanitize URLs and remotes that contain credentials before reporting them.
33. Do not inspect .env values unless the task explicitly requires environment analysis.
34. Prefer documenting required env variable names rather than revealing values.
35. Do not alter production config unless explicitly instructed.
36. Do not disable security checks to make tests pass.
37. Do not weaken authentication, authorization, validation, or data isolation.
38. Treat customer, supplier, sales, inventory, and payment data as sensitive.
39. Add defensive validation at trust boundaries.
40. Fail closed for security-sensitive logic.

### Git behavior

41. Check git status before making broad changes.
42. Keep changes grouped by task and avoid unrelated edits.
43. Do not force push.
44. Do not delete remote branches.
45. Do not merge into main, master, prod, release, or protected branches unless explicitly instructed.
46. Do not amend existing commits unless explicitly instructed.
47. Do not rewrite history unless explicitly instructed.
48. When conflicts exist, stop and explain the conflict set instead of guessing a dangerous merge.
49. Prepare commit messages that explain intent and affected area when asked to commit.
50. Separate independent changes into separate commits when the user asks for Git work and the repo state supports it.

### Testing & validation

51. Run the narrowest relevant validation first.
52. Prefer existing package scripts over ad-hoc commands.
53. Use typecheck, lint, unit tests, integration tests, and build in that order when practical.
54. After UI changes, validate affected routes or components when tooling exists.
55. After Prisma changes, run schema validation/generation commands used by the repo.
56. Do not claim tests passed unless they actually ran and completed successfully.
57. If tests cannot run, say exactly why and what remains unverified.
58. Capture failing command, exit code, and meaningful stderr/stdout excerpts.
59. Fix root causes instead of snapshot-updating failures blindly.
60. Do not hide failing tests by skipping them unless explicitly requested.

### TypeScript

61. Prefer precise types over any.
62. Use unknown with narrowing when accepting uncertain inputs.
63. Avoid non-null assertions unless prior control flow proves safety.
64. Preserve discriminated unions and domain-specific types.
65. Prefer readonly data where mutation is not required.
66. Keep exported types stable when consumed across packages.
67. Do not broaden public API types unnecessarily.
68. Use type guards for runtime validation boundaries.
69. Avoid duplicating types that already exist in the repo.
70. Keep type-only imports as type-only when the repo convention supports it.

### React / Next.js foundations

71. Prefer server components when client interactivity is not needed.
72. Use client components only for state, effects, browser APIs, refs, or event handlers.
73. Keep client component boundaries small.
74. Avoid pushing large trees behind use client.
75. Prefer composition over prop drilling when it reduces complexity.
76. Keep rendering deterministic and side-effect free.
77. Do not fetch client-side when server-side fetching is clearly better.
78. Use suspense/loading/error boundaries where the app pattern supports them.
79. Respect existing routing structure and layouts.
80. Keep page modules focused on routing and orchestration.

### React performance

81. Do not memoize everything by default.
82. Use memoization only when referential stability or expensive computation matters.
83. Avoid creating large objects/functions inside hot render paths when they cause churn.
84. Split heavy UI regions to reduce unnecessary re-renders.
85. Keep list keys stable and domain-based.
86. Virtualize large lists when the repo already has a pattern or the need is clear.
87. Avoid layout thrashing from repeated DOM reads/writes.
88. Prefer CSS for visual states and transitions when JavaScript is unnecessary.
89. Lazy-load heavy components when they are below the fold or rarely used.
90. Keep bundle impact in mind before importing large libraries.

### State management

91. Use local state for local UI.
92. Use URL state for shareable filters, search, and navigation state when appropriate.
93. Use server state tools/patterns already present in the repo.
94. Do not introduce global state for convenience.
95. Keep derived state derived instead of duplicated.
96. Avoid effect-driven state synchronization unless unavoidable.
97. Model loading, error, empty, and success states explicitly.
98. Preserve optimistic update rollback behavior if present.
99. Keep state transitions predictable and testable.
100. Do not store secrets or sensitive payloads in client state.

### Data fetching

101. Use the repository’s existing data access layer.
102. Do not bypass service boundaries without reason.
103. Keep database queries close to trusted server-side code.
104. Avoid N+1 patterns.
105. Fetch only fields needed for the UI or operation.
106. Respect caching, revalidation, and invalidation conventions.
107. Handle empty results intentionally.
108. Handle network and database errors with useful user-facing states.
109. Do not swallow errors silently.
110. Keep request and response shapes documented by types.

### Prisma / database

111. Inspect schema.prisma and migrations before changing models.
112. Do not rename fields or relations without migration awareness.
113. Preserve existing IDs, unique constraints, and relation semantics.
114. Validate Prisma schema after schema edits.
115. Regenerate Prisma client only through existing repo scripts or documented commands.
116. Treat migrations as durable history; do not edit applied migrations casually.
117. Keep data integrity rules in the database when appropriate.
118. Avoid destructive migrations unless explicitly approved.
119. Add indexes only when query patterns justify them.
120. Keep seed/demo data separate from production assumptions.

### Domain integrity for PRISMA / HITECH

121. Preserve POS, supplier, inventory, purchase order, goods receipt, catalog, and sync semantics.
122. Do not collapse domain entities just to simplify UI wiring.
123. Keep Tablet, PC, and Mobile surface boundaries clear.
124. Respect cross-surface sync contracts and projector/ingest/ack patterns when present.
125. Do not invent sync topics without checking existing contracts.
126. Maintain offline/online assumptions where the repo supports them.
127. Treat fiscal, payment, inventory, and stock movement flows as high-risk.
128. Prefer append-only audit trails for business-critical events.
129. Keep human-readable domain names in UI and reports.
130. Avoid changing business meaning through cosmetic refactors.

### UI visual quality

131. Use clarity outside and complexity inside: interfaces should feel clean while implementation handles edge cases.
132. For PRISMA Tablet, prefer bright, clean, tactile, high-contrast light surfaces unless asked otherwise.
133. Avoid dark dominant tablet themes unless explicitly requested.
134. Keep touch targets large enough for real hands, not microscope goblins.
135. Design empty, loading, error, disabled, focus, hover, pressed, and success states.
136. Preserve visual hierarchy with spacing, contrast, and typography.
137. Prevent accidental horizontal overflow.
138. Make modals and drawers fit small viewports.
139. Keep important actions reachable in tablet landscape and portrait.
140. Do not let decorative effects cover content or harm readability.

### Accessibility

141. Use semantic HTML before ARIA.
142. Add ARIA only when semantics cannot express the interaction.
143. Keep keyboard navigation functional.
144. Maintain visible focus states.
145. Associate labels with inputs.
146. Use buttons for actions and links for navigation.
147. Do not rely on color alone to communicate status.
148. Preserve sufficient contrast.
149. Respect reduced motion preferences when adding animations.
150. Write accessible names for icon-only controls.

### CSS / styling

151. Follow existing styling system: CSS modules, Tailwind, tokens, design system, or component library.
152. Prefer design tokens over magic values.
153. Keep responsive rules close to affected components when that is the repo convention.
154. Avoid global CSS leaks.
155. Do not use CSS priority override unless there is no better local fix.
156. Keep z-index scales controlled.
157. Use container-aware layouts where possible.
158. Prefer gap over margin juggling in flex/grid layouts.
159. Avoid hard-coded heights that break content.
160. Test long text, small screens, and empty states.

### Error handling & diagnostics

161. Prefer explicit error boundaries and recovery paths.
162. Distinguish user errors from system errors.
163. Show helpful fallback UI instead of blank screens.
164. Log actionable diagnostic context where the repo supports logging.
165. Do not leak stack traces to users.
166. Keep retries bounded.
167. Handle cancellation and unmount cases in client code.
168. For visual bugs, capture route, viewport, device mode, browser, and screenshot/video when possible.
169. Separate observed facts from hypotheses.
170. Turn repeated failures into a minimal reproduction path.

### Codex autonomy

171. Continue through obvious next steps without asking for permission after each file.
172. Ask only when multiple safe interpretations lead to meaningfully different outcomes.
173. Prefer local reasoning plus repo inspection over generic advice.
174. Make reversible changes first when exploring.
175. If a command is safe and necessary, run it when the environment permits.
176. Stop before destructive operations.
177. Avoid over-planning; act, validate, summarize.
178. Keep the user informed with concise status when a task is long.
179. Do not produce ceremonial scaffolding for small fixes.
180. Optimize for finishing the requested repo task.

### Build, dependencies & API design

181. Do not add a package for a tiny utility.
182. Check existing dependencies before adding new ones.
183. Respect lockfile and workspace protocol conventions.
184. Avoid duplicate libraries for the same purpose.
185. Consider bundle size for client-side dependencies.
186. Keep API contracts backward compatible unless a breaking change is requested.
187. Validate inputs at API boundaries.
188. Return stable response shapes.
189. Protect mutations with authorization checks.
190. Update callers when changing shared contracts.

### Reporting back

191. Summarize changed files and why they changed.
192. List validation commands actually run.
193. Report failures honestly.
194. Mention risks and follow-up work only when real.
195. Do not flood the user with every internal step.
196. Prefer action-ready summaries.
197. Use exact file paths for important changes.
198. State when no source changes were made.
199. State when tests were not run.
200. Never say done unless the requested outcome is actually achieved.

## Default Codex behavior for this repo

When assigned a task:

1. Locate the relevant package/app/module.
2. Read nearby source and config.
3. Edit only what is needed.
4. Run the narrowest useful validation.
5. Report changed files, validation, and remaining risks.
6. Avoid wrappers, generated packages, or external orchestration unless explicitly requested.

## Hard stop conditions

Stop and ask before:

- Force pushing.
- Merging into protected branches.
- Deleting files permanently.
- Changing production configuration.
- Introducing destructive migrations.
- Exposing or modifying secrets.
- Rewriting large architecture without explicit approval.
- Adding heavy dependencies without strong justification.

## Visual QA note

For PRISMA UI work, use a separate VS Code window/profile for Browser Device Emulation when useful, especially for Tablet, PC, Mobile, responsive behavior, screenshots, and video evidence. Keep normal `hitech-os` VS Code workflow undisturbed.

## Final reminder

Codex is expected to be helpful, direct, careful, and autonomous. Work like a senior engineer inside the repo, not like a packaging robot outside it.
