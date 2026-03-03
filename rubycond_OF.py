# -*- coding: utf-8 -*-
"""

Title: Rubycond_OF: tool for opening data files in the most common formats

Rubycond: Python software to determine pressure in diamond anvil cell experiments by Ruby and Samarium luminescence.

Version 0.2.0
Release 260301

Author:

Yiuri Garino:

Copyright (c) 2023-2026 Yiuri Garino

Download: 
    https://github.com/CelluleProjet/Rubycond_of

Contacts:

Yiuri Garino
    yiuri.garino@cnrs.fr

Silvia Boccato
    silvia.boccato@cnrs.fr

License: GPLv3

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.

"""

def reset():
    import sys
    
    if hasattr(sys, 'ps1'):
        
        #clean Console and Memory
        from IPython import get_ipython
        get_ipython().run_line_magic('clear','/')
        get_ipython().run_line_magic('reset','-sf')
        print("Running interactively")
        print()

    else:
        print("Running in terminal")
        print()


if __name__ == '__main__':
    reset()


import numpy as np
import matplotlib.pyplot as plt
from PyQt5 import QtWidgets, QtCore, QtGui
from datetime import datetime 

#https://stackoverflow.com/questions/16981921/relative-imports-in-python-3
import os, sys, platform
script = os.path.abspath(__file__)
script_dir = os.path.dirname(script)
sys.path.append(script_dir)


from model.OF_Model import my_model
from view.OF_View import Data_Table, Frame_1_graph, open_file_commands
from view.OF_about import about

class pop_up_simple(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        layout = QtWidgets.QVBoxLayout()
        self.label = QtWidgets.QLabel()
        self.label.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        layout.addWidget(self.label)
        self.setLayout(layout)

class open_file(QtWidgets.QWidget): #QtWidgets.QWidget): 
    def __init__(self, debug = False, model = None):
        super().__init__()
        
        self.__name__ = 'Rubycond Open File'
        self.__version__ = '0.2.0' 
        self.__release__ = '260301'
        
        self.about = about(self.__name__, self.__version__, self.__release__)
        self.pop_up_info = pop_up_simple()
        
        if model is None:
            self.model = my_model(debug)
        else:
            self.model = model
        self.debug = debug
        
        if self.debug : print('\nopen_file\n')
        
        self.setWindowTitle("Open File")

    


        self.tabs = QtWidgets.QTabWidget()

        
        self.tab_data = Data_Table(self.model, self.debug)
        self.tab_fig = Frame_1_graph(self.model, self.debug)
        self.tabs.addTab(self.tab_data, "Select Data")
        self.tabs.addTab(self.tab_fig, "Plot")
        self.commands = open_file_commands(self.model, self.debug, self.about)
        
        layout_Left = QtWidgets.QVBoxLayout()
        layout_Left.addWidget(self.commands)
        layout_Left.setAlignment(QtCore.Qt.AlignTop)

        layout_Right = QtWidgets.QVBoxLayout()
        layout_Right.addWidget(self.tabs)
        
        layout_main = QtWidgets.QHBoxLayout()
        layout_main.addLayout(layout_Left)
        layout_main.addLayout(layout_Right)
        
        
        self.label_status_bar = QtWidgets.QLabel()
        self.label_status_bar.setText('Status Bar')
        self.model.statusbar_message_add(self.label_status_bar.setText)
        
        
        Widget_status_bar = QtWidgets.QWidget()

        
        Widget_status_bar.setObjectName('statusbar')
        Widget_status_bar.setStyleSheet("#statusbar {border: 2px solid darkgray; border-radius: 10px;}")
        
        layout_status_bar = QtWidgets.QGridLayout(Widget_status_bar)
        layout_status_bar.addWidget(self.label_status_bar, 1, 1)
        
        layout_final = QtWidgets.QGridLayout()
        layout_final.addLayout(layout_main, 1, 1)
        layout_final.addWidget(Widget_status_bar, 2, 1)
        
        self.setLayout(layout_final)

        #self.init_Statusbar()
        
        #Signal Slot Connection
        
        self.commands.signal_plot_data.connect(self.tab_fig.plot_data)
        
        self.commands.signal_fill_float_table.connect(self.tab_data.set_numpy_2D)
        self.commands.signal_fill_float_table.connect(self.update_command_plot_combobox)
        self.commands.signal_fill_float_table.connect(self.update_command_accept_combobox)
        
        
        self.commands.signal_fill_str_table.connect(self.tab_data.set_str_2D)
        self.commands.signal_fill_str_table.connect(self.update_command_plot_combobox)
        self.commands.signal_fill_str_table.connect(self.update_command_accept_combobox)
        
        self.commands.button_Plot_data.clicked.connect(self.add_plot)
        
        self.commands.button_Delete_plot.clicked.connect(self.delete_plot)
        
        self.commands.signal_quit.connect(self.close)
        
        #Shortcuts
        
        shortcut = QtGui.QKeySequence(QtCore.Qt.CTRL + QtCore.Qt.Key_I)
        shortcut = QtWidgets.QShortcut(shortcut, self)
        shortcut.activated.connect(self.script_info) 
        
        self.model.statusbar_message(message = f'Done init OF {__file__}')
        
    def delete_plot(self):
        element = self.commands.combobox_button_Delete_plot.currentIndex()
        name = self.commands.combobox_button_Delete_plot.currentText()
        self.tab_fig.delete_plot(element)
        
        self.commands.combobox_button_Delete_plot.clear()
        self.commands.combobox_button_Delete_plot.addItems(self.tab_fig.fig_ref_names)
        self.model.statusbar_message(message = f"Deleted {name}")
    
    def add_plot(self):
        
        x_index = self.commands.combobox_Plot_data_column_x.currentIndex()
        y_index = self.commands.combobox_Plot_data_column_y.currentIndex()
        data_x = self.commands.file_data[:, x_index]
        data_y = self.commands.file_data[:, y_index]
        
        if self.debug:
            print("\nAdd plot\n")
            print(data_x)
            print(data_y)
            print(data_x.dtype)
            print(data_x.dtype == '<U32')
        
        if self.commands.flag_custom_file:
            try :
                try:
                    data_x = data_x.astype(float)
                except:
                    data_x = np.char.replace(data_x, ',','.')
                    data_x = data_x.astype(float)
                try:
                    data_y = data_y.astype(float)
                except:
                    data_y = np.char.replace(data_y, ',','.')
                    data_y = data_y.astype(float)
                
            except Exception as e:
                self.error_box(e)
        
        name = f"Col_X {x_index + 1} Col_Y {y_index + 1}"
        self.tab_fig.add_plot(data_x, data_y, name)
        
            
        self.commands.combobox_button_Delete_plot.clear()
        self.commands.combobox_button_Delete_plot.addItems(self.tab_fig.fig_ref_names)
        self.model.statusbar_message(message = f"Added Plot {name}")
        
    
    def update_command_accept_combobox(self, data):
        row, col = data.shape
        
        self.commands.combobox_Accept_data_column_x.clear()
        self.commands.combobox_Accept_data_column_y.clear()
        items = [ f'Col {i+1}' for i in range(col)]
        
        self.commands.combobox_Accept_data_column_x.addItems(items)
        self.commands.combobox_Accept_data_column_y.addItems(items)
        self.commands.combobox_Accept_data_column_x.setCurrentIndex(0)
        self.commands.combobox_Accept_data_column_y.setCurrentIndex(1)
        
    def update_command_plot_combobox(self, data):

        self.commands.combobox_button_Delete_plot.clear()
        self.commands.combobox_button_Delete_plot.addItems(self.tab_fig.fig_ref_names)
        
        row, col = data.shape
        
        self.commands.combobox_Plot_data_column_x.clear()
        self.commands.combobox_Plot_data_column_y.clear()
        items = [ f'Col {i+1}' for i in range(col)]
        
        self.commands.combobox_Plot_data_column_x.addItems(items)
        self.commands.combobox_Plot_data_column_y.addItems(items)
    
    def error_box(self, error):
        msgBox = QtWidgets.QMessageBox()
        msgBox.setIcon(QtWidgets.QMessageBox.Critical)
        msgBox.setWindowTitle("Error Opening File")
        msgBox.setText(str(error))
        msgBox.setStandardButtons(QtWidgets.QMessageBox.Ok)
        msgBox.exec()
    
    def script_info(self):
        script = os.path.abspath(__file__)
        script_dir = os.path.dirname(script)
        script_name = os.path.basename(script)
        now = datetime.now()
        date = now.isoformat(sep = ' ', timespec = 'seconds') #example = '2024-03-27 18:04:46'
        
        print()
        print('_/‾\\'*20)
        print()
        print(date)
        print()
        print("File folder = " + script_dir)
        print("File name = " + script_name)
        print("Current working directory (AKA Called from ...) = " + os.getcwd())
        print("Python version = " + sys.version)
        print("Python folder = " + sys.executable)
        print()
        print('_/‾\\'*20)
        print()
        
        time = datetime.now().strftime("%d %B %Y %H:%M:%S")
        message = '\n'
        message+= f'Program name = {self.__name__}\n'
        message+= f'Version {self.__version__} | Release {self.__release__}\n'
        message+= '\n'
        message+= "Sys Info:\n"
        message+= '\n'
        message+= f"OS: {platform.system()} {platform.release()}\n"
        message+= f"Architecture: {platform.machine()}\n"
        message+= '\n'
        message+= 'Script Info:\n'
        message+= '\n'
        message+= f"File folder = {script_dir}\n"
        message+= f"File name = {script_name}\n"
        message+= f"Current working directory = {os.getcwd()}\n"
        message+= f"Python version = {sys.version}\n"
        message+= f"Python folder = {sys.executable}\n"
        message+= '\n'
        self.pop_up_info.setWindowTitle('Info ' + time)
        self.pop_up_info.label.setText(message)
        self.pop_up_info.show()
        
class Window(QtWidgets.QMainWindow):
    def __init__(self, model, debug = False):
        super().__init__()
        self.setWindowTitle("Open File 240318")
        self.resize(500, 500)
        self.debug = debug
        self.model = model
        
        
        SMALL_SIZE = 15
        MEDIUM_SIZE = 17
        BIGGER_SIZE = 19
        
        plt.rcParams["font.size"] = BIGGER_SIZE
        
        plt.rc('font', size=SMALL_SIZE)          # controls default text sizes
        plt.rc('axes', labelsize=MEDIUM_SIZE)    # fontsize of the x and y labels
        plt.rc('xtick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
        plt.rc('ytick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
        plt.rc('legend', fontsize=SMALL_SIZE)    # legend fontsize
        plt.rc('figure', titlesize=BIGGER_SIZE)  # fontsize of the figure title
        
        central_winget = open_file(self.model, self.debug) 
        self.setCentralWidget(central_winget)
        self.init_Statusbar()
        self.model.statusbar_message(message = 'Done init')
    
    def init_Statusbar(self):
        self.statusbar = QtWidgets.QStatusBar()
        #self.statusbar.addPermanentWidget(QtWidgets.QLabel("Welcome !"))
        #self.statusbar.addWidget(QtWidgets.QLineEdit())
        self.setStatusBar(self.statusbar)
        #self.statusbar.showMessage('Init 2')
        self.model.statusbar_message_ref = self.statusbar.showMessage
        
def main():
    #Entry point in poetry pyproject.toml
    app = QtWidgets.QApplication(sys.argv)
    app.setStyleSheet("""
                      * {
                          font-size: 15px;
                    }
                      """)


    window = open_file(debug = False) 

    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()