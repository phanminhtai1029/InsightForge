import urllib.request
from dataclasses import dataclass, field

OLLAMA_BASE_URL = "http://localhost:11434"

OFFLINE_COMMANDS = ["/scan", "/stack", "/history", "/save", "/clear", "/exit"]
ONLINE_COMMANDS = OFFLINE_COMMANDS + ["chat", "/index"]


@dataclass
class OllamaChecker:
    base_url: str = OLLAMA_BASE_URL
    available: bool = field(init=False)

    def __init__(self, base_url: str = OLLAMA_BASE_URL, available: bool | None = None):
        self.base_url = base_url
        if available is not None:
            self.available = available
        else:
            self.available = self._ping()

    def _ping(self) -> bool:
        try:
            with urllib.request.urlopen(self.base_url, timeout=2):
                return True
        except Exception:
            return False

    def is_available(self) -> bool:
        return self.available

    def has_model(self, model_name: str) -> bool:
        if not self.available:
            return False
        try:
            url = f"{self.base_url}/api/tags"
            with urllib.request.urlopen(url, timeout=3) as resp:
                import json
                data = json.loads(resp.read())
                models = [m["name"] for m in data.get("models", [])]
                # match exact or prefix (qwen2.5:7b matches qwen2.5:7b)
                return any(m == model_name or m.startswith(model_name) for m in models)
        except Exception:
            return False

    def available_commands(self) -> list[str]:
        return ONLINE_COMMANDS if self.available else OFFLINE_COMMANDS

    def offline_banner(self) -> str:
        return (
            "\n[yellow]⚠ Ollama không tìm thấy tại localhost:11434[/yellow]\n"
            "[dim]Chạy offline mode — chat AI bị tắt.\n"
            f"Lệnh khả dụng: {', '.join(OFFLINE_COMMANDS)}\n"
            "Để bật chat: [bold]ollama serve[/bold][/dim]\n"
        )
