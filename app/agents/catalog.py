from dataclasses import dataclass


@dataclass(frozen=True)
class AgentDefinition:
    agent_id: str
    display_name: str
    scope: str
    integration_status: str = "todo"


AGENT_CATALOG = (
    AgentDefinition("location", "Location / City Intelligence", "City identity and location context"),
    AgentDefinition("environment", "Environment / Climate", "Weather, climate, and air quality"),
    AgentDefinition("mobility", "Mobility / Transportation", "Transportation and mobility options"),
    AgentDefinition("cost_of_living", "Cost-of-Living / Budget", "Costs, budgets, and affordability"),
    AgentDefinition("accommodation", "Accommodation / Locality", "Accommodation and neighborhood context"),
    AgentDefinition("education_culture", "Education / Culture / Lifestyle", "Education, culture, and lifestyle"),
    AgentDefinition("safety_healthcare", "Safety / Healthcare / Essentials", "Safety, healthcare, and essential services"),
)