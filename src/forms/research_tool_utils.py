"""
All functions and form methods should be private.
"""
import datetime
import time
from enum import Enum
import os

import pylab as pl
import userpaths
import sys
import types
import importlib
import jdcal
from calendar import monthrange

# import src.forms.research_tool_skel as gui
# import src.tools.utils_data as td
import src.tools as t
import src.model.globalvars as g
import src.model as m
import src.forms.codesense as codesense
import copy
import random

import math
import numpy as np

import tkcalendar
from tkinter import messagebox, filedialog, simpledialog, ttk
import tkinter as tk
import easygui

from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
# Implement the default Matplotlib key bindings.
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure

import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import transforms3d as t3d
from mpl_toolkits.mplot3d import Axes3D
from sqlalchemy import create_engine, text
import src.model.database as bd

colors = ['red', 'blue', 'green', 'orange', 'purple', 'pink', 'brown', 'cyan', 'magenta']

class User:
    def __init__(self):
        self.id = None
        self.IMUPath = None
        self.postuPath = None
        self.dataIMU = None
        self.dataUser = None
        self.dicUser = None
        self.dataRombergPostu = None
        self.dataRombergPostu_XY = None
        self.dataRombergPostu_FxFy = None
        self.testDone = [False, False, False, False] # ROA, ROC, RGA, RGC

    def setIMUPath(self, path):
        self.IMUPath = path

    def setPostuPath(self, path):
        self.postuPath = path

    def setDicUser(self, dic):
        self.dicUser = dic

    def setDataRomberg(self, dataRomberg):
        self.dataRombergPostu = dataRomberg

    def setDataRomberg_XY(self, dataRombergXY):
        self.dataRombergPostu_XY = dataRombergXY

    def setDataRomberg_FxFy(self, dataRombergFxFy):
        self.dataRombergPostu_FxFy = dataRombergFxFy

    def setDataIMU(self, dataIMU):
        self.dataIMU = dataIMU

    def setID(self, id):
        if self.id is None:
            self.id = id

    def setDataUser(self, dataUser):
        self.dataUser = dataUser


def convertDataHEXA(data, leftshift):
    for i in range(len(data)):
        for j in data.columns:
            if j not in ("time", "action", "id", "test", "steps", "timeSteps"):
                data.loc[i, j] = int(data.loc[i, j], 16)


def convertData(data, column, leftShift):
    for i in range(len(data)):
        if i in data.index:
            temp = data.loc[i, column]
            unsigned = int(temp, 16)

            if unsigned & (1 << 15) != 0:
                unsigned = -1 * ((1 << 15) - (unsigned & ((1 << 15) - 1)))

            data.loc[i, column] = unsigned / (1 << leftShift)
    return data


def processIMUData(data, columns, window, user, progres_var):
    ncolumns = len(columns)
    progres = 100 / ncolumns
    total_progres = progres

    for col in columns:
        convertData(data, col, 10)
        progres_var.set(total_progres)
        total_progres = total_progres + progres

    user.setDataIMU(data)
    window.destroy()
    if user.dataIMU is not None:
        messagebox.showinfo(title="Data imported", message="Data imported successfully")
    else:
        messagebox.showinfo(title="Data imported", message="Error importing data")

    id = data["id"].iloc[0]
    user.setID(id)

def processIMUDataBD(data, columns, window, user, progres_var):
    ncolumns = len(columns)
    progres = 100 / ncolumns
    total_progres = progres

    for col in columns:
        convertData(data, col, 10)
        progres_var.set(total_progres)
        total_progres = total_progres + progres

    user.setDataIMU(data)
    window.destroy()

    id = data["id"].iloc[0]
    user.id = id

    database = bd.Database()
    engine = database.engine

    with engine.connect() as con:
        query = text("SELECT COUNT(*) FROM users WHERE id = :id")
        resultq = con.execute(query, {'id': id}).scalar()

    if resultq > 0:
        messagebox.showinfo(title="Error", message="User " + id + " already exists in database")
    else:
        try:
            dfIMU = user.dataIMU
            dfIMU.to_sql(name='dataIMU', con=engine, if_exists='append', index=False)
            messagebox.showinfo(title="Info", message="Data uploaded successfully for user " + id)
        except Exception as e:
            messagebox.showinfo(title="Error", message=(f"Error uploading data: {e}"))


def encontrar_primer_y_ultimo_valores(lista):
    grupos = []
    grupo_actual = [lista[0]]

    for i in range(1, len(lista)):
        if lista[i] == lista[i - 1] + 1:
            # El valor actual es parte del grupo actual
            grupo_actual.append(lista[i])
        else:
            # El valor actual no es parte del grupo actual, así que guardamos el primer y último valor del grupo anterior
            grupos.append(grupo_actual[0])
            grupos.append(grupo_actual[-1])
            # Iniciamos un nuevo grupo con el valor actual
            grupo_actual = [lista[i]]

    # Añadimos el primer y último valor del último grupo
    grupos.append(grupo_actual[0])
    grupos.append(grupo_actual[-1])
    return grupos


def eliminar_test_invalido(data, long_list):
    for lista in long_list:
        for i in range(0, len(lista), 2):
            valor_actual = lista[i]
            valor_siguiente = lista[i + 1]
            validar = valor_siguiente - valor_actual
            if validar < 1050 or validar > 1300:
                data.drop(data.index[valor_actual:valor_siguiente + 1], inplace=True)


def createDataframesPostu(path, user):
    reader = pd.read_csv(path, delimiter="\t", encoding="ansi", chunksize=1, index_col=False)

    find = path.find("_sve_")
    id = path[find + 5: find + 10]
    user.id = id.lower()

    dataframe1 = reader.get_chunk()
    dataframe1.insert(loc=0,column="ID", value=user.id)
    user.setDataUser(dataframe1)
    dicFrame = dataframe1.to_dict(orient="records")
    user.setDicUser(dicFrame)

    numTest = dicFrame[0]["Nº_ROA"] + dicFrame[0]["Nº_ROC"] + dicFrame[0]["Nº_RGA"] + dicFrame[0]["Nº_RGC"]
    reader = pd.read_csv(path, delimiter="\t", encoding="ansi", skiprows=2, chunksize=numTest, index_col=False)
    dataframe2 = reader.get_chunk()
    dataframe2 = dataframe2.drop(columns=['NºHistorial'])

    dataframe2["Test"] = dataframe2["Prueba ROMBERG"] + dataframe2["Numero"].astype(str)
    dataframe2.insert(loc=0,column="ID", value=user.id)
    user.setDataRomberg(dataframe2)

    rows = 17 + numTest
    reader = pd.read_csv(path, delimiter="\t", encoding="ansi", skiprows=rows, chunksize=1200, index_col=False)
    dataframe3 = reader.get_chunk()
    dataframe3.insert(loc=0,column="ID", value=user.id)
    user.setDataRomberg_XY(dataframe3)

    rows = 1218 + numTest
    reader = pd.read_csv(path, delimiter="\t", encoding="ansi", skiprows=rows, chunksize=1200, index_col=False)
    dataframe4 = reader.get_chunk()
    dataframe4.insert(loc=0,column="ID", value=user.id)
    user.setDataRomberg_FxFy(dataframe4)


    user.testDone = [False, False, False, False]
    dic = user.dicUser[0]
    if dic['Nº_ROA'] >= 1:
        user.testDone[0] = True
    if dic['Nº_ROC'] >= 1:
        user.testDone[1] = True
    if dic['Nº_RGA'] >= 1:
        user.testDone[2] = True
    if dic['Nº_RGC'] >= 1:
        user.testDone[3] = True



def createDataframeIMU(path, user):
    data = pd.read_csv(path, delimiter=";")
    data.drop(data[data["test"] != 5].index, inplace=True)

    ROA_list = data.index[data["action"] == 1].tolist()
    ROC_list = data.index[data["action"] == 2].tolist()
    RGA_list = data.index[data["action"] == 3].tolist()
    RGC_list = data.index[data["action"] == 4].tolist()

    lista = []
    user.testDone = [False, False, False, False]
    if len(ROA_list) != 0:
        lista_con_ROA = encontrar_primer_y_ultimo_valores(ROA_list)
        lista.append(lista_con_ROA)
        user.testDone[0] = True
    if len(ROC_list) != 0:
        lista_con_ROC = encontrar_primer_y_ultimo_valores(ROC_list)
        lista.append(lista_con_ROC)
        user.testDone[1] = True
    if len(RGA_list) != 0:
        lista_con_RGA = encontrar_primer_y_ultimo_valores(RGA_list)
        lista.append(lista_con_RGA)
        user.testDone[2] = True
    if len(RGC_list) != 0:
        lista_con_RGC = encontrar_primer_y_ultimo_valores(RGC_list)
        lista.append(lista_con_RGC)
        user.testDone[3] = True

    eliminar_test_invalido(data, lista)

    return data


def graphsDisplacementIMU(parentFrame, dataTestsList, test):
    frame_graphics = ttk.Frame(parentFrame)
    col = 0
    row = 1
    num = 1
    for i in dataTestsList:
        data = i.loc[i["test"] == 5, ["gravityVectorX", "gravityVectorY"]]
        fig, ax = plt.subplots(figsize=(3.5, 2.5))
        pointsX = data["gravityVectorX"].values.tolist()
        pointsY = data["gravityVectorY"].values.tolist()
        pointsXaux = []
        pointsYaux = []
        for j in range(0, len(pointsX), 10):
            pointsXaux.append(pointsX[j])
            pointsYaux.append(pointsY[j])
        ax.plot(pointsX, pointsY, linewidth=0.5)
        ax.scatter(pointsX[0], pointsY[0], color='red', label='Start Point', zorder=10, alpha=0.8)
        ax.set_xlabel("X-Axis")
        ax.set_ylabel("Y-Axis")
        ax.set_title(test + str(num))
        fig.subplots_adjust(left=0.2, right=0.8, top=0.8, bottom=0.2)
        canvas = FigureCanvasTkAgg(fig, master=frame_graphics)
        canvas.get_tk_widget().grid(row=row, column=col, padx=5, pady=5)
        col = col + 1
        num = num + 1
        if col > 1:
            col = 0
            row = row + 1
    return frame_graphics

def trajectoryIMU(parentFrame, dataTestsList, test):
    frame_graphics = ttk.Frame(parentFrame)
    col = 0
    irow = 1
    num = 1
    for df in dataTestsList:

        madgwick = t.MadgwickAHRS()
        position_x = [0]
        position_y = [0]
        position_z = [0]

        time = 0.025

        error = False
        for index, row in df.iterrows():
            try:
                gyroscope = [float(row['gyroscopeX']), float(row['gyroscopeY']), float(row['gyroscopeZ'])]
                accelerometer = [float(row['accelerometerX']), float(row['accelerometerY']), float(row['accelerometerZ'])]

                madgwick.update_imu(gyroscope, accelerometer)
                t3d.quaternions.quat2mat(madgwick.quaternion.q)

                position_x.append(position_x[-1] + gyroscope[0] * time)
                position_y.append(position_y[-1] + gyroscope[1] * time)
                position_z.append(position_z[-1] + gyroscope[2] * time)
            except Exception as e:
                print(f"Ha ocurrido un error: {e}")
                error = True

        #Bloque de control de bugs -> Si algunos de los datos no ha sido convertido correctamente a hexa se vuelven a convertir
        if error:
            column = ['gyroscopeX','gyroscopeY','gyroscopeZ','accelerometerX','accelerometerY','accelerometerZ']
            for colu in column:
                for i in range(len(df)):
                    if i in df.index:
                        temp = df.loc[i, colu]
                        try:
                            unsigned = int(temp, 16)
                            if unsigned & (1 << 15) != 0:
                                unsigned = -1 * ((1 << 15) - (unsigned & ((1 << 15) - 1)))

                            df.loc[i, colu] = unsigned / (1 << 10)
                        except Exception as e:
                            print(e)

            for index, row in df.iterrows():
                try:
                    gyroscope = [float(row['gyroscopeX']), float(row['gyroscopeY']), float(row['gyroscopeZ'])]
                    accelerometer = [float(row['accelerometerX']), float(row['accelerometerY']),float(row['accelerometerZ'])]

                    # Actualizar el algoritmo de Madgwick
                    madgwick.update_imu(gyroscope, accelerometer)  # No se usa magnenometro

                    # Obtener la orientación estimada en forma de matriz de rotación
                    t3d.quaternions.quat2mat(madgwick.quaternion.q)

                    # ntegra las velocidades angulares para obtener la orientación
                    # time += row['timeSteps']
                    position_x.append(position_x[-1] + gyroscope[0] * time)
                    position_y.append(position_y[-1] + gyroscope[1] * time)
                    position_z.append(position_z[-1] + gyroscope[2] * time)
                except Exception as e:
                    print(e)
        ############################################


        # Visualizar la trayectoria
        fig = plt.figure(figsize=(4.5, 4.5))
        ax = fig.add_subplot(111, projection='3d')
        ax.plot(position_x, position_y, position_z)
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')
        ax.set_title(test + str(num))
        ax.scatter(position_x[0], position_y[0], color='red', label='Start Point', zorder=10, alpha=0.8)
        canvas = FigureCanvasTkAgg(fig, master=frame_graphics)
        canvas.get_tk_widget().grid(row=irow, column=col, padx=5, pady=5)
        col = col + 1
        if col > 1:
            col = 0
            irow = irow + 1
        num = num + 1

    return frame_graphics

def graphsDisplacementPOSTU(parentFrame, user, test):
    frame_graphics = ttk.Frame(parentFrame)
    col = 0
    row = 1
    data = user.dataRombergPostu.loc[user.dataRombergPostu["Prueba ROMBERG"] == test]
    test_list = data["Test"].tolist()
    num = 1
    for item in test_list:
        fig, ax = plt.subplots(figsize=(3.5, 2.5))
        pointsX = user.dataRombergPostu_XY[item + "_X"].values.tolist()
        pointsY = user.dataRombergPostu_XY[item + "_Y"].values.tolist()
        ax.plot(pointsX, pointsY, linewidth=0.5)
        ax.scatter(pointsX[0], pointsY[0], color='red', label='Start Point', zorder=10, alpha=0.8)
        ax.set_xlabel("X-Axis")
        ax.set_ylabel("Y-Axis")
        ax.set_title(test + str(num))
        fig.subplots_adjust(left=0.2, right=0.8, top=0.8, bottom=0.2)
        canvas = FigureCanvasTkAgg(fig, master=frame_graphics)
        canvas.get_tk_widget().grid(row=row, column=col, padx=5, pady=5)
        col = col + 1
        if col > 1:
            col = 0
            row = row + 1
        num = num + 1
    return frame_graphics


def lineGraphIMU(parentFrame, dataTestsList, column):
    frame_graphics = ttk.Frame(parentFrame)
    row = 0
    for i in dataTestsList:
        error = False
        try:
            data = i.loc[i["test"] == 5, column]
            data = data.applymap(float)
            fig, ax = plt.subplots(figsize=(6, 4))
            data.plot(ax=ax, linewidth=0.5)
            ax.set_xlabel("Time")
            # fig.subplots_adjust(left=0.2, right=0.9, top=0.9, bottom=0.25)
            canvas = FigureCanvasTkAgg(fig, master=frame_graphics)
            canvas.get_tk_widget().grid(row=row, column=0, padx=5, pady=5)
        except Exception as e:
            print(f"Ha ocurrido un error: {e}")
            error = True

        #Bloque de control de bugs por no haberse convertido todos los datos a hexa
        if error == True:
            data = i.loc[i["test"] == 5, column]
            for col in column:
                for i in range(len(data)):
                    if i in data.index:
                        temp = data.loc[i, col]
                        try:
                            unsigned = int(temp, 16)

                            if unsigned & (1 << 15) != 0:
                                unsigned = -1 * ((1 << 15) - (unsigned & ((1 << 15) - 1)))

                            data.loc[i, col] = unsigned / (1 << 10)
                        except Exception as e:
                            print(e)
            data = data.applymap(float)
            fig, ax = plt.subplots(figsize=(6, 4))
            data.plot(ax=ax, linewidth=0.5)
            ax.set_xlabel("Time")
            # fig.subplots_adjust(left=0.2, right=0.9, top=0.9, bottom=0.25)
            canvas = FigureCanvasTkAgg(fig, master=frame_graphics)
            canvas.get_tk_widget().grid(row=row, column=0, padx=5, pady=5)
        ###################################

        row = row + 1

    return frame_graphics

def lineGraphForcesPOSTU(parentFrame, user, testname):
    frame_graphics = ttk.Frame(parentFrame)
    data = user.dataRombergPostu.loc[user.dataRombergPostu["Prueba ROMBERG"] == testname]
    test_list = data["Test"].tolist()
    row = 0
    num = 1

    for test in test_list:
        fig, ax = plt.subplots(figsize=(6, 4))
        dadesPostufxfy = user.dataRombergPostu_FxFy[[test + "_Fx", test + "_Fy"]]
        dadesPostufxfy.plot(ax=ax, linewidth=1)
        ax.set_xlabel("Time")
        ax.legend(["X-Axis", "Y-Axis"])
        ax.set_title(testname + str(num))
        fig.subplots_adjust(left=0.2, right=0.8, top=0.8, bottom=0.2)
        canvas = FigureCanvasTkAgg(fig, master=frame_graphics)
        canvas.get_tk_widget().grid(row=row, column=0, padx=5, pady=5)
        row = row + 1
        num = num + 1

    return frame_graphics

def desp_total(parentFrame, user, testname):
    frame_graphics = ttk.Frame(parentFrame)
    data = user.dataRombergPostu.loc[user.dataRombergPostu["Prueba ROMBERG"] == testname]

    aux = []
    for i in range(len(data)):
        aux.append(testname + str(i+1))
    data['Test AUX'] = aux

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.barh(data['Test AUX'], data['Desplaz.Total(mm)'], color=colors)
    ax.set_ylabel('Test ' + testname)
    ax.set_xlabel('Desplazamiento Total (mm)')
    ax.set_title('Desplazamiento Total Tests de ' + testname)
    canvas = FigureCanvasTkAgg(fig, master=frame_graphics)
    canvas.get_tk_widget().grid(row=0, column=0, padx=5, pady=5)

    return frame_graphics

def desp_mlap(parentFrame, user, testname):
    frame_graphics = ttk.Frame(parentFrame)
    data = user.dataRombergPostu.loc[user.dataRombergPostu["Prueba ROMBERG"] == testname]

    bar_witdh = 0.35
    aux = []
    for i in range(len(data)):
        aux.append(testname + str(i + 1))
    data['Test AUX'] = aux

    desp_ml = data['Desplazam.ML (mm)']
    desp_ap = data['Desplazam.AP(mm)']
    tests = data['Test AUX']

    index = np.arange(len(tests))
    fig, ax = plt.subplots(figsize=(6, 4))
    bar1 = ax.bar(np.arange(len(tests)), desp_ml, bar_witdh, label='Desplazamiento ML', color='blue')
    bar2 = ax.bar(np.arange(len(tests)) + bar_witdh, desp_ap, bar_witdh, label='Desplazamiento AP', color='orange')

    ax.set_xlabel('Test ' + testname)
    ax.set_ylabel('Desplazamiento (mm)')
    ax.set_title('Desplazamiento ML y AP para tests ' + testname)
    ax.set_xticks(np.arange(len(tests)) + bar_witdh / 2)
    ax.set_xticklabels(tests)
    ax.legend()
    canvas = FigureCanvasTkAgg(fig, master=frame_graphics)
    canvas.get_tk_widget().grid(row=0, column=0, padx=5, pady=5)

    return frame_graphics

def angulo_desp(parentFrame, user, testname):
    frame_graphics = ttk.Frame(parentFrame)
    data = user.dataRombergPostu.loc[user.dataRombergPostu["Prueba ROMBERG"] == testname]
    data['Angulo Desplaz.(º)'] = np.radians(data['Angulo Desplaz.(º)']) #transformar a radianes

    aux = []
    for i in range(len(data)):
        aux.append(testname + str(i + 1))
    data['Test AUX'] = aux

    angel_color = plt.cm.Dark2(np.linspace(0, 1, len(data)))
    fig, ax = plt.subplots(subplot_kw={'projection': 'polar'},figsize=(4.5, 4.5))

    for i, (_, row) in enumerate(data.iterrows()):
        ax.quiver(0, 0, row['Angulo Desplaz.(º)'], 1, angles='xy', scale_units='xy', scale=1, color=colors[i])
        ax.text(row['Angulo Desplaz.(º)'], 1.2, row['Test AUX'], ha='center', va='center', fontsize=8, color=colors[i])
    ax.set_rmax(1.5)
    ax.set_yticklabels([]) #Oculta etiquetas del eje
    pl.title('Ángulo de Desplazamiento para test ' + testname)

    canvas = FigureCanvasTkAgg(fig, master=frame_graphics)
    canvas.get_tk_widget().grid(row=0, column=0, padx=5, pady=5)

    return frame_graphics

def disp_mlap(parentFrame, user, testname):
    frame_graphics = ttk.Frame(parentFrame)
    data = user.dataRombergPostu.loc[user.dataRombergPostu["Prueba ROMBERG"] == testname]

    bar_witdh = 0.35
    aux = []
    for i in range(len(data)):
        aux.append(testname + str(i + 1))
    data['Test AUX'] = aux

    disp_ml = data['Dispers ML (mm)']
    disp_ap = data['Dispers AP (mm)']
    tests = data['Test AUX']

    index = np.arange(len(tests))
    fig, ax = plt.subplots(figsize=(6, 4))
    bar1 = ax.bar(np.arange(len(tests)), disp_ml, bar_witdh, label='Dispersion ML', color='purple')
    bar2 = ax.bar(np.arange(len(tests)) + bar_witdh, disp_ap, bar_witdh, label='Dispersion AP', color='cyan')

    ax.set_xlabel('Test ' + testname)
    ax.set_ylabel('Dispersion (mm)')
    ax.set_title('Dispersion ML y AP para tests ' + testname)
    ax.set_xticks(np.arange(len(tests)) + bar_witdh / 2)
    ax.set_xticklabels(tests)
    ax.legend()
    canvas = FigureCanvasTkAgg(fig, master=frame_graphics)
    canvas.get_tk_widget().grid(row=0, column=0, padx=5, pady=5)

    return frame_graphics

def area_barrida(parentFrame, user, testname):
    frame_graphics = ttk.Frame(parentFrame)
    data = user.dataRombergPostu.loc[user.dataRombergPostu["Prueba ROMBERG"] == testname]

    aux = []
    for i in range(len(data)):
        aux.append(testname + str(i + 1))
    data['Test AUX'] = aux

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.barh(data['Test AUX'], data['Area barrida (mm2)'], color=colors[3:])
    ax.set_ylabel('Test ' + testname)
    ax.set_xlabel('Area barrida (mm2)')
    ax.set_title('Area barrida Tests de ' + testname)
    canvas = FigureCanvasTkAgg(fig, master=frame_graphics)
    canvas.get_tk_widget().grid(row=0, column=0, padx=5, pady=5)

    return frame_graphics


def valoration_tests_grahps(parentFrame, user):
    frame_graphics = ttk.Frame(parentFrame)

    tests = []
    if user.testDone[0]:
        tests.append("ROA")
    if user.testDone[1]:
        tests.append("ROC")
    if user.testDone[2]:
        tests.append("RGA")
    if user.testDone[3]:
        tests.append("RGC")

    val = []
    val_m = []
    for i in tests:
        val.append(user.dicUser[0]['Val_' + i])
        val_m.append(user.dicUser[0]['Val_' + i] / user.dicUser[0]['Nº_' + i])

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(tests, val,color=colors)
    ax.set_ylabel('Puntuacion')
    ax.set_title('Tests')
    ax.set_title('Puntuacion de valoración')
    canvas = FigureCanvasTkAgg(fig, master=frame_graphics)
    canvas.get_tk_widget().grid(row=0, column=0, padx=10, pady=5)

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(tests, val_m, color=colors)
    ax.set_ylabel('Puntuacion')
    ax.set_title('Tests')
    ax.set_title('Puntuacion de valoración media por test')
    canvas = FigureCanvasTkAgg(fig, master=frame_graphics)
    canvas.get_tk_widget().grid(row=0, column=1, padx=10, pady=5)

    return frame_graphics

class ScrollableFrame(ttk.Frame):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        canvas = tk.Canvas(self)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        scrollbar_h = ttk.Scrollbar(self, orient="horizontal", command=canvas.xview)
        self.scrollable_frame = ttk.Frame(canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.configure(xscrollcommand=scrollbar_h.set)
        scrollbar_h.pack(side="bottom", fill="x")
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)


class Database():
    def __init__(self):
        self.db_config = {
            'user': 'root',
            'password': '',
            'host': 'localhost',
            'port': 3306,
            'database': 'rtanalysis'
        }
        self.engine = create_engine('mysql+pymysql://root:@localhost/rtanalysis')



def help_graphselection(test):
    messagebox.showinfo(title="Help", message="Please select the graphs you want to display for the " + test + " test.\nThen click on the button 'Load graphs' to display the graphs.")

def help_roa():
    messagebox.showinfo(title="Help",
                        message="Romberg test performed by the patient on a flat platform with eyes open (ROA).\n\n"
                                "On the left you can view the results captured by the IMU device and on the right you can view the results captured by the posturograph.\n\n"
                                "Data displayed:\n- Trajectory: This is the displacement or trajectory made by the patient during the test.\n - Acceleration: Represents the acceleration of the patient's body during the test.\n"
                                "-Force: Represents the forces applied by the patient in the horizontal and vertical directions during the test.")

def help_roc():
    messagebox.showinfo(title="Help",
                        message="Romberg test performed by the patient on a flat platform with eyes closed (ROC).\n\n"
                                "On the left you can view the results captured by the IMU device and on the right you can view the results captured by the posturograph.\n\n"
                                "Data displayed:\n- Trajectory: This is the displacement or trajectory made by the patient during the test.\n - Acceleration: Represents the acceleration of the patient's body during the test.\n"
                                "-Force: Represents the forces applied by the patient in the horizontal and vertical directions during the test.")

def help_rga():
    messagebox.showinfo(title="Help",
                        message="Romberg test performed by the patient on a mobile platform and with eyes open (RGA).\n\n"
                                "On the left you can view the results captured by the IMU device and on the right you can view the results captured by the posturograph.\n\n"
                                "Data displayed:\n- Trajectory: This is the displacement or trajectory made by the patient during the test.\n - Acceleration: Represents the acceleration of the patient's body during the test.\n"
                                "-Force: Represents the forces applied by the patient in the horizontal and vertical directions during the test.")

def help_rgc():
    messagebox.showinfo(title="Help",
                        message="Romberg test performed by the patient on a mobile platform and with eyes closed (RGC).\n\n"
                                "On the left you can view the results captured by the IMU device and on the right you can view the results captured by the posturograph.\n\n"
                                "Data displayed:\n- Trajectory: This is the displacement or trajectory made by the patient during the test.\n - Acceleration: Represents the acceleration of the patient's body during the test.\n"
                                "-Force: Represents the forces applied by the patient in the horizontal and vertical directions during the test.")

def help_patient():
    messagebox.showinfo(title="Help",
                        message="The files can be loaded following the next steps: \nLocal data -> Import local data")

class RadioValues(Enum):
    option1 = 1
    option2 = 2


def redim_preserve(arr: list, length: int):
    if len(arr) > length:
        arr = arr[0:length]
    elif len(arr) < length:
        lengthDiff = length - len(arr)
        arr.extend([None] * lengthDiff)


def list1_click(e: tk.Event):
    list1 = e.widget
    cs = g.rt.get_child("cs")

    if len(list1.curselection()) > 0:
        g.rtv.noChange = True
        csText = "\n".join(g.tool.configuration.gaitParameterDef[list1.curselection()[0]].script)
        cs.delete('1.0', tk.END)
        cs.insert('1.0', csText)
        g.rt.vars["text34"].set(g.tool.configuration.gaitParameterDef[list1.curselection()[0]].unit)
        g.rtv.noChange = False


def list15_click(e: tk.Event):
    oldSelToWatch = g.tool.configuration.selectToWatch

    list15 = e.widget
    g.tool.configuration.selectToWatch = "|".join([list15.get(index) for index in list15.curselection()])
    if oldSelToWatch != g.tool.configuration.selectToWatch:
        g.tool.configuration.changed = True


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
            path = os.path.join(g.tool.configuration.users[list3Index].filePath,
                                g.tool.configuration.users[list3Index].name)
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


def form_load():
    g.tool.const1 = 500 * 4 * math.atan(1) / 180 / 2 ** 15
    g.tool.const2 = 8 * 9.82 / 2 ** 15

    g.tool.loading = True

    g.rtv.registry.save_setting(g.rtv.app.title, "Settings", "PATH", g.rtv.app.path)

    path = os.path.join(g.rtv.app.path, "login.txt")
    if t.get_str_from_file(path) == "no":
        g.tool.login = False
    else:
        g.tool.login = True

    # TODO: make work for any linux OS without mydocuments folder
    # g.tool.myDocFolderRoot = os.path.join(userpaths.get_my_documents(), g.rtv.app.title)
    g.tool.myDocFolderRoot = os.path.join(os.getcwd(), g.rtv.app.title)

    # DEBUG
    g.tool.user = "frank.ladman@gmx.at"
    g.tool.password = "stepfu"
    g.tool.user2 = "admin"
    g.tool.password2 = "admin"
    g.tool.myDocFolder = os.path.join(g.tool.myDocFolderRoot, t.unreadable(g.tool.user))

    if t.check_for_update():
        pass

    # g.rt.get_child("combo3")['values'] = ("Comma", "Tab", "Space")
    # g.rt.get_child("combo4")['values'] = ("Point", "Comma")
    # g.rt.get_child("combo5")['values'] = ("CrLf", "Cr", "Lf")

    # g.rt.vars["combo3"] = tk.StringVar(value=["Comma", "Tab", "Space"])
    # g.rt.vars["combo4"].set(("Point", "Comma"))
    # g.rt.vars["combo5"].set(("CrLf", "Cr", "Lf"))

    g.tool.sensorTypes[0] = "Date"
    g.tool.sensorTypes[1] = "Timer right"
    g.tool.sensorTypes[2] = "Pressure sensor right"
    g.tool.sensorTypes[3] = "Pressure sensor left"
    g.tool.sensorTypes[4] = "Vertical acceleration sensor right"
    g.tool.sensorTypes[5] = "Vertical acceleration sensor left"
    g.tool.sensorTypes[6] = "ML acceleration sensor right"
    g.tool.sensorTypes[7] = "ML acceleration sensor left"
    g.tool.sensorTypes[8] = "AP acceleration sensor right"
    g.tool.sensorTypes[9] = "AP acceleration sensor left"
    g.tool.sensorTypes[10] = "Gyro vertical axis sensor right"
    g.tool.sensorTypes[11] = "Gyro vertical axis sensor left"
    g.tool.sensorTypes[12] = "Gyro ML axis sensor right"
    g.tool.sensorTypes[13] = "Gyro ML axis sensor left"
    g.tool.sensorTypes[14] = "Gyro AP axis sensor right"
    g.tool.sensorTypes[15] = "Gyro AP axis sensor left"
    g.tool.sensorTypes[16] = "Timer left"
    g.tool.sensorTypes[17] = "Day Time right"
    g.tool.sensorTypes[18] = "Day Time left"
    g.tool.sensorTypes[19] = "Other"

    g.tool.sensorOptions[0] = "Pressure: Heel sensor"
    g.tool.sensorOptions[1] = "Pressure: Toe sensor"
    g.tool.sensorOptions[2] = "Pressure: Pressure summation"
    g.tool.sensorOptions[3] = "Date: MM/DD/YYYY"
    g.tool.sensorOptions[4] = "Date: DD/MM/YYYY"
    g.tool.sensorOptions[5] = "Date: MMDDYYYY"
    g.tool.sensorOptions[6] = "Date: DDMMYYYY"
    g.tool.sensorOptions[7] = "Date: YYYY-MM-DD"

    g.tool.configuration.stepDiffFilter = g.rt.vars["text1"].get()
    g.tool.configuration.removeNoOfStrides = g.rt.vars["text2"].get()
    g.tool.configuration.stepRecognitionRude = g.rt.vars["text3"].get()
    g.tool.configuration.cleanGaitMinTime = g.rt.vars["text7"].get()
    g.tool.configuration.cuttings = g.rt.vars["text8"].get()
    g.tool.configuration.heightFilter = g.rt.vars["text9"].get()
    g.tool.configuration.removeHighestLowest = g.rt.vars["text10"].get()

    g.tool.configuration.changed = False
    form_load_sensor_selector()


def put_configuration_to_controls(c: m.ConfigurationType):
    """
    
    """
    patterns = []
    # Put to controls

    if c.inputType == 0:
        g.rt.vars["option1"].set(RadioValues.option1.value)
    elif c.inputType == 1:
        g.rt.vars["option2"].set(RadioValues.option2.value)

    list3 = g.rt.get_child("list3")
    list5 = g.rt.get_child("list5")
    list6 = g.rt.get_child("list6")
    list7 = g.rt.get_child("list7")
    list8 = g.rt.get_child("list8")
    list16 = g.rt.get_child("list16")
    list19 = g.rt.get_child("list19")
    list20 = g.rt.get_child("list20")

    list3.delete(0, tk.END)
    list5.delete(0, tk.END)
    list6.delete(0, tk.END)
    list7.delete(0, tk.END)
    list8.delete(0, tk.END)
    list16.delete(0, tk.END)
    list19.delete(0, tk.END)
    list20.delete(0, tk.END)

    for i, user in enumerate(c.users):
        list3.insert(tk.END, user.name)
        list3.selection_set(i)
        if user.active:
            if user.faller == m.Faller.FALLER:
                list5.insert(tk.END, user.name)
                list8.insert(tk.END, user.name)
            elif user.faller == m.Faller.NON_FALLER:
                list6.insert(tk.END, user.name)
                list19.insert(tk.END, user.name)
            elif user.faller == m.Faller.CONTROL_GROUP_FALLER:
                g.rt.get_child("list17").insert(tk.END, user.name)
                list20.insert(tk.END, user.name)
            elif user.faller == m.Faller.CONTROL_GROUP_NON_FALLER:
                g.rt.get_child("list4").insert(tk.END, user.name)
                list16.insert(tk.END, user.name)

    if c.skipLines > 0:
        g.rt.vars["text5"].set(c.skipLines)
        g.rt.vars["check1"].set(True)
    else:
        g.rt.vars["text5"].set(0)
        g.rt.vars["check1"].set(False)

    if c.columnSeparator == ord(","):
        g.rt.get_child("combo3").current(1)
    elif c.columnSeparator == ord("\t"):
        g.rt.get_child("combo3").current(2)
    elif c.columnSeparator == ord(" "):
        g.rt.get_child("combo3").current(3)

    if c.decimalSeparator == ord("."):
        g.rt.get_child("combo4").current(1)
    elif c.decimalSeparator == ord(","):
        g.rt.get_child("combo4").current(2)

    if c.lineSeparator == 23:
        g.rt.get_child("combo5").current(1)
    elif c.lineSeparator == 13:
        g.rt.get_child("combo5").current(2)
    elif c.lineSeparator == 10:
        g.rt.get_child("combo5").current(3)

    list9 = g.rt.get_child("list9")
    for i in range(len(c.columns)):
        list9.insert(tk.END, c.columns[i])
        g.rtv.list9Itemdata.append(c.columnType[i])

    if c.sampleFrequency > 0:
        g.rt.vars["text20"].set(c.sampleFrequency)
        # enable text20 and label39

    combo1 = g.rt.get_child("combo1")
    combo1.delete(0, tk.END)
    marker = -1
    for i in range(len(c.users)):
        if c.users[i].active:
            combo1['values'] = [*combo1['values']] + [c.users[i].name]
            if c.users[i].name == c.selectedUser:
                marker = i

    if marker != -1:
        combo1.selection_set(marker)

    arr = c.selectToWatch.split("|")
    list1 = g.rt.get_child("list1")
    list15 = g.rt.get_child("list15")
    list1.delete(0, tk.END)
    list15.delete(0, tk.END)
    for i, gaitParDef in enumerate(c.gaitParameterDef):
        list15.insert(tk.END, gaitParDef.name)
        if not t.is_array_empty(arr):
            for j in range(len(arr)):
                if arr[j] == gaitParDef.name:
                    list15.selection_set(tk.END)
        list1.insert(tk.END, gaitParDef.name)

    arr = c.sensorToWatch.split("|")
    list14 = g.rt.get_child("list14")
    list14.delete(0, tk.END)
    for i, col in enumerate(c.columns):
        if c.columnType[i] != 0 and c.columnType[i] != 1:
            list14.insert(tk.END, col)
            if not t.is_array_empty(arr):
                for j in range(len(arr)):
                    if arr[j] == col:
                        list14.selection_set(tk.END)

    list13 = g.rt.get_child("list13")
    list13.delete(0, tk.END)
    for i in range(len(c.users)):
        if c.users[i].active:
            list13.insert(tk.END, c.users[i].name)

    list12 = g.rt.get_child("list12")
    list12.delete(0, tk.END)
    for gaitParDef in c.gaitParameterDef:
        list12.insert(tk.END, gaitParDef.name)
        list12.insert(tk.END, f"{gaitParDef.name} variation")

    path = os.path.join(g.tool.myDocFolderRoot, "pattern")
    comPatt = t.get_file_list_from_path(path, "pattern")
    for i in range(len(comPatt)):
        pat = m.Pattern1()
        pat.formula = [""] * 6
        path = os.path.join(g.tool.myDocFolderRoot, "pattern", comPatt[i])
        arr = t.get_arr_from_file(path)
        pat.name = comPatt[i].replace(".pattern", "")
        pat.formula[0] = arr[0]
        pat.formula[1] = arr[1]
        pat.formula[2] = arr[2]
        pat.formula[3] = arr[3]
        pat.formula[4] = arr[4]
        pat.formula[5] = arr[5]
        pat.description = arr[6]
        add_pattern(pat)

    path = os.path.join(g.tool.myDocFolderRoot, "FRI")
    comPatt = t.get_file_list_from_path(path, "fri")
    for i in range(len(comPatt)):
        fri = m.RiskIndex()
        path = os.path.join(g.tool.myDocFolderRoot, "FRI", comPatt[i])
        arr = t.get_arr_from_file(path)
        fri.name = comPatt[i].replace(".fri", "")
        fri.greenEnd[0] = arr[0]
        fri.greenStart[1] = arr[1]
        fri.yellowEnd[2] = arr[2]
        fri.yellowStart[3] = arr[3]
        fri.redEnd[4] = arr[4]
        fri.redStart[5] = arr[5]
        # TODO: add fri components, but folders seem empty... unused?
        t.add_FRI(fri)

    list7 = g.rt.get_child("list7")
    list10 = g.rt.get_child("list10")
    list7.delete(0, tk.END)
    list10.delete(0, tk.END)
    for pat1 in c.gaitPattern1:
        list7.insert(tk.END, pat1.name)
        list10.insert(tk.END, pat1.name)

    # TODO: treeview1

    list2 = g.rt.get_child("list2")
    list2.delete(0, tk.END)
    for i, fri in enumerate(c.fallRiskIndex):
        list2.insert(tk.END, fri.name)
        if fri.active:
            marker = i
        # warning: marker might not be always set
        list2.selection_set(marker)

    combo2 = g.rt.get_child("combo2")
    for user in c.users:
        if user.active:
            combo2['values'] = [*combo2["values"]] + [user.name]

    update_list()

    for widgetName in ["text4", "mainlist", "label22", "label16", "combo3", "combo4", "combo5", "check1", "text5",
                       "label17", "label39", "text20"]:
        if c.inputType == 1:
            g.rt.get_child(widgetName).grid()
        else:
            g.rt.get_child(widgetName).grid_remove()


def mnuopenconfig_click():
    if g.tool.configuration.changed:
        if messagebox.askyesno(message="Your configuration has changed. Save it ?"):
            save_configuration(False)
        else:
            return

    initDir = os.path.join(g.tool.myDocFolder, "configurations")
    filename = filedialog.askopenfilename(initialdir=initDir, filetypes=[("configuration", "*.configuration")])

    if filename != "":
        g.tool.loadingConf = True
        # filename = filename.replace(".configuration", "")
        open_configuration(filename)


def mnusaveconfig_click():
    cond1 = check_for_time_column()
    if False:  # not cond1 and g.tool.configuration.sampleFrequency == 0:
        messagebox.showerror(message="Please add the sample frequency")
        text20 = g.rt.get_child("text20")
        text20['state'] = tk.NORMAL
        text20['background'] = "red"
    else:
        save_configuration(False)


def check_for_time_column() -> bool:
    res = False
    if len(g.tool.configuration.columns) > 0:
        marker = False
        for i in range(len(g.tool.configuration.columns)):
            if g.tool.configuration.columnType[i] == 1:
                marker = True
                break
        if marker:
            res = True
            g.rt.get_child("text20")['state'] = tk.DISABLED
            g.rt.vars["text20"].set(0)
            g.rt.get_child("label39")['state'] = tk.DISABLED
        else:
            res = False
            g.rt.get_child("text20")['state'] = tk.NORMAL
            g.rt.get_child("label39")['state'] = tk.NORMAL
    return res


# repo
def open_configuration(path: str) -> bool:
    """
    
    """
    nr = 0
    cnt = 0
    cnt2 = 0
    fri_merker = False
    area = 0

    arr = t.get_arr_from_file(path)
    i = 0
    # compensation for increasing index first
    i -= 1
    while i < len(arr) - 1:
        i += 1
        arr[i] = arr[i].removesuffix("\n")
        if arr[i] != "":
            if nr > 0:
                # Read values Area 1
                if nr == 1:
                    g.tool.configuration.name = t.rem_k(arr[i])
                    nr = -1
                    continue
                elif nr == 2:
                    g.tool.configuration.inputType = int(t.rem_k(arr[i]))
                    nr = -1
                    continue
                elif nr == 3:
                    if arr[i] != "]":
                        buf = t.rem_k(arr[i])
                        newUser = m.UserType()

                        i += 1
                        elements = t.rem_k(arr[i]).split("|")
                        newUser.name = t.crypt(elements[0])
                        if len(elements) >= 2:
                            newUser.id = elements[1]
                        if buf == "-":
                            path = os.path.join(g.tool.myDocFolder, "data", newUser.id)
                            newUser.filePath = path
                        else:
                            newUser.filePath = buf
                        i += 1
                        newUser.active = True if t.rem_k(arr[i]) == "1" else False
                        i += 1
                        newUser.faller = m.Faller(int(t.rem_k(arr[i])))
                        i += 1
                        newUser.fallSelectedAppr2 = True if t.rem_k(arr[i]) == "1" else False
                        i += 1
                        newUser.falls = t.get_falls(newUser.id)

                        path = os.path.join(g.tool.myDocFolder, "configurations", g.tool.configuration.name, "subjects",
                                            newUser.id, "parameter", "LastDate.txt")
                        a = t.get_str_from_file(path)
                        b = t.get_date_from_str(a)

                        newUser.lastProcessedDate = t.get_str_from_file(path).strip()
                        i += 1
                        newUser.selectedApp1 = True if t.rem_k(arr[i]) == "1" else False
                        i += 1
                        newUser.age = int(t.rem_k(arr[i]))
                        i += 1
                        newUser.note = "\n".join(t.rem_k(arr[i]).split("|"))
                        i += 1
                        if t.rem_k(arr[i]) != "-":
                            newUser.showParameter = t.rem_k(arr[i]).split("|")
                        i += 1
                        if t.rem_k(arr[i]) != "-":
                            newUser.showFRI = t.rem_k(arr[i]).split("|")
                        i += 1
                        if t.rem_k(arr[i]) != "-":
                            newUser.showStats = t.rem_k(arr[i]).split("|")
                        i += 1
                        newUser.firstname = t.crypt(t.rem_k(arr[i]))
                        i += 1
                        newUser.lastname = t.crypt(t.rem_k(arr[i]))
                        if newUser.name != f"{newUser.firstname} {newUser.lastname} {newUser.id}":
                            newUser.name = f"{newUser.firstname} {newUser.lastname} {newUser.id}"

                        i += 1
                        newUser.phone = t.rem_k(arr[i])
                        i += 1
                        # ********************************************* "abc.def@xy.com"
                        newUser.email = t.rem_k(arr[i])
                        i += 1
                        newUser.address = "\r\n".join(t.rem_k(arr[i]).split("|"))
                        i += 1
                        newUser.insole = t.rem_k(arr[i])
                        i += 1
                        newUser.ampelOnPhone = True if t.rem_k(arr[i]) == "1" else False
                        i += 1
                        newUser.pressureCaliPath = t.rem_k(arr[i])
                        i += 1
                        newUser.filter = True if t.rem_k(arr[i]) == "1" else False
                        i += 1
                        newUser.stepDiffFilter = int(t.rem_k(arr[i]))
                        i += 1
                        newUser.removeNoOfStrides = int(t.rem_k(arr[i]))
                        i += 1
                        newUser.stepRecognitionRude = int(t.rem_k(arr[i]))
                        i += 1
                        newUser.minNoOfStrides = int(t.rem_k(arr[i]))
                        i += 1
                        newUser.cleanGaitMinTime = int(t.rem_k(arr[i]))
                        i += 1
                        newUser.cuttings = int(t.rem_k(arr[i]))
                        i += 1
                        newUser.heightFilter = float(t.rem_k(arr[i]))
                        i += 1
                        newUser.removeHighestLowest = float(t.rem_k(arr[i]))
                        i += 1
                        newUser.uploadStats = True if t.rem_k(arr[i]) == "1" else False
                        i += 1
                        i += 1
                        i += 1

                        if arr[i][-1] == "]":
                            nr = -1
                        cnt += 1
                        g.tool.configuration.users.append(newUser)
                    else:
                        nr = -1
                    continue
                elif nr == 4:
                    g.tool.configuration.skipLines = int(t.rem_k(arr[i]))
                    nr = -1
                    continue
                elif nr == 5:
                    if t.rem_k(arr[i]) == "comma":
                        g.tool.configuration.columnSeparator = ord(",")
                    elif t.rem_k(arr[i]) == "tab":
                        g.tool.configuration.columnSeparator = ord("\t")
                    elif t.rem_k(arr[i]) == "space":
                        g.tool.configuration.columnSeparator = ord(" ")
                    nr = -1
                    continue
                elif nr == 6:
                    if t.rem_k(arr[i]) == "point":
                        g.tool.configuration.decimalSeparator = ord(".")
                    elif t.rem_k(arr[i]) == "comma":
                        g.tool.configuration.decimalSeparator = ord(",")
                    nr = -1
                    continue
                elif nr == 7:
                    if t.rem_k(arr[i]) == "CrLf":
                        g.tool.configuration.lineSeparator = 23
                    elif t.rem_k(arr[i]) == "Cr":
                        g.tool.configuration.lineSeparator = 13
                    elif t.rem_k(arr[i]) == "Lf":
                        g.tool.configuration.lineSeparator = 10
                    nr = -1
                    continue
                elif nr == 8:
                    if arr[i] != "]":
                        redim_preserve(g.tool.configuration.columns, cnt + 1)
                        redim_preserve(g.tool.configuration.columnType, cnt + 1)
                        redim_preserve(g.tool.configuration.columnOption, cnt + 1)
                        redim_preserve(g.tool.configuration.columnUnit, cnt + 1)
                        if arr[i][-1] == "]":
                            arr[i] = arr[i][0:-1]
                            nr = -1
                        elements = t.rem_k(arr[i]).split("|")
                        g.tool.configuration.columns[cnt] = elements[0]
                        g.tool.configuration.columnType[cnt] = elements[1]
                        g.tool.configuration.columnOption[cnt] = elements[2]
                        g.tool.configuration.columnUnit[cnt] = elements[3]
                        cnt += 1
                    else:
                        nr = -1
                    continue
                elif nr == 9:
                    g.tool.configuration.sampleFrequency = int(t.rem_k(arr[i]))
                    nr = -1
                    continue

                # read values area 2
                elif nr == 101:
                    g.tool.configuration.selectedUser = t.rem_k(arr[i])
                    nr = -1
                    continue
                elif nr == 102:
                    g.tool.configuration.stepDiffFilter = float(t.rem_k(arr[i]))
                    nr = -1
                    continue
                elif nr == 103:
                    g.tool.configuration.removeNoOfStrides = int(t.rem_k(arr[i]))
                    nr = -1
                    continue
                elif nr == 104:
                    g.tool.configuration.stepRecognitionRude = int(t.rem_k(arr[i]))
                    nr = -1
                    continue
                elif nr == 105:
                    g.tool.configuration.minNoOfStrides = int(t.rem_k(arr[i]))
                    nr = -1
                    continue
                elif nr == 106:
                    g.tool.configuration.cleanGaitMinTime = int(t.rem_k(arr[i]))
                    nr = -1
                    continue
                elif nr == 107:
                    g.tool.configuration.cuttings = int(t.rem_k(arr[i]))
                    nr = -1
                    continue
                elif nr == 108:
                    g.tool.configuration.heightFilter = float(t.rem_k(arr[i]))
                    nr = -1
                    continue
                elif nr == 109:
                    g.tool.configuration.removeHighestLowest = float(t.rem_k(arr[i]))
                    nr = -1
                    continue
                elif nr == 110:
                    g.tool.configuration.selectToWatch = t.rem_k(arr[i])
                    nr = -1
                    continue
                elif nr == 111:
                    g.tool.configuration.sensorToWatch = t.rem_k(arr[i])
                    nr = -1
                    continue
                elif nr == 112:
                    g.tool.configuration.filter = True if t.rem_k(arr[i]) == "1" else False
                    nr = -1
                    continue

                # read values area 3
                elif nr == 201:
                    if arr[i] != "]":
                        # if cnt == 0:
                        #     cnt = 1
                        redim_preserve(g.tool.configuration.gaitParameterDef, cnt + 1)
                        g.tool.configuration.gaitParameterDef[-1] = m.GaitDef()
                        g.tool.configuration.gaitParameterDef[cnt].name = t.rem_k(arr[i])
                        i += 1
                        g.tool.configuration.gaitParameterDef[cnt].unit = t.rem_k(arr[i])
                        i += 1
                        g.tool.configuration.gaitParameterDef[cnt].active = True
                        i += 1
                        g.tool.configuration.gaitParameterDef[cnt].script = t.rem_k(arr[i]).split("|")
                        for j in range(len(g.tool.configuration.users)):
                            redim_preserve(g.tool.configuration.users[j].gaitParameter, cnt + 1)
                            for k in range(len(g.tool.configuration.users[j].gaitParameter)):
                                g.tool.configuration.users[j].gaitParameter[k] = m.GaitParameterType()
                            g.tool.configuration.users[j].gaitParameter[cnt - 1].name = \
                                g.tool.configuration.gaitParameterDef[cnt].name
                        if arr[i][-1] == "]":
                            nr = -1
                        cnt += 1
                    else:
                        nr = -1
                    continue

                # read values area 4
                elif nr == 301:
                    if arr[i] != "]":
                        g.tool.configuration.gaitPattern1.append(m.Pattern1())
                        g.tool.configuration.gaitPattern1[cnt].name = t.rem_k(arr[i])
                        i += 1
                        g.tool.configuration.gaitPattern1[cnt].mean = float(t.rem_k(arr[i]))
                        i += 1
                        g.tool.configuration.gaitPattern1[cnt].variance = float(t.rem_k(arr[i]))
                        i += 1
                        g.tool.configuration.gaitPattern1[cnt].stdDev = float(t.rem_k(arr[i]))
                        i += 1
                        g.tool.configuration.gaitPattern1[cnt].stdErr = float(t.rem_k(arr[i]))
                        i += 1
                        g.tool.configuration.gaitPattern1[cnt].forAll = True if t.rem_k(arr[i]) == "1" else False
                        i += 1
                        g.tool.configuration.gaitPattern1[cnt].formula = t.rem_k(arr[i]).split("|")
                        # warning: < 5 ???
                        if len(g.tool.configuration.gaitPattern1[cnt].formula) < 6:
                            redim_preserve(g.tool.configuration.gaitPattern1[cnt].formula, 6)
                        i += 1
                        g.tool.configuration.gaitPattern1[cnt].description = t.rem_k(arr[i]).replace("|", "\n")
                        if arr[i][-1] == "]":
                            nr = -1
                        cnt += 1
                    else:
                        nr = -1
                    continue
                elif nr == 302:
                    if arr[i] != "]":
                        redim_preserve(g.tool.configuration.gaitPattern2, cnt + 1)
                        g.tool.configuration.gaitPattern2[cnt].base = t.rem_k(arr[i])
                        i += 1
                        g.tool.configuration.gaitPattern2[cnt].name = t.rem_k(arr[i])
                        i += 1
                        g.tool.configuration.gaitPattern2[cnt].evolution = t.rem_k(arr[i]).split("|")
                        i += 1
                        g.tool.configuration.gaitPattern2[cnt].description = t.rem_k(arr[i])
                        if arr[i][-1] == "]":
                            nr = -1
                        cnt += 1
                    else:
                        nr = -1
                    continue
                elif nr == 303:
                    elements = t.rem_k(arr[i]).split("|")
                    g.tool.configuration.filterStdDevF = float(elements[0])
                    g.tool.configuration.filterStdDevN = float(elements[1])
                    nr = -1
                    continue
                elif nr == 304:
                    elements = t.rem_k(arr[i]).split("|")
                    g.tool.configuration.filterVarianceF = float(elements[0])
                    g.tool.configuration.filterVarianceN = float(elements[1])
                    nr = -1
                    continue
                elif nr == 305:
                    elements = t.rem_k(arr[i]).split("|")
                    g.tool.configuration.filterStdErrF = float(elements[0])
                    g.tool.configuration.filterStdErrN = float(elements[1])
                    nr = -1
                    continue
                elif nr == 306:
                    elements = t.rem_k(arr[i]).split("|")
                    g.tool.configuration.filterHighLowF = float(elements[0])
                    g.tool.configuration.filterHighLowN = float(elements[1])
                    nr = -1
                    continue

                # read values area 5
                elif nr == 401:
                    if arr[i] != "]":
                        g.tool.configuration.fallRiskIndex.append(m.RiskIndex())
                        g.tool.configuration.fallRiskIndex[cnt].name = t.rem_k(arr[i])
                        i += 1
                        if t.rem_k(arr[i]) == "1":
                            if not fri_merker:
                                g.tool.configuration.fallRiskIndex[cnt].active = True
                                fri_merker = True
                            else:
                                g.tool.configuration.fallRiskIndex[cnt].active = False
                        else:
                            g.tool.configuration.fallRiskIndex[cnt].active = False
                        i += 1
                        g.tool.configuration.fallRiskIndex[cnt].redStart = float(t.rem_k(arr[i]))
                        i += 1
                        g.tool.configuration.fallRiskIndex[cnt].redEnd = float(t.rem_k(arr[i]))
                        i += 1
                        g.tool.configuration.fallRiskIndex[cnt].yellowStart = float(t.rem_k(arr[i]))
                        i += 1
                        g.tool.configuration.fallRiskIndex[cnt].yellowEnd = float(t.rem_k(arr[i]))
                        i += 1
                        g.tool.configuration.fallRiskIndex[cnt].greenStart = float(t.rem_k(arr[i]))
                        i += 1
                        g.tool.configuration.fallRiskIndex[cnt].greenEnd = float(t.rem_k(arr[i]))
                        i += 1
                        g.tool.configuration.fallRiskIndex[cnt].forAll = t.rem_k(arr[i]) == "1"

                        nr = -1
                    else:
                        nr = -1
                    continue
                elif nr == 402:
                    if arr[i] != "]":
                        elements = t.rem_k(arr[i]).split("|")
                        g.tool.configuration.fallRiskIndex[cnt].components.append(m.Component())
                        g.tool.configuration.fallRiskIndex[cnt].components[cnt2].elementName = t.rem_k(elements[0])
                        g.tool.configuration.fallRiskIndex[cnt].components[cnt2].weight = float(t.rem_k(elements[1]))
                        g.tool.configuration.fallRiskIndex[cnt].components[cnt2].impact = float(t.rem_k(elements[2]))
                        if arr[i][-1] == "]":
                            nr = 401
                            cnt += 1
                        cnt2 += 1
                    else:
                        nr = 401
                        cnt += 1
                    continue

                # read values area 6
                elif nr == 501:
                    g.tool.configuration.selectedFactsheet = t.rem_k(arr[i])
                    nr = -1
                    continue

            # set area
            if arr[i] == "-1-":
                area = 1
                continue
            elif arr[i] == "-2-":
                area = 2
                continue
            elif arr[i] == "-3-":
                area = 3
                continue
            elif arr[i] == "-4-":
                area = 4
                continue
            elif arr[i] == "-5-":
                area = 5
                continue
            elif arr[i] == "-6-":
                area = 6
                continue

            # set pointer in area
            if area == 1:
                if arr[i] == "[name":
                    nr = 1
                    continue
                elif arr[i] == "[data input":
                    nr = 2
                    continue
                elif arr[i] == "[selected":
                    nr = 3
                    cnt = 0
                    continue
                elif arr[i] == "[skip":
                    nr = 4
                    continue
                elif arr[i] == "[column separator":
                    nr = 5
                    continue
                elif arr[i] == "[decimal separator":
                    nr = 6
                    continue
                elif arr[i] == "[newline separator":
                    nr = 7
                    continue
                elif arr[i] == "[columns":
                    nr = 8
                    cnt = 0
                    continue
                elif arr[i] == "[sample":
                    nr = 9
                    continue
            elif area == 2:
                if arr[i] == "[subject":
                    nr = 101
                    continue
                elif arr[i] == "[step diff filter":
                    nr = 102
                    continue
                elif arr[i] == "[remove no of strides":
                    nr = 103
                    continue
                elif arr[i] == "[step recognition rude":
                    nr = 104
                    continue
                elif arr[i] == "[min no of strides":
                    nr = 105
                    continue
                elif arr[i] == "[clean gait min time frame":
                    nr = 106
                    continue
                elif arr[i] == "[cuttings":
                    nr = 107
                    continue
                elif arr[i] == "[height filter":
                    nr = 108
                    continue
                elif arr[i] == "[remove highest lowest":
                    nr = 109
                    continue
                elif arr[i] == "[select gait parameter":
                    nr = 110
                    continue
                elif arr[i] == "[select sensor":
                    nr = 111
                    continue
                elif arr[i] == "[filter data":
                    nr = 112
                    continue
            elif area == 3:
                if arr[i] == "[gait parameter":
                    nr = 201
                    cnt = 0
                    continue
            elif area == 4:
                if arr[i] == "[list of pattern":
                    nr = 301
                    cnt = 0
                    continue
                if arr[i] == "[list of pattern2":
                    nr = 302
                    cnt = 0
                    continue
                if arr[i] == "[filter stddev":
                    nr = 303
                elif arr[i] == "[filter variance":
                    nr = 304
                elif arr[i] == "[filter stderr":
                    nr = 305
                elif arr[i] == "[filter highlow":
                    nr = 306
            elif area == 5:
                if arr[i] == "[fall risk index":
                    nr = 401
                    cnt = 0
                    continue
                elif arr[i] == "[components":
                    nr = 402
                    cnt2 = 0
                    continue
            elif area == 6:
                if arr[i] == "[subject":
                    nr = 501
                    continue
        # NEXTONE

    put_configuration_to_controls(g.tool.configuration)
    g.tool.configuration.changed = False
    g.tool.configuration.coreChange = False

    g.tool.loadingConf = False
    # list2_click
    # combo2_click

    # warning
    return False


# repo
def save_configuration(quiet: bool) -> bool:
    """
    Store all elements in singleton "Configuration" of type ConfigurationType to files.

    Return True if an attempt to save is made (a.k.a. no filedialog cancelled)
    """
    res = False
    if g.tool.configuration.name == "":
        quiet = False

    if len(g.tool.configuration.users) <= 0:
        messagebox.showinfo(
            message="You need to add at least one subject to the configuration, before you can save it.")
        return False

    if len(g.tool.configuration.columns) <= 0:
        messagebox.showinfo(message="You need to add at least one column to the configuration, before you can save it.")
        return False

    initDir = os.path.join(g.tool.myDocFolder, "configurations")

    title = g.tool.configuration.name if g.tool.configuration.name != "Default" else ""

    if not quiet:
        if g.tool.configuration.name == "WIISEL default":
            g.tool.configuration.name = f"WIISEL default {g.tool.user}"

        filename = filedialog.asksaveasfilename(defaultextension="*.configuration", initialdir=initDir, title=title)

    else:
        title = g.tool.configuration.name
        filename = os.path.join(g.tool.myDocFolder, "configurations", g.tool.configuration.name)

    if filename != "":
        if title != "":
            if ".configuration" not in title:
                title = title + ".configuration"
            if ".configuration" not in filename:
                filename = filename + ".configuration"
            # g.tool.configuration.name = title.replace(".configuration", "")

            if 1 == 1 or quiet:
                res = True
                t.save_str_to_file(filename, "-1-\n")
                t.append_str_to_file(filename, "[name")
                t.append_str_to_file(filename, f"{g.tool.configuration.name}]")
                t.append_str_to_file(filename, "[data input")
                t.append_str_to_file(filename, f"{g.tool.configuration.inputType}]")
                t.append_str_to_file(filename, "[selected")
                ubnd = min(len(g.tool.configuration.users), len(g.tool.patients))
                # ubnd = len(g.tool.configuration.users)
                for i in range(ubnd):
                    if len(g.tool.patients) < len(g.tool.configuration.users):
                        ubnd = len(g.tool.patients)
                    if g.tool.configuration.users[i].filePath == os.path.join(g.tool.myDocFolder, "data",
                                                                              g.tool.patients[i].userID):
                        t.append_str_to_file(filename, "-")
                    else:
                        t.append_str_to_file(filename, g.tool.configuration.users[i].filePath)
                    t.append_str_to_file(filename,
                                         f"{g.tool.configuration.users[i].name}|{g.tool.configuration.users[i].id}")
                    t.append_str_to_file(filename, "1" if g.tool.configuration.users[i].active else "0")
                    t.append_str_to_file(filename, g.tool.configuration.users[i].faller.name)
                    t.append_str_to_file(filename, "1" if g.tool.configuration.users[i].fallSelectedAppr2 else "0")

                    t.append_str_to_file(filename, "-")

                    t.append_str_to_file(filename, "1" if g.tool.configuration.users[i].selectedApp1 else "0")
                    t.append_str_to_file(filename, str(g.tool.configuration.users[i].age))
                    t.append_str_to_file(filename, "|".join(g.tool.configuration.users[i].note.split("\r\n")))
                    if not t.is_array_empty(g.tool.configuration.users[i].showParameter):
                        t.append_str_to_file(filename, "|".join(g.tool.configuration.users[i].showParameter))
                    else:
                        t.append_str_to_file(filename, "-")
                    if not t.is_array_empty(g.tool.configuration.users[i].showFRI):
                        t.append_str_to_file(filename, "|".join(g.tool.configuration.users[i].showFRI))
                    else:
                        t.append_str_to_file(filename, "-")
                    if not t.is_array_empty(g.tool.configuration.users[i].showStats):
                        t.append_str_to_file(filename, "|".join(g.tool.configuration.users[i].showStats))
                    else:
                        t.append_str_to_file(filename, "-")
                    t.append_str_to_file(filename, g.tool.configuration.users[i].firstname)
                    t.append_str_to_file(filename, g.tool.configuration.users[i].lastname)
                    t.append_str_to_file(filename, g.tool.configuration.users[i].phone)
                    t.append_str_to_file(filename, g.tool.configuration.users[i].email)
                    t.append_str_to_file(filename, "|".join(g.tool.configuration.users[i].address.split("\r\n")))
                    t.append_str_to_file(filename, g.tool.configuration.users[i].insole)
                    t.append_str_to_file(filename, "1" if g.tool.configuration.users[i].ampelOnPhone else "0")
                    t.append_str_to_file(filename, "-" if g.tool.configuration.users[i].pressureCaliPath == "" else
                    g.tool.configuration.users[i].pressureCaliPath)

                    t.append_str_to_file(filename, "1" if g.tool.configuration.users[i].filter else "0")
                    t.append_str_to_file(filename, str(g.tool.configuration.users[i].stepDiffFilter))
                    t.append_str_to_file(filename, str(g.tool.configuration.users[i].removeNoOfStrides))
                    t.append_str_to_file(filename, str(g.tool.configuration.users[i].stepRecognitionRude))
                    t.append_str_to_file(filename, str(g.tool.configuration.users[i].minNoOfStrides))
                    t.append_str_to_file(filename, str(g.tool.configuration.users[i].cleanGaitMinTime))
                    t.append_str_to_file(filename, str(g.tool.configuration.users[i].cuttings))
                    t.append_str_to_file(filename, str(g.tool.configuration.users[i].heightFilter))
                    t.append_str_to_file(filename, str(g.tool.configuration.users[i].removeHighestLowest))
                    t.append_str_to_file(filename, "1" if g.tool.configuration.users[i].uploadStats else "0")

                    t.append_str_to_file(filename, "-")  # reserve
                    t.append_str_to_file(filename, "-")  # reserve
                    t.append_str_to_file(filename, "-")  # reserve

                    t.make_user_paths(g.tool.configuration.users[i].id)

                t.append_str_to_file(filename, "]")
                t.append_str_to_file(filename, "[skip")
                t.append_str_to_file(filename, f"{g.tool.configuration.skipLines}]")
                t.append_str_to_file(filename, "[column separator")
                if g.tool.configuration.columnSeparator == ord(","):
                    t.append_str_to_file(filename, "comma]")
                elif g.tool.configuration.columnSeparator == ord("\t"):
                    t.append_str_to_file(filename, "tab]")
                elif g.tool.configuration.columnSeparator == ord(" "):
                    t.append_str_to_file(filename, "space]")
                else:
                    t.append_str_to_file(filename, "]")
                t.append_str_to_file(filename, "[decimal separator")
                if g.tool.configuration.decimalSeparator == ord("."):
                    t.append_str_to_file(filename, "point]")
                elif g.tool.configuration.decimalSeparator == ord(","):
                    t.append_str_to_file(filename, "comma]")
                else:
                    t.append_str_to_file(filename, "]")
                t.append_str_to_file(filename, "[newline separator")
                if g.tool.configuration.lineSeparator == 23:
                    t.append_str_to_file(filename, "CrLf]")
                elif g.tool.configuration.lineSeparator == 13:
                    t.append_str_to_file(filename, "Cr]")
                elif g.tool.configuration.lineSeparator == 10:
                    t.append_str_to_file(filename, "Lf]")
                else:
                    t.append_str_to_file(filename, "]")

                t.append_str_to_file(filename, "[columns")
                for i, col in enumerate(g.tool.configuration.columns):
                    if i < len(g.tool.configuration.columns):
                        t.append_str_to_file(filename,
                                             f"{col}|{g.tool.configuration.columnType[i]}|{g.tool.configuration.columnOption[i]}|{g.tool.configuration.columnUnit[i]}")
                    else:
                        t.append_str_to_file(filename,
                                             f"{col}|{g.tool.configuration.columnType[i]}|{g.tool.configuration.columnOption[i]}|{g.tool.configuration.columnUnit[i]}]")
                t.append_str_to_file(filename, "[sample")
                t.append_str_to_file(filename, f"{g.tool.configuration.sampleFrequency}]")
                t.append_str_to_file(filename, "")

                t.append_str_to_file(filename, "-2-")
                t.append_str_to_file(filename, "[subject")
                t.append_str_to_file(filename, f"{g.tool.configuration.selectedUser}]")
                t.append_str_to_file(filename, "[step diff filter")
                t.append_str_to_file(filename, f"{g.tool.configuration.stepDiffFilter}]")
                t.append_str_to_file(filename, "[remove no of strides")
                t.append_str_to_file(filename, f"{g.tool.configuration.removeNoOfStrides}]")
                t.append_str_to_file(filename, "[step recognition rude")
                t.append_str_to_file(filename, f"{g.tool.configuration.stepRecognitionRude}]")
                t.append_str_to_file(filename, "[min no of strides")
                t.append_str_to_file(filename, f"{g.tool.configuration.minNoOfStrides}]")
                t.append_str_to_file(filename, "[clean gait min time frame")
                t.append_str_to_file(filename, f"{g.tool.configuration.cleanGaitMinTime}]")
                t.append_str_to_file(filename, "[cuttings")
                t.append_str_to_file(filename, f"{g.tool.configuration.cuttings}]")
                t.append_str_to_file(filename, "[height filter")
                t.append_str_to_file(filename, f"{g.tool.configuration.heightFilter}]")
                t.append_str_to_file(filename, "[remove highest lowest")
                t.append_str_to_file(filename, f"{g.tool.configuration.removeHighestLowest}]")
                t.append_str_to_file(filename, "[select gait parameter")
                t.append_str_to_file(filename, f"{g.tool.configuration.selectToWatch}]")
                t.append_str_to_file(filename, "[select sensor")
                t.append_str_to_file(filename, f"{g.tool.configuration.sensorToWatch}]")
                t.append_str_to_file(filename, "[filter data")
                t.append_str_to_file(filename, f'{"1" if g.tool.configuration.filter else "0"}]')

                t.append_str_to_file(filename, "-3-")
                t.append_str_to_file(filename, "[gait parameter")
                if len(g.tool.configuration.gaitParameterDef) > 0:
                    for i, gaitParDef in enumerate(g.tool.configuration.gaitParameterDef):
                        t.append_str_to_file(filename, gaitParDef.name)
                        t.append_str_to_file(filename, gaitParDef.unit)
                        t.append_str_to_file(filename, "1")  # "1" if gaitParDef.Active else "0"
                        if i < len(g.tool.configuration.gaitParameterDef) - 1:
                            t.append_str_to_file(filename, "|".join(gaitParDef.script))
                        else:
                            t.append_str_to_file(filename, f'{"|".join(gaitParDef.script)}]')
                            if True:
                                print("True")
                else:
                    t.append_str_to_file(filename, "]")
                t.append_str_to_file(filename, "")

                t.append_str_to_file(filename, "-4-")
                t.append_str_to_file(filename, "[list of pattern")
                if len(g.tool.configuration.gaitPattern1) > 0:
                    for i, pat in enumerate(g.tool.configuration.gaitPattern1):
                        t.append_str_to_file(filename, pat.name)
                        t.append_str_to_file(filename, str(pat.mean))
                        t.append_str_to_file(filename, str(pat.variance))
                        t.append_str_to_file(filename, str(pat.stdDev))
                        t.append_str_to_file(filename, str(pat.stdErr))
                        t.append_str_to_file(filename, "1" if pat.forAll else "0")

                        t.append_str_to_file(filename, "|".join(pat.formula))
                        newline = "\n"
                        if i < len(g.tool.configuration.gaitPattern1) - 1:
                            t.append_str_to_file(filename, pat.description.replace(newline, "|"))
                        else:
                            t.append_str_to_file(filename, f'{pat.description.replace(newline, "|")}]')
                else:
                    t.append_str_to_file(filename, "]")
                t.append_str_to_file(filename, "[list of pattern2")
                if len(g.tool.configuration.gaitPattern2) > 0:
                    for i, pat in enumerate(g.tool.configuration.gaitPattern2):
                        t.append_str_to_file(filename, pat.base)
                        t.append_str_to_file(filename, pat.name)
                        t.append_str_to_file(filename, "|".join(pat.evolution))
                        if i < len(g.tool.configuration.gaitPattern2) - 1:
                            t.append_str_to_file(filename, pat.description)
                        else:
                            t.append_str_to_file(filename, f'{pat.description}]')
                else:
                    t.append_str_to_file(filename, "]")
                t.append_str_to_file(filename, "[filter stddev")
                t.append_str_to_file(filename,
                                     f'{g.tool.configuration.filterStdDevF}|{g.tool.configuration.filterStdDevN}]')
                t.append_str_to_file(filename, "[filter variance")
                t.append_str_to_file(filename,
                                     f'{g.tool.configuration.filterVarianceF}|{g.tool.configuration.filterVarianceN}]')
                t.append_str_to_file(filename, "[filter stderr")
                t.append_str_to_file(filename,
                                     f'{g.tool.configuration.filterStdErrF}|{g.tool.configuration.filterStdErrN}]')
                t.append_str_to_file(filename, "[filter highlow")
                t.append_str_to_file(filename,
                                     f'{g.tool.configuration.filterHighLowF}|{g.tool.configuration.filterHighLowN}]')
                t.append_str_to_file(filename, "")

                t.append_str_to_file(filename, "-5-")
                t.append_str_to_file(filename, "[fall risk index")
                if len(g.tool.configuration.fallRiskIndex) > 0:
                    for i, fri in enumerate(g.tool.configuration.fallRiskIndex):
                        t.append_str_to_file(filename, fri.name)
                        t.append_str_to_file(filename, "1" if fri.active else "0")
                        t.append_str_to_file(filename, str(fri.redStart))
                        t.append_str_to_file(filename, str(fri.redEnd))
                        t.append_str_to_file(filename, str(fri.yellowStart))
                        t.append_str_to_file(filename, str(fri.yellowEnd))
                        t.append_str_to_file(filename, str(fri.greenStart))
                        t.append_str_to_file(filename, str(fri.greenEnd))
                        t.append_str_to_file(filename, "1" if fri.forAll else "0")
                        t.append_str_to_file(filename, "[components")
                        if len(fri.components) > 0:
                            for j, comp in enumerate(fri.components):
                                if j < len(fri.components) - 1:
                                    t.append_str_to_file(filename, f'{comp.elementName}|{comp.weight}|{comp.impact}')
                                else:
                                    t.append_str_to_file(filename, f'{comp.elementName}|{comp.weight}|{comp.impact}]')
                        else:
                            t.append_str_to_file(filename, "]")
                t.append_str_to_file(filename, "]")
                t.append_str_to_file(filename, "")

                t.append_str_to_file(filename, "-6-")
                t.append_str_to_file(filename, "[subject")
                t.append_str_to_file(filename, f'{g.tool.configuration.selectedFactsheet}]')

                g.tool.configuration.changed = False
            else:
                messagebox.showinfo(
                    message="Please use a different name for the configuration. 'WIISEL default' is reserved.")
    return res


def command4_click():
    if g.tool.configuration.users[t.get_user_no(g.rt.vars["combo1"].get())].filterChange:
        if messagebox.askyesno(
                f"You made major changes to the configuration.\nThe gait parameter need to be recalculated. This may last some time. Continue?"):
            if save_configuration(True):
                g.tool.configuration.users[t.get_user_no(g.rt.vars["text1"].get())].lastProcessedDate = ""
                process_data()
            else:
                return
        else:
            return

    combo1 = g.rt.get_child("combo1")
    calendar1 = g.rt.get_child("calendar1")
    if len(combo1['values']) > 0:
        # str date format is M/D/YY
        dateStr = calendar1.get_date().split("/")
        date = datetime.date(int(dateStr[2]) + 2000, int(dateStr[0]), int(dateStr[1]))
        if g.tool.configuration.inputType == 1:
            path = os.path.join(
                f'{g.tool.configuration.users[t.get_user_no(combo1.get())].filePath}{g.tool.configuration.users[t.get_user_no(combo1.get())].name}')
            if os.path.isdir(path):
                if t.date_is_available_in_file(date, path):
                    g.rtv.date = date
        elif g.tool.configuration.inputType == 0:
            if t.folder_exists(g.tool.configuration.users[t.get_user_no(combo1.get())].filePath):
                path = os.path.join(g.tool.configuration.users[t.get_user_no(combo1.get())].filePath,
                                    f'reg_{date.day:02d}-{date.month:02d}-{date.year:04d}.txt')
                if t.file_exists(path):
                    g.rtv.date = date

        if g.rtv.date != m.default_datetime():
            if g.tool.configuration.sensorToWatch != "":
                clear_chart()
                command4 = g.rt.get_child("command4")
                command4['state'] = tk.DISABLED
                load_chart2()
                command4['state'] = tk.NORMAL
            else:
                messagebox.showwarning(message="Select at least one sensor to show")
        else:
            # StockChartX1.RemoveAllSeries
            # StockChartX1.ClearAllSeries
            # StockChartX1.ClearDrawings
            # StockChartX1.Update
            # TODO
            pass
    else:
        messagebox.showwarning(message="No subject selected")


def command5_click():
    codesenseWidget = g.rt.get_child("cs")

    list1 = g.rt.get_child("list1")
    selectedGaitParameterName = list1.get(tk.ACTIVE)

    rawFunction = codesenseWidget.get('1.0', tk.END)
    codesense.save_function(rawFunction, selectedGaitParameterName)

    codesense.execute_function(selectedGaitParameterName)


def cmdsensorhealth_click():
    form_load_sensor_health()


def sensors_click():
    """
    Each red circle has a mapping with it's relative position (in percentage) to the full image.
    """
    sensorsGrid = g.rt.get_child("sensors", root=g.rt.sensorHealth)

    sensorLayout = g.rt.get_child("sensorlayout", root=g.rt.sensorHealth)
    circles = sensorLayout.find_withtag("marked")
    for circle in circles:
        sensorLayout.delete(circle)

    selectedRowId = sensorsGrid.selection()[0]
    sensorNumbers = sensorsGrid.item(selectedRowId)['values'][1].split(",")
    mapping = {
        "0": (26.2, 10),
        "1": (26.2, 10),
        "2": (30.34, 61),
        "3": (17.24, 63),
        "4": (77.24, 15),
        "5": (63.45, 15),
        "6": (17.24, 81),
        "7": (35.86, 13),
        "8": (30.34, 41),
        "9": (75.5, 71),
        "10": (77.24, 87),
        "11": (63.45, 87),
        "12": (52.41, 90),
        "13": (35.86, 90)
    }
    for sensorNr in sensorNumbers:
        sensorNr = sensorNr.strip()
        if sensorNr in mapping:
            center = mapping[sensorNr]
            radius = 15
            x = int(sensorLayout['width']) * center[0] / 100
            y = int(sensorLayout['height']) * center[1] / 100
            top = (x - radius, y + radius)
            bottom = (x + radius, y - radius)
            sensorLayout.create_oval(top[0], top[1], bottom[0], bottom[1], outline='red', tags=('marked'), width=5)


def do_markers(status: bool):
    calendar = g.rt.get_child("calendar1")
    calendarMonthDayYear = calendar.get_date().split("/")
    daysInMonth = monthrange(int(calendarMonthDayYear[2]), int(calendarMonthDayYear[0]))[1]
    for intday in range(1, daysInMonth + 1):
        date = datetime.date(int(calendar._date.year), int(calendarMonthDayYear[0]), int(intday))
        calendar.selection_set(date)


def calendar1_sel_changed(e: tk.Event):
    combo1 = g.rt.get_child("combo1")
    if combo1.current() != -1:
        g.rt.get_child()
        mark_calendar_days(g.tool.configuration.users[t.get_user_no(combo1.get())].id)


def mark_calendar_days(id: str) -> str:
    """
    Highlight days in calendar for user with id 'id' with events in Dates.txt.

    Updates label "last date of data"
    """
    path = os.path.join(g.tool.myDocFolder, "configurations", g.tool.configuration.name, "subjects", id, "parameter",
                        "Dates.txt")
    arr = t.get_arr_from_file(path)
    calendar1 = g.rt.get_child("calendar1")
    # calendar1 = tkcalendar.Calendar(None)
    # for row in calendar1._calendar:
    #     for day in row:
    #         day['background'] = ''

    if not t.is_array_empty(arr):
        if arr[-1] == "":
            arr.pop()
        for i in range(len(arr)):
            if arr[i] != "":
                dateInDatesTXT = t.get_date_from_str(arr[i])

                calendar1.calevent_create(dateInDatesTXT, "", [""])
        g.rt.vars["label54"].set(f"Last date of data: {t.get_date_from_str(arr[-1])}")
        do_markers(False)
        return arr[-1]
    return ""


def calendar1_button_click(e: tk.Event):
    """
    Event callback for changing month in calendar. Calls command4_click event.
    """
    command4_click()


def combo1_click():
    if not g.tool.loadingConf:
        combo1 = g.rt.get_child("combo1")
        list11 = g.rt.get_child("list11")
        if len(combo1['values']) > 0:
            list11.delete(0, tk.END)
            combo1Text = combo1.get()
            selectedUserIndex = t.get_user_no(combo1Text)
            if not t.is_array_empty(g.tool.configuration.users[selectedUserIndex].falls):
                for fall in g.tool.configuration.users[selectedUserIndex].falls:
                    list11.insert(tk.END, fall)
            g.rt.vars["check4"] = g.tool.configuration.users[selectedUserIndex].filter
            g.rt.vars["text1"].set(g.tool.configuration.users[selectedUserIndex].stepDiffFilter)
            g.rt.vars["text2"].set(g.tool.configuration.users[selectedUserIndex].removeNoOfStrides)
            g.rt.vars["text3"].set(g.tool.configuration.users[selectedUserIndex].stepRecognitionRude)
            g.rt.vars["text7"].set(g.tool.configuration.cleanGaitMinTime)
            g.rt.vars["text8"].set(g.tool.configuration.users[selectedUserIndex].cuttings)
            g.rt.vars["text9"].set(g.tool.configuration.users[selectedUserIndex].heightFilter)
            g.rt.vars["text10"].set(g.tool.configuration.users[selectedUserIndex].removeHighestLowest)

            do_markers(False)

            if g.tool.configuration.users[selectedUserIndex].lastProcessedDate != "":
                date = mark_calendar_days(g.tool.configuration.users[selectedUserIndex].id)
                if date != "":
                    g.rtv.date = datetime.date(int(date[-4:]), int(date[:2]), int(date[3:3 + 2]))
                else:
                    g.rtv.date = m.default_datetime()
                g.rt.get_child("calendar1").selection_set(date)
            else:
                g.rtv.date = m.default_datetime()
            g.rtv.start = 0
            command4_click()


# TODO
def combo2_selection_change():
    """
    
    """
    if not g.tool.loadingConf:
        combo2 = g.rt.get_child("combo2")
        if combo2.current() != -1:
            if not g.rtv.dontRefillList:
                fill_subject_list()
            else:
                pass
            g.rtv.dontRefillList = False


def combo3_click():
    """
    
    """
    if not g.tool.loadingConf:
        pass


def option1_click():
    if not g.tool.loadingConf:
        auto_open_default(0)
    for widgetName in ["text4", "mainlist", "label22", "label16", "combo3", "combo4", "combo5", "check1", "text5",
                       "label17", "label39", "text20"]:
        g.rt.get_child(widgetName).grid_remove()
    g.tool.configuration.inputType = g.rt.vars["option1"].get()
    g.rt.get_child("command28")['text'] = "Select subject(s)"
    g.rt.get_child("label6")['text'] = "Select subject(s)"


def option2_click():
    if not g.tool.loadingConf:
        auto_open_default(1)
    for widgetName in ["text4", "mainlist", "label22", "label16", "combo3", "combo4", "combo5", "check1", "text5",
                       "label17", "label39", "text20"]:
        g.rt.get_child(widgetName).grid()
    g.tool.configuration.inputType = g.rt.vars["option2"].get()
    g.rt.get_child("command28")['text'] = "Select file(s)"
    g.rt.get_child("label6")['text'] = "Select file(s)"


def fill_WIISEL_patients_to_list():
    """"""
    if len(g.tool.patients) > 0:
        selSubjList1 = g.rt.get_child("list1", g.rt.selectSubjects)
        for patient in g.tool.patients:
            valToInsert = f'{patient.firstname} {patient.lastname} {patient.userID}'
            selSubjList1.insert(tk.END, valToInsert)
            for user in g.tool.configuration.users:
                if user.id == patient.userID:
                    selSubjList1.selection_set(tk.END)
                    break
        g.rt.selectSubjects.deiconify()

        # TODO

    else:
        messagebox.showerror(message="No subjects are assigned to you")


def user_exists(username: str) -> int:
    """
    Return index of user. -1 if doesn't exist
    """
    for i in range(len(g.tool.configuration.users)):
        if g.tool.configuration.users[i].name == username:
            return i

    return -1


def autofill_wiisel_patients_to_list() -> bool:
    """unused, not implemented"""
    return False


def command28_click():
    if g.tool.configuration.inputType == 0:
        fill_WIISEL_patients_to_list()
        return

    # TODO
    # if g.rtv.autoAdd:


def command34_click():
    list3 = g.rt.get_child("list3")
    if len(list3.get(0, tk.END)) > 0:
        selectedUser = list3.curselection()[0]
        newName = False

        form_load_userinfo()

        g.rt.userInfoVars["text10"].set(g.tool.configuration.users[selectedUser].id)
        if g.tool.configuration.users[selectedUser].age > 0:
            g.rt.userInfoVars["text2"].set(str(g.tool.configuration.users[selectedUser].age))
        g.rt.userInfoVars["text3"].set(g.tool.configuration.users[selectedUser].note)
        g.rt.userInfoVars["text1"].set(g.tool.configuration.users[selectedUser].firstname)
        g.rt.userInfoVars["text4"].set(g.tool.configuration.users[selectedUser].lastname)
        g.rt.userInfoVars["text5"].set(g.tool.configuration.users[selectedUser].phone)
        g.rt.userInfoVars["text6"].set(g.tool.configuration.users[selectedUser].email)
        g.rt.userInfoVars["text8"].set(g.tool.configuration.users[selectedUser].address)
        g.rt.userInfoVars["text7"].set(g.tool.configuration.users[selectedUser].insole)
        g.rt.userInfoVars["check2"].set(g.tool.configuration.users[selectedUser].ampelOnPhone)
        g.rt.userInfoVars["text9"].set(g.tool.configuration.users[selectedUser].pressureCaliPath)
        g.rt.userInfoVars["check3"].set(g.tool.configuration.users[selectedUser].uploadStats)
        if g.rt.userInfoVars["check3"].get() == False:
            g.rt.get_child("check2", root=g.rt.userInfo)['state'] = tk.DISABLED

        list1 = g.rt.get_child("list1", root=g.rt.userInfo)
        for i in range(len(g.tool.configuration.users[selectedUser].showStats)):
            list1Items = list1.get(0, tk.END)
            for j in range(len(list1Items)):
                if list1Items[j] == g.tool.configuration.users[selectedUser].showStats[i]:
                    list1.selection_set(j)
                    break

        list2 = g.rt.get_child("list2", root=g.rt.userInfo)
        for i in range(len(g.tool.configuration.users[selectedUser].showParameter)):
            list2Items = list2.get(0, tk.END)
            for j in range(len(list2Items)):
                if list2Items[j] == g.tool.configuration.users[selectedUser].showParameter[i]:
                    list2.selection_set(j)
                    break

        list3 = g.rt.get_child("list3", root=g.rt.userInfo)
        for i in range(len(g.tool.configuration.users[selectedUser].showFRI)):
            list3Items = list3.get(0, tk.END)
            for j in range(len(list3Items)):
                if list3Items[j] == g.tool.configuration.users[selectedUser].showFRI[i]:
                    list3.selection_set(j)
                    break

        g.rt.userInfo.wm_deiconify()


def command7_click():
    form_load_patternextraction()
    g.rt.patternExtraction.deiconify()


def list3_click():
    string = ""
    list3 = g.rt.get_child("list3")
    if not g.tool.loadingConf:
        if g.tool.configuration.users[list3.current()].name != "":
            if g.tool.configuration.inputType == 1:
                path = os.path.join(g.tool.configuration.users[list3.current()].filePath,
                                    g.tool.configuration.users[list3.current()].name)
                string = t.get_limited_str_from_file(path, 2000)
            g.rt.vars["text4"].set(string)
            listIndex = [*list3.get(0, tk.END)].index(list3.get(tk.ACTIVE))
            if g.tool.configuration.users[listIndex].active != listIndex in list3.curselection():
                g.tool.configuration.users[listIndex].active = listIndex in list3.curselection()
                g.tool.configuration.changed = True

                add_remove_subject_from_lists(g.tool.configuration.users[listIndex].name,
                                              g.tool.configuration.users[listIndex].active)
            update_list()


def list14_click(e: tk.Event):
    oldSelToWatch = g.tool.configuration.sensorToWatch

    list14 = e.widget
    g.tool.configuration.sensorToWatch = "|".join([list14.get(index) for index in list14.curselection()])
    if oldSelToWatch != g.tool.configuration.selectToWatch:
        g.tool.configuration.changed = True


def move_selected_to_listbox(origListboxName: str, destListboxName: str):
    """
    Generic function to move the selected item in listbox with name 'origListboxName' to listbox with name 'destListboxName'
    """
    origListbox = g.rt.get_child(origListboxName)
    destListbox = g.rt.get_child(destListboxName)

    selectedItemsIndex = origListbox.curselection()
    if len(selectedItemsIndex) > 0:
        itemIndex = selectedItemsIndex[0]
        destListbox.insert(tk.END, origListbox.get(itemIndex))
        origListbox.delete(itemIndex)


def add_remove_subject_from_lists(name: str, active: bool):
    """
    If active == True, add to lists. Otherwise, remove name from lists
    """
    marker = -1

    combo1 = g.rt.get_child("combo1")
    combo2 = g.rt.get_child("combo2")

    combo1["values"] = ()
    combo2["values"] = ()
    for i in range(len(g.tool.configuration.users)):
        if g.tool.configuration.users[i].active:
            combo1['values'] = [*combo1["values"]] + [g.tool.configuration.users[i].name]
            combo2['values'] = [*combo2["values"]] + [g.tool.configuration.users[i].name]
            if g.tool.configuration.users[i].name == g.tool.configuration.selectedUser:
                marker = i
    if marker > -1:
        combo1.current(marker)

    if len(combo2["values"]) > 0:
        combo2.current(0)

    if active:
        for listbox in ["list13", "list5", "list8"]:
            g.rt.get_child(listbox).insert(tk.END, name)
    else:
        for listbox in ["list13", "list5", "list6", "list8", "list17", "list4", "list16", "list19", "list20"]:
            t.remove_item_from_list(g.rt.get_child(listbox), name)
        t.remove_item_from_combo(combo1, "name")
        t.remove_item_from_combo(combo2, "name")


def process_data():
    partDate = ""
    partly = 0
    isOpen = False
    date = ""
    arr = []
    values = []  # list[str]

    press = False
    acc = False

    update = False

    if len(g.tool.configuration.users) > 0:
        if len(g.tool.configuration.gaitParameterDef) > 0:
            if len(g.tool.configuration.columns) > 0:
                # mousePointer = 11 #hourglass
                # TODO: indefinite progress bar
                for i in range(len(g.tool.configuration.users)):
                    # VistaProgress1.Value = I / (UBound(Configuration.Users) + 1) * 100
                    if g.tool.configuration.users[i].active:
                        # VistaProgress2.Caption = Configuration.Users(I).Name
                        t.make_user_paths(g.tool.configuration.users[i].id)

                        # If Not GetInputState = 0 Then DoEventsç
                        date = g.tool.configuration.users[i].lastProcessedDate
                        oldDate = date

                        noOfStrides = 0
                        actTime = 0
                        distanceWalked = 0
                        g.rtv.processedRows = 0
                        if len(g.tool.configuration.users[i].gaitParameter) > 0:
                            g.rtv.buffer = [m.Buff] * len(g.tool.configuration.users[i].gaitParameter)
                        while True:
                            erase_gait()
                            if g.tool.configuration.inputType == 0:
                                # Get day by day data from WIISEL
                                date, isOpen, partly, partDate = t.get_day_data_from_wiisel(arr,
                                                                                            g.tool.configuration.users[
                                                                                                i].filePath, date,
                                                                                            isOpen, partly, partDate)
                                if partly == 0 or partly == 1:
                                    noOfStrides = 0
                                    actTime = 0
                                    distanceWalked = 0
                                    g.rtv.processedRows = 0
                                    for j in range(len(g.tool.configuration.users[i].gaitParameter)):
                                        g.tool.configuration.users[i].gaitParameter[j].date = ""
                                if len(arr) == 0:
                                    break
                                if len(date) == 0:
                                    break
                            else:
                                partly = 0 if partly == -1 else partly
                                path = os.path.join(g.tool.configuration.users[i].filePath,
                                                    g.tool.configuration.users[i].name)
                                arr, date, isOpen, partly, partDate = t.get_day_data_from_file(path, date, isOpen,
                                                                                               partly, partDate)
                                if partly == 0 or partly == 1:
                                    noOfStrides = 0
                                    actTime = 0
                                    distanceWalked = 0
                                    g.rtv.processedRows = 0
                                    for j in range(len(g.tool.configuration.users[i].gaitParameter)):
                                        g.tool.configuration.users[i].gaitParameter[j].date = ""
                                if len(arr) == 0:
                                    break
                            # If l_Percent > 100 Then l_Percent = 100
                            # VistaProgress2.Value = l_Percent
                            # If Not GetInputState = 0 Then DoEvents
                            add_date_to_subject(g.tool.configuration.users[i].name, date)

                            print(f"Preprocess data for {g.tool.configuration.users[i].id}: {date}")

                            press, acc = make_data_values(arr, press, acc, date, i, g.tool.configuration.users[i].id)
                            add_calibration_data(i)

                            print(f"Extract steps for {g.tool.configuration.users[i].id}: {date}")

                            calculate_steps4(i)

                            print(f"Calculate gait parameter for {g.tool.configuration.users[i].id}: {date}")

                            gait = m.Gait()
                            # Gait.SetRef Me
                            # ScriptControl1.Reset
                            # ScriptControl1.AddObject "Gait", Gait, False
                            # ScriptControl1.Timeout = -1
                            values = []
                            if len(g.tool.rawGait.strides) > 0:
                                set_data_to_public(gait)

                                if len(g.tool.configuration.users[i].gaitParameter) > 0:
                                    if len(g.tool.rawGait.gRightAccAP) > 10:
                                        calculate_gait_parameter(gait, i, partly)
                                # Save data
                                # 1.Rude data
                                values = gait.get_intraday_raw_data()

                            if partly == -1:
                                if len(g.tool.configuration.users[i].gaitParameter) > 0:  # LVL 1
                                    for j in range(len(g.tool.configuration.users[i].gaitParameter)):
                                        if len(g.rtv.buffer[j].values) > 0:
                                            # delete high low
                                            if g.tool.configuration.users[i].filter:
                                                if g.tool.configuration.users[i].removeHighestLowest > 0:
                                                    remove_highest_lowest_from_arr(g.rtv.buffer[j].values,
                                                                                   g.tool.configuration.removeHighestLowest)
                                            gait.calc_daily_parameter_special(j, g.rtv.buffer[j].values)
                                            g.tool.configuration.users[i].gaitParameter[j].date = g.tool.rawGait.gDate[
                                                0]
                                            g.tool.configuration.users[i].gaitParameter[j].mean = gait.get_mean(j)
                                            g.tool.configuration.users[i].gaitParameter[
                                                j].variation = gait.get_variation(j)

                            if len(g.tool.rawGait.strides) > 0:
                                if partly == 0:
                                    path = os.path.join(g.tool.myDocFolder, "configurations", g.tool.configuration.name,
                                                        "subjects", g.tool.configuration.users[i].id, "parameter",
                                                        "intraday", f'{date.replace("/", "")}_RawGait.txt')
                                    t.save_arr_to_file(path, values)
                                elif partly != 0:
                                    path = os.path.join(g.tool.myDocFolder, "configurations", g.tool.configuration.name,
                                                        "subjects", g.tool.configuration.users[i].id, "parameter",
                                                        "intraday", f'{partDate.replace("/", "")}_RawGait.txt')
                                    if partly == 1:
                                        t.delete_file(path)
                                        t.append_arr_to_file(path, values)
                                    else:
                                        t.append_arr_to_file(path, values)

                            if len(g.tool.rawGait.strides) > 0:
                                for j in range(len(g.tool.configuration.users[i].gaitParameter)):
                                    if len(g.tool.configuration.users[i].gaitParameter[j].date) > 0:
                                        values = gait.get_intraday_parameter(j)
                                        if partly == 0:
                                            path = os.path.join(g.tool.myDocFolder, "configurations",
                                                                g.tool.configuration.name, "subjects",
                                                                g.tool.configuration.users[i].id, "parameter",
                                                                "intraday",
                                                                f'{date.replace("/", "")}_{g.tool.configuration.users[i].gaitParameter[j].name}.txt')
                                            t.save_arr_to_file(path, values)
                                        elif partly != 0:
                                            path = os.path.join(g.tool.myDocFolder, "configurations",
                                                                g.tool.configuration.name, "subjects",
                                                                g.tool.configuration.users[i].id, "parameter",
                                                                "intraday",
                                                                f'{partDate.replace("/", "")}_{g.tool.configuration.users[i].gaitParameter[j].name}.txt')
                                            if partly == 1:
                                                t.delete_file(path)
                                                t.append_arr_to_file(path, values)
                                            else:
                                                t.append_arr_to_file(path, values)
                            if partly == 0:
                                path = os.path.join(g.tool.myDocFolder, "configurations", g.tool.configuration.name,
                                                    "subjects", g.tool.configuration.users[i].id, "parameter", "daily",
                                                    "NoOfSteps.txt")
                                t.append_str_to_file(path,
                                                     f"{date},{t.kzp(str(g.tool.rawGait.noOfStrides * 2).strip())}")
                                path = os.path.join(g.tool.myDocFolder, "configurations", g.tool.configuration.name,
                                                    "subjects", g.tool.configuration.users[i].id, "parameter", "daily",
                                                    "ActivityTime.txt")
                                t.append_str_to_file(path, f"{date},{t.kzp(str(g.tool.rawGait.activityTime).strip())}")
                                path = os.path.join(g.tool.myDocFolder, "configurations", g.tool.configuration.name,
                                                    "subjects", g.tool.configuration.users[i].id, "parameter", "daily",
                                                    "DistanceWalked.txt")
                                t.append_str_to_file(path,
                                                     f"{date},{t.kzp(str(g.tool.rawGait.distanceWalked).strip())}")
                            elif partly == -1:
                                noOfStrides += g.tool.rawGait.noOfStrides
                                actTime += g.tool.rawGait.activityTime
                                distanceWalked += g.tool.rawGait.distanceWalked
                                path = os.path.join(g.tool.myDocFolder, "configurations", g.tool.configuration.name,
                                                    "subjects", g.tool.configuration.users[i].id, "parameter", "daily",
                                                    "NoOfSteps.txt")
                                t.append_str_to_file(path,
                                                     f"{date},{t.kzp(str(g.tool.rawGait.noOfStrides * 2).strip())}")
                                path = os.path.join(g.tool.myDocFolder, "configurations", g.tool.configuration.name,
                                                    "subjects", g.tool.configuration.users[i].id, "parameter", "daily",
                                                    "ActivityTime.txt")
                                t.append_str_to_file(path, f"{date},{t.kzp(str(g.tool.rawGait.activityTime).strip())}")
                                path = os.path.join(g.tool.myDocFolder, "configurations", g.tool.configuration.name,
                                                    "subjects", g.tool.configuration.users[i].id, "parameter", "daily",
                                                    "DistanceWalked.txt")
                                t.append_str_to_file(path,
                                                     f"{date},{t.kzp(str(g.tool.rawGait.distanceWalked).strip())}")
                            else:
                                noOfStrides += g.tool.rawGait.noOfStrides
                                actTime += g.tool.rawGait.activityTime
                                distanceWalked += g.tool.rawGait.distanceWalked
                            g.tool.configuration.users[i].lastProcessedDate = date

                            if g.tool.configuration.users[i].lastProcessedDate != oldDate or partly != 0:
                                for j in range(g.tool.configuration.users[i].gaitParameter):
                                    if len(g.tool.configuration.users[i].gaitParameter[j].date) > 0:
                                        if partly == 0 or partly == -1:
                                            path = os.path.join(g.tool.myDocFolder, "configurations",
                                                                g.tool.configuration.name, "subjects",
                                                                g.tool.configuration.users[i].id, "parameter", "daily",
                                                                f'{g.tool.configuration.users[i].gaitParameter[j].name}.txt')
                                            t.append_str_to_file(path,
                                                                 f"{g.tool.configuration.users[i].gaitParameter[j].date},{t.kzp(str(round(g.tool.configuration.users[i].gaitParameter[j].mean, ndigits=4))).strip()},{t.kzp(str(round(g.tool.configuration.users[i].gaitParameter[j].variation, ndigits=4))).strip()}")

                            g.rtv.processedRows += len(g.tool.rawGait.gDate)

                            # gait = m.Gait()

                            if not (isOpen or (g.tool.configuration.inputType == 0 and len(date) > 0)):
                                break

                        # end while

                        # daily
                        if g.tool.configuration.users[i].lastProcessedDate != oldDate:
                            update = True
                            path = os.path.join(g.tool.myDocFolder, "configurations", g.tool.configuration.name,
                                                "subjects", g.tool.configuration.users[i].id, "parameter",
                                                "LastDate.txt")
                            t.save_str_to_file(path, g.tool.configuration.users[i].lastProcessedDate)
                        g.tool.configuration.users[i].filterChange = False

                print("Status: Calculate Fall Risk Index")
                t.calc_all_FRI()
                if g.tool.configuration.inputType == 0:
                    if update:
                        if not g.tool.isUserMonitor:
                            # TODO
                            # upload_user_statistics()
                            pass
                g.tool.configuration.coreChange = False
                # clear_chart()
                # combo2_click()

                # progressBar

                print("Finished")
    # mousePointer back to regular


def calculate_steps4(userNo: int):
    """
    
    """
    i = 0
    i2 = 0
    i3 = 0
    lAvg = 0.0
    rAvg = 0.0
    x = 0
    x2 = 0
    state = 0
    meanR = 0.0
    cnt = 0
    start = 0
    end = 0
    duration = 0.0
    stepDiffFilter = 0.0
    ap = 0.0
    ml = 0.0
    vert = 0.0
    marker = False
    rEnd = 0
    lStart = 0
    lEnd = 0
    currRudeLap = 0
    currRudeRap = 0
    currRudeL = 0
    currRudeR = 0
    lastRudeLap = 0
    lastRudeRap = 0
    lastRudeL = 0
    lastRudeR = 0
    initNew = False
    rStage = 0
    lStage = 0

    if len(g.tool.rawGait.gRightAccAP) > 10:
        x = 0
        # warning warning warning warning... was this a safety measure in original application?
        g.tool.rawGait.strides = [m.RawStepdata()]
        i = 0
        g.tool.rawGait.activityTime = 0
        while True:
            lastRudeRap = currRudeRap
            lastRudeLap = currRudeLap
            lastRudeR = currRudeR
            lastRudeL = currRudeL

            currRudeRap = t.make_rude_acc2(int(lastRudeRap), g.tool.rawGait.gRightAccAP[i],
                                           g.tool.rawGait.gRightAccAP[i + 1], g.tool.rawGait.gRightAccAP[i + 2],
                                           g.tool.rawGait.gRightAccAP[i + 3],
                                           g.tool.rawGait.gRightAccAP[i + 4], g.tool.rawGait.gRightAccAP[i + 5],
                                           g.tool.rawGait.gRightAccAP[i + 6], g.tool.rawGait.gRightAccAP[i + 7],
                                           g.tool.rawGait.gRightAccAP[i + 8],
                                           g.tool.rawGait.gRightAccAP[i + 9],
                                           t.get_max(g.tool.rawGait.gRightAccAP, 200, i))
            currRudeLap = t.make_rude_acc2(int(lastRudeLap), g.tool.rawGait.gLeftAccAP[i],
                                           g.tool.rawGait.gLeftAccAP[i + 1], g.tool.rawGait.gLeftAccAP[i + 2],
                                           g.tool.rawGait.gLeftAccAP[i + 3],
                                           g.tool.rawGait.gLeftAccAP[i + 4], g.tool.rawGait.gLeftAccAP[i + 5],
                                           g.tool.rawGait.gLeftAccAP[i + 6], g.tool.rawGait.gLeftAccAP[i + 7],
                                           g.tool.rawGait.gLeftAccAP[i + 8],
                                           g.tool.rawGait.gLeftAccAP[i + 9],
                                           t.get_max(g.tool.rawGait.gLeftAccAP, 200, i))

            currRudeR = t.make_rude3_acc(lastRudeR, g.tool.rawGait.gRightAcc[i], g.tool.rawGait.gRightAcc[i + 1],
                                         g.tool.rawGait.gRightAcc[i + 1], g.tool.configuration.stepRecognitionRude)
            currRudeL = t.make_rude3_acc(lastRudeR, g.tool.rawGait.gLeftAcc[i], g.tool.rawGait.gLeftAcc[i + 1],
                                         g.tool.rawGait.gLeftAcc[i + 1], g.tool.configuration.stepRecognitionRude)

            if i > 0:
                # Start right
                if lastRudeRap > 0:
                    if currRudeRap == 0:
                        # Process previous
                        if rStage == 3:
                            if g.tool.rawGait.gRtime[i] - g.tool.rawGait.strides[x].rightStart > 0.5:
                                if g.tool.rawGait.gRtime[i] - g.tool.rawGait.strides[
                                    x].rightStart < 5:  # Strides >0.5 and  < 5 sec ?
                                    g.tool.rawGait.activityTime = round(g.tool.rawGait.activityTime + (
                                            g.tool.rawGait.gRtime[i] - g.tool.rawGait.strides[x].rightHeel),
                                                                        ndigits=2)
                                    g.tool.rawGait.strides[x].no = x
                                    x += 1
                                    # warning: append instead?
                                    redim_preserve(g.tool.rawGait.strides, x)
                                    # warning: most safe is for stride, if None, then that element = m.RawStepdata()
                                    g.tool.rawGait.strides[-1] = m.RawStepdata()
                        # Init new step right heel strike
                        g.tool.rawGait.strides[x].rightHeel = g.tool.rawGait.gRtime[i]
                        g.tool.rawGait.strides[x].rightHeelRow = i
                        rStage = 0
                # Right step end
                if rStage == 0:
                    if lastRudeR > 0:
                        if currRudeR == 0:
                            g.tool.rawGait.strides[x].rightStart = g.tool.rawGait.gRtime[i]
                            g.tool.rawGait.strides[x].rightStartRow = i
                            rStage = 1
                # right step start
                if rStage == 1:
                    if lastRudeR == 0:
                        if currRudeR > 0:
                            g.tool.rawGait.strides[x].rightEnd = g.tool.rawGait.gRtime[i]
                            g.tool.rawGait.strides[x].rightEndRow = i
                            rStage = 2
                # right Toe off
                if rStage == 2:
                    if lastRudeRap == 0:
                        if currRudeRap > 0:
                            g.tool.rawGait.strides[x].rightToe = g.tool.rawGait.gRtime[i]
                            g.tool.rawGait.strides[x].rightToeRow = i
                            rStage = 3

                if g.tool.rawGait.strides[x2].rightHeel != 0:
                    # Start links
                    if lastRudeLap > 0:
                        if currRudeLap == 0:
                            x2 = x
                            # Init new step left heel strike
                            g.tool.rawGait.strides[x2].leftHeel = g.tool.rawGait.gRtime[i]
                            g.tool.rawGait.strides[x2].leftHeelRow = i
                            lStage = 0
                    # left step end
                    if lStage == 0:
                        if lastRudeL > 0:
                            if currRudeL == 0:
                                g.tool.rawGait.strides[x2].leftStart = g.tool.rawGait.gRtime[i]
                                g.tool.rawGait.strides[x2].leftStartRow = i
                                lStage = 1
                    # left step start
                    if lStage == 1:
                        if lastRudeL == 0:
                            if currRudeL > 0:
                                g.tool.rawGait.strides[x2].leftEnd = g.tool.rawGait.gRtime[i]
                                g.tool.rawGait.strides[x2].leftEndRow = i
                                lStage = 2
                    # left toe off
                    if lStage == 2:
                        if lastRudeLap == 0:
                            if currRudeLap > 0:
                                g.tool.rawGait.strides[x2].leftToe = g.tool.rawGait.gRtime[i]
                                g.tool.rawGait.strides[x2].leftToeRow = i
                                lStage = 3
            i += 1
            # warning: -9... is strange, -8 or -10 perhaps?
            if i > len(g.tool.rawGait.gDate) - 9:
                break
        # while ends here
        g.tool.rawGait.noOfStrides = x
        g.tool.rawGait.distanceWalked = 0
        if x > 0:
            # extend values
            # warning: rango del for
            for i in range(1, len(g.tool.rawGait.strides)):
                g.tool.rawGait.strides[i - 1].rightStartNext = g.tool.rawGait.strides[i].rightStart
                g.tool.rawGait.strides[i - 1].rightStartNextRow = g.tool.rawGait.strides[i].rightStartRow
                g.tool.rawGait.strides[i - 1].leftStartNext = g.tool.rawGait.strides[i].leftStartNext
                g.tool.rawGait.strides[i - 1].leftStartNextRow = g.tool.rawGait.strides[i].rightStart
                g.tool.rawGait.strides[i - 1].leftEndNext = g.tool.rawGait.strides[i].rightStart
                g.tool.rawGait.strides[i - 1].leftEndNextRow = g.tool.rawGait.strides[i].rightStart
                g.tool.rawGait.strides[i - 1].rightHeelNext = g.tool.rawGait.strides[i].rightStart
                g.tool.rawGait.strides[i - 1].rightHeelNextRow = g.tool.rawGait.strides[i].rightStart
                g.tool.rawGait.strides[i - 1].leftHeelNext = g.tool.rawGait.strides[i].rightStart
                g.tool.rawGait.strides[i - 1].leftHeelNextRow = g.tool.rawGait.strides[i].rightStart
                g.tool.rawGait.strides[i - 1].leftToeNext = g.tool.rawGait.strides[i].rightStart
                g.tool.rawGait.strides[i - 1].leftToeNextRow = g.tool.rawGait.strides[i].rightStart

                g.tool.rawGait.strides[i].leftStartLast = g.tool.rawGait.strides[i - 1].rightStart
                g.tool.rawGait.strides[i].leftStartLastRow = g.tool.rawGait.strides[i - 1].rightStart
                g.tool.rawGait.strides[i].leftEndLast = g.tool.rawGait.strides[i - 1].rightStart
                g.tool.rawGait.strides[i].leftEndLastRow = g.tool.rawGait.strides[i - 1].rightStart
                g.tool.rawGait.strides[i].rightStartLast = g.tool.rawGait.strides[i - 1].rightStart
                g.tool.rawGait.strides[i].rightStartLastRow = g.tool.rawGait.strides[i - 1].rightStart
                g.tool.rawGait.strides[i].rightStartNext = g.tool.rawGait.strides[i - 1].rightStart
            if not t.remove_too_long_strides():
                print(f"calculate_steps4 - not remove_too_long_strides")
                return

            # calculate step lengths
            for i in range(g.tool.rawGait.strides):
                if g.tool.rawGait.strides[i].leftEndRow < g.tool.rawGait.strides[i].leftStartNextRow:
                    g.tool.rawGait.strides[i].leftStrideLength = t.calc_distance2(0,
                                                                                  g.tool.rawGait.strides[i].leftEndRow,
                                                                                  g.tool.rawGait.strides[
                                                                                      i].leftStartNextRow)  # Stridetime
                    g.tool.rawGait.strides[i].rightLength /= 2
                if g.tool.rawGait.strides[i].rightEndRow < g.tool.rawGait.strides[i].rightStartNextRow:
                    g.tool.rawGait.strides[i].rightStrideLength = t.calc_distance2(1, g.tool.rawGait.strides[
                        i].rightEndRow, g.tool.rawGait.strides[i].rightStartNextRow)  # stridetime
                    g.tool.rawGait.strides[i].rightLength /= 2

                if g.tool.rawGait.strides[i].leftStrideLength < 2 and g.tool.rawGait.strides[i].rightStrideLength < 2:
                    g.tool.rawGait.distanceWalked += g.tool.rawGait.strides[
                        i].leftStrideLength  # + g.tool.rawgait.strides[i].rightLength

            if not t.remove_too_big_strides():
                print(f"calculate_steps4 - not remove_too_big_strides")
                return

            # Filter steps of length 0
            if not t.filter_zero_steps(userNo):
                print(f"calculate_steps4 - not filter_zero_steps")
                return

            # Filter irregular Steps
            if g.tool.configuration.users[userNo].filter:
                if not t.delete_unequal_steps(userNo):
                    print(f"calculate_steps4 - not delete_unequal_steps")
                    return

                if not t.delete_too_short_walkperiods(g.tool.configuration.cleanGaitMinTime,
                                                      g.tool.configuration.users[userNo].cuttings):
                    print(f"calculate_steps4 - not delete_too_short_walkperiods")
                    return

            if not t.remove_highest_lowest(g.tool.configuration.users[userNo].removeHighestLowest):
                print(
                    f"calculate_steps4 - not remove_highest_lowest({g.tool.configuration.users[userNo].removeHighestLowest})")
                return

            if g.tool.configuration.users[userNo].filter:
                # Remove first and last of each period (because of extend values)
                g.tool.rawGait.strides[0].remove = True
                for i in range(1, len(g.tool.rawGait.strides)):
                    if g.tool.rawGait.strides[i].no != g.tool.rawGait.strides[i + 1].no + 1:
                        g.tool.rawGait.strides[i].remove = True
                        g.tool.rawGait.strides[i - 1].remove = True
                g.tool.rawGait.strides[-1].remove = True
                t.remove_marked_strides()
        else:
            g.tool.rawGait.strides = []


def calculate_steps2():
    """
    
    """
    i = 0
    # i2 = 0
    # i3 = 0
    # lAvg = 0.0
    # rAvg = 0.0
    x = 0
    x2 = 0
    # state = 0
    # meanR = 0.0
    # cnt = 0
    # start = 0
    # end = 0
    # duration = 0.0
    # stepDiffFilter = 0.0
    # ap = 0.0
    # ml = 0.0
    # vert = 0.0
    # marker = False
    # rEnd = 0
    # lStart = 0
    # lEnd = 0
    currRudeLap = 0
    currRudeRap = 0
    currRudeL = 0
    currRudeR = 0
    lastRudeLap = 0
    lastRudeRap = 0
    lastRudeL = 0
    lastRudeR = 0
    # initNew = False
    rStage = 0
    lStage = 0

    if len(g.tool.rawGait.gRightAccAP) > 10:
        x = 0
        # warning warning warning warning...
        g.tool.rawGait.strides = [m.RawStepdata()]
        i = 0
        g.tool.rawGait.activityTime = 0
        while True:
            lastRudeRap = currRudeRap
            lastRudeLap = currRudeLap
            lastRudeR = currRudeR
            lastRudeL = currRudeL

            currRudeRap = t.make_rude_acc2(int(lastRudeRap), g.tool.rawGait.gRightAccAP[i],
                                           g.tool.rawGait.gRightAccAP[i + 1], g.tool.rawGait.gRightAccAP[i + 2],
                                           g.tool.rawGait.gRightAccAP[i + 3],
                                           g.tool.rawGait.gRightAccAP[i + 4], g.tool.rawGait.gRightAccAP[i + 5],
                                           g.tool.rawGait.gRightAccAP[i + 6], g.tool.rawGait.gRightAccAP[i + 7],
                                           g.tool.rawGait.gRightAccAP[i + 8],
                                           g.tool.rawGait.gRightAccAP[i + 9],
                                           t.get_max(g.tool.rawGait.gRightAccAP, 200, i))
            currRudeLap = t.make_rude_acc2(int(lastRudeLap), g.tool.rawGait.gLeftAccAP[i],
                                           g.tool.rawGait.gLeftAccAP[i + 1], g.tool.rawGait.gLeftAccAP[i + 2],
                                           g.tool.rawGait.gLeftAccAP[i + 3],
                                           g.tool.rawGait.gLeftAccAP[i + 4], g.tool.rawGait.gLeftAccAP[i + 5],
                                           g.tool.rawGait.gLeftAccAP[i + 6], g.tool.rawGait.gLeftAccAP[i + 7],
                                           g.tool.rawGait.gLeftAccAP[i + 8],
                                           g.tool.rawGait.gLeftAccAP[i + 9],
                                           t.get_max(g.tool.rawGait.gLeftAccAP, 200, i))

            currRudeR = t.make_rude3_acc(lastRudeR, g.tool.rawGait.gRightAcc[i], g.tool.rawGait.gRightAcc[i + 1],
                                         g.tool.rawGait.gRightAcc[i + 1], g.tool.configuration.stepRecognitionRude)
            currRudeL = t.make_rude3_acc(lastRudeR, g.tool.rawGait.gLeftAcc[i], g.tool.rawGait.gLeftAcc[i + 1],
                                         g.tool.rawGait.gLeftAcc[i + 1], g.tool.configuration.stepRecognitionRude)

            if i > 0:
                # Start right
                if lastRudeRap > 0:
                    if currRudeRap == 0:
                        # Process previous
                        if rStage == 3:
                            if g.tool.rawGait.gRtime[i] - g.tool.rawGait.strides[x].rightStart > 0.5:
                                if g.tool.rawGait.gRtime[i] - g.tool.rawGait.strides[
                                    x].rightStart < 5:  # Strides >0.5 and  < 5 sec ?
                                    g.tool.rawGait.activityTime = round(g.tool.rawGait.activityTime + (
                                            g.tool.rawGait.gRtime[i] - g.tool.rawGait.strides[x].rightHeel),
                                                                        ndigits=2)
                                    g.tool.rawGait.strides[x].no = x
                                    x += 1
                                    # warning: append instead?
                                    redim_preserve(g.tool.rawGait.strides, x)
                                    # warning: most safe is for stride, if None, then that element = m.RawStepdata()
                                    g.tool.rawGait.strides[-1] = m.RawStepdata()
                        # Init new step right heel strike
                        g.tool.rawGait.strides[x].rightHeel = g.tool.rawGait.gRtime[i]
                        g.tool.rawGait.strides[x].rightHeelRow = i
                        rStage = 0
                # Right step end
                if rStage == 0:
                    if lastRudeR > 0:
                        if currRudeR == 0:
                            g.tool.rawGait.strides[x].rightStart = g.tool.rawGait.gRtime[i]
                            g.tool.rawGait.strides[x].rightStartRow = i
                            rStage = 1
                # right step start
                if rStage == 1:
                    if lastRudeR == 0:
                        if currRudeR > 0:
                            g.tool.rawGait.strides[x].rightEnd = g.tool.rawGait.gRtime[i]
                            g.tool.rawGait.strides[x].rightEndRow = i
                            rStage = 2
                # right Toe off
                if rStage == 2:
                    if lastRudeRap == 0:
                        if currRudeRap > 0:
                            g.tool.rawGait.strides[x].rightToe = g.tool.rawGait.gRtime[i]
                            g.tool.rawGait.strides[x].rightToeRow = i
                            rStage = 3

                if g.tool.rawGait.strides[x2].rightHeel != 0:
                    # Start links
                    if lastRudeLap > 0:
                        if currRudeLap == 0:
                            x2 = x
                            # Init new step left heel strike
                            g.tool.rawGait.strides[x2].leftHeel = g.tool.rawGait.gRtime[i]
                            g.tool.rawGait.strides[x2].leftHeelRow = i
                            lStage = 0
                    # left step end
                    if lStage == 0:
                        if lastRudeL > 0:
                            if currRudeL == 0:
                                g.tool.rawGait.strides[x2].leftStart = g.tool.rawGait.gRtime[i]
                                g.tool.rawGait.strides[x2].leftStartRow = i
                                lStage = 1
                    # left step start
                    if lStage == 1:
                        if lastRudeL == 0:
                            if currRudeL > 0:
                                g.tool.rawGait.strides[x2].leftEnd = g.tool.rawGait.gRtime[i]
                                g.tool.rawGait.strides[x2].leftEndRow = i
                                lStage = 2
                    # left toe off
                    if lStage == 2:
                        if lastRudeLap == 0:
                            if currRudeLap > 0:
                                g.tool.rawGait.strides[x2].leftToe = g.tool.rawGait.gRtime[i]
                                g.tool.rawGait.strides[x2].leftToeRow = i
                                lStage = 3
            i += 1
            # warning: -9... odd, -8 o -10 maybe
            if i > len(g.tool.rawGait.gDate) - 9:
                break
        # while ends here

        g.tool.rawGait.noOfStrides = x
        g.tool.rawGait.distanceWalked = 0
        if x > 0:
            # extend values
            # warning: for interval range
            for i in range(1, len(g.tool.rawGait.strides)):
                g.tool.rawGait.strides[i - 1].rightStartNext = g.tool.rawGait.strides[i].rightStart
                g.tool.rawGait.strides[i - 1].rightStartNextRow = g.tool.rawGait.strides[i].rightStartRow
                g.tool.rawGait.strides[i - 1].leftStartNext = g.tool.rawGait.strides[i].leftStartNext
                g.tool.rawGait.strides[i - 1].leftStartNextRow = g.tool.rawGait.strides[i].rightStart
                g.tool.rawGait.strides[i - 1].leftEndNext = g.tool.rawGait.strides[i].rightStart
                g.tool.rawGait.strides[i - 1].leftEndNextRow = g.tool.rawGait.strides[i].rightStart
                g.tool.rawGait.strides[i - 1].rightHeelNext = g.tool.rawGait.strides[i].rightStart
                g.tool.rawGait.strides[i - 1].rightHeelNextRow = g.tool.rawGait.strides[i].rightStart
                g.tool.rawGait.strides[i - 1].leftHeelNext = g.tool.rawGait.strides[i].rightStart
                g.tool.rawGait.strides[i - 1].leftHeelNextRow = g.tool.rawGait.strides[i].rightStart
                g.tool.rawGait.strides[i - 1].leftToeNext = g.tool.rawGait.strides[i].rightStart
                g.tool.rawGait.strides[i - 1].leftToeNextRow = g.tool.rawGait.strides[i].rightStart

                g.tool.rawGait.strides[i].leftStartLast = g.tool.rawGait.strides[i - 1].rightStart
                g.tool.rawGait.strides[i].leftStartLastRow = g.tool.rawGait.strides[i - 1].rightStart
                g.tool.rawGait.strides[i].leftEndLast = g.tool.rawGait.strides[i - 1].rightStart
                g.tool.rawGait.strides[i].leftEndLastRow = g.tool.rawGait.strides[i - 1].rightStart
                g.tool.rawGait.strides[i].rightStartLast = g.tool.rawGait.strides[i - 1].rightStart
                g.tool.rawGait.strides[i].rightStartLastRow = g.tool.rawGait.strides[i - 1].rightStart
                g.tool.rawGait.strides[i].rightStartNext = g.tool.rawGait.strides[i - 1].rightStart
            if not t.remove_too_long_strides():
                print(f"calculate_steps2 - not remove_too_long_strides")
                return

            # calculate step lengths
            for i in range(g.tool.rawGait.strides):
                if g.tool.rawGait.strides[i].leftEndRow < g.tool.rawGait.strides[i].leftStartNextRow:
                    g.tool.rawGait.strides[i].leftStrideLength = t.calc_distance2(0,
                                                                                  g.tool.rawGait.strides[i].leftEndRow,
                                                                                  g.tool.rawGait.strides[
                                                                                      i].leftStartNextRow)  # Stridetime
                    g.tool.rawGait.strides[i].rightLength /= 2
                if g.tool.rawGait.strides[i].rightEndRow < g.tool.rawGait.strides[i].rightStartNextRow:
                    g.tool.rawGait.strides[i].rightStrideLength = t.calc_distance2(1, g.tool.rawGait.strides[
                        i].rightEndRow, g.tool.rawGait.strides[i].rightStartNextRow)  # stridetime
                    g.tool.rawGait.strides[i].rightLength /= 2

                if g.tool.rawGait.strides[i].leftStrideLength < 2 and g.tool.rawGait.strides[i].rightStrideLength < 2:
                    g.tool.rawGait.distanceWalked += g.tool.rawGait.strides[
                        i].leftStrideLength  # + g.tool.rawgait.strides[i].rightLength

            if not t.remove_too_big_strides():
                print(f"calculate_steps2 - not remove_too_big_strides")
                return

            # Filter steps of length 0
            if not t.filter_zero_steps(0):
                print(f"calculate_steps2 - not filter_zero_steps")
                return

            # Filter irregular Steps
            if g.tool.configuration.filter:
                if not t.delete_unequal_steps(0):
                    print(f"calculate_steps2 - not delete_unequal_steps")
                    return

                if not t.delete_too_short_walkperiods(g.tool.configuration.cleanGaitMinTime,
                                                      g.tool.configuration.cuttings):
                    print(f"calculate_steps2 - not delete_too_short_walkperiods")
                    return

            if not t.remove_highest_lowest(g.tool.configuration.removeHighestLowest):
                print(f"calculate_steps2 - not remove_highest_lowest({g.tool.configuration.removeHighestLowest})")
                return

            if g.tool.configuration.filter:
                # Remove first and last of each period (because of extend values)
                g.tool.rawGait.strides[0].remove = True
                for i in range(1, len(g.tool.rawGait.strides)):
                    if g.tool.rawGait.strides[i].no != g.tool.rawGait.strides[i + 1].no + 1:
                        g.tool.rawGait.strides[i].remove = True
                        g.tool.rawGait.strides[i - 1].remove = True
                g.tool.rawGait.strides[-1].remove = True
                t.remove_marked_strides()
        else:
            g.tool.rawGait.strides = []


def add_calibration_data(userNo: int):
    """
    Load calibration data from file "mydoc/data/userId/Calibration.txt to global tool.rawgait
    """
    path = os.path.join(g.tool.myDocFolder, "data", g.tool.configuration.users[userNo].id, "Calibration.txt")
    arr = t.get_str_from_file(path).split(",")
    if not t.is_array_empty(arr):
        if len(arr) == 18:
            g.tool.rawGait.calibrationData.CaliBxR = float(arr[0])
            g.tool.rawGait.calibrationData.CaliByR = float(arr[1])
            g.tool.rawGait.calibrationData.CaliBzR = float(arr[2])
            g.tool.rawGait.calibrationData.CaliKxR = float(arr[3])
            g.tool.rawGait.calibrationData.CaliKyR = float(arr[4])
            g.tool.rawGait.calibrationData.CaliKzR = float(arr[5])
            g.tool.rawGait.calibrationData.CaliHxR = float(arr[6])
            g.tool.rawGait.calibrationData.CaliHyR = float(arr[7])
            g.tool.rawGait.calibrationData.CaliHzR = float(arr[8])
            g.tool.rawGait.calibrationData.CaliBxL = float(arr[9])
            g.tool.rawGait.calibrationData.CaliByL = float(arr[10])
            g.tool.rawGait.calibrationData.CaliBzL = float(arr[11])
            g.tool.rawGait.calibrationData.CaliKxL = float(arr[12])
            g.tool.rawGait.calibrationData.CaliKyL = float(arr[13])
            g.tool.rawGait.calibrationData.CaliKzL = float(arr[14])
            g.tool.rawGait.calibrationData.CaliHxL = float(arr[15])
            g.tool.rawGait.calibrationData.CaliHyL = float(arr[16])
            g.tool.rawGait.calibrationData.CaliHzL = float(arr[17])
        else:
            g.tool.rawGait.calibrationData.CaliBxR = 0
            g.tool.rawGait.calibrationData.CaliByR = 0
            g.tool.rawGait.calibrationData.CaliBzR = 0
            g.tool.rawGait.calibrationData.CaliKxR = 1
            g.tool.rawGait.calibrationData.CaliKyR = 1
            g.tool.rawGait.calibrationData.CaliKzR = 1
            g.tool.rawGait.calibrationData.CaliHxR = 0
            g.tool.rawGait.calibrationData.CaliHyR = 0
            g.tool.rawGait.calibrationData.CaliHzR = 0
            g.tool.rawGait.calibrationData.CaliBxL = 0
            g.tool.rawGait.calibrationData.CaliByL = 0
            g.tool.rawGait.calibrationData.CaliBzL = 0
            g.tool.rawGait.calibrationData.CaliKxL = 1
            g.tool.rawGait.calibrationData.CaliKyL = 1
            g.tool.rawGait.calibrationData.CaliKzL = 1
            g.tool.rawGait.calibrationData.CaliHxL = 0
            g.tool.rawGait.calibrationData.CaliHyL = 0
            g.tool.rawGait.calibrationData.CaliHzL = 0


def add_calibration_data2(user: str):
    """
    Load calibration data from file "mydoc/data/userId/Calibration.txt to global tool.rawgait
    """
    path = os.path.join(g.tool.myDocFolder, "data", user, "Calibration.txt")
    arr = t.get_str_from_file(path).split(",")
    if not t.is_array_empty(arr):
        if len(arr) == 18:
            g.tool.rawGait.calibrationData.CaliBxR = float(arr[0])
            g.tool.rawGait.calibrationData.CaliByR = float(arr[1])
            g.tool.rawGait.calibrationData.CaliBzR = float(arr[2])
            g.tool.rawGait.calibrationData.CaliKxR = float(arr[3])
            g.tool.rawGait.calibrationData.CaliKyR = float(arr[4])
            g.tool.rawGait.calibrationData.CaliKzR = float(arr[5])
            g.tool.rawGait.calibrationData.CaliHxR = float(arr[6])
            g.tool.rawGait.calibrationData.CaliHyR = float(arr[7])
            g.tool.rawGait.calibrationData.CaliHzR = float(arr[8])
            g.tool.rawGait.calibrationData.CaliBxL = float(arr[9])
            g.tool.rawGait.calibrationData.CaliByL = float(arr[10])
            g.tool.rawGait.calibrationData.CaliBzL = float(arr[11])
            g.tool.rawGait.calibrationData.CaliKxL = float(arr[12])
            g.tool.rawGait.calibrationData.CaliKyL = float(arr[13])
            g.tool.rawGait.calibrationData.CaliKzL = float(arr[14])
            g.tool.rawGait.calibrationData.CaliHxL = float(arr[15])
            g.tool.rawGait.calibrationData.CaliHyL = float(arr[16])
            g.tool.rawGait.calibrationData.CaliHzL = float(arr[17])
        else:
            g.tool.rawGait.calibrationData.CaliBxR = 0
            g.tool.rawGait.calibrationData.CaliByR = 0
            g.tool.rawGait.calibrationData.CaliBzR = 0
            g.tool.rawGait.calibrationData.CaliKxR = 1
            g.tool.rawGait.calibrationData.CaliKyR = 1
            g.tool.rawGait.calibrationData.CaliKzR = 1
            g.tool.rawGait.calibrationData.CaliHxR = 0
            g.tool.rawGait.calibrationData.CaliHyR = 0
            g.tool.rawGait.calibrationData.CaliHzR = 0
            g.tool.rawGait.calibrationData.CaliBxL = 0
            g.tool.rawGait.calibrationData.CaliByL = 0
            g.tool.rawGait.calibrationData.CaliBzL = 0
            g.tool.rawGait.calibrationData.CaliKxL = 1
            g.tool.rawGait.calibrationData.CaliKyL = 1
            g.tool.rawGait.calibrationData.CaliKzL = 1
            g.tool.rawGait.calibrationData.CaliHxL = 0
            g.tool.rawGait.calibrationData.CaliHyL = 0
            g.tool.rawGait.calibrationData.CaliHzL = 0


def add_data():
    """Unused."""


def get_column_positions():
    """Unused"""


def command21_click():
    """Add fall in Fall list (raw data filtering)"""
    combo1 = g.rt.get_child("combo1")
    if combo1.current() > -1:
        userNo = t.get_user_no(combo1.get())
        string = simpledialog.askstring(title="Serene GAT",
                                        prompt="Please enter new fall event time [MM/DD/YYYY HH:MM:SS]")
        if string != "":
            try:
                dateAndTime = string.split(" ")
                monthDayYear = dateAndTime[0].split("/")
                hourMinuteSecond = dateAndTime[1].split(":")
                # validate format, otherwise catch error
                datetime.datetime.strptime(string, "%m/%d/%Y %H:%M:%S")

                list11 = g.rt.get_child("list11")
                currentDatetimes = [date.lower() for date in list11.get(0, tk.END)]
                if string.lower() in currentDatetimes:
                    messagebox.showerror(message="This fall event already exists. Please choose a different date")
                else:
                    g.tool.configuration.users[userNo].falls.append(string)
                    t.save_falls(g.tool.configuration.users[userNo].id, g.tool.configuration.users[userNo].falls)
                    list11.insert(tk.END, string)
                    combo2_selection_change()
                    g.tool.configuration.changed = True

            except ValueError as err:
                messagebox.showerror(message="Please enter a valid date [MM/DD/YYYY HH:MM:SS]")


def command22_click():
    """Edit selected fall in Fall list (raw data filtering)"""
    combo1 = g.rt.get_child("combo1")
    if combo1.current() > -1:
        userNo = t.get_user_no(combo1.get())
        if len(g.tool.configuration.users[userNo].falls) > 0:
            list11 = g.rt.get_child("list11")
            if len(list11.curselection()) > 0:
                list11Index = list11.curselection()[0]
                inputDate = simpledialog.askstring(title="Serene GAT",
                                                   prompt="Please enter fall event time [MM/DD/YYYY HH:MM:SS]")
                if inputDate == "" or inputDate is None:
                    return

                try:
                    # if list11.get(list11Index).lower() in [fall.lower() for i, fall in enumerate(g.tool.configuration.users[userNo].falls) if i != list11Index]:
                    selectedList11Fall = list11.get(tk.ACTIVE)
                    # validate format, otherwise catch error
                    datetime.datetime.strptime(inputDate, "%m/%d/%Y %H:%M:%S")
                    marker = False
                    for i, fall in enumerate(g.tool.configuration.users[userNo].falls):
                        if i != list11Index and selectedList11Fall.lower() == fall.lower():
                            marker = True
                    if marker:
                        messagebox.showerror(message="This fall event already exists. Please choose a different date")
                    else:
                        g.tool.configuration.users[userNo].falls[list11Index] = inputDate
                        t.save_falls(g.tool.configuration.users[userNo].id, g.tool.configuration.users[userNo].falls)
                        list11.insert(tk.END, inputDate)
                        combo2_selection_change()
                        g.tool.configuration.changed = True

                except ValueError as err:
                    messagebox.showerror(message="Please enter a valid date [MM/DD/YYYY HH:MM:SS]")


def command23_click():
    """Delete the selected fall (Raw dataq filtering)"""
    combo1 = g.rt.get_child("combo1")
    if combo1.current() > -1:
        userNo = t.get_user_no(combo1.get())
        if len(g.tool.configuration.users[userNo].falls) > 0:
            list11 = g.rt.get_child("list11")
            if len(list11.curselection()) > -1:
                list11Index = list11.curselection()[0]
                list11.delete(list11Index)
                g.tool.configuration.users[userNo].falls.pop(list11Index)
                t.save_falls(g.tool.configuration.users[userNo].id, g.tool.configuration.users[userNo].falls)
                combo2_selection_change()
                g.tool.configuration.changed = True


def add_fall_event(userID: str, string: str, filename: str):
    """
    Add fall event to user, with userID in path
    """
    arr = string.split(",")
    time = arr[1]
    hour, minute, second = t.sec_to_time(int(time))
    time = f"{hour:02}:{minute:02}:{second:02}"
    date = filename.replace(".txt", "")
    date = date.replace("left_", "")
    date = date.replace("right_", "")
    date = f"{date[3:3 + 2]}/{date[0:2]}/{date[6:6 + 4]}"

    path = os.path.join(g.tool.myDocFolder, "data", userID, "Falls.txt")
    arr = t.get_arr_from_file(path)

    # [MM/DD/YYYY HH:MM:SS]
    fullDate = f"{date} {time}"
    if not fullDate in arr:
        t.add_to_array(arr, fullDate)
        t.save_falls(userID, arr)


def add_fall_event2(email: str, string: str, filename: str):
    """
    Add fall event to user, with email in path
    """
    arr = string.split(",")
    time = arr[1]
    hour, minute, second = t.sec_to_time(int(time))
    time = f"{hour:02}:{minute:02}:{second:02}"
    date = filename.replace(".txt", "")
    date = date.replace("left_", "")
    date = date.replace("right_", "")
    date = f"{date[3:3 + 2]}/{date[0:2]}/{date[6:6 + 4]}"

    path = os.path.join(g.tool.myDocFolder, "data", email, "Falls.txt")
    arr = t.get_arr_from_file(path)

    # [MM/DD/YYYY HH:MM:SS]
    fullDate = f"{date} {time}"
    if not fullDate in arr:
        t.add_to_array(arr, fullDate)
        t.save_falls(email, arr)


def add_date_to_subject(name: str, date: str):
    """
    Add date to subject's with name 'name' in "Dates.txt" if doesn't already exist.
    """
    marker = False

    path = os.path.join(g.tool.myDocFolder, "configurations", g.tool.configuration.name, "subjects",
                        t.get_id_from_name(name), "parameters", "Dates.txt")
    arr = t.get_arr_from_file(path)
    if not t.is_array_empty(arr):
        for i in range(len(arr)):
            if date == arr[i]:
                marker = True
                break
    if not marker:
        t.append_str_to_file(path, date)


def add_date_to_subject2(id: str, date: str):
    """
    Add date to subject's with id 'id' in "Dates.txt" if doesn't already exist.
    """
    marker = False

    path = os.path.join(g.tool.myDocFolder, "configurations", g.tool.configuration.name, "subjects", id, "parameters",
                        "Dates.txt")
    arr = t.get_arr_from_file(path)
    if not t.is_array_empty(arr):
        for i in range(len(arr)):
            if date == arr[i]:
                marker = True
                break
    if not marker:
        t.append_str_to_file(path, date)


def calculate_gait_parameter(gait: m.Gait, userNo: int, partly: int):
    """
    Use codesense to execute each parameter function and get it's result.
    """
    path = os.path.join(g.rtv.app.path, "codesense")
    if not t.folder_exists(path):
        os.makedirs(path, exist_ok=True, mode=0o777)
    gait.set_nr_of_gait_parameter(len(g.tool.configuration.gaitParameterDef))

    parameterNames = []
    for i in range(len(g.tool.configuration.gaitParameterDef)):
        gait._gaitParameterName[i] = g.tool.configuration.gaitParameterDef[i].name

        currentGaitParameter = gait._gaitParameterName[i]

        parameterNames.append(g.tool.configuration.gaitParameterDef[i].name)
        filePath = os.path.join(path, f"{currentGaitParameter}.py")
        with open(filePath, 'w') as file:
            file.writelines(g.tool.configuration.gaitParameterDef[i].script)

        # Refresh imports of each gaitParameter function script, if already existed
        loaded_package_modules = dict([
            (key, value) for key, value in sys.modules.items()
            if key.startswith(currentGaitParameter) and isinstance(value, types.ModuleType)
        ])
        for key in loaded_package_modules:
            del sys.modules[key]

        gaitParamModule = importlib.import_module(f'app.codesense.{currentGaitParameter}')
        gaitParamFunc = getattr(gaitParamModule, currentGaitParameter)
        # Here, the gait parameter are calculated
        gaitParamFunc()

        # review if partly or not, need to update input parameter 'gait'
        if partly == 0:
            gait.calc_daily_parameter(i)
            g.rtv.userData[userNo].gaitParameter[i].date = g.tool.rawGait.gDate[0]
            g.rtv.userData[userNo].gaitParameter[i].mean = gait.get_mean(i)
            g.rtv.userData[userNo].gaitParameter[i].variation = gait.get_variation(i)
        else:
            g.rtv.userData[userNo].gaitParameter[i].date = g.tool.rawGait.gDate[0]
            arr = codesense.Gait.get_parameter_arr(i)
            # arr = g.rtv.gait.get_parameter_arr(i)
            g.rtv.buffer[i].values.extend(arr)

    if partly == 0:
        for i in range(len(g.tool.configuration.gaitParameterDef)):
            if g.tool.configuration.filter:
                if g.tool.configuration.removeHighestLowest > 0:
                    gait.remove_highest_lowest_gait(i, g.tool.configuration.removeHighestLowest)


def set_data_to_public(gait: m.Gait):
    """
    Set all gait data from global rawGait to global Gait object.
    """
    # warning: len+1??
    gait.set_step_nr(len(g.tool.rawGait.strides))
    gait.set_sensor_no(len(g.tool.rawGait.columnName))
    for i in range(len(g.tool.rawGait.columnName)):
        gait._sensorNames[i] = g.tool.rawGait.columnName[i]
    gait.set_sensor_data(g.tool.rawGait.columnData)
    gait.processedRows = g.rtv.processedRows

    for i in range(len(g.tool.rawGait.strides)):
        names = ["rightStart", "rightEnd", "rightStartNext", "leftStartLast", "leftStart", "leftEnd", "leftEndNext",
                 "rightHeel", "rightToe", "leftHeel", "leftToe", "rightHeelNext", "leftHeelNext", "leftToeNext",
                 "rightStartRow", "rightEndRow", "rightStartNextRow", "leftStartLastRow", "leftStartRow", "leftEndRow",
                 "leftEndNextRow",
                 "rightHeelRow", "rightToeRow", "leftHeelRow", "leftToeRow", "rightHeelNextRow", "leftHeelNextRow",
                 "leftToeNextRow",
                 "rightHeight", "leftHeight",
                 "rightWidth", "leftWidth",
                 "rightLength", "leftLength", "rightStrideLength", "leftStrideLength"]
        for name in names:
            value = getattr(g.tool.rawGait.strides[i], name)
            setattr(gait._strides[i], name, value)


def erase_gait():
    g.tool.rawGait = m.GaitData()


def make_data_values(arr: list[str], press: bool, acc: bool, date: str, userNo: int, userID: str) -> tuple[bool, bool]:
    """
    Return:  (press: bool, acc: bool), used to be as reference in positions 1,2
    """
    press = False
    acc = False

    eventer = 0

    dateFormat = 0
    dayTimePos = 0
    pressRightPos = 0
    pressLeftPos = 0

    corrector = 65536
    datePos = -1
    timePosR = -1
    timePosL = -1
    pressRightPos = -1
    apAccR = -1
    apAccL = -1
    mlAccR = -1
    mlAccL = -1
    vAccR = -1
    vAccL = -1
    overL = False
    overR = False
    sampleCounter = 0

    g.rtv.health = list()

    for i, col in enumerate(g.tool.configuration.columns):
        if g.tool.configuration.columnType[i] == 0:
            datePos = i
            dateFormat = g.tool.configuration.columnOption[i]
        elif g.tool.configuration.columnType == 1:
            timePosR = i
        elif g.tool.configuration.columnType == 16:
            timePosL = i
        elif g.tool.configuration.columnType == 18:
            dayTimePos = i
        elif g.tool.configuration.columnType == 2 and g.tool.configuration.columnOption[i] == 0:
            pressRightPos = i
            press = True
        elif g.tool.configuration.columnType == 3 and g.tool.configuration.columnOption[i] == 0:
            pressLeftPos = i
            press = True
        elif g.tool.configuration.columnType == 8:
            apAccR = i
            acc = True
            g.tool.unknownData.aY_columnR = i
        elif g.tool.configuration.columnType == 9:
            apAccL = i
            acc = True
            g.tool.unknownData.aY_columnL = i
        elif g.tool.configuration.columnType == 6:
            mlAccR = i
            acc = True
            g.tool.unknownData.aX_columnR = i
        elif g.tool.configuration.columnType == 7:
            mlAccL = i
            acc = True
            g.tool.unknownData.aX_columnL = i
        elif g.tool.configuration.columnType == 4:
            vAccR = i
            acc = True
            g.tool.unknownData.aZ_columnR = i
        elif g.tool.configuration.columnType == 5:
            vAccL = i
            acc = True
            g.tool.unknownData.aZ_columnL = i

        elif g.tool.configuration.columnType == 10:
            g.tool.unknownData.gZ_columnR = i
        elif g.tool.configuration.columnType == 12:
            g.tool.unknownData.gX_columnR = i
        elif g.tool.configuration.columnType == 14:
            g.tool.unknownData.gX_columnR = i
        elif g.tool.configuration.columnType == 11:
            g.tool.unknownData.gZ_columnL = i
        elif g.tool.configuration.columnType == 13:
            g.tool.unknownData.gX_columnL = i
        elif g.tool.configuration.columnType == 15:
            g.tool.unknownData.gY_columnL = i

    # Reset gait values
    # warning: redims size +1?
    if not t.is_array_empty(arr):
        g.tool.rawGait.gDate = [""] * len(arr)
        g.tool.rawGait.gRtime = [0.0] * len(arr)
        g.tool.rawGait.gLtime = [0.0] * len(arr)
        g.tool.rawGait.gRightAcc = [0.0] * len(arr)
        g.tool.rawGait.gLeftAcc = [0.0] * len(arr)
        g.tool.rawGait.gRightAccAP = [0.0] * len(arr)
        g.tool.rawGait.gLeftAccAP = [0.0] * len(arr)
        g.tool.rawGait.columnName = [""] * len(g.tool.configuration.columns)
        g.tool.rawGait.columnData = [[0.0] * len(arr)] * len(g.tool.configuration.columns)
        g.rtv.health = [False] * len(g.tool.configuration.columns)

        for i in range(len(g.tool.configuration.columns)):
            g.tool.rawGait.columnName[i] = g.tool.configuration.columns[i]
        # l_timer = Timer
        for i in range(len(arr)):
            # l_Eventer = l_Eventer + 1
            # If l_Eventer > 1000 Then
            #     l_Eventer = 0
            #     If Not GetInputState = 0 Then DoEvents
            # End If
            if len(arr[i]) > 0:
                line = arr[i].split(",")
                arr[i] = ""
                if datePos > -1:
                    g.tool.rawGait.gDate[i] = f"{line[datePos][5:5 + 2]}/{line[datePos][8:8 + 2]}/{line[datePos][:4]}"
                else:
                    g.tool.rawGait.gDate[i] = date
                if timePosR > -1:
                    g.tool.rawGait.gLtime[i] = float(line[timePosL]) * 0.001
                    g.tool.rawGait.gRtime[i] = float(line[timePosR]) * 0.001
                    # if i > 0:
                    if g.tool.rawGait.gLtime[i] < g.tool.rawGait.gLtime[0]:
                        overL = True
                    if g.tool.rawGait.gRtime[i] < g.tool.rawGait.gRtime[0]:
                        overR = True
                    if overL:
                        g.tool.rawGait.gLtime[i] = g.tool.rawGait.gLtime[i] + corrector
                        line[timePosL] = g.tool.rawGait.gLtime[i] * 1000
                    if overR:
                        g.tool.rawGait.gRtime[i] = g.tool.rawGait.gRtime[i] + corrector
                        line[timePosR] = g.tool.rawGait.gRtime[i]
                else:
                    sampleCounter = sampleCounter + 1 / g.tool.configuration.sampleFrequency
                    g.tool.rawGait.gRtime[i] = sampleCounter
                    g.tool.rawGait.gLtime[i] = sampleCounter

                # Pressure
                if pressRightPos > -1 and pressLeftPos > -1:
                    for j in range(len(g.tool.rawGait.columnName)):
                        g.tool.rawGait.columnData[j][i] = float(line[j])
                        if g.tool.configuration.inputType == 0:
                            # Pressure calibration
                            if (j > 9 and j < 24) or (j > 35 and j < 50):
                                adjust_pressure(j, g.tool.rawGait.columnData[j][i], userID)
                                if i > 0:
                                    check_health(j, g.tool.rawGait.columnData[j][i - 1],
                                                 g.tool.rawGait.columnData[j][i])
                            # Acceleration values
                            if j in [4, 5, 6, 30, 31, 32]:
                                g.tool.rawGait.columnData[j][i] *= g.tool.const2
                                if i > 0:
                                    check_health(j, g.tool.rawGait.columnData[j][i - 1],
                                                 g.tool.rawGait.columnData[j][i])
                            if j in [1, 2, 3, 27, 28, 29]:
                                g.tool.rawGait.columnData[j][i] *= g.tool.const1
                                if i > 0:
                                    check_health(j, g.tool.rawGait.columnData[j][i - 1],
                                                 g.tool.rawGait.columnData[j][i])
                    g.tool.rawGait.gRightAccAP[i] = abs(g.tool.rawGait.columnData[31][i])
                    g.tool.rawGait.gRightAcc[i] = math.sqrt(
                        g.tool.rawGait.columnData[30][i] ** 2 + g.tool.rawGait.columnData[31][i] ** 2 +
                        g.tool.rawGait.columnData[32][i] ** 2)

                    g.tool.rawGait.gLeftAccAP[i] = abs(g.tool.rawGait.columnData[5][i])
                    g.tool.rawGait.gLeftAcc[i] = math.sqrt(
                        g.tool.rawGait.columnData[4][i] ** 2 + g.tool.rawGait.columnData[5][i] ** 2 +
                        g.tool.rawGait.columnData[6][i] ** 2)
                # acceleration
                elif vAccR > -1:
                    if i > 0:
                        for j in range(len(g.tool.rawGait.columnName)):
                            g.tool.rawGait.columnData[j][i] = t.remove_E(line[j])
        if i > 9000:
            process_health(userID, date)

    return (press, acc)


def adjust_pressure(i: int, value: float, userID: str):
    """Not implemented"""
    pass


def check_health(j: int, oldData: float, data: float):
    if oldData != data:
        g.rtv.health[j] = True


def pressure_sum(insole: int, line: list[str]) -> float:
    acc = 0
    if insole == 0:
        for i in range(36, 49 + 1):
            acc += float(line[i])
    elif insole == 1:
        for i in range(10, 23 + 1):
            acc += line[i]
    return acc


def process_health(userID: str, date: str):
    """
    Read data in myDoc/data/sensors.txt and append if i in some values...???
    """
    if len(g.rtv.health) > 0:
        path = os.path.join(g.tool.myDocFolder, "data", "sensors.txt")
        arr = t.get_arr_from_file(path)
        for i in range(len(g.rtv.health)):
            if (i > 9 and i < 24) or (i > 35 and i < 50):
                # pressure
                if not g.rtv.health[i]:
                    string = f"{userID},{date},{i}"
                    if string not in arr:
                        t.append_str_to_file(path, string)
            elif i in [4, 5, 6, 30, 31, 32]:
                # acceleration
                if not g.rtv.health[i]:
                    string = f"{userID},{date},{i}"
                    if string not in arr:
                        t.append_str_to_file(path, string)
            elif i in [1, 2, 3, 27, 28, 29]:
                # gyro
                if not g.rtv.health[i]:
                    string = f"{userID},{date},{i}"
                    if string not in arr:
                        t.append_str_to_file(path, string)


def remove_highest_lowest_from_arr(arr: list[float], remmoveHighestLowest: float):
    if len(arr) > 0:
        noToRemove = int(len(arr) * 0.01 * remmoveHighestLowest)
        # warning: start is 1 o 0? and noToRemove or noToRemove+1, bc it's not inclusive?
        for i in range(noToRemove):
            remove_lowest_stride_from_arr(arr)
            remove_highest_stride_from_arr(arr)


def remove_lowest_stride_from_arr(arr: list[float]):
    # 1. Find lowest
    low = 9999999
    for i in range(len(arr)):
        if arr[i] < low:
            low = arr[i]

    # 2. Replace all instances of lowest with the previous
    for i in range(1, len(arr)):
        if arr[i] == low:
            arr[i] = arr[i - 1]
            break

    # What, if the first is the lowest ? First = 0
    if arr[0] == low:
        arr[0] = arr[-1]


def remove_highest_stride_from_arr(arr: list[float]):
    # 1. Find highest
    high = -9999999
    for i in range(len(arr)):
        if arr[i] > high:
            high = arr[i]

    # 2. Replace all instances of lowest with the previous
    for i in range(1, len(arr)):
        if arr[i] == high:
            arr[i] = arr[i - 1]
            break

    # What, if the first is the lowest ? First = 0
    if arr[0] == high:
        arr[0] = arr[-1]


def add_pattern(pattern: m.Pattern1):
    """
    Add pattern1 to global conf.gaitPattern1, if already doesn't exist one with same name.
    """
    marker = False
    for i in range(g.tool.configuration.gaitPattern1):
        if g.tool.configuration.gaitPattern1[i].name == pattern.name:
            marker = True
            break
    if not marker:
        g.tool.configuration.gaitPattern1.append(pattern)
        g.rt.get_child("list7").insert(tk.END, g.tool.configuration.gaitPattern1[-1].name)
        g.rt.get_child("list10").insert(tk.END, g.tool.configuration.gaitPattern1[-1].name)


def load_chart2():
    """Read raw data from selected user in combo1, and graph it, adding subplots for each selected gait parameter."""
    sensorFull = False
    rudeFull = False
    paraFull = False
    overflow = False  # ?????
    fDate = ""
    fDate2 = ""
    filePath = ""
    oldLine = 0
    timeCnt = 0

    start = []
    end = 0

    width = g.rt.vars["text24"]
    if width == 0:
        width = 1
    sensors = g.tool.configuration.sensorToWatch.split("|")
    if not t.is_array_empty(sensors):
        sensorPos = [0] * len(sensors)
        sensorFull = True

    parameters = g.tool.configuration.selectToWatch.split("|")
    fDate = f'{g.rtv.date.month:02d}{g.rtv.date.day:02d}{g.rtv.date.year:02d}'

    combo1Text = g.rt.get_child("combo1").get()

    if g.tool.configuration.inputType == 1:
        fDate2 = t.get_str_from_date(g.rtv.date)
        filePath = os.path.join(g.tool.configuration.users[t.get_user_no(combo1Text)].filePath,
                                g.tool.configuration.users[t.get_user_no(combo1Text)].name)
    elif g.tool.configuration.inputType == 0:
        fDate2 = f'{g.rtv.date.day:02d}-{g.rtv.date.month:02d}-{g.rtv.date.year:02d}'
        filePath = os.path.join(g.tool.configuration.users[t.get_user_no(combo1Text)].filePath, f'reg_{fDate2}.txt')

    valuesToDraw = 5000
    arr = [""] * valuesToDraw
    start = [0.0] * valuesToDraw
    noOfRows = t.count_file_lines(filePath)
    start[0] = noOfRows * 0.01 * g.rt.get_child("rangetool1").get()
    end = noOfRows * 0.01 * g.rt.get_child("rangetool1")['to']
    step = (end - start[0]) / valuesToDraw
    for i in range(valuesToDraw):
        if i > 0:
            start[i] = start[i - 1] + step
        arr[i] = t.read_file_line(filePath, int(start[i]))

    # rude gait
    if len(arr) > 0:
        path = os.path.join(g.tool.myDocFolder, "configurations", g.tool.configuration.name, "subjects",
                            g.tool.configuration.users[t.get_user_no(combo1Text)].id, "parameter", "intraday",
                            f'{fDate}_RawGait.txt')
        rude = t.get_arr_from_file(path)
        if not t.is_array_empty(rude):
            rudeFull = True
            rudeDetails = [[] for x in range(4)]
            for i in range(len(rude)):
                temp = rude[i].split(",")
                if not t.is_array_empty(temp):
                    if len(temp) == 4:
                        rudeDetails[0].append(float(temp[0]))
                        rudeDetails[1].append(float(temp[1]))
                        rudeDetails[2].append(float(temp[2]))
                        rudeDetails[3].append(float(temp[3]))

            # intraday gait parameter
            if not t.is_array_empty(parameters):
                units = [""] * len(parameters)
                for i in range(len(parameters)):
                    getParaNo = t.get_para_no(parameters[i])
                    if getParaNo > -1:
                        units[i] = f'[{g.tool.configuration.gaitParameterDef[getParaNo].unit}]'
                paraFull = True
                tempValue = [[float()] * len(rude)] * len(parameters)
                tempPos = [[float()] * len(rude)] * len(parameters)
                tempValue = np.zeros((len(parameters), len(rude))).tolist()
                tempPos = np.zeros((len(parameters), len(rude))).tolist()
                for i in range(len(parameters)):
                    path = os.path.join(g.tool.myDocFolder, "configurations", g.tool.configuration.name, "subjects",
                                        g.tool.configuration.users[t.get_user_no(combo1Text)].id, "parameter",
                                        "intraday", f'{fDate}_{parameters[i]}.txt')
                    paraArr = t.get_arr_from_file(path)
                    if not t.is_array_empty(paraArr):
                        for j in range(len(rude)):
                            if paraArr[j] != "":
                                temp = paraArr[j].split(",")
                                tempPos[i][j] = float(temp[2])
                                tempValue[i][j] = float(temp[1])
                    else:
                        print("parArr is empty")
        # rude is empty
        else:
            rudeFull = False

        if sensorFull:
            sensorUnits = [""] * len(sensors)
            for i in range(len(sensors)):
                getSensorNo = t.get_column_no(sensors[i])
                if getSensorNo > -1:
                    sensorUnits[i] = f'[{g.tool.configuration.columnUnit[getSensorNo]}]'
                for j in range(len(g.tool.configuration.columns)):
                    if sensors[i] == g.tool.configuration.columns[j]:
                        sensorPos[i] = j
                        break

        # look if timeCol exists
        timeCol = -1
        for i in range(len(g.tool.configuration.columns)):
            if g.tool.configuration.columnType[i] == str(1):
                timeCol = i
                break

        numSubplots = 0
        currSubplot = 0
        if sensorFull:
            numSubplots += 1  # sensor values plotted in same plot
        if rudeFull:
            numSubplots += 1  # step diff filter right/left plotted in same plot
            if paraFull:
                numSubplots += len(parameters)  # param[i] values plotted each in a separate plot

        # getting plot values
        sensorValues = [[] for x in range(len(sensors))]
        parameterValues = [[] for x in range(len(parameters))]
        stepDiffValues = [[] for x in range(2)]
        for row in range(len(arr)):
            if arr[row] != "":
                line = arr[row].split(",")
                if sensorFull:
                    for i in range(len(sensors)):
                        dbl = float(t.rem_k(line[sensorPos[i]]))
                        if sensorPos[i] in [4, 5, 6, 30, 31, 32]:
                            dbl = dbl * g.tool.const2
                        if sensorPos[i] in [1, 2, 3, 27, 28, 29]:
                            dbl = dbl * g.tool.const1
                        sensorValues[i].append(dbl)

                if rudeFull:
                    if paraFull:
                        for i in range(len(parameters)):
                            # warning: len(rude) or len(rude)-1
                            paramVal = how_is_current_value_of_indicator(i, float(line[timeCol]) * 0.001, tempPos,
                                                                         tempValue, len(rude))
                            parameterValues[i].append(paramVal)
                    # warning: len(rude) or len(rude)-1
                    value1, value2 = how_is_current_state(float(line[timeCol]) * 0.001, rudeDetails, len(rude))
                    stepDiffValues[0].append(value1)
                    stepDiffValues[1].append(value2)

        fig = Figure(figsize=(8, 7), dpi=100)

        if sensorFull:
            currSubplot += 1
            ax = fig.add_subplot(numSubplots, 1, currSubplot)
            for i in range(len(sensors)):
                # ax.set_xlabel(f'{sensors[i]}{sensorUnits[i]}')
                # ax.set_ylim(bottom=-8, top=8)
                ax.plot(sensorValues[i], label=f'{sensors[i]}{sensorUnits[i]}')
            ax.legend(bbox_to_anchor=[1, 1.3], loc='upper center', fontsize='small')
        if rudeFull:
            if paraFull:
                for i in range(len(parameters)):
                    currSubplot += 1
                    ax = fig.add_subplot(numSubplots, 1, currSubplot)
                    ax.set_ylabel(f'{parameters[i]}{units[i]}')
                    ax.plot(parameterValues[i])
            currSubplot += 1
            ax = fig.add_subplot(numSubplots, 1, currSubplot)
            ax.plot(stepDiffValues[0], label='Step filter right')
            ax.plot(stepDiffValues[1], label='Step filter left')
            ax.legend(bbox_to_anchor=[1, 1.3], loc='upper center', fontsize='small')

        # find x axis, shared by all plots
        # axisX = []
        # for row in range(len(arr)):
        #     if arr[row] != "":
        #         line = arr[i].split(",")
        #         year = g.rtv.date.year
        #         month = g.rtv.date.month
        #         day = g.rtv.date.day

        #         if timeCol > -1:
        #             if line[timeCol] < oldLine:
        #                 overflow = True
        #             if overflow:
        #                 line[timeCol] += 65536000 #???
        #             if row == 0:
        #                 oldLine = line[timeCol]
        #             hour, minute, second = t.sec_to_time(int(line[timeCol]))
        #         else:
        #             timeCnt = timeCnt + 1 / g.tool.configuration.sampleFrequency
        #             time = t.make_time(timeCnt)
        #             hour = time.seconds // 3600
        #             minute = time.seconds // 60
        #             second = time.seconds
        #         #TODO: change value of axisX... in vb6, went from 0 to 5000, but jDate values were in julianDate (float...)
        #         axisX.append(sum(jdcal.gcal2jd()))

        parent = g.rt.get_child("stockchartx1")
        figCanvas = FigureCanvasTkAgg(fig, master=parent)
        figCanvas.draw()

        toolbar = NavigationToolbar2Tk(figCanvas, parent, pack_toolbar=False)
        toolbar.update()

        toolbar.grid(row=2, column=0)
        figCanvas.get_tk_widget().grid(row=0, column=0, sticky=tk.NSEW)


def command24_click():
    g.tool.cluster.clear()
    g.tool.Ncluster.clear()

    treeview1 = g.rt.get_child("treeview1")
    treeview1.delete(*treeview1.get_children())
    treeview2 = g.rt.get_child("treeview2")
    treeview2.delete(*treeview2.get_children())

    for i, gaitParDef in enumerate(g.tool.configuration.gaitParameterDef):
        newClusterF = m.Cluster()
        newClusterN = m.Cluster()
        newClusterF.name = gaitParDef.name
        newClusterF.clusterId = gaitParDef.name
        newClusterN.name = gaitParDef.name
        newClusterN.name = gaitParDef.name

        fAll = list()
        nAll = list()
        for j, user in enumerate(g.tool.configuration.users):
            if user.active:
                path = os.path.join(g.tool.myDocFolder, "configurations", g.tool.configuration.name, "subjects",
                                    user.id, "parameter", "intraday")
                pathList = t.get_file_list_from_path(path, extension="txt")
                if len(pathList) > 0:
                    for k in range(len(pathList)):
                        # DoEvents
                        if gaitParDef.name in pathList[k]:
                            # TODO: borrar
                            # path = os.path.join(g.tool.myDocFolder, "configurations", g.tool.configuration.name, "subjects", user.id, "parameter", "intraday")
                            arr = t.get_arr_from_file(pathList[k])
                            if user.faller == m.Faller.FALLER:
                                print(
                                    f'Faller - user = {user.name}. GaitParam = {gaitParDef.name}. File = {pathList[k]}')
                                fAll = t.add_to_all(fAll, arr, 1, True, True)
                            elif user.faller == m.Faller.NON_FALLER:
                                print(
                                    f'NonFaller - user = {user.name}. GaitParam = {gaitParDef.name}. File = {pathList[k]}')
                                nAll = t.add_to_all(nAll, arr, 1, True, True)
            if g.rtv.cancel:
                g.rtv.cancel = False
                return

        print(f'Finished looping over users')
        if len(fAll) > 0:
            newClusterF.correlation = 0.6  # magic
            print("Adding clusters")
            for j in range(len(fAll)):
                newSerie = [all.value for all in fAll[j]]
                newClusterF.add_serie(newSerie, gaitParDef.name)
            print("finished adding clusters")
            if newClusterF.clustering():
                treeview1.insert('', tk.END, gaitParDef.name, text=newClusterF.name)
                for j in range(newClusterF._noOfCluster):
                    if newClusterF.get_no_of_cluster_series(j) > 1:
                        treeview1.insert(gaitParDef.name, tk.END, f'{newClusterF.name}|{j}',
                                         text=f'{j + 1}-{newClusterF.get_no_of_cluster_series(j)}')

        g.tool.cluster.append(newClusterF)
        g.tool.cluster.append(newClusterN)


def how_is_current_value_of_indicator(indiNo: int, time: float, tempPos: list[list[float]], tempValue: list[float],
                                      ubnd: int) -> float:
    res = 0.0
    marker = False
    for i in range(ubnd - 1):
        if time == tempPos[indiNo][i]:
            res = tempValue[indiNo][i]
            marker = True
            break
        elif time > tempPos[indiNo][i] and time < tempPos[indiNo][i + 1]:
            res = tempValue[indiNo][i]
            marker = True
            break

    if not marker:
        if time < tempPos[indiNo][0]:
            res = tempValue[indiNo][0]
        elif time > tempPos[indiNo][ubnd - 1]:
            res = tempValue[indiNo][ubnd - 1]
    return res


def how_is_current_state(time: float, rudeDetails: list[list[float]], ubnd: int) -> tuple[float, float]:
    """
    Return: (value1, value2)... were by ref, first 2 params.
    """
    value1 = 0
    value2 = 0.5
    for i in range(ubnd):
        # Exactly start
        if time == rudeDetails[0][i]:
            value1 = 0.5
            # break
        elif time == rudeDetails[1][i]:
            value1 = 0
            # break
        # Exactly end
        if time == rudeDetails[2][i]:
            value2 = 1
            # break
        elif time == rudeDetails[3][i]:
            value2 = 0.5
            # break

        # Between start and end
        if time > rudeDetails[0][i]:
            if time < rudeDetails[1][i]:
                value1 = 0.5
                # break
        if time > rudeDetails[2][i]:
            if time < rudeDetails[3][i]:
                value2 = 1
                # break
        # 'Zwischen ende und start
        # '    If l_Time > l_RudeDetails(0, I) And l_Time > l_RudeDetails(1, I) Then
        # '        l_Value1 = 0
        # '        Exit For
        # '    End If
        # '    If l_Time > l_RudeDetails(2, I) And l_Time > l_RudeDetails(3, I) Then
        # '        l_Value2 = 0
        # '        Exit For
        # '    End If
    return (value1, value2)


def rangetool1_change():
    load_chart2()


def auto_open_default(inputType: int):
    name = ""
    if inputType == 0:
        name = "WIISEL default"
    elif inputType == 1:
        name = "Import default"
    if g.tool.configuration.changed:
        if messagebox.askyesno(message="Your configuration has changed. Save it ?"):
            save_configuration(False)

    path = os.path.join(g.tool.myDocFolder, "configurations", f'{name}.configuration')
    open_configuration(path)
    if name == "WIISEL default":
        # g.tool.configuration.changed = autofill_wiisel_patients_to_list()
        pass
    else:
        g.tool.configuration.changed = False


def form_load_sensor_health():
    sensorGrid = g.rt.get_child("sensors", root=g.rt.sensorHealth)

    sensorGrid.delete(*sensorGrid.get_children())

    columnHeaders = ('Subject', 'Date', 'Sensor no')
    sensorGrid['columns'] = columnHeaders
    for i, column in enumerate(columnHeaders):
        sensorGrid.column(f'#{i}', anchor=tk.CENTER, width=100)
        sensorGrid.heading(f'#{i}', text=column)

    path = os.path.join(g.tool.myDocFolder, "data", "sensors.txt")
    arr = t.get_arr_from_file(path)
    for line in arr:
        if arr[i] != "":
            lineArr = line.split(",")
            add_sensor_problem(lineArr[0], lineArr[1], lineArr[2])

    g.rt.sensorHealth.wm_deiconify()


def add_sensor_problem(subject: str, date: str, sensorNo: int):
    matchedChildId = ''
    sensorGrid = g.rt.get_child("sensors", root=g.rt.sensorHealth)

    for childId in sensorGrid.get_children():
        child = sensorGrid.item(childId)
        if child['text'] == subject and child['values'][0] == date:
            matchedChildId = childId
            break

    if matchedChildId == '':
        sensorGrid.insert('', tk.END, text=subject, values=(date, sensorNo))
    else:
        currSensorNames = sensorGrid.item(matchedChildId)['values'][1]  # ("sensor1,sensor2...")
        currSensorNames = f'{currSensorNames},{sensorNo}'
        sensorGrid.set(matchedChildId, '#2', currSensorNames)


def form_load_userinfo():
    list1 = g.rt.get_child("list1", g.rt.userInfo)
    list1.insert(tk.END, "Number of steps")
    list1.insert(tk.END, "Activity time")
    list1.insert(tk.END, "Number of falls")

    list2 = g.rt.get_child("list2", g.rt.userInfo)
    for gaitParDef in g.tool.configuration.gaitParameterDef:
        list2.insert(tk.END, gaitParDef.name)
        list2.insert(tk.END, f'{gaitParDef.name} variation')

    list3 = g.rt.get_child("list3", g.rt.userInfo)
    for fri in g.tool.configuration.fallRiskIndex:
        list3.insert(tk.END, fri.name)


def form_load_patternextraction():
    resultsList = g.rt.get_child("resultslist", root=g.rt.patternExtraction)
    resultsList.delete(*resultsList.get_children())

    combo1 = g.rt.get_child("combo1", g.rt.patternExtraction)
    combo1.delete(0, tk.END)
    comboitems = ["Bar chart 3D", "Bar chart 2D", "Line chart 3D", "Line chart 2D"]
    combo1['values'] = tuple(comboitems)
    combo1.current(len(combo1['values']) - 1)

    if g.tool.configuration.filterVarianceF > 0:
        g.rt.patternExtractionVars["text30"].set(g.tool.configuration.filterVarianceF)
        g.rt.patternExtractionVars["check2"].set(True)
    else:
        g.rt.patternExtractionVars["text30"].set(0)
        g.rt.patternExtractionVars["check2"].set(False)
    if g.tool.configuration.filterStdDevF > 0:
        g.rt.patternExtractionVars["text21"].set(g.tool.configuration.filterStdDevF)
        g.rt.patternExtractionVars["check1"].set(True)
    else:
        g.rt.patternExtractionVars["text21"].set(0)
        g.rt.patternExtractionVars["check1"].set(False)
    if g.tool.configuration.filterStdErrF > 0:
        g.rt.patternExtractionVars["text33"].set(g.tool.configuration.filterStdErrF)
        g.rt.patternExtractionVars["check3"].set(True)
    else:
        g.rt.patternExtractionVars["text33"].set(0)
        g.rt.patternExtractionVars["check3"].set(False)
    if g.tool.configuration.filterVarianceN > 0:
        g.rt.patternExtractionVars["text2"].set(g.tool.configuration.filterVarianceN)
        g.rt.patternExtractionVars["check5"].set(True)
    else:
        g.rt.patternExtractionVars["text2"].set(0)
        g.rt.patternExtractionVars["check5"].set(False)
    if g.tool.configuration.filterStdDevN > 0:
        g.rt.patternExtractionVars["text1"].set(g.tool.configuration.filterStdDevN)
        g.rt.patternExtractionVars["check6"].set(True)
    else:
        g.rt.patternExtractionVars["text1"].set(0)
        g.rt.patternExtractionVars["check6"].set(False)
    if g.tool.configuration.filterStdErrN > 0:
        g.rt.patternExtractionVars["text3"].set(g.tool.configuration.filterStdErrN)
        g.rt.patternExtractionVars["check4"].set(True)
    else:
        g.rt.patternExtractionVars["text3"].set(0)
        g.rt.patternExtractionVars["check4"].set(False)
    if g.tool.configuration.filterHighLowF > 0:
        g.rt.patternExtractionVars["text5"].set(g.tool.configuration.filterHighLowF)
        g.rt.patternExtractionVars["check8"].set(True)
    else:
        g.rt.patternExtractionVars["text5"].set(0)
        g.rt.patternExtractionVars["check8"].set(False)
    if g.tool.configuration.filterHighLowN > 0:
        g.rt.patternExtractionVars["text4"].set(g.tool.configuration.filterHighLowN)
        g.rt.patternExtractionVars["check7"].set(True)
    else:
        g.rt.patternExtractionVars["text4"].set(0)
        g.rt.patternExtractionVars["check7"].set(False)


def form_load_enter_fri():
    friNamesList = g.rt.get_child("list2")
    if len(friNamesList.curselection()) > 0:
        g.rt.enterFriVars["text1"].set(friNamesList.curselection()[0])
        listIndex = [*friNamesList.get(0, tk.END)].index(friNamesList.get(tk.ACTIVE))
        g.rt.enterFriVars["check1"] = g.tool.configuration.fallRiskIndex[listIndex].forAll

        g.rt.enterFri.wm_deiconify()


def form_load_sensor_selector():
    combo1SensorSelector = g.rt.get_child("combo1", root=g.rt.sensorSelector)
    combo1SensorSelector['values'] = [sensorType for sensorType in g.tool.sensorTypes]

    combo2SensorSelector = g.rt.get_child("combo2", root=g.rt.sensorSelector)
    combo2SensorSelector['values'] = [sensorOption for sensorOption in g.tool.sensorOptions]


def command33_click():
    """Select all gait parameters (Fall Risk Index definition)"""
    list10 = g.rt.get_child("list10")
    list10.selection_clear(0, tk.END)
    list10.selection_set(0, tk.END)


def command8_click():
    name = easygui.enterbox("Please enter a name for the Fall risk index")
    if name != "" and name is not None:
        for fri in g.tool.configuration.fallRiskIndex:
            if name.lower() == fri.name.lower():
                messagebox.showerror(message="This name already exists")
                return
        newFri = m.RiskIndex(name=name, active=False, greenStart=0, greenEnd=30, yellowStart=30, yellowEnd=70,
                             redStart=70, redEnd=100)
        g.rt.get_child("list2").insert(tk.END, newFri.name)
        g.tool.configuration.fallRiskIndex.append(newFri)
        g.tool.configuration.changed = True


def command9_click():
    list2 = g.rt.get_child("list2")
    if len(list2.curselection()) > 0:
        form_load_enter_fri()


def command10_click():
    list2 = g.rt.get_child("list2")
    if len(list2.curselection()) > 0:
        list2Index = [*list2.get(0, tk.END)].index(list2.get(tk.ACTIVE))
        if g.tool.configuration.fallRiskIndex[list2Index].forAll:
            path = os.path.join(g.tool.myDocFolderRoot, "FRI",
                                f'{t.safe_file_name(g.tool.configuration.fallRiskIndex[list2Index].name)}.fri')
            if os.path.exists(path):
                os.remove(path)
        if len(g.tool.configuration.fallRiskIndex) > 0:
            g.tool.configuration.fallRiskIndex.pop(list2Index)
        t.delete_FRI_from_subjects(list2.get(list2Index))
        list2.delete(list2Index)
        g.tool.configuration.changed = True


def list2_click():
    if not g.tool.loadingConf:
        list2 = g.rt.get_child("list2")
        if len(list2.curselection()) > 0:
            list2Index = [*list2.get(0, tk.END)].index(list2.get(tk.ACTIVE))
            for i in range(len(g.tool.configuration.fallRiskIndex)):
                g.tool.configuration.fallRiskIndex[i].active = False
            g.tool.configuration.fallRiskIndex[i].active = True
            g.tool.configuration.changed = True

        g.rtv.noChange = True

        list10 = g.rt.get_child("list10")
        list10.selection_clear(0, tk.END)

        for i, element in enumerate(list10.get(0, tk.END)):
            for component in g.tool.configuration.fallRiskIndex[list2Index].components:
                if component.elementName == element:
                    list10.selection_set(i)
                    break
        g.rtv.noChange = False

        fill_fri_list()


def list10_click(e: tk.Event):
    if not g.rtv.noChange:
        list2 = g.rt.get_child("list2")
        if len(list2.curselection()) > 0:
            list2Index = [*list2.get(0, tk.END)].index(list2.get(tk.ACTIVE))
            # list10 = g.rt.get_child("list10")
            list10 = e.widget
            list10Index = [*list10.get(0, tk.END)].index(list10.get(tk.ACTIVE))
            if list10Index in list10.curselection():
                newComponent = m.Component(elementName=list10.get(tk.ACTIVE))
                g.tool.configuration.fallRiskIndex[list2Index].components.append(newComponent)
            else:
                for i, component in enumerate(g.tool.configuration.fallRiskIndex[list2Index].components):
                    if component.elementName.lower() == list10.get(tk.ACTIVE).lower():
                        del g.tool.configuration.fallRiskIndex[list2Index].components[i]
                        break

            make_100(g.tool.configuration.fallRiskIndex[list2Index].components, 0)
            fill_fri_list()
            g.tool.configuration.changed = True


def fill_fri_list():
    """SetFIndexList"""
    fri_list = g.rt.get_child("fri_list")
    fri_list.delete(*fri_list.get_children())
    list2 = g.rt.get_child("list2")
    list2Index = [*list2.get(0, tk.END)].index(list2.get(tk.ACTIVE))

    columnHeaders = ('Selected pattern', 'Weight [%]', 'Minimum impact [%]')
    fri_list['columns'] = columnHeaders[1:]
    for i, column in enumerate(columnHeaders):
        fri_list.column(f'#{i}', width=100, anchor=tk.CENTER)
        fri_list.heading(f'#{i}', text=column)
    for component in g.tool.configuration.fallRiskIndex[list2Index].components:
        fri_list.insert('', tk.END, text=component.elementName, values=(component.weight, component.impact))
    set_pie()

    g.rt.vars["text11"].set(g.tool.configuration.fallRiskIndex[list2Index].redStart)
    g.rt.vars["text12"].set(g.tool.configuration.fallRiskIndex[list2Index].redEnd)
    g.rt.vars["text13"].set(g.tool.configuration.fallRiskIndex[list2Index].yellowStart)
    g.rt.vars["text14"].set(g.tool.configuration.fallRiskIndex[list2Index].yellowEnd)
    g.rt.vars["text15"].set(g.tool.configuration.fallRiskIndex[list2Index].greenStart)
    g.rt.vars["text16"].set(g.tool.configuration.fallRiskIndex[list2Index].greenEnd)

    fill_fri_detail_list()


def set_pie():
    list2 = g.rt.get_child("list2")
    list2Index = [*list2.get(0, tk.END)].index(list2.get(tk.ACTIVE))

    fig = Figure(figsize=(4, 3), dpi=100)
    ax = fig.add_subplot(1, 1, 1)
    ax.set_title("Distribution of pattern [%]")
    plotValues = [component.weight for component in g.tool.configuration.fallRiskIndex[list2Index].components]
    plotLabels = [component.elementName for component in g.tool.configuration.fallRiskIndex[list2Index].components]
    ax.pie(plotValues, labels=plotLabels)

    parent = g.rt.get_child("piechart")
    figCanvas = FigureCanvasTkAgg(fig, master=parent)
    figCanvas.draw()

    toolbar = NavigationToolbar2Tk(figCanvas, parent, pack_toolbar=False)
    toolbar.update()

    toolbar.grid(row=2, column=0)
    figCanvas.get_tk_widget().grid(row=0, column=0)


def fill_fri_detail_list():
    list2 = g.rt.get_child("list2")
    list2Index = [*list2.get(0, tk.END)].index(list2.get(tk.ACTIVE))

    if len(list2.curselection()) > 0:
        friTable = g.rt.get_child("fri_table")
        friTable.delete(*friTable.get_children())

        patternHeaders = [f'{component.elementName} (Weight: {component.weight} %)' for component in
                          g.tool.configuration.fallRiskIndex[list2Index].components]
        columnHeaders = ('Subject', *patternHeaders, 'Fall risk Index')
        friTable['columns'] = [f'#{i}' for i in range(1, len(columnHeaders))]

        for i, column in enumerate(columnHeaders):
            friTable.column(f'#{i}', anchor=tk.CENTER, width=100)
            friTable.heading(f'#{i}', text=column)

        for i, user in enumerate(g.tool.configuration.users):
            if user.active:
                details = list()
                values = t.calc_FRI(i, list2.get(tk.ACTIVE), details)
                if len(details) > 0:
                    # TODO: add color to row
                    color = ""

                    rowToInsert = list()
                    for detail in details:
                        line = detail.split("|")
                        rowToInsert.append(f'{line[2]} %')
                    if len(values) > 0:
                        line = values[-1].split(",")
                        value = float(t.kzp(line[1]))
                        rowToInsert.append(str(value))
                    else:
                        rowToInsert.append("")
                    friTable.insert('', tk.END, text=user.name, values=rowToInsert)


def make_100(components: list[m.Component], last: int):
    """Average out the weights of the components, so that they retain their relative difference, but end up summing 100 (%)"""
    # if len(components) == 1:
    #     components[0].weight = 100
    # else:
    #     if components[last].weight > 100:
    #         components[last].weight = 100
    #         return
    #     elif components[last].weight < 0:
    #         components[last].weight = 0
    #         return

    #     while sum():
    #         weightSum = 0
    #         for component in components:
    #             weightSum += component.weight

    #         if weightSum < 100:
    #             for component in components:
    #                 pass
    if len(components) == 1:
        components[0].weight = 100
    else:
        maxComponent = max(components, key=lambda comp: comp.weight)
        for i in range(len(components)):
            components[i].weight *= 100 / maxComponent.weight


def command35_click():
    if len(g.tool.configuration.fallRiskIndex) > 0:
        list2 = g.rt.get_child("list2")
        list2Index = [*list2.get(0, tk.END)].index(list2.get(tk.ACTIVE))
        list2Count = len(list2.get(0, tk.END))
        for i in range(len(g.tool.configuration.fallRiskIndex[list2Index].components)):
            g.tool.configuration.fallRiskIndex[list2Index].components[i].weight = round(100 / list2Count, ndigits=2)
        fill_fri_list()
        g.tool.configuration.changed = True


def fill_subject_list():
    combo2 = g.rt.get_child("combo2")
    if combo2.current() != -1:
        username = combo2.get()

        # List: Subject data
        subjectList = g.rt.get_child("fact_subject")
        subjectList.delete(*subjectList.get_children())

        columnHeaders = ('First name', 'Last name', 'Age', 'Phone', 'Email', 'Size of insole', 'Addresses', 'Note',
                         'Ampel shown on smartphone')
        subjectList['columns'] = [f'#{i}' for i in range(1, len(columnHeaders))]
        for i in range(len(columnHeaders)):
            subjectList.heading(f'#{i}', text=columnHeaders[i])
            subjectList.column(f'#{i}', anchor=tk.CENTER, width=45)

        user = g.tool.configuration.users[t.get_user_no(username)]
        subjectListData = (
            user.firstname, user.lastname, user.age, user.phone, user.email, user.insole, user.address, user.note,
            user.ampelOnPhone)
        subjectList.insert('', tk.END, text=subjectListData[0], values=subjectListData[1:])

        # List: Statistics
        statisticsList = g.rt.get_child("fact_statistics")
        statisticsList.delete(*statisticsList.get_children())

        columnHeaders = ('Stat', 'Last month', 'Last week', 'Last day')
        statisticsList['columns'] = [f'#{i}' for i in range(1, len(columnHeaders))]
        for i in range(len(columnHeaders)):
            statisticsList.heading(f'#{i}', text=columnHeaders[i])
            statisticsList.column(f'#{i}', anchor=tk.CENTER, width=70)

        # No of steps
        noOfSteps = list(('Number of steps',))
        noOfSteps = noOfSteps + [t.get_steps_from_subject(nr, username) for nr in [30, 7, 1]]
        statisticsList.insert('', tk.END, text=noOfSteps[0], values=noOfSteps[1:])

        # Activity time
        activityTime = list(('Activity time [min]',))
        activityTime = activityTime + [t.get_activity_from_subject(nr, username) for nr in [30, 7, 1]]
        statisticsList.insert('', tk.END, text=activityTime[0], values=activityTime[1:])

        # Distance walked
        distanceWalked = list(('Distance walked',))
        distanceWalked = distanceWalked + [t.get_distance_walked_from_subject(nr, username) for nr in [30, 7, 1]]
        statisticsList.insert('', tk.END, text=distanceWalked[0], values=distanceWalked[1:])

        # Falls
        falls = list(('Number of falls',))
        falls = falls + [t.get_falls_from_subject(nr, username) for nr in [30, 7, 1]]
        statisticsList.insert('', tk.END, text=falls[0], values=falls[1:])

        # List: Gait parameter
        gaitParameterList = g.rt.get_child("fact_parameters")
        gaitParameterList.delete(*gaitParameterList.get_children())

        columnHeaders = (
            'Parameter', 'Avg value last month', 'Avg value last week', 'Value last day', 'Variation last day')
        gaitParameterList['columns'] = [f'#{i}' for i in range(1, len(columnHeaders))]
        for i in range(len(columnHeaders)):
            gaitParameterList.heading(f'#{i}', text=columnHeaders[i])
            gaitParameterList.column(f'#{i}', anchor=tk.CENTER, width=70)

        for i, gaitParDef in enumerate(g.tool.configuration.gaitParameterDef):
            lastMonth = f'{t.get_parameter_from_subject(30, username, gaitParDef.name)} {gaitParDef.unit}' if abs(
                t.get_parameter_from_subject(30, username, gaitParDef.name)) < 10000 else ''
            lastWeek = f'{t.get_parameter_from_subject(7, username, gaitParDef.name)} {gaitParDef.unit}' if abs(
                t.get_parameter_from_subject(7, username, gaitParDef.name)) < 10000 else ''
            lastDay = f'{t.get_parameter_from_subject(1, username, gaitParDef.name)} {gaitParDef.unit}' if abs(
                t.get_parameter_from_subject(30, username, gaitParDef.name)) < 10000 else ''
            lastDayVariation = f'{t.get_parameter_from_subject(1, username, gaitParDef.name + " variation")} %' if abs(
                t.get_parameter_from_subject(1, username, gaitParDef.name + " variation")) < 10000 else ''
            gaitParameterList.insert('', tk.END, text=gaitParDef.name,
                                     values=(lastMonth, lastWeek, lastDay, lastDayVariation))


def command40_click():
    """
    Show frame to find best weights, if there are more than 2 components on selected FRI.
    """
    friList = g.rt.get_child("fri_list")
    if len(friList.get_children()) > 2:
        optiList = g.rt.get_child("opti_list")

        columnHeaders = ('Accuracy [%]', 'Pattern', 'Weight [%]', 'Min. impact [%]')
        optiList['columns'] = [f'#{i}' for i in range(1, len(columnHeaders))]
        for i in range(len(columnHeaders)):
            optiList.heading(f'#{i}', text=columnHeaders[i])
            optiList.column(f'#{i}', anchor=tk.CENTER, width=70)
    else:
        messagebox.showwarning(message="To start automatical value search, you need at least 2 parameters")


def command41_click():
    """
    Compute similar weights by iteratively randomizing components and checking if it's FRI reaches specified accuracy.
    """
    if float(g.rt.vars["text21"].get()) <= 0:
        messagebox.showinfo(message="Enter a minimum no of at least 1")
        return
    if float(g.rt.vars["text18"].get()) <= 0:
        messagebox.showinfo(message="Enter a minimum accuracy of at least 1")
        return

    list2 = g.rt.get_child("list2")
    if len(list2.curselection()) > 0:
        g.rtv.results = list()
        minNoOfResults = g.rt.vars["text21"].get()

        friNo = t.get_FRI_no(list2.get(tk.ACTIVE))
        buffComponents = copy.copy(g.tool.configuration.fallRiskIndex[friNo].components)
        components = copy.copy(g.tool.configuration.fallRiskIndex[friNo].components)

        cnt = 0
        details = list()
        good = 0
        while 1:
            cnt += 1
            random_values(components, g.tool.configuration.fallRiskIndex[friNo].redStart)
            g.tool.configuration.fallRiskIndex[friNo].components = components

            userNo = 0
            accuracy = 0
            for i, user in enumerate(g.tool.configuration.users):
                values = t.calc_FRI(i, list2.get(tk.ACTIVE), details)
                if len(values) > 0:
                    line = values[-1].split(",")
                    if user.faller.name == m.Faller.FALLER.name and float(line[1]) > g.tool.configuration.fallRiskIndex[
                        friNo].redStart:
                        accuracy += 1
                    elif user.faller.name == m.Faller.NON_FALLER.name and float(line[1]) <= \
                            g.tool.configuration.fallRiskIndex[friNo].greenEnd:
                        accuracy += 1
                    userNo += 1

            accuracy = round(accuracy / userNo * 100, ndigits=2)
            # good = 0
            if accuracy >= g.rt.vars["text18"].get():
                if not result_exists(g.rtv.results, components):
                    good += 1
                    newAccuracy = m.Accuracy(percent=accuracy, weights=components)
                    g.rtv.results.append(newAccuracy)
            # label57.text = cnt
            if good >= float(minNoOfResults):
                break

        g.tool.configuration.fallRiskIndex[friNo].components = buffComponents
        if len(g.rtv.results) > 0:
            optiList = g.rt.get_child("opti_list")
            for i, result in enumerate(g.rtv.results):
                optiList.insert('', tk.END, text=str(result.percent))
                for j, component in enumerate(components):
                    optiList.insert('', tk.END, values=(
                        result.weights[j].elementName, result.weights[j].weight, result.weights[j].impact))


def result_exists(results: list[m.Accuracy], components: list[m.Component]) -> bool:
    exists = False
    if len(results) > 0:
        for i, result in enumerate(results):
            for j, weight in enumerate(result.weights):
                if weight.impact != components[j].impact or weight.weight != components[j].weight:
                    exists = False
                    return exists

        exists = True
    return exists


def random_values(components: list[m.Component], redStart: float):
    random.seed()

    sum = 0
    for i in range(len(components)):
        if g.rt.vars["check3"].get() == True:
            components[i].impact = 0 if random.random() < 0.5 else redStart + 1
        components[i].weight = int(random.random() * 100)
        sum += components[i].weight

    sum2 = 0
    for i in range(len(components)):
        components[i].weight = round(components[i].weight / sum * 100, ndigits=2)
        sum2 += components[i].weight

    if sum2 > 100:
        for i in range(len(components)):
            if components[i].weight > sum2 - 100:
                components[i].weight = components[i].weight - (sum2 - 100)
                break
    elif sum2 < 100:
        for i in range(len(components)):
            if components[i].weight < sum2:
                components[i].weight = components[i].weight + (100 - sum2)
                break


def command32_click():
    list13 = g.rt.get_child("list13")
    list12 = g.rt.get_child("list12")
    atLeastUserSelected = len(list13.curselection()) > 0
    atLeastGaitParSelected = len(list12.curselection()) > 0

    if atLeastUserSelected and atLeastGaitParSelected:
        # grid stockchartx4
        load_daily_chart(g.rt.vars["check2"].get())
    else:
        if not g.rtv.resize:
            messagebox.showinfo(message="Please select at least one subject and one gait parameter")


def load_daily_chart(intraday: bool) -> bool:
    list13 = g.rt.get_child("list13")
    list12 = g.rt.get_child("list12")

    # subjects = list13.selection_get().split("\n")
    # parameters = list12.selection_get().split("\n")
    subjects = [list13.get(i) for i in list13.curselection()]
    parameters = [list12.get(i) for i in list12.curselection()]

    all = list()

    # Add charts for each parameter
    for parameter in parameters:
        for subject in subjects:
            if intraday:
                path = os.path.join(g.tool.myDocFolder, "configurations", g.tool.configuration.name, "subjects",
                                    t.get_id_from_name(subject), "parameter", "LastDate.txt")
                lastDate = t.get_str_from_file(path)
                if t.is_type_variation(parameter):
                    fileName = f'{lastDate.replace("/", "")}_{parameter[:-10]}.txt'
                else:
                    fileName = f'{lastDate.replace("/", "")}_{parameter}.txt'
                path = os.path.join(g.tool.myDocFolder, "configurations", g.tool.configuration.name, "subjects",
                                    t.get_id_from_name(subject), "parameter", "intraday", fileName)
                arr = t.get_arr_from_file(path)
                dataColumn = 1
            else:
                if t.is_type_variation(parameter):
                    path = os.path.join(g.tool.myDocFolder, "configurations", g.tool.configuration.name, "subjects",
                                        t.get_id_from_name(subject), "parameter", "daily", f'{parameter[:-10]}.txt')
                    dataColumn = 2
                else:
                    path = os.path.join(g.tool.myDocFolder, "configurations", g.tool.configuration.name, "subjects",
                                        t.get_id_from_name(subject), "parameter", "daily", f'{parameter}.txt')
                    dataColumn = 1
                arr = t.get_arr_from_file(path)
            if len(arr) > 0:
                all = t.add_to_all(all, arr, dataColumn, intraday, True)

    if len(all) > 0:
        cnt = 0
        plotNr = 1
        fig = Figure(figsize=(7, 6), dpi=100)
        for parameter in parameters:
            ax = fig.add_subplot(len(parameters), 1, plotNr)
            plotNr += 1
            ax.set_title(label=f'{parameter}_{"|".join(subjects)}')
            for subject in subjects:
                values = [elem.value for elem in all[cnt]]

                cnt += 1

                ax.plot(values)

            # cnt += 1

        parent = g.rt.get_child("stockchartx4", g.rt.patternExtraction)
        figCanvas = FigureCanvasTkAgg(fig, master=parent)
        figCanvas.draw()

        toolbar = NavigationToolbar2Tk(figCanvas, parent, pack_toolbar=False)
        toolbar.update()

        toolbar.grid(row=2, column=0)
        figCanvas.get_tk_widget().grid(row=0, column=0)


def command13_click():
    """Show sensor selector window, set to add new column"""
    g.rt.sensorSelectorVars["text1"].set("")
    g.rt.sensorSelectorVars["text2"].set("")
    g.rtv.sensorSelector.newSensor = True
    g.rt.sensorSelector.wm_deiconify()


def command12_click():
    """Show sensor selector window, set to edit selected column"""
    form_load_sensor_selector()
    marker = -1
    selectedItem = g.rt.get_child("list9").curselection()
    if len(selectedItem) > 0:
        marker = selectedItem[0]
    if marker > -1:
        g.rt.sensorSelectorVars["text1"].set(g.tool.configuration.columns[marker])
        g.rt.sensorSelectorVars["text2"].set(g.tool.configuration.columnUnit[marker])
        g.rt.get_child("combo1", root=g.rt.sensorSelector).current(marker)
        g.rt.get_child("combo2", root=g.rt.sensorSelector).current(marker)
        g.rtv.sensorSelector.newSensor = False
        g.rt.sensorSelector.wm_deiconify()


def command11_click():
    """Remove Column (and columnType, columnOption, columnUnit) selected (Data input selection)"""
    if len(g.tool.configuration.columns > 0):
        list9 = g.rt.get_child("list9")
        list9Selection = list9.curselection()
        list9Index = list9Selection[0] if len(list9Selection) > 0 else -1
        if list9Index > -1:
            list9.delete(list9Index)
            g.tool.configuration.columns.pop(list9Index)
            g.tool.configuration.columnType.pop(list9Index)
            g.tool.configuration.columnOption.pop(list9Index)
            g.tool.configuration.columnUnit.pop(list9Index)
            update_list()
            update_sensors()
            check_for_time_column()
            g.tool.configuration.changed = True
            g.tool.configuration.coreChange = True


def update_sensors():
    arr = g.tool.configuration.sensorToWatch.split("|")
    list14 = g.rt.get_child("list14")
    list14.delete(0, tk.END)
    for i in range(len(g.tool.configuration.columns)):
        if g.tool.configuration.columnType[i] not in [0, 1]:
            list14.insert(tk.END, g.tool.configuration.columns[i])
            if g.tool.configuration.columns[i] in arr:
                list14.selection_set(tk.END)


def command1_click():
    """Add new gait parameter to the configuration"""
    marker = False

    paraName = simpledialog.askstring("Please enter a name for the gait parameter", "Gait parameter name:")
    if paraName != "" and paraName is not None:
        if " " in paraName:
            messagebox.showerror(message="Parameter cannot contain 'space' character'")
            return
        for i, gaitParDef in enumerate(g.tool.configuration.gaitParameterDef):
            if paraName.lower() == gaitParDef.name.lower():
                marker = True
                break
        if marker:
            messagebox.showerror(message="This gait parameter name already exists. Please choose another one")
            return

        g.rtv.noChange = True
        newGaitParDef = m.GaitDef(name=paraName)
        g.tool.configuration.gaitParameterDef.append(newGaitParDef)
        g.rt.get_child("list1").insert(tk.END, paraName)
        g.tool.configuration.changed = True
        g.tool.configuration.coreChange = True
        g.rtv.noChange = False
        update_parameter_data()
        add_gait_parameter_to_users(paraName)


def command2_click():
    list1 = g.rt.get_child("list1")
    if len(list1.curselection()) > 0:
        list1Index = list1.curselection()[0]
        paraName = simpledialog.askstring("Serene GAT", "Please enter a new name for the gait parameter")
        if paraName != "" and paraName is not None:
            marker = -1
            for i, gaitParDef in enumerate(g.tool.configuration.gaitParameterDef):
                if i != list1Index:
                    if paraName.lower() == gaitParDef.name.lower():
                        marker = i
                        break
            if marker > -1:
                messagebox.showerror(message="This gait parameter already exists. Please choose another one")
            oldName = g.tool.configuration.gaitParameterDef[list1Index].name
            g.tool.configuration.gaitParameterDef[list1Index].name = paraName
            list1.delete(list1Index)
            list1.insert(tk.END, paraName)
            g.tool.configuration.changed = True
            update_parameter_data()
            change_gait_parameter_to_users(oldName, paraName)


def command3_click():
    list1 = g.rt.get_child("list1")
    if len(list1.curselection()) > 0:
        list1Index = list1.curselection()[0]
        name = list1.get(tk.ACTIVE)

        g.tool.configuration.gaitParameterDef[list1Index].pop()
        list1.delete(list1Index)

        g.tool.configuration.changed = True
        list1_click()
        update_parameter_data()
        remove_gait_parameter_to_users(name)


def update_parameter_data():
    """"""
    list12 = g.rt.get_child("list12")
    list15 = g.rt.get_child("list15")
    list12.delete(0, tk.END)
    list15.delete(0, tk.END)
    for gaitParDef in g.tool.configuration.gaitParameterDef:
        # if gaitParDef.active:
        list12.insert(tk.END, gaitParDef.name)
        list12.insert(tk.END, f'{gaitParDef.name} variation')
        list15.insert(tk.END, gaitParDef.name)


def add_gait_parameter_to_users(name: str):
    for i, user in enumerate(g.tool.configuration.users):
        g.tool.configuration.users[i].gaitParameter.append(m.GaitParameterType(name=name))


def exchange_gait_parameter_from_users(index1: int, index2: int):
    for i in range(len(g.tool.configuration.users)):
        if len(g.tool.configuration.users[i].gaitParameter) > 0:
            para = g.tool.configuration.users[i].gaitParameter[index1]
            g.tool.configuration.users[i].gaitParameter[index1] = g.tool.configuration.users[i].gaitParameter[index2]
            g.tool.configuration.users[i].gaitParameter[index2] = para


def remove_gait_parameter_to_users(name: str):
    for i, user in enumerate(g.tool.configuration.users):
        if len(user.gaitParameter) > 0:
            try:
                marker = user.gaitParameter.index(name)
            except ValueError:
                marker = -1

            if marker > -1:
                g.tool.configuration.users[i].gaitParameter.pop(marker)


def change_gait_parameter_to_users(oldName: str, paraName: str):
    for i, user in enumerate(g.tool.configuration.users):
        for j, gaitParam in enumerate(g.tool.configuration.users[i].gaitParameter):
            if gaitParam.name == oldName:
                g.tool.configuration.users[i].gaitParameter[j] = paraName
                break

        for j, showParameter in enumerate(g.tool.configuration.users[i].showParameter):
            if showParameter == oldName:
                g.tool.configuration.users[i].showParameter[j] = paraName
                break
