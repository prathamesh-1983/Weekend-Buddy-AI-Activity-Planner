import streamlit as st
from dotenv import load_dotenv
from agent.planner import create_plan, apply_preference_text

load_dotenv()
st.set_page_config(page_title="Weekend Buddy", page_icon="🌙", layout="wide")

st.markdown("""
<style>
.stApp{background:radial-gradient(ellipse at 10% 0%,rgba(124,58,237,.18),transparent 35%),#090b12;color:#eef0fa}
[data-testid="stHeader"]{background:rgba(9,11,18,.85)}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#111421,#0c0e17);border-right:1px solid #292d42}
.block-container{max-width:1250px;padding-top:2rem}
h1,h2,h3{color:#f6f5ff!important;letter-spacing:-.025em}
p,label,.stMarkdown{color:#c5c9dc}
.hero{border:1px solid #45336d;background:linear-gradient(120deg,rgba(124,58,237,.23),#111421 65%,rgba(14,165,233,.12));border-radius:24px;padding:30px;margin-bottom:24px}
.eyebrow{color:#c4b5fd;font-size:.75rem;font-weight:800;letter-spacing:.16em;text-transform:uppercase}
.hero-title{font-size:clamp(2.2rem,4vw,3.5rem);line-height:1.08;font-weight:850;color:white;margin:10px 0}
.hero-sub{font-size:1.02rem;color:#c5c9dc;max-width:720px}
.pill{display:inline-block;background:#191b2c;border:1px solid #393653;color:#dcd6ff;border-radius:999px;padding:5px 10px;margin:12px 5px 0 0;font-size:.8rem}
.card{background:linear-gradient(145deg,#191d2e,#0f121d);border:1px solid #2b3047;border-radius:18px;padding:18px;margin-bottom:12px;min-height:190px}
.card-title{color:#fff;font-size:1.1rem;font-weight:750;margin:8px 0}
.card-meta{color:#a6aec8;font-size:.84rem}
.card-desc{color:#c5c9dc;font-size:.91rem;line-height:1.5}
.kicker{color:#a78bfa;font-size:.75rem;letter-spacing:.14em;text-transform:uppercase;font-weight:800}
div.stButton>button[kind="primary"]{background:linear-gradient(90deg,#7c3aed,#6366f1);border:0;border-radius:12px;color:white;font-weight:800;min-height:2.9rem}
div.stButton>button{border-radius:10px}
[data-testid="stMetric"]{background:#151827;border:1px solid #2a2e43;border-radius:14px;padding:12px}
[data-testid="stMetricLabel"]{color:#9da4bf}[data-testid="stMetricValue"]{color:#fff}
.stTextInput input,.stNumberInput input,.stTextArea textarea,.stSelectbox div[data-baseweb="select"]>div{background:#111421!important;color:#f3f4ff!important;border-color:#30344b!important}
</style>
""", unsafe_allow_html=True)

if "plan" not in st.session_state:
    st.session_state.plan = None
if "prefs" not in st.session_state:
    st.session_state.prefs = None
if "completed" not in st.session_state:
    st.session_state.completed = []

with st.sidebar:
    st.markdown("## 🌙 Weekend Buddy")
    st.caption("Your screen-free time, better planned.")
    st.markdown("---")
    with st.form("preferences"):
        st.markdown("### ✨ Your vibe")
        budget = st.slider("Budget (₹)", 0, 3000, 500, 50)
        hours = st.slider("Free time (hours)", 0.5, 12.0, 4.0, 0.5)
        category_label = st.selectbox("Activity style", ["Any", "Indoor", "Outdoor"])
        energy_label = st.selectbox("Energy level", ["Any", "Relaxing", "Moderate", "Active"])
        company_label = st.selectbox("Who is joining?", ["Anyone", "Solo", "Friends / family"])
        max_items = st.slider("Number of activities", 1, 4, 3)
        generate = st.form_submit_button("✨ Build my weekend plan", type="primary", use_container_width=True)
    st.markdown("---")
    st.caption("Works without an API key. Costs are estimates; venues and opening hours are not verified.")

st.markdown("""
<div class="hero">
 <div class="eyebrow">YOUR PERSONAL OFFLINE-ACTIVITY AGENT</div>
 <div class="hero-title">Make room for a<br>better kind of weekend.</div>
 <div class="hero-sub">Tell me your time, budget, and mood. I'll build a realistic mini-itinerary so you spend less time deciding and more time enjoying.</div>
 <span class="pill">✦ Personalised plans</span><span class="pill">◷ Time-aware</span><span class="pill">₹ Budget-friendly</span><span class="pill">☾ Screen-free ideas</span>
</div>
""", unsafe_allow_html=True)

def get_prefs():
    return {
        "budget": int(budget), "available_minutes": int(hours*60),
        "category": {"Any":"either","Indoor":"indoor","Outdoor":"outdoor"}[category_label],
        "energy": {"Any":"any","Relaxing":"relaxing","Moderate":"moderate","Active":"active"}[energy_label],
        "company": {"Anyone":"any","Solo":"solo","Friends / family":"group"}[company_label],
        "max_items": int(max_items)
    }

if generate:
    st.session_state.prefs = get_prefs()
    st.session_state.plan = create_plan(st.session_state.prefs)
    st.session_state.completed = []

left, right = st.columns([1.35, 1], gap="large")
with left:
    st.markdown('<div class="kicker">01 / YOUR PLAN</div>', unsafe_allow_html=True)
    st.subheader("A little structure. A lot more fun.")
    if st.session_state.plan is None:
        st.markdown("""
        <div class="card"><div style="font-size:2rem">🪄</div><h3>Ready when you are</h3>
        <p>Choose your preferences in the left panel and build your first plan. Your activity cards will appear here with time and cost estimates.</p></div>
        """, unsafe_allow_html=True)
        a,b,c = st.columns(3)
        for col, icon, title, meta, desc in [
            (a,"🌿","Reset","₹0 · 60 min","A walk and a journal break"),
            (b,"🎲","Connect","₹200 · 2 hours","Games and a snack with friends"),
            (c,"🧘","Recharge","₹0 · 45 min","Stretching and reading")]:
            with col:
                st.markdown(f'<div class="card"><div style="font-size:1.8rem">{icon}</div><div class="card-title">{title}</div><div class="card-meta">{meta}</div><p class="card-desc">{desc}</p></div>', unsafe_allow_html=True)
    else:
        result = st.session_state.plan
        st1,st2,st3 = st.columns(3)
        st1.metric("Estimated spend", f"₹{result['total_cost']}")
        st2.metric("Time planned", f"{result['total_minutes']} min")
        st3.metric("Budget left", f"₹{result['remaining_budget']}")
        st.info(result["explanation"], icon="✨")
        if not result["activities"]:
            st.warning("No activities match these constraints. Try more time, a higher budget, or Any activity style.")
        for i, activity in enumerate(result["activities"]):
            if i % 2 == 0:
                cols = st.columns(2, gap="medium")
            with cols[i % 2]:
                st.markdown(f'<div class="card"><div style="font-size:1.8rem">{activity.get("icon","✨")}</div><div class="card-title">{activity["name"]}</div><div class="card-meta">◷ {activity["duration_minutes"]} min · ₹{activity["estimated_cost"]} estimated</div><p class="card-desc">{activity["description"]}</p><span class="pill">{activity["category"].title()}</span><span class="pill">{activity["energy"].title()}</span></div>', unsafe_allow_html=True)
                checked = st.checkbox("Completed", key=f"done_{activity['id']}", value=activity["id"] in st.session_state.completed)
                if checked and activity["id"] not in st.session_state.completed:
                    st.session_state.completed.append(activity["id"])
                elif not checked and activity["id"] in st.session_state.completed:
                    st.session_state.completed.remove(activity["id"])
        if result["activities"]:
            done = sum(a["id"] in st.session_state.completed for a in result["activities"])
            st.progress(done/len(result["activities"]), text=f"{done} of {len(result['activities'])} activities completed")
        if st.button("🔄 Generate another plan", use_container_width=True):
            st.session_state.plan = create_plan(st.session_state.prefs)
            st.session_state.completed = []
            st.rerun()

with right:
    st.markdown('<div class="kicker">02 / MAKE IT YOURS</div>', unsafe_allow_html=True)
    st.subheader("A plan that listens")
    st.write("Ask for a tweak in plain language. Supported requests update your constraints and rebuild the plan.")
    with st.form("adjust"):
        adjustment = st.text_input("What would you like to change?", placeholder="Make it cheaper and indoors")
        adjust = st.form_submit_button("Update my plan", use_container_width=True)
    if adjust:
        if not adjustment.strip():
            st.warning("Type a change first, such as “make it shorter”.")
        else:
            current = st.session_state.prefs or {"budget":500,"available_minutes":240,"category":"either","energy":"any","company":"any","max_items":3}
            st.session_state.prefs = apply_preference_text(current, adjustment)
            st.session_state.plan = create_plan(st.session_state.prefs)
            st.session_state.completed = []
            st.rerun()
    st.markdown("---")
    st.markdown("### 🧠 How the agent works")
    st.markdown("""
    <div class="card">
    <p><b style="color:#ddd6fe">1. Understand</b><br>Read your time, budget, energy, and company preferences.</p>
    <p><b style="color:#ddd6fe">2. Use tools</b><br>Filter activities against constraints, then assemble a feasible itinerary.</p>
    <p><b style="color:#ddd6fe">3. Explain</b><br>Return the plan, estimates, and remaining budget. Optional Bedrock adds an AI-generated explanation.</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("### 💬 Quick changes")
    for prompt in ["Make it cheaper", "I want something indoors", "Make it shorter", "I need something relaxing"]:
        if st.button(prompt, key=f"quick_{prompt}", use_container_width=True):
            current = st.session_state.prefs or {"budget":500,"available_minutes":240,"category":"either","energy":"any","company":"any","max_items":3}
            st.session_state.prefs = apply_preference_text(current, prompt)
            st.session_state.plan = create_plan(st.session_state.prefs)
            st.session_state.completed = []
            st.rerun()

st.markdown("---")
st.caption("Weekend Buddy · Python + Streamlit · Optional Amazon Bedrock · Prototype activity costs are estimates.")
