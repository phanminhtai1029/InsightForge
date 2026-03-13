from insightforge.config import Config

def test_default_llm_model():
    config = Config()
    assert config.llm_model == "qwen2.5:7b"

def test_default_embed_model():
    config = Config()
    assert config.embed_model == "nomic-embed-text"

def test_insightforge_dir():
    config = Config()
    assert config.insightforge_dir.name == ".insightforge"

def test_chroma_dir_inside_insightforge():
    config = Config()
    assert config.chroma_dir.parent == config.insightforge_dir
