## Module: Tools

### Meaningful functions:
* EraseConfiguration()
* GetUserNo: search user by name
* GetFalls(userID) []string: get falls from "data/user_id/falls.txt"
* IsUserInOnlineList: check if user is in tools.patients
* GetRowsFromFile: get rows from a certain file. Choose starting row and how many rows you want.
* GetDayDataFromFile:
* GetNextDateFile:
* SortDates: 
* GetDayDataFromWIISEL:

* GetMax(...): same as above
* GetMin2(col int, length int) float: minimum element of array tools.rawGait.columnData
* MakeRude3Acc(lastRude int, acc float, acc2 float, acc3 float, rudeness int) int
    1. LastRude==0:

        if all [acc, acc2, acc3] > 11
            
            return 1
            
    2. lastRude==1:

        if all [acc, acc2, acc3] >= 11

            return 1

* MakeRudeAcc2(lastRude int, acc1... acc10 float, maxAcc float) int
    1. if maxAcc < 5 --> maxAcc = 10
    2. lastRude=1:

        if all [acc1..acc10] < 0.1 then return 0
        
        else return 1
    3. lastRude=0:
    
        if acc1 > (max*0.1) then return 1
        else return 0

* MakeUserPaths: Build paths for storing user data. Path list is following:
    * myDocFolder/configurations/conf.Name/subjects/user.ID
    * myDocFolder/configurations/conf.Name/subjects/user.ID/parameter
    * myDocFolder/configurations/conf.Name/subjects/user.ID/parameter/daily
    * myDocFolder/configurations/conf.Name/subjects/user.ID/parameter/intraday

* DateIsAvailableInFile: check if date exists in file... no se para que
* DeleteDirectory
* GetRanges(fallers []float, nonFallers []float, controlF []float, controlN []float, max float, min float, distribution []float, distributionN []float, distributionC []float, distributionCN []float, ranges []float):
    1. Find the min and max of [fallers, nonFallers]
    2. distCnt = max(len(fallers), len(nonFallers)) +1 /2. distCnt >= 3 always
    3. len(ranges), len(distr), len(distrN), len(distrC), len(distrCN) = distCnt
    4. Check if any item in [fallers, nonFallers, controlF, controlN] is <= any item in [ranges] (so 4 loops). If so, increase [distribution, distributionN, distributionC, distributionCN] (respectively) in "ranges"'s index, terminate that loop.

* GetStats(arr []float, expectation float, mean float, variance float, stdDev float, stdErr float, median float): use functions from math module to get these stats by reference.
* DeleteTooShortWalkPeriods(cleanGaitMinTime int, cuttings int) bool: remove rawGait.Strides elements according to a certain formula
    * CANDIDATE for class GaitData
    * ALGORITHM check original
* RemoveHighestLowest(removeHighestLowest float) bool:
    1. if rawGait.strides == null then return false
    2. noToRemove=(len(rawGait.strides)+1) *0.01 * removeHighestLowest * 2
    3. Alternate between RemoveLowestStride(rawGait.Strides) and RemoveHighestStride(rawGait.Strides). Repeat noToRemoveTimes. (so execute remLowest noToRemove/2)
* RemoveHeightDifference(heightFilter float) bool:
    1. For each abs(rawGait.Strides(i).LeftHeight - rawGait.Strides(i-1)) > heightFilter
        * Mark that stride, and remove it.
    2. If no elements removed, return true
    * CANDIDATE for class GaitData
* RemoveMarkedStrides(): delete strides with stride.Remove set to true
* RemoveLowestStride(strides []Stepdata): delete element with lowest (strides(i).RightStartNext - strides(i).RightStart) to strides passed by parameter
    * CANDIDATE for class GaitData
* RemoveHighestStride(strides []Stepdata): delete element with biggest (strides(i).RightStartNext - strides(i).RightStart) to strides passed by parameter
    * CANDIDATE for class GaitData
* RemoveTooLongStrides() bool: delete elements from rawGait according to algorithm
    * CANDIDATE for class GaitData (o Gait)
* RemoveTooBigStrides() bool: delete elements from rawGait according to algorithm
    * CANDIDATE for class GaitData (o Gait)
* RemoveStep(strides []Stepdata, nr int) bool: delete stride in strides(nr). Returns false if doesn't exist


* GetFallHistory(falls []string) []string: 
    * Extracts from file
* GetParameterFromSubject(dayNr int, userName string, parameterName string) string:
    * Extracts from file
* GetStepsFromSubject(dayNr int, userName string) int: get data from user's file "configurations/conf.Name/subjects/user.ID/parameter/daily/NoOfSteps.txt"
* GetActivityFromSubject(dayNr int, userName string) int: get data from user's file "configurations/conf.Name/subjects/user.ID/parameter/daily/ActivityTime.txt"
* GetDistanceWalkedFromSubject(dayNr int, userName string) int: get data from user's file "configurations/conf.Name/subjects/user.ID/parameter/daily/DistanceWalked.txt"
* SaveFalls(userID string, falls []string): store in "data/userID/Falls.txt"
* SaveFalls2: same as above, but use email instead of userID.
* GetFallsFromSubject
* GetFRIno(name string) int: return index from array configuration.FallRiskIndex with matching FallRiskIndex.Name
* GetParaNo(name string) int: return index from array configuration.GaitParameterDef with matching GaitDef.Name
* GetColumnNo(name string) int: return index from array configuration.Columns with matching conf.Columns[i]
* GetPatternByName(name string) Pattern1: return pattern in list conf.Pattern1 with matching pattern1.Name
* CalcAllFRI():
    1. for each conf.User
        1. if user.Active...
        2. for each user.ShowFRI
            1. no = GetFrino(showFri)
            2. if found and conf.FallRiskIndex(no) exists...
            3. fri = CalcFRI(user index, showFri, destination) #destination is a []string
            4. store fri to "documents/configurations/conf.Name/subjects/user.email/parameter/daily/FRI_[conf.FallRiskIndex(no).Name] .txt"
* CalcFri
* MakeOverallRisk
* CalcDistance2
* init3x3
* gn
* DoCaliCalc
* Gauss(noOfStrides int, width int) []float

* ChangeAllFRInamesForSubjects(oldName string, newName string)
* DeleteFRIfromSubjects

* Threshold (x float, y float) bool: threshold function to detect movement
    * ALGORITHM check original
* ThresholdTop(x float) float: threshold function to filter big values
* ThresholdBottom(x float) float: threshold function to filter negative values
* ThresholdGyroMax(x float) bool: threshold function to detect big rotation
* GetIDfromName(name string) string

* GenerateHistories !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
* AddHistory
* AddPattern(pattern Pattern1): insert pattern into conf.GaitPattern1 (if one with same name didn't exist already). If inserted, add item in Forms List7 and List10
* AddFRI(fri RiskIndex): insert fri into conf.FallRiskIndex (if one with same name didn't exist already)
* FilterZeroSteps
* DeleteUnequalSteps
* GiveMeanSteps
* GetColorOfFRI
* CurrentVersion


### Private functions:
* gn_step
* residuals
* jacobian
* Gaussian_func(x float, range float) float

### GUI functions:
* StayOnTop
* RemoveFromTop

* PutConfigurationToControls
* OpenConfiguration: get config from file
* SaveConfiguration: store config to file

* RemoveItemFromList(list ListBox, name string)
* RemoveItemFromCombo(list ComboBox, name string)
* Pause(seconds float)
* CheckForUpdate() bool:
* IsFormLoaded(name string) bool
* BlockRedraw
* AddPattern(pattern Pattern1): insert pattern into conf.GaitPattern1 (if one with same name didn't exist already). If inserted, add item in Forms List7 and List10
* Status(msg string): show panel with text in msg, 

### Unused or unnecessary functions:
* GetMin(pressureArr []float, length int) float: minimum element of array "pressureArr"
* GetMax2
* AbsMittlewert(arr []float) float: creo que promedio...
* Mittlewert: same as above

* ShowChart

* RemK: remove trailing "]" from string
* IsDateStr
* ModifyCharacter
* SpaceToComma
* MakeRude(pressure float, maxPressure float, minPressure float, rudeness int) int
    1. For each i=1..rudeness
        
        i=1: 
        
            if (pressure-minPressure) <= (i/rudeness * maxPressure)
            
                merker = true
                return i-1

        2<=i<=rudeness:

            if (pressure) <= (i/rudeness * maxPressure)
            
                merker = true
                return i-1

* GetSpecialFolder

* MakeRudePress
* MakeRudeAcc
* MakeRude4Acc
* GiveXYZ(startRow int, endRow int, vertical, ml, ap float):


* ArrHasDate: check if string array contains a certain Date. boooo
* CumSum
* CumSumPart
* mat2mult: matrix product
* mat2mult2
* GetSum(arr []float) float
* FormatLineEndings
* ExtractURL
* URLencode
* URLdecode
* ParseJSON
* GetValueFromStr
* MakePathSave
* UnixToTime
* isLeapYear
* secsInMonth
* mergeFiles
* mergeFiles2
* secToTime
* WasDownloaded
* FileExistsNot
* NextSun: check when is next sunday, given a date.
* GetArrFromFile(path: str) -> []str: Returns a list of str, where each element is a line in the file.

### Pending review:
* RemoveE
* getEqualValue(cnt int, lastPos int, max int, value string, arrRight []string, flags []bool) string


* CheckMonitor
* GetVari() --> variance
