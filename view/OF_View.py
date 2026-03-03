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
from matplotlib.backend_bases import MouseEvent
from datetime import datetime
import sys 
import os

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
    
from PyQt5 import QtWidgets, QtCore
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

import traceback

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

class Data_Table(QtWidgets.QTableWidget):
    def __init__(self, model, debug = False):
        super().__init__()
        self.__name__ = 'Rubycond Open File View'
        self.__version__ = '0.2.0'
        self.__release__ = '260301'
        self.model = model 
        self.debug = debug
        if self.debug : print('\nData_Table\n')

        self.setColumnCount(5)
        self.setRowCount(5)
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self)

    def error_box(self, title):
        msgBox = QtWidgets.QMessageBox()
        msgBox.setIcon(QtWidgets.QMessageBox.Critical)
        msgBox.setWindowTitle(str(title))
        msgBox.setText(traceback.format_exc())
        msgBox.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        msgBox.setStandardButtons(QtWidgets.QMessageBox.Ok)
        msgBox.exec()
       
    def reset(self):
        tot = self.rowCount()
        for i in range(tot+1):
            self.removeColumn(i)
        
    def set_numpy_2D(self, data):
        try:
            self.clear()
            row, col = data.shape
            self.model.table_row = row
            self.model.table_col = col
            self.setColumnCount(col)
            self.setRowCount(row)
            for i_r in range(row):
                for i_c in range(col):
                    self.setItem(i_r, i_c, QtWidgets.QTableWidgetItem(f'{data[i_r,i_c]:.2f}'))
        except Exception:
            self.error_box('Data_Table set_numpy_2D')
    
    def set_str_2D(self, data):
        try:
            self.clear()
            row, col = data.shape
            self.model.table_row = row
            self.model.table_col = col
            self.setColumnCount(col)
            self.setRowCount(row)
            for i_r in range(row):
                for i_c in range(col):
                    self.setItem(i_r, i_c, QtWidgets.QTableWidgetItem(data[i_r,i_c]))
        except Exception:
            self.error_box('Data_Table set_str_2D')
                
class show_text_file(QtWidgets.QFrame):
    def __init__(self, filename, debug = False):
        super().__init__()
        
        
        self.setWindowTitle(f'file = {str(filename)}')
        try:

            text_edit = QtWidgets.QPlainTextEdit()
            text=open(filename).read()
            text_edit.setPlainText(text)
    
            #Final layout
            
            layout = QtWidgets.QVBoxLayout()
            layout.addWidget(text_edit)
            
            self.setLayout(layout)
            
            self.setSizePolicy(
                QtWidgets.QSizePolicy.Fixed,
                QtWidgets.QSizePolicy.Fixed)
        except Exception:
            self.error_box('Show text file error')
    
    def error_box(self, title):
        msgBox = QtWidgets.QMessageBox()
        msgBox.setIcon(QtWidgets.QMessageBox.Critical)
        msgBox.setWindowTitle(str(title))
        msgBox.setText(traceback.format_exc())
        msgBox.setStandardButtons(QtWidgets.QMessageBox.Ok)
        msgBox.exec()
   
class open_file_commands(QtWidgets.QFrame):
    
    signal_plot_data = QtCore.pyqtSignal(np.ndarray)
    #signal_add_plot = QtCore.pyqtSignal(np.ndarray)
    signal_fill_float_table = QtCore.pyqtSignal(np.ndarray)
    signal_fill_str_table = QtCore.pyqtSignal(np.ndarray)
    
    signal_selected_data_all = QtCore.pyqtSignal(np.ndarray, str)
    signal_selected_data_xy = QtCore.pyqtSignal(np.ndarray, np.ndarray, str)

    
    
    signal_quit = QtCore.pyqtSignal()
    
    def __init__(self, model, debug = False, about = None):
        super().__init__()
        self.model = model
        self.debug = debug
        self.about = about
        
        if self.debug : print('\nopen_file_commands\n')
        
        self.file_data = None
        self.file_data_i_x = 0 #Default value X data = column 0
        self.file_data_i_y = 1 #Default value Y data = column 1
        self.flag_custom_file = False
        self.loadtxt_comments = ['#', '"']
        self.loadtxt_delimiter = r' ' 
        self.loadtxt_skiprows = 0
        
        self.max_width = 300
        
        self.label_decimal = QtWidgets.QLabel(self)
        self.label_decimal.setText('Decimal separator')
        
        #(['Decimal separator = point .', 'Decimal separator = comma ,'])
        
        self.combobox_decimal_separator = QtWidgets.QComboBox()
        self.combobox_decimal_separator.addItems(['point .', 'comma ,'])
        self.combobox_decimal_separator.currentIndexChanged.connect(self.combobox_decimal_separator_index_changed)
                                                  
        self.button_Open_npy = QtWidgets.QPushButton("Open numpy (npy)")
        self.button_Open_npy.clicked.connect(self.open_data_File_npy)
        
        self.button_Open_csv = QtWidgets.QPushButton("Open comma delimiter (csv)")
        self.button_Open_csv.clicked.connect(self.open_data_File_csv)
        
        self.button_Open_dat = QtWidgets.QPushButton("Open space/tab delimiter (txt, dat)")
        self.button_Open_dat.clicked.connect(self.open_data_File_dat)
        
        #self.button_Open_tab = QtWidgets.QPushButton("Open tab delimiter")
        #self.button_Open_tab.clicked.connect(self.open_data_File_tab)
        
        self.button_Show_preview = QtWidgets.QPushButton("Show plain text")
        self.button_Show_preview.clicked.connect(self.open_Show_preview)
        
        self.button_Open_custom = QtWidgets.QPushButton("Open")
        self.button_Open_custom.clicked.connect(self.open_data_File_custom)
        
        
        self.label_comments = QtWidgets.QLabel(self)
        self.label_comments.setText('Commented lines (ch)')
        
        self.label_delimiter = QtWidgets.QLabel(self)
        self.label_delimiter.setText('Columns delimiter')
        
        self.label_skiprows = QtWidgets.QLabel(self)
        self.label_skiprows.setText('Skip first (n) lines')
        
        
        self.button_about = QtWidgets.QPushButton("About Open File")
        self.button_about.clicked.connect(self.open_about)
        
        _ =''
        for i in self.loadtxt_comments:
            _ = _ + i
        self.open_button_comments = QtWidgets.QPushButton(_)
        self.open_button_comments.clicked.connect(self.command_button_comments)
        
        '''ComboBox better ?
        self.label_loadtxt_delimiter = QtWidgets.QLineEdit(self, placeholderText=self.loadtxt_delimiter,
        clearButtonEnabled=True)
        #self.label_loadtxt_delimiter.returnPressed.connect(self.change_loadtxt_delimiter) 
        '''
        
        self.combobox_loadtxt_delimiter = QtWidgets.QComboBox()
        self.combobox_loadtxt_delimiter.addItems(['space', 'tab', 'comma ,', 'semicolon ;'])
        self.combobox_loadtxt_delimiter.currentIndexChanged.connect(self.combobox_loadtxt_delimiter_index_changed)

        #self.label_loadtxt_skiprows = QtWidgets.QLineEdit(self, placeholderText=str(self.loadtxt_skiprows),clearButtonEnabled=True)
        #self.label_loadtxt_skiprows.returnPressed.connect(self.change_loadtxt_skiprows)
        #Plot Commands
        
        self.open_button_skiprows = QtWidgets.QPushButton("0")
        self.open_button_skiprows.clicked.connect(self.command_button_skiprows)
        
        self.open_button_skiprows
        
        self.button_Plot_data = QtWidgets.QPushButton("Plot")
        #self.button_Plot_data.clicked.connect(self.open_data_File_custom)
        
        self.label_plot_x = QtWidgets.QLabel(self)
        self.label_plot_x.setText('X Data')
        
        self.combobox_Plot_data_column_x = QtWidgets.QComboBox()
        
        self.label_plot_y = QtWidgets.QLabel(self)
        self.label_plot_y.setText('Y Data')
        
        self.combobox_Plot_data_column_y = QtWidgets.QComboBox()
        
        self.button_Delete_plot = QtWidgets.QPushButton("Delete")
        #self.button_Delete_plot.clicked.connect(self.open_data_File_custom)
        
        self.combobox_button_Delete_plot = QtWidgets.QComboBox()
        
        #Accept Close Commands
        self.button_Accept = QtWidgets.QPushButton("Accept")
        self.button_Accept.setStyleSheet("background-color: limegreen"); #lightgreen
        self.button_Accept.clicked.connect(self.app_accept_quit)
        
        self.combobox_Accept_data_column_x = QtWidgets.QComboBox()
        self.combobox_Accept_data_column_y = QtWidgets.QComboBox()

        self.button_Cancel = QtWidgets.QPushButton("Cancel")
        self.button_Cancel.setStyleSheet("background-color: red");
        self.button_Cancel.clicked.connect(self.app_quit)
        
        
        
        Widget_Open = QtWidgets.QWidget()
        Widget_Open.setMaximumWidth(self.max_width)
        Widget_Open.setObjectName('Widget_Open')
        Widget_Open.setStyleSheet("#Widget_Open {border: 2px solid green; border-radius: 10px;}")
        
        layout_Open = QtWidgets.QGridLayout(Widget_Open)
        
        layout_Open.addWidget(self.label_decimal, 0, 1)
        layout_Open.addWidget(self.combobox_decimal_separator, 0, 2)
        
        
        #layout_Open.addWidget(self.button_Open_csv, 2, 1)
        #layout_Open.addWidget(self.button_Open_dat, 3, 1)
        
        layout_Open.addWidget(self.label_comments, 1, 1)
        layout_Open.addWidget(self.label_delimiter, 2, 1)
        layout_Open.addWidget(self.label_skiprows, 3, 1)
        
        
        
        #layout_Open.addWidget(self.label_loadtxt_comments, 1, 2)
        layout_Open.addWidget(self.open_button_comments, 1, 2)
        layout_Open.addWidget(self.combobox_loadtxt_delimiter, 2, 2)
        layout_Open.addWidget(self.open_button_skiprows, 3, 2)
        
        layout_Open.addWidget(self.button_Open_custom, 4, 1)
        
        Widget_numpy = QtWidgets.QWidget()
        Widget_numpy.setMaximumWidth(self.max_width)
        Widget_numpy.setObjectName('Widget_numpy')
        Widget_numpy.setStyleSheet("#Widget_numpy {border: 2px solid green; border-radius: 10px;}")
        
        layout_numpy = QtWidgets.QGridLayout(Widget_numpy)
        layout_numpy.addWidget(self.button_Open_npy, 1, 1)
        
        Widget_text = QtWidgets.QWidget()
        Widget_text.setMaximumWidth(self.max_width)
        Widget_text.setObjectName('Widget_Text')
        Widget_text.setStyleSheet("#Widget_Text {border: 2px solid black; border-radius: 10px;}")
        
        layout_text = QtWidgets.QGridLayout(Widget_text)
        layout_text.addWidget(self.button_Show_preview, 0, 1)
        
        # Widget_Custom = QtWidgets.QWidget()
        # Widget_Custom.setMaximumWidth(self.max_width)
        # Widget_Custom.setObjectName('Widget_Custom')
        # Widget_Custom.setStyleSheet("#Widget_Custom {border: 2px solid green; border-radius: 10px;}")
        
        # layout_Custom = QtWidgets.QGridLayout(Widget_Custom)

        # layout_Custom.addWidget(self.label_comments, 1, 1)
        # layout_Custom.addWidget(self.label_delimiter, 2, 1)
        # layout_Custom.addWidget(self.label_skiprows, 3, 1)
        # layout_Custom.addWidget(self.button_Open_custom, 4, 1)
        
        
        # layout_Custom.addWidget(self.label_loadtxt_comments, 1, 2)
        # layout_Custom.addWidget(self.combobox_loadtxt_delimiter, 2, 2)
        # layout_Custom.addWidget(self.label_loadtxt_skiprows, 3, 2)
        
        #Plot Widget
        Widget_Plot = QtWidgets.QWidget()
        Widget_Plot.setMaximumWidth(self.max_width)
        Widget_Plot.setObjectName('Widget_Close')
        Widget_Plot.setStyleSheet("#Widget_Close {border: 2px solid blue; border-radius: 10px;}")
        
        layout_Plot = QtWidgets.QGridLayout(Widget_Plot)
        layout_Plot.addWidget(self.button_Plot_data, 1, 1)
        layout_Plot.addWidget(self.label_plot_x, 2, 1)
        layout_Plot.addWidget(self.label_plot_y, 3, 1)
        layout_Plot.addWidget(self.combobox_Plot_data_column_x, 2, 2)
        layout_Plot.addWidget(self.combobox_Plot_data_column_y, 3, 2)
        layout_Plot.addWidget(self.button_Delete_plot, 4, 1)
        layout_Plot.addWidget(self.combobox_button_Delete_plot, 4, 2)

        #Accept Close Widget
        Widget_Close = QtWidgets.QWidget()
        Widget_Close.setMaximumWidth(self.max_width)
        Widget_Close.setObjectName('Widget_Close')
        Widget_Close.setStyleSheet("#Widget_Close {border: 2px solid blue; border-radius: 10px;}")
        
        layout_Close = QtWidgets.QGridLayout(Widget_Close)
        layout_Close.addWidget(self.button_Accept, 1, 1)
        layout_Close.addWidget(self.combobox_Accept_data_column_x, 1, 2)
        layout_Close.addWidget(self.combobox_Accept_data_column_y, 1, 3)
        layout_Close.addWidget(self.button_Cancel, 2, 1, 1, 3) #, columnSpan = 3)

        #About Widget
        Widget_About = QtWidgets.QWidget()
        Widget_About.setMaximumWidth(self.max_width)
        Widget_About.setObjectName('Widget_About')
        #Widget_About.setStyleSheet("#Widget_Close {border: 2px solid blue; border-radius: 10px;}")
        
        layout_About = QtWidgets.QGridLayout(Widget_About)
        layout_About.addWidget(self.button_about, 1, 1)
        
        #Final layout
        
        layout_controls = QtWidgets.QVBoxLayout()
        
        layout_controls.addWidget(Widget_About)
        layout_controls.addWidget(Widget_text)
        layout_controls.addWidget(Widget_Open)
        #layout_controls.addWidget(Widget_Custom)
        layout_controls.addWidget(Widget_numpy)
        
        layout_controls.addWidget(Widget_Plot)
        layout_controls.addWidget(Widget_Close)
        
        layout_controls.setAlignment(QtCore.Qt.AlignTop)
        # layout_controls = QtWidgets.QVBoxLayout()
        
        # layout_controls.addWidget(button_Open_csv)
        # layout_controls.addWidget(button_Open_dat)
        # layout_controls.addWidget(button_Open_custom)
        # #layout_controls.addWidget(self.combo)
        
        # layout_controls.addWidget(button_Accept)
        # layout_controls.addWidget(button_Cancel)
        # layout_controls.setAlignment(QtCore.Qt.AlignTop)
        
        self.setLayout(layout_controls)
        
        self.setSizePolicy(
            QtWidgets.QSizePolicy.Fixed,
            QtWidgets.QSizePolicy.Fixed)
    
    def open_about(self):
        if self.about is not None:
            self.about.show()
            
    def command_button_comments(self):
        title = 'New comment character'
        label = 'The characters or list of characters used to indicate the start of a comment'

        new_value, ok = QtWidgets.QInputDialog.getText(self, title, label)
        if ok:
            self.loadtxt_comments = list(new_value)
            self.open_button_comments.setText(new_value)
            self.model.statusbar_message('Commented lines (ch) = ' + '|'.join(self.loadtxt_comments))
    
    def command_button_skiprows(self):
        title = 'New skip lines number'
        label = 'Skip the first n lines, including comments'

        new_value, ok = QtWidgets.QInputDialog.getInt(self, title, label, self.loadtxt_skiprows, 0)
        if ok:
            self.loadtxt_skiprows = new_value
            self.open_button_skiprows.setText(str(new_value))
            self.model.statusbar_message('Skip the first ' + str(self.loadtxt_skiprows0 + ' lines, including comments'))
            
    def error_box(self, title : str):
        msgBox = QtWidgets.QMessageBox()
        msgBox.setIcon(QtWidgets.QMessageBox.Critical)
        msgBox.setWindowTitle(str(title))
        msgBox.setText(traceback.format_exc())
        msgBox.setStandardButtons(QtWidgets.QMessageBox.Ok)
        msgBox.exec()
    
    def error_message(self, title : str, error : str):
        msgBox = QtWidgets.QMessageBox()
        msgBox.setIcon(QtWidgets.QMessageBox.Critical)
        msgBox.setWindowTitle(title)
        msgBox.setText(error)
        msgBox.setStandardButtons(QtWidgets.QMessageBox.Ok)
        msgBox.exec()
        
    def open_Show_preview(self):
        self.fileName, _ = QtWidgets.QFileDialog.getOpenFileName(self,"Select File")
        if self.fileName:
            self.model.statusbar_message(message = "Open plain text")
            self.show_text_file = show_text_file(self.fileName)
            self.show_text_file.show()
            
    def combobox_loadtxt_delimiter_index_changed(self):
        index = self.combobox_decimal_separator.currentIndex()
        # if index = 0:
        #     self.loadtxt_delimiter
        # elif index == 1 :
        #     ['space', 'tab', 'comma ,', 'semicolon ;']
        
        #setItemText
    
    def combobox_decimal_separator_index_changed(self):
        index = self.combobox_decimal_separator.currentIndex()
        if self.debug : print(f'combobox_decimal_separator = {index}')
        if index == 0: # point .
            self.button_Open_csv.setText("Open comma delimiter (csv)")
            self.model.statusbar_message(message = "'Decimal separator = point .")
            self.combobox_loadtxt_delimiter.setItemText(2, 'comma ,')
        elif index == 1: # comma ,
            self.button_Open_csv.setText("Open semicolon delimiter (csv)")
            self.model.statusbar_message(message = "'Decimal separator = comma ,")
            self.combobox_loadtxt_delimiter.setItemText(2, 'point .')
    
    def open_data_File_csv(self):
        
        index = self.combobox_decimal_separator.currentIndex()
        if self.debug : print('open_data_File_csv')
        if index == 0: # point .
            self.open_data_File(delimiter=',')
            self.model.statusbar_message(message = "Open comma delimiter (csv)")
        elif index == 1: # comma ,
            self.open_data_File(delimiter=';')
            self.model.statusbar_message(message = "Open semicolon delimiter (csv)")
    

    
    def change_loadtxt_skiprows(self):
        try :
            text = self.label_loadtxt_skiprows.text()
            self.loadtxt_skiprows = int(text)
            self.model.statusbar_message('Skip first (n) lines = ' + self.label_loadtxt_skiprows.text())
            self.label_loadtxt_skiprows.setPlaceholderText(text)

        
        except Exception:
            self.model.error_box('open_file_commands change_loadtxt_skiprows')
            self.model.statusbar_message('Skip first (n) lines = ' + self.loadtxt_skiprows)
            
    def change_loadtxt_comments(self):
        
        try :
            text = self.label_loadtxt_comments.text()
            self.loadtxt_comments = text
            message='Commented lines (ch) = '
            for i in text:
                message = message + i
            self.model.statusbar_message(message)
            self.label_loadtxt_comments.setPlaceholderText(text)

        
        except Exception:
            self.model.error_box('open_file_commands change_loadtxt_comments')
            self.model.statusbar_message('invalid value, Commented lines (ch) =' + self.loadtxt_comments)
    
    def print_time(self, event = None, Message = 'Now = '):
        now = datetime.now()
        current_time = now.strftime("%A %d %B %Y %H:%M:%S")
        print(Message + current_time) 
        
    def open_data_File_custom(self):
        self.flag_custom_file = True
        
        self.fileName, _ = QtWidgets.QFileDialog.getOpenFileName(self,"Select File")
        try:
            
            if self.fileName:
                if self.debug: print(self.fileName)
                
                loadtxt_delimiter = self.combobox_loadtxt_delimiter.currentText()
                #['space', 'tab', 'comma ,', 'semicolon ;']
                
                if loadtxt_delimiter == 'space':
                    self.loadtxt_delimiter = ' '
                elif loadtxt_delimiter == 'tab' :
                    self.loadtxt_delimiter = '\t'
                elif loadtxt_delimiter == 'comma ,' :
                    self.loadtxt_delimiter = ','
                elif loadtxt_delimiter == 'semicolon ;' :
                    self.loadtxt_delimiter = ';'
                elif loadtxt_delimiter == 'point .':
                    self.loadtxt_delimiter = '.'
                    
                index = self.combobox_decimal_separator.currentIndex()
                
                
                # if index == 0: # point .
                #     s = self.fileName
                # elif index == 1: # comma ,
                #     s = open(self.fileName).read().replace(',','.')
                #if self.debug: 
                    
                if self.debug: print(f'delim = {loadtxt_delimiter} = |{self.loadtxt_delimiter}| decimal = |{index}|0=. 1=,')
                _ = ''
                for i in self.loadtxt_delimiter:
                    _ = _ + i
                if self.debug: print(f'comments = {self.loadtxt_comments} delim = {_} skip = {self.loadtxt_skiprows}')
                message = f'comments = {self.loadtxt_comments} delim = {self.loadtxt_delimiter} skip = {self.loadtxt_skiprows}'
                self.model.statusbar_message(message)
                
                self.file_data = np.loadtxt(self.fileName, dtype = str, 
                                             comments = self.loadtxt_comments, 
                                             delimiter = self.loadtxt_delimiter,
                                             skiprows = self.loadtxt_skiprows)
                if self.debug: print(self.file_data)
                # print(self.loadtxt_comments)
                # print(self.loadtxt_delimiter)
                # print(self.loadtxt_skiprows)
                # print(len(self.file_data.shape))
                
                if len(self.file_data.shape) == 2:
                    self.signal_fill_str_table.emit(self.file_data)
                    try:
                        a = self.file_data[:,0].astype(float)
                        b = self.file_data[:,1].astype(float)
                        c = np.column_stack((a,b))
                        self.signal_plot_data.emit(c)
                    except:
                        self.error_message('column 1 or column 2 contains text that cannot be converted to numbers')
                else:
                    self.error_message('Open data file error', 'Data must be in a 2D format, at least 2 lines 2 columns')
                
        except Exception:
            self.error_box('open_file_commands open_data_File_custom')
            
    def open_data_File_npy(self, delimiter = ''):
        self.model.statusbar_message(message = "Open numpy npy")
        self.fileName, _ = QtWidgets.QFileDialog.getOpenFileName(self,"Select File", filter = "numpy files (*.npy)")
        try:
            if self.fileName:
                if self.debug: print(self.fileName)
                self.file_data= np.load(self.fileName)
                
                if len(self.file_data.shape) == 2:
                    self.signal_plot_data.emit(self.file_data)
                    self.signal_fill_float_table.emit(self.file_data)
                else:
                    self.error_message('Open numpy data file error', 'Data must be in a 2D format, at least 2 lines 2 columns')
                    
        except Exception:
            self.error_box('open_file_commands open_data_File_npy')
        
    
    def open_data_File(self, delimiter = ''):
        self.flag_custom_file = False
        self.fileName, _ = QtWidgets.QFileDialog.getOpenFileName(self,"Select File")
        try:
            if self.fileName:
                index = self.combobox_decimal_separator.currentIndex()
                if index == 0: # point .
                    self.file_data= np.loadtxt(self.fileName, delimiter = delimiter)
                elif index == 1: # comma ,
                    s = open(self.fileName).read().replace(',','.')
                    self.file_data= np.loadtxt(StringIO(s), delimiter = delimiter)
                
                if len(self.file_data.shape) == 2:
                    self.signal_plot_data.emit(self.file_data)
                    self.signal_fill_float_table.emit(self.file_data)
                else:
                    self.error_message('Open data file error', 'Data must be in a 2D format, at least 2 lines 2 columns')
                    
                if self.debug: print(self.fileName)
                if self.debug: print(self.file_data)
        except Exception:
            self.error_box('open_file_commands open_data_File')
                
    
            
    def open_data_File_dat(self):
        self.model.statusbar_message(message = "Open space delimiter")
        self.open_data_File(delimiter= None) 
    
    def open_data_File_tab(self):
        self.model.statusbar_message(message = "Open tab delimiter")
        self.open_data_File(delimiter='\t')
            
    
    def data_to_model(self, data):
        #Data to model
        self.model.ndarray_from_file = self.ndarray_from_file
        self.model.x_data_from_file = self.ndarray_from_file[:,0] 
        self.model.x_data_from_file = self.ndarray_from_file[:,1] 
   
    def app_quit(self):
        self.signal_quit.emit()
    
    def app_accept_quit(self):

        file_data_i_x = self.combobox_Accept_data_column_x.currentIndex()
        file_data_i_y = self.combobox_Accept_data_column_y.currentIndex()
        print(file_data_i_x)
        print(file_data_i_y)
        try:
            if self.file_data is not None:
                self.file_data = self.file_data.astype(float)
                file_data_i_x = self.combobox_Accept_data_column_x.currentIndex()
                file_data_i_y = self.combobox_Accept_data_column_y.currentIndex()
                try:
                    file_data_x = self.file_data[:, file_data_i_x].astype(float)
                    file_data_y = self.file_data[:, file_data_i_y].astype(float)
                    self.signal_selected_data_all.emit(self.file_data, self.fileName)
                    self.signal_selected_data_xy.emit(file_data_x, file_data_y, self.fileName)
                    self.signal_quit.emit()
                except:
                    print('error')
                    choice = QtWidgets.QMessageBox.question(self, "Quit", "Data conversion to numbers failed, exit without data?", QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
                    QtWidgets.QMessageBox()
                    if choice == QtWidgets.QMessageBox.Yes:
                        self.signal_quit.emit()
                        self.signal_selected_data_all.emit(self.file_data, self.fileName)
            else:
                self.signal_quit.emit()
        except Exception:
            self.error_box('open_file_commands app_accept_quit')
        
class Frame_1_graph(QtWidgets.QFrame):
    
    signal_fig_on_click = QtCore.pyqtSignal(MouseEvent)
    signal_fig_click_no_drag = QtCore.pyqtSignal(MouseEvent)
    signal_fig_click_drag = QtCore.pyqtSignal(MouseEvent)
    
    def __init__(self, model, debug = False):
        
        super().__init__()
        self.model = model
        self.debug = debug
        if self.debug: print("\nDebug mode\n")
        if self.debug: self.setStyleSheet("border: 20px solid red")
        
        layout = QtWidgets.QVBoxLayout()
        
        self.fig_ref = [] #List of plot ref
        self.fig_ref_names = [] #List of plot names
        self.x_min_all = np.inf
        self.x_max_all = -np.inf
        self.y_min_all = np.inf
        self.y_max_all = -np.inf
        self.total_plot_n = 0 
        
        self.fig = plt.figure(figsize=(5, 5))
        self.canvas = FigureCanvas(self.fig)
        self.canvas.mpl_connect('button_press_event', self.on_click)
        self.canvas.mpl_connect('button_release_event', self.off_click)
        
        self.navigationToolbar = NavigationToolbar(self.canvas, self, coordinates=True)
        self.ax = self.fig.add_subplot(111)
        self.ax.grid()
        self.x_moving_ref_left = 0 #Ref to detect drag
        self.y_moving_ref_left = 0 #Ref to detect drag
        #self.navigationToolbar.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        
        # show canvas
        self.canvas.show()
        
        # create main layout

        layout.addWidget(self.canvas)
        layout.addWidget(self.navigationToolbar)

        self.setLayout(layout)
        
        self.plot_ref = None
        self.data_x = None
        self.data_y = None
        self.plot_simple_calib_ref = None
    
    def error_box(self, title):
        msgBox = QtWidgets.QMessageBox()
        msgBox.setIcon(QtWidgets.QMessageBox.Critical)
        msgBox.setWindowTitle(str(title))
        msgBox.setText(traceback.format_exc())
        msgBox.setStandardButtons(QtWidgets.QMessageBox.Ok)
        msgBox.exec()
        
    def on_click(self, event):
        if self.debug: print('on_click')
        self.x_moving_ref_left = event.xdata
        self.y_moving_ref_left = event.ydata
        self.signal_fig_on_click.emit(event)
    
    def off_click(self, event):
        if self.debug: print('off_click')
        _x = event.xdata
        _y = event.ydata
        not_moved = ((self.x_moving_ref_left == _x) and (self.y_moving_ref_left == _y))
        if not_moved:
            self.signal_fig_click_no_drag.emit(event)
        else:
            self.signal_fig_click_drag.emit(event)
    
    def reset(self):
        self.ax.cla()
        self.fig_ref = []
        self.fig_ref_names = []
        self.total_plot_n = 0 
        
    def plot_data(self, data):
        self.reset()
        
        self.data_x = data[:,0]
        self.data_y = data[:,1]
        
        self.ax.grid()
        plot_label = 'Col_X 1 Col_Y 2'
        ref, = self.ax.plot(self.data_x, self.data_y, '-o', label = plot_label)
        self.total_plot_n+= 1
        self.fig_ref.append(ref)
        self.fig_ref_names.append(plot_label)
        leg = self.ax.legend()
        leg.set_draggable(True)
        self.canvas.draw()
    
    def delete_plot(self, element):
        try:
            if self.debug: print(f'pop {element}')
            _ = self.fig_ref.pop(element)
            _.remove()
            self.fig_ref_names.pop(element)
            leg = self.ax.legend()
            leg.set_draggable(True)
            self.autoscale_ax()
            self.canvas.draw()
        except Exception:
            self.error_box('Frame_1_graph delete_plot')

    def add_plot(self, data_x, data_y = None, plot_label = None):
        if data_y is None:
            data_y = data_x[:,1]
            data_x = data_x[:,0]
        i = self.total_plot_n
        #plot_label = f'Plot {i}'
        self.total_plot_n+= 1
        ref, = self.ax.plot(data_x, data_y, '-o', label = plot_label)
        self.fig_ref.append(ref)
        self.fig_ref_names.append(plot_label)
        
        leg = self.ax.legend()
        leg.set_draggable(True) 
        self.autoscale_ax()
        self.canvas.draw()
    
    def autoscale_ax(self):
        try:
            border = 0.1
            max_x = -np.inf
            max_y = -np.inf
            min_x = np.inf
            min_y = np.inf
            lines = self.ax.get_lines()
            for line in lines:
                x_data = line.get_xdata()
                y_data = line.get_ydata()
                max_x = max(max_x, x_data.max())
                max_y = max(max_y, y_data.max())
                min_x = min(min_x, x_data.min())
                min_y = min(min_y, y_data.min())
            
            border_x = (max_x - min_x)*border/2
            border_y = (max_y - min_y)*border/2
            self.ax.set_xlim(min_x-border_x, max_x+border_x)
            self.ax.set_ylim(min_y-border_y, max_y+border_y)
        except:
            #No graph, do nothing
            pass
    
    def rescale_xy(self, event = None):
        x_min = self.x_min_all
        x_max = self.x_max_all
        x_range = (x_max -x_min)*0.05*np.array((-1,1))+np.array((x_min,x_max))
        self.ax_Spectro.set_xlim(x_range)
        if self.debug: print('Rescale x')
        y_min = self.intensities.min()
        y_max = self.intensities.max()
        y_range = (y_max -y_min)*0.05*np.array((-1,1))+np.array((y_min,y_max))
        self.ax_Spectro.set_ylim(y_range)
        if self.debug: print('Rescale y')
        
    def rescale_x(self):
        x_min = self.x_min_all
        x_max = self.x_max_all
        x_range = (x_max -x_min)*0.05*np.array((-1,1))+np.array((x_min,x_max))
        self.ax_Spectro.set_xlim(x_range)
        if self.debug: print('Rescale x')

    def rescale_y(self):
        y_min = self.y_min_all
        y_max = self.y_max_all
        y_range = (y_max -y_min)*0.05*np.array((-1,1))+np.array((y_min,y_max))
        self.ax.set_ylim(y_range)
        self.canvas.draw()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.setStyleSheet("""
                      * {
                          font-size: 15px;
                    }
                      """)
    #from OF_Model_11 import my_model
    model = None
    #window = Frame_1_graph(model)
    #window = Fig_2_Commands(model)
    #window = Fine_calib_Commands(model)
    #window= Data_Table_Points(model)
    #window = Frame_1_graph(model)
    window = open_file_commands(model)
    #window =  show_text_file()
    window.show()
    sys.exit(app.exec())