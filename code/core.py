import file_manager as fm
from plot_graph import graph
from keyboard_controller import timeout_action
from receive_data import data_receive as rx
from program_settings import graphing_settings as gs

# Setup of the main functions:

class Main_control():
    def choose_animation(self):
        if not gs.ANIMATE:
            graph.draw_static()
        else:
            graph.animate()

    def draw_only_initiation(self): # the option to not initiate the program and only draw the graph from existing data directory
        print("Press any key to interrupt startup\n")
        if timeout_action(3.5):
            print("Startup interrupted")
            file = fm.File(True)
            graph.data_handover(file)
            self.choose_animation()
            exit()
        
    def file_initiate_wrapper(self):
        global file
        file = fm.File(False)

    def file_rename_prompt(self):
        print("Press any key to rename newly created file\n")
        if timeout_action(3):
            file.rename()
    
    def save_all(self):
        data = rx.output()
        for index in range(len(rx.output()[0])):
            file.write((data[0][index],data[1][index]))

    def imitate_receive(self):
        print("Imitating receive!!!!!")
        fake_file = fm.File(True,handover_path=r"D:\Coding adventures\engine_readout\data\video-run-2.txt")
        
        fake_data = fake_file.read_column()
        for index in range(len(fake_data[0])):
            file.write((fake_data[0][index],fake_data[1][index]))


main = Main_control()

# Asks the user if they want to only plot-graph
main.draw_only_initiation()
# Listens for data and outputs them
rx.listen()
# Saves data to a file 
main.file_initiate_wrapper()
main.save_all()
#main.imitate_receive()
main.file_rename_prompt()

# Plots the data
if gs.GENERATE_GRAPH:
    graph.data_handover(file)
    main.choose_animation()
else:
    file._close_file()