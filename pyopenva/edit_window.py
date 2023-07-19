# -*- coding: utf-8 -*-

"""
pyopenva.edit_window
~~~~~~~~~~~~~~
This module creates the window for editing data.
"""

from pickle import TRUE
from PyQt5.QtWidgets import (QTableView, QMainWindow)
from PyQt5.QtCore import QAbstractTableModel, Qt, QSortFilterProxyModel
from PyQt5.QtWidgets import (QTableView, QMainWindow, QHeaderView, QLineEdit)
from PyQt5.QtCore import (QAbstractTableModel, Qt, QSortFilterProxyModel,
                          QModelIndex)


class TableModel(QAbstractTableModel):

    def __init__(self, data):
        super(TableModel, self).__init__()
        self.data = data

    def data(self, index, role):

        if role == Qt.DisplayRole:
            return self.data[index.row()][index.column()]

        if index.isValid():
            if role == Qt.DisplayRole or role == Qt.EditRole:
                value = self.data[index.row()][index.column()]
                return str(value)

    def setData(self, index, value, role):
        if role == Qt.EditRole:
            self.data[index.row()][index.column()] = value
            return True

    def rowCount(self, index):
        return len(self.data)

    def columnCount(self, index):
        return len(self.data[0])

    def flags(self, index):
        return Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable

    def column_name(self, column, role):
        if role == Qt.DisplayRole:
            return self.data[0][column]

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.data[0][section]


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


class EditableHeaderView(QHeaderView):

    def __init__(self, orientation, parent=None):
        super(EditableHeaderView, self).__init__(orientation,
                                                 parent)
        self.setSectionsMovable(True)
        self.setSectionsClickable(True)
        self.line = QLineEdit(parent=self.viewport())
        self.line.setAlignment(Qt.AlignTop)
        self.line.setHidden(True)
        self.line.blockSignals(True)
        self.sectionedit = 0

    def edit_header(self, section):
        edit_geometry = self.line.geometry()
        edit_geometry.setWidth(self.sectionSize(section))
        edit_geometry.moveLeft(self.sectionViewportPosition(section))
        self.line.setGeometry(edit_geometry)
        self.line.setText(self.model().headerData(section, Qt.Horizontal))
        self.line.setHidden(False)
        self.line.blockSignals(False)
        self.line.setFocus()
        self.line.selectAll()
        self.sectionedit = section

    def done_editing(self):
        self.line.blockSignals(True)
        self.line.setHidden(True)
        # oldname = self.model().headerData(self.sectionedit, Qt.Horizontal)
        newname = str(self.line.text())
        field = self.model().index(0, self.sectionedit)
        self.model().setData(field, newname)
        self.line.setText('')
        self.setCurrentIndex(QModelIndex())
