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

