import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
EXERCISES = ["duration_parser", "config_merge"]
ATTEMPTS = ["claude_attempt", "codex_attempt"]


def main() -> int:
    failures = []
    for exercise in EXERCISES:
        exercise_dir = ROOT / exercise
        for attempt in ATTEMPTS:
            result = subprocess.run(
                [sys.executable, "run_eval.py", attempt],
                cwd=exercise_dir,
                text=True,
                capture_output=True,
            )
            status = "PASS" if result.returncode == 0 else "FAIL"
            print(f"{exercise}/{attempt}: {status}")
            output = (result.stdout + result.stderr).strip()
            if output:
                print(output)
            if result.returncode != 0:
                failures.append(f"{exercise}/{attempt}")
    if failures:
        print("Failed:", ", ".join(failures))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

