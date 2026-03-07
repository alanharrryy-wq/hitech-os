from __future__ import annotations


class TrendAnalyzer:
    def compare(self, previous_snapshot: dict | None, current_snapshot: dict) -> dict:
        current_fps = set(current_snapshot.get('active_fingerprints', []))
        if not previous_snapshot:
            return {
                'has_previous': False,
                'new_findings': len(current_fps),
                'resolved_findings': 0,
                'unchanged_findings': 0,
                'delta_total_findings': len(current_fps),
            }
        previous_fps = set(previous_snapshot.get('active_fingerprints', []))
        previous_total = len(previous_fps)
        return {
            'has_previous': True,
            'new_findings': len(current_fps - previous_fps),
            'resolved_findings': len(previous_fps - current_fps),
            'unchanged_findings': len(current_fps & previous_fps),
            'delta_total_findings': len(current_fps) - previous_total,
        }
