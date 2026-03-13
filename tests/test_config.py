from insightforge.config import Config


def test_default_llm_model(tmp_path):
    config = Config(insightforge_dir=tmp_path / ".insightforge")
    assert config.llm_model == "qwen2.5:7b"


def test_default_embed_model(tmp_path):
    config = Config(insightforge_dir=tmp_path / ".insightforge")
    assert config.embed_model == "nomic-embed-text"


def test_insightforge_dir(tmp_path):
    config = Config(insightforge_dir=tmp_path / ".insightforge")
    assert config.insightforge_dir.name == ".insightforge"


def test_chroma_dir_inside_insightforge(tmp_path):
    config = Config(insightforge_dir=tmp_path / ".insightforge")
    assert config.chroma_dir.parent == config.insightforge_dir


def test_ollama_base_url_default(tmp_path, monkeypatch):
    monkeypatch.delenv("OLLAMA_HOST", raising=False)
    config = Config(insightforge_dir=tmp_path / ".insightforge")
    assert config.ollama_base_url == "http://localhost:11434"


def test_ollama_base_url_from_env(tmp_path, monkeypatch):
    monkeypatch.setenv("OLLAMA_HOST", "http://192.168.1.100:11434")
    config = Config(insightforge_dir=tmp_path / ".insightforge")
    assert config.ollama_base_url == "http://192.168.1.100:11434"
