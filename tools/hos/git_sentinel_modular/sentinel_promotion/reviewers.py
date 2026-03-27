from __future__ import annotations

from .path_rules import classify_many

def reviewers_for_paths(paths: list[str]) -> list[str]:
    buckets = classify_many(paths)
    reviewers = {"platform", "repo-owner"}
    if buckets["high"]:
        reviewers.add("security-review")
    return sorted(reviewers)
