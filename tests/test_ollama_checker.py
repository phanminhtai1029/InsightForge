from unittest.mock import patch, MagicMock
from insightforge.ollama_checker import OllamaChecker

def test_checker_returns_false_when_connection_refused():
    with patch("urllib.request.urlopen", side_effect=Exception("connection refused")):
        checker = OllamaChecker()
        assert checker.is_available() is False

def test_checker_returns_true_when_reachable():
    mock_response = MagicMock()
    mock_response.__enter__ = lambda s: s
    mock_response.__exit__ = MagicMock(return_value=False)
    with patch("urllib.request.urlopen", return_value=mock_response):
        checker = OllamaChecker()
        assert checker.is_available() is True

def test_checker_has_model_returns_false_when_offline():
    with patch("urllib.request.urlopen", side_effect=Exception("offline")):
        checker = OllamaChecker()
        assert checker.has_model("qwen2.5:7b") is False

def test_offline_commands_list():
    checker = OllamaChecker(available=False)
    cmds = checker.available_commands()
    assert "/scan" in cmds
    assert "/stack" in cmds
    assert "/save" in cmds
    assert "/history" in cmds
    assert "chat" not in cmds
    assert "/index" not in cmds   # index cần Ollama embed

def test_online_commands_includes_chat():
    checker = OllamaChecker(available=True)
    cmds = checker.available_commands()
    assert "chat" in cmds


import json as _json

def test_has_model_returns_true_when_model_present():
    tags_response = _json.dumps({"models": [{"name": "qwen2.5:7b"}]}).encode()
    mock_resp = MagicMock()
    mock_resp.__enter__ = lambda s: s
    mock_resp.__exit__ = MagicMock(return_value=False)
    mock_resp.read.return_value = tags_response
    with patch("urllib.request.urlopen", return_value=mock_resp):
        checker = OllamaChecker(available=True)
        assert checker.has_model("qwen2.5:7b") is True

def test_has_model_returns_false_when_model_not_in_list():
    tags_response = _json.dumps({"models": [{"name": "llama3.2:latest"}]}).encode()
    mock_resp = MagicMock()
    mock_resp.__enter__ = lambda s: s
    mock_resp.__exit__ = MagicMock(return_value=False)
    mock_resp.read.return_value = tags_response
    with patch("urllib.request.urlopen", return_value=mock_resp):
        checker = OllamaChecker(available=True)
        assert checker.has_model("qwen2.5:7b") is False

def test_has_model_returns_false_when_api_raises():
    with patch("urllib.request.urlopen", side_effect=Exception("connection reset")):
        checker = OllamaChecker(available=True)
        assert checker.has_model("qwen2.5:7b") is False
