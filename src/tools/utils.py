import copy
import datetime
import math
import os
import shutil
import statistics
import string
import tkinter as tk
from tkinter import ttk
import numpy as np
import random
from scipy import linalg
from itertools import accumulate
#from src.tools.utils_data import ToolVars, toolVars as t
from src.tools import useful_fx as ufx

import src.model as m
import src.model.globalvars as g

def redim_preserve(arr: list, length: int):
    if len(arr) > length:
        arr = arr[0:length]
    elif len(arr) < length:
        lengthDiff = length - len(arr)
        arr.extend([None] * lengthDiff)

#repo (quiza)
def get_id_from_name(name: str) -> str:
    """
    Get user ID by name from global t.configuration variable.
    """
    for user in g.tool.configuration.users:
        if user.name == name:
            return user.id
    return ""

def make_time(seconds: float) -> datetime.timedelta:
    """
    Convert seconds to time
    """
    return datetime.timedelta(seconds=seconds)

#GUI
def stay_on_top():
    pass

#GUI
def remove_from_top():
    pass

def erase_configuration() -> m.ConfigurationType:
    """
    Returns a new blank ConfigurationType. REPLACE VARIABLE WITH THIS FOR SAME EFFECT
    """
    return m.ConfigurationType()

def get_user_no(name: str) -> int:
    """
    Return user INDEX by name. Is case insensitive.
    Returns -1 if not found.
    """
    name = name.lower()
    for i in range(len(g.tool.configuration.users)):
        if g.tool.configuration.users[i].name.lower() == name:
            return i
    return -1

#GUI
def show_chart():
    #TODO
    pass

def crypt(string: str) -> str:
    """
    #QoL: actually encrypt (pending), rather than return same string
    """
    return string

def get_falls(userID: str) -> list[str]:
    """
    Returns fall data from myDocuments/data/:userID/Falls.txt. If not found, returns [].
    """
    #path = f"{g.tool.myDocFolder}/data/{userID}/Falls.txt"
    path = os.path.join(g.tool.myDocFolder, "data", userID, "Falls.txt")
    content = ufx.get_arr_from_file(path)
    if not ufx.is_array_empty:
        #???
        if content[-1] == "":
            ufx.remove_from_arr(content, len(content))
    return content

    
def _is_user_in_online_list(user: m.UserType) -> bool:
    """
    Finds patient by id
    """
    for patient in g.tool.patients:
        if user.id == patient.userID:
            return True

    return False
    
def get_first_date_from_file(path: str) -> datetime.date:

    fileContent = ufx.get_str_from_file(path)
    return ufx.get_date_from_str(fileContent[0:10])

#repo
def get_rows_from_file(path: str, date: str, startRow: int, noOfRows: int) -> tuple[list[str], int]:
    """
    Returns lines as string in the first 'noOfRows' from file in 'path', that are equal to 'date' given (MM/DD/YYYY).
    Skips the first 'startRow' lines.
    Return: (lines, fromRow)
    - lines: lines that match 'date'
    - fromRow: offset of the first encountered line with matching 'date'
    """
    content = []
    fromRow = 0
    try:
        with open(path, "r") as file:
            for i in range(startRow):
                file.readline()
            for line in file:
                content.append(line)
        if not ufx.is_array_empty(content):
            #find date Column (value '0') in global configuration
            datePos = -1
            for i in range(g.tool.configuration.columns):
                if g.tool.configuration.columnType[i] == 0:
                    datePos = i
                    break

            if datePos > -1:
                filteredContent = []
                for i in range(content):
                    if len(content[i]) > 0:
                        line = content[i].split(sep=",")
                        if line[datePos:datePos+len(date)] == date:
                            if len(filteredContent) <= 0:
                                fromRow = i
                            filteredContent.append(content[i])
                #warning
                return filteredContent, fromRow
            else:
                return content, fromRow
        return [], -1


    except FileNotFoundError as err:
        print(f'get_rows_from_file - File not found. Path: {path}')


file = None

def get_day_data_from_file(path: str, lastDate: str, isOpen: bool, partly: int, partDate: str) -> tuple[list[str], str, bool, int, str]:
    """
    isOpen: by ref

    VB6: va devolviendo las líneas leídas del fichero en cada una de las llamadas

    1.Abre el archivo y salta conf.skipLines lineas.
    2.isOpen = True


    Return: (arr, lastDate, isOpen, partly, partDate)

    """
    global file
    #find date Column (value '0') in global configuration
    #What type of file, with or without a date?
    nr = 0
    end = False

    datePos = -1
    for i in range(g.tool.configuration.columns):
        if g.tool.configuration.columnType[i] == 0:
            datePos = i
            break

    if not isOpen:
        file = open(path, 'r')
        for i in range(g.tool.configuration.skipLines):
            string = modify_character(file.readline().strip())
        isOpen = True
        if datePos == -1:
            dateTime = datetime.datetime.fromtimestamp(os.path.getmtime(path))
            date = ufx.get_str_from_date(dateTime.date())
        else:
            line = string.split(",")
            date = line[datePos]
        if lastDate != "":
            if ufx.get_date_from_str(lastDate) >= ufx.get_date_from_str(date):
                file.close()
                isOpen = False
            else:
                print(path)
    
    if isOpen:
        #Bring by the end or other date
        arr = [""] * 10000
        while True:
            string = file.readline().strip()
            if string == "":
                end = True
            if string != "":
                if datePos > -1:
                    line = string.split(",")
                    if nr == 0:
                        lastDate = line[datePos]
                    if line[datePos] != lastDate:
                        if partly > 0:
                            partly = -1
                            break
                arr[nr] = string
                nr += 1
                if nr >= len(arr):
                    redim_preserve(arr, len(arr) + 10000)
                if nr >= 360000:
                    partly += 1
                    if date != "":
                        partDate = date
                    break
            if end:
                break
        
        if end:
            file.close()
            file = None
            isOpen = False
            if datePos == -1:
                if date != "":
                    lastDate = date
                else:
                    dateTime = datetime.datetime.fromtimestamp(os.path.getmtime(path))
                    lastDate = ufx.get_str_from_date(dateTime.date())
            if partly > 0:
                partly = -1
        redim_preserve(arr, nr)
        return (arr, lastDate, isOpen, partly, partDate)
    return ("", lastDate, isOpen, partly, partDate)

fileWiisel = None

def get_day_data_from_wiisel(arr: list[str], path: str, lastDate: str, isOpen: bool, partly: int, partDate: str) -> tuple[str, bool, int, str]:
    """
    Return: (lastDate, isOpen, partly, partDate)
    """
    global fileWiisel
    #find date Column (value '0') in global configuration
    #What type of file, with or without a date?
    nr = 0
    end = False

    arr = []

    if not isOpen:
        sdate, filePath = get_next_date_file2(path, lastDate)
        if len(filePath) > 0:
            lastDate = f"{lastDate[5:5+2]}/{lastDate[-2:]}/{lastDate[0:4]}"
            fileWiisel = open(path, 'r')
            for i in range(len(g.tool.configuration.skipLines)):
                string = fileWiisel.readline().strip()
            if string != "":
                isOpen = True
            else:
                fileWiisel.close()
                fileWiisel = None
                isOpen = False
            date = lastDate
            partly = 0
    
    if isOpen:
        #Bring by the end or other date
        arr = [""] * 10000
        while True:
            string = fileWiisel.readline().strip()
            if string == "":
                end = True
            if string != "":
                arr[nr] = string
                nr += 1
                if nr >= len(arr):
                    redim_preserve(arr, len(arr)+10000)
                if nr >= 260000:
                    partly += 1
                    if len(date) > 0:
                        partDate = date
                    break
            if end:
                break
        
        if end:
            fileWiisel.close()
            isOpen = False
            if partly > 0:
                partly = -1
        
        redim_preserve(arr, nr)
        return (lastDate, isOpen, partly, partDate)
    return (lastDate, isOpen, partly, partDate)


#repo
def get_next_date_file2(path: str, sdate: str) -> str:
    """
    Return: (sdate: str, str), sdate was by ref.
    """
    list2 = []

    if len(sdate) > 0:
        date = ufx.get_date_from_str(sdate[0:10])
    list = ufx.get_file_list_from_path(path, "txt")
    if not ufx.is_array_empty(list):
        for i in range(len(list)):
            if "reg_" in list[i]:
                if "reg_left" not in list[i] and "reg_right" not in list[i]:
                    list2.append(list[i].replace("..", "."))
        if len(list2) > 0:
            _sort_dates2(list2)

            if len(sdate) == 0:
                res = list2[0] #"reg_" & Format$(Day(l_Dates(0)), "00") & "-" & Format$(Month(l_Dates(0)), "00") & "-" & Format$(Year(l_Dates(0)), "0000") & ".txt"
                dstr1 = list2[0].replace(".txt", "")
                dstr1 = dstr1[-10:].replace("-", "/")
                dstr1Components = dstr1.split("/")
                date1 = datetime.date(int(dstr1Components[2]), int(dstr1Components[1]), int(dstr1Components[0]))
                sdate = ufx.get_str_from_date(date1)
                return (sdate, res)
            else:
                sdate = ""
                for i in range(len(list2)):
                    dstr1 = list2[0].replace(".txt", "")
                    dstr1 = dstr1[-10:].replace("-", "/")
                    dstr1Components = dstr1.split("/")
                    date1 = datetime.date(int(dstr1Components[2]), int(dstr1Components[1]), int(dstr1Components[0]))
                    if date1 > date:
                        res = list2[i]
                        sdate = ufx.get_str_from_date(date1)
                        return (sdate, res)
    return ("", "")

#repo
def _sort_dates2(dates: list[str]):
    """
    Sort string dates from least to most recent. dates is BY ref.
    """
    for i in range(len(dates)):
        for j in range(0, len(dates)-1):
            strCurr = dates[j].replace(".txt", "")
            strCurr = strCurr[-10:]
            strCurr = strCurr.replace("-", "/")
            componentsCurr = strCurr.split("/")
            dateCurr = datetime.date(int(componentsCurr[2]), int(componentsCurr[1]), int(componentsCurr[0]))
            strNext = dates[j].replace(".txt", "")
            strNext = strNext[-10:]
            strNext = strNext.replace("-", "/")
            componentsNext = strNext.split("/")
            dateNext = datetime.date(int(componentsNext[2]), int(componentsNext[1]), int(componentsNext[0]))
            if dateCurr > dateNext:
                string = dates[j+1]
                dates[j+1] = dates[j]
                dates[j] = string

def modify_character(string: str) -> str:
    """
    Make 'string' safe according to configuration (configuration.<attribute>). Attribute can be:

    lineSeparator (NOT IMPLEMENTED):
    - 'CR' (10) -> 'CRLF'
    - 'LF' (13) -> 'CRLF'

    decimalSeparator:
    - ',' (44) -> '.'
    
    columnSeparator:
    - 'TAB' (9) -> ','
    - ' ' (32) -> ','
    """
    if string != "":
        if g.tool.configuration.lineSeparator == 10:
            string = string.replace(chr(10), "\n")
        #warning: controll crlf
        if g.tool.configuration.decimalSeparator == 44:
            #ord(' ') -> 32
            #chr(32) -> ' '
            string = string.replace(chr(44), '.')
        if g.tool.configuration.columnSeparator == 9:
            string = string.replace(chr(9), ',')
        elif g.tool.configuration.columnSeparator == 32:
            string = string.replace(chr(32), ',')
        
    return string

def get_min2(col: int) -> float:
    """
    Returns smallest value of g_rawGait.columnData[col]
    """
    return min(g.tool.rawGait.columnData[col])

def get_max(arr: list[float], length: int, ubnd: int) -> float:
    """
    
    """
    res = 0.0
    if ubnd >= length:
        #warning: +0 +1, could be +1 +0 
        for i in range(ubnd-length, ubnd+1):
            if arr[i] > res:
                if i < ubnd:
                    if arr[i-1] > 1 or arr[i+1] > 1:
                        res = arr[i]
    else:
        #warning... yo que se ya
        for i in range(ubnd+1):
            if arr[i] > res:
                if i > 0:
                    if i < ubnd:
                        if arr[i-1] > 1 or arr[i+1] > 1:
                            res = arr[i]
    return res

def get_max2(col: int, length: int, ubnd: int) -> float:
    res = 0.0
    if ubnd >= length:
        for i in range(ubnd-length, ubnd+1):
            if g.tool.rawGait.columnData[col][i] > res:
                if i > 0:
                    if i < ubnd:
                        if g.tool.rawGait.columnData[col][i-1] > 1 or g.tool.rawGait.columnData[col][i+1] > 1:
                            res = g.tool.rawGait.columnData[col][i]
    else:
        for i in range(ubnd+1):
            if g.tool.rawGait.columnData[col][i] > res:
                if i > 0:
                    if i < ubnd:
                        if g.tool.rawGait.columnData[col][i-1] > 1 or g.tool.rawGait.columnData[col][i+1] > 1:
                            res = g.tool.rawGait.columnData[col][i]
    return res

def make_rude3_acc(lastRude: bool, acc1: float, acc2: float, acc3: float, rudeness: int) -> bool:
    """
    Magic: 11
    """
    if lastRude:
        if acc1 < 11 and acc2 < 11 and acc3 < 11:
            return False
        else:
            return True
    else:
        if acc1 > 11 and acc2 > 11 and acc3 > 11:
            return True
        else:
            return False

def make_rude_acc2(lastRude: bool, acc1: float, acc2: float, acc3: float, acc4: float, acc5: float,
 acc6: float, acc7: float, acc8: float, acc9: float, acc10: float, maxAcc: float) -> bool:
    if maxAcc < 5:
        maxAcc = 10
    if lastRude:
        if all([x < maxAcc*0.1 for x in [acc1, acc2, acc3, acc4, acc5, acc6, acc7, acc8, acc9, acc10]]):
            return False
        else:
            return True
    else:
        if acc1 > maxAcc*0.1:
            return True
        else:
            return False

#repo
def make_user_paths(id: string):
    """
    Create all paths for user with 'id'. If a directory already exists, nothing happens.
    """
    paths = [
        [g.tool.myDocFolder, "configurations", g.tool.configuration.name],
        [g.tool.myDocFolder, "configurations", g.tool.configuration.name, "subjects"],
        [g.tool.myDocFolder, "configurations", g.tool.configuration.name, "subjects", id],
        [g.tool.myDocFolder, "configurations", g.tool.configuration.name, "subjects", id, "parameter"],
        [g.tool.myDocFolder, "configurations", g.tool.configuration.name, "subjects", id, "parameter", "daily"],
        [g.tool.myDocFolder, "configurations", g.tool.configuration.name, "subjects", id, "parameter", "intraday"]
    ]
    for pathComponents in paths:
        osPath = os.path.join(*pathComponents)
        if not ufx.folder_exists(osPath):
            os.makedirs(osPath, mode=777)

#repo
def delete_directory(dirName: str):
    """
    Delete this directory and all the files it contains.
    """
    shutil.rmtree(dirName, ignore_errors=True)

#repo
def date_is_available_in_file(searchDate: datetime.date, path: str) -> bool:
    """
    If configuration.columnType (for date) is set (== 0), check if file content contains 'searchDate'.
    Otherwise, check if lastModified date is equal to 'searchDate'
    """
    dateIsAvailable = False
    #find date Column (value '0') in global configuration
    datePos = -1
    for i in range(g.tool.configuration.columns):
        if g.tool.configuration.columnType[i] == 0:
            datePos = i
            break
    if datePos > -1:
        strDate = ufx.get_str_from_date(searchDate)
        fileContentStr = ufx.get_str_from_file(path)
        if strDate in fileContentStr:
            dateIsAvailable = True
    else:
        lastModifiedUnix = os.path.getmtime(path)
        lastModifiedDatetime = datetime.datetime.fromtimestamp(lastModifiedUnix)
        if searchDate == lastModifiedDatetime.date():
            dateIsAvailable = True
    return dateIsAvailable

def get_ranges(fallers: list[float], nonFallers: list[float], controlF: list[float], controlN: list[float], maximum: float, minimum: float,
distribution: list[float], distributionN: list[float], distributionC: list[float], distributionCN: list[float], ranges: list[float]) -> tuple[float, float]:
    """
    ranges, distribution, distributionN, distributionC, distributionCN are passed by reference.
    Input arguments maximum, minimum are removed, instead are returned.

    1. Find the min and max of [fallers, nonFallers]
    2. distCnt = max(len(fallers), len(nonFallers)) +1 /2. distCnt >= 3 always
    3. len(ranges), len(distr), len(distrN), len(distrC), len(distrCN) = distCnt
    4. Check if any item in [fallers, nonFallers, controlF, controlN] is <= any item in [ranges] (so 4 loops). 
    If so, increase [distribution, distributionN, distributionC, distributionCN] (respectively) in "ranges"'s index, terminate that loop.

    Return:
    - overall maximum
    - overall minimum
    """
    overall_min = min(fallers + nonFallers)
    overall_max = max(fallers + nonFallers)

    distCnt = max(len(fallers), len(nonFallers)) + 1 / 2
    if distCnt < 3:
        distCnt = 3
    
    ranges = []
    for i in range(distCnt):
        if i == 0:
            ranges.append(overall_min + (overall_max - overall_min) / distCnt)
        elif i == distCnt-1:
            ranges.append(overall_max)
        else:
            ranges.append(ranges[i-1] + (overall_max - overall_min)  / distCnt)
    
    distribution = len(distCnt) * [0]
    distributionN = len(distCnt) * [0]
    distributionC = len(distCnt) * [0]
    distributionN = len(distCnt) * [0]

    for i in range(len(fallers)):
        for j in range(ranges):
            if fallers[i] <= ranges[j]:
                distribution[j] += 1

    for i in range(len(nonFallers)):
        for j in range(ranges):
            if nonFallers[i] <= ranges[j]:
                distributionN[j] += 1

    for i in range(len(controlF)):
        for j in range(ranges):
            if controlF[i] <= ranges[j]:
                distributionC[j] += 1

    for i in range(len(controlN)):
        for j in range(ranges):
            if controlN[i] <= ranges[j]:
                distributionCN[j] += 1

    return (overall_max, overall_min)

def get_stats(arr: list[float]) -> tuple[float]:
    """
    Return:
    - expectation (NOT IMPLEMENTED, always 0)
    - mean
    - stdDev
    - stdErr
    - variance
    - median
    """
    expectation = 0
    mean = statistics.mean(arr)
    stdDev = statistics.stdev(arr) if len(arr) > 1 else 0.0
    stdErr = stdDev / len(arr)
    variance = statistics.variance(arr) if len(arr) > 1 else 0.0
    median = statistics.median(arr)

    return (expectation, mean, stdDev, stdErr, variance, median)

def delete_too_short_walkperiods(cleanGaitMinTime: int, cuttings: int) -> bool:
    """
    Removes strides in global "rawGait" that accomplish a certain criteria
    """
    begin = False
    start = 0

    currentStrides = copy.deepcopy(g.tool.rawGait.strides)
    if begin:
        for i in range(g.tool.rawGait):
            currentStrides[i].remove = True
            if currentStrides[i+1].rightStart - currentStrides[i].rightStart < 2:
                if not begin:
                    begin = True
                    start = i
            else:
                if begin:
                    if currentStrides[i].rightStart - currentStrides[start].rightStart > cleanGaitMinTime:
                        for j in range(start+cuttings,i-cuttings+1):
                            currentStrides[j].remove = False
                    begin = False
        #if at the end mode is on good gait
        if begin:
            if currentStrides[len(currentStrides)].rightStart - currentStrides[start].rightStart > cleanGaitMinTime:
                for j in range(start+cuttings, len(currentStrides)-cuttings+1):
                    currentStrides[j].remove = False
        
        remainingStrides = copy.deepcopy(currentStrides)
        numToRemove = 0
        for i in range(len(currentStrides)+1):
            if not currentStrides[i].remove:
                remainingStrides.strides[numToRemove] = currentStrides.strides[i]
                numToRemove += 1
            
        if numToRemove != 0:
            remainingStrides = remainingStrides[0:numToRemove]
        else:
            return False
        g.tool.rawGait.strides = remainingStrides
        return True
    else:
        return False

def remove_lowest_stride(strides: list[m.RawStepdata]):
    """
    Removes the stride with lowest "rightStartNext - rightStart"
    """
    for i in range(strides):
        if i == 0:
            low = strides[i].rightStartNext - strides[i].rightStart
            nr = 0
        else:
            if strides[i].rightStartNext - strides[i].rightStart < low:
                low = strides[i].rightStartNext - strides[i].rightStart
                nr = i
    
    strides.pop(nr)


def remove_highest_stride(strides: list[m.RawStepdata]):
    """
    Removes the stride with highest "rightStartNext - rightStart"
    """
    for i in range(strides):
        if i == 0:
            high = strides[i].rightStartNext - strides[i].rightStart
            nr = 0
        else:
            if strides[i].rightStartNext - strides[i].rightStart > high:
                high = strides[i].rightStartNext - strides[i].rightStart
                nr = i
    
    strides.pop(nr)

def remove_highest_lowest(removeHighestLowest: float) -> bool:
    """
    """
    switch = False
    res = False
    if len(g.tool.rawGait.strides) != 0:
        noToRemove = (len(g.tool.rawGait.strides)) * 0.01 * removeHighestLowest * 2
        res = True
        for i in range(1, noToRemove+1):
            if len(g.tool.rawGait.strides) > 0:
                if switch:
                    remove_lowest_stride(g.tool.rawGait.strides)
                    switch = not switch
                else:
                    remove_highest_stride(g.tool.rawGait.strides)
                    switch = not switch
            else:
                break
    return res 

def remove_marked_strides():
    """
    Removes strides in global rawGait marked previously (.remove == True)
    """
    strides = []
    for stride in g.tool.rawGait.strides:
        if not stride.remove:
            strides.append(stride)
    g.tool.rawGait.strides = strides

def remove_height_difference(heightFilter: float) -> bool:
    """
    For each stride in global rawGait, mark it if not abs()... and remove it.
    Return True if none were been removed.
    """
    for i, stride in enumerate(g.tool.rawGait.strides):
        if i == 0:
            pass
        else:
            valToCompare = abs(stride.leftHeight - g.tool.rawGait.strides[i-1].leftHeight)
            if abs(valToCompare) > heightFilter:
                g.tool.rawGait.strides[i].remove = True

    remove_marked_strides()

#GUI
def remove_item_from_list(listt: tk.Listbox, name: str):
    """
    Remove element by name from listbox. IF not found, does nothing.
    """
    for i in range(listt.size()):
        if name == listt.get(i):
            listt.delete(i)
            return
    return

#GUI
def remove_item_from_combo(combo: ttk.Combobox, name: str):
    """
    Remove element by name from combobox. IF not found, does nothing.
    """
    for i in range(len(combo["values"])):
        if name == combo.get(i):
            combo.delete(i)
            return
    return

def remove_E(string: str) -> float:
    """Returns the value of a string with exponential format xxxe+yyy"""
    string = string.lower()
    string = string.replace(",", ".")
    return float(string)

def get_fall_history(falls: list[str]) -> list[str]:
    """
    Returns a "historic" of ocurrences of falls in the given 'falls' list (format 'MM/DD/YYYY HH:MM:SS)
    """
    
    someDict = {}
    if not ufx.is_array_empty(falls):
        for i in range(falls):
            #get date from line with format "Falls.txt"
            dateToSearch = falls[i][0:10]
            if not dateToSearch in someDict.keys():
                someDict[dateToSearch] = 1
            else:
                someDict[dateToSearch] += 1
        
        #contains all entries in someDict, in format "date,amount"
        hist = []
        for key in someDict.keys():
            hist.append(f"{key},{someDict[key]}")
        
        hist.sort()

        startDate = ufx.get_date_from_str(hist[0])
        endDate = ufx.get_date_from_str(hist[-1])

        #fill empty values
        while startDate != endDate:
            if startDate not in someDict.keys():
                hist.append(f"{ufx.get_str_from_date(startDate)},0")
            startDate = startDate + datetime.timedelta(days=1)
        
        hist.sort()
        return hist

#repo
def get_parameter_from_subject(dayNr: int, username: str, parameterName: str) -> float:
    """
    Obtain the average of a parameter 'parameterName' with measures of a user 'username' from all dates where the number of days between
    (file.lastProcessedDate - conf.user.lastProcessedDate) is less than 'dayNr'.

    File searched is "myDoc/configurations/conf.Name/subjects/user.ID/parameter/daily/{parameterName}.txt"

    Returns 0 if not found.

    NOTE: used to be returned as a string, with 2 decimals.
    """
    if ufx.is_type_variation(parameterName):
        path = os.path.join(g.tool.myDocFolder, "configurations", g.tool.configuration.name, "subjects", get_id_from_name(username), "parameter", "daily", f"{parameterName[0:-10]}.txt")
    else:
        path = os.path.join(g.tool.myDocFolder, "configurations", g.tool.configuration.name, "subjects", get_id_from_name(username), "parameter", "daily", f"{parameterName}.txt")
    fileContent = ufx.get_arr_from_file(path)
    
    if not ufx.is_array_empty(fileContent):
        count = 0
        sum = 0
        lastDate = ufx.get_date_from_str(g.tool.configuration.users[get_user_no(username)].lastProcessedDate)
        for i in range(len(fileContent)-1, 0-1, -1):
            line = fileContent[i].split(",")
            date = ufx.get_date_from_str(line[0])
            if abs((date - lastDate).days) <= dayNr:
                count += 1
                if ufx.is_type_variation(parameterName):
                    sum += float(line[2])
                else:
                    sum += float(line[1])
        if count > 0:
            return float(round(sum / count, ndigits=2))
        
    return 0.0

#repo
def get_steps_from_subject(dayNr: int, username: str) -> int:
    """
    Obtain the total of steps of a user 'username' from all dates where the number of days between
    (file.lastProcessedDate - conf.user.lastProcessedDate) is less than 'dayNr'.

    File searched is "myDoc/configurations/conf.Name/subjects/user.ID/parameter/daily/NoOfSteps.txt"
    """
    path = os.path.join(g.tool.myDocFolder, "configurations", g.tool.configuration.name, "subjects", get_id_from_name(username), "parameter", "daily", "NoOfSteps.txt")
    fileContent = ufx.get_arr_from_file(path)
    count = 0
    if not ufx.is_array_empty(fileContent):
        lastDate = ufx.get_date_from_str(g.tool.configuration.users[get_user_no(username)].lastProcessedDate)
        for i in range(len(fileContent)-1, 0-1, -1):
            line = fileContent[i].split(",")
            date = ufx.get_date_from_str(line[0])
            if abs((date - lastDate).days) <= dayNr:
                count += int(line[1])
    return count

#repo
def get_activity_from_subject(dayNr: int, username: str) -> float:
    """
    Obtain the total of activity of a user 'username' from all dates where the number of days between
    (file.lastProcessedDate - conf.user.lastProcessedDate) is less than 'dayNr'.

    File searched is "myDoc/configurations/conf.Name/subjects/user.ID/parameter/daily/ActivityTime.txt"
    """
    path = os.path.join(g.tool.myDocFolder, "configurations", g.tool.configuration.name, "subjects", get_id_from_name(username), "parameter", "daily", "ActivityTime.txt")
    fileContent = ufx.get_arr_from_file(path)
    count = 0
    if not ufx.is_array_empty(fileContent):
        lastDate = ufx.get_date_from_str(g.tool.configuration.users[get_user_no(username)].lastProcessedDate)
        for i in range(len(fileContent)-1, 0-1, -1):
            line = fileContent[i].split(",")
            date = ufx.get_date_from_str(line[0])
            if abs((date - lastDate).days) <= dayNr:
                count += float(ufx.kzp(line[1]))
    return count

#repo
def get_distance_walked_from_subject(dayNr: int, username: str) -> float:
    """
    Obtain the total of distance walked of a user 'username' from all dates where the number of days between
    (file.lastProcessedDate - conf.user.lastProcessedDate) is less than 'dayNr'.

    File searched is "myDoc/configurations/conf.Name/subjects/user.ID/parameter/daily/DistanceWalked.txt"
    """
    path = os.path.join(g.tool.myDocFolder, "configurations", g.tool.configuration.name, "subjects", get_id_from_name(username), "parameter", "daily", "DistanceWalked.txt")
    fileContent = ufx.get_arr_from_file(path)
    count = 0
    if not ufx.is_array_empty(fileContent):
        lastDate = ufx.get_date_from_str(g.tool.configuration.users[get_user_no(username)].lastProcessedDate)
        for i in range(len(fileContent)-1, 0-1, -1):
            line = fileContent[i].split(",")
            date = ufx.get_date_from_str(line[0])
            if abs((date - lastDate).days) <= dayNr:
                count += float(ufx.kzp(line[1]))
    return count

#repo
def save_falls(userID: str, falls: list[str]):
    """
    OVERWRITE falls to user with id 'userID'.

    File written is "myDoc/data/{userID}/Falls.txt"
    """
    path = os.path.join(g.tool.myDocFolder, "data", userID, "Falls.txt")
    ufx.save_arr_to_file(path, falls)

#repo
def save_falls2(email: str, falls: list[str]):
    """
    OVERWRITE falls to user with email 'email'.

    File written is "myDoc/data/{email}/Falls.txt"
    """
    path = os.path.join(g.tool.myDocFolder, "data", email, "Falls.txt")
    ufx.save_arr_to_file(path, falls)

#repo
def get_falls_from_subject(dayNr: int, username: str) -> int:
    """
    Return total of falls from user in global t.config.users.
    """
    falls = g.tool.configuration.users[get_user_no(username)].falls
    count = 0
    if not ufx.is_array_empty(falls):
        #WARNING: lastProcessedDate is not a string
        lastDate = ufx.get_date_from_str(g.tool.configuration.users[get_user_no(username)].lastProcessedDate)
        for i in range(falls):
            if falls[i] != "":
                date = ufx.get_date_from_str(falls[i][0:10])
                #WARNING
                if (date - lastDate).days > -1 and (date - lastDate).days <= dayNr:
                    count += 1
    return count

def get_FRI_no(name: str) -> int:
    """
    Return index of FRI in t.configuration.fallriskindex list. Search by 'name'.
    Return -1 if not found.
    """
    for i, fri in enumerate(g.tool.configuration.fallRiskIndex):
        if fri.name == name:
            return i
    return -1

def get_para_no(name: str) -> int:
    """
    Return index of GaitParameterDef in t.configuration.gaitParameterDef list. Search by 'name'.
    Return -1 if not found.
    """
    for i, gaitParam in enumerate(g.tool.configuration.gaitParameterDef):
        if gaitParam.name == name:
            return i
    return -1

def get_column_no(name: str) -> int:
    """
    Return index of Columns in t.configuration.columns list.
    Return -1 if not found.
    """
    for i, column in enumerate(g.tool.configuration.columns):
        if column == name:
            return i
    return -1

def get_pattern_by_name(name: str) -> m.Pattern1:
    """
    Return Pattern1 in t.configuration.gaitPattern1 list. Search by 'name'.
    Return empty Pattern1 if not found.
    """
    for pattern1 in g.tool.configuration.gaitPattern1:
        if pattern1.name == name:
            return pattern1
    return m.Pattern1()

# def make_overall_risk(components: list[m.Component], collections: dict[str, list[str]], redStart: float) -> list[str]:
#     """
#     Collections: {"i": ["fecha1,FRIvalue", "fecha2,FRIvalue2"...]}
#     dictDateFRI: {"fecha1": ["FRIvalue1", "FRIvalue2"...]}
#     collections was l_All
#     dictDateFRI es un LIST[dict[str, list[str]]] YO QUE SE QUE TIENE DENTRO
#     """
#     coll = [[]] * len(collections) #list[list[tuple(str, str)]]
#     fri = []
#     if len(collections) > 0:
#         #WARNING
#         for i, key in enumerate(collections.keys()):
#             arr = collections[key]
#             for line in arr:
#                 if line != "":
#                     lineSplit = line.split(",")
#                     newEntry = (lineSplit[0], lineSplit[1]) #("date1", "friValue1")
#                     coll[i].append(newEntry)
            
#         #Is the respective date available in all of them?
#         for i in range(len(coll[0])):
#             marker = False
#             for j in range(len(coll)):
#                 arrToSearchInto = coll[j] #each array element of coll
#                 for pair in arrToSearchInto:
#                     if pair[0] == coll[0][i][0]: #coll[0][i][0] was l_Coll[0].key[i]
#                         marker = True
#             if not marker:
#                 #Calculate and save
#                 value = 0
#                 friToInsert = 0.0
#                 for j in range(len(coll)):
#                     if float(coll[j][i][1]) > redStart:
#                         if float(coll[j][i][1]) > value:
#                             if components[j].impact > value:
#                                 value = components[j].impact
#                     friToInsert = friToInsert + float(coll[j][i][1]) * components[j].weight / 100
#                 if friToInsert < value:
#                     friToInsert = value
#                 friToInsertFormatted = f"{coll[0][i][0]},{ufx.kzp(str(round(friToInsert, ndigits=2)))}" #"dateX, friValueY"
#                 fri.append(friToInsertFormatted)
#     return fri

def make_overall_risk(components: list[m.Component], all: list[list[str]], redStart: float) -> list[str]:
    """
    coll: list[dict]
    """
    fri = list()

    if len(all) > 0:
        coll = list()

        for dateAndValueArr in all: #len(components) iterations in loop
            newCollDict = dict()
            for dateAndValue in dateAndValueArr: #len(contentOfFile) iterations in loop
                if dateAndValue != "":
                    line = dateAndValue.split(",")
                    newCollDict[line[0]] = line[1]
            coll.append(newCollDict)
        
        #Is the respective date available in all of them?
        for key in coll[0].keys():
            marker = False

            for j, dictDateAndValues in enumerate(coll):
                if key not in dictDateAndValues.keys():
                    marker = True
                    break
            if not marker:
                fri.append("0")

                value = 0.0
                for j, dictDateAndValues in enumerate(coll):
                    if float(dictDateAndValues[key]) > redStart:
                        if float(dictDateAndValues[key]) > value:
                            if components[j].impact > value:
                                value = components[j].impact
                    
                    newFri = float(ufx.kzp(fri[-1])) + float(dictDateAndValues[key]) * components[j].weight / 100
                    fri[-1] = str(newFri)
                if float(fri[-1]) < value:
                    fri[-1] = str(value)
                fri[-1] = f'{key},{ufx.kzp(str(round(float(fri[-1]), ndigits=2)))}'
        
    return fri

def calc_FRI(userNo: int, friName: str, details: list[str]) -> list[str]:

    friNo = get_FRI_no(friName)
    if friNo > -1:
        if len(g.tool.configuration.fallRiskIndex)-1 >= friNo:
            all = list()
            #details = list()

            for i, component in enumerate(g.tool.configuration.fallRiskIndex[friNo].components):
                pattern = get_pattern_by_name(g.tool.configuration.fallRiskIndex[friNo].components[i].elementName)
                if ufx.is_type_variation(pattern.formula[0]):
                    #path = os.path.join(g.tool.myDocFolder, "configurations", g.tool.configuration.name, "subjects", ufx.save_path(g.tool.configuration.users[userNo].email), "parameter", "daily", f"{pattern.formula[0][0:-10]}.txt")
                    path = os.path.join(g.tool.myDocFolder, "configurations", g.tool.configuration.name, "subjects", ufx.save_path(g.tool.configuration.users[userNo].id), "parameter", "daily", f"{pattern.formula[0][0:-10]}.txt")
                else:
                    #path = os.path.join(g.tool.myDocFolder, "configurations", g.tool.configuration.name, "subjects", ufx.save_path(g.tool.configuration.users[userNo].email), "parameter", "daily", f"{pattern.formula[0]}.txt")
                    path = os.path.join(g.tool.myDocFolder, "configurations", g.tool.configuration.name, "subjects", ufx.save_path(g.tool.configuration.users[userNo].id), "parameter", "daily", f"{pattern.formula[0]}.txt")
                fileContent = ufx.get_arr_from_file(path)
                if len(fileContent) > 0:
                    fullRisk = float(ufx.kzp(pattern.formula[1]))
                    noRisk = float(ufx.kzp(pattern.formula[3]))
                    values = list()
                    for line in fileContent:
                        if line != "":
                            lineArr = line.split(",")
                            if ufx.is_type_variation(pattern.formula[0]):
                                value = (float(ufx.kzp(lineArr[2])) - noRisk) / (fullRisk - noRisk) * 100
                            else:
                                value = (float(ufx.kzp(lineArr[1])) - noRisk) / (fullRisk - noRisk) * 100
                            value = 0 if value < 0 else value
                            value = 100 if value > 100 else value
                            values.append(f'{lineArr[0]},{ufx.kzp(str(value)).strip()}')
                    all.append(values)
                    details.append(f'{component.elementName}|{component.weight}|{ufx.kzp(str(round(value, ndigits=2))).strip()}')
            return make_overall_risk(g.tool.configuration.fallRiskIndex[friNo].components, all, g.tool.configuration.fallRiskIndex[friNo].redStart)
    return list()


#repo
def calc_all_FRI() -> None:
    """
    Calculate FRI of every active user, for each of it's associated FRI (user.showFRI).

    It is finally saved in each corresponding file.

    File locations: "myDoc/configurations/{conf.name}/subjects/email/parameter/daily/FRI_{fri.name}.txt"
    """
    for i in range(len(g.tool.configuration.users)):
        if g.tool.configuration.users[i].active:
            for j in range(len(g.tool.configuration.users[i].showFRI)):
                no = get_FRI_no(g.tool.configuration.users[i].showFRI[j])
                if no > -1:
                    fri = calc_FRI(i, g.tool.configuration.users[i].showFRI[j], "ALGOOOOOOOOOOOOOO")
                    if len(fri) > 0:
                        path = os.path.join(g.tool.myDocFolder, "configurations", g.tool.configuration.name, "subjects", ufx.save_path(g.tool.configuration.users[i].email), "parameter", "daily", f"FRI_{g.tool.configuration.fallRiskIndex[no].name}.txt")
                        ufx.save_arr_to_file(path, fri)


def cum_sum(arr: list[float]) -> list[float]:
    """
    Cumulative sum of all array
    """
    return list(accumulate(arr))

def cum_sum_part(arr: list[float], pos: int) -> list[float]:
    """
    Cumulative sum of all array up to pos
    """
    return list(accumulate(arr[0:pos+1]))

def _mat2_mult(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    """
    Matrix multiplication x * y = Z.
    Return Z
    """

    return np.matmul(x, y)
    

def _mat2_mult2(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    """
    Used to multiply matrix X by arr Y. Alias to mat2mult.

    Used to work only with Y a 1-dimensional array
    """
    return _mat2_mult(x, y)

def _init3x3(a1: float, a2: float, a3: float, a4: float, a5: float, a6: float, a7: float, a8: float, a9: float) -> np.ndarray:
    """
    Both input "x" and res are the same matrix [[a1,a2...]]
    Returned: 

    a1 a2 a3

    a4 a5 a6

    a7 a8 a9
    """
    res = np.zeros((3,3))
    res[0] = [a1, a2, a3]
    res[1] = [a4,a5,a6]
    res[2] = [a7,a8,a9]
    return res

def calc_distance2(type: int, startRow: int, endRow: int) -> float:
    """
    

    type:
    - 0 = left
    - 1 = right
    """
    #type: 0=left; 1=right
    
    #define pi
    pi = math.pi

    #WARNING
    L1 = endRow - startRow #+ 1
    gyrx = np.zeros(L1)
    gyry = np.zeros(L1)
    gyrz = np.zeros(L1)
    ax = np.zeros(L1)
    ay = np.zeros(L1)
    az = np.zeros(L1)

    k = 0
    #WARNING
    for il in range(startRow, endRow+1):
        if type == 0: #left
            gyrx[k] = g.tool.rawGait.columnData[g.tool.unknownData.gX_columnL][il] - g.tool.rawGait.calibrationData.CaliHxL
            gyry[k] = g.tool.rawGait.columnData[g.tool.unknownData.gY_columnL][il] - g.tool.rawGait.calibrationData.CaliHyL
            gyrz[k] = g.tool.rawGait.columnData[g.tool.unknownData.gZ_columnL][il] - g.tool.rawGait.calibrationData.CaliHzL
            ax[k] = (g.tool.rawGait.columnData[g.tool.unknownData.aX_columnL][il] - g.tool.rawGait.calibrationData.CaliBxL) * g.tool.rawGait.calibrationData.CaliKxL
            ay[k] = (g.tool.rawGait.columnData[g.tool.unknownData.aY_columnL][il] - g.tool.rawGait.calibrationData.CaliByL) * g.tool.rawGait.calibrationData.CaliKyL
            az[k] = (g.tool.rawGait.columnData[g.tool.unknownData.aZ_columnL][il] - g.tool.rawGait.calibrationData.CaliBzL) * g.tool.rawGait.calibrationData.CaliKzL
        elif type == 1: #right
            gyrx[k] = g.tool.rawGait.columnData[g.tool.unknownData.gX_columnR][il] - g.tool.rawGait.calibrationData.CaliHxR
            gyry[k] = g.tool.rawGait.columnData[g.tool.unknownData.gY_columnR][il] - g.tool.rawGait.calibrationData.CaliHyR
            gyrz[k] = g.tool.rawGait.columnData[g.tool.unknownData.gZ_columnR][il] - g.tool.rawGait.calibrationData.CaliHzR
            ax[k] = (g.tool.rawGait.columnData[g.tool.unknownData.aX_columnR][il] - g.tool.rawGait.calibrationData.CaliBxR) * g.tool.rawGait.calibrationData.CaliKxR
            ay[k] = (g.tool.rawGait.columnData[g.tool.unknownData.aY_columnR][il] - g.tool.rawGait.calibrationData.CaliByR) * g.tool.rawGait.calibrationData.CaliKyR
            az[k] = (g.tool.rawGait.columnData[g.tool.unknownData.aZ_columnR][il] - g.tool.rawGait.calibrationData.CaliBzR) * g.tool.rawGait.calibrationData.CaliKzR
        k += 1
    
    if az[0] > 0:
        angx0 = math.atan2(ay[0], az[0])
        angy0 = math.atan2(-ax[0], az[1])
    else:
        return 0.0
    
    #Euler rotation matrixes
    Rx = _init3x3(1, 0, 0, 0, math.cos(angx0), -math.sin(angx0), 0, math.sin(angx0), math.cos(angx0))
    Ry = _init3x3(math.cos(angy0), 0, math.sin(angy0), 0, 1, 0, -math.sin(angy0), 0, math.cos(angy0))

    #works only with 2d (in vb6... not in python)
    R = _mat2_mult(Rx, Ry)

    #30ms time interval between samples
    dt = 0.03

    #%Vectors with the gyro angles traversed in each sample.
    angx = np.zeros(L1)
    angy = np.zeros(L1)
    angz = np.zeros(L1)

    ae = np.zeros((3, L1))
    P = np.zeros(3)
    #########Rz = np.zeros((3, 3))

    for i in range(L1):
        angx[i] = gyrx[i] * dt
        angy[i] = gyry[i] * dt
        angz[i] = gyrz[i] * dt
        P[0] = ax[i]
        P[1] = ay[i]
        P[2] = az[i]

        W = _mat2_mult2(R, P)

        ae[0][i] = W[0][0]
        ae[1][i] = W[1][0]
        ae[2][i] = W[2][0]

        Rx = _init3x3(1, 0, 0, 0, math.cos(angx0[i]), -math.sin(angx0[i]), 0, math.sin(angx0[i]), math.cos(angx0[i]))
        Ry = _init3x3(math.cos(angy0[i]), 0, math.sin(angy0[i]), 0, 1, 0, -math.sin(angy0[i]), 0, math.cos(angy0[i]))
        Rz = _init3x3(math.cos(angz[i]), -math.sin(angz[i]), 0, math.sin(angz[i]), math.cos(angz[i]), 0, 0, 0, 1)

        R = _mat2_mult(_mat2_mult(_mat2_mult(R, Rx), Ry), Rz)
    
    comp = np.zeros(3)
    for i in range(comp):
        for j in range(L1):
            comp[i] = comp[i] + ae[i][j]
        comp[i] = 2*comp[i] / (L1 * L1)
    
    a1 = np.zeros((1, 1))
    b1 = np.zeros((1, L1))
    a2 = np.zeros((1,1))
    c1 = np.zeros((1, L1))
    c2 = np.zeros((1, L1))
    d1 = np.zeros((2, L1))
    ve = np.zeros((2, L1))
    temp1 = temp2 = 0.0

    a1[0][0] = comp[0]
    for i in range(L1):
        b1[0][i] = i
    
    a2[0][0] = comp[1]

    c1 = _mat2_mult(a1, b1)
    c2 = _mat2_mult(a2, b1)

    for j in range(L1):
        d1[0][j] = ae[0][j] - c1[0][j]
        d1[1][j] = ae[1][j] - c2[0][j]
    
    #cumsum
    for i in range(L1):
        temp1 = 0
        temp2 = 0
        for j in range(i):
            temp1 += d1[0][j]
            temp2 += d1[1][j]
        ve[0][i] = dt * temp1
        ve[1][i] = dt * temp2
    
    #Integrate velocities to get distances traveled in x and y direction
    le = np.zeros((2, L1))

    #cumsum
    for i in range(L1):
        temp1 = 0
        temp2 = 0
        for j in range(i):
            temp1 += ve[0][j]
            temp2 += ve[1][j]
        le[0][i] = dt * temp1
        le[1][i] = dt * temp2

    #Total distance traveled is sum of squares of components

    tot = np.zeros(1, L1)

    for i in range(L1):
        tot[i] = (le[0][i]**2 + le[1][i]**2)**0.5
    #WARNING: return tot[-1]
    return tot[-2]



def _residuals(data_r: list[list[float]], beta_r: list[float]) -> np.ndarray:
    """
    Return list[float]
    """
    L = len(data_r)
    retval_j = np.ones(L)
    

    for i in range(L):
        for j in range(1, 3+1):
            retval_j[i] = retval_j[i] - beta_r[3+j]**2 * (data_r[i][j] - beta_r[j])**2
    
    return retval_j

def _jacobian(data_j: list[list[float]], beta_j: list[float]) -> np.ndarray:
    """
    Return list[list[float]]
    """
    L = len(data_j)
    retval_j = np.zeros((L, 6))

    for i in range(L):
        for j in range(1, 3+1):
            retval_j[i][j] = 2 * beta_j[3+j]**2 * (data_j[i][j] - beta_j[j])
            retval_j[i][j+3] = -2 * beta_j[3+j] * (data_j[i][j] - beta_j[j])**2

    return retval_j


def _gn_step(data_s: list[float], beta_s: list[float]) -> list[float]:
    """
    Return: list size of L2
    """
    R = _residuals(data_s, beta_s)
    J = _jacobian(data_s, beta_s)

    L1 = J.shape[0]
    L2 = J.shape[1]

    Jt = np.zeros((L2, L1))
    
    Jt = np.transpose(J)

    js = _mat2_mult(Jt, J)
    pm = _mat2_mult2(Jt, R)

    js1 = np.zeros((L2, L2))
    pm1 = np.zeros((L2))

    for t in range(1,L2):
        for h in range(L2):
            js1[t-1][h-1] = js[t][h]
    
    for u in range(1, L2):
        pm1[u-1] = pm[u]

    delta_s = linalg.solve(js1, pm1)

    res = np.zeros(L2)
    for i in range(1, L2):
        res[i] = beta_s[i] - delta_s[i-1]

    return res.tolist()
    

def gn(acc_data: list[float], beta1: list[float]) -> list[float]:
    """"""
    chng = 100
    step = 0

    beta = copy.copy(beta1)
    A = copy.copy(acc_data)
    while chng > 0.00000001 and step < 100:
        oldBeta = beta
        beta = _gn_step(A, beta)
        chng = 0
        for i in range(1, 7):
            if oldBeta[i] != 0:
                chng = chng + abs((beta[i] - oldBeta[i]) / oldBeta[i])
            step += 1

    return beta

def do_cali_calc(acc_data: list[float], gyr_data: list[list[float]], n: int, b: list[float], k: list[float], h: list[float]):
    """"""
    ar = np.zeros(6)
    
    ar[0] = 0
    ar[1] = 0
    ar[2] = 0
    ar[3] = 0.00024414
    ar[4] = 0.00024414
    ar[5] = 0.00024414

    ret = gn(acc_data, ar)

    for T in range(1, 4):
        b[T] = ret[T]

    for T in range(1, 4):
        k[T] = ret[T+3]* 2**15 / 8
    
    temp1 = 0
    temp2 = 0
    temp3 = 0
    for q in range(n):
        temp1 += gyr_data[q][1]
        temp2 += gyr_data[q][2]
        temp3 += gyr_data[q][3]
    h[1] = temp1 / n
    h[2] = temp2 / n
    h[3] = temp3 / n

def change_all_FRI_names_for_subjects(oldname: str, newname: str):
    """"""
    for i in range(g.tool.configuration.users):
        if not ufx.is_array_empty(g.tool.configuration.users[i].showFRI):
            for j in range(g.tool.configuration.users[i].showFRI):
                lowerCurr = g.tool.configuration.users[i].showFRI[j].lower()
                lowerOld = oldname.lower()
                if lowerCurr == lowerOld:
                    g.tool.configuration.users[i].showFRI[j] = newname
                    g.tool.configuration.changed = True
                    return
    
def delete_FRI_from_subjects(name: str):
    """"""
    for i in range(g.tool.configuration.users):
        if not ufx.is_array_empty(g.tool.configuration.users[i].showFRI):
            for j in range(g.tool.configuration.users[i].showFRI):
                lowerCurr = g.tool.configuration.users[i].showFRI[j].lower()
                lowerNew = name.lower()
                if lowerCurr == lowerNew:
                    ufx.remove_from_arr(g.tool.configuration.users[i].showFRI, j)

def _gaussian_func(x: float, range: float) -> float:
    """"""
    #change
    stddev = 3.14159

    res = 0.0
    if abs(x) < range:
        o = range / stddev
        res = 0.398942280401433 / o * math.exp(-x * x / (o * o * 2))
    return res

def gauss(noOfStrides: int, width: int) -> list[float]:
    """"""
    Y_MAX = 1
    res = []
    size = width + 1
    zero = 0

    di = 0
    py = y
    for x in range(noOfStrides):
        y = _gaussian_func((x / noOfStrides - 0.5) * size * 2, size)
        di += (y + py) * size / noOfStrides
        py = y
        y = ((1-y) * 0.5 + 0.25) * Y_MAX
        if x == 0:
            zero = y
        res.append(-(y - zero))

    return res

def get_sum(arr: list[float]) -> float:
    """"""
    return np.array(arr).sum()

def give_xyz(startRow: int, endRow: int) -> tuple[float, float, float]:
    """
    Return: (vertical, ml, ap)
    """
    vertical = 0
    ml = 0
    ap = 0

    for i in range(startRow, endRow+1):
        ap += math.sqrt(g.tool._distanceXnew[i] * g.tool._distanceXnew[i])
        ml += math.sqrt(g.tool._distanceYnew[i] * g.tool._distanceYnew[i])
        vertical += math.sqrt(g.tool._distanceZnew[i] * g.tool._distanceZnew[i])
    
    return (vertical, ml, ap)

def threshold(x: float, y: float) -> bool:
    """
    threshold function to detect movement. If difference is small, then there is not movement.
    """
    if y != 0:
        res = abs((x-y) / y)
        return False if res < 0.03 else True
    return True

def threshold_top(x: float) -> float:
    """
    threshold function to filter big values.

    If increase this number, then we will filter more small noise. But difference in steps length will be bigger.
    """
    return 0.5 if x > 0.5 else x

def threshold_bottom(x: float) -> float:
    """
    threshold function to filter negative values.

    same as for thresholdTop
    """
    return -0.5 if x < -0.5 else x

def threshold_gyro_max(x: float) -> bool:
    """
    threshold function to detect big rotation.

    If there is big rotation we cannot measure distance.
    """
    return False if x > 0.75 else True

def remove_too_long_strides() -> bool:
    """
    Deletes strides in t.rawGait with some criteria.

    Returns False if g.tool.rawGait.strides has 0 strides.
    """
    for i in range(g.tool.rawGait.strides):
        if g.tool.rawGait.strides[i].leftEnd == 0:
            g.tool.rawGait.strides[i].remove = True
        if g.tool.rawGait.strides[i].rightStartNext - g.tool.rawGait.strides[i].leftStart > 2:
            g.tool.rawGait.strides[i].remove = True
        if g.tool.rawGait.strides[i].leftStart - g.tool.rawGait.strides[i].rightStart > 2:
            g.tool.rawGait.strides[i].remove = True
    remove_marked_strides()
    return False if len(g.tool.rawGait.strides) <= 0 else True

def remove_too_big_strides() -> bool:
    """
    Deletes strides in t.rawGait with some criteria.

    Returns False if t.rawGait.strides has 0 strides.
    """
    for i in range(g.tool.rawGait.strides):
        if g.tool.rawGait.strides[i].rightLength > 2:
            g.tool.rawGait.strides[i].remove = True
        elif g.tool.rawGait.strides[i].leftLength > 2:
            g.tool.rawGait.strides[i].remove = True
    remove_marked_strides()
    return False if len(g.tool.rawGait.strides) <= 0 else True

def remove_step(strides: list[m.RawStepdata], nr: int) -> bool:
    """
    Deletes element of strides (by ref) at index "nr".

    Return True if could be deleted.
    """
    try:
        strides.pop(nr)
        return True
    except IndexError as err:
        print(f"remove_step - unable to delete step: {err}")
        return False

def get_value_from_str(arr: list[str], dateStr: str, dataColumn: int, intra: bool, startIndex: int, multi: int) -> tuple[float, int]:
    """
    
    Return:
    -(value: float, startIndex: int)

    Return value = -1 if not found.
    """
    import time
    DEBUGSTART = time.time()
    if intra:
        #intraLine = dateStr.split(sep=",")
        L2 = int(float(dateStr) / multi)
    for i in range(startIndex, len(arr)):
        if intra:
            line = arr[i].split(",")
            L1 = int(float(line[0]) / multi)
            if L1 == L2:
                #warning
                intraLine = line[dataColumn]
                DEBUGEND = time.time()
                #print(f'Start get_value_from_str: {DEBUGSTART}. Elapsed time: {DEBUGEND - DEBUGSTART}')
                return (float(intraLine), i)
            elif L1 > L2:
                DEBUGEND = time.time()
                #print(f'Start get_value_from_str: {DEBUGSTART}. Elapsed time: {DEBUGEND - DEBUGSTART}')
                return (-1, i)
        else:
            if dateStr in arr[i]:
                line = arr[i].split(",")
                DEBUGEND = time.time()
                #print(f'Start get_value_from_str: {DEBUGSTART}. Elapsed time: {DEBUGEND - DEBUGSTART}')
                return (float(line[dataColumn]), i)
    DEBUGEND = time.time()
    #print(f'Start get_value_from_str: {DEBUGSTART}. Elapsed time: {DEBUGEND - DEBUGSTART}')
    return -1, 0

def add_to_all(all: list[m.AllData], arr: list[str], dataColumn: int, intra: bool, minute: bool) -> list[list[m.AllData]]:
    """
    Args:
    - all: list[list[AllData]] of size 1xN (???): input MUST be empty list [], initialized by reference.
    - arr: file content (lines)
    - dataColumn: 
    - intra: True = intraday, False = daily
    - minute:

    Return:
    - list[list[AllData]] of size 1xN (???)
    """
    multi = 0
    fillZero = False
    rannge = 0
    lExtend = False
    hExtend = False
    res = list()

    #warning todito: variables no previamente inicializadas
    if not ufx.is_array_empty(arr):
        if arr[-1] == "":
            ufx.remove_from_arr(arr, len(arr)-1)

        if len(arr) > 1:
        
            if not ufx.is_array_empty(arr):
                #if len(arr) > 0:
                lLine = arr[0].split(",")

                if intra:
                    lowTime = int(lLine[0])
                    if minute:
                        multi = 1980
                    else:
                        multi = 100
                else:
                    lowDate = datetime.date(int(lLine[0][-4:]), int(lLine[0][0:2]), int(lLine[0][3:3+2]))
                    #lowDate = ufx.get_date_from_str(lLine[0][0:10])
                hLine = arr[-1].split(",")
                if intra:
                    highTime = int(hLine[0])
                else:
                    highDate = datetime.date(int(hLine[0][-4:]), int(hLine[0][0:2]), int(hLine[0][3:3+2]))
                    #highDate = ufx.get_date_from_str(hLine[0][0:10])
                if len(all) <= 0:
                    if intra:
                        rannge = (highTime - lowTime) / multi
                    else:
                        rannge = abs((lowDate - highDate).days)
                    #warning: conversion of rannge to int
                    #all = [[None] * len(int(rannge))]
                    all = list()
                    all.append([m.AllData(date='0') for x in range(math.ceil(rannge)+1)])
                    all[0][0].date = lLine[0] if lLine[0] != "" else '0'
                    all[0][0].value = float(lLine[dataColumn])

                    i = 0
                    startIndex = 0
                    while True:
                        i += 1
                        if i >= len(all[0]):
                            break
                        if intra:
                            lowTime += multi
                        else:
                            lowDate = lowDate + datetime.timedelta(days=1)

                        if intra:
                            all[0][i].date = str(lowTime)
                        else:
                            all[0][i].date = ufx.get_str_from_date(lowDate)
                        value, startIndex = get_value_from_str(arr, all[0][i].date, dataColumn, intra, startIndex, multi)
                        if value > -1:
                            all[0][i].value = value
                        else:
                            all[0][i].value = all[0][i-1].value
                    
                    #return all
                    res = all

                else:
                    if intra:
                        if lowTime < round(int(all[0][0].date)):
                            lExtend = True
                        if highTime > round(int(all[0][-1].date)):
                            hExtend = True
                    else:
                        if lowDate < ufx.get_date_from_str(all[0][0].date):
                            lExtend = True
                        if highDate > ufx.get_date_from_str(all[0][-1].date):
                            hExtend = True
                
                    if lExtend:
                        if intra:
                            rannge = int((round(float(all[0][-1].date)) - lowTime) / multi)
                        else:
                            rannge = abs((lowDate - ufx.get_date_from_str(all[0][0][0:10])).days)
                        #TODO: same as above
                        #all = list()
                        #all.append([m.AllData() for x in range(math.ceil(rannge))])
                        buff = list()
                        for i in range(len(all)):
                            buff.append([m.AllData(date='0') for x in range(math.ceil(rannge + len(all[0])))])
                        #buff = [[None]* (len(all[0]) + rannge)] * len(all)

                        for i in range(len(all)):
                            for j in range(len(all[0])):
                                buff[i][j + rannge].date = all[i][j].date
                                buff[i][j + rannge].value = all[i][j].value
                        for i in range(len(all)):
                            if intra:
                                dateLng = int(all[0][0].date)
                            else:
                                date = ufx.get_date_from_str(all[0][0].date[0:10])
                            for j in range(rannge-1, 0-1, -1):
                                if intra:
                                    dateLng = dateLng - multi
                                    buff[i][j].date = dateLng
                                else:
                                    date = date - datetime.timedelta(days = 1)
                                    buff[i][j].date = ufx.get_str_from_date(date[0:10])
                                
                                buff[i][j].value = all[i][0].value
                        #return buff
                        #res = buff
                        all = buff
                
                    if hExtend:
                        if intra:
                            rannge = round((highTime - round(float(all[0][-1].date)) / multi))
                        else:
                            rannge = abs((ufx.get_date_from_str(all[0][-1].date) - highDate).days)
                        #buff = [[None]* (len(all[0]) + rannge)] * len(all)
                        buff = list()
                        for i in range(len(all)):
                            buff.append([m.AllData(date='0') for x in range(math.ceil(rannge + len(all[0])))])

                        for i in range(len(all)):
                            for j in range(len(all[0])):
                                buff[i][j].date = all[i][j].date
                                buff[i][j].value = all[i][j].value
                        for i in range(len(all)):
                            if intra:
                                dateLng = int(all[0][-1].date)
                            else:
                                date = ufx.get_date_from_str(all[0][-1].date[0:10])
                            for j in range(len(all[0]), len(all[0])+rannge):
                                if intra:
                                    dateLng = dateLng + multi
                                    buff[i][j].date = dateLng
                                else:
                                    date = date + datetime.timedelta(days = 1)
                                    buff[i][j].date = ufx.get_str_from_date(date)
                                
                                buff[i][j].value = all[i][-1].value
                        #return buff
                        #res = buff
                        all = buff
                    
                    #TODO: same as above
                    #buff = [[None]* (len(all[0]))] * len(all)
                    buff = list()
                    for i in range(len(all)+1):
                        buff.append([m.AllData(date='0') for x in range(len(all[0]))])
                    

                    for i in range(len(all)):
                        for j in range(len(all[0])):
                            buff[i][j].date = all[i][j].date
                            buff[i][j].value = all[i][j].value
                    startIndex = 0
                    for j in range(len(all[0])):
                        buff[-1][j].date = buff[0][j].date
                        value, startIndex = get_value_from_str(arr, buff[0][j].date, dataColumn, intra, startIndex, multi)
                        if value > -1:
                            buff[-1][j].value = value
                        else:
                            if j > 0:
                                buff[-1][j].value = buff[-1][j-1].value
                            else:
                                fillZero = True
                    if fillZero:
                        no = -1
                        for j in range(len(all[0])):
                            if buff[-1][j].value != 0:
                                no = j
                                break
                        
                        if no > -1:
                            for j in range(no):
                                buff[-1][j].value = buff[-1][no].value
                    
                    #return buff
                    res = buff
    else:
        return all
    #return []
    return res

def _add_history(string: str, strength: int) -> list[str]:
    """
    Pass a line ('string') with a date in front.

    Return a list with str in format: MM/DD/YYYY,value1,value2optional
    """
    line = string.split(",")
    date = ufx.get_date_from_str(line[0])
    value = float(line[1])
    if len(line) > 1:
        var = float(line[2])

    arr = []
    for i in range(300, 0-1, -1):
        #if len(line) > 1:
        if len(line) > 2:
            arr.append(f"{ufx.get_str_from_date(date)},{ufx.kzp(str(value))},{ufx.kzp(str(var))}")
        else:
            arr.append(f"{ufx.get_str_from_date(date)},{ufx.kzp(str(value))}")
        date = date - datetime.timedelta(days = 1)
        value = round(value + random.random() * value / strength - value / (strength * 2), ndigits=4)
        #if len(line) > 1:
        if len(line) > 2:
            var = round(var + random.random() * var / strength - value / (strength * 2), ndigits=4)
    return arr

#repo
def generate_histories():
    """
    Adds some points of data (300 points) for each user parameter and activity time and 

    Files read/written: 
    - myDoc/config/{confName}/subjects/{userID}/parameter/daily/{gaitParamName}.txt
    - myDoc/config/{confName}/subjects/{userID}/parameter/daily/NoOfSteps.txt
    - myDoc/config/{confName}/subjects/{userID}/parameter/daily/ActivityTime.txt
    """
    #GUI: should put cursor with hourglass icon
    for i in range(g.tool.configuration.users):
        for j in range(g.tool.configuration.users[i].gaitParameter):
            pathGaitParam = os.path.join(g.tool.myDocFolder, "configurations", g.tool.configuration.name, "subjects", g.tool.configuration.users[i].id, "parameter", "daily", f"{g.tool.configuration.users[i].gaitParameter[j].name}.txt")
            arr = ufx.get_arr_from_file(pathGaitParam)
            if not ufx.is_array_empty(arr):
                if arr[-1] == "":
                    arr.pop()
                arr = _add_history(arr[0], 200)
                ufx.save_arr_to_file(pathGaitParam, arr)
        pathNoOfSteps = os.path.join(g.tool.myDocFolder, "configurations", g.tool.configuration.name, "subjects", g.tool.configuration.users[i].id, "parameter", "daily", "NoOfSteps.txt")
        arr = ufx.get_arr_from_file(pathNoOfSteps)
        if not ufx.is_array_empty(arr):
            if arr[-1] == "":
                arr.pop()
            arr = _add_history(arr[0], 200)
            ufx.save_arr_to_file(pathGaitParam, arr)
        
        pathActivityTime = os.path.join(g.tool.myDocFolder, "configurations", g.tool.configuration.name, "subjects", g.tool.configuration.users[i].id, "parameter", "daily", "ActivityTime.txt")
        arr = ufx.get_arr_from_file(pathActivityTime)
        if not ufx.is_array_empty(arr):
            if arr[-1] == "":
                arr.pop()
            arr = _add_history(arr[0], 200)
            ufx.save_arr_to_file(pathActivityTime, arr)
    calc_all_FRI()
            
def make_path_save(string: str) -> str:
    """
    Removes appearances of "@", ".", "/", `\`, "*" in given 'string'
    """
    string = string.replace("@", "")
    string = string.replace(".", "")
    string = string.replace("\\", "")
    string = string.replace("*", "")
    return string
        
#GUI
def add_FRI(fri: m.RiskIndex):
    """
    Add pattern1 to global conf.gaitPattern1, if already doesn't exist one with same name.
    """
    marker = False
    for i in range(g.tool.configuration.fallRiskIndex):
        if g.tool.configuration.gaitPattern1[i].name == fri.name:
            marker = True
            break
    if not marker:
        g.tool.configuration.fallRiskIndex.append(fri)

def check_for_update() -> bool:
    """TODO"""
    return False

def sec_to_time(nr: int) -> tuple[int, int, int]:
    """
    Return: (nr/3600000 a.k.a. hour, minute, second)
    """
    res = int(nr / 3600000)
    minute = int((nr - res * 3600000) / 60000)
    second = int(nr - res * 3600000 - minute * 60000) * 0.001
    return (res, minute, second)

def filter_zero_steps(userNo: int) -> bool:
    """
    Remove strides with zero length. If no steps remain, return False.
    """

    for i in range(len(g.tool.rawGait.strides)):
        if g.tool.rawGait.strides[i].leftLength <= 0 or g.tool.rawGait.strides[i].rightLength <= 0:
            g.tool.rawGait.strides[i].remove = True
    remove_marked_strides()
    if len(g.tool.rawGait.strides) == 0:
        return False
    else:
        return True

def delete_unequal_steps(userNo: int) -> bool:
    """
    Remove strides with a certain criteria. If no steps remain, return False.
    """
    if g.tool.configuration.removeNoOfStrides > 0:
        meanR = 0
        meanL = 0
        currR = 0
        currL = 0

        cnt = 6
        stepDiffFilter = 1 + g.tool.configuration.stepDiffFilter / 100
        for i in range(cnt, len(g.tool.rawGait.strides)):
            meanR = _give_mean_steps(i, "R")
            meanL = _give_mean_steps(i, "L")
            currR = g.tool.rawGait.strides[i].rightEnd - g.tool.rawGait.strides[i].rightStart
            currL = g.tool.rawGait.strides[i].leftEnd - g.tool.rawGait.strides[i].leftStartLast

            if not (meanR == 0 or meanL == 0 or currR == 0 or currL == 0):
                if currR / meanR > stepDiffFilter or meanR / currR > stepDiffFilter or currL / meanL > stepDiffFilter or meanL/currL > stepDiffFilter:
                    for j in range(g.tool.configuration.removeNoOfStrides):
                        if j + i - int(g.tool.configuration.removeNoOfStrides*0.5) > -1:
                            if j + i - int(g.tool.configuration.removeNoOfStrides*0.5) <= len(g.tool.rawGait.strides):
                                g.tool.rawGait.strides[j + i - int(g.tool.configuration.removeNoOfStrides/2)].remove = True
        remove_marked_strides()
        if len(g.tool.rawGait.strides) == 0:
            return False
        else:
            return True

def _give_mean_steps(nr: int, side: str) -> float:
    """
    
    """
    sum = 0
    cnt = 0

    #warning... nr-1 o nr?
    for i in range(nr-1, 0-1, -1):
        if side == "R":
            if g.tool.rawGait.strides[i].rightEnd - g.tool.rawGait.strides[i].rightStart < 2:
                sum += g.tool.rawGait.strides[i].rightEnd - g.tool.rawGait.strides[i].rightStart
                cnt += 1
                if cnt == 5:
                    break
        elif side == "L":
            if g.tool.rawGait.strides[i].leftEnd - g.tool.rawGait.strides[i].leftStartLast < 2:
                sum += g.tool.rawGait.strides[i].leftEnd - g.tool.rawGait.strides[i].leftStartLast
                cnt += 1
                if cnt == 5:
                    break
    if cnt > 0:
        return sum/cnt
    else:
        return 0.0

def get_color_of_fri(friName: str, value: str) -> str:
    """
    Return color of fri (either "green", "red", "yellow", or "" if friName is not found in global configuration.fallriskIndex[])
    """
    color = ""
    i = -1
    for j in range(g.tool.configuration.fallRiskIndex):
        if friName.lower() == g.tool.configuration.fallRiskIndex[j].name.lower():
            i = j
            break
    if i > -1:
        if float(value) <= g.tool.configuration.fallRiskIndex[i].greenEnd:
            color = "green"
        elif float(value) <= g.tool.configuration.fallRiskIndex[i].yellowEnd:
            color = "yellow"
        elif float(value) > g.tool.configuration.fallRiskIndex[i].redEnd:
            color = "red"
    return color

def check_monitor(user: str) -> bool:

    path = os.path.join(g.rtv.app.path, "ini.dat")
    arr = ufx.get_arr_from_file(path)
    if not ufx.is_array_empty(arr):
        for i in range(arr):
            if user == arr[i]:
                return True
    return False