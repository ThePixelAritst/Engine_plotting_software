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
            graph.animate(gs.FRAME_RATE)

    def draw_only_initiation(self): # the option to not initiate the program and only draw the graph from existing data directory
        print("Press any key to interrupt startup\n")
        if timeout_action(3.5):
            file = fm.File(True)
            graph.data_handover(file)
            self.choose_animation()
        
    def file_initiate_wrapper():
        global file
        file = fm.File()

    def file_rename_prompt(self):
        print("Press any key to rename newly created file\n")
        if timeout_action(3):
            file.rename()
    
    def save_all(self):
        data = rx.output()
        for index in range(len(rx.output()[0])):
            file.write((data[0][index],data[1][index]))

main = Main_control()

# Asks the user if they want to only plot-graph
main.draw_only_initiation()

# Listens for data and outputs them
rx.listen()

# Saves data to a file 
main.file_initiate_wrapper()
main.save_all()
main.file_rename_prompt()

# Plots the data
if gs.GENERATE_GRAPH:
    graph.data_handover(file._get_file_path())
    main.choose_animation()
else:
    file._close_file()