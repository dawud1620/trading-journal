import streamlit as st
import pandas as pd
from datetime import datetime, date
import io
import base64

from supabase import create_client, Client


# ============================================================
# OPTIONAL MT5
# ============================================================

try:
    import MetaTrader5 as mt5
    MT5_AVAILABLE = True
except ImportError:
    MT5_AVAILABLE = False


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Trading Journal",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# BRIGHT DARK UI
# ============================================================

st.markdown(
    """
    <style>

    .stApp {
        background-color: #0b0f14;
        color: #f5f7fa;
    }

    section[data-testid="stSidebar"] {
        background-color: #10161f;
        border-right: 1px solid #293241;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1500px;
    }

    /* ALL NORMAL TEXT */
    p,
    label,
    span,
    div,
    .stMarkdown,
    .stText {
        color: #f1f5f9;
    }

    /* INPUT LABELS */
    label,
    [data-testid="stWidgetLabel"],
    [data-testid="stWidgetLabel"] p {
        color: #f1f5f9 !important;
        font-weight: 600 !important;
    }

    /* INPUT BOXES */
    input,
    textarea {
        color: #111827 !important;
        background-color: #ffffff !important;
    }

    /* SELECTBOX */
    div[data-baseweb="select"] {
        color: #111827 !important;
    }

    /* METRICS */
    div[data-testid="stMetric"] {
        background-color: #141b24;
        border: 1px solid #293241;
        padding: 18px;
        border-radius: 12px;
    }

    div[data-testid="stMetricLabel"] {
        color: #cbd5e1 !important;
    }

    div[data-testid="stMetricValue"] {
        color: #ffffff !important;
    }

    /* SIDEBAR TEXT */
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] span {
        color: #f1f5f9 !important;
    }

    /* HEADINGS */
    h1, h2, h3, h4 {
        color: #ffffff !important;
    }

    /* CAPTIONS */
    .stCaption,
    [data-testid="stCaptionContainer"] {
        color: #cbd5e1 !important;
    }

    /* TABLE */
    [data-testid="stDataFrame"] {
        border: 1px solid #293241;
        border-radius: 10px;
    }

    /* SIDEBAR BRAND */
    .brand {
        font-size: 25px;
        font-weight: 800;
        letter-spacing: 1px;
        color: #ffffff !important;
        margin-bottom: 4px;
    }

    .brand-sub {
        color: #cbd5e1 !important;
        font-size: 12px;
        margin-bottom: 20px;
    }

    footer {
        visibility: hidden;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# SUPABASE
# ============================================================

SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

supabase: Client = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)


# ============================================================
# SESSION
# ============================================================

def clear_session():

    for key in [
        "user_id",
        "access_token",
        "refresh_token",
        "user_email",
    ]:
        st.session_state.pop(
            key,
            None
        )


def save_session(session, user):

    st.session_state["user_id"] = str(
        user.id
    )

    st.session_state["access_token"] = (
        session.access_token
    )

    st.session_state["refresh_token"] = (
        session.refresh_token
    )

    st.session_state["user_email"] = (
        user.email
    )


def restore_session():

    access_token = st.session_state.get(
        "access_token"
    )

    refresh_token = st.session_state.get(
        "refresh_token"
    )

    if not access_token or not refresh_token:
        return False

    try:

        response = supabase.auth.set_session(
            access_token,
            refresh_token
        )

        if response and response.user:

            st.session_state["user_id"] = str(
                response.user.id
            )

            st.session_state["user_email"] = (
                response.user.email
            )

            return True

    except Exception:
        clear_session()

    return False


def login_user(email, password):

    try:

        response = (
            supabase
            .auth
            .sign_in_with_password(
                {
                    "email": email,
                    "password": password,
                }
            )
        )

        if response.session and response.user:

            save_session(
                response.session,
                response.user
            )

            return True, "Login successful."

        return False, "Login failed."

    except Exception as e:

        return False, str(e)


def signup_user(email, password):

    try:

        response = (
            supabase
            .auth
            .sign_up(
                {
                    "email": email,
                    "password": password,
                }
            )
        )

        if not response.user:

            return False, "Could not create account."

        if response.session:

            save_session(
                response.session,
                response.user
            )

            return True, "Account created successfully."

        return (
            True,
            "Account created. Check your email to confirm your account."
        )

    except Exception as e:

        return False, str(e)


# ============================================================
# LOGIN SCREEN
# ============================================================

if "user_id" not in st.session_state:

    st.title("📈 Trading Journal")

    st.caption(
        "Your private cloud trading workspace"
    )

    login_tab, signup_tab = st.tabs(
        [
            "🔐 Login",
            "🆕 Create Account"
        ]
    )

    with login_tab:

        st.subheader("Welcome back")

        email = st.text_input(
            "Email",
            key="login_email"
        )

        password = st.text_input(
            "Password",
            type="password",
            key="login_password"
        )

        if st.button(
            "Login",
            type="primary",
            use_container_width=True
        ):

            if not email or not password:

                st.error(
                    "Enter your email and password."
                )

            else:

                success, message = login_user(
                    email,
                    password
                )

                if success:

                    st.success(message)

                    st.rerun()

                else:

                    st.error(message)

    with signup_tab:

        st.subheader("Create your account")

        new_email = st.text_input(
            "Email",
            key="signup_email"
        )

        new_password = st.text_input(
            "Password",
            type="password",
            key="signup_password"
        )

        confirm_password = st.text_input(
            "Confirm password",
            type="password",
            key="signup_confirm_password"
        )

        if st.button(
            "Create Account",
            type="primary",
            use_container_width=True
        ):

            if not new_email or not new_password:

                st.error(
                    "Enter your email and password."
                )

            elif len(new_password) < 6:

                st.error(
                    "Password must be at least 6 characters."
                )

            elif new_password != confirm_password:

                st.error(
                    "Passwords do not match."
                )

            else:

                success, message = signup_user(
                    new_email,
                    new_password
                )

                if success:

                    st.success(message)

                    if "user_id" in st.session_state:
                        st.rerun()

                else:

                    st.error(message)

    st.stop()


# ============================================================
# RESTORE AUTH SESSION
# ============================================================

if not restore_session():

    st.warning(
        "Your session expired. Please log in again."
    )

    clear_session()

    st.rerun()


USER_ID = st.session_state["user_id"]


# ============================================================
# SETTINGS
# ============================================================

def get_settings():

    try:

        response = (
            supabase
            .table("settings")
            .select("*")
            .eq("user_id", USER_ID)
            .limit(1)
            .execute()
        )

        if response.data:

            return response.data[0]

        new_settings = {
            "user_id": USER_ID,
            "starting_balance": 5000.0,
            "currency": "$",
            "default_risk": 0.5,
        }

        inserted = (
            supabase
            .table("settings")
            .insert(new_settings)
            .execute()
        )

        if inserted.data:
            return inserted.data[0]

        return new_settings

    except Exception as e:

        st.error(
            f"Settings error: {e}"
        )

        return {
            "starting_balance": 5000.0,
            "currency": "$",
            "default_risk": 0.5,
        }


def save_settings(
    starting_balance,
    currency,
    default_risk
):

    existing = (
        supabase
        .table("settings")
        .select("id")
        .eq("user_id", USER_ID)
        .limit(1)
        .execute()
    )

    data = {
        "starting_balance": float(
            starting_balance
        ),
        "currency": currency,
        "default_risk": float(
            default_risk
        ),
    }

    if existing.data:

        (
            supabase
            .table("settings")
            .update(data)
            .eq("user_id", USER_ID)
            .execute()
        )

    else:

        data["user_id"] = USER_ID

        (
            supabase
            .table("settings")
            .insert(data)
            .execute()
        )


settings = get_settings()

STARTING_BALANCE = float(
    settings.get(
        "starting_balance",
        5000
    )
)

CURRENCY = settings.get(
    "currency",
    "$"
)

DEFAULT_RISK = float(
    settings.get(
        "default_risk",
        0.5
    )
)


# ============================================================
# TRADE DATABASE
# ============================================================

def load_trades():

    try:

        response = (
            supabase
            .table("trades")
            .select("*")
            .eq("user_id", USER_ID)
            .order("id", desc=True)
            .execute()
        )

        data = response.data or []

        df = pd.DataFrame(data)

        if df.empty:
            return df

        if "trade_date" in df.columns:

            df["trade_date"] = pd.to_datetime(
                df["trade_date"],
                errors="coerce"
            )

        numeric_columns = [
            "entry",
            "stop_loss",
            "take_profit",
            "risk_percent",
            "lot_size",
            "pnl",
            "r_multiple",
        ]

        for column in numeric_columns:

            if column in df.columns:

                df[column] = pd.to_numeric(
                    df[column],
                    errors="coerce"
                )

        return df

    except Exception as e:

        st.error(
            f"Could not load trades: {e}"
        )

        return pd.DataFrame()


def add_trade(data):

    data["user_id"] = USER_ID

    response = (
        supabase
        .table("trades")
        .insert(data)
        .execute()
    )

    return response


# ============================================================
# JOURNAL DATABASE
# ============================================================

def load_journal():

    try:

        response = (
            supabase
            .table("journal")
            .select("*")
            .eq("user_id", USER_ID)
            .order("id", desc=True)
            .execute()
        )

        data = response.data or []

        df = pd.DataFrame(data)

        if not df.empty:

            if "journal_date" in df.columns:

                df["journal_date"] = pd.to_datetime(
                    df["journal_date"],
                    errors="coerce"
                )

            if "discipline" in df.columns:

                df["discipline"] = pd.to_numeric(
                    df["discipline"],
                    errors="coerce"
                )

        return df

    except Exception as e:

        st.error(
            f"Could not load journal: {e}"
        )

        return pd.DataFrame()


def add_journal(data):

    data["user_id"] = USER_ID

    response = (
        supabase
        .table("journal")
        .insert(data)
        .execute()
    )

    return response


# ============================================================
# SCREENSHOT
# ============================================================

def encode_screenshot(uploaded_file):

    if uploaded_file is None:
        return None

    raw = uploaded_file.getvalue()

    if not raw:
        return None

    return base64.b64encode(
        raw
    ).decode("ascii")


def decode_screenshot(value):

    if not value:
        return None

    try:

        return io.BytesIO(
            base64.b64decode(value)
        )

    except Exception:

        return None


# ============================================================
# LOAD DATA
# ============================================================

trades = load_trades()
journal = load_journal()


# ============================================================
# CALCULATIONS
# ============================================================

def money(value):

    try:

        return (
            f"{CURRENCY}"
            f"{float(value):,.2f}"
        )

    except Exception:

        return f"{CURRENCY}0.00"


def calculate_metrics(df):

    if df.empty:

        return {
            "total_pnl": 0.0,
            "win_rate": 0.0,
            "profit_factor": 0.0,
            "max_drawdown": 0.0,
            "wins": 0,
            "losses": 0,
            "breakeven": 0,
        }

    pnl = pd.to_numeric(
        df["pnl"],
        errors="coerce"
    ).fillna(0)

    total_pnl = float(
        pnl.sum()
    )

    wins = int(
        (pnl > 0).sum()
    )

    losses = int(
        (pnl < 0).sum()
    )

    breakeven = int(
        (pnl == 0).sum()
    )

    decided = wins + losses

    win_rate = (
        wins / decided * 100
        if decided > 0
        else 0
    )

    gross_profit = float(
        pnl[pnl > 0].sum()
    )

    gross_loss = abs(
        float(
            pnl[pnl < 0].sum()
        )
    )

    profit_factor = (
        gross_profit / gross_loss
        if gross_loss > 0
        else 0
    )

    equity = (
        STARTING_BALANCE
        + pnl.cumsum()
    )

    peak = equity.cummax()

    drawdown = equity - peak

    max_drawdown = abs(
        float(drawdown.min())
    )

    return {
        "total_pnl": total_pnl,
        "win_rate": win_rate,
        "profit_factor": profit_factor,
        "max_drawdown": max_drawdown,
        "wins": wins,
        "losses": losses,
        "breakeven": breakeven,
    }


metrics = calculate_metrics(
    trades
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown(
        """
        <div class="brand">
            📈 TRADING JOURNAL
        </div>

        <div class="brand-sub">
            PRIVATE CLOUD WORKSPACE
        </div>
        """,
        unsafe_allow_html=True
    )

    st.write(
        st.session_state.get(
            "user_email",
            ""
        )
    )

    st.divider()

    page = st.radio(
        "Navigation",
        [
            "🏠 Dashboard",
            "➕ Add Trade",
            "📋 Trade History",
            "📊 Analytics",
            "📅 Calendar",
            "🧠 Trader Journal",
            "🔌 MT5",
            "💾 Backup",
            "⚙️ Settings",
        ]
    )

    st.divider()

    if st.button(
        "🚪 Sign out",
        use_container_width=True
    ):

        try:
            supabase.auth.sign_out()
        except Exception:
            pass

        clear_session()

        st.rerun()


# ============================================================
# DASHBOARD
# ============================================================

if page == "🏠 Dashboard":

    st.title("Dashboard")

    st.caption(
        "Your trading performance at a glance."
    )

    c1, c2, c3, c4, c5 = st.columns(5)

    with c1:

        st.metric(
            "Balance",
            money(
                STARTING_BALANCE
                + metrics["total_pnl"]
            )
        )

    with c2:

        st.metric(
            "Total P/L",
            money(
                metrics["total_pnl"]
            )
        )

    with c3:

        st.metric(
            "Win Rate",
            f"{metrics['win_rate']:.1f}%"
        )

    with c4:

        st.metric(
            "Profit Factor",
            (
                f"{metrics['profit_factor']:.2f}"
                if metrics["profit_factor"]
                else "—"
            )
        )

    with c5:

        st.metric(
            "Max Drawdown",
            money(
                metrics["max_drawdown"]
            )
        )

    st.divider()

    if not trades.empty:

        chart_df = trades.copy()

        chart_df = chart_df.sort_values(
            ["trade_date", "id"]
        )

        chart_df["equity"] = (
            STARTING_BALANCE
            + pd.to_numeric(
                chart_df["pnl"],
                errors="coerce"
            ).fillna(0).cumsum()
        )

        st.subheader(
            "Equity Curve"
        )

        st.line_chart(
            chart_df.set_index(
                "trade_date"
            )[["equity"]]
        )

    else:

        st.info(
            "No trades yet. Add your first trade."
        )

    st.subheader(
        "Recent Trades"
    )

    if not trades.empty:

        columns = [
            "trade_date",
            "pair",
            "direction",
            "session",
            "setup",
            "result",
            "pnl",
            "r_multiple",
        ]

        columns = [
            c
            for c in columns
            if c in trades.columns
        ]

        st.dataframe(
            trades[columns].head(10),
            use_container_width=True,
            hide_index=True
        )

    else:

        st.write(
            "No trades recorded yet."
        )


# ============================================================
# ADD TRADE
# ============================================================

elif page == "➕ Add Trade":

    st.title("Add Trade")

    st.caption(
        "Record the trade exactly as you executed it."
    )

    with st.form(
        "trade_form",
        clear_on_submit=True
    ):

        c1, c2, c3 = st.columns(3)

        with c1:

            trade_date = st.date_input(
                "Trade date",
                date.today()
            )

            pair = st.text_input(
                "Pair / Instrument",
                placeholder="XAUUSD"
            )

            direction = st.selectbox(
                "Direction",
                [
                    "Buy",
                    "Sell"
                ]
            )

            session = st.selectbox(
                "Session",
                [
                    "London",
                    "New York",
                    "London + New York",
                    "Asian",
                    "Other"
                ]
            )

        with c2:

            setup = st.text_input(
                "Setup",
                placeholder="Liquidity + BOS + POI"
            )

            result = st.selectbox(
                "Result",
                [
                    "Win",
                    "Loss",
                    "Breakeven"
                ]
            )

            risk_percent = st.number_input(
                "Risk %",
                min_value=0.0,
                max_value=100.0,
                value=DEFAULT_RISK,
                step=0.1
            )

            lot_size = st.number_input(
                "Lot size",
                min_value=0.0,
                value=0.0,
                step=0.01
            )

        with c3:

            pnl = st.number_input(
                "P/L",
                value=0.0,
                step=0.01
            )

            r_multiple = st.number_input(
                "R Multiple",
                value=0.0,
                step=0.1
            )

            entry = st.number_input(
                "Entry",
                value=0.0,
                step=0.00001,
                format="%.5f"
            )

            stop_loss = st.number_input(
                "Stop Loss",
                value=0.0,
                step=0.00001,
                format="%.5f"
            )

            take_profit = st.number_input(
                "Take Profit",
                value=0.0,
                step=0.00001,
                format="%.5f"
            )

        st.divider()

        entry_reason = st.text_area(
            "Why did you take the trade?"
        )

        mistakes = st.text_area(
            "Mistakes"
        )

        psychology = st.text_area(
            "Psychology"
        )

        lesson = st.text_area(
            "Lesson"
        )

        notes = st.text_area(
            "Additional notes"
        )

        screenshot = st.file_uploader(
            "Trade screenshot",
            type=[
                "png",
                "jpg",
                "jpeg",
                "webp"
            ]
        )

        submitted = st.form_submit_button(
            "💾 Save Trade",
            type="primary",
            use_container_width=True
        )

        if submitted:

            if not pair.strip():

                st.error(
                    "Enter a pair or instrument."
                )

            else:

                trade_data = {
                    "trade_date": trade_date.isoformat(),
                    "pair": pair.strip().upper(),
                    "direction": direction,
                    "session": session,
                    "setup": setup,
                    "entry": float(entry),
                    "stop_loss": float(stop_loss),
                    "take_profit": float(take_profit),
                    "risk_percent": float(risk_percent),
                    "lot_size": float(lot_size),
                    "result": result,
                    "pnl": float(pnl),
                    "r_multiple": float(r_multiple),
                    "entry_reason": entry_reason,
                    "mistakes": mistakes,
                    "psychology": psychology,
                    "lesson": lesson,
                    "notes": notes,
                    "screenshot": encode_screenshot(
                        screenshot
                    ),
                    "created_at": datetime.now().isoformat(),
                    "user_id": USER_ID,
                }

                try:

                    response = add_trade(
                        trade_data
                    )

                    if response.data:

                        st.success(
                            "✅ Trade saved to your cloud database."
                        )

                        st.rerun()

                    else:

                        st.warning(
                            "The database accepted the request but returned no row."
                        )

                except Exception as e:

                    st.error(
                        f"❌ Trade was not saved: {e}"
                    )


# ============================================================
# TRADE HISTORY
# ============================================================

elif page == "📋 Trade History":

    st.title("Trade History")

    if trades.empty:

        st.warning(
            "No trades are being returned from Supabase for this account."
        )

        st.caption(
            f"Logged-in user: {USER_ID}"
        )

    else:

        search = st.text_input(
            "🔎 Search pair or setup"
        )

        filtered = trades.copy()

        if search.strip():

            query = search.lower()

            filtered = filtered[
                filtered["pair"]
                .fillna("")
                .astype(str)
                .str.lower()
                .str.contains(
                    query,
                    na=False
                )
                |
                filtered["setup"]
                .fillna("")
                .astype(str)
                .str.lower()
                .str.contains(
                    query,
                    na=False
                )
            ]

        columns = [
            "id",
            "trade_date",
            "pair",
            "direction",
            "session",
            "setup",
            "result",
            "pnl",
            "r_multiple",
            "risk_percent",
        ]

        columns = [
            c
            for c in columns
            if c in filtered.columns
        ]

        st.dataframe(
            filtered[columns],
            use_container_width=True,
            hide_index=True
        )

        st.divider()

        st.subheader(
            "Inspect Trade"
        )

        selected_id = st.selectbox(
            "Select trade",
            filtered["id"].tolist()
        )

        selected = filtered[
            filtered["id"] == selected_id
        ].iloc[0]

        a, b, c = st.columns(3)

        with a:

            st.write(
                f"**Pair:** {selected.get('pair', '')}"
            )

            st.write(
                f"**Direction:** {selected.get('direction', '')}"
            )

            st.write(
                f"**Session:** {selected.get('session', '')}"
            )

        with b:

            st.write(
                f"**Result:** {selected.get('result', '')}"
            )

            st.write(
                f"**P/L:** {money(selected.get('pnl', 0))}"
            )

            st.write(
                f"**R:** {selected.get('r_multiple', 0)}"
            )

        with c:

            st.write(
                f"**Entry:** {selected.get('entry', 0)}"
            )

            st.write(
                f"**SL:** {selected.get('stop_loss', 0)}"
            )

            st.write(
                f"**TP:** {selected.get('take_profit', 0)}"
            )

        st.divider()

        st.write(
            "**Entry reason**"
        )

        st.write(
            selected.get(
                "entry_reason",
                ""
            )
        )

        st.write(
            "**Mistakes**"
        )

        st.write(
            selected.get(
                "mistakes",
                ""
            )
        )

        st.write(
            "**Psychology**"
        )

        st.write(
            selected.get(
                "psychology",
                ""
            )
        )

        st.write(
            "**Lesson**"
        )

        st.write(
            selected.get(
                "lesson",
                ""
            )
        )

        st.write(
            "**Notes**"
        )

        st.write(
            selected.get(
                "notes",
                ""
            )
        )

        screenshot = selected.get(
            "screenshot"
        )

        if screenshot:

            image = decode_screenshot(
                screenshot
            )

            if image:

                st.subheader(
                    "Trade Screenshot"
                )

                st.image(
                    image,
                    use_container_width=True
                )


# ============================================================
# ANALYTICS
# ============================================================

elif page == "📊 Analytics":

    st.title("Analytics")

    if trades.empty:

        st.info(
            "Add trades first."
        )

    else:

        tabs = st.tabs(
            [
                "Overview",
                "Pairs",
                "Sessions",
                "Setups",
            ]
        )

        with tabs[0]:

            chart_df = trades.copy()

            chart_df = chart_df.sort_values(
                ["trade_date", "id"]
            )

            chart_df["equity"] = (
                STARTING_BALANCE
                + pd.to_numeric(
                    chart_df["pnl"],
                    errors="coerce"
                ).fillna(0).cumsum()
            )

            st.subheader(
                "Equity Curve"
            )

            st.line_chart(
                chart_df.set_index(
                    "trade_date"
                )[["equity"]]
            )

            monthly = trades.copy()

            monthly["month"] = (
                pd.to_datetime(
                    monthly["trade_date"],
                    errors="coerce"
                )
                .dt.to_period("M")
                .astype(str)
            )

            monthly_stats = (
                monthly
                .groupby("month")["pnl"]
                .sum()
            )

            st.subheader(
                "Monthly P/L"
            )

            st.bar_chart(
                monthly_stats
            )

        with tabs[1]:

            pair_stats = (
                trades
                .groupby("pair")
                .agg(
                    Trades=("id", "count"),
                    PnL=("pnl", "sum"),
                    Average_R=("r_multiple", "mean")
                )
                .reset_index()
                .sort_values(
                    "PnL",
                    ascending=False
                )
            )

            st.dataframe(
                pair_stats,
                use_container_width=True,
                hide_index=True
            )

        with tabs[2]:

            session_stats = (
                trades
                .groupby("session")
                .agg(
                    Trades=("id", "count"),
                    PnL=("pnl", "sum"),
                    Average_R=("r_multiple", "mean")
                )
                .reset_index()
                .sort_values(
                    "PnL",
                    ascending=False
                )
            )

            st.dataframe(
                session_stats,
                use_container_width=True,
                hide_index=True
            )

        with tabs[3]:

            setup_stats = (
                trades
                .groupby("setup")
                .agg(
                    Trades=("id", "count"),
                    PnL=("pnl", "sum"),
                    Average_R=("r_multiple", "mean")
                )
                .reset_index()
                .sort_values(
                    "PnL",
                    ascending=False
                )
            )

            st.dataframe(
                setup_stats,
                use_container_width=True,
                hide_index=True
            )


# ============================================================
# CALENDAR
# ============================================================

elif page == "📅 Calendar":

    st.title("Trading Calendar")

    if trades.empty:

        st.info(
            "No trading days recorded yet."
        )

    else:

        calendar = trades.copy()

        calendar["trade_date"] = pd.to_datetime(
            calendar["trade_date"],
            errors="coerce"
        )

        daily = (
            calendar
            .groupby(
                calendar["trade_date"].dt.date
            )["pnl"]
            .sum()
            .reset_index()
        )

        daily.columns = [
            "Date",
            "P/L"
        ]

        daily["Status"] = daily["P/L"].apply(
            lambda x:
            "🟢 Profit"
            if x > 0
            else
            "🔴 Loss"
            if x < 0
            else
            "⚪ Breakeven"
        )

        st.dataframe(
            daily.sort_values(
                "Date",
                ascending=False
            ),
            use_container_width=True,
            hide_index=True
        )


# ============================================================
# TRADER JOURNAL
# ============================================================

elif page == "🧠 Trader Journal":

    st.title("Trader Journal")

    st.caption(
        "Record your plan, execution and psychology."
    )

    with st.form(
        "journal_form",
        clear_on_submit=True
    ):

        journal_date = st.date_input(
            "Journal date",
            date.today()
        )

        market_bias = st.text_area(
            "Market bias"
        )

        plan = st.text_area(
            "Trading plan"
        )

        execution = st.text_area(
            "Execution"
        )

        psychology = st.text_area(
            "Psychology"
        )

        discipline = st.slider(
            "Discipline score",
            1,
            10,
            10
        )

        what_went_well = st.text_area(
            "What went well?"
        )

        mistakes = st.text_area(
            "Mistakes"
        )

        lesson = st.text_area(
            "Lesson"
        )

        gratitude = st.text_area(
            "Gratitude"
        )

        submitted = st.form_submit_button(
            "💾 Save Journal Entry",
            type="primary",
            use_container_width=True
        )

        if submitted:

            data = {
                "journal_date": journal_date.isoformat(),
                "market_bias": market_bias,
                "plan": plan,
                "execution": execution,
                "psychology": psychology,
                "discipline": int(discipline),
                "what_went_well": what_went_well,
                "mistakes": mistakes,
                "lesson": lesson,
                "gratitude": gratitude,
                "created_at": datetime.now().isoformat(),
                "user_id": USER_ID,
            }

            try:

                response = add_journal(
                    data
                )

                if response.data:

                    st.success(
                        "Journal entry saved."
                    )

                    st.rerun()

                else:

                    st.warning(
                        "The database accepted the request but returned no row."
                    )

            except Exception as e:

                st.error(
                    f"Could not save journal entry: {e}"
                )

    st.divider()

    st.subheader(
        "Previous Entries"
    )

    if journal.empty:

        st.info(
            "No journal entries yet."
        )

    else:

        for _, entry in journal.iterrows():

            with st.expander(
                f"📅 {entry.get('journal_date', '')}"
            ):

                st.write(
                    "**Market bias**"
                )
                st.write(
                    entry.get(
                        "market_bias",
                        ""
                    )
                )

                st.write(
                    "**Plan**"
                )
                st.write(
                    entry.get(
                        "plan",
                        ""
                    )
                )

                st.write(
                    "**Execution**"
                )
                st.write(
                    entry.get(
                        "execution",
                        ""
                    )
                )

                st.write(
                    "**Psychology**"
                )
                st.write(
                    entry.get(
                        "psychology",
                        ""
                    )
                )

                st.write(
                    f"**Discipline:** "
                    f"{entry.get('discipline', '')}/10"
                )

                st.write(
                    "**What went well**"
                )
                st.write(
                    entry.get(
                        "what_went_well",
                        ""
                    )
                )

                st.write(
                    "**Mistakes**"
                )
                st.write(
                    entry.get(
                        "mistakes",
                        ""
                    )
                )

                st.write(
                    "**Lesson**"
                )
                st.write(
                    entry.get(
                        "lesson",
                        ""
                    )
                )

                st.write(
                    "**Gratitude**"
                )
                st.write(
                    entry.get(
                        "gratitude",
                        ""
                    )
                )


# ============================================================
# MT5
# ============================================================

elif page == "🔌 MT5":

    st.title("MetaTrader 5")

    st.caption(
        "Read-only MT5 connection."
    )

    st.warning(
        "MT5 works locally when this app is running on the same computer as the MT5 desktop terminal."
    )

    if not MT5_AVAILABLE:

        st.error(
            "MetaTrader5 package is not installed."
        )

    else:

        if st.button(
            "🔌 Connect to MT5",
            type="primary"
        ):

            try:

                if not mt5.initialize():

                    st.error(
                        f"MT5 initialization failed: {mt5.last_error()}"
                    )

                else:

                    account = mt5.account_info()

                    terminal = mt5.terminal_info()

                    st.success(
                        "Connected to MT5."
                    )

                    if account:

                        a, b, c = st.columns(3)

                        with a:

                            st.metric(
                                "Balance",
                                f"{account.balance:,.2f}"
                            )

                        with b:

                            st.metric(
                                "Equity",
                                f"{account.equity:,.2f}"
                            )

                        with c:

                            st.metric(
                                "Profit",
                                f"{account.profit:,.2f}"
                            )

                        st.write(
                            f"**Login:** {account.login}"
                        )

                        st.write(
                            f"**Server:** {account.server}"
                        )

                    if terminal:

                        st.write(
                            f"**Terminal:** {terminal.company}"
                        )

                        st.write(
                            f"**Path:** {terminal.path}"
                        )

            except Exception as e:

                st.error(
                    f"MT5 error: {e}"
                )


# ============================================================
# BACKUP
# ============================================================

elif page == "💾 Backup":

    st.title("Backup & Export")

    st.caption(
        "Download your cloud data whenever you want."
    )

    if not trades.empty:

        trade_csv = trades.to_csv(
            index=False
        ).encode("utf-8")

        st.download_button(
            "⬇️ Download Trades CSV",
            trade_csv,
            "trading_journal_trades.csv",
            "text/csv",
            use_container_width=True
        )

    else:

        st.info(
            "No trades to export."
        )

    if not journal.empty:

        journal_csv = journal.to_csv(
            index=False
        ).encode("utf-8")

        st.download_button(
            "⬇️ Download Journal CSV",
            journal_csv,
            "trading_journal_journal.csv",
            "text/csv",
            use_container_width=True
        )

    else:

        st.info(
            "No journal entries to export."
        )


# ============================================================
# SETTINGS PAGE
# ============================================================

elif page == "⚙️ Settings":

    st.title("Settings")

    st.caption(
        "Customize your trading journal."
    )

    with st.form(
        "settings_form"
    ):

        starting_balance = st.number_input(
            "Starting balance",
            min_value=0.0,
            value=float(
                STARTING_BALANCE
            ),
            step=100.0
        )

        currency = st.text_input(
            "Currency symbol",
            value=CURRENCY
        )

        default_risk = st.number_input(
            "Default risk %",
            min_value=0.0,
            max_value=100.0,
            value=float(
                DEFAULT_RISK
            ),
            step=0.1
        )

        submitted = st.form_submit_button(
            "💾 Save Settings",
            type="primary",
            use_container_width=True
        )

        if submitted:

            try:

                save_settings(
                    starting_balance,
                    currency,
                    default_risk
                )

                st.success(
                    "Settings saved."
                )

                st.rerun()

            except Exception as e:

                st.error(
                    f"Could not save settings: {e}"
                )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "Trading Journal • Supabase Cloud • Private user data • Read-only MT5"
)