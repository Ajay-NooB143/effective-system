export const STOP_CATALOGUE = [
  {
    name: "Market Structure",
    title: "Stop 1 · Market Structure",
    levels: "all",
    content:
      "Markets move in waves: higher-highs / higher-lows (uptrend) or lower-highs / lower-lows (downtrend). A Break of Structure (BoS) signals a potential trend change; a Change of Character (CHoCH) confirms it.",
    demo_prompt:
      "Look at the last 20 candles on any chart. Can you spot the most recent swing high and swing low? Type what you see (or 'skip' to continue).",
    fact_labels: [
      ["Higher-highs / higher-lows define an uptrend.", "Per trading theory"],
      [
        "BoS / CHoCH terminology is widely used in ICT / SMC methodology.",
        "Per trading theory — Uncertain: exact definitions vary by educator",
      ],
    ],
  },
  {
    name: "Order Blocks",
    title: "Stop 2 · Order Blocks",
    levels: "all",
    content:
      "An Order Block (OB) is the last bearish candle before a bullish impulse (bullish OB) or the last bullish candle before a bearish impulse (bearish OB). Price often returns to these zones before continuing in the impulse direction.",
    demo_prompt:
      "On your chart, find the most recent strong move. What is the colour of the candle just before that move started? (or 'skip')",
    fact_labels: [
      [
        "Order blocks are supply/demand zones defined by the last opposing candle.",
        "Per trading theory",
      ],
      [
        "Price returning to an OB is not guaranteed.",
        "Uncertain — verify before trading with real capital",
      ],
    ],
  },
  {
    name: "Fair Value Gaps",
    title: "Stop 3 · Fair Value Gaps (FVG)",
    levels: "all",
    content:
      "A Fair Value Gap is a three-candle pattern where candle 1's wick and candle 3's wick do not overlap — leaving an imbalanced price range. Price frequently 'fills' the gap before continuing.",
    demo_prompt:
      "Can you find a three-candle sequence on your chart where there is a visible gap between candle 1's high and candle 3's low (or vice versa)? (or 'skip')",
    fact_labels: [
      ["FVGs represent price imbalance / inefficiency.", "Per trading theory"],
      ["Not every FVG gets filled.", "Per trading theory"],
    ],
  },
  {
    name: "Entry Logic",
    title: "Stop 4 · Entry Logic",
    levels: "all",
    content:
      "A high-probability entry combines: (1) a premium/discount zone (OB or FVG), (2) confirmation (CHoCH on a lower timeframe), and (3) a defined invalidation level (stop-loss placement).",
    demo_prompt:
      "Given a bullish OB on the 1H chart with a CHoCH on the 15m, where would you place your entry? What would invalidate the trade? (or 'skip')",
    fact_labels: [
      [
        "Confluence of zone + confirmation improves win rate.",
        "Per trading theory",
      ],
      [
        "Win rate improvement figures vary — no universal stat.",
        "Uncertain — verify before trading with real capital",
      ],
    ],
  },
  {
    name: "Risk Management",
    title: "Stop 5 · Risk Management",
    levels: "all",
    content:
      "Risk per trade is typically 0.5–2% of account equity. Position size = (Account × Risk%) / (Entry − Stop). Minimum reward:risk target is usually 1:2 or better.",
    demo_prompt:
      "Account: $10,000, Risk: 1%, Entry: 1.2000, Stop: 1.1950. What is your position size in units? (or 'skip')",
    fact_labels: [
      [
        "Position sizing formula: (Account × Risk%) / (Entry − Stop).",
        "Per trading theory",
      ],
      [
        "The 1–2% rule is a common guideline, not a guarantee of success.",
        "Uncertain — verify before trading with real capital",
      ],
    ],
  },
  {
    name: "Checkpointing",
    title: "Stop 6 · Checkpointing & Review",
    levels: "all",
    content:
      "After every trade (win or loss) log: date/time, asset, direction, entry, stop, target, outcome, and your reasoning. Review weekly: are entries consistent? Is risk being respected?",
    demo_prompt:
      "Open a spreadsheet or text file right now and create the column headers for your trade journal. Done? (yes / skip)",
    fact_labels: [
      [
        "Journaling is universally recommended by professional traders.",
        "Per trading theory",
      ],
      [
        "Specific review cadence (weekly vs daily) is personal preference.",
        "Per trading theory",
      ],
    ],
  },
  {
    name: "Liquidity & Inducement",
    title: "Stop 7 · Liquidity & Inducement (Advanced)",
    levels: "advanced",
    content:
      "Price hunts liquidity (clusters of stops) before reversing. An inducement is a false move that triggers retail stops, allowing institutions to fill large orders at better prices.",
    demo_prompt:
      "On your chart, identify a swing point that was briefly broken then immediately reversed. Was that a liquidity sweep? (or 'skip')",
    fact_labels: [
      [
        "Stop hunts / liquidity sweeps are observed across all liquid markets.",
        "Per trading theory",
      ],
      [
        "'Institutional' intent behind moves is inferred, not proven.",
        "Uncertain — verify before trading with real capital",
      ],
    ],
  },
];

export function buildStopList(level) {
  return STOP_CATALOGUE.filter(
    (s) => s.levels === "all" || s.levels === level
  );
}

export function inferLevel(answers) {
  const text = answers.join(" ").toLowerCase();
  const advKw = ["advanced", "expert", "years", "professional", "quant"];
  const begKw = ["new", "beginner", "learning", "start", "never", "no"];
  const advHits = advKw.filter((kw) => text.includes(kw)).length;
  const begHits = begKw.filter((kw) => text.includes(kw)).length;
  if (advHits > begHits) return "advanced";
  if (advHits === begHits && advHits > 0) return "intermediate";
  if (begHits > 0) return "beginner";
  return "intermediate";
}
