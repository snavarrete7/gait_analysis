from dataclasses import dataclass, field
from datetime import datetime
from src.model.default_initializers import default_datetime
from src.model.gait_def import GaitDef
from src.model.gait_parameter_type import GaitParameterType

@dataclass
class UserData:
    name: str = ""
    email: str = ""
    id: str = ""
    newDates: list[datetime] = field(default_factory=list)
    gaitParameterDef: list[GaitDef] = field(default_factory=list)
    gaitParameter: list[GaitParameterType] = field(default_factory=list)
    lastProcessedDate: datetime = field(default_factory=default_datetime)