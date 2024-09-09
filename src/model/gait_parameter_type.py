from dataclasses import dataclass, field
from datetime import datetime
from src.model.default_initializers import default_datetime

@dataclass
class GaitParameterType:
    name: str = ""
    mean: float = 0
    variation: float = 0
    date: datetime = field(default_factory=default_datetime)