"""
AI Personal Trainer - Streamlit App
Collects structured user info and generates a personalized weekly workout plan via the Groq API.

Run locally:
    pip install streamlit
    Add GROQ_API_KEY and GROQ_MODEL to .env
    streamlit run workout_planner_app.py
"""

import streamlit as st
from api_backend import get_api_key, get_client, get_model, build_prompt, build_default_plan
from api_request import APIRequest

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
# Structured inputs
# ---------------------------------------------------------------------------
st.subheader("Tell me about yourself")

col1, col2 = st.columns(2)

with col1:
    goal: list = st.selectbox(
        "Fitness goal",
        ["Please select one option", "Build muscle", "Lose fat", "General fitness", "Improve endurance"],
    )
    experience: list = st.selectbox(
        "Experience level",
        ["Please select one option", "Beginner", "Intermediate", "Advanced"],
    )

with col2:
    days_per_week: int = st.slider("Days available per week", min_value=1, max_value=7, value=3)
    equipment: list = st.multiselect(
        "Equipment access",
        ["No equipment", "Home dumbbells", "Full gym"]
    )

# A few extra questions a real trainer would ask — kept optional so the
# minimum required fields alone are enough to generate a plan.
with st.expander("A few more details a trainer would ask (optional)"):
    age_range: list = st.selectbox(
        "Age range",
        ["Prefer not to say", "Under 18", "18–29", "30–39", "40–49", "50–59", "60+"],
    )
    session_length: str = st.select_slider(
        "Preferred session length",
        options=["15–30 min", "30–45 min", "45–60 min", "60–90 min"],
        value="45–60 min",
    )
    focus_areas: list = st.multiselect(
        "Any specific areas you'd like to prioritize?",
        ["Upper body", "Lower body", "Core", "Glutes", "Back", "Cardio/conditioning", "Mobility/flexibility"],
    )

limitations: str = st.text_area(
    "Injuries or limitations (optional)",
    placeholder='e.g. "bad knees", "no overhead pressing", "lower back issues"',
)

st.markdown("---")

# ---------------------------------------------------------------------------
# Generate button + output
# ---------------------------------------------------------------------------
generate = st.button("🏋️ Generate Plan", type="primary", use_container_width=True)

if generate:
    if not get_api_key():
        st.error("Groq API key missing.")
    elif not goal or goal == "Please select one option" :
        st.error("Please select at least one fitness goal option.")
    elif not experience or experience == "Please select one option" :
        st.error("Please select at least one experience level.")
    elif not equipment:
        st.error("Please select at least one equipment option.")
    else:
        with st.spinner("Building your personalized weekly plan..."):
            try:
                client = get_client()
                model: str = get_model()
                api_request: APIRequest = APIRequest(equipment=equipment,
                    focus_areas=focus_areas,
                    limitations=limitations,
                    goal=goal,
                    experience=experience,
                    days_per_week=days_per_week,
                    age_range=age_range,
                    session_length=session_length)
                prompt: str = build_prompt(api_request)
                response = client.chat.completions.create(
                    model = model,
                    messages=[
                        {"role": "system", "content": "You are a well-qualified popular fitness trainer."},
                        {"role": "user", "content": prompt}],
                    temperature=0.8,
                    max_completion_tokens=1000
                )
                plan_text: str = response.choices[0].message.content
                if not plan_text:
                    st.markdown("---")
                    st.subheader("📋 Your Default Plan")
                    st.markdown("API response was empty. Hence, here's your default plan: \n")
                    st.markdown(build_default_plan())
                else:
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