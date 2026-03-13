import base64
import json
from io import BytesIO
from unittest.mock import MagicMock, patch

from insightforge.tools.github import _parse_repo, scan_github_repo, read_github_file


# --- _parse_repo tests ---

def test_parse_repo_shorthand():
    assert _parse_repo("torvalds/linux") == "torvalds/linux"


def test_parse_repo_https_url():
    assert _parse_repo("https://github.com/torvalds/linux") == "torvalds/linux"


def test_parse_repo_https_url_with_trailing_slash():
    assert _parse_repo("https://github.com/torvalds/linux/") == "torvalds/linux"


def test_parse_repo_ssh_url():
    assert _parse_repo("git@github.com:torvalds/linux.git") == "torvalds/linux"


# --- Helpers ---

def _mock_response(data: dict | list) -> MagicMock:
    body = json.dumps(data).encode()
    m = MagicMock()
    m.__enter__ = MagicMock(return_value=m)
    m.__exit__ = MagicMock(return_value=False)
    m.read = MagicMock(return_value=body)
    return m


# --- scan_github_repo tests ---

def test_scan_github_repo_returns_structure():
    tree_data = {
        "tree": [
            {"type": "blob", "path": "README.md"},
            {"type": "blob", "path": "src/main.py"},
            {"type": "blob", "path": "src/utils.py"},
            {"type": "tree", "path": "src"},
        ],
        "truncated": False,
    }
    with patch("insightforge.tools.github.urlopen", return_value=_mock_response(tree_data)):
        result = scan_github_repo("owner/repo")

    assert "owner/repo" in result
    assert "main.py" in result
    assert "README.md" in result


def test_scan_github_repo_http_error():
    with patch("insightforge.tools.github.urlopen", side_effect=Exception("connection refused")):
        result = scan_github_repo("owner/broken")

    assert "Lỗi" in result


def test_scan_github_repo_missing_tree():
    bad_data = {"message": "Not Found"}
    with patch("insightforge.tools.github.urlopen", return_value=_mock_response(bad_data)):
        result = scan_github_repo("owner/repo")

    assert "Không lấy được" in result


# --- read_github_file tests ---

def test_read_github_file_base64():
    content = base64.b64encode(b"print('hello')").decode() + "\n"
    file_data = {"encoding": "base64", "content": content, "type": "file"}
    with patch("insightforge.tools.github.urlopen", return_value=_mock_response(file_data)):
        result = read_github_file("owner/repo", "main.py")

    assert "print('hello')" in result


def test_read_github_file_directory():
    dir_data = [
        {"name": "src", "type": "dir"},
        {"name": "main.py", "type": "file"},
    ]
    with patch("insightforge.tools.github.urlopen", return_value=_mock_response(dir_data)):
        result = read_github_file("owner/repo", "src")

    assert "directory" in result


def test_read_github_file_error():
    with patch("insightforge.tools.github.urlopen", side_effect=Exception("404")):
        result = read_github_file("owner/repo", "missing.py")

    assert "Lỗi" in result
