from dataclasses import dataclass, field
#import src.model as m
from src.model.gait_data import GaitData
from src.model.configuration_type import ConfigurationType
from src.model.cluster import Cluster
from src.model.UNKNOWN_DATA import UnknownData
from src.model.patient import Patient
from src.model.default_initializers import init_sensor_options, init_sensor_types


@dataclass
class ToolVars:
    """
    Additional class to enforce type hinting. Meant to be used as a Singleton instance, globally.
    """
    rawGait: GaitData = field(default_factory=GaitData)
    #GUI
    #fileDialog: fileDialog
    loadingConf: bool = False
    configuration: ConfigurationType = field(default_factory=ConfigurationType)
    sensorTypes: list[str] = field(default_factory=init_sensor_types)
    sensorOptions: list[str] = field(default_factory=init_sensor_options)
    _distanceXnew: list[float] = field(default_factory=list)
    _distanceYnew: list[float] = field(default_factory=list)
    _distanceZnew: list[float] = field(default_factory=list)
    cluster: list[Cluster] = field(default_factory=list)
    Ncluster: list[Cluster] = field(default_factory=list)
    #GUI
    loading: bool = False

    user: str = ""
    password: str = ""
    user2: str = ""
    password2: str = ""
    isUserMonitor: bool = False
    patients: list[Patient] = field(default_factory=list)
    login: bool = False
    const1: float = 0
    const2: float = 0

    unknownData: UnknownData = field(default_factory=UnknownData)

    myDocFolder: str = ""
    """Will point to MyDocumentsFolder"""
    myDocFolderRoot: str = ""
    """Will point to MyDocumentsFolder/{appName}"""