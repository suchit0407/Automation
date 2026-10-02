import json

from taskrun.__main__ import main
from taskrun.runner import load_tasks, run_all, run_task


def test_success():
    assert run_task({"cmd": "echo hi"}).ok


def test_retries_then_succeeds(tmp_path):
    marker = tmp_path / "m"
    cmd = f"if [ -f {marker} ]; then exit 0; else touch {marker}; exit 1; fi"
    r = run_task({"cmd": cmd, "retries": 2})
    assert r.ok and r.attempts == 2


def test_timeout():
    r = run_task({"cmd": "sleep 3", "timeout": 0.2})
    assert not r.ok and "timed out" in r.output


def test_stops_on_failure_unless_allowed():
    tasks = [{"cmd": "false"}, {"cmd": "echo x"}]
    assert len(run_all(tasks)) == 1
    assert len(run_all(tasks, keep_going=True)) == 2
    assert len(run_all([{"cmd": "false", "allow_failure": True}, {"cmd": "echo x"}])) == 2


def test_validation(tmp_path):
    p = tmp_path / "t.json"
    p.write_text(json.dumps([{"name": "no cmd"}]))
    try:
        load_tasks(p)
    except ValueError:
        return
    raise AssertionError("expected ValueError")


def test_cli_exit_code(tmp_path):
    p = tmp_path / "t.json"
    p.write_text(json.dumps([{"cmd": "false"}]))
    assert main([str(p)]) == 1


def test_allowed_failure_exit_zero(tmp_path):
    p = tmp_path / "t.json"
    p.write_text(json.dumps([{"cmd": "false", "allow_failure": True}]))
    assert main([str(p)]) == 0
