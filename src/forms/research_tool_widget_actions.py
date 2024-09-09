import src.tools as t
import src.model.globalvars as g
from tkinter import messagebox
import datetime
datetime.datetime.now().date()

def command4_click():
    if g.tool.configuration.users[t.get_user_no(g.rt.vars["text1"].get())].filterChange:
        if messagebox.askyesno(f"You made major changes to the configuration.\nThe gait parameter need to be recalculated. This may last some time. Continue?"):
            if t.save_configuration(True):
                g.tool.configuration.users[t.get_user_no(g.rt.vars["text1"].get())].lastProcessedDate = ""
