import hashlib
from datetime import datetime
from pathlib import Path


class SessionHistory:
    def __init__(self, sessions_dir: Path, folder_path: str):
        self.folder_hash = hashlib.md5(folder_path.encode()).hexdigest()[:12]
        self.session_dir = Path(sessions_dir) / self.folder_hash
        self.session_dir.mkdir(parents=True, exist_ok=True)
        self.messages: list[dict] = []
        self.folder_path = folder_path
        self._timestamp = datetime.now().strftime("%Y-%m-%d_%Hh%M")

    def add(self, role: str, content: str) -> None:
        self.messages.append({"role": role, "content": content})

    def save(self) -> Path:
        filepath = self.session_dir / f"{self._timestamp}.md"
        filepath.write_text(self.export_markdown(), encoding="utf-8")
        # Cross-platform: dùng latest.txt thay symlink (Windows không hỗ trợ symlink không admin)
        latest = self.session_dir / "latest.txt"
        latest.write_text(filepath.name, encoding="utf-8")
        return filepath

    def list_sessions(self) -> list[Path]:
        return sorted(
            [f for f in self.session_dir.glob("*.md") if f.name != "latest.md"]
        )

    def load_all(self) -> None:
        self.messages = []
        for session_file in self.list_sessions():
            content = session_file.read_text(encoding="utf-8")
            for line in content.splitlines():
                if line.startswith("> "):
                    self.messages.append({"role": "user", "content": line[2:]})
                elif line.startswith("**AI:** "):
                    self.messages.append({"role": "assistant", "content": line[8:]})

    def search(self, query: str) -> str:
        query_lower = query.lower()
        relevant = []
        for i, msg in enumerate(self.messages):
            if query_lower in msg["content"].lower():
                # lấy cả câu trả lời tiếp theo nếu có
                relevant.append(msg["content"])
                if i + 1 < len(self.messages) and self.messages[i + 1]["role"] == "assistant":
                    relevant.append(self.messages[i + 1]["content"])
        if not relevant:
            return ""
        return "\n---\n".join(relevant[:4])  # trả về tối đa 4 đoạn

    def delete_session(self, name: str) -> bool:
        """Xóa một session theo tên file (vd: '2026-03-13_13h30.md'). Trả về True nếu thành công."""
        target = self.session_dir / name
        if target.exists() and target.suffix == ".md":
            target.unlink()
            latest = self.session_dir / "latest.txt"
            if latest.exists() and latest.read_text(encoding="utf-8").strip() == name:
                latest.unlink()
            return True
        return False

    def delete_all_sessions(self) -> int:
        """Xóa toàn bộ session đã lưu. Trả về số session đã xóa."""
        sessions = self.list_sessions()
        for f in sessions:
            f.unlink()
        latest = self.session_dir / "latest.txt"
        if latest.exists():
            latest.unlink()
        return len(sessions)

    def export_markdown(self) -> str:
        lines = [
            f"# InsightForge Session — {self._timestamp}",
            f"\n**Folder:** {self.folder_path}\n",
        ]
        for msg in self.messages:
            if msg["role"] == "user":
                lines.append(f"> {msg['content']}\n")
            else:
                lines.append(f"**AI:** {msg['content']}\n")
        return "\n".join(lines)
