from __future__ import annotations

"""Evidence graph base para findings, fixes y verificaciones."""

from .session import DiagnosticSession



def _dedupe(values: list[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for value in values:
        text = str(value or "").strip()
        if not text or text in seen:
            continue
        seen.add(text)
        ordered.append(text)
    return ordered


def annotate_evidence_graph(session: DiagnosticSession) -> DiagnosticSession:
    artifact_ids = {artifact.artifact_id for artifact in session.artifacts if artifact.artifact_id}
    finding_ids = {finding.finding_id for finding in session.findings if finding.finding_id}

    for finding in session.findings:
        finding.evidence_refs = _dedupe(list(finding.evidence_refs or []))
        finding.cross_signal_support = _dedupe(list(finding.cross_signal_support or []))
        finding.contradictions = _dedupe(list(finding.contradictions or []))
        finding.evidence_refs = [ref for ref in finding.evidence_refs if ref in artifact_ids]
        finding.cross_signal_support = [
            ref for ref in finding.cross_signal_support if ref in finding_ids and ref != finding.finding_id
        ]
        finding.contradictions = [
            ref for ref in finding.contradictions if ref in finding_ids and ref != finding.finding_id
        ]
        finding.evidence_count = len(finding.evidence_refs)
        if finding.confidence_score is None:
            finding.confidence_score = finding.confidence
        if not finding.confidence_reason:
            finding.confidence_reason = (
                f"{finding.evidence_count} evidence refs enlazadas"
                if finding.evidence_count
                else "sin evidencia enlazada todavía"
            )

    for recommendation in session.recommendations:
        recommendation.evidence_refs = _dedupe(list(recommendation.evidence_refs or []))
        recommendation.evidence_refs = [ref for ref in recommendation.evidence_refs if ref in artifact_ids]

    for proposal in session.fix_proposals:
        metadata = proposal.metadata if isinstance(proposal.metadata, dict) else {}
        evidence_refs = _dedupe(list(metadata.get("evidence_refs", []) or []))
        cross_support = _dedupe(list(metadata.get("cross_signal_support", []) or []))
        contradictions = _dedupe(list(metadata.get("contradictions", []) or []))
        evidence_refs = [ref for ref in evidence_refs if ref in artifact_ids]
        cross_support = [ref for ref in cross_support if ref in finding_ids]
        contradictions = [ref for ref in contradictions if ref in finding_ids]
        metadata["evidence_refs"] = evidence_refs
        metadata["cross_signal_support"] = cross_support
        metadata["contradictions"] = contradictions
        proposal.metadata = metadata
        proposal.evidence_count = len(evidence_refs)
        proposal.cross_signal_support = cross_support
        proposal.contradictions = contradictions
        if not proposal.confidence_reason:
            proposal.confidence_reason = (
                f"{proposal.evidence_count} evidence refs enlazadas"
                if proposal.evidence_count
                else "sin evidencia enlazada todavía"
            )

    for verification in session.verification_results:
        verification.evidence_refs = _dedupe(list(verification.evidence_refs or []))
        verification.evidence_refs = [ref for ref in verification.evidence_refs if ref in artifact_ids]

    session.options["evidence_graph"] = {
        "artifact_count": len(artifact_ids),
        "finding_count": len(finding_ids),
        "findings_with_evidence": sum(1 for item in session.findings if item.evidence_refs),
        "fixes_with_evidence": sum(1 for item in session.fix_proposals if item.evidence_count),
        "verifications_with_evidence": sum(1 for item in session.verification_results if item.evidence_refs),
    }
    return session
