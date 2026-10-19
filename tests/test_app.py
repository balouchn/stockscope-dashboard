import unittest
from datetime import date
from math import sqrt
from unittest.mock import patch

import pandas as pd

from market_data import build_comparison_frames, fetch_market_data


class FakeTicker:
    def __init__(self, history: pd.DataFrame) -> None:
        self._history = history
        self.history_options: dict[str, object] = {}

    def history(self, **kwargs: object) -> pd.DataFrame:
        self.history_options = kwargs
        return self._history


class ComparisonFramesTests(unittest.TestCase):
    def setUp(self) -> None:
        dates = pd.date_range("2026-01-05", periods=35, freq="B")
        self.prices = pd.concat(
            [
                pd.DataFrame(
                    {
                        "Date": dates,
                        "ticker": ticker,
                        "Close": [100 + index * multiplier for index in range(35)],
                        "Volume": [1_000_000] * 35,
                    }
                )
                for ticker, multiplier in (("AAA", 1), ("BBB", 2), ("CCC", 3))
            ],
            ignore_index=True,
        )

    def test_indexes_each_company_to_100_at_its_first_close(self) -> None:
        frames = build_comparison_frames(
            self.prices, date(2026, 1, 5), date(2026, 2, 23)
        )
        self.assertEqual(frames["indexed"].iloc[0].tolist(), [100.0, 100.0, 100.0])
        self.assertEqual(frames["close"].iloc[0]["AAA"], 100)

    def test_drawdowns_are_non_positive_and_volume_uses_millions(self) -> None:
        frames = build_comparison_frames(
            self.prices, date(2026, 1, 5), date(2026, 2, 23)
        )
        self.assertTrue((frames["drawdown"].dropna() <= 0).all().all())
        self.assertAlmostEqual(frames["volume"].iloc[0, 0], 1.0)

    def test_drawdown_is_measured_from_the_selected_period_peak(self) -> None:
        prices = self.prices.copy()
        drop_date = prices.loc[prices["ticker"] == "AAA", "Date"].iloc[11]
        prices.loc[
            (prices["ticker"] == "AAA") & (prices["Date"] == drop_date), "Close"
        ] = 88
        frames = build_comparison_frames(
            prices, date(2026, 1, 5), date(2026, 2, 23)
        )
        self.assertAlmostEqual(frames["drawdown"].loc[drop_date, "AAA"], -20)

    def test_rolling_volatility_is_annualized_daily_return_standard_deviation(self) -> None:
        frames = build_comparison_frames(
            self.prices, date(2026, 1, 5), date(2026, 2, 23)
        )
        daily_returns = self.prices.loc[
            self.prices["ticker"] == "AAA", "Close"
        ].pct_change() * 100
        expected = daily_returns.iloc[1:21].std() * sqrt(252)
        actual = frames["volatility"].iloc[20]["AAA"]
        self.assertAlmostEqual(actual, expected)

    def test_date_filter_excludes_out_of_range_rows(self) -> None:
        frames = build_comparison_frames(
            self.prices, date(2026, 1, 12), date(2026, 1, 20)
        )
        self.assertGreaterEqual(frames["close"].index.min().date(), date(2026, 1, 12))
        self.assertLessEqual(frames["close"].index.max().date(), date(2026, 1, 20))
        self.assertFalse(pd.isna(frames["returns"].iloc[0]["AAA"]))

    def test_range_start_return_uses_the_previous_available_close(self) -> None:
        frames = build_comparison_frames(
            self.prices, date(2026, 1, 12), date(2026, 1, 20)
        )
        expected = (105 / 104 - 1) * 100
        self.assertAlmostEqual(frames["returns"].iloc[0]["AAA"], expected)

    def test_empty_date_range_returns_empty_frames(self) -> None:
        frames = build_comparison_frames(
            self.prices, date(2025, 1, 1), date(2025, 1, 2)
        )
        self.assertTrue(all(frame.empty for frame in frames.values()))

    def test_market_source_errors_are_reported_per_company(self) -> None:
        history = pd.DataFrame(
            {"Close": [123.45], "Volume": [1_000_000]},
            index=pd.DatetimeIndex(["2026-01-05"], tz="UTC"),
        )
        successful_ticker = FakeTicker(history)
        with patch(
            "market_data.yf.Ticker",
            side_effect=[successful_ticker, TimeoutError("connection timed out")],
        ):
            market, errors = fetch_market_data(
                ("AAA", "BBB"), "2026-01-05", "2026-01-06"
            )

        self.assertEqual(market["ticker"].tolist(), ["AAA"])
        self.assertIn("timed out", errors["BBB"])
        self.assertTrue(successful_ticker.history_options["auto_adjust"])


if __name__ == "__main__":
    unittest.main()
