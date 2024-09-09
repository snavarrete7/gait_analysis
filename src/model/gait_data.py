from dataclasses import dataclass, field
from src.model.mode import Mode
from src.model.calibration_data import CalibrationData
from src.model.default_initializers import default_datetime

from datetime import datetime

@dataclass
class RawStepdata:
    rightStart: float = 0.0
    rightStartNext: float = 0.0
    rightStartLast: float = 0.0
    rightEnd: float = 0.0
    leftStart: float = 0.0
    leftStartNext: float = 0.0
    leftStartLast: float = 0.0
    leftEnd: float = 0.0
    leftEndNext: float = 0.0
    leftEndLast: float = 0.0

    rightHeel: float = 0.0
    rightToe: float = 0.0
    leftHeel: float = 0.0
    leftToe: float = 0.0
    rightHeelNext: float = 0.0
    leftHeelNext: float = 0.0
    leftToeNext: float = 0.0

    rightStartRow: int = 0
    rightStartNextRow: int = 0
    rightStartLastRow: int = 0
    rightEndRow: int = 0
    leftStartRow: int = 0
    leftStartNextRow: int = 0
    leftStartLastRow: int = 0
    leftEndRow: int = 0
    leftEndNextRow: int = 0
    leftEndLastRow: int = 0

    rightHeelRow: int = 0
    rightToeRow: int = 0
    leftHeelRow: int = 0
    leftToeRow: int = 0
    rightHeelNextRow: int = 0
    leftHeelNextRow: int = 0
    leftToeNextRow: int = 0

    rightHeight: float = 0.0
    leftHeight: float = 0.0

    rightWidth: float = 0.0
    leftWidth: float = 0.0

    rightLength: float = 0.0
    leftLength: float = 0.0
    rightStrideLength: float = 0.0
    leftStrideLength: float = 0.0

    no: int = 0
    remove: bool = False

@dataclass
class GaitData:

    gDate: list[str] = field(default_factory=list)
    gLtime: list[float] = field(default_factory=list)
    gRtime: list[float] = field(default_factory=list)
    
    gRightAcc: list[float] = field(default_factory=list)
    gRightAccAP: list[float] = field(default_factory=list)

    gLeftAcc: list[float] = field(default_factory=list)
    gLeftAccAP: list[float] = field(default_factory=list)

    strides: list[RawStepdata] = field(default_factory=list)

    columnName: list[str] = field(default_factory=list)
    columnData: list[list[float]] = field(default_factory=list)

    activityTime: float = 0
    noOfStrides: int = 0
    distanceWalked: float = 0

    mode: Mode = 0
    calibrationData: CalibrationData = field(default_factory=CalibrationData)