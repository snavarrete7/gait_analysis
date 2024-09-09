from dataclasses import dataclass, field
import src.model as m

@dataclass
class PatternExtraction:
    selected: str = ""
    pattern: list[m.Pattern1] = field(default_factory=list)