from __future__ import annotations
import ast
import importlib
import pkgutil
import sys
sys.dont_write_bytecode = True
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENGINE = ROOT / "engine"
sys.path.insert(0, str(ENGINE))

def main() -> int:
    py_files = [p for p in (ENGINE / "autogit_engine").rglob("*.py") if "__pycache__" not in p.parts]
    for p in py_files:
        source = p.read_text(encoding="utf-8")
        compile(source, str(p), "exec")
        ast.parse(source, filename=str(p))
    for mod in pkgutil.walk_packages([str(ENGINE / "autogit_engine")], "autogit_engine."):
        importlib.import_module(mod.name)
    from autogit_engine.secret_scan import redact_literal_keys
    safe = "secret = scan_text(text)"
    assert redact_literal_keys(safe, code=True) == safe
    js_member = "const x={token:v[O].token,style:s};"
    assert redact_literal_keys(js_member, code=True) == js_member
    assert '"<REDACTED>"' in redact_literal_keys('token = "<REDACTED>"', code=True)
    assert 'password = "<REDACTED>"' == redact_literal_keys('password = "<REDACTED>"', code=True)
    assert 'token: "<REDACTED>"' == redact_literal_keys('token: abc12345xyz')
    from autogit_engine.paths import contains_local_path, redact_local_paths, repo_path
    from autogit_engine.sanitizers.code_sanitizer import sanitize_code_text
    html_regex = 'text = re.sub(r"(?is)<script.+?</script>", " ", text)'
    assert redact_local_paths(html_regex) == html_regex
    assert sanitize_code_text(html_regex) == html_regex
    assert not contains_local_path("</div>")
    assert not contains_local_path("/api/prismo/status")
    assert contains_local_path(r"F:\descargasf\autogit report.zip")
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        nested = repo_path(base, "a/b/c.py")
        assert nested == base / "a" / "b" / "c.py"
    print(f"AUTOGIT SELFTEST OK: {len(py_files)} python files")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
