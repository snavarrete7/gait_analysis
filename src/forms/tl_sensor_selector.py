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

def combo1_selection_change():
    combo1 = g.rt.get_child("combo1", root=g.rt.sensorSelector)
    combo2 = g.rt.get_child("combo2", root=g.rt.sensorSelector)
    if combo1.current() in [0, 2, 3]:
        combo2['state'] = tk.NORMAL
    else:
        combo2['state'] = tk.DISABLED
    
def command2_click():
    g.rt.sensorSelector.wm_withdraw()

def command1_click():
    """
    If name of FRI doesn't already exist, saves OR updates each pattern and fri under mydocFolderRoot.
    """
    newSensorName = g.rt.sensorSelectorVars["text1"].get()
    type = g.rt.get_child("combo1", root=g.rt.sensorSelector).get()
    option = g.rt.get_child("combo2", root=g.rt.sensorSelector).get()
    unit = g.rt.sensorSelectorVars["text2"].get()
    if g.rtv.sensorSelector.newSensor:

        if newSensorName != "":
            #check if a sensor with same name exists first
            marker = False
            for columnName in g.tool.configuration.columns:
                if columnName.lower() == newSensorName.lower():
                    marker = True
                    break
            
            if not marker:
                g.tool.configuration.columns.append(newSensorName)
                g.tool.configuration.columnType.append(type)
                g.tool.configuration.columnOption.append(option)
                g.tool.configuration.columnUnit.append(unit)
                g.rt.get_child("list9").insert(tk.END, newSensorName)
                update_list()
                update_sensors()
                check_for_time_column()
                g.tool.configuration.changed = True
                g.tool.configuration.coreChange = True
                g.rt.sensorSelector.wm_withdraw()
                
            else:
                messagebox.showerror(message="This column already exists. Please choose a different name")
                return
        else:
            messagebox.showerror(message="Please enter a name for the column")
    else:
        #update the existing sensor
        for i, columnName in enumerate(g.tool.configuration.columns):
            if columnName.lower() == newSensorName.lower() and g.rtv.sensorSelector.selectedSensor != i:
                marker = True
                break

        if not marker:
            messagebox.showerror(message="This column already exists. Please choose a different name")
        else:
            g.tool.configuration.columns[g.rtv.sensorSelector.selectedSensor] = newSensorName
            g.tool.configuration.columnType[g.rtv.sensorSelector.selectedSensor] = type
            g.tool.configuration.columnOption[g.rtv.sensorSelector.selectedSensor] = option
            g.tool.configuration.columnUnit[g.rtv.sensorSelector.selectedSensor] = unit
            update_list()
            update_sensors()
            check_for_time_column()
            g.tool.configuration.changed = True
            g.tool.configuration.coreChange = True
            g.rt.sensorSelector.wm_withdraw()
            

def check_for_time_column() -> bool:
    """ Check if time column exists in current configuration, and set some widgets as active/disabled.
    
        If not found, return False.
    """
    marker = False
    for i, column in enumerate(g.tool.configuration.columns):
        if g.tool.configuration.columnType[i] == 1:
            marker = True
    
    if marker:
        g.rt.vars["text20"].set("")
        g.rt.get_child("text20")['state'] = tk.DISABLED
        g.rt.get_child("label39")['state'] = tk.DISABLED
        return True
    else:
        g.rt.vars["text20"].set("")
        g.rt.get_child("text20")['state'] = tk.NORMAL
        g.rt.get_child("label39")['state'] = tk.NORMAL
        return False

def update_sensors():
    arr = g.tool.configuration.sensorToWatch.split("|")
    list14 = g.rt.get_child("list14")
    list14.delete(0, tk.END)
    for i in range(len(g.tool.configuration.columns)):
        if g.tool.configuration.columnType[i] not in [0, 1]:
            list14.insert(tk.END, g.tool.configuration.columns[i])
            if g.tool.configuration.columns[i] in arr:
                list14.selection_set(tk.END)

def update_list():
    """
    """
    mainlist = g.rt.get_child("mainlist")
    mainlist.delete(*mainlist.get_children())
    list9 = g.rt.get_child("list9")
    list3 = g.rt.get_child("list3")

    users = []
    cols = list9.size()
    mainlist['columns'] = [username for username in list9.get(0, tk.END)]
    for column in mainlist['columns']:
        mainlist.column(column, width=1, stretch=tk.NO)
    for i in range(list9.size()):
        users.append(list9.get(i))
    if g.tool.configuration.inputType == 1:
        list3Index = [*list3.get(0, tk.END)].index(list3.get(tk.ACTIVE))
        if len(g.tool.configuration.users) > list3Index:
            path = os.path.join(g.tool.configuration.users[list3Index].filePath, g.tool.configuration.users[list3Index].name)
            string = t.get_limited_str_from_file(path, 2000)
        if g.tool.configuration.lineSeparator == 10:
            string = string.replace(chr(10), "\n")
        elif g.tool.configuration.lineSeparator == 13: 
            string = string.replace(chr(13), "\n")
        
        if g.tool.configuration.columnSeparator == ord(","):
            string = string.replace(",", ".")
        
        if g.tool.configuration.columnSeparator == ord("\t"):
            string = string.replace("\t", ",")
        elif g.tool.configuration.columnSeparator == ord(" "):
            string = string.replace(" ", ",")
        arr = string.split("\n")
        if not t.is_array_empty(arr):
            for i in range(g.tool.configuration.skipLines, len(arr)):
                line = arr[i].split(",")
                if not t.is_array_empty(line):
                    rowToInsert = []
                    for j in range(cols):
                        if j < len(line):
                            rowToInsert.append(line[j])
                        else:
                            rowToInsert.append("")
                    mainlist.insert('', rowToInsert)    