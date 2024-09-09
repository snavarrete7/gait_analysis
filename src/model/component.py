from dataclasses import dataclass

@dataclass
class Component:
    elementName: str = ""
    weight: float = 0
    impact: float = 0