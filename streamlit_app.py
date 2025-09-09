# app_drilldowns.py — Two Popovers for Drill-down (branch & product)
import streamlit as st

st.set_page_config(page_title="Ask with Drill-down Popovers", layout="wide")

# ========== State ==========
def _init_state():
    st.session_state.setdefault("question", "")
    st.session_state.setdefault("answer", "")
    st.session_state.setdefault("suggestions", [])
    st.session_state.setdefault("pending_question", None)
    st.session_state.setdefault("drilldown", None)  # {"type": "branch"|"product", "params": {...}}

_init_state()

# ========== Mock backends (replace with real AI / SQL) ==========
def ask_ai(q: str):
    # Return answer + suggestions without mutating question
    sug = [
        "Last 30 days trend",
        "Member vs non-member split",
        "Top/bottom 5 stores by proportion",
    ]
    return f"✨ AI Answer for:\n{q}\n(…table / charts…)", sug

def run_drilldown(drill_type: str, params: dict):
    # Replace this with real SQL or AI chain
    if drill_type == "branch":
        return f"🔎 Branch Drill-down\n- Branches: {', '.join(params.get('branches', []) or ['(all)'])}\n- Metric: {params.get('metric','proportion')}\n(…branch table / chart…)"
    else:
        return f"🔎 Product Drill-down\n- Scope: {params.get('scope','all products')}\n- Group: {params.get('group_by','category L2')}\n(…product table / chart…)"

def rerun_with(q: str):
    st.session_state.pending_question = q
    st.rerun()

def run_question(q: str):
    ans, sug = ask_ai(q)
    st.session_state.question = q
    st.session_state.answer = ans
    st.session_state.suggestions = sug

# ========== Sidebar (Question) ==========
with st.sidebar:
    st.header("Ask a Question")
    default_q = (
        "Show the number and proportion of customers by days since last visit "
        "(0–7, 8–14, 15–30, 31–45, >45 days)"
    )
    q = st.text_area("Your question", value=st.session_state.get("question") or default_q, height=100)
    if st.button("Ask"):
        rerun_with(q)

    st.markdown("**Suggested**")
    for sug in [
        "Member vs non-member strike rate",
        "Top/bottom 5 branches by proportion",
        "Trend for the last 30 days",
    ]:
        if st.button(sug, key=f"sug-{sug}"):
            rerun_with(sug)

# If pending, execute now
if st.session_state.pending_question:
    run_question(st.session_state.pending_question)
    st.session_state.pending_question = None

# ========== Main ==========
st.title("AI Business Assistant — Drill-down Ready")

# Answer area
if st.session_state.answer:
    st.subheader("Answer")
    st.write(st.session_state.answer)

# ---- Two separate popovers (two “pop” UIs) ----
st.subheader("Drill-down")

# Lay out side-by-side so both popovers are visible and independent
c1, c2 = st.columns(2)

# --- Pop 1: by branch ---
with c1:
    try:
        pop1 = st.popover("Drill-down: by branch")
        container1 = pop1
    except Exception:
        container1 = st.expander("Drill-down: by branch")  # fallback if st.popover unavailable

    with container1:
        st.caption("Open a focused branch view without changing the main question.")
        # Example selectors (replace with dynamic lists from DB)
        branches = st.multiselect("Select branches", ["thonglor", "kingsquare", "aree", "laguna phuket"], key="dd_branches")
        metric = st.selectbox("Metric", ["proportion", "count", "trend_30d"], key="dd_metric")
        if st.button("Run drill-down (branch)"):
            st.session_state.drilldown = {"type": "branch", "params": {"branches": branches, "metric": metric}}
            st.rerun()

# --- Pop 2: by product ---
with c2:
    try:
        pop2 = st.popover("Drill-down: by product")
        container2 = pop2
    except Exception:
        container2 = st.expander("Drill-down: by product")  # fallback

    with container2:
        st.caption("Open a focused product view (e.g., by category or item).")
        scope = st.selectbox("Scope", ["all products", "only promo=No", "fresh only", "grocery only"], key="dd_scope")
        group_by = st.selectbox("Group by", ["category L2", "category L3", "product (erp_name)"], key="dd_groupby")
        if st.button("Run drill-down (product)"):
            st.session_state.drilldown = {"type": "product", "params": {"scope": scope, "group_by": group_by}}
            st.rerun()

# ---- Render drill-down result (does not alter the main Q/A) ----
if st.session_state.drilldown:
    with st.container(border=True):
        st.markdown("### Drill-down Result")
        dd = st.session_state.drilldown
        st.write(run_drilldown(dd["type"], dd["params"]))
        # Optional: clear drilldown button
        if st.button("Clear drill-down"):
            st.session_state.drilldown = None
            st.rerun()

# “Next questions” after the answer
if st.session_state.answer:
    st.subheader("Suggested Next Questions")
    cols = st.columns(len(st.session_state.suggestions) or 1)
    for i, sug in enumerate(st.session_state.suggestions or []):
        with cols[i]:
            if st.button(sug, key=f"next-{sug}"):
                rerun_with(sug)
