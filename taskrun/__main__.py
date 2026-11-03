import argparse
import sys

from .runner import load_tasks, run_all, run_parallel


def main(argv=None):
    ap = argparse.ArgumentParser(prog="taskrun", description="Run a JSON list of shell tasks.")
    ap.add_argument("file", help="path to tasks JSON")
    ap.add_argument("-k", "--keep-going", action="store_true", help="continue after failures")
    ap.add_argument("-v", "--verbose", action="store_true", help="show output of passing tasks")
    ap.add_argument("-j", "--jobs", type=int, default=1, help="run N tasks at once (runs all tasks)")
    args = ap.parse_args(argv)

    tasks = load_tasks(args.file)
    if args.jobs > 1:
        results = run_parallel(tasks, args.jobs)
    else:
        results = run_all(tasks, keep_going=args.keep_going)
    for r in results:
        mark = "ok  " if r.ok else ("warn" if r.allowed else "FAIL")
        extra = f" (attempts: {r.attempts})" if r.attempts > 1 else ""
        print(f"[{mark}] {r.name}  {r.seconds:.2f}s{extra}")
        if r.output and (args.verbose or not r.ok):
            print("       " + r.output.replace("\n", "\n       "))
    failed = sum(not r.ok and not r.allowed for r in results)
    print(f"\n{len(results) - failed}/{len(results)} passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
