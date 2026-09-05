# Mark Six AI Lab V2

A research-first Streamlit rebuild of the original `Marksix-analyzer` project.

## Goals

1. Separate **main-number hits** from the Extra number.
2. Validate the Core-12 hypothesis with strict walk-forward testing.
3. Compare every model with a mathematically defined random baseline.
4. Research the user's **2 Core + 3 Secondary + 1** Smart Wheel structure.
5. Optimize a finite betting budget for score + diversification instead of pretending an unlimited "full cover" is practical.
6. Keep prediction, backtesting and UI logic modular.

> Important: model scores are rankings, not guaranteed probabilities. A fair lottery is expected to be random; the purpose of this project is to test whether any apparent historical edge survives out-of-sample validation.

## Pages

- **Home** — latest draw, Core 12, Secondary 32, Lowest-ranked 5.
- **Prediction** — transparent statistical models and an experimental logistic-regression model.
- **Smart Wheel** — 2 Core + 3 Secondary + 1, with budget-aware ticket diversification.
- **Backtest** — strict walk-forward Core-12 validation; Extra is reported separately.
- **Model Lab** — compares Legacy 60/40, frequency, recent trend, gap and ensemble models under identical rules.

## Repository structure

```text
Marksix/
├── app.py
├── requirements.txt
├── README.md
├── data/
│   └── README.md
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
├── tests/
└── .github/workflows/tests.yml
```

## Data

On first run, if `data/marksix.csv` does not exist, the app automatically bootstraps the public historical CSV from the old project:

`https://raw.githubusercontent.com/jinwoosolo/Marksix-analyzer/main/marksix.csv`

After download it is saved locally as `data/marksix.csv`.

Required fields are:

```text
date,n1,n2,n3,n4,n5,n6,extra
```

Additional legacy columns are preserved when available.

## Run locally

Python 3.11 is recommended.

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

macOS/Linux:

```bash
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Streamlit Community Cloud deployment

1. Push all files to `jinwoosolo/Marksix`.
2. In Streamlit Community Cloud, create a new app.
3. Repository: `jinwoosolo/Marksix`
4. Branch: `main`
5. Main file: `app.py`
6. Deploy.

The first app launch needs outbound internet access so it can bootstrap `data/marksix.csv` if the CSV is not committed to the new repository.

### Recommended production setup

For maximum reliability, copy the latest `marksix.csv` from the old repository into `data/marksix.csv` and commit it. The automatic remote bootstrap then becomes a fallback rather than a hard dependency.

## Core-12 benchmark

For 6 main numbers drawn from 49, a random set of 12 numbers has expected main-number hits:

```text
12 × 6 / 49 = 1.469387755...
```

The Backtest page compares observed Core-12 results with this baseline. It reports:

- average main-number hits;
- bootstrap confidence interval;
- 2+, 3+ and 4+ hit rates;
- one-sided permutation p-value;
- Extra hit separately.

A good-looking historical average is **not** enough. If many models or weights are tested, reserve a final untouched holdout period before making any claim of edge.

## Smart Wheel logic

Default partition:

```text
49 numbers
├── Core 12
├── Secondary 32
└── Lowest-ranked 5
```

Ticket template:

```text
2 Core + 3 Secondary + 1 additional number
```

There are:

```text
C(12,2) = 66 Core pairs
C(32,3) = 4,960 Secondary triples
66 × 4,960 = 327,360 five-number skeletons
```

Adding every possible sixth number to every skeleton creates millions of raw variants and many duplicates. V2 therefore exposes a finite-budget optimizer that tries to balance model score with ticket diversification.

## Models

### `legacy_60_40`
Recreates the spirit of V1's 60% frequency + 40% gap ranking, but normalizes components for comparison.

### `frequency`
Long-run frequency only.

### `recent`
Short- and medium-window frequency blend.

### `gap`
Gap ranking only. Included mainly to test whether the mean-reversion assumption actually survives out-of-sample testing.

### `ensemble`
Transparent blend of long-term frequency, recent frequency, trend, gap and previous-draw status. This is a research baseline, not a claim of true predictive probability.

### `ml_logistic`
Experimental logistic-regression ranking trained on historical number-level features. It is intentionally not the default until it passes proper holdout validation.

## Tests

```bash
pytest -q
```

GitHub Actions runs the test suite on pushes and pull requests.

## Next research milestones

- Frozen final holdout period.
- Multiple-testing correction when comparing many weights/models.
- Full Smart-Wheel historical backtest at equal ticket counts against random tickets.
- Prize-tier and cost/return simulation using historical prize tables where reliable.
- Periodic model refit for ML walk-forward evaluation.
- Coverage diagnostics: unique tickets, number exposure, pair/triple exposure and overlap heat maps.

## Responsible interpretation

The app should describe the bottom five as **Lowest-ranked 5**, not "five numbers that will not appear". Likewise, a Core 12 score is a model ranking rather than a guarantee or objectively known draw probability.
