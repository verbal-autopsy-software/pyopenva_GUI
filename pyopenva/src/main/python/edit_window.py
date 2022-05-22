# -*- coding: utf-8 -*-

"""
pyopenva.edit_window
~~~~~~~~~~~~~~
This module creates the window for editing data.
"""

from pickle import TRUE
from PyQt5.QtWidgets import (QTableView, QMainWindow)
from PyQt5.QtCore import QAbstractTableModel, Qt, QSortFilterProxyModel

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
    
    def column_name(self, column, role):
        if role == Qt.DisplayRole:
            return self.data[0][column]


class EditData(QMainWindow):

    def __init__(self, data):
        super().__init__()
        
        self.table = QTableView() 
        self.model = TableModel(data)
        self.sort_model = QSortFilterProxyModel()
        self.sort_model.setSourceModel(self.model)
        # self.table.setModel(self.model)
        self.table.setModel(self.sort_model)
        self.setCentralWidget(self.table)
    