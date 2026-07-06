# ORPHAN_DETECTOR_RULES

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
| missing audit for claim | PASS | docs/ops/licscope/relationship_edges.json |
| missing audit for setup | PASS | docs/ops/licscope/relationship_edges.json |
| missing audit for revoke | PASS | docs/ops/licscope/relationship_edges.json |
| missing audit for renewal | PASS | docs/ops/licscope/relationship_edges.json |
| missing audit for device replacement | PASS | docs/ops/licscope/relationship_edges.json |
