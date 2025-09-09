# app_sidebar.py — Sidebar Question Flow
import streamlit as st

st.set_page_config(page_title="Ask with Sidebar", layout="wide")

# -----------------------------
# State
# -----------------------------
def _init_state():
    st.session_state.setdefault("question", "")
    st.session_state.setdefault("answer", "")
    st.session_state.setdefault("suggestions", [])
    st.session_state.setdefault("pending_question", None)

_init_state()

# -----------------------------
# Mock AI Answer
# -----------------------------
def ask_ai(q: str):
    sug = [
        "Show trend for the last 30 days",
        "Split by member vs non-member",
        "Top/bottom 5 branches by proportion",
    ]
    return f"✨ AI Answer for:\n{q}", sug

def rerun_with(q: str):
    st.session_state.pending_question = q
    st.rerun()

def run_question(q: str):
    ans, sug = ask_ai(q)
    st.session_state.question = q
    st.session_state.answer = ans
    st.session_state.suggestions = sug

# -----------------------------
# Sidebar
# -----------------------------
with st.sidebar:
    st.header("Ask a Question")
    q = st.text_area("Your question", value=st.session_state.get("question") or "", height=100)

    if st.button("Ask"):
        rerun_with(q)

    st.markdown("**Suggested Questions**")
    for sug in [
        "Show number and proportion of customers by days since last visit",
        "Sales trend by product",
        "Member vs non-member strike rate",
    ]:
        if st.button(sug, key=f"sug-{sug}"):
            rerun_with(sug)

# -----------------------------
# Run if pending
# -----------------------------
if st.session_state.pending_question:
    run_question(st.session_state.pending_question)
    st.session_state.pending_question = None

# -----------------------------
# Main Area: Answer + Refine
# -----------------------------
st.title("AI Business Assistant")
if st.session_state.answer:
    st.subheader("Answer")
    st.write(st.session_state.answer)

    st.subheader("Refine")
    try:
        pop = st.popover("Refine…")
        container = pop
    except Exception:
        container = st.expander("Refine…")

    with container:
        st.caption("Choose refinement:")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("by branch"):
                rerun_with(f"{q} by branch")
        with c2:
            if st.button("by product"):
                rerun_with(f"{q} by product")

    st.subheader("Suggested Next Questions")
    for sug in st.session_state.suggestions:
        if st.button(sug, key=f"next-{sug}"):
            rerun_with(sug)