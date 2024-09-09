from dataclasses import dataclass, field

from src.model.component import Component

@dataclass
class RiskIndex:
    name: str = ""
    active: bool = False
    redStart: float = 0
    redEnd: float = 0
    yellowStart: float = 0
    yellowEnd: float = 0
    greenStart: float = 0
    greenEnd: float = 0
    components: list[Component] = field(default_factory=list)
    forAll: bool = False