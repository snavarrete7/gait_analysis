from enum import Enum

class Faller(Enum):
    NON_FALLER = 0
    FALLER = 1
    CONTROL_GROUP_FALLER = -1
    CONTROL_GROUP_NON_FALLER = -2