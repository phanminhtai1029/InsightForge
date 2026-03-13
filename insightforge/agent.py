import asyncio

from llama_index.core.agent import AgentWorkflow
from llama_index.core.tools import FunctionTool
from llama_index.llms.ollama import Ollama

from insightforge.config import Config
from insightforge.guard import GuardLayer
from insightforge.tools.history import SessionHistory
from insightforge.tools.indexer import index_codebase
from insightforge.tools.retriever import query_index
from insightforge.tools.runner import run_script
from insightforge.tools.scanner import scan_folder
from insightforge.tools.scanner import read_file as _read_file
from insightforge.tools.stack import analyze_stack
from insightforge.tools.github import scan_github_repo, read_github_file


class SyncAgent:
    """Wrapper đồng bộ xung quanh AgentWorkflow async của LlamaIndex 0.14+."""

    def __init__(self, workflow: AgentWorkflow) -> None:
        self._workflow = workflow

    def chat(self, message: str) -> str:
        async def _run() -> str:
            handler = self._workflow.run(user_msg=message)
            result = await handler
            return str(result)

        return asyncio.run(_run())


def build_agent(
    folder_path: str,
    config: Config | None = None,
    history: SessionHistory | None = None,
) -> SyncAgent:
    if config is None:
        config = Config()

    guard = GuardLayer()

    # --- Tool definitions ---

    def tool_scan_folder(path: str = folder_path) -> str:
        """Liệt kê và phân loại tất cả các file trong folder. Dùng khi cần tổng quan về nội dung folder."""
        return scan_folder(path)

    def tool_read_file(file_path: str) -> str:
        """Đọc nội dung một file cụ thể. Giá trị nhạy cảm sẽ được tự động mask."""
        content, warnings = _read_file(file_path, guard)
        if warnings:
            warn_str = f"[Guard: {len(warnings)} sensitive pattern(s) masked]\n"
            return warn_str + content
        return content

    def tool_analyze_stack(path: str = folder_path) -> str:
        """Phân tích tech stack của codebase: frontend, backend, database, CI/CD, cloud, container."""
        return analyze_stack(path)

    def tool_index_codebase(path: str = folder_path) -> str:
        """Index toàn bộ codebase vào ChromaDB để phục vụ RAG. Chạy lần đầu hoặc khi codebase thay đổi."""
        return index_codebase(path, config)

    def tool_query_index(query: str, path: str = folder_path) -> str:
        """Tìm kiếm context liên quan từ index đã build. Dùng khi cần tìm code/logic cụ thể trong codebase lớn."""
        return query_index(path, query, config)

    def tool_run_script(command: str) -> str:
        """Chạy lệnh shell hoặc Python script. Trả về stdout và stderr."""
        return run_script(command)

    def tool_search_history(query: str) -> str:
        """Tìm kiếm trong conversation history các session trước. Dùng trước khi phân tích để xem có câu trả lời sẵn không."""
        if history is None:
            return "Không có session history."
        result = history.search(query)
        return result if result else "Không tìm thấy trong history."

    def tool_scan_github_repo(repo: str, branch: str = "HEAD") -> str:
        """Liệt kê cấu trúc file của một GitHub repo (công khai hoặc private với GITHUB_TOKEN).
        repo: 'owner/repo' hoặc URL GitHub đầy đủ. branch: nhánh muốn xem (mặc định HEAD).
        """
        return scan_github_repo(repo, branch)

    def tool_read_github_file(repo: str, file_path: str, branch: str = "HEAD") -> str:
        """Đọc nội dung một file từ GitHub repo.
        repo: 'owner/repo' hoặc URL GitHub. file_path: đường dẫn file trong repo (vd: 'src/main.py').
        """
        return read_github_file(repo, file_path, branch)

    tools = [
        FunctionTool.from_defaults(fn=tool_scan_folder, name="scan_folder"),
        FunctionTool.from_defaults(fn=tool_read_file, name="read_file"),
        FunctionTool.from_defaults(fn=tool_analyze_stack, name="analyze_stack"),
        FunctionTool.from_defaults(fn=tool_index_codebase, name="index_codebase"),
        FunctionTool.from_defaults(fn=tool_query_index, name="query_index"),
        FunctionTool.from_defaults(fn=tool_run_script, name="run_script"),
        FunctionTool.from_defaults(fn=tool_search_history, name="search_history"),
        FunctionTool.from_defaults(fn=tool_scan_github_repo, name="scan_github_repo"),
        FunctionTool.from_defaults(fn=tool_read_github_file, name="read_github_file"),
    ]

    llm = Ollama(
        model=config.llm_model,
        base_url=config.ollama_base_url,
        request_timeout=120.0,
        additional_kwargs={"keep_alive": config.llm_keep_alive},
    )

    workflow = AgentWorkflow.from_tools_or_functions(
        tools_or_functions=tools,
        llm=llm,
        verbose=False,
    )

    return SyncAgent(workflow)
