
from dataclasses import dataclass, field
import statistics

@dataclass
class Stepdata:
    """
    Stores measured gait data.
    """
    rightStart: float = 0.0
    rightStartNext: float = 0.0
    rightEnd: float = 0.0
    leftStart: float = 0.0
    leftStartLast: float = 0.0
    leftEnd: float = 0.0
    leftEndNext: float = 0.0
    rightHeel: float = 0.0
    rightToe: float = 0.0
    leftHeel: float = 0.0
    leftToe: float = 0.0
    rightHeelNext: float = 0.0
    leftHeelNext: float = 0.0
    leftToeNext: float = 0.0

    rightStartRow: int = 0
    rightStartNextRow: int = 0
    rightEndRow: int = 0
    leftStartRow: int = 0
    leftStartLastRow: int = 0
    leftEndRow: int = 0
    leftEndNextRow: int = 0
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
    gaitParameter: list[float] = field(default_factory=list)

@dataclass
class Gait:
    _strides: list[Stepdata] = field(default_factory=list)
    _sensorNames: list[str] = field(default_factory=list)
    _sensorData: list[list[float]] = field(default_factory=list)
    _gaitParameterName: list[str] = field(default_factory=list)
    Parameter: list[float] = field(default_factory=list)


    _means: list[float] = field(default_factory=list)
    _variations: list[float] = field(default_factory=list)

    numStrides: int = 0
    numSensors: int = 0
    noOfParameter: int = 0
    currentName: str = ""
    processedRows: int = 0

    
    def get_intraday_raw_data(self) -> list[str]:
        # TODO: refactor list of string to something else
        """
        Turn class gait data (right-left start-end) into raw lines.

        Returns these lines
        """
        result = []
        for stride in self._strides:
            line = f"{stride.rightStart},{stride.rightEnd},{stride.leftStart},{stride.leftEnd}"
            result.append(line)
        return result
    
    def get_intraday_parameter(self, paraNr: int) -> list:
        """
        Iterate over self._strides, 
        """
        result = []
        for stride in self._strides:
            rawData = f"{stride.rightStartRow + self.processedRows},{round(stride.gaitParameter[paraNr], ndigits=4)},{stride.rightStart}"
            result.append(rawData)
        return result

    def calc_mean_and_variation(self, paraArr: list[float]) -> tuple:
        """
        Old name: get_mean_and_variation
        Calculates mean and variation of input numeric array.
        Return: (mean, variation)
        """
        mean = statistics.mean(paraArr)
        variation = statistics.stdev(paraArr) / mean * 100
        return mean, variation


    def get_mean(self, paraNr: int) -> float:
        return self._means[paraNr]

    def get_variation(self, paraNr: int) -> float:
        return self._variations[paraNr]

    def calc_daily_parameter(self, nr: int):
        """
        Sets mean and variation for data at index nr.
        """
        paraArr = []
        for stride in self._strides:
            paraArr.append(stride.gaitParameter[nr])

        mean, variation = self.calc_mean_and_variation(paraArr)
        self._means[nr] = mean
        self._variations[nr] = variation

    def calc_daily_parameter_special(self, nr: int, floatArr: list[float]):
        """
        Same as self.calc_daily_parameter, but obtain floatArr as parameter instead.
        """
        if len(self._variations) < nr or len(self._variations) == 0:
            lengthDiff = nr - len(self._variations)
            self._variations = list(self._variations).extend(lengthDiff * [0])
            self._means = list(self._means).extend(lengthDiff * [0])

        mean, variation = self.calc_mean_and_variation(floatArr)
        self._means[nr] = mean
        self._variations[nr] = variation
    
    def remove_highest_lowest_gait(self, nr: int, removeHighestLowest: float):
        nrToRemove = ( len(self._strides)+1 ) * 0.01 * removeHighestLowest
        for i in range(nrToRemove):
            self._remove_lowest_stride(nr)
            self._remove_highest_stride(nr)
    
    def _remove_lowest_stride(self, paraNr: int):
        """
        Replace strides with lowest gaitParameter[paraNr] with the previous value.
        """
        #1. Find lowest
        low = 9999999
        for i in range(self._strides):
            if self._strides[i].gaitParameter[paraNr] < low:
                low = self._strides[i].gaitParameter[paraNr]

        #2. Replace all instances of lowest with the previous
        for i in range(1, len(self._strides)):
            if self._strides[i].gaitParameter[paraNr] == low:
                self._strides[i].gaitParameter[paraNr] = self._strides[i-1].gaitParameter[paraNr]

        #What, if the first is the lowest ? First = 0
        if self._strides[0].gaitParameter[paraNr] == low:
            self._strides[0].gaitParameter[paraNr] = self._strides[-1].gaitParameter[paraNr]

    def _remove_highest_stride(self, paraNr: int):
        """
        Replace strides with biggest gaitParameter[paraNr] with the previous value.
        """
        #1. Find lowest
        high = -9999999
        for i in range(self._strides):
            if self._strides[i].gaitParameter[paraNr] > high:
                high = self._strides[i].gaitParameter[paraNr]

        #2. Replace all instances of highest with the previous
        for i in range(1, len(self._strides)):
            if self._strides[i].gaitParameter[paraNr] == high:
                self._strides[i].gaitParameter[paraNr] = self._strides[i-1].gaitParameter[paraNr]

        #What, if the first is the highest ? First = 0
        if self._strides[0].gaitParameter[paraNr] == high:
            self._strides[0].gaitParameter[paraNr] = self._strides[-1].gaitParameter[paraNr]

    def get_parameter_arr(self, nr: int) -> list[float]:
        """
        Returns corresponding GaitParameter from every stride as list[float].
        """
        result = []
        for stride in self._strides:
            result.append(stride.gaitParameter[nr])
        return result

    def set_step_nr(self, nr: int):
        """
        Set self.numStrides and allocate space for self._strides.
        """
        self._strides = nr * [Stepdata()]
        self.numStrides = nr

    def sensor_nr(self, name: str) -> int:
        """
        Return index of self._sensorNames with same name.

        If not found, returns -1 and logs.
        """
        try:
            return list(self._sensorNames).index(name)
        except ValueError as err:
            print(f"Gait.sensor_nr: value {name} is not present. Err: {err}")
            return -1

    def set_sensor_data(self, data: list):
        """
        Set self._sensor_data with provided float matrix.
        """
        self._sensorData = data

    def set_nr_of_gait_parameter(self, nr: int):
        """
        Initialize arrays self._gaitParameterName, self._means, self._variations and each stride.gaitParameter with provided nr size.
        """
        self._gaitParameterName = nr * [""]
        self._means = nr * [0.0]
        self._variations = nr * [0.0]

        for stride in self._strides:
            stride.gaitParameter = nr * [0.0]

    def sensor_nr_of_data(self, x: int) -> int:
        """
        Returns length of self._sensorData
        """
        return len(self._sensorData)

    def get_index_gait_param_name(self, gaitParameterName: str) -> int:
        """
        Old name: get_no
        Return index of self.gaitParameterName with matching provided gaitParameterName.

        If not found, return -1 and logs.
        """
        try:
            return list(self._gaitParameterName).index(gaitParameterName)
        except ValueError as err:
            print(f"Gait.get_index_gait_param_name: a value with name {gaitParameterName} is not present in _gaitParameterName [{self._gaitParameterName}]. Err: f{err}")
            return -1

    # Here begin properties

    def set_sensor_no(self, no: int):
        self._sensorNames = [""] * no
        self.numSensors = no

    def set_sensor_name(self, x: int, value: str):
        """
        Set self._sensorName at index x
        """
        self._sensorNames[x] = value
    
    def get_sensor_name(self, x: int) -> str:
        return self._sensorNames[x]

    def set_sensorData(self, x: int, y: int, value: float):
        """
        Set self._sensorData at index x, y
        """
        self._sensorData[x][y] = value

    def get_sensor_data(self, x: int, y: int) -> float:
        return self._sensorData[x][y]

    def set_stride_parameter(self, x: int, name: str, value):
        """
        Old name: set_strides
        Set any stride value (except stride.gaitParameter) providing the index x and the right name (i.e.: rightStartNext, rightEnd...).
        All class "Stride" member names are valid except "gaitParameter"
        """
        # TODO: check if name is valid + verify only valid names are provided i.e. "gaitParameter" is forbidden
        setattr(self._strides[x], name, value)

    def get_stride_parameter(self, x: int, name: str):
        """
        Get a value at stride index x by name. If name is incorrect, returns None.
        """
        return getattr(self._strides[x], name)

    def set_gait_parameter(self, x: int, name: str, value: float):
        """
        Set self._strides[x].GaitParameter[name] with value.
        """
        self._strides[x].gaitParameter[self.get_index_gait_param_name(name)] = value

    def get_gait_parameter(self, x: int, name: str) -> float:
        """
        Get self._strides[x] with index of gaitParameter with matching name.
        """
        return self._strides[x].gaitParameter[self.get_index_gait_param_name(name)]

    def set_gait_parameter_name(self, x: int, value: str):
        """
        Set self._gaitParameterName[x]
        """
        self._gaitParameterName[x] = value

    def get_gait_parameter_name(self, x: int) -> str:
        """
        Get self._gaitParameterName[x]
        """
        return self._gaitParameterName[x]

    #GUI
    #TODO???
    #def set_ref()
    #    pass