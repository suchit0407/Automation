# Automation

`taskrun` is a tiny, dependency-free task runner. Describe steps in JSON; it runs them
with retries, timeouts, and a pass/fail summary.

```bash
python -m taskrun tasks.example.json      # stop at first failure
python -m taskrun tasks.example.json -k   # keep going
python -m taskrun tasks.example.json -j 4 # run 4 tasks at once (runs all tasks)
```

Task fields: `cmd` (required), `name`, `retries`, `timeout` (seconds), `allow_failure`.

Run tests: `pip install pytest && pytest -q`
