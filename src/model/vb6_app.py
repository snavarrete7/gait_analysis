
from dataclasses import dataclass, field
from src.model.default_initializers import default_app_path



@dataclass
class VB6app:
    """
    Emulate default VB6 object "App", like App.Major, App.Title...
    """
    major: str = ""
    minor: str = ""
    revision: str = ""
    title: str = field(default_factory=default_app_path)
    path: str = field(default_factory=default_app_path)
    """Changed to 'appDirectory/app' from 'appDirectory', for better clarity"""
    #icon

class VB6registry:
    """
    Emulate Windows XP registry, like SaveSetting... or GetSetting...
    """
    def __init__(self):
        self.registry = {}

    def save_setting(self, appName: str, section: str, key: str, setting):
        self.registry[f"{appName}-{section}-{key}"] = setting

    def get_Setting(self, appName: str, section: str, key: str, default: str = ""):
        return self.registry[f"{appName}-{section}-{key}"]