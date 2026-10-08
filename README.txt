TRADING JOURNAL PRO — FRESH LAPTOP SETUP

1. Install Python 3.12 from python.org and tick "Add Python to PATH".
2. Install VS Code from code.visualstudio.com.
3. In VS Code install the Python extension by Microsoft.
4. Extract this folder to Documents\TradingJournal.
5. Open the folder in VS Code.
6. Open Terminal > New Terminal.
7. Run:
   python -m pip install -r requirements.txt
8. Run:
   streamlit run app.py

The app creates trading_journal.db automatically.

Included:
Dashboard, trade entry, history, analytics, calendar, trader journal,
screenshots, CSV export, SQLite backup, and read-only MT5 candle/account
integration.

IMPORTANT: MT5 integration is deliberately read-only at this stage. It does
not include an order-placement function.
