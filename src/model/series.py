from dataclasses import dataclass
from collections.abc import Iterable
import statistics

class Series:
    """
    _timeSeries: _uBound * noOfSeries matrix. Each row is a series.
    """

    # TODO: implement constructor
    def __init__(self):
        self.noOfSeries = 0
        self._timeSeries = []
        self._avgSeries = []
        self._complexity = 0
        self._seriesNames = []
        self._uBound = 0

    def add_data_serie(self, serie: list, name: str):
        """
        1. Set self.uBound (which is 0..len(serie)+1)
        2. Allocate space for self._timeSeries and self._seriesNames
        3. self._timeSeries: MxN, where M=uBound, and N=noOfSeries (each serie has uBound items)
        4. append serie into self._timeSeries
        5. insert name into seriesNames
        6. increase noOfSeries

        """
        self._uBound = len(serie)
        self._timeSeries.append(serie)
        self._seriesNames.append(name)
        self.noOfSeries +=1
        self._avgSeries = self._uBound * [None]

        for i in range(self._uBound):
            sum = 0
            for j in range(self.noOfSeries):
                sum += self._timeSeries[j][i]
            self._avgSeries[i] = sum/self.noOfSeries

    def get_series_names(self) -> list:
        return self._seriesNames

    def get_data_uBound(self, nr: int) -> int:
        return self._uBound
    
    def get_data_serie(self, nr: int) -> list:
        return self._timeSeries[nr]
        
    def get_avg_serie(self) -> list:
        return self._avgSeries

    def set_complexity(self, value: int):
        self._complexity = value

    def get_complexity(self) -> int:
        return self._complexity