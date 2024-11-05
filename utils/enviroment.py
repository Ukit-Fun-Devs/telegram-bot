from dataclasses import dataclass
from os import getenv

from dotenv import load_dotenv

__all__ = (
    "env",
)


@dataclass
class _Environment:
    TOKEN: str
    DATABASE_URL: str


load_dotenv()

env = _Environment(
    TOKEN=getenv("TOKEN"),
    DATABASE_URL=getenv("DATABASE_URL")
)
