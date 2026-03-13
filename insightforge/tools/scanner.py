from pathlib import Path
from insightforge.guard import GuardLayer, SensitiveMatch

CODE_EXTENSIONS = {".py", ".js", ".ts", ".go", ".rs", ".java", ".cpp", ".c", ".rb", ".php"}
DATA_EXTENSIONS = {".csv", ".json", ".parquet", ".xlsx", ".xls", ".yaml", ".yml", ".xml"}
CONFIG_EXTENSIONS = {".toml", ".ini", ".cfg", ".conf", ".env"}

IGNORED_DIRS = {".git", ".venv", "venv", "node_modules", "__pycache__", ".idea", ".vscode"}


def scan_folder(folder_path: str) -> str:
    root = Path(folder_path)
    if not root.exists():
        return f"Folder không tồn tại: {folder_path}"

    code_files, data_files, config_files, sensitive_files, other_files = [], [], [], [], []

    for path in sorted(root.rglob("*")):
        if any(part in IGNORED_DIRS for part in path.parts):
            continue
        if not path.is_file():
            continue
        rel = str(path.relative_to(root))
        guard = GuardLayer()
        if guard.is_sensitive_filename(path.name):
            sensitive_files.append(rel)
        elif path.suffix in CODE_EXTENSIONS:
            code_files.append(rel)
        elif path.suffix in DATA_EXTENSIONS:
            data_files.append(rel)
        elif path.suffix in CONFIG_EXTENSIONS:
            config_files.append(rel)
        else:
            other_files.append(rel)

    lines = [f"Folder: {folder_path}"]
    if code_files:
        lines.append(f"\nCode files ({len(code_files)}):")
        lines.extend(f"  {f}" for f in code_files)
    if data_files:
        lines.append(f"\nData files ({len(data_files)}):")
        lines.extend(f"  {f}" for f in data_files)
    if config_files:
        lines.append(f"\nConfig files ({len(config_files)}):")
        lines.extend(f"  {f}" for f in config_files)
    if sensitive_files:
        lines.append(f"\n[SENSITIVE] Files ({len(sensitive_files)}):")
        lines.extend(f"  {f}" for f in sensitive_files)
    if other_files:
        lines.append(f"\nOther ({len(other_files)}):")
        lines.extend(f"  {f}" for f in other_files)

    return "\n".join(lines)


def read_file(file_path: str, guard: GuardLayer) -> tuple[str, list[SensitiveMatch]]:
    content = Path(file_path).read_text(encoding="utf-8", errors="replace")
    masked, matches = guard.mask_content(content)
    return masked, matches
