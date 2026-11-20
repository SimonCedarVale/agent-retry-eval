"""Offline smoke test for paired retries. The demo uses a scripted agent."""

import argparse
import json
from collections.abc import Callable
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True)
class Attempt:
    action: str
    answer: str | None
    feedback: str | None
    tool_calls: int


def compare_retries(
    attempt: Callable[[str | None, str | None], Attempt],
    reflect: Callable[[str], str],
    judge: Callable[[Attempt], bool],
) -> list[dict]:
    first = attempt(None, None)
    if judge(first) or not first.feedback:
        raise ValueError("The demo requires a failed first attempt with feedback.")

    rows = [{"group": "shared_first_attempt", **asdict(first), "success": False}]
    for group, reflection in (("baseline", None), ("reflection", reflect(first.feedback))):
        retry = attempt(first.feedback, reflection)
        rows.append({
            "group": group,
            "prior_feedback": first.feedback,
            "reflection": reflection,
            **asdict(retry),
            "success": judge(retry),
        })
    return rows


def scripted_attempt(feedback: str | None, reflection: str | None) -> Attempt:
    # Fixture behavior: the baseline repeats its lookup, while the reflection
    # branch follows a corrected path. This exercises the harness offline.
    files = {"papers/notes.txt": "Start with the experiment section."}
    path = reflection.removeprefix("Read ") if reflection else "notes.txt"
    answer = files.get(path)
    error = None if answer is not None else f"{path} missing; check papers/{path}."
    return Attempt(f"read {path}", answer, error, tool_calls=1)


def scripted_reflection(feedback: str) -> str:
    corrected_path = feedback.split("; check ", 1)[1].removesuffix(".")
    return f"Read {corrected_path}"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=Path("artifacts"))
    args = parser.parse_args()

    rows = compare_retries(
        scripted_attempt,
        scripted_reflection,
        lambda attempt: attempt.answer == "Start with the experiment section.",
    )
    args.output_dir.mkdir(parents=True, exist_ok=True)
    records_path = args.output_dir / "retry_results.jsonl"
    with records_path.open("w", encoding="utf-8") as output:
        for row in rows:
            print(json.dumps(row, ensure_ascii=False), file=output)

    report = [
        "# Paired retry smoke test",
        "",
        "Deterministic fixture with no live model. The outcomes exercise the reporting pipeline.",
        "",
        "| Group | Task outcome | Simulated tool calls |",
        "| --- | --- | ---: |",
    ]
    for row in rows:
        outcome = "PASS" if row["success"] else "FAIL"
        report.append(f"| {row['group']} | {outcome} | {row['tool_calls']} |")
    report_text = "\n".join(report) + "\n"
    (args.output_dir / "summary.md").write_text(report_text, encoding="utf-8")
    print(report_text, end="")


if __name__ == "__main__":
    main()
