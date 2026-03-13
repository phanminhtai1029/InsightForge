from pathlib import Path
from insightforge.tools.history import SessionHistory


def test_save_and_load_session(tmp_path):
    history = SessionHistory(sessions_dir=tmp_path, folder_path="/test/folder")
    history.add("user", "hello")
    history.add("assistant", "world")
    history.save()  # phải save trước khi list
    sessions = history.list_sessions()
    assert len(sessions) >= 1


def test_search_history_finds_match(tmp_path):
    history = SessionHistory(sessions_dir=tmp_path, folder_path="/test/folder")
    history.add("user", "tech stack của project")
    history.add("assistant", "Next.js và FastAPI")
    history.save()

    history2 = SessionHistory(sessions_dir=tmp_path, folder_path="/test/folder")
    history2.load_all()
    result = history2.search("tech stack")
    assert "Next.js" in result


def test_search_history_no_match(tmp_path):
    history = SessionHistory(sessions_dir=tmp_path, folder_path="/test/folder")
    history.add("user", "hello world")
    history.save()

    history2 = SessionHistory(sessions_dir=tmp_path, folder_path="/test/folder")
    history2.load_all()
    result = history2.search("database schema")
    assert result == "" or "không" in result.lower()


def test_export_markdown(tmp_path):
    history = SessionHistory(sessions_dir=tmp_path, folder_path="/test/folder")
    history.add("user", "câu hỏi")
    history.add("assistant", "câu trả lời")
    md = history.export_markdown()
    assert "câu hỏi" in md
    assert "câu trả lời" in md
