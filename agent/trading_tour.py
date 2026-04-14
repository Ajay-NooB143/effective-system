"""
agent/trading_tour.py — Stop definitions, survey questions, and the
interactive runner that presents each stop to the user.

Per the codebase: stop content is driven by agent/graph.py state transitions.
Per trading theory: stops follow the canonical learning sequence
  Market Structure → Entry Logic → Risk Management → Checkpointing.
Uncertain — verify before trading with real capital: any specific price
  levels, indicator thresholds, or strategy claims made here.
"""

from __future__ import annotations

from typing import Optional

from agent.graph import TourContext, State, transition
from agent import progress

# ---------------------------------------------------------------------------
# Survey
# ---------------------------------------------------------------------------

SURVEY_QUESTIONS = [
    "1️⃣  How long have you been studying or trading markets? "
    "(e.g. 'never traded', '6 months', '3 years as a prop trader')",

    "2️⃣  Which concept feels most confusing right now? "
    "(e.g. 'market structure', 'entries', 'risk sizing', 'all of it')",

    "3️⃣  What is your primary goal for this tour? "
    "(e.g. 'understand the codebase', 'learn trading basics', 'both')",
]

# ---------------------------------------------------------------------------
# Stop catalogue
# ---------------------------------------------------------------------------
# Each stop is a dict with:
#   name        – unique identifier / commit label
#   title       – display title
#   levels      – which user levels see this stop ('all' = everyone)
#   content     – the main teaching text (short, interactive)
#   demo_prompt – question/exercise shown after the content
#   fact_labels – list of (claim, label) tuples shown in a "fact check" block

STOP_CATALOGUE: list[dict] = [
    {
        "name": "Market Structure",
        "title": "Stop 1 · Market Structure",
        "levels": "all",
        "content": (
            "Markets move in waves: higher-highs / higher-lows (uptrend) or "
            "lower-highs / lower-lows (downtrend). A **Break of Structure (BoS)** "
            "signals a potential trend change; a **Change of Character (CHoCH)** "
            "confirms it."
        ),
        "demo_prompt": (
            "Look at the last 20 candles on any chart. "
            "Can you spot the most recent swing high and swing low? "
            "Type what you see (or 'skip' to continue)."
        ),
        "fact_labels": [
            ("Higher-highs / higher-lows define an uptrend.", "Per trading theory"),
            ("BoS / CHoCH terminology is widely used in ICT / SMC methodology.",
             "Per trading theory — Uncertain: exact definitions vary by educator"),
        ],
    },
    {
        "name": "Order Blocks",
        "title": "Stop 2 · Order Blocks",
        "levels": "all",
        "content": (
            "An **Order Block (OB)** is the last bearish candle before a bullish "
            "impulse (bullish OB) or the last bullish candle before a bearish "
            "impulse (bearish OB). Price often returns to these zones before "
            "continuing in the impulse direction."
        ),
        "demo_prompt": (
            "On your chart, find the most recent strong move. "
            "What is the colour of the candle just before that move started? "
            "(or 'skip')"
        ),
        "fact_labels": [
            ("Order blocks are supply/demand zones defined by the last opposing candle.",
             "Per trading theory"),
            ("Price returning to an OB is not guaranteed.",
             "Uncertain — verify before trading with real capital"),
        ],
    },
    {
        "name": "Fair Value Gaps",
        "title": "Stop 3 · Fair Value Gaps (FVG)",
        "levels": "all",
        "content": (
            "A **Fair Value Gap** is a three-candle pattern where candle 1's wick "
            "and candle 3's wick do not overlap — leaving an imbalanced price range. "
            "Price frequently 'fills' the gap before continuing."
        ),
        "demo_prompt": (
            "Can you find a three-candle sequence on your chart where there is a "
            "visible gap between candle 1's high and candle 3's low (or vice versa)? "
            "(or 'skip')"
        ),
        "fact_labels": [
            ("FVGs represent price imbalance / inefficiency.", "Per trading theory"),
            ("Not every FVG gets filled.", "Per trading theory"),
        ],
    },
    {
        "name": "Entry Logic",
        "title": "Stop 4 · Entry Logic",
        "levels": "all",
        "content": (
            "A high-probability entry combines: (1) a premium/discount zone "
            "(OB or FVG), (2) confirmation (CHoCH on a lower timeframe), and "
            "(3) a defined invalidation level (stop-loss placement)."
        ),
        "demo_prompt": (
            "Given a bullish OB on the 1H chart with a CHoCH on the 15m, "
            "where would you place your entry? What would invalidate the trade? "
            "(or 'skip')"
        ),
        "fact_labels": [
            ("Confluence of zone + confirmation improves win rate.", "Per trading theory"),
            ("Win rate improvement figures vary — no universal stat.",
             "Uncertain — verify before trading with real capital"),
        ],
    },
    {
        "name": "Risk Management",
        "title": "Stop 5 · Risk Management",
        "levels": "all",
        "content": (
            "Risk per trade is typically 0.5–2% of account equity. "
            "Position size = (Account × Risk%) / (Entry − Stop). "
            "Minimum reward:risk target is usually 1:2 or better."
        ),
        "demo_prompt": (
            "Account: $10,000, Risk: 1%, Entry: 1.2000, Stop: 1.1950. "
            "What is your position size in units? (or 'skip')"
        ),
        "fact_labels": [
            ("Position sizing formula: (Account × Risk%) / (Entry − Stop).",
             "Per trading theory"),
            ("The 1–2% rule is a common guideline, not a guarantee of success.",
             "Uncertain — verify before trading with real capital"),
        ],
    },
    {
        "name": "Checkpointing",
        "title": "Stop 6 · Checkpointing & Review",
        "levels": "all",
        "content": (
            "After every trade (win or loss) log: date/time, asset, direction, "
            "entry, stop, target, outcome, and your reasoning. "
            "Review weekly: are entries consistent? Is risk being respected?"
        ),
        "demo_prompt": (
            "Open a spreadsheet or text file right now and create the column headers "
            "for your trade journal. Done? (yes / skip)"
        ),
        "fact_labels": [
            ("Journaling is universally recommended by professional traders.",
             "Per trading theory"),
            ("Specific review cadence (weekly vs daily) is personal preference.",
             "Per trading theory"),
        ],
    },
    # Advanced-only stop
    {
        "name": "Liquidity & Inducement",
        "title": "Stop 7 · Liquidity & Inducement (Advanced)",
        "levels": "advanced",
        "content": (
            "Price hunts **liquidity** (clusters of stops) before reversing. "
            "An **inducement** is a false move that triggers retail stops, "
            "allowing institutions to fill large orders at better prices."
        ),
        "demo_prompt": (
            "On your chart, identify a swing point that was briefly broken then "
            "immediately reversed. Was that a liquidity sweep? (or 'skip')"
        ),
        "fact_labels": [
            ("Stop hunts / liquidity sweeps are observed across all liquid markets.",
             "Per trading theory"),
            ("'Institutional' intent behind moves is inferred, not proven.",
             "Uncertain — verify before trading with real capital"),
        ],
    },
]


# ---------------------------------------------------------------------------
# Stop list builder
# ---------------------------------------------------------------------------

def build_stop_list(ctx: TourContext) -> list[str]:
    """Return stop names appropriate for the user's level."""
    names = []
    for stop in STOP_CATALOGUE:
        lvl = stop["levels"]
        if lvl == "all" or lvl == ctx.user_level:
            names.append(stop["name"])
    return names


def _get_stop(name: str) -> Optional[dict]:
    for s in STOP_CATALOGUE:
        if s["name"] == name:
            return s
    return None


# ---------------------------------------------------------------------------
# Presenter helpers
# ---------------------------------------------------------------------------

def _render_stop(stop: dict, level: str) -> str:
    depth_note = {
        "beginner": "_(beginner depth)_",
        "intermediate": "_(intermediate depth)_",
        "advanced": "_(advanced depth)_",
    }.get(level, "")

    lines = [
        f"\n{'─' * 50}",
        f"### {stop['title']}  {depth_note}",
        "",
        stop["content"],
        "",
        "**Fact check:**",
    ]
    for claim, label in stop["fact_labels"]:
        lines.append(f"  • {label}: _{claim}_")
    lines += [
        "",
        f"**Demo / Exercise:**",
        f"> {stop['demo_prompt']}",
        "",
        "_(Type your answer, or press Enter to skip)_",
        f"{'─' * 50}",
    ]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main interactive runner
# ---------------------------------------------------------------------------

def run_tour(read_line=None, write=None) -> None:
    """
    Drive the full trading tour interactively.

    Parameters
    ----------
    read_line : callable() -> str   (defaults to input())
    write     : callable(str)       (defaults to print())
    """
    if read_line is None:
        read_line = input
    if write is None:
        write = print

    ctx = TourContext()
    transition(ctx, "start_learn")

    # ── Survey ────────────────────────────────────────────────────────────
    write("\n🚀 Welcome to the Trading Tour!  (/_learn)\n")
    write("First, 3 quick questions to personalise your tour.\n")

    for q in SURVEY_QUESTIONS:
        write(q)
        answer = ""
        while not answer:
            answer = read_line().strip()
            if not answer:
                write("  (Please type an answer, or type 'skip' to continue.)")
        if answer.lower() == "skip":
            answer = "no answer"
        transition(ctx, "survey_answer", answer)

    transition(ctx, "survey_done")

    # ── Build stop list ───────────────────────────────────────────────────
    ctx.stops = build_stop_list(ctx)
    progress.init_progress(ctx.stops)

    write(
        f"\n✅ Survey complete.  Level detected: **{ctx.user_level}**\n"
        f"Your tour has {len(ctx.stops)} stops:\n"
    )
    for i, name in enumerate(ctx.stops, 1):
        write(f"  {i}. {name}")
    write("\nLet's begin! Press Enter at each stop to continue.\n")

    # ── Tour stops ────────────────────────────────────────────────────────
    while ctx.current_stop_index < len(ctx.stops):
        stop_name = ctx.stops[ctx.current_stop_index]
        stop_data = _get_stop(stop_name)
        if stop_data is None:
            transition(ctx, "next_stop")
            continue

        write(_render_stop(stop_data, ctx.user_level))
        read_line()  # wait for user to acknowledge / answer

        progress.mark_stop_done(stop_name)
        write(f"✔ Stop committed: {stop_name}\n")

        transition(ctx, "next_stop")

    # ── Completion ────────────────────────────────────────────────────────
    transition(ctx, "finish")
    progress.finish_tour()

    write("\n🎉 Tour complete!\n")
    write(progress.build_gap_map(ctx.stops))
    write(
        "\n\nAll progress committed to git (trading-tour: complete).\n"
        "Revisit any skipped stop by re-running /_learn.\n"
    )
