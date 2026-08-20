import os
from dotenv import load_dotenv
from groq import Groq
from api_request import APIRequest

load_dotenv()

api_key: str = os.getenv("GROQ_API_KEY")

def get_api_key() -> str:
    return api_key

def get_client() -> Groq:
    return Groq()

def get_model() -> str:
    return os.getenv("GROQ_MODEL", "gpt-oss-20b")

# ---------------------------------------------------------------------------
# Prompt construction
# ---------------------------------------------------------------------------
def build_prompt(apiRequest: APIRequest) -> str:
    equipment_str: str = ", ".join(apiRequest.equipment) if apiRequest.equipment else "Not specified"
    focus_str: str = ", ".join(apiRequest.focus_areas) if apiRequest.focus_areas else "None specified"
    limitations_str: str = apiRequest.limitations.strip() if apiRequest.limitations.strip() else "None reported"

    prompt: str = f"""You are an experienced, certified personal trainer creating a real program for a client.
Use the information below the way a good trainer would. Factor in their goal, experience,
schedule, equipment, and any limitations, and make sensible adjustments (exercise selection,
volume, intensity, progression) rather than giving generic advice. 
Refer to some fitness books such as 'Encyclopedia of modern bodybuilding' by Arnold Schwarzennegar 
or 'Becoming Ageless' by Strauss Zelnick.

CLIENT PROFILE
- Fitness goal: {apiRequest.goal}
- Experience level: {apiRequest.experience}
- Days available per week: {apiRequest.days_per_week}
- Equipment access: {equipment_str}
- Age range: {apiRequest.age_range}
- Preferred session length: {apiRequest.session_length}
- Priority focus areas: {focus_str}
- Injuries / limitations: {limitations_str}

INSTRUCTIONS
1. If there are injuries or limitations, explicitly note how you adapted the plan for them
   (e.g. substituted exercises, avoided certain movements).
2. Build a full weekly split matching the number of available days exactly. Label each day
   with a name (e.g. "Day 1 - Upper Body Push") and rest days if applicable.
3. For each training day, list exercises with sets, reps (or duration), rest periods, and
   brief form/intensity cues. Match volume and intensity to the stated experience level.
4. Keep total time per session close to the client's preferred session length.
5. Add a short section at the top: "Why this plan". 2-4 sentences explaining the overall
   approach and how it's tailored to this specific client.
6. Add a brief "Progression" note at the end explaining how to advance over the coming weeks.
7. Format everything in clean Markdown with headers per day and bullet/numbered lists for
   exercises, so it renders well in a Markdown viewer.
"""
    return prompt


def build_default_plan() -> str:
    return "TODO - this is a default plan"