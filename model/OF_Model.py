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


import os
from datetime import datetime
from PyQt5 import QtWidgets

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

class my_model():
    def __init__(self, debug = False):
        self.version = 'OF_Model_11wwww'
        self.debug = debug
        if self.debug: print('\nModel\n')
        
        self.ndarray_from_file = None
        self.x_data_from_file = None
        self.y_data_from_file = None

        self.statusbar_message_ref = [print] #List of messages method (print, label, statusbar, etc)
    
    def statusbar_message(self, message):
        now = datetime.now()
        text = now.strftime("%H:%M:%S : ") + message
        for method in self.statusbar_message_ref:
            method(text)

    def error_box(self, error):
        msgBox = QtWidgets.QMessageBox()
        msgBox.setIcon(QtWidgets.QMessageBox.Critical)
        msgBox.setWindowTitle("Script Error")
        msgBox.setText(str(error))
        msgBox.setStandardButtons(QtWidgets.QMessageBox.Ok)
        msgBox.exec()
    
    def statusbar_message_add(self, method):
        self.statusbar_message_ref.append(method)
