# -*- coding: utf-8 -*-

"""
pyopenva.load
~~~~~~~~~~~~~~
This module creates a window for loading a csv file.
"""

from PyQt5.QtWidgets import (QWidget, QFileDialog)
import csv


class LoadData(QWidget):

    def __init__(self):
        super().__init__()
        
        file_name = QFileDialog.getOpenFileName(self,"Open csv file", "","csv Files (*.csv)")
        self.fname = file_name[0]
        if file_name is not None and file_name[0] != '':
            header = []
            rows = []
            data = []
            with open(self.fname, 'r', newline = '') as file:
                csvreader = csv.reader(file)
                header.append(next(csvreader))
                for row in csvreader:
                    rows.append(row)
                data += header + rows
            self.header = header
            self.data = data
