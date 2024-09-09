import src.model.globalvars as g
import tkinter as tk
from tkinter import messagebox, filedialog
import os

def check3_click():
    if g.rt.userInfoVars["check3"].get() == True:
        g.rt.get_child("check2", g.rt.userInfo)['state'] = tk.NORMAL
    else:
        g.rt.get_child("check2", g.rt.userInfo)['state'] = tk.DISABLED

def command1_click():
    g.rtv.userInfo.valid = True
    g.rt.userInfo.wm_withdraw()

def command2_click():
    g.rtv.userInfo.valid = False
    g.rt.userInfo.wm_withdraw()

def command3_click():
    initDir = os.path.join(g.tool.myDocFolder, "configurations")
    fileFilter = ('Configurations', '*.configuration')
    dialogFilename = g.rt.userInfoVars["text9"].get()
    filename = filedialog.askopenfilename(filetypes=fileFilter, initialdir=initDir, initialfile=dialogFilename)
    if filename != "":
        if ".calibration" not in filename:
            filename += ".calibration"
        g.rt.userInfoVars["text9"].set(filename)
    

  
def list3_click(e: tk.Event):
    list3 = g.rt.get_child("list3", g.rt.userInfo)
    elementsSelected = list3.curselection()
    if len(elementsSelected) > 1:
        messagebox.showinfo(message="You can only select one Fall Risk Index for each subject")