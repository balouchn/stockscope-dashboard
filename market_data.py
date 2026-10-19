from datetime import date, timedelta

import numpy as np
import pandas as pd
import yfinance as yf


COMPANIES = {
    "AAPL": "Apple",
    "MSFT": "Microsoft",
    "NVDA": "NVIDIA",
    "GOOGL": "Alphabet",
    "AMZN": "Amazon",
}
COLORS = {
    "AAPL": "#6D1028",
    "MSFT": "#B85F3E",
    "NVDA": "#28796C",
    "GOOGL": "#78527F",
    "AMZN": "#98701E",
}


def fetch_market_data(
    tickers: tuple[str, ...], start_iso: str, end_iso: str
) -> tuple[pd.DataFrame, dict[str, str]]:
    """Fetch adjusted daily prices from Yahoo Finance and retain per-ticker errors."""
    start = date.fromisoformat(start_iso) - timedelta(days=60)
    end = date.fromisoformat(end_iso) + timedelta(days=1)
    frames: list[pd.DataFrame] = []
    errors: dict[str, str] = {}

    for ticker in tickers:
        try:
            history = yf.Ticker(ticker).history(
                start=start.isoformat(),
                end=end.isoformat(),
                auto_adjust=True,
                actions=False,
            )
            if history.empty or not {"Close", "Volume"}.issubset(history.columns):
                errors[ticker] = "Yahoo Finance returned no usable daily price or volume data."
                continue

            history = history[["Close", "Volume"]].dropna(subset=["Close"]).copy()
            history["ticker"] = ticker
            history.index = pd.to_datetime(history.index).tz_localize(None).normalize()
            frames.append(
                history.rename_axis("Date")
                .reset_index()[["Date", "ticker", "Close", "Volume"]]
            )
        except Exception as exc:
            errors[ticker] = f"{type(exc).__name__}: {exc}"

    if not frames:
        return pd.DataFrame(columns=["Date", "ticker", "Close", "Volume"]), errors
    return pd.concat(frames, ignore_index=True), errors


def build_comparison_frames(
    prices: pd.DataFrame, start: date, end: date
) -> dict[str, pd.DataFrame]:
    """Prepare shared-period price, return, volume, volatility, and drawdown series."""
    data = prices.copy()
    data["Date"] = pd.to_datetime(data["Date"]).dt.tz_localize(None).dt.normalize()
    period_data = data.loc[
        (data["Date"].dt.date >= start) & (data["Date"].dt.date <= end)
    ]
    if period_data.empty:
        empty = pd.DataFrame()
        return {
            "close": empty,
            "indexed": empty,
            "returns": empty,
            "volume": empty,
            "volatility": empty,
            "drawdown": empty,
        }

    close = period_data.pivot_table(
        index="Date", columns="ticker", values="Close", aggfunc="last"
    ).sort_index()
    close = close.dropna(axis="columns", how="all")
    volume = (
        period_data.pivot_table(
            index="Date", columns="ticker", values="Volume", aggfunc="last"
        )
        .sort_index()
        .reindex(columns=close.columns)
        / 1_000_000
    )
    all_close = (
        data.pivot_table(
            index="Date", columns="ticker", values="Close", aggfunc="last"
        )
        .sort_index()
        .reindex(columns=close.columns)
    )
    baseline = close.apply(lambda series: series.dropna().iloc[0])
    all_returns = all_close.pct_change(fill_method=None) * 100
    returns = all_returns.reindex(close.index)
    volatility = (
        all_returns.rolling(window=30, min_periods=20).std() * np.sqrt(252)
    ).reindex(close.index)

    return {
        "close": close,
        "indexed": close.divide(baseline, axis="columns") * 100,
        "returns": returns,
        "volume": volume,
        "volatility": volatility,
        "drawdown": (close.divide(close.cummax()) - 1) * 100,
    }
