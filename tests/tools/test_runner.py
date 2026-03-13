from insightforge.tools.runner import run_script


def test_run_simple_command():
    result = run_script("echo hello")
    assert "hello" in result


def test_run_python_script():
    result = run_script("python3 -c \"print('test output')\"")
    assert "test output" in result


def test_run_failed_command_returns_error():
    result = run_script("this_command_does_not_exist_xyz")
    assert "error" in result.lower() or "not found" in result.lower()


def test_run_with_timeout():
    result = run_script("sleep 10", timeout=1)
    assert "timeout" in result.lower()
