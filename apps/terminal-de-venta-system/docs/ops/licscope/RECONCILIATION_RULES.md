# RECONCILIATION_RULES

| rule | status | evidence |
| --- | --- | --- |
| venta sin provenance | PASS | docs/ops/licscope/relationship_edges.json |
| device sin licencia | PASS | docs/ops/licscope/relationship_edges.json |
| license sin client | PASS | docs/ops/licscope/relationship_edges.json |
| client sin license | PASS | docs/ops/licscope/relationship_edges.json |
| business sin client/scope | PASS | docs/ops/licscope/relationship_edges.json |
| store sin business | PASS | docs/ops/licscope/relationship_edges.json |
| terminal sin store | PASS | docs/ops/licscope/relationship_edges.json |
| cash session sin user/terminal | PASS | docs/ops/licscope/relationship_edges.json |
| sale sin cash session | PASS | docs/ops/licscope/relationship_edges.json |
| sale sin line | PASS | docs/ops/licscope/relationship_edges.json |
| sale sin tender | PASS | docs/ops/licscope/relationship_edges.json |
| outbox sin sale | PASS | docs/ops/licscope/relationship_edges.json |
| sync dormido | PASS | docs/ops/licscope/relationship_edges.json |
| duplicate device id | PASS | docs/ops/licscope/relationship_edges.json |
| duplicate license id | PASS | docs/ops/licscope/relationship_edges.json |
| duplicate setup code | PASS | docs/ops/licscope/relationship_edges.json |
| duplicate sale id | PASS | docs/ops/licscope/relationship_edges.json |
| duplicate idempotencyKey | PASS | docs/ops/licscope/relationship_edges.json |
| stale heartbeat | PASS | docs/ops/licscope/relationship_edges.json |
| stale sync checkpoint | PASS | docs/ops/licscope/relationship_edges.json |
| stale outbox event | PASS | docs/ops/licscope/relationship_edges.json |
| stale cash session | PASS | docs/ops/licscope/relationship_edges.json |
| stale device | PASS | docs/ops/licscope/relationship_edges.json |
| missing audit for claim | PASS | docs/ops/licscope/relationship_edges.json |
| missing audit for setup | PASS | docs/ops/licscope/relationship_edges.json |
| missing audit for revoke | PASS | docs/ops/licscope/relationship_edges.json |
| missing audit for renewal | PASS | docs/ops/licscope/relationship_edges.json |
| missing audit for device replacement | PASS | docs/ops/licscope/relationship_edges.json |
