from dataclasses import dataclass, field

@dataclass
class SensorSelector:
    newSensor: bool = False
    selectedSensor: int = -1
