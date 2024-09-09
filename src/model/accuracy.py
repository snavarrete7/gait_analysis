from dataclasses import dataclass, field
from src.model.component import Component

@dataclass
class Accuracy:
    percent: float = 0
    weights: list[Component] = field(default_factory=list)