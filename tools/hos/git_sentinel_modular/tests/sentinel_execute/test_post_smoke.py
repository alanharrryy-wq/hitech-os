from pathlib import Path

from sentinel_execute.post_smoke import run_post_execution_smoke
from sentinel_execute.policy_loader import default_policy

def test_post_smoke_catches_bad_python(tmp_path):
    target = tmp_path / "target"
    (target / "tools").mkdir(parents=True, exist_ok=True)
    (target / "tools" / "bad.py").write_text("def broken(:\n", encoding="utf-8")

    result = run_post_execution_smoke(
        target_root=target,
        execution_result={
            "applied": [{"path": "tools/bad.py", "action": "add"}],
        },
        policy=default_policy(),
    )

    assert result["ok"] is False
    assert any("python_parse_failed_after_apply:tools/bad.py" == x for x in result["failures"])
