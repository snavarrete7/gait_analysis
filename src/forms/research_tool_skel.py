import time
from enum import Enum
import math
import threading
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, font
# from tkinter.ttk import *
import re

import pandas as pd
from PIL import ImageTk, Image
from matplotlib import pyplot as plt

from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
# Implement the default Matplotlib key bindings.
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure

import src.forms.research_tool_utils as utils
import src.forms.tl_user_info as utilsUserInfo
import src.forms.tl_pattern_extraction as utilsPatternExtraction
import src.forms.tl_enter_fri as utilsEnterFri
import src.forms.tl_sensor_selector as utilsSensorSelector
import tkcalendar
import src.model.globalvars as g

from PIL import Image, ImageTk
from sqlalchemy import create_engine, text, Table, MetaData
import src.model.database as bd

"""
import matplotlib

matplotlib.use('TkAgg')

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg,
    NavigationToolbar2Tk
)
"""


class EventType:
    """
    Constants for event types of package Tkinter
    """
    leftClick = "<ButtonPress-1>"
    """A leftClick event will use the state of that widget before clicking, so a 
    selected item will appear as not selected if binding to this event type. To avoid that, use a listboxSelect or comboboxSelect... virtual events"""
    doubleLeftClick = "<Double-ButtonPress-1>"
    rightClick = "<ButtonPress-3>"
    doubleRightClick = "<Double-ButtonPress-3>"

    calendarDaySel = "<<CalendarSelected>>"
    calendarMonthChange = "<<CalendarMonthChanged>>"

    listboxSelect = "<<ListboxSelect>>"

    comboboxSelectionChanged = "<<ComboboxSelected>>"

    leftClickRelease = "<ButtonRelease-1>"


class ResearchToolGUI:
    def __init__(self):
        """
        Initialize dynamic form variables, forms and everything else.
        """
        self.vars = {}
        self.userInfoVars = {}
        self.patternExtractionVars = {}
        self.enterFriVars = {}
        self.sensorSelectorVars = {}

        self.root = tk.Tk()
        self.root.title("Infore gait analysis tool")
        self.root.state("zoomed")

        self.current_notebook = None
        self.current_notebook_name = None
        self.current_content_frame = None
        self.user = utils.User()
        self.check1 = None
        self.boton = None

        self.tab_to_show = None

        self.v_movement_roa = False
        self.v_acc_roa = False
        self.v_forces_roa = False
        self.ROASelected = False
        self.reset_graphs_roa = False

        self.v_movement_roc = False
        self.v_acc_roc = False
        self.v_forces_roc = False
        self.ROCSelected = False
        self.reset_graphs_roc = False

        self.v_movement_rga = False
        self.v_acc_rga = False
        self.v_forces_rga = False
        self.RGASelected = False
        self.reset_graphs_rga = False

        self.v_movement_rgc = False
        self.v_acc_rgc = False
        self.v_forces_rgc = False
        self.RGCSelected = False
        self.reset_graphs_rgc = False

        self.databaseUsed = False

        self._init_menus()
        self._init_buttons()

        self.create_main_notebook()

        self.sensorHealth = self._init_toplevel_sensor_health()
        self.selectSubjects = self._init_toplevel_select_subjects()
        self.userInfo = self._init_toplevel_user_info()
        self.patternExtraction = self._init_toplevel_pattern_extraction()
        self.enterFri = self._init_toplevel_enter_fri()
        self.sensorSelector = self._init_toplevel_sensor_selector()

    def _init_buttons(self):
        button_frame = ttk.Frame(self.root)
        button_frame.pack(side="top")

        # Botón para abrir el primer notebook (principal)
        open_main_notebook_button = ttk.Button(button_frame, text="     GAIT Analysis      ", command=self.open_main_notebook)
        open_main_notebook_button.pack(side="left", padx=10, pady=10)

        # Botón para abrir el segundo notebook
        open_second_notebook_button = ttk.Button(button_frame, text="       RT Analysis      ", command=self.open_second_notebook)
        open_second_notebook_button.pack(side="left", padx=10, pady=10)

    def create_main_notebook(self):
        # Crear el Notebook principal
        self.tabs = ttk.Notebook(self.root, name="sstab1")
        self.create_notebook1_tabs()
        self.tabs.pack()
        self.current_notebook = self.tabs
        self.current_notebook_name = self.tabs.winfo_name()

    def create_second_notebook(self):
        # Crear el Notebook principal
        self.tabs2 = ttk.Notebook(self.root, name="sstab2", width=1700, height=1100) #800
        self.create_notebook2_tabs(self.tabs2)
        self.tabs2.pack()
        self.current_notebook = self.tabs2
        self.current_notebook_name = self.tabs2.winfo_name()

    def create_notebook1_tabs(self):
        dataInputSelection = self._init_data_input_selection(self.tabs)
        rawDataFiltering = self._init_raw_data_filtering(self.tabs)
        gaitParameterDefinition = self._init_gait_parameter_definition(self.tabs)
        gaitParameterHistory = self._init_gait_parameter_history(self.tabs)
        patternExtraction = self._init_pattern_extraction(self.tabs)
        fallRiskIndexDefinition = self._init_fall_risk_index_definition(self.tabs)
        factSheet = self._init_fact_sheet(self.tabs)

        self.tabs.add(dataInputSelection, text=dataInputSelection.winfo_name())
        self.tabs.add(rawDataFiltering, text=rawDataFiltering.winfo_name())
        self.tabs.add(gaitParameterDefinition, text=gaitParameterDefinition.winfo_name())
        self.tabs.add(gaitParameterHistory, text=gaitParameterHistory.winfo_name())
        self.tabs.add(patternExtraction, text=patternExtraction.winfo_name())
        self.tabs.add(fallRiskIndexDefinition, text=fallRiskIndexDefinition.winfo_name())
        self.tabs.add(factSheet, text=factSheet.winfo_name())

    def create_notebook2_tabs(self, notebook):
        patient_tab = self.patient_tab_new_module(notebook)

        if self.ROASelected:
            tab1 = self.ROA(notebook)
        else:
            tab1 = self.load_ROA(notebook)

        if self.ROCSelected:
            tab2 = self.ROC(notebook)
        else:
            tab2 = self.load_ROC(notebook)

        if self.RGASelected:
            tab3 = self.RGA(notebook)
        else:
            tab3 = self.load_RGA(notebook)

        if self.RGCSelected:
            tab4 = self.RGC(notebook)
        else:
            tab4 = self.load_RGC(notebook)

        tab5 = self.overview_tab(notebook)

        notebook.add(patient_tab, text="       Patient data        ", padding=10)
        notebook.add(tab1, text="       ROA         ", padding=10)
        notebook.add(tab2, text="           ROC           ", padding=10)
        notebook.add(tab3, text="           RGA           ", padding=10)
        notebook.add(tab4, text="           RGC           ", padding=10)
        notebook.add(tab5, text= "      Overview        ", padding=10)

        if self.tab_to_show == "ROA":
            notebook.select(1)
        elif self.tab_to_show == "ROC":
            notebook.select(2)
        elif self.tab_to_show == "RGA":
            notebook.select(3)
        elif self.tab_to_show == "RGC":
            notebook.select(4)
        else:
            notebook.select(0)

    def open_second_notebook(self):
        if self.current_notebook:
            self.current_notebook.destroy()
            self.create_second_notebook()
            self.current_notebook = self.tabs2

    def open_main_notebook(self):
        # Reemplazamos el segundo Notebook con el Notebook principal
        if self.current_notebook:
            self.current_notebook.destroy()
            self.create_main_notebook()
            self.current_notebook = self.tabs

    def importDataIMU(self):
        path = utils.filedialog.askopenfilename(filetypes=[("Archivo Excel", "*.csv")])
        self.user.setIMUPath(path)
        self.user.IMUdata = utils.pd.read_csv(self.user.IMUPath, delimiter=";")

        data = utils.createDataframeIMU(path, self.user)
        columns = data.columns
        columns = columns[4:20]

        loading_window = tk.Toplevel(self.root)
        loading_window.title("Loading...")
        loading_window.geometry("300x200")
        x = self.root.winfo_x() + self.root.winfo_width() // 2 - loading_window.winfo_width() // 2
        y = (self.root.winfo_y() + self.root.winfo_height() // 2 - loading_window.winfo_height() // 2)
        loading_window.geometry(f"+{x}+{y}")
        label_loading = tk.Label(loading_window, text="Processing data... Please wait")
        label_loading.pack(padx=50, pady=20)
        loading_window.wm_transient(self.root)

        progress_var = tk.DoubleVar()
        progress_bar = ttk.Progressbar(loading_window, variable=progress_var, maximum=100)
        progress_bar.pack(pady=20)

        processing_thread = threading.Thread(target=utils.processIMUData, args=(data, columns, loading_window, self.user, progress_var))
        processing_thread.start()

        if self.current_notebook_name == "sstab2":
            self.current_notebook.destroy()
            self.create_second_notebook()

    def uploadDataIMU(self):
        path = utils.filedialog.askopenfilename(filetypes=[("Archivo Excel", "*.csv")])
        self.user.setIMUPath(path)
        self.user.IMUdata = utils.pd.read_csv(self.user.IMUPath, delimiter=";")

        data = utils.createDataframeIMU(path, self.user)
        columns = data.columns
        columns = columns[4:20]

        loading_window = tk.Toplevel(self.root)
        loading_window.title("Loading...")
        loading_window.geometry("300x200")
        x = self.root.winfo_x() + self.root.winfo_width() // 2 - loading_window.winfo_width() // 2
        y = (self.root.winfo_y() + self.root.winfo_height() // 2 - loading_window.winfo_height() // 2)
        loading_window.geometry(f"+{x}+{y}")
        label_loading = tk.Label(loading_window, text="Uploading data... Please wait")
        label_loading.pack(padx=50, pady=20)
        loading_window.wm_transient(self.root)

        progress_var = tk.DoubleVar()
        progress_bar = ttk.Progressbar(loading_window, variable=progress_var, maximum=100)
        progress_bar.pack(pady=20)

        processing_thread = threading.Thread(target=utils.processIMUDataBD, args=(data, columns, loading_window, self.user, progress_var))
        processing_thread.start()

        if self.current_notebook_name == "sstab2":
            self.current_notebook.destroy()
            self.create_second_notebook()

    def importDataPostu(self):
        path = utils.filedialog.askopenfilename(filetypes=[("Archivo de texto", "*.txt")])
        self.user.setPostuPath(path)

        utils.createDataframesPostu(self.user.postuPath, self.user)
        match = re.search(r'_(.*?)_(.*?)\.txt', path)
        id = match.group(2).lower()
        self.user.setID(id)

        if self.user.postuPath:
            messagebox.showinfo(title="Data imported", message="Data imported successfully")
        else:
            messagebox.showinfo(title="Data imported", message="Error importing data")

        if self.current_notebook_name == "sstab2":
            self.current_notebook.destroy()
            self.create_second_notebook()

    def uploadDataPostu(self):
        path = utils.filedialog.askopenfilename(filetypes=[("Archivo de texto", "*.txt")])
        self.user.setPostuPath(path)

        utils.createDataframesPostu(self.user.postuPath, self.user)
        match = re.search(r'_(.*?)_(.*?)\.txt', path)
        id = match.group(2).lower()
        self.user.setID(id)

        database = bd.Database()
        engine = database.engine

        with engine.connect() as con:
            query = text("SELECT COUNT(*) FROM users WHERE id = :id")
            resultq = con.execute(query, {'id': id}).scalar()

        if resultq > 0:
            messagebox.showinfo(title="Error", message="User " + id + " already exists in database")
        else:
            try:
                dfDataUser = self.user.dataUser
                dfDataUser.to_sql(name='dataUser', con=engine, if_exists='append', index=False)

                dfDataRomberg = self.user.dataRombergPostu
                dfDataRomberg.to_sql(name='dataRombergPostu', con=engine, if_exists='append', index=False)

                dfDataRombergXY = self.user.dataRombergPostu_XY
                dfDataRombergXY = dfDataRombergXY.drop(dfDataRombergXY.columns[-1], axis=1)
                dfDataRombergXY.to_sql(name='dataRombergPostu_XY', con=engine, if_exists='append', index=False)

                dfDataRombergfXfY = self.user.dataRombergPostu_FxFy
                dfDataRombergfXfY = dfDataRombergfXfY.drop(dfDataRombergfXfY.columns[-1], axis=1)
                dfDataRombergfXfY.to_sql(name='dataRombergPostu_FxFy', con=engine, if_exists='append', index=False)

                id = self.user.id
                nombre = dfDataUser["Nombre"][0]
                apellidos = dfDataUser["Apellidos"][0]

                auxframe = pd.DataFrame({'ID': [id], 'Nombre': [nombre], 'Apellidos': [apellidos]})
                auxframe.to_sql(name='users', con=engine, if_exists='append', index=False)

                messagebox.showinfo(title="Info", message="Data uploaded successfully for user " + id)

            except Exception as e:
                messagebox.showinfo(title="Error", message=(f"Error uploading data: {e}"))


        if self.current_notebook_name == "sstab2":
            self.current_notebook.destroy()
            self.create_second_notebook()

    def userSelection(self):

        user_selection_w = tk.Toplevel(self.root)
        user_selection_w.title("User selection")
        user_selection_w.geometry("500x500")
        user_selection_w.geometry(f"+{600}+{200}")

        database = bd.Database()
        engine = database.engine

        with engine.connect() as con:
            query = text("SELECT * FROM users")
            resultq = con.execute(query)

        tk.Label(user_selection_w, text="ID", font=("Arial", 12,"bold")).grid(row=0, column=0, padx=10, pady=10)
        tk.Label(user_selection_w, text="NAME", font=("Arial", 12, "bold")).grid(row=0, column=1, padx=10, pady=10)
        tk.Label(user_selection_w, text="SUBNAME", font=("Arial", 12, "bold")).grid(row=0, column=2, padx=10, pady=10)
        row = 1
        for res in resultq:
            idUser = res[0]
            name = res[1]
            subname = res[2]

            tk.Label(user_selection_w, text=idUser, font=("Arial", 12,)).grid(row=row, column=0, padx=10, pady=10)
            tk.Label(user_selection_w, text=name, font=("Arial", 12,)).grid(row=row, column=1, padx=10, pady=10)
            tk.Label(user_selection_w, text=subname, font=("Arial", 12,)).grid(row=row, column=2, padx=10, pady=10)
            tk.Button(user_selection_w, bg="orange", text="Import", command=lambda x=idUser: self.importDataFromDatabase(x)).grid(row=row, column=3, padx=10, pady=10)
            row = row + 1

        user_selection_w.wm_transient(self.root)

    def importDataFromDatabase(self, id):
        print(f"Mostrando datos del usuario con ID: {id}")

        database = bd.Database()
        engine = database.engine

        self.user.id = id
        self.user.setIMUPath("")
        self.user.setPostuPath("")
        dfDataImu = pd.read_sql_query('SELECT * FROM dataimu WHERE id = "' + id + '"', con=engine)
        self.user.setDataIMU(dfDataImu)
        dfDataUser = pd.read_sql_query('SELECT * FROM datauser WHERE ID = "' + id + '"', con=engine)
        self.user.setDataUser(dfDataUser)
        dfDataRombergPostu = pd.read_sql_query('SELECT * FROM datarombergpostu WHERE ID = "' + id + '"', con=engine)
        self.user.setDataRomberg(dfDataRombergPostu)
        dfDataRombergPostu_XY = pd.read_sql_query('SELECT * FROM datarombergpostu_xy WHERE ID = "' + id + '"', con=engine)
        self.user.setDataRomberg_XY(dfDataRombergPostu_XY)
        dfDataRombergPostu_fXfY = pd.read_sql_query('SELECT * FROM datarombergpostu_fxfy WHERE ID = "' + id + '"', con=engine)
        self.user.setDataRomberg_FxFy(dfDataRombergPostu_fXfY)
        dicFrame = dfDataUser.to_dict(orient="records")
        self.user.setDicUser(dicFrame)

        self.user.testDone = [False, False, False, False]
        dic = self.user.dicUser[0]
        if dic['Nº_ROA'] >= 1:
            self.user.testDone[0] = True
        if dic['Nº_ROC'] >= 1:
            self.user.testDone[1] = True
        if dic['Nº_RGA'] >= 1:
            self.user.testDone[2] = True
        if dic['Nº_RGC'] >= 1:
            self.user.testDone[3] = True

        messagebox.showinfo(title="Info", message="Data imported successfully for user " + id)

        if self.current_notebook_name == "sstab2":
            self.current_notebook.destroy()
            self.create_second_notebook()


    def run(self):
        utils.form_load()

        # DEBUG
        utils.mnuopenconfig_click()

        self.root.mainloop()

    def _init_menus(self):
        # recommended for menus
        self.root.option_add('*tearOff', tk.FALSE)

        menubar = tk.Menu(self.root)
        self.root['menu'] = menubar

        menuConfig = tk.Menu(menubar)
        menuOptions = tk.Menu(menubar)
        menuInfo = tk.Menu(menubar)

        menuBD = tk.Menu(menubar)
        menuUploadFiles = tk.Menu(menuBD)
        menuUploadFiles.add_command(label="Upload IMU data", command=self.uploadDataIMU)
        menuUploadFiles.add_command(label="Upload Posturographer data", command=self.uploadDataPostu)
        menuBD.add_cascade(label="Upload files", menu=menuUploadFiles)
        menuBD.add_command(label="Import patient data from Database", command=self.userSelection)

        menuData = tk.Menu(menubar)
        menuImportData = tk.Menu(menuData)
        menuImportData.add_command(label="Import data IMU", command=self.importDataIMU)
        menuImportData.add_command(label="Import data Posturographer", command=self.importDataPostu)
        menuData.add_cascade(menu=menuImportData, label="Import local data")
        menubar.add_cascade(menu=menuData, label='Local data')

        menubar.add_cascade(menu=menuBD, label='Data Base')

        menubar.add_cascade(menu=menuConfig, label='Configuration')
        menubar.add_cascade(menu=menuOptions, label='Options')
        menubar.add_cascade(menu=menuInfo, label="Info")
        # menuData.add_command(label="Export data")
        menuConfig.add_command(label="Open configuration", command=utils.mnuopenconfig_click)
        menuConfig.add_command(label="Save configuration", command=utils.mnusaveconfig_click)

    def patient_tab_new_module(self, parent: ttk.Notebook) -> tk.Frame:

        fuente = font.Font(family="Arial", size=20, weight="bold", underline=True)

        mainframe = tk.Frame(parent, name="patient tab")
        mainframe.grid()


        if self.user.postuPath is None :

            tk.Label(mainframe, text="Please, load the posturographer file (.txt) to see the information", font=("Arial", 16, "bold")).grid(row=0,column=0,pady=10, padx=10)
            self.img_help_patient = ImageTk.PhotoImage(Image.open("app/help2.png"))
            self.buttonHelp_patient = tk.Button(mainframe, image=self.img_help_patient, borderwidth=0,
                                            command=lambda: utils.help_patient())
            self.buttonHelp_patient.place(x=1600, y=10)

        else:
            pacientData = self.user.dataUser.iloc[0]
            etiquetasData = []
            etiquetasHeader = ['Nº Historial', 'Nombre', 'Apellidos', 'Sexo', 'DNI', 'Fecha Nacimiento', 'Talla (mm)', 'Peso (Kg)', 'Fecha Pruebas', 'Edad', 'Observaciones', 'Esc.Func.Ap.Locomotor', 'Valor EFAL', 'Esc.Vestibular', 'Conclusiones', 'Valoración GLB', 'Nº ROA', 'Valoración ROA', 'Repetición ROA', 'Estabilidad ML ROA', 'Estabilidad AP ROA', 'Nº ROC', 'Valoración ROC', 'Repetición ROC', 'Estabilidad ML ROC', 'Estabilidad AP ROC', 'Nº RGA', 'Valoración RGA', 'Repetición RGA', 'Estabilidad ML RGA', 'Estabilidad AP RGA', 'Nº RGC', 'Valoración RGC', 'Repetición RGC', 'Estabilidad ML RGC', 'Estabilidad AP RGC', 'Nº_RAV', 'Val_RAV', 'Rep_RAV', 'EstML_RAV']
            for i in range(1, 66):
                if i != "" and i != "-":
                    etiquetasData.append(pacientData.iloc[i])

            tk.Label(mainframe, text="Personal Data:", font=fuente).grid(row=0, column=0, pady=10)
            i = 0
            for j in range(0, 8):
                lb1 = tk.Label(mainframe, text=etiquetasHeader[j] + ": ", font=("TkDefaultFont",10,"bold"))
                lb1.grid(row=i + 1, column=0, pady=5)
                i = i + 1
            tk.Label(mainframe, text=etiquetasHeader[9] + ": ", font=("TkDefaultFont",10,"bold")).grid(row=9, column=0, pady=5)

            i = 0
            for j in range(0, 8):
                if etiquetasData[j] == "":
                    lb2 = tk.Label(mainframe, text="-", justify="left")
                    lb2.grid(row=i + 1, column=2, pady=5)
                    i = i + 1
                else:
                    lb2 = tk.Label(mainframe, text=etiquetasData[j], justify="left")
                    lb2.grid(row=i + 1, column=2, pady=5)
                    i = i + 1
            lb2 = tk.Label(mainframe, text=etiquetasData[9])
            lb2.grid(row=i + 1, column=2, pady=5)

            tk.Label(mainframe, text="              ", font=("Arial", 18)).grid(row=0, column=3, pady=5)
            tk.Label(mainframe, text="Test Data:", font=fuente).grid(row=0, column=4, pady=10)
            tk.Label(mainframe, text=etiquetasHeader[8] + ": ", font=("TkDefaultFont",10,"bold")).grid(row=1, column=4, pady=5)
            tk.Label(mainframe, text=etiquetasData[8]).grid(row=1, column=5, pady=5)
            row = 1
            col = 4
            for j in range(10, 36):
                if j % 9 == 0 or j % 9 == 9:
                    col = col + 2
                    row = 1
                else:
                    row = row + 1

                lb1 = tk.Label(mainframe, text=etiquetasHeader[j] + ": ", font=("TkDefaultFont",10,"bold"))
                lb1.grid(row=row, column=col, pady=5)

            row = 1
            col = 5
            for j in range(10, 36):
                if j % 9 == 0 or j % 9 == 9:
                    col = col + 2
                    row = 1
                else:
                    row = row + 1
                lb1 = tk.Label(mainframe, text=etiquetasData[j])
                lb1.grid(row=row, column=col, pady=5)

            dataframe = pd.DataFrame(self.user.dicUser)
            df_roa = dataframe[['Nº_ROA', 'Val_ROA', 'Rep_ROA', 'EstML_ROA', 'EstAP_ROA']]
            df_roc = dataframe[['Nº_ROC', 'Val_ROC', 'Rep_ROC', 'EstML_ROC', 'EstAP_ROC']]
            df_rga = dataframe[['Nº_RGA', 'Val_RGA', 'Rep_RGA', 'EstML_RGA', 'EstAP_RGA']]
            df_rgc = dataframe[['Nº_RGC', 'Val_RGC', 'Rep_RGC', 'EstML_RGC', 'EstAP_RGC']]

            tv_roa = ttk.Treeview(mainframe, columns=("col1"))
            tv_roa.configure(height=5)
            tv_roa.column("#0", width=100)
            tv_roa.column("col1", width=100, anchor="center")
            tv_roa.heading("#0", text="ROA")
            tv_roa.heading("col1", text="Valores")
            for col in range(len(df_roa.columns)):
                tv_roa.insert("",0,text=df_roa.columns[col],values=(df_roa.iloc[0,col]))
            tv_roa.grid(row=11, column=0, pady=40, padx=10)

            tv_roc = ttk.Treeview(mainframe, columns=("col1"))
            tv_roc.configure(height=5)
            tv_roc.column("#0", width=100)
            tv_roc.column("col1", width=100, anchor="center")
            tv_roc.heading("#0", text="ROC")
            tv_roc.heading("col1", text="Valores")
            for col in range(len(df_roc.columns)):
                tv_roc.insert("", 0, text=df_roc.columns[col], values=(df_roc.iloc[0, col]))
            tv_roc.grid(row=11, column=2, pady=40, padx=10)

            tv_rga = ttk.Treeview(mainframe, columns=("col1"))
            tv_rga.configure(height=5)
            tv_rga.column("#0", width=100)
            tv_rga.column("col1", width=100, anchor="center")
            tv_rga.heading("#0", text="RGA")
            tv_rga.heading("col1", text="Valores")
            for col in range(len(df_roc.columns)):
                tv_rga.insert("", 0, text=df_rga.columns[col], values=(df_rga.iloc[0, col]))
            tv_rga.grid(row=11, column=3, pady=40, padx=10)

            tv_rgc = ttk.Treeview(mainframe, columns=("col1"))
            tv_rgc.configure(height=5)
            tv_rgc.column("#0", width=100)
            tv_rgc.column("col1", width=100, anchor="center")
            tv_rgc.heading("#0", text="RGC")
            tv_rgc.heading("col1", text="Valores")
            for col in range(len(df_roc.columns)):
                tv_rgc.insert("", 0, text=df_rgc.columns[col], values=(df_rgc.iloc[0, col]))
            tv_rgc.grid(row=11, column=4, pady=40, padx=10)

        return mainframe

    def tab1_new_module(self, parent: ttk.Notebook) -> tk.Frame:

        mainframe = tk.Frame(parent, name="tab 1")
        radio_buttons_frame = tk.Frame(mainframe)
        #opcion_var = tk.IntVar()
        opcion_var = tk.StringVar(value="Option 1")
        radiobutton1 = ttk.Radiobutton(radio_buttons_frame, text="ROA", variable=opcion_var, value="Option 1",command=lambda: self.ROA(mainframe))
        radiobutton1.grid(row=0, column=0)
        radiobutton2 = ttk.Radiobutton(radio_buttons_frame, text="ROC", variable=opcion_var,value="Option 2", command=lambda: self.open_contentFramePOSTU_tab1(mainframe))
        radiobutton2.grid(row=0, column=1)
        radiobutton3 = ttk.Radiobutton(radio_buttons_frame, text="RGA", variable=opcion_var,
                                       value="Option 3", command=lambda: self.open_contentFramePOSTU_tab1(mainframe))
        radiobutton3.grid(row=0, column=2)
        radiobutton4 = ttk.Radiobutton(radio_buttons_frame, text="RGC", variable=opcion_var,
                                       value="Option 4", command=lambda: self.open_contentFramePOSTU_tab1(mainframe))
        radiobutton4.grid(row=0, column=3)
        # content_frame = self.content_frame_tab1(mainframe)

        radio_buttons_frame.grid(row=0, column=0, sticky="ew")

        # Se pueden utilizar los de ttk que son mas visuales pero no se puede marcar automaticamente

        #content_frame.grid()
        mainframe.grid()

        return mainframe



    def content_frame_IMU_tab1(self, parent: ttk.Frame) -> tk.Frame:
        mainframe = tk.Frame(parent)
        #mainframe = utils.ScrollableFrame(parent)
        self.current_content_frame = mainframe

        if self.user.dataIMU is None:
            label_file_not_loaded = tk.Label(mainframe, text="Please load the IMU file (.csv)").grid(row=0, column=0)
        else:
            """
            tree = ttk.Treeview(mainframe, columns=list(self.user.dataIMU.columns), show="headings")
            for col in self.user.dataIMU.columns:
                tree.heading(col, text=col)
                tree.column(col, width=50)
            for i, row in self.user.dataIMU.head(10).iterrows():
                tree.insert("", "end", values=list(row))

            tree.grid(row=0, column=0)"""

            """
            frame_buttons_nextpage = ttk.Frame(mainframe)
            btn_next = ttk.Button(frame_buttons_nextpage, text="<-")
            btn_next.grid(row=0, column=0)
            btn_back = ttk.Button(frame_buttons_nextpage, text="->")
            btn_back.grid(row=0, column=1)
            frame_buttons_nextpage.grid(row=4, column=0,sticky="w")"""

            data = self.user.dataIMU[self.user.dataIMU["action"] == 1]
            ROA_list = data.index[data["action"] == 1].tolist()
            indicesTestROA = utils.encontrar_primer_y_ultimo_valores(ROA_list)

            dataTestsList = []
            lenth = len(indicesTestROA)
            i = 0
            while i < lenth:
                start = indicesTestROA[i]
                stop = indicesTestROA[i + 1]
                new_dataframe = data.loc[start:stop]
                new_dataframe.reset_index(inplace=True, drop=True)
                dataTestsList.append(new_dataframe)
                i = i + 2

            tk.Label(mainframe, text="Analysis made by the IMU device").grid(row=0, column=0)


            tk.Label(mainframe, text="Movement made by the patient (Gravity vector X - Y)").grid(row=1, column=0, sticky="w")
            frame_graphics1 = utils.graphsDisplacementIMU(mainframe,dataTestsList)
            frame_graphics1.grid(row=2, column=0)

            tk.Label(mainframe, text="Analysis made by the Posturographer").grid(row=0, column=1)


            tk.Label(mainframe, text="Movement made by the patient (Gravity vector X - Y)").grid(row=1, column=1,sticky="w")
            frame_graphics2 = utils.graphsDisplacementIMU(mainframe, dataTestsList)
            frame_graphics2.grid(row=2, column=1)

            tk.Label(mainframe, text="Acceleration").grid(row=3, column=0, sticky="w")
            frame_graphics3 = utils.lineGraphIMU(mainframe, dataTestsList, ["accelerometerX","accelerometerY","accelerometerZ"])
            frame_graphics3.grid(row=4, column=0, sticky="w")

            """
            tk.Label(mainframe, text="TEXTO A COMPLETAR").grid(row=2, column=0, sticky="w")
            frame_graphics2 = utils.lineGraphIMU(mainframe, dataTestsList, "accelerometerX")
            frame_graphics2.grid(row=3, column=0,sticky="w")"""


        mainframe.grid()
        #mainframe.pack(side="top", fill="both", expand=True)
        return mainframe

    def reset_variables(self):
        self.tab_to_show = None
        self.v_movement_roa = False
        self.v_acc_roa = False
        self.v_forces_roa = False
        #self.ROASelected = False
        self.reset_graphs_roa = False
        self.v_movement_roc = False
        self.v_acc_roc = False
        self.v_forces_roc = False
        #self.ROCSelected = False
        self.reset_graphs_roc = False
        self.v_movement_rga = False
        self.v_acc_rga = False
        self.v_forces_rga = False
        #self.RGASelected = False
        self.reset_graphs_rga = False
        self.v_movement_rgc = False
        self.v_acc_rgc = False
        self.v_forces_rgc = False
        #self.RGCSelected = False
        self.reset_graphs_rgc = False

    def load_ROA(self, parent: ttk.Notebook):

        fuente = font.Font(family="TkDefaultFont", size=20, weight="bold")

        mainframe = ttk.Frame(parent, name="load_roa")
        self.current_content_frame = mainframe

        ttk.Label(mainframe, text="Graph selection: ", font=fuente).grid(row=0, column=0, padx=650, pady=(100, 10))

        self.img_help = ImageTk.PhotoImage(Image.open("app/help2.png"))
        self.button = tk.Button(mainframe, image=self.img_help,borderwidth=0, command=lambda:utils.help_graphselection("ROA"))
        self.button.place(x=10,y=10,width=50, height=50)

        chk_v_movement_roa = tk.IntVar()
        chk_v_acc_roa = tk.IntVar()
        chk_v_forces_roa = tk.IntVar()

        chk_movement_roa = tk.Checkbutton(mainframe, text='Movement made by the patient', variable=chk_v_movement_roa,
                                          font=("Arial", 14))
        chk_movement_roa.grid(row=1, column=0, padx=650, pady=5, sticky="w")

        chk_acc_roa = tk.Checkbutton(mainframe, text='Acceleration', variable=chk_v_acc_roa, font=("Arial", 14))
        chk_acc_roa.grid(row=2, column=0, padx=650, pady=5, sticky="w")

        chk_forces_roa = tk.Checkbutton(mainframe, text='Forces', variable=chk_v_forces_roa, font=("Arial", 14))
        chk_forces_roa.grid(row=3, column=0, padx=650, pady=5, sticky="w")

        btn_load_graphs_roa = tk.Button(mainframe, text='Load graphs', bg="orange", font=("TkDefaultFont", 14), command=lambda: self.buton_load_ROA(chk_v_movement_roa.get(), chk_v_acc_roa.get(), chk_v_forces_roa.get()))
        btn_load_graphs_roa.grid(row=4, column=0, padx=650, pady=(10, 20), sticky="e")

        mainframe.grid(sticky="nsew")
        return mainframe

    def buton_load_ROA(self, movement, acceleration, forces):
        #self.reset_variables()
        self.ROASelected = True
        self.tab_to_show = "ROA"
        self.reset_graphs_roa = False
        if movement == 1:
            self.v_movement_roa = True
        if acceleration == 1:
            self.v_acc_roa = True
        if forces == 1:
            self.v_forces_roa = True

        if self.current_notebook_name == "sstab2":
            self.current_notebook.destroy()
            self.create_second_notebook()

    def buton_reset_graphs_ROA(self):
        self.tab_to_show = "ROA"
        self.reset_graphs_roa = True
        self.reset_graphs_roc = False
        self.reset_graphs_rga = False
        self.ROASelected = False
        self.v_forces_roa = False
        self.v_acc_roa = False
        self.v_movement_roa = False

        if self.current_notebook_name == "sstab2":
            self.current_notebook.destroy()
            self.create_second_notebook()



    def ROA(self, parent: ttk.Frame) -> tk.Frame:

        fuente = font.Font(family="Arial", size=20, weight="bold", underline=True)

        mainframe = ttk.Frame(parent, name="roa")
        self.current_content_frame = mainframe
        mainframe.config(takefocus=0)
        mainframe.config(borderwidth=0, relief="flat")
        mainframe.grid(sticky="nsew")


        myframe = utils.ScrollableFrame(mainframe)
        myframe.scrollable_frame.focus_set()
        myframe.grid(sticky="nsew")

        mainframe.grid_rowconfigure(0, weight=1)
        mainframe.grid_columnconfigure(0, weight=1)

        if self.user.IMUPath != None:

            if self.user.testDone[0] == True:
                data = self.user.dataIMU[self.user.dataIMU["action"] == 1]
                ROA_list = data.index[data["action"] == 1].tolist()
                indicesTestROA = utils.encontrar_primer_y_ultimo_valores(ROA_list)

                longitud = len(indicesTestROA)
                listElim = []
                for i in range(0, longitud, 2):
                    ele1 = indicesTestROA[i]
                    ele2 = indicesTestROA[i + 1]
                    dif = ele2 - ele1
                    if dif > 1300 or dif < 250:
                        listElim.append(ele1)
                        listElim.append(ele2)
                for i in listElim:
                    indicesTestROA.remove(i)

                dataTestsList = []
                lenth = len(indicesTestROA)
                i = 0
                while i < lenth:
                    start = indicesTestROA[i]
                    stop = indicesTestROA[i + 1]
                    new_dataframe = data.loc[start:stop]
                    new_dataframe.reset_index(inplace=True, drop=True)
                    dataTestsList.append(new_dataframe)
                    i = i + 2

                ttk.Label(myframe.scrollable_frame, text="", font=fuente).grid(row=0, column=0, pady=10, padx=10, sticky="w")
                self.img_help_roa = ImageTk.PhotoImage(Image.open("app/help2.png"))
                self.buttonHelp_roa = tk.Button(mainframe, image=self.img_help_roa, borderwidth=0,
                                        command=lambda: utils.help_roa())
                self.buttonHelp_roa.place(x=10, y=10)

                btn_select_grapsh_roa = tk.Button(myframe.scrollable_frame,text='Load graphs', bg="orange", command=lambda: self.buton_reset_graphs_ROA())
                btn_select_grapsh_roa.place(x=65, y=15)

                tk.Label(myframe.scrollable_frame, text="Analysis made by the IMU device", font=fuente).grid(row=1, column=0)

                if self.v_movement_roa:
                    tk.Label(myframe.scrollable_frame, text="Trajectory made by the patient", font=("TkDefaultFont", 12, "bold")).grid(row=2,column=0,sticky="w", pady=15, padx=5)
                    frame_graphics1 = utils.trajectoryIMU(myframe.scrollable_frame, dataTestsList, "ROA")
                    frame_graphics1.grid(row=3, column=0, padx=5, pady=5)

                tk.Label(myframe.scrollable_frame, text="Analysis made by the Posturographer", font=fuente).grid(row=1, column=1)

                if self.v_movement_roa:
                    tk.Label(myframe.scrollable_frame, text="Trajectory made by the patient", font=("TkDefaultFont", 12, "bold")).grid(row=2,column=1,sticky="w", pady=15, padx=5)
                    frame_graphics2 = utils.graphsDisplacementPOSTU(myframe.scrollable_frame, self.user, "ROA")
                    frame_graphics2.grid(row=3, column=1)

                if self.v_acc_roa:
                    tk.Label(myframe.scrollable_frame, text="Acceleration catched by the IMU device", font=("TkDefaultFont", 12, "bold")).grid(row=4, column=0, sticky="w", pady=15, padx=5)
                    frame_graphics3 = utils.lineGraphIMU(myframe.scrollable_frame, dataTestsList, ["accelerometerX", "accelerometerY", "accelerometerZ"])
                    frame_graphics3.grid(row=5, column=0)

                if self.v_forces_roa:
                    tk.Label(myframe.scrollable_frame, text="Forces catched by the Posturographer", font=("TkDefaultFont", 12, "bold")).grid(row=4, column=1, sticky="w", pady=15, padx=5)
                    frame_graphics4 = utils.lineGraphForcesPOSTU(myframe.scrollable_frame, self.user, "ROA")
                    frame_graphics4.grid(row=5, column=1, sticky="w")
            else:
                ttk.Label(myframe.scrollable_frame, text="The user has not performed ROA type testing", font=("TkDefaultFont", 15, "bold")).grid(row=0, column=0, pady=10, padx=10, sticky="w")
        else:
            messagebox.showwarning(title="Warning", message="Please load the IMU file.\nData -> Import Data -> Import Data IMU")
            self.tab_to_show = "ROA"
            self.reset_graphs_roa = True
            self.reset_graphs_roc = False
            self.reset_graphs_rga = False
            self.ROASelected = False
            self.v_forces_roa = False
            self.v_acc_roa = False
            self.v_movement_roa = False

            if self.current_notebook_name == "sstab2":
                self.current_notebook.destroy()
                self.create_second_notebook()


        return mainframe

    def load_ROC(self, parent: ttk.Notebook):
        fuente = font.Font(family="TkDefaultFont", size=20, weight="bold")
        mainframe = ttk.Frame(parent, name="load_roc")
        self.current_content_frame = mainframe

        ttk.Label(mainframe, text="Graph selection: ", font=fuente).grid(row=0, column=0, padx=650, pady=(100, 10))

        self.img_help2 = ImageTk.PhotoImage(Image.open("app/help2.png"))
        self.button2 = tk.Button(mainframe, image=self.img_help2, borderwidth=0, command=lambda: utils.help_graphselection("ROC"))
        self.button2.place(x=10, y=10, width=50, height=50)

        chk_v_movement_roc = tk.IntVar()
        chk_v_acc_roc = tk.IntVar()
        chk_v_forces_roc = tk.IntVar()

        chk_movement_roc = tk.Checkbutton(mainframe, text='Movement made by the patient', variable=chk_v_movement_roc,
                                          font=("Arial", 14))
        chk_movement_roc.grid(row=1, column=0, padx=650, pady=5, sticky="w")

        chk_acc_roc = tk.Checkbutton(mainframe, text='Acceleration', variable=chk_v_acc_roc, font=("Arial", 14))
        chk_acc_roc.grid(row=2, column=0, padx=650, pady=5, sticky="w")

        chk_forces_roc = tk.Checkbutton(mainframe, text='Forces', variable=chk_v_forces_roc, font=("Arial", 14))
        chk_forces_roc.grid(row=3, column=0, padx=650, pady=5, sticky="w")

        btn_load_graphs_roc = tk.Button(mainframe, text='Load graphs', bg="orange", font=("TkDefaultFont", 14), command=lambda: self.buton_load_ROC(chk_v_movement_roc.get(), chk_v_acc_roc.get(), chk_v_forces_roc.get()))
        btn_load_graphs_roc.grid(row=4, column=0, padx=650, pady=(10, 20), sticky="e")

        mainframe.grid(sticky="nsew")
        return mainframe

    def buton_load_ROC(self, movement, acceleration, forces):
        #self.reset_variables()
        self.ROCSelected = True
        self.tab_to_show = "ROC"
        self.reset_graphs_roc = False
        if movement == 1:
            self.v_movement_roc = True
        if acceleration == 1:
            self.v_acc_roc = True
        if forces == 1:
            self.v_forces_roc = True

        if self.current_notebook_name == "sstab2":
            self.current_notebook.destroy()
            self.create_second_notebook()

    def buton_reset_graphs_ROC(self):
        self.tab_to_show = "ROC"
        self.reset_graphs_roc = True
        self.reset_graphs_roa = False
        self.reset_graphs_rga = False
        self.ROCSelected = False
        self.v_forces_roc = False
        self.v_acc_roc = False
        self.v_movement_roc = False

        if self.current_notebook_name == "sstab2":
            self.current_notebook.destroy()
            self.create_second_notebook()


    def ROC(self, parent: ttk.Frame) -> tk.Frame:

        fuente = font.Font(family="Arial", size=20, weight="bold", underline=True)

        mainframe = ttk.Frame(parent, name="roc")
        mainframe.config(takefocus=0)
        mainframe.config(borderwidth=0, relief="flat")
        mainframe.grid(sticky="nsew")

        myframe = utils.ScrollableFrame(mainframe)
        myframe.scrollable_frame.focus_set()
        myframe.grid(sticky="nsew")

        mainframe.grid_rowconfigure(0, weight=1)
        mainframe.grid_columnconfigure(0, weight=1)

        if self.user.IMUPath != None:
            if self.user.testDone[1] == True:
                data = self.user.dataIMU[self.user.dataIMU["action"] == 2]
                ROC_list = data.index[data["action"] == 2].tolist()
                indicesTestROC = utils.encontrar_primer_y_ultimo_valores(ROC_list)

                longitud = len(indicesTestROC)
                listElim = []
                for i in range(0, longitud, 2):
                    ele1 = indicesTestROC[i]
                    ele2 = indicesTestROC[i + 1]
                    dif = ele2 - ele1
                    if dif > 1300 or dif < 250:
                        listElim.append(ele1)
                        listElim.append(ele2)
                for i in listElim:
                    indicesTestROC.remove(i)

                dataTestsList = []
                lenth = len(indicesTestROC)
                i = 0
                while i < lenth:
                    start = indicesTestROC[i]
                    stop = indicesTestROC[i + 1]
                    new_dataframe = data.loc[start:stop]
                    new_dataframe.reset_index(inplace=True, drop=True)
                    dataTestsList.append(new_dataframe)
                    i = i + 2

                ttk.Label(myframe.scrollable_frame, text="", font=fuente).grid(row=0, column=0, pady=10, padx=10, sticky="w")
                self.img_help_roc = ImageTk.PhotoImage(Image.open("app/help2.png"))
                self.buttonHelp_roc = tk.Button(mainframe, image=self.img_help_roc, borderwidth=0,
                                                command=lambda: utils.help_roc())
                self.buttonHelp_roc.place(x=10, y=10)

                btn_select_grapsh_roc = tk.Button(myframe.scrollable_frame, text='Load graphs', bg="orange",
                                              command=lambda: self.buton_reset_graphs_ROC())
                btn_select_grapsh_roc.place(x=65, y=15)

                tk.Label(myframe.scrollable_frame, text="Analysis made by the IMU device", font=fuente).grid(row=1, column=0)

                if self.v_movement_roc:
                    tk.Label(myframe.scrollable_frame, text="Trajectory made by the patient", font=("TkDefaultFont", 12, "bold")).grid(row=2,column=0,sticky="w", pady=15, padx=5)
                    frame_graphics1 = utils.trajectoryIMU(myframe.scrollable_frame, dataTestsList, "ROC")
                    frame_graphics1.grid(row=3, column=0, padx=5, pady=5)

                tk.Label(myframe.scrollable_frame, text="Analysis made by the Posturographer", font=fuente).grid(row=1, column=1)

                if self.v_movement_roc:
                    tk.Label(myframe.scrollable_frame, text="Trajectory made by the patient", font=("TkDefaultFont", 12, "bold")).grid(row=2,column=1,sticky="w", pady=15, padx=5)
                    frame_graphics2 = utils.graphsDisplacementPOSTU(myframe.scrollable_frame, self.user, "ROC")
                    frame_graphics2.grid(row=3, column=1)

                if self.v_acc_roc:
                    tk.Label(myframe.scrollable_frame, text="Acceleration catched by the IMU device", font=("TkDefaultFont", 12, "bold")).grid(row=4, column=0, sticky="w", pady=15, padx=5)
                    frame_graphics3 = utils.lineGraphIMU(myframe.scrollable_frame, dataTestsList,
                                                         ["accelerometerX", "accelerometerY", "accelerometerZ"])
                    frame_graphics3.grid(row=5, column=0, sticky="w")

                if self.v_forces_roc:
                    tk.Label(myframe.scrollable_frame, text="Forces catched by the Posturographer", font=("TkDefaultFont", 12, "bold")).grid(row=4, column=1, sticky="w", pady=15, padx=5)
                    frame_graphics4 = utils.lineGraphForcesPOSTU(myframe.scrollable_frame, self.user, "ROC")
                    frame_graphics4.grid(row=5, column=1, sticky="w")
            else:
                ttk.Label(myframe.scrollable_frame, text="The user has not performed ROC type testing",
                          font=("TkDefaultFont", 15, "bold")).grid(row=0, column=0, pady=10, padx=10, sticky="w")
        else:
            messagebox.showwarning(title="Warning", message="Please load the IMU file.\nData -> Import Data -> Import Data IMU")
            self.tab_to_show = "ROC"
            self.reset_graphs_roc = True
            self.reset_graphs_roa = False
            self.reset_graphs_rga = False
            self.ROCSelected = False
            self.v_forces_roc = False
            self.v_acc_roc = False
            self.v_movement_roc = False

            if self.current_notebook_name == "sstab2":
                self.current_notebook.destroy()
                self.create_second_notebook()


        return mainframe

    def load_RGA(self, parent: ttk.Notebook):
        fuente = font.Font(family="TkDefaultFont", size=20, weight="bold")
        mainframe = ttk.Frame(parent, name="load_rga")
        self.current_content_frame = mainframe

        ttk.Label(mainframe, text="Graph selection: ", font=fuente).grid(row=0, column=0, padx=650, pady=(100, 10))

        self.img_help3 = ImageTk.PhotoImage(Image.open("app/help2.png"))
        self.button3 = tk.Button(mainframe, image=self.img_help3, borderwidth=0, command=lambda:utils.help_graphselection("RGA"))
        self.button3.place(x=10, y=10, width=50, height=50)

        chk_v_movement_rga = tk.IntVar()
        chk_v_acc_rga = tk.IntVar()
        chk_v_forces_rga = tk.IntVar()

        chk_movement_rga = tk.Checkbutton(mainframe, text='Movement made by the patient', variable=chk_v_movement_rga,
                                          font=("Arial", 14))
        chk_movement_rga.grid(row=1, column=0, padx=650, pady=5, sticky="w")

        chk_acc_rga = tk.Checkbutton(mainframe, text='Acceleration', variable=chk_v_acc_rga, font=("Arial", 14))
        chk_acc_rga.grid(row=2, column=0, padx=650, pady=5, sticky="w")

        chk_forces_rga = tk.Checkbutton(mainframe, text='Forces', variable=chk_v_forces_rga, font=("Arial", 14))
        chk_forces_rga.grid(row=3, column=0, padx=650, pady=5, sticky="w")

        btn_load_graphs_rga = tk.Button(mainframe, text='Load graphs', bg="orange", font=("TkDefaultFont", 14),
                                    command=lambda: self.buton_load_RGA(chk_v_movement_rga.get(), chk_v_acc_rga.get(),
                                                                        chk_v_forces_rga.get()))
        btn_load_graphs_rga.grid(row=4, column=0, padx=650, pady=(10, 20), sticky="e")

        mainframe.grid(sticky="nsew")
        return mainframe


    def buton_load_RGA(self, movement, acceleration, forces):
        #self.reset_variables()
        self.RGASelected = True
        self.tab_to_show = "RGA"
        self.reset_graphs_rga = False
        if movement == 1:
            self.v_movement_rga = True
        if acceleration == 1:
            self.v_acc_rga = True
        if forces == 1:
            self.v_forces_rga = True

        if self.current_notebook_name == "sstab2":
            self.current_notebook.destroy()
            self.create_second_notebook()

    def buton_reset_graphs_RGA(self):
        self.tab_to_show = "RGA"
        self.reset_graphs_rga = True
        self.reset_graphs_roa = False
        self.reset_graphs_roc = False
        self.RGASelected = False
        self.v_forces_rga = False
        self.v_acc_rga = False
        self.v_movement_rga = False

        if self.current_notebook_name == "sstab2":
            self.current_notebook.destroy()
            self.create_second_notebook()

    def RGA(self, parent: ttk.Frame) -> tk.Frame:

        fuente = font.Font(family="Arial", size=20, weight="bold", underline=True)

        mainframe = ttk.Frame(parent, name="rga")
        mainframe.config(takefocus=0)
        mainframe.config(borderwidth=0, relief="flat")
        mainframe.grid(sticky="nsew")

        myframe = utils.ScrollableFrame(mainframe)
        myframe.scrollable_frame.focus_set()
        myframe.grid(sticky="nsew")

        mainframe.grid_rowconfigure(0, weight=1)
        mainframe.grid_columnconfigure(0, weight=1)

        if self.user.IMUPath != None:
            if self.user.testDone[2] == True:
                data = self.user.dataIMU[self.user.dataIMU["action"] == 3]
                RGA_list = data.index[data["action"] == 3].tolist()
                indicesTestRGA = utils.encontrar_primer_y_ultimo_valores(RGA_list)

                longitud = len(indicesTestRGA)
                listElim = []
                for i in range(0, longitud, 2):
                    ele1 = indicesTestRGA[i]
                    ele2 = indicesTestRGA[i + 1]
                    dif = ele2 - ele1
                    if dif > 1300 or dif < 250:
                        listElim.append(ele1)
                        listElim.append(ele2)
                for i in listElim:
                    indicesTestRGA.remove(i)

                dataTestsList = []
                lenth = len(indicesTestRGA)
                i = 0
                while i < lenth:
                    start = indicesTestRGA[i]
                    stop = indicesTestRGA[i + 1]
                    new_dataframe = data.loc[start:stop]
                    new_dataframe.reset_index(inplace=True, drop=True)
                    dataTestsList.append(new_dataframe)
                    i = i + 2

                ttk.Label(myframe.scrollable_frame, text="", font=fuente).grid(row=0, column=0, pady=10, padx=10, sticky="w")
                self.img_help_rga = ImageTk.PhotoImage(Image.open("app/help2.png"))
                self.buttonHelp_rga = tk.Button(mainframe, image=self.img_help_rga, borderwidth=0,
                                                command=lambda: utils.help_rga())
                self.buttonHelp_rga.place(x=10, y=10)

                btn_select_grapsh_rga = tk.Button(myframe.scrollable_frame, text='Load graphs', bg="orange",
                                              command=lambda: self.buton_reset_graphs_RGA())
                btn_select_grapsh_rga.place(x=65, y=15)

                tk.Label(myframe.scrollable_frame, text="Analysis made by the IMU device", font=fuente).grid(row=1, column=0)

                if self.v_movement_rga:
                    tk.Label(myframe.scrollable_frame, text="Trajectory made by the patient", font=("TkDefaultFont", 12, "bold")).grid(row=2,column=0,sticky="w", pady=15, padx=5)
                    frame_graphics1 =  utils.trajectoryIMU(myframe.scrollable_frame, dataTestsList, "RGA")
                    frame_graphics1.grid(row=3, column=0, padx=5, pady=5)

                tk.Label(myframe.scrollable_frame, text="Analysis made by the Posturographer", font=fuente).grid(row=1, column=1)

                if self.v_movement_rga:
                    tk.Label(myframe.scrollable_frame, text="Trajectory made by the patient", font=("TkDefaultFont", 12, "bold")).grid(row=2,column=1,sticky="w", pady=15, padx=5)
                    frame_graphics2 = utils.graphsDisplacementPOSTU(myframe.scrollable_frame, self.user, "RGA")
                    frame_graphics2.grid(row=3, column=1)

                if self.v_acc_rga:
                    tk.Label(myframe.scrollable_frame, text="Acceleration catched by the IMU device", font=("TkDefaultFont", 12, "bold")).grid(row=4, column=0, sticky="w", pady=15, padx=5)
                    frame_graphics3 = utils.lineGraphIMU(myframe.scrollable_frame, dataTestsList,
                                                         ["accelerometerX", "accelerometerY", "accelerometerZ"])
                    frame_graphics3.grid(row=5, column=0, sticky="w")

                if self.v_forces_rga:
                    tk.Label(myframe.scrollable_frame, text="Forces catched by the Posturographer", font=("TkDefaultFont", 12, "bold")).grid(row=4, column=1, sticky="w", pady=15, padx=5)
                    frame_graphics4 = utils.lineGraphForcesPOSTU(myframe.scrollable_frame, self.user, "RGA")
                    frame_graphics4.grid(row=5, column=1, sticky="w")
            else:
                ttk.Label(myframe.scrollable_frame, text="The user has not performed RGA type testing",
                          font=("TkDefaultFont", 15, "bold")).grid(row=0, column=0, pady=10, padx=10, sticky="w")
        else:
            messagebox.showwarning(title="Warning",
                                   message="Please load the IMU file.\nData -> Import Data -> Import Data IMU")
            self.tab_to_show = "RGA"
            self.reset_graphs_rga = True
            self.reset_graphs_roa = False
            self.reset_graphs_roc = False
            self.RGASelected = False
            self.v_forces_rga = False
            self.v_acc_rga = False
            self.v_movement_rga = False

            if self.current_notebook_name == "sstab2":
                self.current_notebook.destroy()
                self.create_second_notebook()

        return mainframe


    def load_RGC(self, parent: ttk.Notebook):
        fuente = font.Font(family="TkDefaultFont", size=20, weight="bold")
        mainframe = ttk.Frame(parent, name="load_rgc")
        self.current_content_frame = mainframe

        ttk.Label(mainframe, text="Graph selection: ", font=fuente).grid(row=0, column=0, padx=650, pady=(100, 10))

        self.img_help4 = ImageTk.PhotoImage(Image.open("app/help2.png"))
        self.button4 = tk.Button(mainframe, image=self.img_help4, borderwidth=0, command=lambda:utils.help_graphselection("RGC"))
        self.button4.place(x=10, y=10, width=50, height=50)

        chk_v_movement_rgc = tk.IntVar()
        chk_v_acc_rgc = tk.IntVar()
        chk_v_forces_rgc = tk.IntVar()

        chk_movement_rgc = tk.Checkbutton(mainframe, text='Movement made by the patient', variable=chk_v_movement_rgc,
                                          font=("Arial", 14))
        chk_movement_rgc.grid(row=1, column=0, padx=650, pady=5, sticky="w")

        chk_acc_rgc = tk.Checkbutton(mainframe, text='Acceleration', variable=chk_v_acc_rgc, font=("Arial", 14))
        chk_acc_rgc.grid(row=2, column=0, padx=650, pady=5, sticky="w")

        chk_forces_rgc = tk.Checkbutton(mainframe, text='Forces', variable=chk_v_forces_rgc, font=("Arial", 14))
        chk_forces_rgc.grid(row=3, column=0, padx=650, pady=5, sticky="w")

        btn_load_graphs_rgc = tk.Button(mainframe, text='Load graphs', bg="orange", font=("TkDefaultFont", 14),
                                    command=lambda: self.buton_load_RGC(chk_v_movement_rgc.get(), chk_v_acc_rgc.get(),
                                                                        chk_v_forces_rgc.get()))
        btn_load_graphs_rgc.grid(row=4, column=0, padx=650, pady=(10, 20), sticky="e")

        mainframe.grid(sticky="nsew")
        return mainframe


    def buton_load_RGC(self, movement, acceleration, forces):
        #self.reset_variables()
        self.RGCSelected = True
        self.tab_to_show = "RGC"
        self.reset_graphs_rgc = False
        if movement == 1:
            self.v_movement_rgc = True
        if acceleration == 1:
            self.v_acc_rgc = True
        if forces == 1:
            self.v_forces_rgc = True

        if self.current_notebook_name == "sstab2":
            self.current_notebook.destroy()
            self.create_second_notebook()

    def buton_reset_graphs_RGC(self):
        self.tab_to_show = "RGC"
        self.reset_graphs_rgc = True
        self.reset_graphs_roa = False
        self.reset_graphs_roc = False
        self.reset_graphs_rga = False
        self.RGCSelected = False
        self.v_forces_rgc = False
        self.v_acc_rgc = False
        self.v_movement_rgc = False

        if self.current_notebook_name == "sstab2":
            self.current_notebook.destroy()
            self.create_second_notebook()

    def RGC(self, parent: ttk.Frame) -> tk.Frame:
        fuente = font.Font(family="Arial", size=20, weight="bold", underline=True)
        mainframe = ttk.Frame(parent, name="rgc")
        mainframe.config(takefocus=0)
        mainframe.config(borderwidth=0, relief="flat")
        mainframe.grid(sticky="nsew")

        myframe = utils.ScrollableFrame(mainframe)
        myframe.scrollable_frame.focus_set()
        myframe.grid(sticky="nsew")

        mainframe.grid_rowconfigure(0, weight=1)
        mainframe.grid_columnconfigure(0, weight=1)

        if self.user.IMUPath != None:
            if self.user.testDone[3] == True:
                data = self.user.dataIMU[self.user.dataIMU["action"] == 4]
                RGC_list = data.index[data["action"] == 4].tolist()
                indicesTestRGC = utils.encontrar_primer_y_ultimo_valores(RGC_list)

                longitud = len(indicesTestRGC)
                listElim = []
                for i in range(0, longitud, 2):
                    ele1 = indicesTestRGC[i]
                    ele2 = indicesTestRGC[i + 1]
                    dif = ele2 - ele1
                    if dif > 1300 or dif < 250:
                        listElim.append(ele1)
                        listElim.append(ele2)
                for i in listElim:
                    indicesTestRGC.remove(i)

                dataTestsList = []
                lenth = len(indicesTestRGC)
                i = 0
                while i < lenth:
                    start = indicesTestRGC[i]
                    stop = indicesTestRGC[i + 1]
                    new_dataframe = data.loc[start:stop]
                    new_dataframe.reset_index(inplace=True, drop=True)
                    dataTestsList.append(new_dataframe)
                    i = i + 2

                ttk.Label(myframe.scrollable_frame, text="", font=fuente).grid(row=0, column=0, pady=10, padx=10, sticky="w")
                self.img_help_rgc = ImageTk.PhotoImage(Image.open("app/help2.png"))
                self.buttonHelp_rgc = tk.Button(mainframe, image=self.img_help_rgc, borderwidth=0,
                                                command=lambda: utils.help_rgc())
                self.buttonHelp_rgc.place(x=10, y=10)

                btn_select_grapsh_rgc = tk.Button(myframe.scrollable_frame, text='Load graphs', bg="orange",
                                              command=lambda: self.buton_reset_graphs_RGC())
                btn_select_grapsh_rgc.place(x=65, y=15)

                tk.Label(myframe.scrollable_frame, text="Analysis made by the IMU device", font=fuente).grid(row=1, column=0)

                if self.v_movement_rgc:
                    tk.Label(myframe.scrollable_frame, text="Trajectory made by the patient", font=("TkDefaultFont", 12, "bold")).grid(row=2,column=0,sticky="w", pady=15, padx=5)
                    frame_graphics1 = utils.trajectoryIMU(myframe.scrollable_frame, dataTestsList, "RGC")
                    frame_graphics1.grid(row=3, column=0, padx=5, pady=5)

                tk.Label(myframe.scrollable_frame, text="Analysis made by the Posturographer", font=fuente).grid(row=1, column=1)

                if self.v_movement_rgc:
                    tk.Label(myframe.scrollable_frame, text="Trajectory made by the patient", font=("TkDefaultFont", 12, "bold")).grid(row=2,column=1,sticky="w", pady=15, padx=5)
                    frame_graphics2 = utils.graphsDisplacementPOSTU(myframe.scrollable_frame, self.user, "RGC")
                    frame_graphics2.grid(row=3, column=1)

                if self.v_acc_rgc:
                    tk.Label(myframe.scrollable_frame, text="Acceleration catched by the IMU device", font=("TkDefaultFont", 12, "bold")).grid(row=4, column=0, sticky="w", pady=15, padx=5)
                    frame_graphics3 = utils.lineGraphIMU(myframe.scrollable_frame, dataTestsList,
                                                         ["accelerometerX", "accelerometerY", "accelerometerZ"])
                    frame_graphics3.grid(row=5, column=0, sticky="w")

                if self.v_forces_rgc:
                    tk.Label(myframe.scrollable_frame, text="Forces catched by the Posturographer", font=("TkDefaultFont", 12, "bold")).grid(row=4, column=1, sticky="w", pady=15, padx=5)
                    frame_graphics4 = utils.lineGraphForcesPOSTU(myframe.scrollable_frame, self.user, "RGC")
                    frame_graphics4.grid(row=5, column=1, sticky="w")
            else:
                ttk.Label(myframe.scrollable_frame, text="The user has not performed RGC type testing",
                          font=("TkDefaultFont", 15, "bold")).grid(row=0, column=0, pady=10, padx=10, sticky="w")
        else:
            messagebox.showwarning(title="Warning",
                                   message="Please load the IMU file.\nData -> Import Data -> Import Data IMU")
            self.tab_to_show = "RGC"
            self.reset_graphs_rgc = True
            self.reset_graphs_roa = False
            self.reset_graphs_roc = False
            self.reset_graphs_rga = False
            self.RGCSelected = False
            self.v_forces_rgc = False
            self.v_acc_rgc = False
            self.v_movement_rgc = False

            if self.current_notebook_name == "sstab2":
                self.current_notebook.destroy()
                self.create_second_notebook()

        return mainframe

    def overview_tab(self, parent: ttk.Notebook) -> tk.Frame:
        mainframe = tk.Frame(parent, name="overview tab")
        mainframe.grid()

        radio_buttons_frame = tk.Frame(mainframe)
        v_test = tk.IntVar()

        self.img_help_patient_ov = ImageTk.PhotoImage(Image.open("app/help2.png"))
        self.buttonHelp_patient_ov = tk.Button(mainframe, image=self.img_help_patient_ov, borderwidth=0,
                                            command=lambda: utils.help_patient())
        self.buttonHelp_patient_ov.place(x=1600, y=10)

        radiobutton1 = ttk.Radiobutton(radio_buttons_frame, text="Desplazamiento total (mm)", variable=v_test, value=1, command=lambda: self.overview_desp_total(mainframe))
        radiobutton1.grid(row=0, column=0, padx=5, pady=5)
        radiobutton2 = ttk.Radiobutton(radio_buttons_frame, text="Desplazamiento ML / AP (mm)", variable=v_test, value=2, command=lambda: self.overview_desp_mlap(mainframe))
        radiobutton2.grid(row=0, column=1, padx=5, pady=5)
        radiobutton3 = ttk.Radiobutton(radio_buttons_frame, text="Angulo desplazado (º)", variable=v_test, value=3, command=lambda: self.overview_angulo_desp(mainframe))
        radiobutton3.grid(row=0, column=2, padx=5, pady=5)
        radiobutton4 = ttk.Radiobutton(radio_buttons_frame, text="Dispersión ML / AP", variable=v_test, value=4, command=lambda: self.overview_disp_mlap(mainframe))
        radiobutton4.grid(row=0, column=3, padx=5, pady=5)
        radiobutton6 = ttk.Radiobutton(radio_buttons_frame, text="Area barrida (mm2)", variable=v_test, value=5, command=lambda: self.overview_area_bar(mainframe))
        radiobutton6.grid(row=0, column=4, padx=5, pady=5)
        radiobutton7 = ttk.Radiobutton(radio_buttons_frame, text="Valoracion", variable=v_test, value=6, command=lambda: self.overview_val(mainframe))
        radiobutton7.grid(row=0, column=5, padx=5, pady=5)

        radio_buttons_frame.grid(row=0, column=0, sticky="ew")
        return mainframe

    def overview_desp_total(self, parent: ttk.Frame) -> tk.Frame:
        mainframe = tk.Frame(parent, name="overview") #En todas se pone el mismo nombre porque si no no se sustituyen en la pantalla

        frame_graphics1 = utils.desp_total(mainframe,self.user,"ROA")
        frame_graphics1.grid(row=0, column=0)

        frame_graphics2 = utils.desp_total(mainframe, self.user, "ROC")
        frame_graphics2.grid(row=0, column=1)

        frame_graphics3 = utils.desp_total(mainframe, self.user, "RGA")
        frame_graphics3.grid(row=1, column=0)

        frame_graphics4 = utils.desp_total(mainframe, self.user, "RGC")
        frame_graphics4.grid(row=1, column=1)

        mainframe.grid()
        return mainframe

    def overview_desp_mlap(self, parent: ttk.Frame) -> tk.Frame:
        mainframe = tk.Frame(parent, name="overview")

        frame_graphics1 = utils.desp_mlap(mainframe, self.user, "ROA")
        frame_graphics1.grid(row=0, column=0)

        frame_graphics2 = utils.desp_mlap(mainframe, self.user, "ROC")
        frame_graphics2.grid(row=0, column=1)

        frame_graphics3 = utils.desp_mlap(mainframe, self.user, "RGA")
        frame_graphics3.grid(row=1, column=0)

        frame_graphics4 = utils.desp_mlap(mainframe, self.user, "RGC")
        frame_graphics4.grid(row=1, column=1)

        mainframe.grid()
        return mainframe

    def overview_angulo_desp(self, parent: ttk.Frame) -> tk.Frame:
        mainframe = tk.Frame(parent, name="overview")

        frame_graphics1 = utils.angulo_desp(mainframe, self.user, "ROA")
        frame_graphics1.grid(row=0, column=0)

        frame_graphics2 = utils.angulo_desp(mainframe, self.user, "ROC")
        frame_graphics2.grid(row=0, column=1)

        frame_graphics3 = utils.angulo_desp(mainframe, self.user, "RGA")
        frame_graphics3.grid(row=1, column=0)

        frame_graphics4 = utils.angulo_desp(mainframe, self.user, "RGC")
        frame_graphics4.grid(row=1, column=1)

        mainframe.grid()
        return mainframe

    def overview_disp_mlap(self, parent: ttk.Frame) -> tk.Frame:
        mainframe = tk.Frame(parent, name="overview")

        frame_graphics1 = utils.disp_mlap(mainframe, self.user, "ROA")
        frame_graphics1.grid(row=0, column=0)

        frame_graphics2 = utils.disp_mlap(mainframe, self.user, "ROC")
        frame_graphics2.grid(row=0, column=1)

        frame_graphics3 = utils.disp_mlap(mainframe, self.user, "RGA")
        frame_graphics3.grid(row=1, column=0)

        frame_graphics4 = utils.disp_mlap(mainframe, self.user, "RGC")
        frame_graphics4.grid(row=1, column=1)

        mainframe.grid()
        return mainframe

    def overview_area_bar(self,parent: ttk.Frame) -> tk.Frame:
        mainframe = tk.Frame(parent, name="overview")

        frame_graphics1 = utils.area_barrida(mainframe, self.user, "ROA")
        frame_graphics1.grid(row=0, column=0)

        frame_graphics2 = utils.area_barrida(mainframe, self.user, "ROC")
        frame_graphics2.grid(row=0, column=1)

        frame_graphics3 = utils.area_barrida(mainframe, self.user, "RGA")
        frame_graphics3.grid(row=1, column=0)

        frame_graphics4 = utils.area_barrida(mainframe, self.user, "RGC")
        frame_graphics4.grid(row=1, column=1)

        mainframe.grid()
        return mainframe

    def overview_val(self,parent: ttk.Frame) -> tk.Frame:
        mainframe = tk.Frame(parent, name="overview")

        frame_graphics1 = utils.valoration_tests_grahps(mainframe, self.user)
        frame_graphics1.grid(row=0, column=0)

        mainframe.grid()
        return mainframe

    def content_frame_POSTU_tab1(self, parent: ttk.Frame) -> tk.Frame:
        mainframe = tk.Frame(parent)
        self.current_content_frame = mainframe

        if self.user.postuPath is None:
            tk.Label(mainframe, text="Please load the Posturographer file (.txt)").grid(row=1, column=0)
        else:
            with open(self.user.postuPath, 'r') as archivo:
                lineas = archivo.readlines()
                cabecera_paciente = lineas[0]
                linea_paciente = lineas[1]
            headerData = cabecera_paciente.split("\t")
            pacientData = linea_paciente.split("\t")
            etiquetasData = []
            etiquetasHeader = []

            framePatient = tk.Frame(mainframe)
            for i in range(0, 10):
                etiquetasData.append(pacientData[i])
            tk.Label(framePatient, text="Patient: ").grid(row=1, column=0)
            for i in range(0, 10):
                etiquetasHeader.append(headerData[i])
            i = 1
            for et in etiquetasHeader:
                tk.Label(framePatient, text=et).grid(row=1, column=i)
                i = i + 1
            i = 1
            for et in etiquetasData:
                tk.Label(framePatient, text=et).grid(row=2, column=i)
                i = i + 1
            framePatient.grid(row=0, column=0)

            tree = ttk.Treeview(mainframe, columns=list(self.user.dataRombergPostu.columns), show="headings")
            for col in self.user.dataRombergPostu.columns:
                tree.heading(col, text=col)
                tree.column(col, width=50)
            for i, row in self.user.dataRombergPostu.iterrows():
                tree.insert("", "end", values=list(row))
            tree.grid(row=1, column=0)

        mainframe.grid()
        return mainframe

    def open_contentFrameIMU_tab1(self, parent):
        if self.current_content_frame:
            self.current_content_frame.destroy()
            content_frame = self.content_frame_IMU_tab1(parent)
            self.current_content_frame = content_frame
        else:
            content_frame = self.content_frame_IMU_tab1(parent)
            self.current_content_frame = content_frame

    def open_contentFramePOSTU_tab1(self, parent):
        if self.current_content_frame:
            self.current_content_frame.destroy()
            content_frame = self.content_frame_POSTU_tab1(parent)
            self.current_content_frame = content_frame
        else:
            content_frame = self.content_frame_POSTU_tab1(parent)
            self.current_content_frame = content_frame

    def tab2_new_module(self, parent: ttk.Notebook) -> tk.Frame:

        mainframe = tk.Frame(parent, name="tab 2")

        radio_buttons_frame = tk.Frame(mainframe)
        opcion_var = tk.IntVar()
        radiobutton1 = ttk.Radiobutton(radio_buttons_frame, text="IMU Analysis", variable=opcion_var, value=1,
                                       command=lambda: self.open_contentFrameIMU_tab2(mainframe))
        radiobutton1.grid(row=0, column=0)
        radiobutton2 = ttk.Radiobutton(radio_buttons_frame, text="Posturographer Analysis", variable=opcion_var,
                                       value=2,
                                       command=lambda: self.open_contentFramePOSTU_tab2(mainframe))
        radiobutton2.grid(row=0, column=1)

        # content_frame = self.content_frame_tab1(mainframe)

        radio_buttons_frame.grid(row=0, column=0, sticky="w")
        # content_frame.grid()
        mainframe.grid()

        return mainframe

    def content_frame_IMU_tab2(self, parent: ttk.Frame) -> tk.Frame:
        mainframe = tk.Frame(parent)
        self.current_content_frame = mainframe
        if self.user.IMUPath is None and self.user.postuPath is None:
            label_file_not_loaded = tk.Label(mainframe, text="File not loaded").grid(row=1, column=0)
        elif self.user.IMUPath is None:
            label_file_not_loaded = tk.Label(mainframe, text="Please load the IMU file (.csv)").grid(row=1,
                                                                                                     column=0)
        elif self.user.postuPath is None:
            label_file_not_loaded = tk.Label(mainframe, text="Please load the Posturographer file (.txt)").grid(
                row=1, column=0)
        else:
            label_file_loaded = tk.Label(mainframe, text="Files loaded").grid(row=1, column=0)
            # TODO: Leer archivo
            data = utils.pd.read_csv(self.user.IMUPath, delimiter=";")
            # convertData(data,"gravityVectorX",10)
            i = 0

        mainframe.grid()
        return mainframe

    def content_frame_POSTU_tab2(self, parent: ttk.Frame) -> tk.Frame:
        mainframe = tk.Frame(parent)
        self.current_content_frame = mainframe

        if self.user.postuPath is None:
            tk.Label(mainframe, text="Please load the Posturographer file (.txt)").grid(row=1, column=0)
        else:
            with open(self.user.postuPath, 'r') as archivo:
                lineas = archivo.readlines()
                cabecera_paciente = lineas[0]
                linea_paciente = lineas[1]
            headerData = cabecera_paciente.split("\t")
            pacientData = linea_paciente.split("\t")
            etiquetasData = []
            etiquetasHeader = []
            for i in range(0, 10):
                etiquetasData.append(pacientData[i])
            tk.Label(mainframe, text="Patient: ").grid(row=1, column=0)
            for i in range(0, 10):
                etiquetasHeader.append(headerData[i])
            i = 1
            for et in etiquetasHeader:
                tk.Label(mainframe, text=et).grid(row=1, column=i)
                i = i + 1
            i = 1
            for et in etiquetasData:
                tk.Label(mainframe, text=et).grid(row=2, column=i)
                i = i + 1

        mainframe.grid()
        return mainframe

    def open_contentFrameIMU_tab2(self, parent):
        if self.current_content_frame:
            self.current_content_frame.destroy()
            content_frame = self.content_frame_IMU_tab2(parent)
            self.current_content_frame = content_frame
        else:
            content_frame = self.content_frame_IMU_tab2(parent)
            self.current_content_frame = content_frame

    def open_contentFramePOSTU_tab2(self, parent):
        if self.current_content_frame:
            self.current_content_frame.destroy()
            content_frame = self.content_frame_POSTU_tab2(parent)
            self.current_content_frame = content_frame
        else:
            content_frame = self.content_frame_POSTU_tab2(parent)
            self.current_content_frame = content_frame

    def tab3_new_module(self, parent: ttk.Notebook) -> tk.Frame:

        mainframe = tk.Frame(parent, name="tab 3")

        radio_buttons_frame = tk.Frame(mainframe)
        opcion_var = tk.IntVar()
        radiobutton1 = ttk.Radiobutton(radio_buttons_frame, text="IMU Analysis", variable=opcion_var, value=1,
                                       command=lambda: self.open_contentFrameIMU_tab3(mainframe))
        radiobutton1.grid(row=0, column=0)
        radiobutton2 = ttk.Radiobutton(radio_buttons_frame, text="Posturographer Analysis", variable=opcion_var,
                                       value=2,
                                       command=lambda: self.open_contentFramePOSTU_tab3(mainframe))
        radiobutton2.grid(row=0, column=1)

        # content_frame = self.content_frame_tab1(mainframe)

        radio_buttons_frame.grid(row=0, column=0, sticky="w")
        # content_frame.grid()
        mainframe.grid()

        return mainframe

    def content_frame_IMU_tab3(self, parent: ttk.Frame) -> tk.Frame:
        mainframe = tk.Frame(parent)
        self.current_content_frame = mainframe
        if self.user.IMUPath is None and self.user.postuPath is None:
            label_file_not_loaded = tk.Label(mainframe, text="File not loaded").grid(row=1, column=0)
        elif self.user.IMUPath is None:
            label_file_not_loaded = tk.Label(mainframe, text="Please load the IMU file (.csv)").grid(row=1,
                                                                                                     column=0)
        elif self.user.postuPath is None:
            label_file_not_loaded = tk.Label(mainframe, text="Please load the Posturographer file (.txt)").grid(
                row=1, column=0)
        else:
            label_file_loaded = tk.Label(mainframe, text="Files loaded").grid(row=1, column=0)
            # TODO: Leer archivo
            data = utils.pd.read_csv(self.user.IMUPath, delimiter=";")
            # convertData(data,"gravityVectorX",10)
            i = 0

        mainframe.grid()
        return mainframe

    def content_frame_POSTU_tab3(self, parent: ttk.Frame) -> tk.Frame:
        mainframe = tk.Frame(parent)
        self.current_content_frame = mainframe

        if self.user.postuPath is None:
            tk.Label(mainframe, text="Please load the Posturographer file (.txt)").grid(row=1, column=0)
        else:
            with open(self.user.postuPath, 'r') as archivo:
                lineas = archivo.readlines()
                cabecera_paciente = lineas[0]
                linea_paciente = lineas[1]
            headerData = cabecera_paciente.split("\t")
            pacientData = linea_paciente.split("\t")
            etiquetasData = []
            etiquetasHeader = []
            for i in range(0, 10):
                etiquetasData.append(pacientData[i])
            tk.Label(mainframe, text="Patient: ").grid(row=1, column=0)
            for i in range(0, 10):
                etiquetasHeader.append(headerData[i])
            i = 1
            for et in etiquetasHeader:
                tk.Label(mainframe, text=et).grid(row=1, column=i)
                i = i + 1
            i = 1
            for et in etiquetasData:
                tk.Label(mainframe, text=et).grid(row=2, column=i)
                i = i + 1

        mainframe.grid()
        return mainframe

    def open_contentFrameIMU_tab3(self, parent):
        if self.current_content_frame:
            self.current_content_frame.destroy()
            content_frame = self.content_frame_IMU_tab3(parent)
            self.current_content_frame = content_frame
        else:
            content_frame = self.content_frame_IMU_tab3(parent)
            self.current_content_frame = content_frame

    def open_contentFramePOSTU_tab3(self, parent):
        if self.current_content_frame:
            self.current_content_frame.destroy()
            content_frame = self.content_frame_POSTU_tab3(parent)
            self.current_content_frame = content_frame
        else:
            content_frame = self.content_frame_POSTU_tab3(parent)
            self.current_content_frame = content_frame

    def _init_data_input_selection(self, parent: ttk.Notebook) -> tk.Frame:
        mainframe = tk.Frame(parent, name="input data selection")
        mainframe.grid()

        optionVar = tk.IntVar()
        self._add_dynamic_variable("option1", optionVar)
        self._add_dynamic_variable("option2", optionVar)

        option1 = tk.Radiobutton(mainframe, name="option1", text="WIISEL hardware", variable=optionVar, value=1,
                                 command=utils.option1_click)
        option1.grid(row=0, column=0)
        option2 = tk.Radiobutton(mainframe, name="option2", text="Import raw data file", variable=optionVar, value=2,
                                 command=utils.option2_click)
        option2.grid(row=0, column=1)

        label6 = tk.Label(mainframe, name="label6", text="Select subjects:")
        label6.grid(row=1, column=0)

        list3 = tk.Listbox(mainframe, name="list3", exportselection=False, selectmode=tk.MULTIPLE)
        list3.grid(row=1, column=0, columnspan=3, rowspan=4, sticky="we")

        command28 = tk.Button(mainframe, name="command28", text="Add data file(s)", command=utils.command28_click)
        command28.grid(row=5, column=0)

        cmdSensorHealth = tk.Button(mainframe, name="cmdsensorhealth", text="Sensor Health", bg="orange",
                                    command=utils.cmdsensorhealth_click)
        cmdSensorHealth.grid(row=5, column=1)

        command34 = tk.Button(mainframe, name="command34", text="Edit subject Data", command=utils.command34_click)
        command34.grid(row=5, column=2)

        command14 = tk.Button(mainframe, name="command14", text="Load demo data")
        command14.grid(row=6, column=0)

        label22 = tk.Label(mainframe, name="label22", text="Data structure:")
        label22.grid(row=8, column=0)

        # MainList widget
        mainlist = ttk.Treeview(mainframe, name="mainlist")
        mainlist.grid(row=10, column=0, rowspan=10, columnspan=4)

        label15 = tk.Label(mainframe, name="label15", text="Columns:")
        label15.grid(row=1, column=4)

        list9 = tk.Listbox(mainframe, name="list9")
        list9.grid(row=2, column=4, rowspan=4, columnspan=2)

        label37 = tk.Label(mainframe, name="label9", text="label38")
        label37.grid(row=6, column=4)

        command13 = tk.Button(mainframe, name="command13", text="New", command=utils.command13_click)
        command13.grid(row=7, column=4)

        command12 = tk.Button(mainframe, name="command12", text="Edit", command=utils.command12_click)
        command12.grid(row=7, column=5)

        command11 = tk.Button(mainframe, name="command11", text="Delete", command=utils.command11_click)
        command11.grid(row=7, column=6)

        # skipping UpDown1

        label39 = tk.Label(mainframe, name="label39", text="Sample Freq [Hz]")
        label39.grid(row=9, column=4, columnspan=2)

        self._add_dynamic_variable("text20", tk.IntVar())
        text20 = tk.Entry(mainframe, name="text20", textvariable=self.vars["text20"])
        text20.grid(row=9, column=6)

        label16 = tk.Label(mainframe, name="label16", text="Preview")
        label16.grid(row=1, column=8)

        text4 = tk.Frame(mainframe, name="text4")
        text4.grid(row=2, column=8, rowspan=4, columnspan=4)

        text4entry = tk.Entry(text4, name="sadasd")
        text4entry.grid(sticky='w', columnspan=4, rowspan=4, row=0, column=0)

        self._add_dynamic_variable("combo3", tk.StringVar())
        combo3 = ttk.Combobox(mainframe, name="combo3", values=["Comma", "Tab", "Space"],
                              textvariable=self.vars["combo3"])
        combo3.grid(row=6, column=8)

        self._add_dynamic_variable("combo4", tk.StringVar())
        combo4 = ttk.Combobox(mainframe, name="combo4", values=("Point", "Comma"), textvariable=self.vars["combo4"])
        combo4.grid(row=6, column=9)

        self._add_dynamic_variable("combo5", tk.StringVar())
        combo5 = ttk.Combobox(mainframe, name="combo5", values=("CrLf", "Cr", "Lf"), textvariable=self.vars["combo5"])
        combo5.grid(row=6, column=10)

        self._add_dynamic_variable("check1", tk.BooleanVar())
        check1 = tk.Checkbutton(mainframe, name="check1", text="SkipFirst", variable=self.vars["check1"])
        check1.grid(row=7, column=8)

        self._add_dynamic_variable("text5", tk.IntVar())
        text5 = tk.Entry(mainframe, name="text5", textvariable=self.vars["text5"])
        text5.grid(row=7, column=9)

        label17 = tk.Entry(mainframe, name="label17", text="Lines")
        label17.grid(row=7, column=10)

        return mainframe

    def _init_raw_data_filtering(self, parent: ttk.Notebook) -> tk.Frame:
        rowLabel24 = 8
        columnCommand4 = 4

        mainframe = tk.Frame(parent, name="raw data filtering")
        mainframe.grid(padx=2, )
        mainframe.columnconfigure(columnCommand4, weight=2)
        mainframe.columnconfigure(0, weight=2)

        frame10 = tk.Frame(mainframe, name="frame10")
        frame10.grid(row=0, column=0, rowspan=6, padx=4)

        label43 = tk.Label(frame10, name="label43", text="Subject:")
        label43.grid(row=0, column=0, sticky=tk.W)

        self._add_dynamic_variable("combo1", tk.StringVar())
        combo1 = ttk.Combobox(frame10, name="combo1")
        combo1.bind(EventType.comboboxSelectionChanged, lambda e: utils.combo1_click())
        combo1.grid(row=1, column=0, columnspan=2)

        self._add_dynamic_variable("label54", tk.StringVar())
        label54 = tk.Label(frame10, name="label54", text="Last date of data:", textvariable=self.vars["label54"])
        label54.grid(row=3, column=0)

        calendar1 = tkcalendar.Calendar(frame10, name="calendar1")
        calendar1.grid(row=4, column=0, rowspan=2)
        calendar1.bind(EventType.calendarMonthChange, lambda e: utils.calendar1_sel_changed(e))
        calendar1.bind(EventType.calendarDaySel, lambda e: utils.calendar1_button_click(e))
        calendar1.get_date()

        label24 = tk.Label(frame10, name="label24", text="List of fall events:")
        label24.grid(row=6, column=0, sticky=tk.W, pady=(20, 0))

        list11 = tk.Listbox(frame10, name="list11")
        list11.grid(row=7, column=0, rowspan=2, columnspan=3, sticky=tk.NSEW)

        command21 = tk.Button(frame10, name="command21", text="New", command=utils.command21_click)
        command21.grid(row=9, column=0)

        command22 = tk.Button(frame10, name="command22", text="Edit", command=utils.command22_click)
        command22.grid(row=9, column=1)

        command23 = tk.Button(frame10, name="command23", text="Delete", command=utils.command23_click)
        command23.grid(row=9, column=2)

        frame11 = tk.Frame(mainframe, name="frame11")
        frame11.grid(row=1, column=1, rowspan=5, padx=5)

        command4 = tk.Button(frame11, name="command4", text="Update chart", command=utils.command4_click)
        command4.grid(row=0, column=0, columnspan=2, sticky=tk.S)

        list14 = tk.Listbox(frame11, name="list14", selectbackground='light sky blue', selectmode=tk.MULTIPLE,
                            exportselection=tk.FALSE)
        list14.grid(row=1, column=0, rowspan=2, columnspan=2)
        list14.bind(EventType.listboxSelect, lambda e: utils.list14_click(e))

        label49 = tk.Label(frame11, name="label49", text="Intraday gait parameter")
        label49.grid(row=3, column=0, pady=(15, 0))

        list15 = tk.Listbox(frame11, name="list15", selectbackground='light sky blue', selectmode=tk.MULTIPLE,
                            exportselection=tk.FALSE)
        list15.grid(row=4, column=0, rowspan=2, columnspan=2)
        list15.bind(EventType.listboxSelect, lambda e: utils.list15_click(e))

        check4 = tk.Checkbutton(mainframe, name="check4", text="Filter data")
        check4.grid(row=0, column=1)

        frame3 = tk.LabelFrame(mainframe, name="frame3", text="Raw data filtering for selected subject")
        frame3.grid(row=0, column=2, rowspan=1, columnspan=8)

        label3 = tk.Label(frame3, name="label3", text="Step diff filter [%]")
        label3.grid(row=0, column=0)

        self._add_dynamic_variable("text1", tk.DoubleVar())
        text1 = tk.Entry(frame3, name="text1", textvariable=self.vars["text1"])
        text1.grid(row=0, column=1)

        label4 = tk.Label(frame3, name="label4", text="Remove no of steps")
        label4.grid(row=0, column=2)

        self._add_dynamic_variable("text2", tk.IntVar())
        text2 = tk.Entry(frame3, name="text2", textvariable=self.vars["text2"])
        text2.grid(row=0, column=3)

        label5 = tk.Label(frame3, name="label5", text="Step recogn rude")
        label5.grid(row=0, column=4)

        self._add_dynamic_variable("text3", tk.IntVar())
        text3 = tk.Entry(frame3, name="text3", textvariable=self.vars["text3"])
        text3.grid(row=0, column=5)

        label25 = tk.Label(frame3, name="label25", text="Remove highest/lowest [%]")
        label25.grid(row=0, column=6)

        self._add_dynamic_variable("text10", tk.DoubleVar())
        text10 = tk.Entry(frame3, name="text10", textvariable=self.vars["text10"])
        text10.grid(row=0, column=7)

        label18 = tk.Label(frame3, name="label18", text="Clean gait min time frame [s]")
        label18.grid(row=1, column=0)

        self._add_dynamic_variable("text7", tk.IntVar())
        text7 = tk.Entry(frame3, name="text7", textvariable=self.vars["text7"])
        text7.grid(row=1, column=1)

        label19 = tk.Label(frame3, name="label19", text="Cuttings [no of steps]")
        label19.grid(row=1, column=2)

        self._add_dynamic_variable("text8", tk.IntVar())
        text8 = tk.Entry(frame3, name="text8", textvariable=self.vars["text8"])
        text8.grid(row=1, column=3)

        label20 = tk.Label(frame3, name="label20", text="Height filter [cm]")
        label20.grid(row=1, column=4)

        self._add_dynamic_variable("text9", tk.DoubleVar())
        text9 = tk.Entry(frame3, name="text9", textvariable=self.vars["text9"])
        text9.grid(row=1, column=5)

        command29 = tk.Button(frame3, name="command29", text="Apply settings to all subjects")
        command29.grid(row=1, column=6, columnspan=2)

        frame12 = tk.Frame(mainframe, name="frame12")
        frame12.grid(row=1, column=2, rowspan=4, columnspan=8)

        label59 = tk.Label(frame12, name="label59", text="Line width:")
        label59.grid(row=0, column=0, sticky=tk.NW)

        self._add_dynamic_variable("text24", tk.IntVar())
        self.vars["text24"].set(1)
        text24 = tk.Entry(frame12, name="text24", textvariable=self.vars["text24"])
        text24.grid(row=0, column=1, sticky=tk.W)

        stockChartX1 = tk.Frame(frame12, name="stockchartx1", borderwidth=5, relief=tk.RIDGE)
        stockChartX1.grid(row=1, column=0, columnspan=4, rowspan=2)

        rangeTool1 = tk.Scale(frame12, name="rangetool1", from_=0, to=100, orient=tk.HORIZONTAL, length=600)
        rangeTool1.grid(row=3, column=0, columnspan=4, sticky='we')
        rangeTool1.bind(EventType.leftClickRelease, lambda e: utils.rangetool1_change())

        return mainframe

    def _init_gait_parameter_definition(self, parent: ttk.Notebook) -> tk.Frame:
        list1Rows = 8
        label64Row = list1Rows + 1
        label7Col = 4
        codeSenseRowspan = 7

        mainframe = tk.Frame(parent, name="gait parameter definition")
        mainframe.grid()

        label1 = tk.Label(mainframe, name="label1", text="Gait parameter")
        label1.grid(row=0, column=0)

        list1 = tk.Listbox(mainframe, name="list1", exportselection=False, width=30)
        list1.grid(row=1, column=0, columnspan=2, rowspan=list1Rows, sticky=tk.NS)
        list1.bind(EventType.listboxSelect, lambda e: utils.list1_click(e))

        label64 = tk.Label(mainframe, name="label64", text="Gait parameter unit")
        label64.grid(row=label64Row, column=0)

        self._add_dynamic_variable("text34", tk.StringVar())
        text34 = tk.Entry(mainframe, name="text34", textvariable=self.vars["text34"])
        text34.grid(row=label64Row, column=1)

        command1 = tk.Button(mainframe, name="command1", text="New", command=utils.command1_click)
        command1.grid(row=label64Row + 1, column=0)

        command2 = tk.Button(mainframe, name="command2", text="Edit", command=utils.command2_click)
        command2.grid(row=label64Row + 1, column=1)

        command3 = tk.Button(mainframe, name="command3", text="Delete", command=utils.command3_click)
        command3.grid(row=label64Row + 1, column=2)

        label7 = tk.Label(mainframe, name="label7", text="Definition script")
        label7.grid(row=0, column=label7Col)

        cs = tk.Text(mainframe, name="cs", height=20, width=150)
        cs.grid(row=1, column=label7Col)

        command5 = tk.Button(mainframe, name="command5", text="Check code", command=utils.command5_click)
        command5.grid(row=codeSenseRowspan + 1 + 1, column=label7Col)

        return mainframe

    def _init_gait_parameter_history(self, parent: ttk.Notebook) -> tk.Frame:
        label42Col = 3

        mainframe = tk.Frame(parent, name="gait parameter history")
        mainframe.grid()

        label41 = tk.Label(mainframe, name="label41", text="Subjects")
        label41.grid(row=0, column=0)

        list13 = tk.Listbox(mainframe, name="list13", selectmode=tk.MULTIPLE, selectbackground='light sky blue',
                            exportselection=tk.FALSE)
        list13.grid(row=1, column=0, rowspan=3, columnspan=2)

        label40 = tk.Label(mainframe, name="label40", text="Gait parameter")
        label40.grid(row=4, column=0)

        list12 = tk.Listbox(mainframe, name="list12", selectmode=tk.MULTIPLE, selectbackground='light sky blue',
                            exportselection=tk.FALSE)
        list12.grid(row=5, column=0, rowspan=5, columnspan=2)

        command32 = tk.Button(mainframe, name="command32", text="Update chart", command=utils.command32_click)
        command32.grid(row=10, column=0)

        label42 = tk.Label(mainframe, name="label42", text="Gait parameter history")
        label42.grid(row=0, column=label42Col)

        self._add_dynamic_variable("check2", tk.BooleanVar())
        check2 = tk.Checkbutton(mainframe, name="check2", text="intraday", variable=self.vars["check2"])
        check2.grid(row=0, column=label42Col + 1)

        text_daily = tk.Entry(mainframe, name="text_daily")
        text_daily.grid(row=0, column=label42Col + 2)

        # TODO: stockChartX4, graph. Y SUS command6, command29, command31, command30

        stockChartX4 = tk.Frame(mainframe, name="stockchartx4")
        stockChartX4.grid(row=2, column=0, columnspan=4, rowspan=4)

        return mainframe

    def _init_pattern_extraction(self, parent: ttk.Notebook) -> ttk.Notebook:
        tabs = ttk.Notebook(parent, name="pattern extraction")
        tabs.grid()

        comparisonFrame = tk.Frame(name="comparison pattern")
        deviationFrame = tk.Frame(name="deviation pattern")

        tabs.add(comparisonFrame, text=comparisonFrame.winfo_name())
        tabs.add(deviationFrame, text=deviationFrame.winfo_name())

        frame4 = tk.LabelFrame(comparisonFrame, name="frame4", text="Step 1: Setup groups")
        frame4.grid(row=0, column=0, rowspan=2)

        label12 = tk.Label(frame4, name="label12", text="Faller (training set)")
        label12.grid(row=0, column=0)

        list5 = tk.Listbox(frame4, name="list5", exportselection=tk.FALSE)
        list5.grid(row=1, column=0, columnspan=3)

        label13 = tk.Label(frame4, name="label13", text="Non faller (training set)")
        label13.grid(row=2, column=0)

        up3 = tk.Button(frame4, name="up3", text="Up", command=lambda: utils.move_selected_to_listbox("list6", "list5"))
        up3.grid(row=2, column=1)

        down3 = tk.Button(frame4, name="down3", text="Down",
                          command=lambda: utils.move_selected_to_listbox("list5", "list6"))
        down3.grid(row=2, column=2)

        list6 = tk.Listbox(frame4, name="list6", exportselection=tk.FALSE)
        list6.grid(row=3, column=0, columnspan=3)

        label65 = tk.Label(frame4, name="label65", text="Faller (validation set)")
        label65.grid(row=4, column=0)

        up4 = tk.Button(frame4, name="up4", text="Up",
                        command=lambda: utils.move_selected_to_listbox("list17", "list6"))
        up4.grid(row=4, column=1)

        down4 = tk.Button(frame4, name="down4", text="Down",
                          command=lambda: utils.move_selected_to_listbox("list6", "list17"))
        down4.grid(row=4, column=2)

        list17 = tk.Listbox(frame4, name="list17", exportselection=tk.FALSE)
        list17.grid(row=5, column=0, columnspan=3)

        label9 = tk.Label(frame4, name="label9", text="Non Faller (validation set)")
        label9.grid(row=6, column=0)

        up5 = tk.Button(frame4, name="up5", text="Up",
                        command=lambda: utils.move_selected_to_listbox("list4", "list17"))
        up5.grid(row=6, column=1)

        down5 = tk.Button(frame4, name="down5", text="Down",
                          command=lambda: utils.move_selected_to_listbox("list17", "list4"))
        down5.grid(row=6, column=2)

        list4 = tk.Listbox(frame4, name="list4", exportselection=tk.FALSE)
        list4.grid(row=7, column=0, columnspan=3)

        frame5 = tk.LabelFrame(comparisonFrame, name="frame5", text="Step 2: Initiate pattern extraction")
        frame5.grid(row=0, column=1)

        command7 = tk.Button(frame5, name="command7", text="Start", command=utils.command7_click)
        command7.grid()

        frame6 = tk.LabelFrame(comparisonFrame, name="frame6", text="Step 3: Handle results")
        frame6.grid(row=1, column=1)

        label21 = tk.Label(frame6, name="label6", text="List of patterns")
        label21.grid(row=0, column=0)

        list7 = tk.Listbox(frame6, name="list7")
        list7.grid(row=1, column=0, columnspan=3)

        command20 = tk.Button(frame6, name="command20", text="New")
        command20.grid(row=2, column=0)

        command21 = tk.Button(frame6, name="command19", text="Edit")
        command21.grid(row=2, column=1)

        command22 = tk.Button(frame6, name="command22", text="Delete")
        command22.grid(row=2, column=2)

        label63 = tk.Label(frame6, name="label63", text="Formula")
        label63.grid(row=3, column=0)

        text6 = tk.Entry(frame6, name="text6")
        text6.grid(row=4, column=0, columnspan=3)

        label35 = tk.Label(frame6, name="label35", text="Details")
        label35.grid(row=5, column=0)

        text19 = tk.Entry(frame6, name="text19")
        text19.grid(row=6, column=0, columnspan=3)

        # TODO: chartPattern (graph)

        frame2 = tk.LabelFrame(deviationFrame, name="frame2", text="Step 1: Setup groups")
        frame2.grid(row=0, column=0, rowspan=2)

        label36 = tk.Label(frame2, name="label36", text="Faller (training set)")
        label36.grid(row=0, column=0)

        list8 = tk.Listbox(frame2, name="list8")
        list8.grid(row=1, column=0, columnspan=3)

        label52 = tk.Label(frame2, name="label52", text="Non faller (training set)")
        label52.grid(row=2, column=0)

        list19 = tk.Listbox(frame2, name="list19")
        list19.grid(row=3, column=0, columnspan=3)

        label53 = tk.Label(frame2, name="label53", text="Faller (validation set)")
        label53.grid(row=4, column=0)

        list20 = tk.Listbox(frame2, name="list20")
        list20.grid(row=5, column=0, columnspan=3)

        label31 = tk.Label(frame2, name="label31", text="Non Faller (validation set)")
        label31.grid(row=6, column=0)

        list16 = tk.Listbox(frame2, name="list16")
        list16.grid(row=7, column=0, columnspan=3)

        frame7 = tk.LabelFrame(deviationFrame, name="frame7", text="Step 2: Initiate pattern extraction")
        frame7.grid(row=0, column=1)

        command24 = tk.Button(frame7, name="command24", text="Pattern extraction", command=utils.command24_click)
        command24.grid(row=0, column=0)

        command44 = tk.Button(frame7, name="command44", text="Cancel")
        command44.grid(row=1, column=0)

        frame8 = tk.LabelFrame(deviationFrame, name="frame8", text="Step 3: Handle results")
        frame8.grid(row=1, column=1)

        label14 = tk.Label(frame8, name="label14", text="Faller: Select pattern")
        label14.grid(row=0, column=0)

        treeview1 = ttk.Treeview(frame8, name="treeview1")
        treeview1.grid(row=1, column=0, columnspan=3)

        command25 = tk.Button(frame8, name="command25", text="New")
        command25.grid(row=2, column=0)

        command26 = tk.Button(frame8, name="command26", text="Edit")
        command26.grid(row=2, column=1)

        command27 = tk.Button(frame8, name="command27", text="Delete")
        command27.grid(row=2, column=2)

        label58 = tk.Label(frame8, name="label58", text="Non faller: Select pattern")
        label58.grid(row=3, column=0)

        treeview2 = ttk.Treeview(frame8, name="treeview2")
        treeview2.grid(row=4, column=0, columnspan=3)

        label44 = tk.Label(deviationFrame, name="label44", text="Gait pattern")
        label44.grid(row=0, column=2)

        # TODO: msChart1, tipo mschart (supongo que grafica)
        # TODO: label "text23" (no se si es label, quiza no hace falta)

        return tabs

    def _init_fall_risk_index_definition(self, parent: ttk.Notebook) -> tk.Frame:
        label32row = 6
        label8col = 5

        mainframe = tk.Frame(parent, name="fall risk index definition")
        mainframe.grid()

        frame13 = tk.Frame(mainframe, name="frame13")
        frame13.grid(row=0, column=0)

        label2 = tk.Label(frame13, name="label2", text="Select Fall Risk Index")
        label2.grid(row=0, column=0)

        list2 = tk.Listbox(frame13, name="list2")
        list2.bind(EventType.listboxSelect, lambda e: utils.list2_click())
        list2.grid(row=1, column=0, columnspan=4)

        command8 = tk.Button(frame13, name="command8", text="New", command=utils.command8_click)
        command8.grid(row=2, column=0)

        command9 = tk.Button(frame13, name="command9", text="Edit", command=utils.command9_click)
        command9.grid(row=2, column=1)

        command10 = tk.Button(frame13, name="command10", text="Delete", command=utils.command10_click)
        command10.grid(row=2, column=2)

        text17 = tk.Entry(frame13, name="text17")
        text17.grid(row=2, column=3)

        frame14 = tk.Frame(mainframe, name="frame14")
        frame14.grid(row=1, column=0)

        label32 = tk.Label(frame14, name="label32", text="Select patterns")
        label32.grid(row=0, column=0)

        command33 = tk.Button(frame14, name="command33", text="Select all", command=utils.command33_click)
        command33.grid(row=0, column=1)

        list10 = tk.Listbox(frame14, name="list10", exportselection=False, selectmode=tk.MULTIPLE)
        list10.bind(EventType.listboxSelect, lambda e: utils.list10_click(e))
        list10.grid(row=1, column=0, columnspan=2)

        frame1 = tk.LabelFrame(mainframe, name="frame1", text="Fall risk index ranges")
        frame1.grid(row=2, column=0)

        label23 = tk.Label(frame1, name="label23", text="Color")
        label23.grid(row=0, column=0)

        label29 = tk.Label(frame1, name="label29", text="from")
        label29.grid(row=0, column=1)

        label30 = tk.Label(frame1, name="label30", text="to")
        label30.grid(row=0, column=3)

        label26 = tk.Label(frame1, name="label26", text="Red")
        label26.grid(row=1, column=0)

        self._add_dynamic_variable("text11", tk.DoubleVar())
        text11 = tk.Entry(frame1, name="text11", textvariable=self.vars["text11"])
        text11.grid(row=1, column=1)

        label33 = tk.Label(frame1, name="label33", text="%")
        label33.grid(row=1, column=2)

        self._add_dynamic_variable("text12", tk.DoubleVar())
        text12 = tk.Entry(frame1, name="text12", textvariable=self.vars["text12"])
        text12.grid(row=1, column=3)

        label11 = tk.Label(frame1, name="label11", text="%")
        label11.grid(row=1, column=4)

        label27 = tk.Label(frame1, name="label27", text="Yellow")
        label27.grid(row=2, column=0)

        self._add_dynamic_variable("text13", tk.DoubleVar())
        text13 = tk.Entry(frame1, name="text13", textvariable=self.vars["text13"])
        text13.grid(row=2, column=1)

        label34 = tk.Label(frame1, name="label34", text="%")
        label34.grid(row=2, column=2)

        self._add_dynamic_variable("text14", tk.DoubleVar())
        text14 = tk.Entry(frame1, name="text14", textvariable=self.vars["text14"])
        text14.grid(row=2, column=3)

        label50 = tk.Label(frame1, name="label50", text="%")
        label50.grid(row=2, column=4)

        label28 = tk.Label(frame1, name="label28", text="Green")
        label28.grid(row=3, column=0)

        self._add_dynamic_variable("text15", tk.DoubleVar())
        text15 = tk.Entry(frame1, name="text15", textvariable=self.vars["text15"])
        text15.grid(row=3, column=1)

        label47 = tk.Label(frame1, name="label47", text="%")
        label47.grid(row=3, column=2)

        self._add_dynamic_variable("text16", tk.DoubleVar())
        text16 = tk.Entry(frame1, name="text16", textvariable=self.vars["text16"])
        text16.grid(row=3, column=3)

        label51 = tk.Label(frame1, name="label51", text="%")
        label51.grid(row=3, column=4)

        command38 = tk.Button(frame1, name="command38", text="Update")
        command38.grid(row=4, column=1, columnspan=3)

        frame15 = tk.Frame(mainframe, name="frame15")
        frame15.grid(row=0, column=1)

        label8 = tk.Label(frame15, name="label 8", text="Fall Risk Index Settings")
        label8.grid(row=0, column=0)

        FRI_list = ttk.Treeview(frame15, name="fri_list")
        FRI_list.grid(row=1, column=0, columnspan=2)

        command35 = tk.Button(frame15, name="command35", text="Weight all equally", command=utils.command35_click)
        command35.grid(row=2, column=0)

        command40 = tk.Button(frame15, name="command40", text="Find best weights", command=utils.command40_click)
        command40.grid(row=2, column=1)

        frame16 = tk.Frame(mainframe, name="frame16")
        frame16.grid(row=1, column=1, rowspan=2, columnspan=2)

        label10 = tk.Label(frame16, name="label10", text="Fall Risk Index details for each subject")
        label10.grid(row=0, column=0)

        FRI_table = ttk.Treeview(frame16, name="fri_table")
        FRI_table.grid(row=1, column=0)

        piechart = tk.Frame(mainframe, name="piechart")
        piechart.grid(row=0, column=2)

        frame9 = ttk.Labelframe(mainframe, name="frame9")
        frame9.grid(row=7, column=0, columnspan=2)

        optiList = ttk.Treeview(frame9, name="opti_list", height=5)
        optiList.grid(row=0, column=0, columnspan=5)

        command41 = tk.Button(frame9, name="command41", command=utils.command41_click)
        command41.grid(row=1, column=0)

        # cancel
        # hide

        label55 = tk.Label(frame9, name="label55", text="Minimum accuracy [%]")
        label55.grid(row=1, column=3)

        self._add_dynamic_variable("text18", tk.DoubleVar())
        text18 = tk.Entry(frame9, name="text18", textvariable=self.vars["text18"])
        text18.grid(row=1, column=4)

        label56 = tk.Label(frame9, name="label56", text="Minimum no of results")
        label56.grid(row=2, column=3)

        self._add_dynamic_variable("text21", tk.IntVar())
        text21 = tk.Entry(frame9, name="text21", textvariable=self.vars["text21"])
        text21.grid(row=2, column=4)

        self._add_dynamic_variable("check3", tk.BooleanVar())
        check3 = tk.Checkbutton(frame9, name="check3", text="Include Maximum impact property",
                                textvariable=self.vars["check3"])
        check3.grid(row=2, column=0)

        return mainframe

    def _init_fact_sheet(self, parent: ttk.Notebook) -> tk.Frame:
        mainframe = tk.Frame(parent, name="fact sheet")
        mainframe.grid()

        label45 = tk.Label(mainframe, name="label45", text="Subject")
        label45.grid(row=0, column=0)

        combo2 = ttk.Combobox(mainframe, name="combo2")
        combo2.bind(EventType.comboboxSelectionChanged, lambda e: utils.combo2_selection_change())
        combo2.grid(row=1, column=0)

        label46 = tk.Label(mainframe, name="label46", text="Fact sheet")
        label46.grid(row=2, column=0)

        subjectList = ttk.Treeview(mainframe, name="fact_subject")
        subjectList.grid(row=3, column=0)

        statisticsList = ttk.Treeview(mainframe, name="fact_statistics")
        statisticsList.grid(row=4, column=0)

        gaitParameterList = ttk.Treeview(mainframe, name="fact_parameters")
        gaitParameterList.grid(row=5, column=0)

        return mainframe

    def _init_toplevel_sensor_health(self) -> tk.Toplevel:
        tl = tk.Toplevel(name="sensorhealth")

        sensors = ttk.Treeview(tl, name="sensors")
        sensors.grid(row=0, column=0)
        sensors.bind(EventType.doubleLeftClick, lambda e: utils.sensors_click())

        im = Image.open("app/PressureSensors.jpg")
        sensorLayout = tk.Canvas(tl, name="sensorlayout", width=im.width, height=im.height)
        sensorLayout.grid(row=0, column=1, rowspan=2)
        sensorLayout.image = ImageTk.PhotoImage(im)
        sensorLayout.create_image(0, 0, image=sensorLayout.image, anchor='nw')

        tl.wm_withdraw()
        return tl

    def _init_toplevel_select_subjects(self) -> tk.Toplevel:
        tl = tk.Toplevel(name="selectsubjects")

        list1 = tk.Listbox(tl, name="list1", selectmode=tk.MULTIPLE)
        list1.grid(row=0, column=0, columnspan=3)

        command1 = tk.Button(tl, name="command1", text="Ok")
        command1.grid(row=1, column=1)

        command2 = tk.Button(tl, name="command2", text="Cancel")
        command2.grid(row=1, column=2)

        tl.wm_withdraw()
        return tl

    def _init_toplevel_user_info(self) -> tk.Toplevel:
        tl = tk.Toplevel(name="userinfo")

        label1 = tk.Label(tl, name="label1", text="ID")
        label1.grid(row=0, column=0)

        self._add_toplevel_dynamic_variable("text10", tk.StringVar(), self.userInfoVars)
        text10 = tk.Entry(tl, name="text10", textvariable=self.userInfoVars["text10"])
        text10.grid(row=0, column=1)

        label8 = tk.Label(tl, name="label8", text="First name:")
        label8.grid(row=0, column=2)

        self._add_toplevel_dynamic_variable("text1", tk.StringVar(), self.userInfoVars)
        text1 = tk.Entry(tl, name="text1", textvariable=self.userInfoVars["text1"])
        text1.grid(row=0, column=3)

        label9 = tk.Label(tl, name="label9", text="Last name:")
        label9.grid(row=0, column=4)

        self._add_toplevel_dynamic_variable("text4", tk.StringVar(), self.userInfoVars)
        text4 = tk.Entry(tl, name="text4", textvariable=self.userInfoVars["text4"])
        text4.grid(row=0, column=5)

        label2 = tk.Label(tl, name="label2", text="Age:")
        label2.grid(row=1, column=0)

        self._add_toplevel_dynamic_variable("text2", tk.StringVar(), self.userInfoVars)
        text2 = tk.Entry(tl, name="text2", textvariable=self.userInfoVars["text2"])
        text2.grid(row=1, column=1)

        label10 = tk.Label(tl, name="label10", text="Phone:")
        label10.grid(row=1, column=2)

        self._add_toplevel_dynamic_variable("text5", tk.StringVar(), self.userInfoVars)
        text5 = tk.Entry(tl, name="text5", textvariable=self.userInfoVars["text5"])
        text5.grid(row=1, column=3)

        label11 = tk.Label(tl, name="label11", text="Email:")
        label11.grid(row=1, column=4)

        self._add_toplevel_dynamic_variable("text6", tk.StringVar(), self.userInfoVars)
        text6 = tk.Entry(tl, name="text6", textvariable=self.userInfoVars["text6"])
        text6.grid(row=1, column=5)

        label12 = tk.Label(tl, name="label12", text="Size of insole:")
        label12.grid(row=1, column=6)

        self._add_toplevel_dynamic_variable("text7", tk.StringVar(), self.userInfoVars)
        text7 = tk.Entry(tl, name="text7", textvariable=self.userInfoVars["text7"])
        text7.grid(row=1, column=7)

        label13 = tk.Label(tl, name="label13", text="Address:")
        label13.grid(row=2, column=0)

        self._add_toplevel_dynamic_variable("text8", tk.StringVar(), self.userInfoVars)
        text8 = tk.Entry(tl, name="text8", textvariable=self.userInfoVars["text8"])
        text8.grid(row=2, column=1, columnspan=3, rowspan=3)

        label3 = tk.Label(tl, name="label3", text="Note:")
        label3.grid(row=2, column=4)

        self._add_toplevel_dynamic_variable("text3", tk.StringVar(), self.userInfoVars)
        text3 = tk.Entry(tl, name="text3", textvariable=self.userInfoVars["text3"])
        text3.grid(row=2, column=5, rowspan=3, columnspan=3)

        label14 = tk.Label(tl, name="label14", text="Select pressure calibration file")
        label14.grid(row=5, column=1)

        self._add_toplevel_dynamic_variable("text9", tk.StringVar(), self.userInfoVars)
        text9 = tk.Entry(tl, name="text9", textvariable=self.userInfoVars["text9"])
        text9.grid(row=6, column=2, columnspan=3)

        command3 = tk.Button(tl, name="command3", text="Browse...", command=utilsUserInfo.command3_click)
        command3.grid(row=6, column=6)

        self._add_toplevel_dynamic_variable("check3", tk.BooleanVar(), self.userInfoVars)
        check3 = tk.Checkbutton(tl, name="check3", text="Upload user statistics to smart phone",
                                variable=self.userInfoVars["check3"])
        check3.grid(row=7, column=1, columnspan=6)

        self._add_toplevel_dynamic_variable("check2", tk.BooleanVar(), self.userInfoVars)
        check2 = tk.Checkbutton(tl, name="check2", text="Fall risk index (Ampel) is visible on the smart phone",
                                variable=self.userInfoVars["check2"])
        check2.grid(row=8, column=1, columnspan=6)

        frame1 = ttk.Labelframe(tl, name="frame1", text="Fact sheet settings")
        frame1.grid(row=9, column=0, rowspan=4, columnspan=8)

        label4 = tk.Label(frame1, name="label4", text="Statistics")
        label4.grid(row=0, column=0)

        list1 = tk.Listbox(frame1, name="list1", selectmode=tk.MULTIPLE, exportselection=tk.FALSE)
        list1.grid(row=1, column=0, columnspan=2)

        label5 = tk.Label(frame1, name="label5", text="Gait parameter")
        label5.grid(row=0, column=3)

        list2 = tk.Listbox(frame1, name="list2", selectmode=tk.MULTIPLE, exportselection=tk.FALSE)
        list2.grid(row=1, column=3, columnspan=2)

        label6 = tk.Label(frame1, name="label6", text="label6")
        label6.grid(row=0, column=6)

        list3 = tk.Listbox(frame1, name="list3", selectmode=tk.MULTIPLE, selectbackground='light sky blue',
                           exportselection=tk.FALSE)
        list3.grid(row=1, column=6, columnspan=2)

        self._add_toplevel_dynamic_variable("check1", tk.BooleanVar(), self.userInfoVars)
        check1 = tk.Checkbutton(frame1, name="check1", text="Apply settings from above lists for all subjects",
                                variable=self.userInfoVars["check1"])
        check1.grid(row=2, column=0)

        command1 = tk.Button(tl, name="command1", text="Ok", command=utilsUserInfo.command1_click)
        command1.grid(row=15, column=5)

        command2 = tk.Button(tl, name="command2", text="Cancel", command=utilsUserInfo.command2_click)
        command2.grid(row=15, column=6)

        tl.wm_withdraw()

        return tl

    def _init_toplevel_pattern_extraction(self) -> tk.Toplevel:
        tl = tk.Toplevel(name="patternextraction")

        frame1 = ttk.Labelframe(tl, name="frame1", text="Step 1: Set filter")
        frame1.grid(row=0, column=0)

        label9 = tk.Label(frame1, name="label9", text="Filter faller", font='TkDefaultFont 11 bold')
        label9.grid(row=0, column=0)

        self._add_toplevel_dynamic_variable("check2", tk.BooleanVar(), self.patternExtractionVars)
        check2 = tk.Checkbutton(frame1, name="check2", text="Max relative Variance [%]",
                                variable=self.patternExtractionVars["check2"])
        check2.grid(row=1, column=0)

        self._add_toplevel_dynamic_variable("text30", tk.DoubleVar(), self.patternExtractionVars)
        text30 = tk.Entry(frame1, name="text30", textvariable=self.patternExtractionVars["text30"])
        text30.grid(row=1, column=1)

        self._add_toplevel_dynamic_variable("check1", tk.BooleanVar(), self.patternExtractionVars)
        check1 = tk.Checkbutton(frame1, name="check1", text="Max relative Std Dev [%]",
                                variable=self.patternExtractionVars["check1"])
        check1.grid(row=2, column=0)

        self._add_toplevel_dynamic_variable("text21", tk.DoubleVar(), self.patternExtractionVars)
        text21 = tk.Entry(frame1, name="text21", textvariable=self.patternExtractionVars["text21"])
        text21.grid(row=2, column=1)

        self._add_toplevel_dynamic_variable("check3", tk.BooleanVar(), self.patternExtractionVars)
        check3 = tk.Checkbutton(frame1, name="check3", text="Max relative Std Error [%]",
                                variable=self.patternExtractionVars["check3"])
        check3.grid(row=3, column=0)

        self._add_toplevel_dynamic_variable("text33", tk.DoubleVar(), self.patternExtractionVars)
        text33 = tk.Entry(frame1, name="text33", textvariable=self.patternExtractionVars["text33"])
        text33.grid(row=3, column=1)

        self._add_toplevel_dynamic_variable("check8", tk.BooleanVar(), self.patternExtractionVars)
        check8 = tk.Checkbutton(frame1, name="check8", text="Cut highest/lowest values [%]",
                                variable=self.patternExtractionVars["check8"])
        check8.grid(row=4, column=0)

        self._add_toplevel_dynamic_variable("text5", tk.DoubleVar(), self.patternExtractionVars)
        text5 = tk.Entry(frame1, name="text5", textvariable=self.patternExtractionVars["text5"])
        text5.grid(row=4, column=1)

        label1 = tk.Label(frame1, name="label1", text="Filter non faller", font='TkDefaultFont 11 bold')
        label1.grid(row=5, column=0)

        self._add_toplevel_dynamic_variable("check5", tk.BooleanVar(), self.patternExtractionVars)
        check5 = tk.Checkbutton(frame1, name="check5", text="Max relative Variance [%]",
                                variable=self.patternExtractionVars["check5"])
        check5.grid(row=6, column=0)

        self._add_toplevel_dynamic_variable("text2", tk.DoubleVar(), self.patternExtractionVars)
        text2 = tk.Entry(frame1, name="text2", textvariable=self.patternExtractionVars["text2"])
        text2.grid(row=6, column=1)

        self._add_toplevel_dynamic_variable("check6", tk.BooleanVar(), self.patternExtractionVars)
        check6 = tk.Checkbutton(frame1, name="check6", text="Max relative Std Dev [%]",
                                variable=self.patternExtractionVars["check6"])
        check6.grid(row=7, column=0)

        self._add_toplevel_dynamic_variable("text1", tk.DoubleVar(), self.patternExtractionVars)
        text1 = tk.Entry(frame1, name="text1", textvariable=self.patternExtractionVars["text1"])
        text1.grid(row=7, column=1)

        self._add_toplevel_dynamic_variable("check4", tk.BooleanVar(), self.patternExtractionVars)
        check4 = tk.Checkbutton(frame1, name="check4", text="Max relative Std Error [%]",
                                variable=self.patternExtractionVars["check4"])
        check4.grid(row=8, column=0)

        self._add_toplevel_dynamic_variable("text3", tk.DoubleVar(), self.patternExtractionVars)
        text3 = tk.Entry(frame1, name="text3", textvariable=self.patternExtractionVars["text3"])
        text3.grid(row=8, column=1)

        self._add_toplevel_dynamic_variable("check7", tk.BooleanVar(), self.patternExtractionVars)
        check7 = tk.Checkbutton(frame1, name="check7", text="Cut highest/lowest values [%]",
                                variable=self.patternExtractionVars["check7"])
        check7.grid(row=9, column=0)

        self._add_toplevel_dynamic_variable("text4", tk.DoubleVar(), self.patternExtractionVars)
        text4 = tk.Entry(frame1, name="text4", textvariable=self.patternExtractionVars["text4"])
        text4.grid(row=9, column=1)

        command7 = tk.Button(frame1, name="command7", text="Extract", command=utilsPatternExtraction.command7_click)
        command7.grid(row=10, column=1)

        frame2 = ttk.Labelframe(tl, name="frame2", text="Step 2: check results")
        frame2.grid(row=0, column=1)

        resultslist = ttk.Treeview(frame2, name="resultslist")
        resultslist.bind(EventType.doubleLeftClick, lambda e: utilsPatternExtraction.resultslist_click(e))
        resultslist.grid(row=0, column=0)

        sstab1 = ttk.Notebook(tl, name="sstab1")
        sstab1.grid(row=1, column=0, columnspan=2)

        overview = tk.Frame(sstab1, name="overview")
        overview.grid(row=0, column=0)

        distributionchart = tk.Frame(overview, name="distributionchart")
        distributionchart.grid(row=0, column=0, columnspan=3)

        combo1 = ttk.Combobox(overview, name="combo1")
        combo1.grid(row=2, column=0)

        details = tk.Frame(sstab1, name="details")
        details.grid(row=0, column=0)

        detailslist = ttk.Treeview(details, name="detailslist")
        detailslist.grid(row=0, column=0)

        sstab1.add(overview, text="Overview")
        sstab1.add(details, text="Details")

        command33 = tk.Button(tl, name="command33", text="Add to List of pattern",
                              command=utilsPatternExtraction.command33_click)
        command33.grid(row=3, column=1)

        tl.wm_withdraw()
        return tl

    def _init_toplevel_enter_fri(self) -> tk.Toplevel:
        tl = tk.Toplevel(name="enterfri")

        label1 = tk.Label(tl, name="label1", text="Name")
        label1.grid(row=0, column=0, sticky=tk.E)

        self._add_toplevel_dynamic_variable("text1", tk.StringVar(), self.enterFriVars)
        text1 = tk.Entry(tl, name="text1", textvariable=self.enterFriVars["text1"])
        text1.grid(row=0, column=1, columnspan=3)

        self._add_toplevel_dynamic_variable("check1", tk.BooleanVar(), self.enterFriVars)
        check1 = tk.Checkbutton(tl, name="check1", variable=self.enterFriVars["check1"],
                                text="Make this Fall Risk index available in all configurations")
        check1.grid(row=1, column=1, columnspan=2)

        command1 = tk.Button(tl, name="command1", text="Ok", command=utilsEnterFri.command1_click)
        command1.grid(row=2, column=2)

        command2 = tk.Button(tl, name="command2", text="Cancel", command=utilsEnterFri.command2_click)
        command2.grid(row=2, column=3)

        tl.wm_withdraw()
        return tl

    def _init_toplevel_sensor_selector(self) -> tk.Toplevel:
        tl = tk.Toplevel(name="sensorselector")

        label1 = tk.Label(tl, name="label1", text="Name")
        label1.grid(row=0, column=0)

        self._add_toplevel_dynamic_variable("text1", tk.StringVar(), self.sensorSelectorVars)
        text1 = tk.Entry(tl, name="text1", textvariable=self.sensorSelectorVars["text1"])
        text1.grid(row=0, column=1, columnspan=2)

        label2 = tk.Label(tl, name="label2", text="Type")
        label2.grid(row=1, column=0)

        combo1 = ttk.Combobox(tl, name="combo1")
        combo1.grid(row=1, column=1, columnspan=2)

        label3 = tk.Label(tl, name="label3", text="Options")
        label3.grid(row=2, column=0)

        combo2 = ttk.Combobox(tl, name="combo2")
        combo2.grid(row=2, column=1, columnspan=2)

        label4 = tk.Label(tl, name="label4", text="Unit")
        label4.grid(row=3, column=0)

        self._add_toplevel_dynamic_variable("text2", tk.StringVar(), self.sensorSelectorVars)
        text2 = tk.Entry(tl, name="text2", textvariable=self.sensorSelectorVars["text2"])
        text2.grid(row=3, column=1, columnspan=2)

        command1 = tk.Button(tl, name="command1", text="Ok", command=utilsSensorSelector.command1_click)
        command1.grid(row=3, column=3)

        command2 = tk.Button(tl, name="command2", text="Cancel", command=utilsSensorSelector.command2_click)
        command2.grid(row=3, column=4)

        tl.wm_withdraw()
        return tl

    def _add_dynamic_variable(self, widgetName: str, var: tk.Variable):
        """
        Maps between widget name and tkinter Variable (StringVar, BooleanVar...)
        """
        # TODO: if widgetName entry in vars already exists, throw error
        self.vars[widgetName] = var

    def _add_toplevel_dynamic_variable(self, widgetName: str, var: tk.Variable, dictionary: dict):
        """
        Maps between widget name and tkinter Variable (StringVar, BooleanVar...)
        """
        # TODO: if widgetName entry in vars already exists, throw error
        dictionary[widgetName] = var

    def get_child(self, name: str, root=None) -> tk.Widget:
        """
        Get widget in research tool by name. Uses a DFS search in postnode order.

        If not found, returns None.
        """
        if root is None:
            root = self.root

        res = None

        def recursive_get_child(currentWidget: tk.Widget):
            nonlocal res
            for child in currentWidget.winfo_children():
                if len(child.winfo_children()) > 0:
                    recursive_get_child(child)
                if child.winfo_name() == name:
                    res = child
                if res != None:
                    return

            return

        recursive_get_child(root)
        return res

    # TODO: repasar como lo creo, si dibujar, como lo borro del frame... necesito pasarle nombre del frame que lo contiene? (creo que no)
    def _add_graph_to_frame(self, x, y, frame: tk.Frame) -> tk.Canvas:
        """
        Returns a tk Canvas, that has been added to the given frame
        """

        x = [a for a in range(1, 20)]
        y = [a ** 2 for a in range(1, 20)]
        y = [math.log(a, 2) for a in y]

        fig = Figure(figsize=(5, 4), dpi=100)
        ax = fig.add_subplot()
        line, = ax.plot(x, y)
        ax.set_xlabel("x")
        ax.set_ylabel("x(t)")

        figCanvas = FigureCanvasTkAgg(fig, master=frame)
        figCanvas.draw()

        toolbar = NavigationToolbar2Tk(figCanvas, frame, pack_toolbar=False)
        toolbar.update()

        toolbar.grid(row=2, column=0)
        figCanvas.get_tk_widget().grid(row=0, column=0)

        canvas = figCanvas.get_tk_widget()
        return canvas

    def _styling(self):
        self.root.configure()
