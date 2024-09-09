from dataclasses import dataclass, field

@dataclass
class Pattern1:
    name: str = ""
    formula: list[str] = field(default_factory=list)
    description: str = ""
    mean: float = 0
    stdDev: float = 0
    variance: float = 0
    stdErr: float = 0
    forAll: bool = False