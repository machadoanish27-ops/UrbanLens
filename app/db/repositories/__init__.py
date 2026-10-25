"""Database repositories package."""

from app.db.repositories.air_quality import AirQualityRepository
from app.db.repositories.base import BaseRepository, clean_mongo_doc
from app.db.repositories.city import CityRepository
from app.db.repositories.country import CountryRepository
from app.db.repositories.cost_of_living import CostOfLivingRepository
from app.db.repositories.source import SourceRegistryRepository
from app.db.repositories.university import UniversityRepository
from app.db.repositories.weather import WeatherRepository

__all__ = [
    "BaseRepository",
    "clean_mongo_doc",
    "CityRepository",
    "CountryRepository",
    "WeatherRepository",
    "AirQualityRepository",
    "CostOfLivingRepository",
    "UniversityRepository",
    "SourceRegistryRepository",
]
