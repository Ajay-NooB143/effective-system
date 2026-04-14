"""
Manages trading-tour-progress.md and git commits for each completed stop.
"""

from __future__ import annotations

import subprocess
from datetime import date
from pathlib import Path

PROGRESS_FILE = Path("trading-tour-progress.md")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _git(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], capture_output=True, text=True)


def _branch_exists(branch: str) -> bool:
    result = _git("branch", "--list", branch)
    return branch in result.stdout


def ensure_branch(branch: str = "_trading-tour") -> None:
    """Create the progress branch if it doesn't already exist."""
    if not _branch_exists(branch):
        _git("branch", branch)


# ---------------------------------------------------------------------------
# Progress file
# ---------------------------------------------------------------------------

def _read_progress() -> dict:
    """Return parsed progress as a dict.  Creates the file if absent."""
    if not PROGRESS_FILE.exists():
        return {"started": None, "completed": None, "stops": {}}

    data: dict = {"started": None, "completed": None, "stops": {}}
    for line in PROGRESS_FILE.read_text().splitlines():
        line = line.strip()
        if line.startswith("started:"):
            data["started"] = line.split(":", 1)[1].strip()
        elif line.startswith("completed:"):
            data["completed"] = line.split(":", 1)[1].strip()
        elif line.startswith("- [x]"):
            stop = line[5:].strip()
            data["stops"][stop] = "done"
        elif line.startswith("- [ ]"):
            stop = line[5:].strip()
            data["stops"][stop] = "pending"
    return data


def _write_progress(data: dict) -> None:
    lines = ["# Trading Tour Progress", ""]
    if data.get("started"):
        lines.append(f"started: {data['started']}")
    if data.get("completed"):
        lines.append(f"completed: {data['completed']}")
    if data.get("started") or data.get("completed"):
        lines.append("")
    lines.append("## Stops")
    lines.append("")
    for stop, status in data["stops"].items():
        mark = "x" if status == "done" else " "
        lines.append(f"- [{mark}] {stop}")
    lines.append("")
    PROGRESS_FILE.write_text("\n".join(lines))


def init_progress(stops: list[str]) -> None:
    """Initialise the progress file for a fresh tour."""
    data = {
        "started": str(date.today()),
        "completed": None,
        "stops": {s: "pending" for s in stops},
    }
    _write_progress(data)


def mark_stop_done(stop_name: str) -> None:
    """Mark a stop as completed and commit the progress file."""
    data = _read_progress()
    data["stops"][stop_name] = "done"
    _write_progress(data)
    _git("add", str(PROGRESS_FILE))
    _git("commit", "-m", f"trading-tour: complete {stop_name}")


def finish_tour() -> None:
    """Mark the whole tour complete and commit."""
    data = _read_progress()
    data["completed"] = str(date.today())
    _write_progress(data)
    _git("add", str(PROGRESS_FILE))
    _git("commit", "-m", "trading-tour: complete")


def get_stops_status() -> dict[str, str]:
    return _read_progress()["stops"]


# ---------------------------------------------------------------------------
# Gap map
# ---------------------------------------------------------------------------

def build_gap_map(all_stops: list[str]) -> str:
    status = get_stops_status()
    toured, skipped = [], []
    for stop in all_stops:
        if status.get(stop) == "done":
            toured.append(stop)
        else:
            skipped.append(stop)

    lines = ["", "## 🗺️ Gap Map", ""]
    lines.append(f"**Toured ({len(toured)}):**")
    for s in toured:
        lines.append(f"  ✅ {s}")
    if skipped:
        lines.append(f"\n**Skipped / available to revisit ({len(skipped)}):**")
        for s in skipped:
            lines.append(f"  ⬜ {s}")
    return "\n".join(lines)
