# library dependancies
import os
import time
import re
import typing
from pathlib import Path
import csv
# internal imports
import program_settings as sett
datset = sett.data_settings
genset = sett.general_settings

# data handling portion, works with an already open file object to file, read, and otherwise work with file contents
class Data():
    file: typing.TextIO

    # --- FUNCTION CALL DISPATCH ---
    def _initialize_function_dispatch(self):
        self.writer_set = {"csv": self._write_csv} 
        self.row_reader_set = {"csv": self._readrow_csv}

    # --- CSV FUNCTIONS ---
    def _write_csv(self,row_content):
        self.csv_writer.writerow(row_content)

    def _readrow_csv(self,row_number,include_header):
        if not include_header:
            row_number += self.header_length
        self.file.seek(0)
        row = list(self.csv_reader)[row_number]
        return row

    # --- VISIBLE AND ACCESSIBLE METHODS ---
    def write(self,tuple_of_values):
        self.writer_set[self.format](tuple_of_values)

    def read_row(self,row_number,include_header=False):
        return self.row_reader_set[self.format](row_number,include_header)
    
    # --- CLASS INITIALIZATION ---
    def _write_header(self):
        self.write(("#","SOFTWARE",genset.VERSION_SOFTWARE))
        self.write(("#","PARSER",genset.VERSION_PARSER))
        self.write(("#","RECEIVER",genset.VERSION_RECEIVER))
        self.header_length = 3

    def _initialize_csv(self):
            self.csv_writer = csv.writer(self.file)
            self.csv_reader = csv.reader(self.file, delimiter=' ', quotechar='|')
    
    def __init__(self,opened_file: typing.TextIO,format):
        if opened_file is None or opened_file.closed:
            raise ValueError(f"Expected an open file object, got: {opened_file!r}!")
        self.file = opened_file
        self.format = str(format)
        self._initialize_function_dispatch()

        if self.format == "csv": # tohle není úplně lovely řešení, rozhodně to jde udělat nějak lépe
            self._initialize_csv()
        elif self.format == "txt":
            pass
        else:
            raise ValueError(f"'{self.format} is not a supported file format!'")
        
        self._write_header()

    # tady přijdou write, read a podobné funkce!


# ---- FILE HANDLING ----

# Handles file creating, opening, closing and renaming of a data file.
# Does not handle the data in the file.
# Ensures handling of the data inside the file can be done smoothly.
class File(Data):

    def is_valid_filename(self,filename):
        try:
            if re.search(r'[<>:"/\\|?*]',filename): # or not str(filename).isascii()
                print("Name cannot contain forbidden characters'")
                raise ValueError()
            elif Path.exists(os.path.join(self.folder_directory,f"{filename}.{self.format}")):
                print("Cannot rename, File with same name already exists!")
                raise ValueError()
        except ValueError: return False
        else: return True 

    def create_file(self,format=datset.DEFAULT_FORMAT): #creates file
        if self.file_open:
            raise RuntimeError("Cannot create secondary file in one class instance'")
        self.file_open = True
        self.file_name = time.strftime("%Y-%m-%d--%a--%H-%M-%S")
        if datset.DEBUG_MODE:
            folder = datset.DEBUG_DIRECTORY
        else:
            folder = "data"
        self.folder_directory = os.path.join(Path(__file__).resolve().parents[1],folder)
        self.format = format
        self.full_path = os.path.join(self.folder_directory,f"{self.file_name}.{self.format}")
        self.file = open(self.full_path,"x+",newline='')

    def close_file(self,report_closed=True):
        self.file.close()
        self.file_open = False
        if report_closed:
            print(f"File {self.file_name}.{self.format} was closed.")

    def open_file(self, handover=None):
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
        self.file = open(self.full_path,"a+",newline='')

    def rename(self):
        watchdog = 0
        old_name = self.file_name

        while watchdog < genset.MAX_WATCHDOG:
            chosen_name = input("Please input a new name for the file.\n")
            if self.is_valid_filename(chosen_name,self.folder_directory,self.format):
                self.file_name = chosen_name
                break
            else:
                watchdog += 1
                print(f"\nEncountered error while renaming file. Please try again! Attempt {watchdog}/{genset.MAX_WATCHDOG}")
                if watchdog >= genset.MAX_WATCHDOG:
                    exit("\nWatchdog exceeded, terminating program.\n\n")

        self.close_file(report_closed=False)
        new_file_path = os.path.join(self.folder_directory,f"{chosen_name}.{self.format}")
        os.rename(self.full_path,new_file_path)
        self.full_path = new_file_path
        self.file_name = chosen_name
        self.open_file(handover=self.full_path)
        print(f"Renamed '{old_name}.{self.format}' to '{chosen_name}.{self.format}'")         
        
    def __init__(self,open_file=True,format=datset.DEFAULT_FORMAT):
        self.file_open = False
        if open_file: 
            self.open_file()
        else:
            self.create_file(format)
        if not hasattr(self, 'file') or self.file is None:
            raise RuntimeError("File not created, cannot initiate Data Class")
        if self.format != datset.DEFAULT_FORMAT:
            print(f"WARNING: file '{self.file_name}' is encoded in '{self.format}' format, a non standard file format!")
        print(f"File '{self.file_name}.{self.format}' was initiated successfully.\n")
        super().__init__(self.file,format=format)

open_file = File(open_file=False,format="csv")
open_file.write(("bleh1","bleh2","bleh3"))
open_file.write(("10","20","30"))
print(open_file.read_row(0))