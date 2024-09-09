from dataclasses import dataclass, field

@dataclass
class GaitDef:
    name: str = ""
    active: bool = False
    script: list[str] = field(default_factory=list)
    unit: str = ""