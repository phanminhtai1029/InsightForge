import base64
import json
import os
import re
from collections import Counter
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

GITHUB_API = "https://api.github.com"

_CODE_EXTS = {
    ".py", ".ts", ".js", ".tsx", ".jsx", ".go", ".rs", ".java",
    ".rb", ".php", ".cs", ".cpp", ".c", ".h", ".sh", ".yaml", ".yml",
    ".toml", ".json", ".md", ".sql", ".html", ".css",
}


def _parse_repo(repo_input: str) -> str:
    """Chuẩn hóa input thành 'owner/repo' từ URL hoặc shorthand."""
    s = repo_input.strip().rstrip("/")
    # https://github.com/owner/repo[.git][/...]
    m = re.match(r"https?://github\.com/([^/]+/[^/.]+)", s)
    if m:
        return m.group(1)
    # git@github.com:owner/repo.git
    m = re.match(r"git@github\.com:([^/]+/[^.]+)", s)
    if m:
        return m.group(1)
    return s


def _token() -> str | None:
    return os.environ.get("GITHUB_TOKEN")


def _api_get(path: str, token: str | None = None) -> dict | list:
    url = f"{GITHUB_API}/{path.lstrip('/')}"
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "InsightForge/1.0",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = Request(url, headers=headers)
    try:
        with urlopen(req, timeout=15) as resp:
            return json.loads(resp.read())
    except HTTPError as e:
        body = e.read().decode(errors="replace")
        msg = json.loads(body).get("message", body) if body.startswith("{") else body
        raise RuntimeError(f"HTTP {e.code}: {msg}") from e


def scan_github_repo(repo: str, branch: str = "HEAD") -> str:
    """Liệt kê cấu trúc file của một GitHub repo công khai hoặc private (cần GITHUB_TOKEN).

    repo: 'owner/repo' hoặc URL GitHub đầy đủ.
    branch: nhánh cần đọc (mặc định HEAD).
    """
    owner_repo = _parse_repo(repo)
    token = _token()
    try:
        data = _api_get(f"repos/{owner_repo}/git/trees/{branch}?recursive=1", token)
    except Exception as e:
        return f"Lỗi khi đọc repo {owner_repo}: {e}"

    if "tree" not in data:
        return f"Không lấy được file tree từ {owner_repo} (nhánh: {branch})"

    files = [item for item in data["tree"] if item["type"] == "blob"]
    truncated = data.get("truncated", False)

    exts: Counter[str] = Counter(
        Path(f["path"]).suffix.lower() or "(none)" for f in files
    )
    top_dirs = sorted({f["path"].split("/")[0] for f in files if "/" in f["path"]})

    sep = "━" * 48
    lines = [sep, f"  GITHUB — {owner_repo} [{branch}]", sep]
    lines.append(f"  Files : {len(files)}{' (truncated)' if truncated else ''}")
    if top_dirs:
        lines.append(f"  Dirs  : {', '.join(top_dirs[:20])}")
    lines.append(f"  Types : {', '.join(f'{e}({c})' for e, c in exts.most_common(8))}")
    lines.append(sep)

    code_files = [f["path"] for f in files if Path(f["path"]).suffix in _CODE_EXTS]
    for p in code_files[:80]:
        lines.append(f"  {p}")
    if len(code_files) > 80:
        lines.append(f"  ... và {len(code_files) - 80} file khác")

    return "\n".join(lines)


def read_github_file(repo: str, file_path: str, branch: str = "HEAD") -> str:
    """Đọc nội dung một file từ GitHub repo.

    repo: 'owner/repo' hoặc URL GitHub.
    file_path: đường dẫn file trong repo (vd: 'src/main.py').
    branch: nhánh cần đọc (mặc định HEAD).
    """
    owner_repo = _parse_repo(repo)
    token = _token()
    try:
        data = _api_get(
            f"repos/{owner_repo}/contents/{file_path.lstrip('/')}?ref={branch}", token
        )
    except Exception as e:
        return f"Lỗi khi đọc {file_path} từ {owner_repo}: {e}"

    if isinstance(data, list):
        entries = "\n".join(f"  {item['name']}" for item in data[:30])
        return f"{file_path} là directory:\n{entries}"

    if data.get("encoding") == "base64":
        try:
            return base64.b64decode(data["content"]).decode("utf-8", errors="replace")
        except Exception as e:
            return f"Không thể decode {file_path}: {e}"

    return data.get("content") or f"File {file_path} trống."
