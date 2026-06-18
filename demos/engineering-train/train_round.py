import argparse
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
ALLOWED_TOOLS = "Bash,Read,Edit,Write,Glob,Grep"


PROMPT_TEMPLATE = """You are doing an engineering training exercise.

Read:
- {task}

Implement only:
- {attempt_file}

Do not edit any other files.

After editing, run or reason against:
- python run_eval.py claude_attempt

Engineering expectations:
- Match the written spec and edge cases.
- Keep the implementation simple, robust, and scoped.
- Do not mutate inputs unless the task explicitly allows it.
- If validation fails, use the failure output to fix the root cause.
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("exercise")
    parser.add_argument("--run-claude", action="store_true")
    args = parser.parse_args()

    exercise_dir = ROOT / args.exercise
    if not exercise_dir.exists():
        print(f"unknown exercise: {args.exercise}")
        return 2

    attempt_files = list((exercise_dir / "claude_attempt").glob("*.py"))
    if len(attempt_files) != 1:
        print("expected exactly one Python file in claude_attempt")
        return 2

    prompt = PROMPT_TEMPLATE.format(
        task=exercise_dir / "task.md",
        attempt_file=attempt_files[0],
    )
    prompt_path = exercise_dir / "claude_prompt.txt"
    prompt_path.write_text(prompt, encoding="utf-8")

    print(f"Wrote prompt: {prompt_path}")
    print("Manual command:")
    print(
        "claude -p --permission-mode acceptEdits "
        f"--allowedTools {ALLOWED_TOOLS} --add-dir {exercise_dir} -- "
        f"\"{prompt.replace(chr(10), ' ')}\""
    )

    if args.run_claude:
        command = [
            "claude",
            "-p",
            "--permission-mode",
            "acceptEdits",
            "--allowedTools",
            ALLOWED_TOOLS,
            "--add-dir",
            str(exercise_dir),
            "--",
            prompt,
        ]
        result = subprocess.run(
            command,
            cwd=exercise_dir,
            text=True,
            capture_output=True,
            timeout=600,
        )
        print(result.stdout)
        print(result.stderr, file=sys.stderr)
        if result.returncode != 0:
            print(f"claude exited with {result.returncode}")

    eval_result = subprocess.run(
        [sys.executable, "run_eval.py", "claude_attempt"],
        cwd=exercise_dir,
        text=True,
        capture_output=True,
    )
    print(eval_result.stdout)
    if eval_result.stderr:
        print(eval_result.stderr, file=sys.stderr)
    return eval_result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
