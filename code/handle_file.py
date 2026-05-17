from pathlib import Path
import time
import os
import ast

MAX_WATCHDOG = 5

class file_handler():
    def __init__(self):
        self.file_open = False


    def inititiate_file(self):
        if not self.file_open:
            self.date = time.strftime("%Y-%m-%d--%a--%H-%M-%S") #creates a date in the following form: "YYYY-MM-DD--Name of day--HH-MinMin-SS"
            self.base_directory = Path(__file__).resolve().parents[1]
            self.data_path = os.path.join(self.base_directory,"data",f"{self.date}.txt") #self.base_directory / "data" / self.date + ".txt"
            self.data_file = open(self.data_path,"a")
            self.file_name = self.date
            self.file_open = True
        else:
            raise Exception("File already open!")

    def save_to_file(self,text):
        self.data_file.write(f"{text}\n")
        self.data_file.flush()

    def fetch_date_name(self):
        return self.date
    
    def close_file(self):
        self.data_file.close()
        self.file_open = False

    def fetch_file_name(self):
        self.file_name = (os.path.basename(self.data_path).split("."))[0]
        print(f"Current file name: {self.file_name}")
        return self.file_name
        
    def rename_file(self): #closes the file automatically just in case
        self.close_file()
        watchdog = 0
        while True:
            chosen_file_name = input("Input chosen name (without extensions):\n").strip("./,")
            if not chosen_file_name:
                print(f"Invalid file name. Watchdog: {watchdog}/{MAX_WATCHDOG}")
                watchdog += 1
            elif watchdog >= MAX_WATCHDOG:
                exit("Watchdog exceeded")     
            else: break   
        new_name = os.path.join(self.base_directory,"data",f"{chosen_file_name}.txt")
        os.rename(self.data_path, new_name)
        self.data_path = new_name

    def open_and_separate(self):
        readable = False
        watchdog = 0
        while True:
            try:
                file_path = input("Please insert full path to file:\n").strip()
                datafile = open(file_path,"r")
                readable = datafile.readable()
                if not readable:
                    raise Exception(f"Unreadable file. Watchdog: {watchdog}/{MAX_WATCHDOG}")
                else:
                    break
            except:
                print(f"File at specified directory does not exist or is not readable. Watchdog: {watchdog}/{MAX_WATCHDOG}")
                if watchdog >= MAX_WATCHDOG:
                    exit("Watchdog exceeded")
                watchdog += 1
        separated_datafile = datafile.readlines()
        processed_check = ast.literal_eval(separated_datafile[0]) #converts the mess of a string into a list with ints 
        if processed_check[0] != processed_check[1]:
            Exception("Count does not match. Cannot draw graph")
        return file_path, separated_datafile
    
file = file_handler()