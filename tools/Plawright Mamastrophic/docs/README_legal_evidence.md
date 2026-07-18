# Mamastrophic Legal Evidence Adapter

`mamlegal1` adds a conditional legal-evidence profile to the existing Plawright Mamastrophic installation.

## Canonical tool root

`F:\repos\hitech-os\tools\Plawright Mamastrophic`

## Installed entry point

`LEGAL_RUN.ps1`

The legacy `RUN.ps1`, normal menus, discovery, quick, full, critical and visualqa modes keep their existing interface. The patched capture engines only enable legal behavior when:

`PRISMA_MAM_LEGAL_EVIDENCE=1`

`LEGAL_RUN.ps1` sets that variable and runs one surface at a time. Each surface may still use internal Playwright workers and shards.

## Legal profile protections

- no process start beyond the explicitly requested child PowerShell capture;
- no dev server start;
- no process kill;
- no port freeing;
- no DB writes;
- no deploy;
- no dependency installation;
- no Git writes;
- no Playwright trace or automatic failure screenshot in legal mode;
- browser-side masking before Mamastrophic screenshots;
- console and network URL sanitization;
- one final ZIP in `F:\descargasf`;
- NDC-compatible evidence and chain of custody.

## Example

```powershell
& 'F:\repos\hitech-os\tools\Plawright Mamastrophic\LEGAL_RUN.ps1' -Surface all -Workers 6 -Shards 1 -AllowPartial
```

## Final package members

- `LEGAL_RUN_MANIFEST.json`
- `LEGAL_INPUT_PACKAGE.json`
- `CANDIDATES.ndc.json`
- `EVIDENCE_INDEX.json`
- `PROVES_DOES_NOT_PROVE.json`
- `CHAIN_OF_CUSTODY.json`
- `REDACTION_REPORT.json`
- `CONFLICTS_AND_UNKNOWNS.md`
- `SUMMARY.md`
- `CONTINUATION.md`
- `ARTIFACT_HASHES.sha256`
- `raw_outputs/`

The output is technical runtime evidence. It is not a legal opinion, compliance certification, IP ownership proof or production-readiness certificate.
