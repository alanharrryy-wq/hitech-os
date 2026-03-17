from .path_rules import normalize_relpath

def reviewers_for_paths(paths, policy):
    mapping = policy.get("reviewer_map", {})
    assigned = set()

    for relpath in paths:
        relpath = normalize_relpath(relpath)
        matched = False

        for prefix, reviewers in mapping.items():
            if prefix == "default":
                continue
            prefix_norm = normalize_relpath(prefix)
            if relpath == prefix_norm or relpath.startswith(prefix_norm):
                for reviewer in reviewers:
                    assigned.add(reviewer)
                matched = True

        if not matched:
            for reviewer in mapping.get("default", []):
                assigned.add(reviewer)

    return sorted(assigned)
