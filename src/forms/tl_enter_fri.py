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

def command1_click():
    """
    If name of FRI doesn't already exist, saves each pattern and fri under mydocFolderRoot.
    """
    friName = g.rt.enterFriVars["text1"]
    if friName == "":
        messagebox.showwarning("Please enter a name")
    else:
        if friName.lower() in [fri.name.lower() for fri in g.tool.configuration.fallRiskIndex]:
            messagebox.showwarning(message="This name already exists")
        else:
            list2 = g.rt.get_child("list2")
            list2Index = [*list2.get(0, tk.END)].index(list2.get(tk.ACTIVE))
            if g.tool.configuration.fallRiskIndex[list2Index].name != friName:
                t.change_all_FRI_names_for_subjects(g.tool.configuration.fallRiskIndex[list2Index].name, friName)
                g.tool.configuration.fallRiskIndex[list2Index].name = friName
            g.tool.configuration.fallRiskIndex[list2Index].forAll = g.rt.enterFriVars["check1"].get()

            if g.tool.configuration.fallRiskIndex[list2Index].forAll:
                currFri = g.tool.configuration.fallRiskIndex[list2Index]
                string = "\n".join([str(currFri.greenEnd), str(currFri.greenStart), str(currFri.yellowEnd), str(currFri.yellowStart), str(currFri.redEnd), str(currFri.redStart)]) + "\n"
                for component in g.tool.configuration.fallRiskIndex[list2Index].components:
                    string = string + "\n".join([component.elementName, str(component.weight), str(component.impact)]) + "\n"

                    pattern = t.get_pattern_by_name(component.elementName)
                    patternStr = "\n".join([pattern.formula[0], pattern.formula[1], pattern.formula[2], pattern.formula[3], pattern.formula[4], pattern.formula[5], pattern.description])
                    path = os.path.join(g.tool.myDocFolderRoot, "pattern", f'{t.safe_file_name(pattern.name)}.pattern')
                    t.save_str_to_file(path, patternStr)
                path = os.path.join(g.tool.myDocFolderRoot, "FRI", f'{t.safe_file_name(currFri.name)}.fri')
                t.save_str_to_file(path, string)
            else:
                currFri = g.tool.configuration.fallRiskIndex[list2Index]
                path = os.path.join(g.tool.myDocFolderRoot, "FRI", f'{t.safe_file_name(currFri.name)}.fri')
                if os.path.exists(path):
                    os.remove(path)
            g.tool.configuration.changed = True

        g.rt.enterFri.wm_withdraw()

def command2_click():
    g.rt.enterFri.wm_withdraw()
