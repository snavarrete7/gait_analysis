import src.model.globalvars as g

def command1_click():
    g.rtv.selectSubjects.valid = True
    g.rt.selectSubjects.wm_withdraw()

def command2_click():
    g.rtv.selectSubjects.valid = False
    g.rt.selectSubjects.wm_withdraw()

    