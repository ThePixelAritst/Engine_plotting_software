import socket
from keyboard_controller import detect_keystroke,clear_keyboard_buffer
from program_settings import data_settings as datset

class Data_calculations():
    def __init__(self):
        # variables
        self.total_runtime = 0
        self.raw_input_data = []
        self.raw_input_data_length = 0
        self.output = []
        self.list_runtime = []
        self.list_rpm = []
        self.missing_point_list = []

    def set_input_data(self,full_raw_data):
        self.raw_input_data = full_raw_data
        self.raw_input_data_length = len(self.raw_input_data)

    def get_period_time(self, position, precision=3, ignore_set_data = False, full_packet=None):
        if not ignore_set_data:
            selected_packet = self.raw_input_data[position][1]
        else:
            selected_packet = full_packet[position][1]
        fetched_period = round(int(selected_packet)*10**-6,precision)
        return(fetched_period)

    def get_rpm(self,position,precision=0,ignore_set_data = False, full_packet=None): #calculates the speed of the engine based on provided data. Input only one period, 
        if not ignore_set_data:
            selected_packet = self.get_period_time(position,5)
        else:
            selected_packet = self.get_period_time(position,5,ignore_set_data=True,full_packet=full_packet)
        rpm = round(60/selected_packet,precision)
        return rpm
    
    def increase_total_runtime(self,position,set_data=False,full_packet=None):
        self.total_runtime += self.get_period_time(position,set_data=set_data,full_packet=full_packet)

    def get_total_runtime(self): #calculates the speed of the engine based on provided data. Input only one period,  
        return self.total_runtime

    def compile_runtime_list(self,manually_set_data=False,data=None):
        if manually_set_data:
            self.set_input_data(data)
        internal_pointer = 1
        self.list_runtime.append(0)
        while internal_pointer < self.raw_input_data_length:
            self.list_runtime.append(round(self.list_runtime[-1]+self.get_period_time(internal_pointer),3))
            internal_pointer += 1

    def compile_rpm_list(self,manually_set_data=False,data=None):
        if manually_set_data:
            self.set_input_data(data)
        internal_pointer = 0
        while internal_pointer < self.raw_input_data_length:
            self.list_rpm.append(self.get_rpm(internal_pointer,2))
            internal_pointer += 1

    def find_missing_points(self,manually_set_data=False,data=None):
        if manually_set_data:
            self.set_input_data(data)

        if self.raw_input_data_length == 0:
            return []
        
        internal_pointer = 0
        starting_point_offset = int(self.raw_input_data[0][0])
        while internal_pointer < self.raw_input_data_length:
            if internal_pointer == (self.raw_input_data[internal_pointer]) - starting_point_offset:
                internal_pointer += 1
            else:
                missing_point = (self.raw_input_data[internal_pointer]) - starting_point_offset
                self.missing_point_list.append([internal_pointer , missing_point])
                internal_pointer = missing_point
                
    def compile_data(self,get_data):
        print("Compiling data")
        self.set_input_data(get_data)
        self.compile_rpm_list()
        self.compile_runtime_list()
        #self.find_missing_points()

    def get_compiled_data(self):
        return [self.list_runtime,self.list_rpm,self]

data_calculate = Data_calculations()



class Data_Input():
    def __init__(self):
        # Constants for Data_Handle
        UDP_IP = "0.0.0.0"
        UDP_PORT = 5005
        TIMEOUT = 2

        # Connection setup
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((UDP_IP, UDP_PORT))
        self.sock.settimeout(TIMEOUT)

        # Common Variables
        self.raw_data = [] # full raw data of a run, stored in list. Structure: [ [Current period n, Period of last turn in microsecs] ]
        self.timeout_number = 0
        self.period_number = 0

    def listen(self):
        # Initiation
        print("Initiation, Clearing keyboard buffer")
        clear_keyboard_buffer()
        print("Listening, press any key to stop")

        # Actual listening loop
        while True:
            if detect_keystroke(): #Quits the loop if any key is pressed
                clear_keyboard_buffer()
                break
    
            try: 
                partial_undecoded = self.sock.recv(1024) #Advances beyond this line if data is received, otherwise skips to except
                
                
                self.timeout_number = 0
                self.raw_data.append(partial_undecoded.decode().split()) #returns the decoded data in a list form [Current period n, Period of last turn in microsecs]
                
                if datset.TELEMETRY_SETTING == 1:
                    print(f"{data_calculate.get_rpm(-1,precision=2,ignore_set_data=True,full_packet=self.raw_data)} RPM\nPoints: {self.period_number}\n")
                elif datset.TELEMETRY_SETTING == 2:
                    data_calculate.increase_total_runtime(-1,True,self.raw_data)
                    run_time = data_calculate.get_total_runtime()
                    print("Data Receive Success")
                    print(f"{data_calculate.get_rpm(-1,ignore_set_data=True,full_packet=self.raw_data)} RPM\n{run_time} sec\n{self.period_number} points\n")

                self.period_number += 1

            except Exception:
                print(f"DATA RECEIVE TIMEOUT! Attempt: {self.timeout_number}")
                self.timeout_number += 1
                continue
        
        print("Listening stopped.")
        
    def output(self):
        data_calculate.compile_data(self.raw_data)
        return data_calculate.get_compiled_data() #[time_list,rpm_list, missing point list - [internal,engine], raw_data - [revolution,micros from last]]

data_receive = Data_Input()