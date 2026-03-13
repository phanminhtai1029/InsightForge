import os
from pathlib import Path
from dataclasses import dataclass, field


@dataclass
class Config:
    llm_model: str = "qwen2.5:7b"
    embed_model: str = "nomic-embed-text"
    llm_keep_alive: str = "5m"     # unload after 5 minutes idle
    embed_keep_alive: str = "0"    # unload immediately after use
    ollama_base_url: str = field(
        default_factory=lambda: os.environ.get("OLLAMA_HOST", "http://localhost:11434")
    )
    insightforge_dir: Path = field(default_factory=lambda: Path.home() / ".insightforge")
    chroma_dir: Path = field(init=False)
    sessions_dir: Path = field(init=False)

    def __post_init__(self):
        self.chroma_dir = self.insightforge_dir / "chroma"
        self.sessions_dir = self.insightforge_dir / "sessions"
        self.insightforge_dir.mkdir(exist_ok=True)
        self.chroma_dir.mkdir(exist_ok=True)
        self.sessions_dir.mkdir(exist_ok=True)
