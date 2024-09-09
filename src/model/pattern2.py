from dataclasses import dataclass, field

@dataclass
class Pattern2:
    base: str = ""
    name: str = ""
    evolution: list[str] = field(default_factory=list)
    description: str = ""