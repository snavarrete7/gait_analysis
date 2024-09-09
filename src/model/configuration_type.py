from dataclasses import dataclass, field, fields

from src.model.user_type import UserType
from src.model.gait_def import GaitDef
from src.model.pattern1 import Pattern1
from src.model.pattern2 import Pattern2
from src.model.risk_index import RiskIndex

@dataclass
class ConfigurationType:
    name: str = ""
    inputType: int = 0
    users: list[UserType] = field(default_factory=list)
    skipLines: int = 0
    columnSeparator: int = 0
    decimalSeparator: int = 0
    lineSeparator: int = 0

    columns: list[str] = field(default_factory=list)
    columnType: list[int] = field(default_factory=list)
    columnOption: list[int] = field(default_factory=list)
    columnUnit: list[str] = field(default_factory=list)
    """Check toplevel window "New" (in data input selection) to understand each of these attributes"""

    selectedUser: str = ""
    stepDiffFilter: float = 0
    removeNoOfStrides: int = 0
    stepRecognitionRude: int = 0
    minNoOfStrides: int = 0
    cleanGaitMinTime: int = 0
    cuttings: int = 0
    heightFilter: float = 0
    removeHighestLowest: float = 0
    selectToWatch: str = ""
    sensorToWatch: str = ""
    gaitParameterDef: list[GaitDef] = field(default_factory=list)
    gaitPattern1: list[Pattern1] = field(default_factory=list)
    gaitPattern2: list[Pattern2] = field(default_factory=list)
    selectedFactsheet: str = ""
    fallRiskIndex: list[RiskIndex] = field(default_factory=list)
    changed: bool = False
    coreChange: bool = False
    sampleFrequency: int = 0
    userAdded: bool = False
    filterStdDevF: float = 0
    filterVarianceF: float = 0
    filterStdErrF: float = 0
    filterStdDevN: float = 0
    filterVarianceN: float = 0
    filterStdErrN: float = 0
    filterHighLowF: float = 0
    filterHighLowN: float = 0
    filter: bool = False