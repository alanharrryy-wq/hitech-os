from __future__ import annotations

from capatch_verify.registry import run_required_verifiers


def _write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def test_visual_gate_is_delta_aware_for_legacy_css_module(tmp_path):
    rel = "products/tablet/app/components/pos/pos.module.css"
    target = tmp_path / rel
    checkpoint = tmp_path / "checkpoint" / rel
    before = "\n".join([f".legacy{i}{{ color:red; }}" for i in range(60)]) + "\n.mask{ mask: linear-gradient(#000 0 0); }\n"
    after = before + ".newMask{ -webkit-mask: linear-gradient(#000 0 0); mask: linear-gradient(#000 0 0); }\n"
    _write(target, after)
    _write(checkpoint, before)
    rows = run_required_verifiers([rel], ["visual-static-gates"], {"root_dir": str(tmp_path), "checkpoint_dir": str(tmp_path / "checkpoint")})
    assert rows and rows[0]["ok"], rows
    assert rows[0]["metrics"]["baseline_available"] is True
    assert rows[0]["metrics"]["important_delta"] == 0
    assert rows[0]["metrics"]["mask_dark_hits_ignored"]


def test_visual_gate_fails_only_on_new_important_delta(tmp_path):
    rel = "products/tablet/app/components/pos/pos.module.css"
    target = tmp_path / rel
    checkpoint = tmp_path / "checkpoint" / rel
    before = ".btn{ color:red; }\n"
    after = ".btn{ color:red; background:white; border-color:red; }\n"
    _write(target, after)
    _write(checkpoint, before)
    rows = run_required_verifiers([rel], ["visual-static-gates"], {"root_dir": str(tmp_path), "checkpoint_dir": str(tmp_path / "checkpoint"), "visual_important_delta_limit": 2})
    assert rows and not rows[0]["ok"], rows
    assert "too many new" in rows[0]["detail"]


def test_visual_gate_ignores_mask_black_but_fails_new_background_black(tmp_path):
    rel = "products/tablet/app/components/pos/pos.module.css"
    target = tmp_path / rel
    checkpoint = tmp_path / "checkpoint" / rel
    before = ".btn{ background:white; }\n.mask{ mask: linear-gradient(#000 0 0); }\n"
    after = before + ".danger{ background:#000; }\n"
    _write(target, after)
    _write(checkpoint, before)
    rows = run_required_verifiers([rel], ["visual-static-gates"], {"root_dir": str(tmp_path), "checkpoint_dir": str(tmp_path / "checkpoint")})
    assert rows and not rows[0]["ok"], rows
    assert "new risky dark Tablet theme tokens" in rows[0]["detail"]


def test_visual_gate_warns_not_hard_for_large_legacy_without_baseline(tmp_path):
    rel = "products/tablet/app/components/pos/pos.module.css"
    target = tmp_path / rel
    huge = "\n".join([f".legacy{i}{{ color:red; }}" for i in range(60)]) + "\n.mask{ mask: linear-gradient(#000 0 0); }\n"
    _write(target, huge)
    rows = run_required_verifiers([rel], ["visual-static-gates"], {"root_dir": str(tmp_path)})
    assert rows and rows[0]["ok"], rows
    assert rows[0]["metrics"]["legacy_debt"] is True
    assert rows[0]["metrics"]["warnings"]
