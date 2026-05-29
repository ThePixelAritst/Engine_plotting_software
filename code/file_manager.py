# library dependancies
import os
import time
import re
import typing
from pathlib import Path
import csv
import ast
# internal imports
import program_settings as sett
datset = sett.data_settings
genset = sett.general_settings

# data handling portion, works with an already open file object to file, read, and otherwise work with file contents
class Data():
    file: typing.TextIO

    # --- WORKING FUNCTIONS --- 
        # 
    def _initialize_function_dispatch(self):
        self.writer_set = {"csv": self._write_csv} 
        self.row_reader_set = {"csv": self._readrow_csv,"txt": self._readrow_txt}
        self.column_reader_set = {"csv": self._readcolumns_csv}

    def _initialize_write_csv(self):
        self.csv_writer = csv.writer(self.file, delimiter=datset.CSV_DELIMITER)
        self.init_csv[0] = True
        
    def _initialize_read_csv(self):
        self.csv_reader = csv.reader(self.file, delimiter=datset.CSV_DELIMITER)
        self.init_csv[1] = True

    def _lock_file_content(self):
        self.allow_write = False


    # --- CSV FUNCTIONS ---
    def _write_csv(self,row_content):
        self.csv_writer.writerow(row_content)

    def _readrow_csv(self,row_number,include_header=False):
        if not include_header:
            row_number += self.header_length
        self.file.seek(0)
        row = list(self.csv_reader)[row_number]
        self.file.seek(0)
        return tuple(row)
    
    def _readcolumns_csv(self,selected_collumns,max_length=None): # reads the selected column without header
        self.file.seek(0)
        if not isinstance(selected_collumns,(tuple,list,int)):
            raise TypeError(f"Cannot interpret '{type(selected_collumns)}' as a collumn index!")
        if type(selected_collumns) == int:
            selected_collumns = (selected_collumns,)
        if isinstance(selected_collumns,(tuple,list)) and not selected_collumns:
            raise ValueError(f"List or tuple cannot be empty!")
        if (max(selected_collumns) or len(selected_collumns)) >= len(self.read_row(0)):
            raise IndexError(f"Requested column index outside row margins")
            
        if not max_length or int(max_length) > len(list(self.csv_reader))-self.header_length:
            max_length = len(list(self.csv_reader))-self.header_length
            print(max_length)

        collumn_list = {col: [] for col in selected_collumns}
        for row_pointer in range(max_length):
            row = self.read_row(row_pointer)
            for collumn in selected_collumns:
                collumn_list[collumn].append(row[collumn])

        return collumn_list
    
    # --- TXT FUNCTIONS --- 
    # NO TEXT WRITE, DO NOT ALLOW CREATION OF TXT FILES, ALLOW OPENING OF TXT FILES, BUT NOT WRITING

    def _readrow_txt(self,row,include_header): # does not work, likely
        self.file.seek(0)
        list_of_rows = self.file.readlines()
        if not include_header:
            row += self.header_length
            self.data_rows = len(list_of_rows) - self.header_length
        else:
            max_header = len(list_of_rows)
        returning_value = ast.literal_eval(list_of_rows[row])
        return returning_value
        
    # --- VISIBLE AND ACCESSIBLE METHODS ---
    def get_maximum_data_index(self,include_header=False):
        self.file.seek(0)
        if not include_header:
            return (len(list(self.file)) - self.header_length)
        else: return len(list(self.file))

    def write(self,tuple_of_values=None):
        if not self.allow_write:
            raise RuntimeError("Cannot write to file! File must be newly created to allow write!")
        elif not tuple_of_values != tuple:
            raise ValueError("Inputed value is not a tuple and thus cannot be writen!")
        elif self.format == "csv" and not self.init_csv[0]:
            self._initialize_write_csv()
        self.writer_set[self.format](tuple_of_values)

    def read_row(self,row_number,include_header=False):
        if row_number > self.get_maximum_data_index(include_header):
            raise IndexError("Cannot access Index outside of file!")
        if self.format == "csv" and not self.init_csv[1]:
            self._initialize_read_csv()
        returned_row = self.row_reader_set[self.format](row_number,include_header)
        return returned_row
    
    # --- CLASS INITIALIZATION ---
    def _get_header_length(self):
        if self.format == "txt":
            return self.header_length
        
        pointer = 0
        try:
            while self.read_row(pointer,include_header=True)[0] == "#":
                pointer += 1
        finally: 
            return pointer

    def _write_header(self):
        self.write(("#","SOFTWARE",genset.VERSION_SOFTWARE))
        self.write(("#","PARSER",genset.VERSION_PARSER))
        self.write(("#","RECEIVER",genset.VERSION_RECEIVER))
        

    def _initialize_txt(self):
        self.header_length = 1
    
    def __init__(self,opened_file: typing.TextIO,format,newfile):
        if opened_file is None or opened_file.closed:
            raise ValueError(f"Expected an open file object, got: {opened_file!r}!")
        self.file = opened_file
        self.format = format
        self._initialize_function_dispatch()
        self.allow_write = newfile
        if format == "csv":
            self.init_csv= [False,False]
            if newfile:
                self._write_header()
            self.header_length = self._get_header_length()
        else:
            self._initialize_txt()


# ---- FILE HANDLING ----

# Handles file creating, opening, closing and renaming of a data file.
# Does not handle the data in the file.
# Ensures handling of the data inside the file can be done smoothly.
class File(Data):

    def _is_valid_filename(self,filename):
        try:
            if re.search(r'[<>:"/\\|?*]',filename): # or not str(filename).isascii()
                print("Name cannot contain forbidden characters'")
                raise ValueError()
            elif Path.exists(os.path.join(self.folder_directory,f"{filename}.{self.format}")):
                print("Cannot rename, File with same name already exists!")
                raise ValueError()
        except ValueError: return False
        else: return True 

    def _create_file(self): #creates file
        if self.file_open:
            raise RuntimeError("Cannot create secondary file in one class instance'")
        self.file_open = True
        self.file_name = time.strftime("%Y-%m-%d--%a--%H-%M-%S")
        if datset.DEBUG_MODE:
            folder = datset.DEBUG_DIRECTORY
        else:
            folder = "data"
        self.folder_directory = os.path.join(Path(__file__).resolve().parents[1],folder)
        self.format = "csv"
        self.new_file = True
        self.full_path = os.path.join(self.folder_directory,f"{self.file_name}.csv")
        self.file = open(self.full_path,"x+",newline='')

    def _close_file(self,report_closed=True):
        self.file.close()
        self.file_open = False
        if report_closed:
            print(f"File {self.file_name}.{self.format} was closed.")

    def _open_file(self, handover=None):
        if self.file_open:
            raise RuntimeError("Cannot open secondary file in one class instance!")
        elif handover:
            self.full_path = handover
        else:
            attempt = 0
            while attempt < genset.MAX_WATCHDOG:
                try:
                    unconfirmed_path = input("Please input file to be opened:\n")
                    if not( Path(unconfirmed_path).exists() and Path(unconfirmed_path).is_file()):
                        raise ValueError()
                    else:
                        self.full_path = unconfirmed_path
                        break
                except Exception:
                    attempt += 1
                    print(f"\nInvalid or unreadable file. Attempt {attempt}/{genset.MAX_WATCHDOG}")
                finally:
                    if attempt >= genset.MAX_WATCHDOG:
                        exit("Watchdog exceeded, terminating program.\n\n")

        full_name = (os.path.basename(self.full_path).split()[-1]).split(".")                
        self.format = full_name[-1]
        self.file_name = full_name[0]
        self.folder_directory = Path(self.full_path).resolve().parent
        self.new_file = False
        if self.format == "txt":
            print(f"WARNING: opening a 'txt' format file. This is no longer a supported format. Please convert this file to {datset.DEFAULT_FORMAT}")
            open_mode = "r"
        else:
            open_mode = "a+"
        self.file = open(self.full_path,open_mode,newline='\n')

    def rename(self):
        watchdog = 0
        old_name = self.file_name

        while watchdog < genset.MAX_WATCHDOG:
            chosen_name = input("Please input a new name for the file.\n")
            if self._is_valid_filename(chosen_name,self.folder_directory,self.format):
                self.file_name = chosen_name
                break
            else:
                watchdog += 1
                print(f"\nEncountered error while renaming file. Please try again! Attempt {watchdog}/{genset.MAX_WATCHDOG}")
                if watchdog >= genset.MAX_WATCHDOG:
                    exit("\nWatchdog exceeded, terminating program.\n\n")

        self._close_file(report_closed=False)
        new_file_path = os.path.join(self.folder_directory,f"{chosen_name}.{self.format}")
        os.rename(self.full_path,new_file_path)
        self.full_path = new_file_path
        self.file_name = chosen_name
        self._open_file(handover=self.full_path)
        print(f"Renamed '{old_name}.{self.format}' to '{chosen_name}.{self.format}'")         
        
    def __init__(self,open_file=True,handover_path=None):
        self.file_open = False
        if open_file: 
            self._open_file(handover=handover_path)
        else:
            self._create_file()
        if not hasattr(self, 'file') or self.file is None:
            raise RuntimeError("File not created, cannot initiate Data Class")
        print(f"File '{self.file_name}.{self.format}' was initiated successfully.\n")
        super().__init__(self.file, format=self.format, newfile=self.new_file)

open_file = File(open_file=True,handover_path="/home/pixel/Documents/coding/Compressed-air-engine-python-part/testing_directory/2026-05-25--Mon--13-47-48.csv")
try:
    for iteration in range(20):
        open_file.write((iteration,iteration*2,iteration*3))
        print("write n.:",iteration)
except Exception:
    print("Cannot write to file!")
print(open_file._get_header_length())
print(open_file.read_row(1,True))
print(open_file.read_row(1))
columns = (0,1,2)
list = open_file._readcolumns_csv(columns)
print(list)