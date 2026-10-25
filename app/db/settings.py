import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class MongoSettings:
    uri: str
    database: str

    @classmethod
    def from_environment(cls) -> "MongoSettings":
        try:
            from dotenv import load_dotenv

            project_root = Path(__file__).resolve().parents[2]
            load_dotenv(project_root / ".env", override=False)
        except ImportError:
            pass
        uri = os.getenv("MONGODB_URI")
        database = os.getenv("MONGODB_DB")
        if not uri or not database:
            raise ValueError("MONGODB_URI and MONGODB_DB must both be configured.")
        return cls(uri=uri, database=database)