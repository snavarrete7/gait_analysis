import src.model.globalvars as g
import tkinter as tk
from tkinter import messagebox, filedialog
import os
import src.model as m
import src.tools as t
import numpy as np
from enum import Enum

from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
# Implement the default Matplotlib key bindings.
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure

class PlotType(Enum):
    BarChart3D = "Bar chart 3D"
    BarChart2D = "Bar chart 2D"
    LineChart3D = "Line chart 3D"
    LineChart2D = "LineChart2D"

def check1_click():
    text21_change()

def text21_change():
    checkVar = g.rt.patternExtractionVars["check1"]
    textVar = g.rt.patternExtractionVars["text21"]
    g.tool.configuration.filterStdDevF = textVar.get() if checkVar.get() == True else 0.0
    
    g.tool.configuration.changed = True

def check2_click():
    text30_change()

def text30_change():
    checkVar = g.rt.patternExtractionVars["check2"]
    textVar = g.rt.patternExtractionVars["text30"]
    g.tool.configuration.filterVarianceF = textVar.get() if checkVar.get() == True else 0.0
    
    g.tool.configuration.changed = True

def check3_click():
    text33_change()

def text33_change():
    checkVar = g.rt.patternExtractionVars["check3"]
    textVar = g.rt.patternExtractionVars["text33"]
    g.tool.configuration.filterStdErrF = textVar.get() if checkVar.get() == True else 0.0
    
    g.tool.configuration.changed = True

def check4_click():
    text3_change()

def text3_change():
    checkVar = g.rt.patternExtractionVars["check4"]
    textVar = g.rt.patternExtractionVars["text3"]
    g.tool.configuration.filterStdErrN = textVar.get() if checkVar.get() == True else 0.0
    
    g.tool.configuration.changed = True

def check5_click():
    text2_change()

def text2_change():
    checkVar = g.rt.patternExtractionVars["check5"]
    textVar = g.rt.patternExtractionVars["text3"]
    g.tool.configuration.filterVarianceN = textVar.get() if checkVar.get() == True else 0.0
    
    g.tool.configuration.changed = True

def check6_click():
    text1_change()

def text1_change():
    checkVar = g.rt.patternExtractionVars["check6"]
    textVar = g.rt.patternExtractionVars["text1"]
    g.tool.configuration.filterStdDevN = textVar.get() if checkVar.get() == True else 0.0
    
    g.tool.configuration.changed = True

def check7_click():
    text4_change()

def text4_change():
    checkVar = g.rt.patternExtractionVars["check7"]
    textVar = g.rt.patternExtractionVars["text4"]
    g.tool.configuration.filterStdDevN = textVar.get() if checkVar.get() == True else 0.0
    
    g.tool.configuration.changed = True

def check8_click():
    text5_change()

def text5_change():
    checkVar = g.rt.patternExtractionVars["check8"]
    textVar = g.rt.patternExtractionVars["text5"]
    g.tool.configuration.filterStdDevN = textVar.get() if checkVar.get() == True else 0.0
    
    g.tool.configuration.changed = True

def combo1_click():
    #TODO
    pass

def command33_click():
    if g.rtv.patternExtraction.selected != "":
        for pattern1 in g.rtv.patternExtraction.pattern:
            if pattern1.name == g.rtv.patternExtraction.selected:
                add_pattern1(pattern1)
                break

def command7_click():
    strList = list()
    fallersName = list()
    nonFallersName = list()
    controlFName = list()
    controlNname = list()
    unit = ""
    paraNo = 0

    fallers = list()
    nonFallers = list()
    controlF = list()
    controlN = list()

    if len(g.tool.configuration.gaitParameterDef) > 0:
        for gaitParDef in g.tool.configuration.gaitParameterDef:
            #if gaitParDef.Active:
            strList.append(gaitParDef.name)
            strList.append(f'{gaitParDef.name} variation')
        if len(strList) > 0:
            g.rtv.patternExtraction.pattern = list()

        # ResultsList.Clear
        # ResultsList.Rows = 1
        # ResultsList.Cols = 6
        # ResultsList.TextMatrix(0, 0) = "Pattern base"
        # ResultsList.TextMatrix(0, 2) = "Faller"
        # ResultsList.TextMatrix(0, 3) = "Non faller"
        # ResultsList.TextMatrix(0, 4) = "Validation faller"
        # ResultsList.TextMatrix(0, 5) = "Validation non faller"

            expectationF = np.zeros(len(strList))
            expectationN = np.zeros(len(strList))
            expectationCF = np.zeros(len(strList))
            expectationCN = np.zeros(len(strList))
            meanF = np.zeros(len(strList))
            meanN = np.zeros(len(strList))
            meanCF = np.zeros(len(strList))
            meanCN = np.zeros(len(strList))
            stdDevF = np.zeros(len(strList))
            stdDevN = np.zeros(len(strList))
            stdDevCF = np.zeros(len(strList))
            stdDevCN = np.zeros(len(strList))
            stdErrF = np.zeros(len(strList))
            stdErrN = np.zeros(len(strList))
            stdErrCF = np.zeros(len(strList))
            stdErrCN = np.zeros(len(strList))
            varianceF = np.zeros(len(strList))
            varianceN = np.zeros(len(strList))
            varianceCF = np.zeros(len(strList))
            varianceCN = np.zeros(len(strList))
            medianF = np.zeros(len(strList))
            medianN = np.zeros(len(strList))
            medianCF = np.zeros(len(strList))
            medianCN = np.zeros(len(strList))

            for i, gaitParamName in enumerate(strList):
                vari = t.is_type_variation(gaitParamName)
                paraNo = t.get_para_no(gaitParamName.removesuffix(" variation"))

                if paraNo > -1:
                    unit = f'[{g.tool.configuration.gaitParameterDef[paraNo].unit}]'
                
                get_subject_data(fallers, nonFallers, controlF, controlN, gaitParamName, vari, fallersName, nonFallersName, controlFName, controlNname)

                if g.tool.configuration.filterHighLowF > 0:
                    remove_high_low(fallers, g.tool.configuration.filterHighLowF)
                expectationF[i], meanF[i], stdDevF[i], stdErrF[i], varianceF[i], medianF[i] = t.get_stats(fallers)

                if g.tool.configuration.filterHighLowN > 0:
                    remove_high_low(nonFallers, g.tool.configuration.filterHighLowN)
                expectationN[i], meanN[i], stdDevN[i], stdErrN[i], varianceN[i], medianN[i] = t.get_stats(nonFallers)

                if g.tool.configuration.filterHighLowF > 0:
                    remove_high_low(controlF, g.tool.configuration.filterHighLowF)
                expectationCF[i], meanCF[i], stdDevCF[i], stdErrCF[i], varianceCF[i], medianCF[i] = t.get_stats(controlF)

                if g.tool.configuration.filterHighLowN > 0:
                    remove_high_low(nonFallers, g.tool.configuration.filterHighLowN)
                expectationCN[i], meanCN[i], stdDevCN[i], stdErrCN[i], varianceCN[i], medianCN[i] = t.get_stats(controlN)

                if meanF[i] != 0:
                    if ((stdDevF[i] / meanF[i] * 100 < g.tool.configuration.filterStdDevF or g.tool.configuration.filterStdDevF == 0) and
                            (varianceF[i] / meanF[i] * 100 < g.tool.configuration.filterVarianceF or g.tool.configuration.filterVarianceF == 0) and
                            (stdErrF[i] / meanF[i] * 100 < g.tool.configuration.filterStdErrF or g.tool.configuration.filterStdErrF == 0)):

                        newPatternFormula = list(("", "", "", "", "", ""))
                        newPatternFormula[0] = gaitParamName
                        newPatternFormula[1] = t.kzp(str(meanF[i])).strip()
                        newPatternFormula[2] = t.kzp(str(round(varianceF[i] / meanF[i] * 100, ndigits=2))).strip()
                        newPatternFormula[5] = unit

                        if ((stdDevN[i] / meanN[i] * 100 < g.tool.configuration.filterStdDevN or g.tool.configuration.filterStdDevN == 0) and
                                (varianceN[i] / meanN[i] * 100 < g.tool.configuration.filterVarianceN or g.tool.configuration.filterVarianceN == 0) and
                                (stdErrN[i] / meanN[i] * 100 < g.tool.configuration.filterStdErrN or g.tool.configuration.filterStdErrN == 0)):
                            newPatternFormula[3] = t.kzp(str(meanN[i])).strip()
                            newPatternFormula[4] = t.kzp(str(round(varianceN[i] / meanN[i] * 100, ndigits=2))).strip()
                        
                        g.rtv.patternExtraction.pattern.append(m.Pattern1(formula=newPatternFormula, description="Automatically extracted"))

            #fill results_list
            resultslist = g.rt.get_child("resultslist", g.rt.patternExtraction)
            resultslist.delete(*resultslist.get_children())

            columnHeaders = ('', 'Faller', 'Non faller', 'Validation faller', 'Validation nonfaller')
            resultslist['columns'] = columnHeaders
            #resultslist['width'] = 100

            #set width of columns
            for header in columnHeaders:
                resultslist.column(header, anchor=tk.CENTER, stretch=tk.NO, width=100)
            resultslist.column('#0', width=100)

            ###############resultslist.heading('Pattern base', text="Pattern base")
            resultslist.heading('Faller', text="Faller")
            resultslist.heading('Non faller', text="Non faller")
            resultslist.heading('Validation faller', text="Validation faller")
            resultslist.heading('Validation nonfaller', text="Validation nonfaller")
            for i, gaitParameterName in enumerate(strList):
                resultslist.insert('', tk.END, gaitParameterName, text=gaitParameterName)
                resultslist.insert('', tk.END, values=(f'Mean {unit}', meanF[i], meanN[i], meanCF[i], meanCN[i]))
                resultslist.insert('', tk.END, values=(f'Median {unit}', medianF[i], medianN[i], medianCF[i], medianCN[i]))
                resultslist.insert('', tk.END, values=(f'Rel. Variance [%]', varianceF[i], varianceN[i], varianceCF[i], varianceCN[i]))
                resultslist.insert('', tk.END, values=(f'Rel. StdDev [%]', stdDevF[i], stdDevN[i], stdDevCF[i], stdDevCN[i]))
                resultslist.insert('', tk.END, values=(f'Rel. StdErr [%]', stdErrF[i], stdErrN[i], stdErrCF[i], stdErrCN[i]))
                
def resultslist_click(e: tk.Event):
    resultslist = e.widget
    unit = list()

    fallers = list()
    nonFallers = list()
    controlF = list()
    controlN = list()

    fallersName = list()
    nonFallersName = list()
    controlFName = list()
    controlNname = list()

    # distributionF = list()
    # distributionN = list()
    # distributionCF = list()
    # distributionCN = list()
    # ranges = list()




    if len(resultslist.get_children()) > 0:
        if len(resultslist.selection()) > 0:
            selectedRowGaitParam = resultslist.selection()[0]
            g.rtv.patternExtraction.selected = selectedRowGaitParam
            vari = t.is_type_variation(selectedRowGaitParam)
            paraNo = t.get_para_no(selectedRowGaitParam)
            if paraNo > -1:
                unit.append(f'[{g.tool.configuration.gaitParameterDef[paraNo].unit}]')
            else:
                unit.append("")
                
            get_subject_data(fallers, nonFallers, controlF, controlN, selectedRowGaitParam, vari, fallersName, nonFallersName, controlFName, controlNname)
            maximum, minimum, distributionF, distributionN, distributionCF, distributionCN, ranges = get_ranges(fallers, nonFallers, controlF, controlN)

            if len(distributionF) > 0:
                #Details list
                detailslist = g.rt.get_child("detailslist", root=g.rt.patternExtraction)
                detailslist.delete(*detailslist.get_children())

                columnHeaders = ('Faller', 'Non Faller', selectedRowGaitParam)
                detailslist['columns'] = columnHeaders
                #detailslist['width'] = 0.0
                for header in columnHeaders:
                    detailslist.column(header, anchor=tk.CENTER, stretch=tk.NO, width=100)
                    detailslist.heading(header, text=header)

                for i, fallerName in enumerate(fallersName):
                    detailslist.insert('', tk.END, values=(fallerName, '', fallers[i]))

                for i, nonFallerName in enumerate(nonFallersName):
                    detailslist.insert('', tk.END, values=('', nonFallerName, nonFallers[i]))

                #Calculate values of each group as percentage
                yValuesF = np.zeros(len(distributionF))
                if sum(distributionF) > 0:
                    for i in range(len(distributionF)):
                        yValuesF[i] = distributionF[i] / sum(distributionF) * 100

                yValuesN = np.zeros(len(distributionN))
                if sum(distributionN) > 0:
                    for i in range(len(distributionN)):
                        yValuesN[i] = distributionN[i] / sum(distributionN) * 100

                yValuesCF = np.zeros(len(distributionCF))
                if sum(distributionCF) > 0:
                    for i in range(len(distributionCF)):
                        yValuesCF[i] = distributionCF[i] / sum(distributionCF) * 100

                yValuesCN = np.zeros(len(distributionCN))
                if sum(distributionCN) > 0:
                    for i in range(len(distributionCN)):
                        yValuesCN[i] = distributionCN[i] / sum(distributionCN) * 100

                xValues = []
                for i in range(len(distributionF)):
                    if i == 0:
                        xValues.append(f'{round(minimum, ndigits=2)} - {round(ranges[i], ndigits=2)}')
                    else:
                        xValues.append(f'{round(ranges[i-1], ndigits=2)} - {round(ranges[i], ndigits=2)}')
                
                #Plot distribution
                fig = Figure(figsize=(5,4), dpi=100)
                ax = fig.add_subplot(1, 1, 1)
                ax.set_title(selectedRowGaitParam)
                ax.set_ylabel("[%]")
                ax.set_ylim(bottom=0, top=100)
                ax.plot(xValues, yValuesF, label='Faller')
                ax.plot(xValues, yValuesN, label='Non faller')
                ax.plot(xValues, yValuesCF,label='Control group faller')
                ax.plot(xValues, yValuesCN, label='Control group non faller')
                ax.legend(bbox_to_anchor=[0.8, 0.9], loc='upper center', fontsize='small')

                parent = g.rt.get_child("distributionchart", g.rt.patternExtraction)
                figCanvas = FigureCanvasTkAgg(fig, master=parent)
                figCanvas.draw()

                toolbar = NavigationToolbar2Tk(figCanvas, parent, pack_toolbar=False)
                toolbar.update()

                toolbar.grid(row=2, column=0)
                figCanvas.get_tk_widget().grid(row=0, column=0)

                    
                

def add_pattern1(pattern: m.Pattern1):
    marker = False
    for confPattern1 in g.tool.configuration.gaitPattern1:
        if confPattern1.name == pattern.name:
            marker = True
            break
    
    if not marker:
        g.tool.configuration.gaitPattern1.append(pattern)
        g.rt.get_child("list7").insert(tk.END, pattern.name)
        g.rt.get_child("list10").insert(tk.END, pattern.name)
        g.tool.configuration.changed = True
        #ResearchTool.List1_Click
    
def remove_high_low(dblArr: list[float], value: float):
    if len(dblArr) > 0:
        switch = False
        noToRemove = len(dblArr) * 0.01 * value
        for i in range(1, int(noToRemove+1)):
            if len(dblArr) > 0:
                if switch:
                    remove_lowest(dblArr)
                    switch = not switch
                else:
                    remove_highest(dblArr)
                    switch = not switch
            else:
                break

def remove_lowest(dblArr: list[float]):
    """dblArr modified by reference"""
    nr = 0
    low = dblArr[0]

    for i in range(dblArr):
        if i > 0:
            if dblArr[i] < low:
                low = dblArr[i]
                nr = i
    for i in range(nr, len(dblArr)-1):
        dblArr[i] = dblArr[i-1]
    dblArr = dblArr[0:-1]

def remove_highest(dblArr: list[float]):
    """dblArr modified by reference"""
    nr = 0
    high = dblArr[0]

    for i in range(dblArr):
        if i > 0:
            if dblArr[i] > high:
                high = dblArr[i]
                nr = i
    for i in range(nr, len(dblArr)-1):
        dblArr[i] = dblArr[i-1]
    dblArr = dblArr[0:-1]

def get_subject_data(fallers: list[float], nonFallers: list[float], controlF: list[float], controlN: list[float], paraName: str, vari: bool, fallersName: list[str], nonFallersName: list[str], controlFName: list[str], controlNName: list[str]):
    """
    Read parameter paraName daily data from each user in all listboxes in "comparison pattern" section, both values (normal and variation) and names into the corresponding input parameter.
    """
    #TODO: review if studying only a subset of all subjects (faller, nonFaller) is the desired effect (when calculating with t.get_stats())
    fallers.clear()
    nonFallers.clear()


    #Fallers
    for listItem in g.rt.get_child("list5").get(0, tk.END):
        if vari:
            path = os.path.join(g.tool.myDocFolder, "configurations", g.tool.configuration.name, "subjects", t.get_id_from_name(listItem), "parameter", "daily", f'{paraName.removesuffix(" variation")}.txt')
        else:
            path = os.path.join(g.tool.myDocFolder, "configurations", g.tool.configuration.name, "subjects", t.get_id_from_name(listItem), "parameter", "daily", f'{paraName}.txt')
        arr = t.get_arr_from_file(path)
        if len(arr) > 0:
            #warning
            line = arr[-1].split(",")
            if vari:
                fallers.append(float(t.kzp(line[2])))
            else:
                fallers.append(float(t.kzp(line[1])))
            fallersName.append(listItem)

    #NonFallers
    for listItem in g.rt.get_child("list6").get(0, tk.END):
        if vari:
            path = os.path.join(g.tool.myDocFolder, "configurations", g.tool.configuration.name, "subjects", t.get_id_from_name(listItem), "parameter", "daily", f'{paraName.removesuffix(" variation")}.txt')
        else:
            path = os.path.join(g.tool.myDocFolder, "configurations", g.tool.configuration.name, "subjects", t.get_id_from_name(listItem), "parameter", "daily", f'{paraName}.txt')
        arr = t.get_arr_from_file(path)
        if len(arr) > 0:
            #warning
            line = arr[-1].split(",")
            if vari:
                nonFallers.append(float(t.kzp(line[2])))
            else:
                nonFallers.append(float(t.kzp(line[1])))
            nonFallersName.append(listItem)
    
    #Control group fallers
    for listItem in g.rt.get_child("list17").get(0, tk.END):
        if vari:
            path = os.path.join(g.tool.myDocFolder, "configurations", g.tool.configuration.name, "subjects", t.get_id_from_name(listItem), "parameter", "daily", f'{paraName.removesuffix(" variation")}.txt')
        else:
            path = os.path.join(g.tool.myDocFolder, "configurations", g.tool.configuration.name, "subjects", t.get_id_from_name(listItem), "parameter", "daily", f'{paraName}.txt')
        arr = t.get_arr_from_file(path)
        if len(arr) > 0:
            #warning
            line = arr[-1].split(",")
            if vari:
                controlF.append(float(t.kzp(line[2])))
            else:
                controlF.append(float(t.kzp(line[1])))
            controlFName.append(listItem)

    #Control group nonfallers
    for listItem in g.rt.get_child("list4").get(0, tk.END):
        if vari:
            path = os.path.join(g.tool.myDocFolder, "configurations", g.tool.configuration.name, "subjects", t.get_id_from_name(listItem), "parameter", "daily", f'{paraName.removesuffix(" variation")}.txt')
        else:
            path = os.path.join(g.tool.myDocFolder, "configurations", g.tool.configuration.name, "subjects", t.get_id_from_name(listItem), "parameter", "daily", f'{paraName}.txt')
        arr = t.get_arr_from_file(path)
        if len(arr) > 0:
            #warning
            line = arr[-1].split(",")
            if vari:
                controlN.append(float(t.kzp(line[2])))
            else:
                controlN.append(float(t.kzp(line[1])))
            controlNName.append(listItem)

#TODO: desplazar a tools, ver con cual de las dos implementaciones me quedo
def get_ranges(fallers: list[float], nonFallers: list[float], controlF: list[float], controlN: list[float]) -> tuple[float, float, list[float], list[float], list[float], list[float]]:
    """
    1.Find minimum and maximum of all combined fallers and nonFallers.
    2.distCnt = max(len(fallers), len(nonFallers)) / 2
    3.inicializar un array de longitud distCnt
    4.Comparar valores de fallers i nonfallers con este array del paso 3

    Return: (min: float, max: float, distributionF: list[float], distributionN: list[float], distributionC: list[float], distributionCN: list[float], ranges: list[float] )
    """
    mininum = 0.0
    maximum = 0.0

    distCnt = int(max(len(fallers), len(nonFallers)) / 2)
    if distCnt < 3:
        distCnt = 3
    
    ranges = list()
    distributionF = np.zeros(distCnt)
    distributionN = np.zeros(distCnt)
    distributionC = np.zeros(distCnt)
    distributionCN = np.zeros(distCnt)

    if len(fallers) > 0:
        mininum = min(fallers + nonFallers)
        maximum = max(fallers + nonFallers)

        for i in range(distCnt):
            if i == 0:
                ranges.append(mininum + (maximum - mininum) / distCnt)
            elif i == distCnt-1:
                ranges.append(maximum)
            else:
                ranges.append(ranges[-1] + (maximum - mininum) / distCnt)
            
        for faller in fallers:
            for j, ran in enumerate(ranges):
                if faller <= ran:
                    distributionF[j] += 1
                    break
        for nonfaller in nonFallers:
            for j, ran in enumerate(ranges):
                if nonfaller <= ran:
                    distributionN[j] += 1
                    break
        for faller in controlF:
            for j, ran in enumerate(ranges):
                if faller <= ran:
                    distributionC[j] += 1
                    break
        for nonFaller in controlN:
            for j, ran in enumerate(ranges):
                if nonFaller <= ran:
                    distributionCN[j] += 1
                    break
        
        distributionF = distributionF.tolist()
        distributionN = distributionN.tolist()
        distributionC = distributionC.tolist()
        distributionCN = distributionCN.tolist()
    return maximum, mininum, distributionF, distributionN, distributionC, distributionCN, ranges
        
