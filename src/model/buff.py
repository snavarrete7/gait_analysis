from dataclasses import dataclass, field

@dataclass
class Buff:
    values: list[float] = field(default_factory=list)