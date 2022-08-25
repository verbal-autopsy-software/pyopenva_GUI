# -*- coding: utf-8 -*-

"""
pyopenva.output
~~~~~~~~~~~~~~
This module creates displays for the algorithm results.
"""

from PyQt5.QtCore import QAbstractTableModel, Qt
from PyQt5.QtWidgets import (QApplication, QDialog, QPushButton, QTableView,
                             QVBoxLayout)
from matplotlib.backends.backend_qt5agg import (FigureCanvasQTAgg,
                                                NavigationToolbar2QT)
from matplotlib.figure import Figure
from matplotlib import style
from matplotlib.pyplot import get_cmap
from numpy import linspace


class PlotDialog(QDialog):

    def __init__(self, results, parent=None, top=5, save=False,
                 file_name=None):
        super(PlotDialog, self).__init__(parent=parent)
        self.setWindowTitle("Cause-Specific Mortality Fraction")
        self.results = results
        self.n_top_causes = top
        style.use("ggplot")
        self.figure = Figure(figsize=(7, 5), dpi=100, constrained_layout=True)
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.toolbar = NavigationToolbar2QT(self.canvas, self)

        vbox_csmf = QVBoxLayout()
        vbox_csmf.addWidget(self.toolbar)
        vbox_csmf.addWidget(self.canvas)
        self.setLayout(vbox_csmf)
        self.plot()
        if save:
            self.figure.savefig(file_name)
        else:
            self.canvas.draw()

        # self.btn_box = QDialogButtonBox(QDialogButtonBox.Cancel |
        #                                 QDialogButtonBox.Ok)
        # self.btn_box.accepted.connect(self.accept)
        # self.btn_box.accepted.connect(
        #     lambda:
        #     self.parent().update_interva_hiv(self.hiv))
        # self.btn_box.accepted.connect(
        #     lambda:
        #     self.parent().update_interva_malaria(self.malaria))
        # self.btn_box.rejected.connect(self.reject)

    def plot(self):
        plt_series = self.results.get_csmf(top=self.n_top_causes)
        plt_series.sort_values(ascending=True, inplace=True)
        cm_greys = get_cmap("Greys")
        linspace_greys = linspace(0.5, 0.9, self.n_top_causes)
        colors = cm_greys(linspace_greys)
        self.ax.barh(plt_series.index.to_list(),
                     plt_series.to_list(),
                     color=colors)
        self.ax.set(title="CSMF")


class TableDialog(QDialog):

    def __init__(self, results, parent=None, top=5):
        super(TableDialog, self).__init__(parent=parent)
        self.setWindowTitle("Cause-Specific Mortality Fraction")
        self.results = results
        self.n_top_causes = top

        self.table = QTableView()
        self.table.setShowGrid(False)

        csmf = self.results.get_csmf(top=self.n_top_causes)
        csmf.sort_values(ascending=False, inplace=True)
        csmf_df = csmf.reset_index()[0:self.n_top_causes]
        csmf_df.rename(columns={"index": "Cause", 0: "CSMF"},
                       inplace=True)
        self.model = TableModel(csmf_df.round(4))
        self.table.setModel(self.model)
        column_width = self.table.sizeHintForColumn(0) + 100
        # self.table.resizeColumnToContents(0)
        self.table.setColumnWidth(0, column_width)

        clipboard = QApplication.clipboard()
        self.btn_copy = QPushButton("Copy table to clipboard")
        self.btn_copy.pressed.connect(
            lambda: clipboard.setText(csmf_df.to_csv(index=False)))

        vbox_csmf = QVBoxLayout()
        vbox_csmf.addWidget(self.table)
        vbox_csmf.addWidget(self.btn_copy)
        self.setLayout(vbox_csmf)


class TableModel(QAbstractTableModel):

    def __init__(self, data):
        super(TableModel, self).__init__()
        self._data = data

    def data(self, index, role):
        if role == Qt.DisplayRole:
            value = self._data.iloc[index.row(), index.column()]
            return str(value)

    def rowCount(self, index):
        return self._data.shape[0]

    def columnCount(self, index):
        return self._data.shape[1]

    def headerData(self, section, orientation, role):
        # section is the index of the column/row.
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return str(self._data.columns[section])
            # if orientation == Qt.Vertical:
            #     return str(self._data.index[section])


def save_plot(results, top=5, file_name=None):

        style.use("ggplot")
        figure = Figure(figsize=(7, 5), dpi=100, constrained_layout=True)
        ax = figure.add_subplot(111)
        plt_series = results.get_csmf(top=top)
        plt_series.sort_values(ascending=True, inplace=True)
        cm_greys = get_cmap("Greys")
        linspace_greys = linspace(0.5, 0.9, top)
        colors = cm_greys(linspace_greys)
        ax.barh(plt_series.index.to_list(),
                plt_series.to_list(),
                color=colors)
        ax.set(title="CSMF")
        figure.savefig(file_name)
