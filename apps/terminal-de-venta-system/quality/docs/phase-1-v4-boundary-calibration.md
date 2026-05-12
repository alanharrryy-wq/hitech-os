# Phase 1 V4 Boundary Calibration

V4 tightens the boundary scanner after the first calibrated `quality:commit` run.

The previous scanner still blocked on plain vocabulary such as `backoffice` in runtime labels, READMEs and UI copy. That is too coarse for a serious architecture gate.

V4 keeps the architecture and Tablet sovereignty gates strict, but changes the blocking rule:

- Hard runtime imports or dynamic imports across forbidden boundaries still block.
- Runtime HTTP/fetch calls that require backoffice/Cloudflare endpoints still block.
- Plain text such as labels, copy, comments and docs becomes evidence-only.
- README and markdown files are non-runtime context.

This preserves the core contract: Tablet must operate alone. It avoids treating vocabulary as a dependency.
