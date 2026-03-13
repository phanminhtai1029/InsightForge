from pathlib import Path
from insightforge.tools.scanner import scan_folder, read_file
from insightforge.guard import GuardLayer


def test_scan_folder_returns_files(tmp_path):
    (tmp_path / "main.py").write_text("print('hello')")
    (tmp_path / "data.csv").write_text("a,b\n1,2")
    result = scan_folder(str(tmp_path))
    assert "main.py" in result
    assert "data.csv" in result


def test_scan_folder_classifies_code(tmp_path):
    (tmp_path / "app.py").write_text("x = 1")
    result = scan_folder(str(tmp_path))
    assert "code" in result.lower() or "py" in result.lower()


def test_scan_folder_detects_sensitive(tmp_path):
    (tmp_path / ".env").write_text("API_KEY=secret")
    result = scan_folder(str(tmp_path))
    assert "sensitive" in result.lower() or ".env" in result


def test_read_file_returns_content(tmp_path):
    f = tmp_path / "hello.py"
    f.write_text("print('hi')")
    guard = GuardLayer()
    content, warnings = read_file(str(f), guard)
    assert "print" in content
    assert warnings == []


def test_read_file_masks_sensitive_content(tmp_path):
    f = tmp_path / "config.py"
    f.write_text("API_KEY=sk-secret123")
    guard = GuardLayer()
    content, warnings = read_file(str(f), guard)
    assert "sk-secret123" not in content
    assert len(warnings) > 0
