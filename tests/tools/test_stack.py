import json
from pathlib import Path
from insightforge.tools.stack import analyze_stack


def test_detect_nextjs(tmp_path):
    pkg = {"dependencies": {"next": "14.0.0", "react": "18.0.0"}}
    (tmp_path / "package.json").write_text(json.dumps(pkg))
    result = analyze_stack(str(tmp_path))
    assert "Next.js" in result


def test_detect_fastapi(tmp_path):
    (tmp_path / "requirements.txt").write_text("fastapi==0.104.0\nuvicorn")
    result = analyze_stack(str(tmp_path))
    assert "FastAPI" in result


def test_detect_github_actions(tmp_path):
    wf_dir = tmp_path / ".github" / "workflows"
    wf_dir.mkdir(parents=True)
    (wf_dir / "ci.yml").write_text("on: push")
    result = analyze_stack(str(tmp_path))
    assert "GitHub Actions" in result


def test_detect_docker(tmp_path):
    (tmp_path / "Dockerfile").write_text("FROM python:3.11")
    result = analyze_stack(str(tmp_path))
    assert "Docker" in result


def test_empty_folder_returns_unknown(tmp_path):
    result = analyze_stack(str(tmp_path))
    assert "unknown" in result.lower() or "không" in result.lower() or "no stack" in result.lower()
