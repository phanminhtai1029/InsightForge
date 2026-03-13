import subprocess
import sys


def run_script(command: str, timeout: int = 30) -> str:
    # Thay python3/python → sys.executable để chạy đúng trên Windows và Linux
    # Dùng if/elif để tránh double-replace khi sys.executable chứa "python"
    if "python3 " in command:
        normalized = command.replace("python3 ", f"{sys.executable} ", 1)
    elif "python " in command:
        normalized = command.replace("python ", f"{sys.executable} ", 1)
    else:
        normalized = command
    try:
        result = subprocess.run(
            normalized,
            shell=True,       # shell=True hoạt động trên cả Windows và Linux
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        output = result.stdout
        if result.returncode != 0:
            output += f"\n[Error (exit {result.returncode})]: {result.stderr}"
        return output.strip() or "(no output)"
    except subprocess.TimeoutExpired:
        return f"[Timeout]: Command exceeded {timeout}s limit"
    except Exception as e:
        return f"[Error]: {e}"
