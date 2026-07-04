# library dependancies
import os
import time
import re
import typing
from pathlib import Path
import csv
import ast
# internal imports
import keyboard_controller as keco
import program_settings as sett
datset = sett.data_settings
genset = sett.general_settings

# data handling portion, works with an already open file object to file, read, and otherwise work with file contents
class Data():
    file: typing.TextIO

    # --- WORKING FUNCTIONS --- 
        # functions which shouldnt be accessed from outside, but are essential for functioning of the program
    def _initialize_function_dispatch(self):
        self.writer_set = {"csv": self._write_csv} 
        self.row_reader_set = {"csv": self._readrow_csv,"txt": self._readrow_txt}
        self.column_reader_set = {"csv": self._readcolumns_csv, "txt": self._readcolumns_txt}
        self.max_index_set = {"csv": self._max_data_index_csv, "txt": self._max_data_index_txt}

    def _initialize_write_csv(self):
        self.csv_writer = csv.writer(self.file, delimiter=datset.CSV_DELIMITER)
        self.init_csv["writer"] = True
        
    def _initialize_read_csv(self):
        self.csv_reader = csv.reader(self.file, delimiter=datset.CSV_DELIMITER)
        self.init_csv["reader"] = True

    def _lock_file_content(self):
        self.allow_write = False
    
    def _check_column_validity(self,columns):
        if not isinstance(columns,(tuple,list,int)):
            raise TypeError(f"Cannot interpret '{type(columns)}' as a collumn index!")
        if type(columns) == int:
            columns = (columns,)
        if isinstance(columns,(tuple,list)) and not columns:
            raise ValueError(f"List or tuple cannot be empty!")
        return columns


    # --- CSV FUNCTIONS ---
        # functions for .csv fileset, primary functions which operate with the data
    def _max_data_index_csv(self,include_header=False):
        self.file.seek(0)
        if not include_header:
            return (len(list(self.file)) - self.header_length)-1
        else: return len(list(self.file))-1

    def _write_csv(self,row_content):
        self.csv_writer.writerow(row_content)

    def _readrow_csv(self,row_number,include_header=False,return_float=True):
        if not include_header:
            row_number += self.header_length
        self.file.seek(0)
        row = list(self.csv_reader)[row_number]
        self.file.seek(0)
        if return_float:
            return tuple(map(float,row))
        else:
            return tuple(row)
    
    def _readcolumns_csv(self,selected_collumns,max_length=None):
        # reads the selected column without header
        self.file.seek(0)
        selected_collumns = self._check_column_validity(selected_collumns)
        if (max(selected_collumns) or len(selected_collumns)) >= len(self.read_row(0)):
            raise IndexError(f"Requested column index outside row margins!")
            
        if not max_length or int(max_length) > len(list(self.csv_reader))-self.header_length:
            max_length = self.get_maximum_data_index() + 1

        column_dict = {col: [] for col in selected_collumns}
        for row_pointer in range(max_length):
            row = self.read_row(row_pointer)
            for collumn in selected_collumns:
                column_dict[collumn].append(row[collumn])

        return column_dict
    

    # --- TXT FUNCTIONS --- 
        # secondary functions for the outdated .txt file and data handling. These are not as thouroughly tested
        # !!! Collums go along a horizontal list, rows go verical between the two data lists. 
        # .txt does not allow writing to file, and no writing functions should ever exist
    def _valid_txt_header(self):
        self.file.seek(0)
        file_content = self.file.readlines()
        header = ast.literal_eval(file_content[0])
        if (len(header) != 2) or (header[0] != header[1]) or (type(header[0]) != int):
            return False
        else:
            return True
    
    def _max_data_index_txt(self,*args):
        return self._readrow_txt(include_header=True)[0]-1
    
    def _readcolumns_txt(self,columns,max_length=None): # reads whole list on a given horizontal line - csv equivalent to column
        columns = self._check_column_validity(columns)
        self.file.seek(0)
        file_content = self.file.readlines()
        read_from_collums = []

        for column in columns:
            read_from_collums.append(column + self.header_length)
        if (max(read_from_collums) or len(read_from_collums)) >= len(file_content):
            raise IndexError(f"Requested column index outside row margins!")
        
        read_limit = max_length
        return_dict = {col: [] for col in columns}
        for current_column in read_from_collums:
            literal_list = ast.literal_eval(file_content[current_column])
            if not max_length:
                read_limit = len(literal_list)
            return_dict[current_column-self.header_length] = (literal_list[:read_limit])
        return dict(return_dict)
    
    def _readrow_txt(self,row=0,include_header=False,return_float=True): # reads both lists' values with the same index - csv equivalent to row
        if not self._valid_txt_header():
            raise ValueError("Unknown '.txt' file data format!")
        self.file.seek(0)
        file_content = self.file.readlines()
        header = ast.literal_eval(file_content[0])
        if include_header:
            return tuple(header)
        desired_rows = (0,1) # the rows it reads are hard set due to the nature .txt data formatting
        returning_row = []
        data = self.read_column(desired_rows)
        for current_item in data:
            returning_row.append(data[current_item][row])
        if return_float:
            return tuple(map(float,returning_row))
        else:
            return tuple(returning_row)
            

    # --- VISIBLE AND ACCESSIBLE METHODS ---
        # methods meant to be accessed from outside the class structure

    def get_maximum_data_index(self,include_header=False):
        return self.max_index_set[self.format](include_header)
    
    def is_write_allowed(self):
        if self.allow_write: return True
        else: return False

    def write(self,tuple_of_values=None):
        """Input a tuple to save to file. Each tuple value is one collumn"""
        if not self.allow_write:
            raise PermissionError("Cannot write to file! File must be newly created to allow write!")
        if not tuple_of_values != tuple:
            raise ValueError("Inputed value is not a tuple and thus cannot be writen!")
        if self.format == "csv" and not self.init_csv["writer"]:
            self._initialize_write_csv()
        self.file.seek(0,2)
        self.writer_set[self.format](tuple_of_values)

    def read_row(self,row_number,include_header=False,return_as_float=True):
        """Reads a row from file and returns it as a tuple object"""
        if self.format == "csv" and not self.init_csv["reader"]:
            self._initialize_read_csv()
        if row_number > self.get_maximum_data_index(include_header):
            raise IndexError("Cannot access Index outside of file!")
        returned_row = self.row_reader_set[self.format](row_number,include_header,return_as_float)
        return returned_row
    
    def read_column(self,columns=(0,1),max_length=None):
        return dict(self.column_reader_set[self.format](columns,max_length))

    # --- CLASS INITIALIZATION ---

    def _get_header_length(self,denominator=datset.DEFAULT_HEADER_DENOMINATOR):
        if self.format == "txt":
            return self.header_length
        pointer = 0
        while True:
            try:
                row = self.read_row(pointer,include_header=True,return_as_float=False)
            except IndexError: # if the file is only header lines, it would otherwise go out of range
                break
            if row[0] != denominator: # denominator - sign at the start of every header line
                break
            pointer += 1
        return pointer

    def _write_header(self): # outputs header, which is present at the start of every newly created file
        self.write(("#","SOFTWARE",genset.VERSION_SOFTWARE))
        self.write(("#","PARSER",genset.VERSION_PARSER))
        self.write(("#","RECEIVER",genset.VERSION_RECEIVER))
        self.write(("#","CREATION_DATE",time.strftime("%Y/%m/%d--%H:%M:%S"),"YYYY/MM/DD--HH:MM:SS"))
        self.write(("#","RPM","TIME"))
        

    def _initialize_txt(self):
        self.header_length = 1
    
    def __init__(self,opened_file: typing.TextIO,format,newfile):
        if opened_file is None or opened_file.closed:
            raise ValueError(f"Expected an open file object, got: {opened_file!r}, with type: {type(opened_file)}!")
        self.file = opened_file
        self.format = format
        self._initialize_function_dispatch()
        self.allow_write = newfile
        if format == "csv":
            self.init_csv= {"reader": False, "writer": False}
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
                print("Name cannot contain forbidden characters!'")
                raise ValueError()
            elif os.path.exists(os.path.join(self.folder_directory,f"{filename}.{self.format}")):
                print("Cannot rename, File with same name already exists!")
                raise ValueError()
        except ValueError: return False
        else: return True 

    def _create_file(self): #creates file
        if self.file_open:
            raise RuntimeError("Cannot create secondary file in one class instance!")
        self.file_open = True
        self.file_name = time.strftime("%Y-%m-%d--%a--%H-%M-%S")
        if datset.DEBUG_MODE:
            folder = datset.DEBUG_DIRECTORY
        else:
            folder = "data"
        self.folder_directory = os.path.join(Path(__file__).resolve().parents[1],folder)
        self.format = "csv"
        self.new_file = True
        self.full_path = os.path.join(self.folder_directory,f"{self.file_name}.{self.format}")
        self.file = open(self.full_path,"x+",newline='')

    def _close_file(self,report_closed=True):
        self.file.close()
        self.file_open = False
        if report_closed:
            print(f"File {self.file_name}.{self.format} was closed.")

    def _get_file_path(self):
        return self.full_path
        
    def _open_file(self, handover=None):
        if self.file_open:
            raise RuntimeError("Cannot open secondary file in one class instance!")
        elif handover:
            self.full_path = handover
        else:
            attempt = 0
            while attempt < genset.MAX_WATCHDOG:
                try:
                    unconfirmed_path = input("Please input path of file to open:\n")
                    if not(Path(unconfirmed_path).exists() and Path(unconfirmed_path).is_file()):
                        raise ValueError()
                    full_name = (os.path.basename(unconfirmed_path).split()[-1]).split(".")
                    if full_name[-1] != ("txt"):
                        print(f"'{full_name[-1]}' is not a supported data file format!")
                        raise ValueError()
                    self.full_path = unconfirmed_path
                        
                except ValueError:
                    attempt += 1
                    print(f"Invalid or unreadable file. Attempt {attempt}/{genset.MAX_WATCHDOG}!\n")
                finally:
                    if attempt >= genset.MAX_WATCHDOG:
                        exit("Watchdog exceeded, terminating program!\n\n")

        full_name = (os.path.basename(self.full_path).split()[-1]).split(".")         
        self.format = full_name[-1]
        self.file_name = full_name[0]
        self.folder_directory = Path(self.full_path).resolve().parent
        self.new_file = False
        if self.format == "txt":
            print(f"WARNING: opening a 'txt' format file. This is no longer a supported format. Please convert this file to '{datset.DEFAULT_FORMAT}' file format!")
            open_mode = "r"
        else:
            open_mode = "a+"
        self.file = open(self.full_path,open_mode,newline='\n')

    def rename(self):
        watchdog = 0
        old_name = self.file_name

        print(f"Current filename is '{self.file_name}'")
        while watchdog < genset.MAX_WATCHDOG:
            chosen_name = input("Please input a new name for the file.\n")
            if self._is_valid_filename(chosen_name):
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
        print(f"Renamed '{old_name}.{self.format}' to '{chosen_name}.{self.format}'.")

    def ask_rename(self):
        print("Press ENTER to rename newly created file.\n")
        if keco.timeout_action(3.5):
            self.rename()        
        
    def __init__(self,open_file=True,handover_path=None):
        self.file_open = False
        if datset.DEBUG_MODE:
            print(f"DEBUG: debug mode is on, new files will be created in {datset.DEBUG_DIRECTORY}!")
        if open_file: 
            self._open_file(handover=handover_path)
        else:
            self._create_file()
        if not hasattr(self, 'file') or self.file is None:
            raise RuntimeError("File not created, cannot initiate Data Class!")
        print(f"File '{self.file_name}.{self.format}' was initiated successfully.")
        super().__init__(self.file, format=self.format, newfile=self.new_file)
