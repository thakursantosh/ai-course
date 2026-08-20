from pydantic import BaseModel

class APIRequest(BaseModel):
    equipment: list
    focus_areas: list
    limitations: str
    goal: str
    experience: str
    days_per_week: int
    age_range: str
    session_length: str
