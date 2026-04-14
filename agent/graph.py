"""
agent/graph.py — State-machine graph for the trading tour agent.

States
------
IDLE       → waiting for a command
SURVEY     → asking the 3 calibration questions
TOURING    → stepping through tour stops one-by-one
COMPLETE   → tour finished, gap map shown

Transitions
-----------
IDLE    --/_learn--> SURVEY
SURVEY  --done-----> TOURING
TOURING --done-----> COMPLETE
COMPLETE-----------> IDLE  (user can restart)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Optional


class State(Enum):
    IDLE = auto()
    SURVEY = auto()
    TOURING = auto()
    COMPLETE = auto()


@dataclass
class TourContext:
    """All mutable state carried through the agent graph."""

    state: State = State.IDLE

    # Survey answers
    survey_answers: list[str] = field(default_factory=list)
    survey_step: int = 0

    # Stop list built after survey
    stops: list[str] = field(default_factory=list)
    current_stop_index: int = 0

    # Level inferred from survey (beginner / intermediate / advanced)
    user_level: str = "beginner"


# ---------------------------------------------------------------------------
# Graph transitions
# ---------------------------------------------------------------------------

def transition(ctx: TourContext, event: str, payload: str = "") -> TourContext:
    """
    Apply *event* to *ctx* and return the (mutated) context.

    Events
    ------
    start_learn   : user typed /_learn
    survey_answer : user answered a survey question
    next_stop     : user is ready to advance to the next stop
    finish        : all stops done
    reset         : return to IDLE
    """
    if event == "start_learn":
        ctx.state = State.SURVEY
        ctx.survey_answers = []
        ctx.survey_step = 0

    elif event == "survey_answer":
        ctx.survey_answers.append(payload)
        ctx.survey_step += 1

    elif event == "survey_done":
        ctx.user_level = _infer_level(ctx.survey_answers)
        ctx.state = State.TOURING
        ctx.current_stop_index = 0

    elif event == "next_stop":
        ctx.current_stop_index += 1

    elif event == "finish":
        ctx.state = State.COMPLETE

    elif event == "reset":
        ctx.__init__()  # type: ignore[misc]

    return ctx


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

_BEGINNER_KEYWORDS = {"new", "beginner", "learning", "start", "never", "no"}
_ADVANCED_KEYWORDS = {"advanced", "expert", "years", "professional", "quant"}


def _infer_level(answers: list[str]) -> str:
    text = " ".join(answers).lower()
    adv_hits = sum(1 for kw in _ADVANCED_KEYWORDS if kw in text)
    beg_hits = sum(1 for kw in _BEGINNER_KEYWORDS if kw in text)
    if adv_hits > beg_hits:
        return "advanced"
    if adv_hits == beg_hits and adv_hits > 0:
        return "intermediate"
    if beg_hits > 0:
        return "beginner"
    return "intermediate"
