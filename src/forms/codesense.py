import importlib
import src.model.globalvars as g
import src.model as m
import src.tools as t
import os
#import app.codesense.gait as Gait
import sys
import types
from tkinter import messagebox

Gait = m.Gait()

def save_function(rawFunction: str, gaitParameterName: str):
    """
    Append in front the import to be able to use Gait (import src.forms.codesense as c)
    """
    path = os.path.join(g.rtv.app.path, "codesense")
    if not t.folder_exists(path):
        os.makedirs(path, mode=777)
    
    filePath = os.path.join(path, f'{gaitParameterName}.py')

    #Añadir algun import a "rawFunction", porque sino no reconoce la variable "Gait". Ejemplo:
    # eloel = "eloel"

    # def StrideTime():
    #     print(eloel)

    #Otra solucion seria reemplazar todas las ocurrencias de "Gait" por "cs.Gait" (y meter en la primera linea "import app.codesense as cs")

    #add 1 tab to each line
    lines = rawFunction.split("\n")
    rawFunctionTabbed = [f'\t{line}' for line in lines]

    insertedImportStatement = "import src.forms.codesense as c\nimport math\n"
    insertedFunctionHeader = f'def {gaitParameterName}():\n'
    rawFunctionTabbed = insertedImportStatement + insertedFunctionHeader + "\n".join(rawFunctionTabbed)

    with open(filePath, 'w') as file:
        file.write(rawFunctionTabbed)
    
def execute_function(gaitParameterName: str):
    """
    Imports function defined in script, and executes. Will prompt with a message box if there is an error in the function.
    """
    #Refresh package (by name) cache
    loaded_package_modules = dict([
        (key, value) for key, value in sys.modules.items()
        if key.startswith(gaitParameterName) and isinstance(value, types.ModuleType)
    ])
    for key in loaded_package_modules:
        del sys.modules[key]

    #execute function
    try:
        appDirectoryName = os.path.basename(g.rtv.app.path)
        gaitParameterModule = importlib.import_module(f'{appDirectoryName}.codesense.{gaitParameterName}')
        gaitParameterFunction = getattr(gaitParameterModule, gaitParameterName)
        gaitParameterFunction()
        messagebox.showinfo(message="Ran successfully!")
    except SyntaxError as err:
        messagebox.showerror(message=f"Syntax error: {err}")
    except ImportError as err:
        messagebox.showerror(message=f"Import error: {err}")
    except NameError as err:
        messagebox.showerror(message=f"Unable to reference a variable in the script. Full error: {err}")

def get_calculated_gait_parameters() -> list[list[float]]:
    return Gait._sensor_data

def set_gait(gait: m.Gait):
    Gait = gait