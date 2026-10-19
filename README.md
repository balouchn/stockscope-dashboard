# StockScope — public company comparison dashboard

An interactive Python dashboard built with Streamlit and Plotly. It compares Apple,
Microsoft, NVIDIA, Alphabet, and Amazon using daily adjusted prices and trading
volume from Yahoo Finance (through `yfinance`). Apple, Microsoft, and NVIDIA are
selected by default.

Prepared by **Noorulain Balouch** · **Developed for CPS*5745**

## Dashboard features

- One shared company filter and date-range filter for every chart.
- Six clearly labeled comparisons:
  1. Indexed performance (each company starts at 100).
  2. Adjusted closing price in U.S. dollars.
  3. Daily return distribution in percent.
  4. Daily trading volume in millions of shares.
  5. Rolling 30-session annualized volatility in percent.
  6. Drawdown from the selected-period peak in percent.
- Summary indicators, a period-specific interpretation, latest available data date,
  full author attribution, and the required “Developed for CPS*5745” statement.
- Hourly caching and visible per-company data-source errors.
- Burgundy, wine, off-white, and blush theme with clear contrast in controls and charts.

## Screenshots

The `screenshots` folder contains readable captures of the dashboard with its
default company selection, date range, author name, six visualizations, and
interpretation.

## Run locally

1. Install Python 3.10 or newer.
2. Open a terminal in this project folder.
3. (Recommended) Create and activate a virtual environment:

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

4. Install the dependencies in `requirements.txt`:

   ```powershell
   python -m pip install -r requirements.txt
   ```

5. Start the dashboard:

   ```powershell
   python -m streamlit run app.py
   ```

6. Open the local URL printed in the terminal, usually
   `http://localhost:8501`. Internet access is needed to retrieve market data.

## Test

Run the calculation tests:

```powershell
python -m unittest discover -s tests -v
```

For a browser smoke test, start the app with `python -m streamlit run app.py`,
then open `http://localhost:8501`. Confirm all six charts render, the company/date
filters update the charts, the selected range and latest close date are shown,
and Noorulain Balouch and the course statement are visible.

## Deploy to Streamlit Community Cloud

Streamlit Community Cloud deploys from a GitHub repository. The dashboard is not
publicly deployed by this project setup alone; complete these steps to publish it:

1. Create a GitHub account if you do not already have one.
2. Create a **public** GitHub repository (for example, `stockscope-dashboard`).
3. Upload `app.py`, `market_data.py`, `requirements.txt`, `README.md`, the
   `.streamlit` folder, and the `tests` folder to the repository's root. Include
   `screenshots` if you want the captures stored alongside the app. You can use GitHub's
   **Add file → Upload files** option in your browser, or use Git to push this
   folder from your computer.
4. Sign in to [Streamlit Community Cloud](https://share.streamlit.io/) using the
   GitHub account that can access that repository. Authorize access if prompted.
5. Choose **Create app**, select the repository, branch, and `app.py` as the main
   file path, then choose **Deploy**.
6. In the app settings, verify that the app's visibility is **Public**. Do not add
   secrets; this app does not require API keys.
7. Wait for the build to finish. Open the generated `*.streamlit.app` link in a
   private/incognito browser window where you are not signed in. The dashboard
   should load without asking viewers to authenticate. If it does not, check the
   build log in Community Cloud and confirm the repository and app visibility.
8. Copy the working public URL and submit it together with readable screenshots
   showing the charts, your name, and selected company/date filters.

The app uses Yahoo Finance data via `yfinance`, which does not require an API key.
As with any external data source, availability and the latest trading date depend
on Yahoo Finance.
