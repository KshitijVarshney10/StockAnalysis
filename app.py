"""
app.py — MarketMind: AI-powered equity research terminal.
Run with:  streamlit run app.py
Requires:  OPENROUTER_API_KEY in .env file
"""

import os
import json
import re
import logging
import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv

from tool_schemas import TOOL_SCHEMAS
from analytics import analytics

# ── Logging setup ──────────────────────────────────────────────────────────

logging.basicConfig(
    filename='marketmind.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def log(msg):
    logging.info(msg)

# ── Load env & init OpenRouter client ───────────────────────────────────────

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
MODEL = os.getenv("OPENROUTER_MODEL", "openai/gpt-3.5-turbo")

# Validate API key
if not OPENROUTER_API_KEY:
    st.error("❌ OPENROUTER_API_KEY missing in .env. Please set it and restart.")
    st.stop()

client = OpenAI(
    api_key=OPENROUTER_API_KEY,
    base_url="https://openrouter.ai/api/v1",
)

# ── Tool dispatch table ──────────────────────────────────────────────────────

TOOLS = {
    "fetch_price": analytics.fetch_price,
    "sma": analytics.sma,
    "ema": analytics.ema,
    "rsi": analytics.rsi,
    "macd": analytics.macd,
    "price_chart": analytics.price_chart,
    "volatility_chart": analytics.volatility_chart,
    "daily_volatility": analytics.daily_volatility,
    "relative_vol": analytics.relative_vol,
    "sharpe": analytics.sharpe,
    "beta": analytics.beta,
    "var": analytics.var,
    "max_drawdown": analytics.max_drawdown,
    "annualized_return": analytics.annualized_return,
    "information_ratio": analytics.information_ratio,
    "rolling_corr": analytics.rolling_corr,
    "omega_ratio": analytics.omega_ratio,
    "r_squared": analytics.r_squared,
    "relative_return": analytics.relative_return,
    "compare_performance": analytics.compare_performance,
    "compare_risk": analytics.compare_risk,
    "compare_volatility": analytics.compare_volatility,
    "compare_relative_volatility": analytics.compare_relative_volatility,
    "compare_rolling_volatility": analytics.compare_rolling_volatility,
}

TOOL_LIST = [{"type": "function", "function": s} for s in TOOL_SCHEMAS]

CHART_OUTPUTS = {
    "price_chart": "price_chart.png",
    "volatility_chart": "volatility_chart.png",
}

COMPARISON_KEYWORDS = {
    "compare", "versus", "vs", "between", "riskier", "better", "superior",
    "comparison", "compared", "more volatile", "outperform",
}

# ── Page config ──────────────────────────────────────────────────────────────

st.set_page_config(page_title="MarketMind", page_icon="📈", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@300;400;600&display=swap');
html, body, [class*="css"] { font-family: 'IBM Plex Sans', sans-serif; background-color: #0d1117; color: #c9d1d9; }
h1, h2, h3 { font-family: 'IBM Plex Mono', monospace; color: #58a6ff; letter-spacing: -0.5px; }
.stTextInput > div > div > input { background-color: #161b22; border: 1px solid #30363d; color: #e6edf3; font-family: 'IBM Plex Mono', monospace; border-radius: 6px; padding: 10px 14px; }
.stTextInput > div > div > input:focus { border-color: #58a6ff; box-shadow: 0 0 0 2px rgba(88,166,255,0.2); }
.stButton button { background-color: #21262d; color: #58a6ff; border: 1px solid #30363d; font-family: 'IBM Plex Mono', monospace; border-radius: 6px; padding: 6px 18px; transition: all 0.15s; }
.stButton button:hover { background-color: #30363d; border-color: #58a6ff; }
.response-box { background: #161b22; border: 1px solid #21262d; border-left: 3px solid #58a6ff; border-radius: 6px; padding: 14px 18px; font-family: 'IBM Plex Mono', monospace; font-size: 0.88rem; margin-bottom: 12px; white-space: pre-wrap; }
.user-bubble { background: #1c2128; border: 1px solid #30363d; border-radius: 6px; padding: 10px 16px; margin-bottom: 8px; font-size: 0.9rem; color: #8b949e; }
.section-label { font-family: 'IBM Plex Mono', monospace; font-size: 0.72rem; color: #484f58; text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 4px; }
.divider { border: none; border-top: 1px solid #21262d; margin: 18px 0; }
.debug-box { background: #1a1a2e; border: 1px solid #f78166; border-radius: 6px; padding: 10px 14px; font-family: 'IBM Plex Mono', monospace; font-size: 0.78rem; color: #f78166; margin-bottom: 8px; white-space: pre-wrap; }
</style>
""", unsafe_allow_html=True)

# ── Session state ────────────────────────────────────────────────────────────

if "history" not in st.session_state:
    st.session_state.history = []
if "pending_chart" not in st.session_state:
    st.session_state.pending_chart = None
if "rate_limit" not in st.session_state:
    st.session_state.rate_limit = 0

# ── Sidebar ──────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("### ⚙️ Config")
    
    # Show API key status
    if OPENROUTER_API_KEY:
        st.success("✅ API key loaded")
    else:
        st.error("❌ OPENROUTER_API_KEY missing in .env")
    
    st.markdown(f"**Model:** `{MODEL}`")
    st.markdown("---")

    st.markdown("### Capabilities")
    caps = [
        ("📊", "Price & Charts", "fetch_price · price_chart"),
        ("〰️", "Moving Averages", "sma · ema"),
        ("⚡", "Momentum", "rsi · macd"),
        ("📉", "Risk", "var · max_drawdown · sharpe"),
        ("🔗", "Correlation", "beta · rolling_corr · r_squared"),
        ("⚖️", "Comparison", "compare_performance · compare_risk"),
        ("🌀", "Volatility", "daily_vol · rolling_vol · omega"),
    ]
    for icon, label, fns in caps:
        st.markdown(
            f"**{icon} {label}**  \n"
            f"<span style='font-family:monospace;font-size:0.75rem;color:#484f58;'>{fns}</span>",
            unsafe_allow_html=True,
        )
        st.markdown("---")

    if st.button("🗑 Clear history"):
        st.session_state.history = []
        st.session_state.pending_chart = None
        st.session_state.rate_limit = 0
        st.rerun()

# ── Layout ───────────────────────────────────────────────────────────────────

col_left, col_main, col_right = st.columns([1, 3, 1])

with col_main:
    st.markdown("## 📈 MarketMind")
    st.markdown(
        "<p style='color:#8b949e;font-size:0.9rem;margin-top:-12px;'>"
        "AI equity research terminal · powered by OpenRouter + yfinance</p>",
        unsafe_allow_html=True,
    )
    st.markdown("<hr class='divider'>", unsafe_allow_html=True)

    # Conversation history
    if st.session_state.history:
        for entry in st.session_state.history:
            if isinstance(entry, dict):
                role = entry.get("role", "")
                content = entry.get("content", "") or ""
            else:
                role = getattr(entry, "role", "")
                content = getattr(entry, "content", "") or ""

            if role == "user" and content:
                st.markdown(
                    f"<div class='section-label'>You</div><div class='user-bubble'>{content}</div>",
                    unsafe_allow_html=True,
                )
            elif role == "assistant" and content:
                st.markdown(
                    f"<div class='section-label'>MarketMind</div><div class='response-box'>{content}</div>",
                    unsafe_allow_html=True,
                )

    # Show chart if one was generated in the last response
    if st.session_state.pending_chart and os.path.exists(st.session_state.pending_chart):
        st.image(st.session_state.pending_chart, use_container_width=True, caption="Stock Chart")

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)

    with st.form(key="query_form", clear_on_submit=True):
        query = st.text_input(
            "",
            placeholder="e.g.  What is AAPL price?  ·  RSI for TSLA  ·  Compare MSFT vs GOOG",
            label_visibility="collapsed",
        )
        submitted = st.form_submit_button("→ Analyze")

    qcols = st.columns(4)
    quick = ["Plot AAPL price", "RSI for NVDA", "Compare MSFT vs GOOG performance", "Max drawdown TSLA"]
    for i, qp in enumerate(quick):
        if qcols[i].button(qp, key=f"qp_{i}"):
            query = qp
            submitted = True

# ── Helper functions ─────────────────────────────────────────────────────────

def log(msg):
    logging.info(msg)


def is_comparison(text: str) -> bool:
    return any(kw in text.lower() for kw in COMPARISON_KEYWORDS)


def validate_query(query: str) -> str:
    if not query.strip():
        return "Query cannot be empty."
    if len(query) > 500:
        return "Query too long (max 500 characters)."
    # Basic check for ticker-like patterns
    if re.search(r'\b[A-Z]{1,5}\b', query.upper()):
        return None  # OK
    return "Please include a valid stock ticker (e.g., AAPL, TSLA)."


def split_requests(text: str):
    if is_comparison(text):
        return [text]
    return [r.strip() for r in re.split(r'\s*(?:then|after that|also|and|,|;|/)\s*', text) if r.strip()]


def history_to_dicts(history):
    result = []
    for entry in history:
        if isinstance(entry, dict):
            result.append(entry)
            continue

        d = {"role": entry.role, "content": entry.content or ""}

        if getattr(entry, "tool_calls", None):
            d["tool_calls"] = [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments,
                    },
                }
                for tc in entry.tool_calls
            ]

        if getattr(entry, "tool_call_id", None):
            d["tool_call_id"] = entry.tool_call_id
            if getattr(entry, "name", None):
                d["name"] = entry.name

        result.append(d)

    return result


def call_gpt(messages):
    try:
        return client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=TOOL_LIST,
            tool_choice="auto",
        )
    except Exception as e:
        log(f"API call failed: {e}")
        raise Exception(f"Failed to call AI model: {str(e)}")


def call_gpt_plain(messages):
    try:
        return client.chat.completions.create(
            model=MODEL,
            messages=messages,
        )
    except Exception as e:
        log(f"Plain API call failed: {e}")
        raise Exception(f"Failed to call AI model: {str(e)}")


def run_tool(name: str, args: dict):
    try:
        # Basic validation
        if name not in TOOLS:
            return f"Unknown tool: {name}"
        # Validate args based on tool
        if name == "fetch_price":
            if not isinstance(args.get("ticker"), str) or not args["ticker"]:
                return "Invalid ticker."
            if args.get("on_date") and not re.match(r'\d{4}-\d{2}-\d{2}', args["on_date"]):
                return "Invalid date format (use YYYY-MM-DD)."
        # Add more validations as needed
        fn = TOOLS[name]
        return fn(**args)
    except Exception as e:
        log(f"Tool execution failed: {name} with {args} - {e}")
        return f"Error executing {name}: {str(e)}"


# ── Main processing loop ─────────────────────────────────────────────────────

if submitted and query:
    # Validate query
    validation_error = validate_query(query)
    if validation_error:
        st.error(validation_error)
        st.stop()

    # Rate limiting: max 10 calls per session
    if st.session_state.rate_limit >= 10:
        st.error("Rate limit exceeded. Please clear history to reset.")
        st.stop()
    st.session_state.rate_limit += 1

    requests_list = split_requests(query)
    log(f"Query: {query}")
    log(f"Split into {len(requests_list)} request(s): {requests_list}")

    with col_main:
        with st.spinner("Analyzing…"):
            for req in requests_list:
                st.session_state.history.append({"role": "user", "content": req})

                # Limit history to last 50 messages for scalability
                if len(st.session_state.history) > 50:
                    st.session_state.history = st.session_state.history[-50:]

                try:
                    log(f"Calling model: {MODEL}")
                    msgs = history_to_dicts(st.session_state.history)
                    log(f"Sending {len(msgs)} messages to API")

                    response = call_gpt(msgs)
                    msg = response.choices[0].message
                    finish_reason = response.choices[0].finish_reason

                    log(f"finish_reason: {finish_reason}")
                    log(f"msg.content: {msg.content}")
                    log(f"msg.tool_calls: {msg.tool_calls}")

                    tool_calls = getattr(msg, "tool_calls", None)

                    if tool_calls:
                        tool_call = tool_calls[0]
                        tool_name = tool_call.function.name
                        tool_args = json.loads(tool_call.function.arguments)

                        log(f"Tool called: {tool_name}({tool_args})")

                        tool_result = run_tool(tool_name, tool_args)
                        log(f"Tool result: {str(tool_result)[:200]}")

                        st.session_state.history.append(msg)
                        st.session_state.history.append({
                            "role": "tool",
                            "name": tool_name,
                            "tool_call_id": tool_call.id,
                            "content": str(tool_result),
                        })

                        followup = call_gpt_plain(history_to_dicts(st.session_state.history))
                        final_content = followup.choices[0].message.content or ""
                        log(f"Final response: {final_content[:200]}")

                        if final_content:
                            st.session_state.history.append({"role": "assistant", "content": final_content})

                        if tool_name in CHART_OUTPUTS:
                            chart_path = CHART_OUTPUTS[tool_name]
                            log(f"Chart path: {chart_path} | exists: {os.path.exists(chart_path)}")
                            if os.path.exists(chart_path):
                                st.session_state.pending_chart = chart_path

                    else:
                        content = msg.content or ""
                        log(f"No tool call. Plain response: {content[:200]}")
                        if content:
                            st.session_state.history.append({"role": "assistant", "content": content})

                except Exception as e:
                    log(f"EXCEPTION: {type(e).__name__}: {e}")
                    st.error(f"Error processing request: {str(e)}")

    st.rerun()
