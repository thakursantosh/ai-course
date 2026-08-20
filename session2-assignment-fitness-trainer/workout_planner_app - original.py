"""
AI Personal Trainer - Streamlit App
Collects structured user info and generates a personalized weekly workout plan via the Anthropic API.

Run locally:
    pip install streamlit anthropic
    export ANTHROPIC_API_KEY="your-key-here"   # or enter it in the sidebar at runtime
    streamlit run workout_planner_app.py
"""

import os
import streamlit as st
from anthropic import Anthropic

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="AI Personal Trainer",
    page_icon="💪",
    layout="centered",
)

st.title("💪 AI Personal Trainer")
st.caption("Tell it about yourself. Get a real weekly plan back — not just \"do some squats.\"")

# ---------------------------------------------------------------------------
# API key handling
# ---------------------------------------------------------------------------
with st.sidebar:
    st.header("Settings")
    default_key = os.environ.get("ANTHROPIC_API_KEY", "")
    api_key = st.text_input(
        "Anthropic API Key",
        value=default_key,
        type="password",
        help="Reads from the ANTHROPIC_API_KEY environment variable if set. "
             "You can also paste a key here for this session only.",
    )
    st.markdown("---")
    st.caption(
        "This app sends your inputs to the Anthropic API to generate a custom plan. "
        "No data is stored — it only lives for this session."
    )

# ---------------------------------------------------------------------------
# Structured inputs
# ---------------------------------------------------------------------------
st.subheader("Tell me about yourself")

col1, col2 = st.columns(2)

with col1:
    goal = st.selectbox(
        "Fitness goal",
        ["Build muscle", "Lose fat", "General fitness", "Improve endurance"],
    )
    experience = st.selectbox(
        "Experience level",
        ["Beginner", "Intermediate", "Advanced"],
    )

with col2:
    days_per_week = st.slider("Days available per week", min_value=1, max_value=7, value=3)
    equipment = st.multiselect(
        "Equipment access",
        ["No equipment", "Home dumbbells", "Full gym"],
        default=["Full gym"],
    )

# A few extra questions a real trainer would ask — kept optional so the
# minimum required fields alone are enough to generate a plan.
with st.expander("A few more details a trainer would ask (optional)"):
    age_range = st.selectbox(
        "Age range",
        ["Prefer not to say", "Under 18", "18–29", "30–39", "40–49", "50–59", "60+"],
    )
    session_length = st.select_slider(
        "Preferred session length",
        options=["15–30 min", "30–45 min", "45–60 min", "60–90 min"],
        value="45–60 min",
    )
    focus_areas = st.multiselect(
        "Any specific areas you'd like to prioritize?",
        ["Upper body", "Lower body", "Core", "Glutes", "Back", "Cardio/conditioning", "Mobility/flexibility"],
    )

limitations = st.text_area(
    "Injuries or limitations (optional)",
    placeholder='e.g. "bad knees", "no overhead pressing", "lower back issues"',
)

st.markdown("---")

# ---------------------------------------------------------------------------
# Prompt construction
# ---------------------------------------------------------------------------
def build_prompt() -> str:
    equipment_str = ", ".join(equipment) if equipment else "Not specified"
    focus_str = ", ".join(focus_areas) if focus_areas else "None specified"
    limitations_str = limitations.strip() if limitations.strip() else "None reported"

    prompt = f"""You are an experienced, certified personal trainer creating a real program for a client.
Use the information below the way a good trainer would — factor in their goal, experience,
schedule, equipment, and any limitations, and make sensible adjustments (exercise selection,
volume, intensity, progression) rather than giving generic advice.

CLIENT PROFILE
- Fitness goal: {goal}
- Experience level: {experience}
- Days available per week: {days_per_week}
- Equipment access: {equipment_str}
- Age range: {age_range}
- Preferred session length: {session_length}
- Priority focus areas: {focus_str}
- Injuries / limitations: {limitations_str}

INSTRUCTIONS
1. If there are injuries or limitations, explicitly note how you adapted the plan for them
   (e.g. substituted exercises, avoided certain movements).
2. Build a full weekly split matching the number of available days exactly — label each day
   with a name (e.g. "Day 1 - Upper Body Push") and rest days if applicable.
3. For each training day, list exercises with sets, reps (or duration), rest periods, and
   brief form/intensity cues. Match volume and intensity to the stated experience level.
4. Keep total time per session close to the client's preferred session length.
5. Add a short section at the top: "Why this plan" — 2-4 sentences explaining the overall
   approach and how it's tailored to this specific client.
6. Add a brief "Progression" note at the end explaining how to advance over the coming weeks.
7. Format everything in clean Markdown with headers per day and bullet/numbered lists for
   exercises, so it renders well in a Markdown viewer.
"""
    return prompt


# ---------------------------------------------------------------------------
# Generate button + output
# ---------------------------------------------------------------------------
generate = st.button("🏋️ Generate Plan", type="primary", use_container_width=True)

if generate:
    if not api_key:
        st.error("Please enter your Anthropic API key in the sidebar first.")
    elif not equipment:
        st.error("Please select at least one equipment option.")
    else:
        with st.spinner("Building your personalized weekly plan..."):
            try:
                client = Anthropic(api_key=api_key)
                response = client.messages.create(
                    model="claude-sonnet-4-5",
                    max_tokens=4000,
                    messages=[{"role": "user", "content": build_prompt()}],
                )
                plan_text = "".join(
                    block.text for block in response.content if block.type == "text"
                )
                st.session_state["plan_text"] = plan_text
            except Exception as e:
                st.error(f"Something went wrong generating your plan: {e}")

# Display last generated plan (persists across reruns within the session)
if "plan_text" in st.session_state:
    st.markdown("---")
    st.subheader("📋 Your Weekly Plan")
    st.markdown(st.session_state["plan_text"])

    st.download_button(
        "Download plan as Markdown",
        data=st.session_state["plan_text"],
        file_name="workout_plan.md",
        mime="text/markdown",
        use_container_width=True,
    )