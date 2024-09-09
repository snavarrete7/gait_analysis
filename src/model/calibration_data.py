from dataclasses import dataclass

@dataclass
class CalibrationData:
    """
    Wrapper to group calibration data.
    """
    CaliBxL: float = 0
    CaliByL: float = 0
    CaliBzL: float = 0
    CaliKxL: float = 0
    CaliKyL: float = 0
    CaliKzL: float = 0
    CaliHxL: float = 0
    CaliHyL: float = 0
    CaliHzL: float = 0

    CaliBxR: float = 0
    CaliByR: float = 0
    CaliBzR: float = 0
    CaliKxR: float = 0
    CaliKyR: float = 0
    CaliKzR: float = 0
    CaliHxR: float = 0
    CaliHyR: float = 0
    CaliHzR: float = 0
    