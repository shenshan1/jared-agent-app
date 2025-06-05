import streamlit as st
import yfinance as yf
import pandas_ta as ta
import plotly.graph_objects as go

# === PAGE CONFIG ===
st.set_page_config(page_title="Jared • AI Stock Scout", layout="wide")

# === SIDEBAR ===
with st.sidebar:
    st.title("🧠 Jared: AI Stock Scout")
    st.markdown("**Enter a ticker symbol** (stock, ETF, or BDC) to get insights.")
    st.markdown("Jared checks the **1H, Daily, and Weekly** charts for:")
    st.markdown("""
    - 🔄 Reversals
    - 📈 Trend Continuations
    - ✅ Buy Zones
    """)
    st.caption("Built with ❤️ for smart traders.")

# === MAIN TITLE ===
st.markdown("<h1 style='text-align: center; color: #00ffcc;'>Jared: Your Technical Analysis Companion</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #cccccc;'>Smart market moves powered by AI & TA</p>", unsafe_allow_html=True)

# === INPUT ===
ticker_input = st.text_input("🔍 Enter ticker (e.g. TSLA, PLTR, VTI, MAIN):", "PLTR")

# === TIMEFRAMES ===
timeframes = {
    "1 Hour": ("60m", "7d"),
    "Daily": ("1d", "6mo"),
    "Weekly": ("1wk", "2y")
}

# === FUNCTIONS ===
def fetch_data(ticker, interval, period):
    df = yf.download(ticker, interval=interval, period=period)
    df.dropna(inplace=True)
    return df

def analyze(df):
    df['EMA20'] = ta.ema(df['Close'], length=20)
    df['EMA50'] = ta.ema(df['Close'], length=50)
    df['RSI'] = ta.rsi(df['Close'], length=14)

    latest = df.iloc[-1]
    previous = df.iloc[-2]

    alerts = []

    # Reversals
    if previous['Close'] < previous['EMA50'] and latest['Close'] > latest['EMA50']:
        alerts.append("🟢 Reversal: Price crossed ABOVE EMA50")
    elif previous['Close'] > previous['EMA50'] and latest['Close'] < latest['EMA50']:
        alerts.append("🔴 Reversal: Price crossed BELOW EMA50")

    # Trend Check
    if latest['EMA20'] > latest['EMA50'] and latest['RSI'] > 50:
        alerts.append("📈 Uptrend: EMA20 > EMA50 and RSI > 50")
    elif latest['EMA20'] < latest['EMA50'] and latest['RSI'] < 50:
        alerts.append("📉 Downtrend: EMA20 < EMA50 and RSI < 50")

    # Buy Signal
    if latest['EMA20'] > latest['EMA50'] and latest['RSI'] < 45:
        alerts.append("✅ Potential BUY: RSI pullback in an uptrend")

    return alerts

def plot_chart(df, tf_label, ticker):
    fig = go.Figure()

    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
        name="Candles"))

    fig.add_trace(go.Scatter(x=df.index, y=df['EMA20'], line=dict(color='blue', width=1), name='EMA20'))
    fig.add_trace(go.Scatter(x=df.index, y=df['EMA50'], line=dict(color='orange', width=1), name='EMA50'))

    fig.update_layout(
        title=f"{ticker.upper()} - {tf_label}",
        xaxis_title="Date", yaxis_title="Price",
        template="plotly_dark", height=400, margin=dict(t=30, b=30)
    )
    return fig

# === ANALYSIS LOOP ===
if ticker_input:
    for tf_label, (interval, period) in timeframes.items():
        st.markdown(f"### ⏱️ {tf_label}")
        df = fetch_data(ticker_input, interval, period)
        if not df.empty:
            alerts = analyze(df)
            cols = st.columns(len(alerts) if alerts else 1)
            if alerts:
                for i, alert in enumerate(alerts):
                    with cols[i]:
                        st.success(alert)
            else:
                st.warning("No technical signal detected at this time.")

            fig = plot_chart(df, tf_label, ticker_input)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.error("⚠️ No data found for this timeframe.")

st.markdown("---")
st.markdown("<p style='text-align: center; color: #888;'>Jared is not financial advice. Do your own research. 🚀</p>", unsafe_allow_html=True)

