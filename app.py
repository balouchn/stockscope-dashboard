from datetime import date, timedelta
from typing import Any

import pandas as pd
import plotly.express as px
import streamlit as st
from market_data import COLORS, COMPANIES, build_comparison_frames, fetch_market_data

st.set_page_config(
    page_title="StockScope | Company comparison",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_data(ttl=3600, show_spinner=False)
def load_market_data(
    tickers: tuple[str, ...], start_iso: str, end_iso: str
) -> tuple[pd.DataFrame, dict[str, str]]:
    return fetch_market_data(tickers, start_iso, end_iso)


def _long_frame(frame: pd.DataFrame, value_name: str) -> pd.DataFrame:
    return (
        frame.rename_axis("Date")
        .reset_index()
        .melt(id_vars="Date", var_name="Ticker", value_name=value_name)
        .dropna(subset=[value_name])
    )


def _line_chart(
    frame: pd.DataFrame, title: str, y_title: str, *, percent_axis: bool = False
) -> Any:
    long_frame = _long_frame(frame, y_title)
    figure = px.line(
        long_frame,
        x="Date",
        y=y_title,
        color="Ticker",
        color_discrete_map=COLORS,
        title=title,
        labels={"Date": "Trading date", y_title: y_title, "Ticker": "Company"},
    )
    figure.update_layout(
        template="plotly_white",
        hovermode="x unified",
        legend_title_text="Company",
        margin=dict(l=12, r=12, t=58, b=12),
        title_font_size=17,
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        font=dict(family="Arial, sans-serif", color="#292329", size=12),
        title_font_color="#420B1A",
        legend=dict(font=dict(color="#292329")),
    )
    figure.update_xaxes(
        showgrid=False,
        color="#51464D",
        linecolor="#E8D5D5",
        title_font_color="#51464D",
    )
    figure.update_yaxes(
        ticksuffix="%" if percent_axis else None,
        color="#51464D",
        gridcolor="#EEE7E6",
        linecolor="#E8D5D5",
        zerolinecolor="#D9C4C6",
        title_font_color="#51464D",
    )
    figure.update_traces(line=dict(width=2))
    return figure


def _distribution_chart(returns: pd.DataFrame) -> Any:
    long_frame = _long_frame(returns, "Daily return (%)")
    figure = px.box(
        long_frame,
        x="Ticker",
        y="Daily return (%)",
        color="Ticker",
        color_discrete_map=COLORS,
        points=False,
        title="Daily return distribution",
        labels={"Ticker": "Company", "Daily return (%)": "Daily return (%)"},
    )
    figure.update_layout(
        template="plotly_white",
        showlegend=False,
        margin=dict(l=12, r=12, t=58, b=12),
        title_font_size=17,
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        font=dict(family="Arial, sans-serif", color="#292329", size=12),
        title_font_color="#420B1A",
    )
    figure.update_xaxes(color="#51464D", linecolor="#E8D5D5")
    figure.update_yaxes(
        ticksuffix="%",
        color="#51464D",
        gridcolor="#EEE7E6",
        linecolor="#E8D5D5",
        zerolinecolor="#D9C4C6",
    )
    return figure


st.markdown(
    """
    <style>
    :root { color-scheme: light; }
    [data-testid="stAppViewContainer"],
    [data-testid="stMain"] { background: #FAF7F5; }
    [data-testid="stHeader"] { background: rgba(250, 247, 245, .96); }
    [data-testid="stSidebar"] {
        background: #420B1A;
        border-right: 1px solid #6D1028;
    }
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {
        color: #FAF7F5;
    }
    [data-testid="stSidebar"] [data-testid="stCaptionContainer"] {
        color: #E8D5D5;
    }
    [data-testid="stSidebar"] input,
    [data-testid="stSidebar"] [data-testid="stDateInputField"] *,
    [data-testid="stSidebar"] [data-baseweb="select"] * {
        color: #292329 !important;
        -webkit-text-fill-color: #292329 !important;
    }
    [data-testid="stSidebar"] [data-baseweb="select"] {
        background: #FFFFFF;
        border-radius: 8px;
    }
    [data-testid="stSidebar"] [data-baseweb="tag"] {
        background: #6D1028;
        border: 1px solid #E8D5D5;
    }
    [data-testid="stSidebar"] [data-baseweb="tag"] *,
    [data-testid="stSidebar"] [data-baseweb="tag"] svg {
        color: #FFFFFF !important;
        fill: #FFFFFF;
        -webkit-text-fill-color: #FFFFFF !important;
    }
    [data-testid="stSidebar"] [role="option"] {
        color: #292329;
        background: #FFFFFF;
    }
    [data-testid="stSidebar"] button { border-color: #E8D5D5; }
    [data-testid="stSidebar"] button:hover {
        border-color: #FFFFFF;
        color: #FFFFFF;
    }
    [data-testid="stAppViewContainer"] button[kind="primary"],
    [data-testid="stAppViewContainer"] [data-testid="stBaseButton-primary"] {
        background: #6D1028;
        border-color: #6D1028;
        color: #FFFFFF;
    }
    [data-testid="stAppViewContainer"] button[kind="primary"]:hover,
    [data-testid="stAppViewContainer"] [data-testid="stBaseButton-primary"]:hover {
        background: #420B1A;
        border-color: #420B1A;
        color: #FFFFFF;
    }
    .hero {
        padding: 1.4rem 1.6rem;
        border-radius: 16px;
        background: linear-gradient(120deg, #420B1A, #6D1028);
        color: #FFFFFF;
        margin-bottom: 1rem;
        box-shadow: 0 8px 24px rgba(66, 11, 26, .12);
    }
    .hero h1 { color: #FFFFFF; margin: 0; }
    .hero p { color: #FAF7F5; margin: .4rem 0 0; }
    .hero .eyebrow {
        color: #E8D5D5;
        font-size: .75rem;
        font-weight: 700;
        letter-spacing: .16em;
        margin-bottom: .45rem;
        text-transform: uppercase;
    }
    .hero .byline {
        border-top: 1px solid rgba(250, 247, 245, .3);
        color: #FFFFFF;
        display: flex;
        flex-wrap: wrap;
        gap: .5rem 1.5rem;
        margin-top: 1rem;
        padding-top: .75rem;
    }
    [data-testid="stMain"] h2,
    [data-testid="stMain"] h3 { color: #420B1A; }
    [data-testid="stMetric"] {
        background: #FFFFFF;
        border: 1px solid #E8D5D5;
        border-top: 3px solid #6D1028;
        padding: .8rem 1rem;
        border-radius: 12px;
    }
    [data-testid="stMetric"] label,
    [data-testid="stMetric"] [data-testid="stMetricLabel"] {
        color: #51464D;
    }
    [data-testid="stPlotlyChart"] {
        background: #FFFFFF;
        border: 1px solid #E8D5D5;
        border-radius: 12px;
        padding: .35rem;
    }
    [data-testid="stAlert"] { border-left-color: #6D1028; }
    @media (max-width: 700px) {
        .hero { padding: 1rem; }
        .hero h1 { font-size: 1.7rem; }
        [data-testid="stPlotlyChart"] { padding: .1rem; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.title("StockScope")
    st.caption("A market comparison dashboard")
    selected_tickers = st.multiselect(
        "Companies",
        options=list(COMPANIES),
        default=["AAPL", "MSFT", "NVDA"],
        format_func=lambda ticker: f"{COMPANIES[ticker]} ({ticker})",
        help="Select at least three companies. Every visualization uses this selection.",
    )
    if len(selected_tickers) < 3:
        st.warning("Choose at least three companies for the assignment comparison.")
        st.stop()

    today = date.today()
    start_default = today - timedelta(days=365)
    selected_dates = st.date_input(
        "Date range",
        value=(start_default, today),
        min_value=date(2015, 1, 1),
        max_value=today,
        format="MM/DD/YYYY",
        help="All comparison charts use this date range.",
    )
if not isinstance(selected_dates, (tuple, list)) or len(selected_dates) != 2:
    st.info("Select both a start date and an end date to load the comparison.")
    st.stop()

start_date, end_date = selected_dates
if start_date > end_date:
    st.error("The start date must be on or before the end date.")
    st.stop()

st.markdown(
    f"""
    <div class="hero">
      <div class="eyebrow">StockScope · Market comparison</div>
      <h1>Public company performance, side by side</h1>
      <p>Compare market performance, trading activity, risk, and drawdowns with one shared filter.</p>
      <div class="byline">
        <span>Prepared by Noorulain Balouch</span>
        <span>Developed for CPS*5745</span>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.spinner("Loading the latest available daily market data from Yahoo Finance..."):
    market_data, data_errors = load_market_data(
        tuple(selected_tickers), start_date.isoformat(), end_date.isoformat()
    )

for ticker, message in data_errors.items():
    st.warning(f"Could not load {COMPANIES[ticker]} ({ticker}): {message}")

if market_data.empty:
    st.error(
        "No market data could be loaded for this selection and date range. "
        "Check your internet connection and try again."
    )
    st.stop()

frames = build_comparison_frames(market_data, start_date, end_date)
close = frames["close"]
available_tickers = list(close.columns)
if len(available_tickers) < 3:
    st.error(
        f"Only {len(available_tickers)} selected companies have data in this date "
        "range; at least three are required. Try another date range or refresh later."
    )
    st.stop()

latest_date = close.index.max()
latest_date_label = pd.Timestamp(latest_date).strftime("%b %d, %Y")
selected_company_labels = ", ".join(
    f"{COMPANIES[ticker]} ({ticker})"
    for ticker in selected_tickers
    if ticker in available_tickers
)
first_prices = close.apply(lambda series: series.dropna().iloc[0])
last_prices = close.apply(lambda series: series.dropna().iloc[-1])
total_returns = (last_prices / first_prices - 1) * 100
best_ticker = total_returns.idxmax()
worst_ticker = total_returns.idxmin()

st.caption(
    f"Selected period: {start_date:%b %d, %Y} – {end_date:%b %d, %Y} "
    f"· Latest available close: {latest_date_label} "
    f"· Companies: {selected_company_labels}"
)

metric_columns = st.columns(3)
metric_columns[0].metric(
    "Top performer",
    f"{COMPANIES[best_ticker]} ({best_ticker})",
    f"{total_returns[best_ticker]:+.1f}% in period",
    delta_color="off",
)
metric_columns[1].metric(
    "Lowest performer",
    f"{COMPANIES[worst_ticker]} ({worst_ticker})",
    f"{total_returns[worst_ticker]:+.1f}% in period",
    delta_color="off",
)
mean_volatility = frames["volatility"].apply(
    lambda series: series.dropna().iloc[-1] if series.notna().any() else float("nan")
).dropna()
if not mean_volatility.empty:
    least_volatile = mean_volatility.idxmin()
    most_volatile = mean_volatility.idxmax()
    metric_columns[2].metric(
        "Lowest current 30-day volatility",
        f"{COMPANIES[least_volatile]} ({least_volatile})",
        f"{mean_volatility[least_volatile]:.1f}% annualized",
    )
else:
    most_volatile = None
    metric_columns[2].metric("30-day volatility", "Not available yet")

st.subheader("Comparison visualizations")
st.caption(
    "Adjusted close prices account for splits and dividends. The indexed chart starts "
    "each company at 100; returns and volatility are percentages; volume is in millions of shares."
)

chart_columns = st.columns(2)
with chart_columns[0]:
    st.plotly_chart(
        _line_chart(
            frames["indexed"],
            "Indexed performance (period start = 100)",
            "Indexed value",
        ),
        width="stretch",
    )
with chart_columns[1]:
    st.plotly_chart(
        _line_chart(frames["close"], "Adjusted closing price (USD)", "Price (USD)"),
        width="stretch",
    )
with chart_columns[0]:
    st.plotly_chart(_distribution_chart(frames["returns"]), width="stretch")
with chart_columns[1]:
    st.plotly_chart(
        _line_chart(
            frames["volume"],
            "Daily trading volume (million shares)",
            "Volume (million shares)",
        ),
        width="stretch",
    )
with chart_columns[0]:
    st.plotly_chart(
        _line_chart(
            frames["volatility"],
            "Rolling 30-session annualized volatility",
            "Volatility (%)",
            percent_axis=True,
        ),
        width="stretch",
    )
with chart_columns[1]:
    st.plotly_chart(
        _line_chart(
            frames["drawdown"],
            "Drawdown from each period peak",
            "Drawdown (%)",
            percent_axis=True,
        ),
        width="stretch",
    )

st.subheader("What stands out")
best_company = COMPANIES[best_ticker]
worst_company = COMPANIES[worst_ticker]
worst_drawdown = frames["drawdown"].min()
deepest_drawdown_ticker = worst_drawdown.idxmin()
deepest_drawdown_value = worst_drawdown[deepest_drawdown_ticker]
volatility_observation = ""
if most_volatile is not None:
    volatility_observation = (
        f" At the end of the period, {COMPANIES[most_volatile]} ({most_volatile}) "
        f"had the highest rolling 30-session annualized volatility "
        f"({mean_volatility[most_volatile]:.1f}%)."
    )
st.markdown(
    f"""
    Over the selected period, **{best_company} ({best_ticker})** had the strongest
    adjusted-price return (**{total_returns[best_ticker]:+.1f}%**), while
    **{worst_company} ({worst_ticker})** had the weakest
    (**{total_returns[worst_ticker]:+.1f}%**). The indexed-performance chart makes
    these relative moves comparable despite different share prices. The daily-return
    distributions and rolling-volatility chart compare risk: {COMPANIES[deepest_drawdown_ticker]}
    ({deepest_drawdown_ticker}) had the deepest peak-to-trough drawdown
    (**{deepest_drawdown_value:.1f}%**).{volatility_observation} Volume is shown in
    millions of shares, so it represents trading activity rather than company size
    or dollar value.
    """
)

st.caption(
    "Source: Yahoo Finance via yfinance · Daily data may be delayed or revised. "
    "For educational purposes only; not investment advice."
)
st.markdown("**Noorulain Balouch** · **Developed for CPS*5745**")
