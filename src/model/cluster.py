from src.model.series import Series
#from src.tools.modules import pearson_correlation, time_weighted_correlation
from scipy import stats

def time_weighted_correlation(x: list, y: list) -> float:
    """
    Custom implementation of time weighted correlation between two lists of float.

    p-value is discarded
    """
    corrs = []
    sum=0
    cnt=0

    noOfSteps=5
    strength=2

    rng=len(x)/noOfSteps
    i=len(x)-rng

    while i <= -rng:
        if i > 0:
            arr1 = rng*[None]
            arr2 = rng*[None]
            for j in range(i, i+rng+1):
                arr1[j-i]=x(j)
                arr2[j-i]=y[j]
            pearsonCorr, pVal = stats.pearsonr(arr1, arr2)
            corrs.append(pearsonCorr)
        else:
            arr1 = rng+i*[None]
            arr2 = rng+i*[None]
            for j in range(i+rng+1):
                arr1[j]=x(j)
                arr2[j]=y[j]
            pearsonCorr, pVal = stats.pearsonr(arr1, arr2)
            corrs.append(pearsonCorr)
        i=i-rng
    
    for i in range(len(corrs)+1):
        sum=sum+corrs[i]*(len(corrs)-i) / len(corrs)*strength
        cnt += len(corrs)-i+1
    
    return sum/cnt

def pearson_correlation(x: list, y: list) -> float:
    """
    Alias for scipy.pearsonr, discards p-value
    """
    corr, pVal = stats.pearsonr(x, y)
    return corr

weighted: bool = False


class Cluster:

    def __init__(self):
        self._seriesCluster = []
        self._noOfCluster = 0
        self.maxSeriesNo = 0
        self.clusterId = ""
        self.correlation = 0.0
        self.totalSeries = 0
        self.biggestClusterIndex = 0
        self._bestCorr = 0.0
        self.name = ""

    def clustering(self) -> bool:
        """
        Return true if self.maxSeriesNo*5 > self.totalSeries
        """
        return self.maxSeriesNo * 5 > self.totalSeries

    def get_no_of_cluster(self) -> int:
        return self._noOfCluster

    def add_serie(self, serie: list, name: str):
        global weighted
        marker = False

        if self.correlation == 0:
            self.correlation = 1
        
        if self._noOfCluster == 0:
            self._noOfCluster += 1
            self._seriesCluster.append(Series())

            self._seriesCluster[self._noOfCluster-1].add_data_serie(serie, name)
            self.maxSeriesNo = 1
            self.biggestClusterIndex = self._noOfCluster -1
        else:
            for i in range(self._noOfCluster):
                # TODO: add time weighted and pearson correlations
                if weighted:
                    corr = time_weighted_correlation(serie, self._seriesCluster[i].get_avg_serie())
                else:
                    corr = pearson_correlation(serie, self._seriesCluster[i].get_avg_serie())

                if corr > self.correlation:
                    if corr > self._bestCorr:
                        self._bestCorr = corr
                    self._seriesCluster[i].add_data_serie(serie, name)
                    marker = True

                    if self._seriesCluster[i].noOfSeries > self.maxSeriesNo:
                        self.maxSeriesNo = self._seriesCluster[i].noOfSeries
                        self.biggestClusterIndex = i
                    
            if not marker:
                self._noOfCluster += 1
                self._seriesCluster.append(Series())
                self._seriesCluster[self._noOfCluster-1].add_data_serie(serie, name)
        self.totalSeries += 1

    def compare_with_all_clusters(self, arr: list, seriesArr: list, maxCnt: int, overallMax: int, bestCorr: float) -> float:
        global weighted

        nr = -1
        overallMax = 0
        bestCorr = self._bestCorr
        bCorr = 0

        for i in range(self._noOfCluster):
            if self._seriesCluster[i].noOfSeries > 1:
                overallMax = self._seriesCluster.index(max(self._seriesCluster))
        
        for i in range(self._noOfCluster):
            if self._seriesCluster[i].noOfSeries > 1:
                if weighted:
                    temp = time_weighted_correlation(arr, self._seriesCluster[i].get_avg_serie())
                else:
                    temp = pearson_correlation(arr, self._seriesCluster[i].get_avg_serie())

                if temp > self.correlation:
                    if temp > bCorr and overallMax*6 > self.totalSeries:
                        bCorr = temp
                        corr = temp
                        nr = i
                        maxCnt = self._seriesCluster[i].noOfSeries

        if nr > -1:
            seriesArr = self._seriesCluster(nr).get_avg_serie()
            return corr

    def get_single_cluster(self, nr: int) -> list:
        arr = []
        data = []

        cnt = self._seriesCluster[nr].noOfSeries
        #ub = self._seriesCluster[nr].get_data_uBound(0)


        for i in range(cnt):
            arr = self._seriesCluster[nr].get_data_serie(i)
            data.append([x for x in arr])

        return data

    def get_single_cluster_avg(self, nr: int) -> list:
        return self._seriesCluster[nr].get_avg_serie()

    def get_no_of_cluster_series(self, nr: int) -> int:
        return self._seriesCluster[nr].noOfSeries

    def names_of_biggest_cluster_serie(self) -> str:
        return self._seriesCluster[self.biggestClusterIndex].get_series_names()