# One-Button v1.2 Locking and Stale Rules

## Document Status
- Status: Frozen
- Version: v1.2
- Scope: project-scoped lock lifecycle for one-button sessions

## 1. Why locking is mandatory
One-button mutates project-scoped runtime state. Without a project-scoped lock, two simultaneous launches could:
- create competing rounds,
- corrupt ledger assumptions,
- produce duplicate or divergent session zips,
- misreport readiness and status to the operator.

The lock is therefore not optional for any real execution path.

## 2. Lock path
`F:\repos\hitech-os\tools\orchestrator_factory\ops\projects\<project_id>\state\locks\one_button.lock.json`

There is exactly one active lock file per project for the one-button launcher.

## 3. Required lock fields
The lock file must contain, at minimum:

```json
{
  "lock_id": "lock_...",
  "session_id": "sess_...",
  "project_id": "hitech-os",
  "pid": 1234,
  "host": "DESKTOP-ABC",
  "acquired_at_utc": "2026-03-27T18:22:10Z",
  "heartbeat_at_utc": "2026-03-27T18:22:25Z",
  "ttl_seconds": 60
}
```

## 4. Acquisition rules
### 4.1 Exclusive creation
The implementation must attempt exclusive creation rather than overwriting blindly. If the lock already exists, the launcher must evaluate its liveness before deciding whether to abort or recover.

### 4.2 Lock ownership
Only the launcher instance that successfully created the lock may treat itself as lock owner. Ownership must remain associated with:
- `lock_id`
- `session_id`
- `pid`
- `host`

## 5. Heartbeat rules
- Default heartbeat interval: 15 seconds
- Default TTL: 60 seconds

The owner should refresh `heartbeat_at_utc` periodically while the session is still running. This allows later processes to distinguish a live run from abandoned state.

## 6. Liveness model
The lock state must be evaluated using a cross-check of **host**, **PID**, and **TTL**.

### 6.1 Live lock
A lock is considered **live** only when all of the following are true:
1. the `host` matches the current machine,
2. the `pid` is still alive on that host,
3. `heartbeat_at_utc` is still within `ttl_seconds`.

### 6.2 Stale lock
A lock is considered **stale** when:
1. the `host` matches the current machine,
2. the `pid` is not alive,
3. the heartbeat is older than `ttl_seconds`.

### 6.3 Cross-host lock
A special rule applies when the lock was created on a different host:
- if TTL has **not** expired, assume the lock is valid,
- if TTL **has** expired, treat it as a **stale-safe candidate**.

Rationale:
- the local machine cannot verify a remote PID directly,
- TTL prevents immediate and dangerous theft,
- stale-safe status still requires explicit, conservative recovery logic.

## 7. Recovery rules
### 7.1 Normal failure on live lock
If the lock is live:
- abort,
- return exit code `10`,
- report the blocking lock details to the operator.

### 7.2 Automatic stale cleanup
If the lock is stale on the same host:
- the launcher may clean it up safely,
- should record a warning issue,
- may continue acquisition.

### 7.3 Stale-safe candidate cleanup
If the lock is from another host and TTL has expired:
- treat it as a stale-safe candidate,
- do not silently assume safety,
- allow takeover only via defined recovery behavior,
- recommended: require `--force-lock-steal` unless project policy explicitly allows automatic stale-safe cleanup.

### 7.4 Force lock steal
`--force-lock-steal` is only valid when the existing lock is:
- stale, or
- stale-safe candidate.

It must never override a same-host live lock.

## 8. Release rules
Lock release must happen in `finally` so normal errors do not strand ownership. If release fails, the launcher should:
- emit a warning issue,
- attempt best-effort cleanup,
- never misreport the session as cleanly completed without surfacing the problem.

## 9. Observability requirements
At minimum, lock events should be visible in logs and optionally in issues:
- lock acquired,
- lock heartbeat refreshed,
- live lock blocked execution,
- stale lock recovered,
- stale-safe candidate encountered,
- lock released,
- lock release warning or failure.

## 10. Failure examples
### Bad behavior
- overwriting an existing lock immediately,
- declaring a same-host lock stale without checking the PID,
- stealing a cross-host lock before TTL expiry,
- suppressing lock recovery warnings.

### Correct behavior
- fail fast on same-host live lock,
- recover safely from stale same-host lock,
- require conservative handling for expired cross-host locks.

## 11. Implementation notes
The lock subsystem should remain narrow:
- read/write JSON,
- probe process liveness on Windows,
- compare timestamps,
- expose a small decision API to the session flow.

Do not spread lock policy across wrapper, CLI, and exporter layers. Centralize it in the lock component.
