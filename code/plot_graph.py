# matplotlib
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
import matplotlib.animation as anim
from matplotlib.ticker import AutoMinorLocator
# python libraries
import math
import ast
import os
from pathlib import Path
import numpy as np
import typing
import imageio_ffmpeg
# Program dependencies
from program_settings import graphing_settings as gs
from program_settings import general_settings as genset
import file_manager as fm


class Graphing():
    def __init__(self):
        self.run_name = None
        plt.rcParams["animation.ffmpeg_path"] = imageio_ffmpeg.get_ffmpeg_exe()
        self.fig = plt.figure(num=genset.NAME,figsize=[gs.SIZE_X,gs.SIZE_Y],layout="constrained")
        if gs.STAT_TEXT:
            self.ax1 = self.fig.add_subplot(1,gs.COLLUMN_NUMBER,(1,gs.GRAPH_COLLUMNS))
        else:
            self.ax1 = self.fig.add_subplot()
        self.ax2 = self.ax1.twinx()
        self.x_ax1=[]
        self.main = []
        self.y_ax1=[]
        self.y_ax2 = []
        self.secondary = []
        self.secondary_label = ""
        self.main_label = "Rotational speed [RPM]"
        self.ax2_stat = ""
        self.axis_length = []
        self.file: fm.File = None

    def read_data_content(self):
        data = self.file.read_column((0,1))
        self.x_ax1 = data[0]
        self.y_ax1 = data[1]
        self.axis_length = len(data[0])
        self.run_name = self.file.file_name

    def data_handover(self,file_object):
        self.file = file_object
        self.read_data_content()

    def basic_data_read(self):
        self.float_run_time = round(self.x_ax1[-1],2)
        self.ceil_run_time = math.ceil(self.float_run_time)
        self.x_points = len(self.x_ax1)
        self.x_max = max(self.x_ax1)

    def save_plotted_graph(self,save_name,animated,format=None,animated_writer="ffmpeg"):
        base_directory = Path(__file__).resolve().parent
        if animated:
            if not format:
                format = "mp4"
            print("Saving animated figure")
            data_path = os.path.join(base_directory,"graphs","animated",f"{save_name}.{format}")
            self.ani.save(data_path,writer=animated_writer)
        else:
            if not format:
                format = "png"
            print("Saving static figure")
            data_path = os.path.join(base_directory,"graphs","static",f"{save_name}.{format}")
            plt.savefig(data_path)




    def calculate_derivation(self):
        pointer = 0
        real_derivation = 0
        derivation_edge = [0,0]
        self.y_ax2=[]
        while pointer < len(self.y_ax1):
            if (self.y_ax1[pointer] or self.y_ax1[pointer-1]) == np.nan:
                self.y_ax2.append(np.nan)
                pointer += 1
                continue

            raw_derivation = self.y_ax1[pointer]-self.y_ax1[pointer-1]
            if self.x_ax1[pointer]-self.x_ax1[pointer-1] != 0:
                interval_coeficient = 1/(self.x_ax1[pointer]-self.x_ax1[pointer-1])
            else:
                interval_coeficient = 1

            real_derivation = raw_derivation * interval_coeficient
            pointer += 1

            if real_derivation > derivation_edge[1]:
                derivation_edge[1] = real_derivation
            elif real_derivation < derivation_edge[0]:
                derivation_edge[0] = real_derivation

            if real_derivation > gs.MAX_ACCELERATION or real_derivation < -gs.MAX_ACCELERATION and gs.LIMIT_ACCELERATION:
                real_derivation = np.nan

            real_derivation = round(real_derivation,2)
            

            self.y_ax2.append(real_derivation)     

        self.ax2.set_ybound(min(self.y_ax1)-(min(self.y_ax1)/10),max(self.y_ax1)+(max(self.y_ax1)/10))
        if gs.ACCELERATION_LOG10:
            self.secondary_label = "Acceleration [log(RPM/s)]"
        else:
            self.secondary_label = "RPM Acceleration [RPM/s]"

        self.ax2_stat = f"Max Accl.: {round(derivation_edge[1],1)} RPM/s\nMin Accl.: {round(derivation_edge[0],1)} RPM/s" #\nAvg. Accl.: {sum(self.y_ax2)/len(self.y_ax2)} <- nefunguje kvůli NaN hodnotám
        self.ax2.set_ylabel(self.secondary_label,size=gs.LABEL_SIZE)



    def calculate_rev_count(self):
        i = 1
        self.y_ax2=[]
        while i <= len(self.x_ax1):
            self.y_ax2.append(i)
            i+=1
        self.ax2.set_ylabel("Completed revolutions []",size=gs.LABEL_SIZE)
        self.ax2.set_ybound(0,len(self.y_ax1)+len(self.y_ax1)/10)
        self.secondary_label = "Rev count"
        self.ax2_stat = f"Rev. Count: {len(self.y_ax2)}"



    def set_stat_subplot(self):
        self.ax_text = self.fig.add_subplot(1,gs.COLLUMN_NUMBER,(gs.GRAPH_COLLUMNS+1,gs.COLLUMN_NUMBER))
        self.ax_text.set_title("Statistics",fontsize=gs.TITLE_SIZE)
        self.ax_text.axis("off")



    def display_stat_text(self):
        self.set_stat_subplot()
        acceleration_limit = "None"
        if gs.LIMIT_ACCELERATION:
            acceleration_limit = gs.MAX_ACCELERATION
        self.full_stat_text = f"Max Speed: {max(self.y_ax1)} RPM\nAvg. Speed: {round(sum(self.y_ax1)/self.x_points,1)} RPM\n{self.ax2_stat}\nRuntime: {self.float_run_time} s\nCutoff: {acceleration_limit}\nPoints: {self.x_points}"
        self.statistics = self.ax_text.text( # cool and useful stats display
                (0.1),
                (0),
                self.full_stat_text,
                bbox={"facecolor": "white","pad": 3.5},
                fontsize=gs.TITLE_SIZE*0.8
            )
        
    def set_common(self):
        self.calculate_derivation()
        self.basic_data_read()

        self.ax1.set_title(f"Analysis of: {self.run_name}",size=gs.TITLE_SIZE)

        self.ax1.set_xlabel("Time [second]",size=gs.LABEL_SIZE)
        self.ax1.set_ylabel(self.main_label,size=gs.LABEL_SIZE)
        self.ax1.grid()

        self.ax1.set_zorder(10)
        self.ax2.set_zorder(1)
        self.ax1.patch.set_visible(False)  # prevents background blocking

        if gs.ACCELERATION_LOG10:
            self.ax2.set_yscale("symlog")
        else:
            self.ax2.yaxis.set_minor_locator(AutoMinorLocator(4))

    def display_legend(self):
        # legend merge
        handle_ax1, label_ax1 = self.ax1.get_legend_handles_labels()
        handle_ax2, label_ax2 = self.ax2.get_legend_handles_labels()

        #display legend
        self.ax1.legend(
            handles=handle_ax1+handle_ax2,
            labels=label_ax1+label_ax2,
            loc="upper right",
            edgecolor="black",
            fancybox = False,
            fontsize= gs.LABEL_SIZE
            )
        
    def plot_main(self,x_coord,y_coord):
        self.main, = self.ax1.plot(
            x_coord,
            y_coord,
            linewidth=gs.AX1_LINE,
            label=self.main_label,
            color=gs.AX1_COLOR
        )
    
    def plot_secondary(self,x_coord,y_coord):
        self.secondary, = self.ax2.plot(
            x_coord,
            y_coord,
            color=gs.AX2_COLOR,
            linewidth=1.3,
            label=self.secondary_label
        )



    def draw_static(self):
        print("generating static graph")
        
        self.set_common()

        #plot lines
        self.plot_secondary(self.x_ax1,self.y_ax2)
        self.plot_main(self.x_ax1,self.y_ax1)


        self.display_legend() #displays legend
        
        self.main.set_path_effects([pe.Stroke(linewidth=(gs.AX1_LINE*2),foreground="white"),pe.Normal()]) # makes sure main line has a slight white outline
        

        #display horizontal lines
        self.ax1.hlines(y=0,xmin=0,xmax=self.x_ax1[-1],linestyles="dashed",color=gs.AX1_COLOR)
        self.ax2.hlines(y=0,xmin=0,xmax=self.x_ax1[-1],linestyles="dashed",color=gs.AX2_COLOR)
        #self.ax1.vlines((self.x_ax1[-1]/2), ymin=0, ymax=max(self.y_ax1), color="red") #for debug only, shows line in the middle of the time

        if gs.STAT_TEXT:
            self.display_stat_text()

        print("Generation of static graph successful")
        if gs.SAVE_FIG:
            self.save_plotted_graph(self.run_name,False)
        plt.show()


    # Animation Portion

    def initiate_animation(self):
        self.main.set_data([],[])
        self.secondary.set_data([],[])
        return(self.main,self.secondary)
    
    def update_frame(self,frame_number):
        # secondary line update
        self.secondary.set_data(self.x_ax1[:frame_number],self.y_ax2[:frame_number])
        # main line update
        self.main.set_data(self.x_ax1[:frame_number],self.y_ax1[:frame_number])
        # set text
        #self.debug_text.set_text(f"Frame: {frame_number}\nFrame count: {len(self.x_ax1)}")
        self.statistics.set_text(f"Cur. Speed: {self.y_ax1[frame_number-1]} RPM\nCur. Accl.: {self.y_ax2[frame_number-1]} RPM/s\n{self.full_stat_text}\nCur. Frame: {frame_number}")
        print(f"Currently generating frame: {frame_number}")
        return(self.main,self.secondary,self.statistics)

    def animate(self):
        print("Generating animation")
        LIMIT_RESERVE = 1.1
        self.set_common()

        self.plot_main([],[])
        self.plot_secondary([],[])

        self.ax1.set_ylim(
            min(self.y_ax1) * LIMIT_RESERVE,
            max(self.y_ax1) * LIMIT_RESERVE
        )

        self.ax1.set_xlim(-0.1 * self.x_max, self.x_max * LIMIT_RESERVE)

        self.ax2.set_ylim(
            np.nanmin(self.y_ax2) * LIMIT_RESERVE,
            np.nanmax(self.y_ax2) * LIMIT_RESERVE
        )

        self.ax2.set_xlim(-0.1 * self.x_max, self.x_max * LIMIT_RESERVE)

        self.main.set_path_effects([pe.Stroke(linewidth=(gs.AX1_LINE*2),foreground="white"),pe.Normal()]) # makes sure main line has a slight white outline
        

        #display horizontal lines
        self.ax1.hlines(y=0,xmin=0,xmax=self.x_ax1[-1],linestyles="dashed",color=gs.AX1_COLOR)
        self.ax2.hlines(y=0,xmin=0,xmax=self.x_ax1[-1],linestyles="dashed",color=gs.AX2_COLOR)
        #self.ax1.vlines((self.x_ax1[-1]/2), ymin=0, ymax=max(self.y_ax1), color="red") #for debug only, shows line in the middle of the time
        
        self.display_legend()

        if gs.STAT_TEXT:
            self.display_stat_text()

        self.ani = anim.FuncAnimation(
            self.fig,
            self.update_frame,
            init_func=self.initiate_animation,
            blit=True,
            frames= len(self.x_ax1),
            interval= 1000*(self.float_run_time)/(len(self.x_ax1))
        )
        if gs.SAVE_FIG:
            self.save_plotted_graph(self.run_name,True)
        print("finished")
        plt.show()
    

graph = Graphing()  