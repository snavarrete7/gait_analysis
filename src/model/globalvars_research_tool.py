from src.model.default_initializers import default_datetime
from dataclasses import dataclass, field
import datetime
# from src.model.buff import Buff
# from src.model.accuracy import Accuracy
# from src.model.user_data import UserData
# from src.model.vb6_app import VB6app, VB6registry
from src.model.globalvars_tl_select_subject import SelectSubject
from src.model.globalvars_tl_user_info import UserInfo
from src.model.globalvars_tl_pattern_extraction import PatternExtraction
from src.model.globalvars_tl_sensor_selector import SensorSelector
import src.model as m

@dataclass
class ResearchToolVars:
    """
    Additional class to enforce type hinting. Meant to be used as a Singleton instance, globally.

    All fields are meant to be private for research_tool
    """
    gait: m.Gait = field(default_factory=m.Gait)
    """
    Gait used for codesense and calculating gait parameters (for function process_data())
    """

    noChange: bool = False
    buffer: list[m.Buff] = field(default_factory=list)
    start: int = 0
    LINES: int = 100000
    col: int = 0
    row: int = 0
    autoAdd: bool = False
    autoArr: list[str] = field(default_factory=list)
    autoType: list[str] = field(default_factory=list)
    processedRows: int = 0
    resize: bool = False
    activated: bool = False
    blnConnected: bool = False
    date: datetime.date = field(default_factory=default_datetime)
    dontRefillList: bool = False
    cancel: bool = False
    results: list[m.Accuracy] = field(default_factory=list)
    health: list[bool] = field(default_factory=list)
    userData: list[m.UserData] = field(default_factory=list)
    oldDate: datetime.date = field(default_factory=default_datetime)

    registry: m.VB6registry = field(default_factory=m.VB6registry)
    app: m.VB6app = field(default_factory=m.VB6app)

    list9Itemdata: list[int] = field(default_factory=list)
    """
    New addition, metadata for list 9 items.
    """

    selectSubjects: SelectSubject = field(default_factory=SelectSubject)
    userInfo: UserInfo = field(default_factory=UserInfo)
    patternExtraction: PatternExtraction = field(default_factory=PatternExtraction)
    sensorSelector: SensorSelector = field(default_factory=SensorSelector)