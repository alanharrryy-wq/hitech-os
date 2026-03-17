from sentinel_cutover.preflight import run_preflight

def test_preflight_fails_when_files_are_missing(tmp_path):
    result = run_preflight(tmp_path)
    assert result["ok"] is False
    assert any("missing_required_file:" in item for item in result["issues"])
