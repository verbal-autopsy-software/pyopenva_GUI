# -*- coding: utf-8 -*-

"""
pyopenva.load
~~~~~~~~~~~~~~
This module creates a window for loading a csv file.
"""

from PyQt5.QtWidgets import (QFileDialog, QMessageBox, QWidget)
import csv
from pandas import read_csv


class LoadData(QWidget):

    def __init__(self, input_fname=None):
        super().__init__()

        if input_fname:
            file_name = (input_fname, "")
        else:
            file_name = QFileDialog.getOpenFileName(self,
                                                    "Open csv file",
                                                    "",
                                                    "csv Files (*.csv)")
        self.fname = file_name[0]
        if file_name is not None and file_name[0] != "":
            header = []
            rows = []
            data = []
            try:
                with open(self.fname, "r", newline="") as file:
                    csvreader = csv.reader(file)
                    header.append(next(csvreader))
                    for row in csvreader:
                        rows.append(row)
                    data += header + rows
                self.header = header
                self.data = data
            except StopIteration:
                alert = QMessageBox()
                alert.setText(
                    f"Unable to analyze {self.fname}.\n\n"
                    "Data file contains zero records!")
                alert.exec()
                self.fname = ""
