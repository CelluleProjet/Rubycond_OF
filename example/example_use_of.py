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

import sys
from rubycond_OF.rubycond_OF import open_file

from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Rubycond_of Use Example")

        button = QPushButton("Open File")
        button.clicked.connect(self.show_open_file)
        self.setCentralWidget(button)
        
        #Signal Slot Connection
        
        self.open_file = open_file()
        self.open_file.commands.signal_selected_data_xy.connect(self.open_file_command_xy)
        self.open_file.commands.signal_selected_data_all.connect(self.open_file_command_all)

    def show_open_file(self):
        self.open_file.show()
        
    def open_file_command_xy(self, data_x, data_y, filename):
        print()
        print('_/‾\\'*20)
        print()
        print("Read only 2 columns, selected X and Y")
        print()
        print(f"filename = {filename}")
        print()
        print("Data x = ")
        print()
        print(data_x)
        print()
        print("Data y = ")
        print()
        print(data_y)
        print()
        print('_/‾\\'*20)
        print()

    def open_file_command_all(self, data, filename):
        print()
        print('_/‾\\'*20)
        print()
        print("Read all data")
        print()
        print(f"filename = {filename}")
        print()
        print("All data = ")
        print()
        print(data)
        print()
        print('_/‾\\'*20)
        print()
        
app = QApplication(sys.argv)
app.setStyleSheet("""
                  * {
                      font-size: 20px;
                }
                  """)
window = MainWindow()
window.show()
app.exec()