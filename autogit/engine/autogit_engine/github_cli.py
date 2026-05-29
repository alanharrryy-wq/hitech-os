from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json
import re
import time
from .errors import GitHubError


@dataclass
class PullRequest:
    url: str
    number: str
    head: str
    base: str


class GitHub:
    def __init__(self, shell):
        self.sh = shell
        self.gh = self.sh.which("gh") or self.sh.which("gh.exe")
        if not self.gh:
            raise GitHubError("GitHub CLI gh not found", phase="github")

    def auth_status(self) -> None:
        self.sh.run([self.gh, "auth", "status"], check=True, timeout=120, name="gh_auth_status")

    def create_pr(self, title: str, body_file: str, base: str, head: str) -> PullRequest:
        r = self.sh.run(
            [self.gh, "pr", "create", "--base", base, "--head", head, "--title", title, "--body-file", body_file],
            check=True,
            timeout=300,
            name="gh_pr_create",
        )
        url = (r.stdout or "").strip().splitlines()[-1].strip()
        m = re.search(r"/pull/(\d+)", url)
        return PullRequest(url, m.group(1) if m else "", head, base)

    def checks_watch(self, pr_url: str) -> tuple[bool, str]:
        r = self.sh.run([self.gh, "pr", "checks", pr_url, "--watch", "--fail-fast"], timeout=1800, name="gh_pr_checks")
        text = (r.stdout or "") + "\n" + (r.stderr or "")
        return (r.code == 0 or "no check" in text.lower()), text

    def merge(self, pr_url: str, *, auto: bool = False, admin: bool = False, delete_branch: bool = False) -> tuple[bool, str]:
        cmd = [self.gh, "pr", "merge", pr_url, "--merge"]
        if auto:
            cmd.append("--auto")
        if admin:
            cmd.append("--admin")
        if delete_branch:
            cmd.append("--delete-branch")
        suffix = "admin" if admin else "auto" if auto else "normal"
        r = self.sh.run(cmd, timeout=600, name=f"gh_pr_merge_{suffix}")
        return r.code == 0, (r.stdout or "") + "\n" + (r.stderr or "")

    def view(self, pr_url: str) -> dict:
        fields = "state,mergedAt,mergeStateStatus,mergeable,autoMergeRequest,url,headRefName,headRefOid,baseRefName"
        r = self.sh.run([self.gh, "pr", "view", pr_url, "--json", fields], timeout=120, name="gh_pr_view")
        if r.code != 0:
            return {"_error": r.stderr or r.stdout, "_code": r.code}
        try:
            return json.loads(r.stdout or "{}")
        except Exception as exc:
            return {"_parse_error": repr(exc), "raw": r.stdout}

    def wait_merged(self, pr_url: str, seconds: int, poll: int = 30) -> tuple[str, dict]:
        start = time.time()
        last = {}
        while time.time() - start < seconds:
            last = self.view(pr_url)
            if last.get("mergedAt"):
                return "merged", last
            if str(last.get("state", "")).upper() == "CLOSED":
                return "closed_unmerged", last
            time.sleep(poll)
        return "pending", last

    def capture_failed_check_logs(self, pr_url: str, report_dir: Path, tag: str = "") -> None:
        suffix = ("_" + tag) if tag else ""
        logs_dir = report_dir / "logs"
        logs_dir.mkdir(parents=True, exist_ok=True)
        r = self.sh.run([self.gh, "pr", "checks", pr_url, "--json", "name,state,link"], timeout=120, name=f"gh_pr_checks_json{suffix}")
        (report_dir / f"gh_pr_checks_json{suffix}.txt").write_text((r.stdout or "") + "\n" + (r.stderr or ""), encoding="utf-8")
        if r.code != 0:
            return
        try:
            checks = json.loads(r.stdout or "[]")
        except Exception:
            return
        (report_dir / f"gh_pr_checks_parsed{suffix}.json").write_text(json.dumps(checks, indent=2, ensure_ascii=False), encoding="utf-8")
        failed = [c for c in checks if str(c.get("state", "")).lower() in {"fail", "failure", "cancelled", "timed_out", "action_required"}]
        for idx, check in enumerate(failed, 1):
            name = re.sub(r"[^A-Za-z0-9_.-]+", "_", str(check.get("name", f"check_{idx}")))[:80]
            link = str(check.get("link", ""))
            run_id_match = re.search(r"/actions/runs/(\d+)", link)
            if run_id_match:
                run_id = run_id_match.group(1)
                self.sh.run([self.gh, "run", "view", run_id, "--log-failed"], timeout=600, name=f"failed_check_{idx}_{name}{suffix}")
