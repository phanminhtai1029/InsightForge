import sys
from datetime import datetime
from pathlib import Path

import click
from rich.console import Console
from rich.markdown import Markdown
from rich.prompt import Confirm, Prompt

from insightforge.config import Config
from insightforge.guard import GuardLayer
from insightforge.ollama_checker import OllamaChecker
from insightforge.tools.history import SessionHistory
from insightforge.tools.scanner import scan_folder, IGNORED_DIRS
from insightforge.tools.stack import analyze_stack

console = Console()


def check_venv() -> bool:
    """Kiểm tra có đang chạy trong venv không. Trả về True nếu ok để tiếp tục."""
    in_venv = sys.prefix != sys.base_prefix
    if in_venv:
        return True
    console.print("\n[yellow]⚠ Bạn chưa kích hoạt virtual environment.[/yellow]")
    console.print("[dim]Khuyến nghị dùng venv để tránh conflict dependencies.\n")
    console.print("  Linux/Mac: [bold]source .venv/bin/activate[/bold]")
    console.print("  Windows:   [bold].venv\\\\Scripts\\\\activate[/bold][/dim]\n")
    return Confirm.ask("Tiếp tục mà không có venv?", default=False)


def check_sensitive_files(folder_path: str, guard: GuardLayer) -> bool:
    root = Path(folder_path)
    sensitive = [
        str(p.relative_to(root))
        for p in root.rglob("*")
        if p.is_file()
        and not any(part in IGNORED_DIRS for part in p.parts)
        and guard.is_sensitive_filename(p.name)
    ]
    if not sensitive:
        return True
    console.print(f"\n[yellow]⚠ Phát hiện {len(sensitive)} file nhạy cảm:[/yellow]")
    for f in sensitive[:10]:
        console.print(f"  [dim]{f}[/dim]")
    console.print("[dim]Các giá trị sẽ được mask trước khi gửi lên AI.[/dim]")
    return Confirm.ask("Tiếp tục?", default=True)


def load_history_prompt(history: SessionHistory) -> bool:
    sessions = history.list_sessions()
    if not sessions:
        return False
    console.print(f"\n[cyan]Tìm thấy {len(sessions)} session trước.[/cyan]")
    return Confirm.ask("Load conversation history?", default=True)


@click.command()
@click.argument("folder", default=".", type=click.Path(exists=True))
@click.option("--model", default=None, help="Override LLM model (vd: llama3.2)")
@click.option("--fresh", is_flag=True, help="Bắt đầu session mới, không load history")
def cli(folder: str, model: str | None, fresh: bool):
    """InsightForge — AI phân tích dataset và codebase của bạn."""
    folder_path = str(Path(folder).resolve())
    config = Config()
    if model:
        config.llm_model = model

    # 1. Venv check
    if not check_venv():
        console.print("[red]Đã hủy. Hãy kích hoạt venv trước.[/red]")
        sys.exit(0)

    # 2. Kiểm tra Ollama
    checker = OllamaChecker(base_url=config.ollama_base_url)
    if checker.is_available():
        console.print(f"\n[bold green]InsightForge[/bold green] — {folder_path}")
        console.print("[dim]Commands: /scan, /stack, /index, /history, /history delete <n|all>, /save, /clear, /exit[/dim]")
        console.print("[dim]Chat: hỏi AI để scan GitHub repo, đọc file từ URL, phân tích code...[/dim]\n")
    else:
        console.print(f"\n[bold green]InsightForge[/bold green] — {folder_path}")
        console.print(checker.offline_banner())

    guard = GuardLayer()

    # 3. Kiểm tra file nhạy cảm
    if not check_sensitive_files(folder_path, guard):
        console.print("[red]Đã hủy.[/red]")
        sys.exit(0)

    # 4. Session history
    history = SessionHistory(
        sessions_dir=config.sessions_dir,
        folder_path=folder_path,
    )
    if not fresh and load_history_prompt(history):
        history.load_all()
        console.print(f"[dim]Loaded {len(history.messages)} messages từ history.[/dim]\n")

    # Build agent (chỉ khi online)
    agent = None
    if checker.is_available():
        with console.status("[dim]Khởi tạo agent...[/dim]"):
            from insightforge.agent import build_agent
            agent = build_agent(folder_path, config, history=history)
        console.print("[green]Sẵn sàng. Gõ câu hỏi của bạn.[/green]\n")
    else:
        console.print("[yellow]Offline mode. Chat AI không khả dụng.[/yellow]\n")

    while True:
        try:
            user_input = Prompt.ask("[bold cyan]>[/bold cyan]").strip()
        except (KeyboardInterrupt, EOFError):
            break

        if not user_input:
            continue

        # Built-in commands (hoạt động cả online lẫn offline)
        if user_input == "/exit":
            break

        if user_input == "/clear":
            history.messages.clear()
            console.print("[dim]Đã xóa conversation history.[/dim]")
            continue

        if user_input == "/scan":
            console.print(scan_folder(folder_path))
            continue

        if user_input == "/stack":
            console.print(analyze_stack(folder_path))
            continue

        if user_input.startswith("/history"):
            parts = user_input.split(maxsplit=2)
            sessions = history.list_sessions()

            # /history delete all
            if len(parts) == 3 and parts[1] == "delete" and parts[2] == "all":
                if not sessions:
                    console.print("[dim]Chưa có session nào để xóa.[/dim]")
                elif Confirm.ask(f"Xóa tất cả {len(sessions)} session?", default=False):
                    n = history.delete_all_sessions()
                    console.print(f"[green]Đã xóa {n} session.[/green]")
                continue

            # /history delete <n>
            if len(parts) == 3 and parts[1] == "delete":
                try:
                    idx = int(parts[2]) - 1
                    if 0 <= idx < len(sessions):
                        name = sessions[idx].name
                        history.delete_session(name)
                        console.print(f"[green]Đã xóa:[/green] {name}")
                    else:
                        console.print(f"[yellow]Số thứ tự không hợp lệ. Có {len(sessions)} session.[/yellow]")
                except ValueError:
                    console.print("[yellow]Dùng: /history delete <số> hoặc /history delete all[/yellow]")
                continue

            # /history (list)
            if not sessions:
                console.print("[dim]Chưa có session nào.[/dim]")
            else:
                for i, s in enumerate(sessions, 1):
                    console.print(f"  [cyan]{i}.[/cyan] [dim]{s.name}[/dim]")
                console.print(f"\n[dim]Dùng /history delete <số> hoặc /history delete all để xóa.[/dim]")
            continue

        if user_input.startswith("/save"):
            parts = user_input.split(maxsplit=1)
            filename = parts[1] if len(parts) > 1 else None
            if filename and not filename.endswith(".md"):
                filename += ".md"
            save_path = Path(filename) if filename else Path(
                f"insightforge_{datetime.now().strftime('%Y-%m-%d_%Hh%M')}.md"
            )
            save_path.write_text(history.export_markdown(), encoding="utf-8")
            console.print(f"[green]Đã lưu:[/green] {save_path}")
            continue

        if user_input == "/index":
            if not checker.is_available():
                console.print("[yellow]Không thể index: Ollama không có sẵn.[/yellow]")
                continue
            with console.status("[dim]Đang index codebase...[/dim]"):
                from insightforge.tools.indexer import index_codebase
                result = index_codebase(folder_path, config)
            console.print(f"[dim]{result}[/dim]")
            continue

        # Chat với AI (chỉ online)
        if agent is None:
            console.print(
                "[yellow]Chat không khả dụng — Ollama chưa chạy.[/yellow]\n"
                "[dim]Chạy [bold]ollama serve[/bold] rồi khởi động lại InsightForge.[/dim]"
            )
            continue

        history.add("user", user_input)
        try:
            with console.status("[dim]Đang suy nghĩ...[/dim]"):
                response = agent.chat(user_input)
            answer = str(response)
            console.print(Markdown(answer))
            history.add("assistant", answer)
        except Exception as e:
            console.print(f"[red]Lỗi:[/red] {e}")

    # Auto-save khi exit
    if history.messages:
        saved = history.save()
        console.print(f"\n[dim]Session đã lưu: {saved}[/dim]")
    console.print("[dim]Tạm biệt![/dim]")


def main():
    cli()


if __name__ == "__main__":
    main()
