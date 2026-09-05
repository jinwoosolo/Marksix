# Mark Six AI Lab V2.1

A Streamlit research dashboard for transparent Mark Six ranking, strict walk-forward validation, and a budget-constrained **2 Core + 3 Secondary + Any 1** wheel.

## What changed in V2.1

V2.1 focuses on the actual strategy hypothesis instead of only asking whether Core 12 averages more hits than random. Every historical prediction uses only data available before that draw, and the six main numbers are evaluated separately from the Extra number.

The Backtest page now measures two different questions:

- **Core 12 prediction:** average main-number hits vs the exact random expectation `12 × 6 / 49 = 1.469...`.
- **Wheel structure:** whether the actual draw has **Core >= 2 and Secondary >= 3**, which is the draw structure a complete `2C + 3S + Any1` wheel can represent.

It also shows the exact `2 Core / 3 Secondary / 1 Lowest` rate, a full Pool Composition Matrix, random partition probabilities, and rolling stability.

## Models

- `legacy_60_40` — original frequency/gap spirit, retained as a benchmark.
- `frequency` — long-run main-number frequency.
- `recent` — 30/60/120 draw recent-frequency blend.
- `gap` — current omission gap.
- `ensemble` — V2 transparent blend.
- `ensemble_v2` — V2.1 robust rank blend across multiple frequency windows plus a modest gap component.
- `ml_logistic` — experimental Logistic Regression on the Prediction page only.

No model score is presented as a true probability. A model should only be treated as interesting if it survives walk-forward and independent holdout testing.

## Smart Wheel V2.1

The old wheel generated one arbitrary sixth number per five-number skeleton. V2.1 generates valid six-number candidate structures directly:

- `2 Core + 4 Secondary`
- `3 Core + 3 Secondary`
- `2 Core + 3 Secondary + 1 Lowest` when the sixth-number pool is all 49 numbers

The optimizer then selects a fixed number of tickets according to the user's budget, balancing:

1. ranking score,
2. overlap with already-selected tickets,
3. repeated use of the same numbers.

This improves **coverage allocation**, not the intrinsic probability of any single ticket.

## Project structure

```text
Marksix/
├── app.py
├── requirements.txt
├── README.md
├── data/
├── pages/
│   ├── 1_Prediction.py
│   ├── 2_Smart_Wheel.py
│   ├── 3_Backtest.py
│   └── 4_Model_Lab.py
├── src/
│   ├── data_loader.py
│   ├── features.py
│   ├── scoring.py
│   ├── models.py
│   ├── metrics.py
│   ├── backtest.py
│   ├── wheel.py
│   └── ui.py
├── scripts/
├── tests/
├── .streamlit/
└── .github/workflows/
```

## Run locally

```bash
python -m pip install -r requirements.txt
streamlit run app.py
```

On first launch, if `data/marksix.csv` does not exist, the data loader attempts to bootstrap from the existing public `jinwoosolo/Marksix-analyzer` dataset.

## Streamlit Community Cloud

Use:

- Repository: `jinwoosolo/Marksix`
- Branch: `main`
- Main file: `app.py`

## Recommended validation workflow

1. Run 1,000-draw Model Lab comparison.
2. Compare `ensemble_v2` with `ensemble`, `gap`, `legacy_60_40`, frequency and recent.
3. Focus on both **Core 12 average hits** and **2C+3S+Any1 structure rate**.
4. Do not tune endlessly on the same 1,000 draws.
5. Freeze a final holdout period before claiming any edge.

## Interpretation warning

Mark Six is designed as a random draw. Historical patterns can be measured and ranked, but statistical variation can easily look like a predictive signal. More tickets increase coverage and cost; they do not make an individual combination intrinsically more likely to be drawn.
