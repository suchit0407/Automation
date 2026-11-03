import json
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass


@dataclass
class Result:
    name: str
    ok: bool
    attempts: int
    seconds: float
    output: str
    allowed: bool = False


def load_tasks(path):
    with open(path) as f:
        tasks = json.load(f)
    if not isinstance(tasks, list):
        raise ValueError("task file must contain a JSON list")
    for i, t in enumerate(tasks):
        if "cmd" not in t:
            raise ValueError(f"task {i} is missing 'cmd'")
    return tasks


def run_task(task):
    name = task.get("name", task["cmd"])
    retries = task.get("retries", 0)
    timeout = task.get("timeout")
    start = time.monotonic()
    output = ""
    ok = False
    attempts = 0
    for attempts in range(1, retries + 2):
        try:
            p = subprocess.run(
                task["cmd"], shell=True, capture_output=True, text=True, timeout=timeout
            )
            output = p.stdout + p.stderr
            ok = p.returncode == 0
        except subprocess.TimeoutExpired:
            output = f"timed out after {timeout}s"
            ok = False
        if ok:
            break
    return Result(
        name, ok, attempts, time.monotonic() - start, output.strip(),
        allowed=bool(task.get("allow_failure")),
    )


def run_all(tasks, keep_going=False):
    results = []
    for task in tasks:
        r = run_task(task)
        results.append(r)
        if not r.ok and not (keep_going or r.allowed):
            break
    return results


def run_parallel(tasks, workers):
    with ThreadPoolExecutor(max_workers=workers) as pool:
        return list(pool.map(run_task, tasks))
