from datetime import date
import os

from src.model.faller import Faller

def default_datetime() -> date:
    return date(2000, 1, 1)

def default_faller() -> Faller:
    return Faller(0)

def default_app_path() -> str:
    path = os.path.join(os.getcwd(), "app")
    return path

def default_app_title() -> str:
    path = os.path.join(os.getcwd(), "app")
    return path

def init_sensor_types() -> list[str]:
    return 20 * [""]

def init_sensor_options() -> list[str]:
    return 8 * [""]