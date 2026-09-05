# Changelog

## V2.1

- Added `ensemble_v2` multi-window transparent rank blend.
- Replaced the old sign-flip p-value with an exact-random hypergeometric Monte Carlo baseline for Core 12 mean hits.
- Added Pool Composition backtest: Core / Secondary / Lowest hits must sum to six.
- Added `Core >= 2 and Secondary >= 3` strategy coverage rate.
- Added exact `2 Core + 3 Secondary + 1 Lowest` rate and analytic random baselines.
- Added Pool Composition Matrix and rolling stability chart.
- Reworked Smart Wheel candidate generation to include 2C+4S, 3C+3S, and optional 2C+3S+1L structures.
- Added budget optimizer penalties for ticket overlap and repeated number usage.
- Added full-wheel unique ticket count.
- Expanded automated tests from 6 to 12.
- Refreshed Traditional Chinese UI labels and interpretation warnings.
