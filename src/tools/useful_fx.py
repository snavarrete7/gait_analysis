import glob
import os
from typing import TypeVar
import uuid

from datetime import date, datetime
import linecache

#generic type for generic functions
T = TypeVar("T")

#GUI
def hide_form():
    pass

def save_str_to_file(path: str, value: str):
    """
    Stores value in file. Overwrites previous content. If doesn't exist, creates file.
    """
    with open(path, "w") as file:
        file.write(value)

def append_str_to_file(path: str, value: str):
    """
    Appends value in end of file, IN A NEW LINE. If doesn't exist, creates file.
    """
    with open(path, "a") as file:
        #warning: \n (Lf) or \r\n (CrLf)
        file.write(value+"\n")

def save_arr_to_file(path: str, values: list[str]):
    """
    Store each string in a separate line to a file. If doesn't exist, create file.
    """
    with open(path, "w") as file:
        file.writelines(values)

def append_arr_to_file(path: str, values: list[str]):
    """
    Appends a line for each value in end of file. If doesn't exist, creates file.
    """
    with open(path, "w") as file:
        file.writelines(values)

def get_str_from_file(path: str) -> str:
    """
    Return contents of file as one single string.
    """
    try:
        with open(path, "r") as file:
            return file.read().strip()
    except FileNotFoundError as err:
        print(f"Could not open file: [{path}]. Err:  {err.strerror}")

def get_limited_str_from_file(path: str, limit: int) -> str:
    """
    Get contents of file from begginning up until limit (amount of lines) as one single string.

    WARNING: VB6 CODE reads always 20 lines, ignores limit.
    """
    try:
        with open(path, "r") as file:
            res = ""
            for i in range(limit):
                res = res + file.readline()
            return res
    except FileNotFoundError as err:
        print(f"get_limited_str_from_file - Could not open file: [{path}]. Err:  {err.strerror}")

def get_arr_from_file(path: str) -> list[str]:
    """
    Reads content of file and returns a list with each line.

    If file doesn't exist it's logged.
    """
    try:
        with open(path, "r") as file:
            read_data = file.readlines()
            lines = [line.removesuffix("\n") for line in read_data]
            return lines
    except FileNotFoundError as err:
        print(f"get_arr_from_file - Could not open file: [{path}]. Err:  {err.strerror}")
        return []

def kzp(string: str) -> str:
    """
    Replace commas with dots.
    """
    return string.replace(",", ".")

def pzk(string: str) -> str:
    """
    Replace dots with commas.
    """
    return string.replace(".", ",")

# TODO: return full path, not basename path
def get_file_list_from_path(path: str, extension: str = "*") -> list[str]:
    """
    Returns a list where each element is the filename in directory 'path'. Can be filtered by file extension (i.e. '.txt' for instance)

    Hint: use [os.path.basename(p) for p in listOfFullPaths] to extract just filename. 
    """
    try:
        res = []
        for file in os.listdir(path):
            if file.endswith(extension) or extension == "*":
                res.append(os.path.join(path, file))
        return res
    except FileNotFoundError as err:
        print(f"get_file_list_from_path - Could not open file: [{path}]. Err:  {err.strerror}")

def file_exists(path: str) -> bool:
    """
    Check if file or directory exists.
    """
    return os.path.exists(path)

def folder_exists(path: str) -> bool:
    """
    Alias for "file exists". Simply pass path to directory.
    """
    return file_exists(path)

def delete_file(path: str):
    """
    Check if file exists, then deletes. No errors will be thrown either way.

    Deletes either file or directory.
    """
    if file_exists(path):
        os.remove(path)

# TODO: add test for full and relative paths
def rename_file(path: str, newName: str):
    """
    Rename file at 'path' with the new name.
    """
    filePath, fileName = os.path.split(path)
    newFilePath = f"{filePath}{newName}"
    os.rename(path, newFilePath)

def safe_file_name(fileName: str) -> str:
    keepcharacters = (' ', '.', '_')
    return "".join(c for c in fileName if c.isalnum() or c in keepcharacters).rstrip()

def is_safe_ascii_name(name: str) -> bool:
    return name.isascii()

def get_date_from_str(string: str) -> date:
    """
    Returns a date from a string with format "MM/DD/YYYY"
    """
    resDatetime = datetime.strptime(string, "%m/%d/%Y")
    return resDatetime.date()

def is_date_str(string: str) -> bool:
    """
    Check if string is date format MM/DD/YYYY
    """
    try:
        get_date_from_str(string)
        return True
    except ValueError as err:
        return False
    except AttributeError as err:
        return False

#arreglar cosa de clase "datetime" a "datetime.datetime" y "date" a "datetime.date"

def get_str_from_date(d: date) -> str:
    """
    Converts a date to string with format "MM/DD/YYYY"
    """
    return d.strftime("%m/%d/%Y")

#GUI
def set_window_focus():
    pass

#GUI
def get_window_info():
    pass

def is_array_empty(arr: list[str]) -> bool:
    return not arr

def is_str_in_array(array: list[str], symbol: str) -> bool:
    """
    Checks if symbol exists in array
    """
    return symbol in array

#GUI
def modal_behavior_alt():
    pass

#GUI
def modal_behavior():
    pass

# TODO: check if generated key exists... somewhere. A statis key arr is in function... idk when it's populated
def unique_key() -> str:
    """
    Has been changed to produce a UUID, no longer checking if key already somewhere...
    """
    return str(uuid.uuid4())

#GUI
def get_window_handle():
    pass

#GUI
def save_window_position():
    pass

#GUI
def set_window_position():
    pass

def add_to_array(arr: list[T], element: T):
    """
    Substitution to previous 'addStrToFile, addDblToFile...'
    """
    arr.append(element)

def join_arrays(arr1: list, arr2: list):
    """
    Modifies arr1 to be the concatenation of both lists.

    Arrays were previously just of type Double. Now any type.
    """
    arr1.extend(arr2)

def remove_from_arr(arr: list, index: int):
    """
    Delete item at index 'index'. If arr is empty, nothing is done.
    """
    if not is_array_empty(arr):
        try:
            arr.pop(index)
        except IndexError as err:
            print(f"remove_from_arr - err deleting at index {index} from array: {arr}")

def get_path(path: str) -> str:
    """
    Gets path 'head' (all except filename) from a given absolute 'path'
    """
    return os.path.dirname(path)

def split_bo4(expression: str, delimiter = ",") -> list[str]:
    """
    Alias of split string. Second input parameter (result) is now returned instead (list[str]).
    
    This was a Sub
    """
    return expression.split(sep=delimiter)

def save_path(path: str) -> str:
    """
    Returns the same path with removed '@', '/' and '\'
    """
    res = path.replace("@", "")
    res = res.replace("/", "")
    return res.replace("\\", "")

def rem_k(string: str) -> str:
    """
    If string is not empty, returns string with removed trailing ']' (if present)
    """
    if len(string) > 0 and string[-1] == "]":
        return string[:-1]
    else:
        return string

def arr_has_date(arr: list[str], date: date) -> int:
    """
    Returns index of 'date' searching in 'arr' (lines of string, date should be at beggining of each line). If not found return -1
    """
    dateStr = get_str_from_date(date)
    for i, line in enumerate(arr):
        if line.startswith(dateStr):
            return i
    return -1

def is_type_variation(name: str) -> bool:
    """
    Checks if given 'name' contains substring 'variation' at the end (right).
    """
    if len(name) < 10:
        return False
    return True if name[-9:] == "variation" else False

def get_limited_str_from_file(path: str, limit: int) -> str:
    """
    Alias to get_str_from_file.

    It originally was for getting first 'limit' characters, but apparently not implemented... instead gets first 20 characters.
    """
    return get_str_from_file(path)

def unreadable(name: str) -> str:
    """
    Converts each character in name to it's unicode code point as a string
    """
    res = ""
    for char in name:
        res = res + str(ord(char))
    return res

def count_file_lines(filePath: str) -> int:
    """
    Count file lines in big file. Returns -1 if file not found
    """

    def blocks(files, size=65536):
        while True:
            b = files.read(size)
            if not b: break
            yield b
    try:
        with open(filePath, "r",encoding="utf-8",errors='ignore') as f:
            return sum(bl.count("\n") for bl in blocks(f))
    except FileNotFoundError as err:
        print("count_file_lines - file {filePath} not found")
        return -1

def read_file_line(filePath: str, startRow: int) -> str:
    """
    Read line at row 'startRow' in file 'filePath'.
    
    If line is too big or file not found, return empty string.
    """
    return linecache.getline(filePath, startRow).rstrip()