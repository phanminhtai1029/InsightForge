from insightforge.guard import GuardLayer, SensitiveMatch


def test_detect_env_file():
    guard = GuardLayer()
    assert guard.is_sensitive_filename(".env") is True


def test_detect_key_file():
    guard = GuardLayer()
    assert guard.is_sensitive_filename("private.key") is True


def test_normal_file_not_sensitive():
    guard = GuardLayer()
    assert guard.is_sensitive_filename("main.py") is False


def test_mask_api_key_in_content():
    guard = GuardLayer()
    content = "API_KEY=sk-abc123xyz\nNAME=myapp"
    masked, matches = guard.mask_content(content)
    assert "sk-abc123xyz" not in masked
    assert "API_KEY=****" in masked
    assert len(matches) == 1


def test_mask_github_token():
    guard = GuardLayer()
    content = "TOKEN=ghp_abcdefghijklmnop"
    masked, matches = guard.mask_content(content)
    assert "ghp_abcdefghijklmnop" not in masked
    assert len(matches) == 1


def test_no_sensitive_content():
    guard = GuardLayer()
    content = "def hello():\n    return 'world'"
    masked, matches = guard.mask_content(content)
    assert masked == content
    assert len(matches) == 0
