from dataclasses import dataclass, field
from datetime import datetime
from src.model.default_initializers import default_datetime, default_faller
from src.model.gait_parameter_type import GaitParameterType
from src.model.faller import Faller

@dataclass
class UserType:
    name: str = ""
    active: bool = False
    id: str = ""
    filePath: str = ""
    gaitParameter: list[GaitParameterType] = field(default_factory=list)
    faller: Faller = field(default_factory=default_faller)
    falls: list[str] = field(default_factory=list)
    lastProcessedDate: str = ""
    fallSelectedAppr2: bool = False
    selectedApp1: bool = False
    age: int = 0
    note: str = ""
    showParameter: list[str] = field(default_factory=list)
    showFRI: list[str] = field(default_factory=list)
    showStats: list[str] = field(default_factory=list)
    firstname: str = ""
    lastname: str = ""
    phone: str =""
    email: str = ""
    address: str = ""
    insole: str = ""
    ampelOnPhone: bool = False
    pressureCaliPath: str = ""
    filterChange: bool = False
    stepDiffFilter: int = 0
    removeNoOfStrides: int = 0
    stepRecognitionRude: int = 0
    minNoOfStrides: int = 0
    cleanGaitMinTime: int = 0
    cuttings: int = 0
    heightFilter: float = 0
    removeHighestLowest: float = 0
    filter: bool = False
    uploadStats: bool = False