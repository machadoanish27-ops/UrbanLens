"""Agent package with 7 modular domain intelligence agents."""

from app.agents.accommodation import AccommodationAgent
from app.agents.base import BaseAgent
from app.agents.catalog import AGENT_CATALOG, AgentDefinition
from app.agents.cost import CostAgent
from app.agents.education_lifestyle import EducationLifestyleAgent
from app.agents.environment import EnvironmentAgent
from app.agents.location import LocationAgent
from app.agents.mobility import MobilityAgent
from app.agents.safety_healthcare import SafetyHealthcareAgent

__all__ = [
    "BaseAgent",
    "AgentDefinition",
    "AGENT_CATALOG",
    "LocationAgent",
    "EnvironmentAgent",
    "MobilityAgent",
    "CostAgent",
    "AccommodationAgent",
    "EducationLifestyleAgent",
    "SafetyHealthcareAgent",
]
