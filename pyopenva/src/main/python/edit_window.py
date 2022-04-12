# -*- coding: utf-8 -*-

"""
pyopenva.edit_window
~~~~~~~~~~~~~~
This module creates the window for editing data.
"""

from PyQt5.QtWidgets import (QTableView, QMainWindow)
from PyQt5.QtCore import QAbstractTableModel, Qt

class TableModel(QAbstractTableModel):
    
    def __init__(self, data):
        super(TableModel, self).__init__()
        self.data = data
    
    def data(self, index, role):
        if role == Qt.DisplayRole:
            return self.data[index.row()][index.column()]

    def setData(self, index, value, role):
        if role == Qt.EditRole:
            self.data[index.row()][index.column()] = value
            return True
        
    def rowCount(self, index):
        return len(self.data)

    def columnCount(self, index):
        return len(self.data[0])
    
    def flags(self, index):
        return Qt.ItemIsSelectable|Qt.ItemIsEnabled|Qt.ItemIsEditable


class EditData(QMainWindow):

    def __init__(self, data):
        super().__init__()
        
        self.table = QTableView() 
        self.model = TableModel(data)
        self.table.setModel(self.model)
        self.setCentralWidget(self.table)
    