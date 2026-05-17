from handle_file import file
from plot_graph import graph
from keyboard_controller import timeout_action
from receive_data import data_receive
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
            graph.set_from_file()
            self.choose_animation()
            exit()

    def file_rename_prompt(self):
        print("Press any key to rename newly created file\n")
        if timeout_action(3):
            file.rename_file()
    
    def save_all(self,data_to_save):
        internal_pointer = 0
        max_length = len(data_to_save)
        while internal_pointer < max_length:
            file.save_to_file(data_to_save[internal_pointer])
            internal_pointer += 1

main = Main_control()

# Asks the user if they want to only plot-graph
main.draw_only_initiation() 

# Listens for data and outputs them
data_receive.listen()
data_output = data_receive.output() #[time_list,rpm_list, missing point list - [internal,engine]]

# Saves data to a file 
file.inititiate_file()
file.save_to_file([len(data_output[0]),len(data_output[1])])
main.save_all(data_output)

file.close_file()
file.fetch_file_name()
main.file_rename_prompt()

# Plots the data
if gs.GENERATE_GRAPH:
    graph.set_from_data([len(data_output[0]),len(data_output[1])],data_output[0],data_output[1],file.fetch_file_name())
    main.choose_animation()