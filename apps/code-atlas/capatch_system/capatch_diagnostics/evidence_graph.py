from __future__ import annotations

"""Evidence graph base para findings, fixes y verificaciones."""

from .session import DiagnosticSession



def annotate_evidence_graph(session: DiagnosticSession) -> DiagnosticSession:
    artifact_ids = {artifact.artifact_id for artifact in session.artifacts}
    finding_ids = {finding.finding_id for finding in session.findings}

    for finding in session.findings:
        finding.evidence_refs = [ref for ref in finding.evidence_refs if ref]
        finding.evidence_count = sum(1 for ref in finding.evidence_refs if ref in artifact_ids)
        if not finding.confidence_reason:
            finding.confidence_reason = (
                f"{finding.evidence_count} evidence refs" if finding.evidence_count else "sin evidencia enlazada todavía"
            )
        finding.cross_signal_support = [ref for ref in finding.cross_signal_support if ref in finding_ids and ref != finding.finding_id]

    for proposal in session.fix_proposals:
        proposal.evidence_count = sum(1 for ref in proposal.metadata.get("evidence_refs", []) if ref in artifact_ids)
        if not proposal.confidence_reason:
            proposal.confidence_reason = (
                f"{proposal.evidence_count} evidence refs" if proposal.evidence_count else "sin evidencia enlazada todavía"
            )

    for verification in session.verification_results:
        verification.evidence_refs = [ref for ref in verification.evidence_refs if ref in artifact_ids]

    return session
