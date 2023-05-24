# -*- coding: utf-8 -*-

"""
pyopenva.output
~~~~~~~~~~~~~~
This module creates displays for the algorithm results.
"""
import pandas as pd
from PyQt5.QtCore import QAbstractTableModel, Qt
from PyQt5.QtWidgets import (QApplication, QDialog, QMessageBox, QPushButton,
                             QTableView, QVBoxLayout)
from matplotlib.backends.backend_qt5agg import (FigureCanvasQTAgg,
                                                NavigationToolbar2QT)
from matplotlib.figure import Figure
from matplotlib import style
from matplotlib.pyplot import get_cmap
from numpy import linspace
from interva import utils


class PlotDialog(QDialog):

    def __init__(self, results, algorithm, parent=None, top=5, save=False,
                 file_name=None, colors="Greys", age="all deaths",
                 sex="all deaths", interva_rule=False):
        super(PlotDialog, self).__init__(parent=parent)
        self.setWindowTitle("Cause-Specific Mortality Fraction")
        self.results = results
        self.n_top_causes = top
        style.use("ggplot")
        self.figure = Figure(figsize=(7, 5), dpi=100, constrained_layout=True)
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.toolbar = NavigationToolbar2QT(self.canvas, self)
        self.colors = colors
        self.age = age
        self.sex = sex
        self.interva_rule = interva_rule

        vbox_csmf = QVBoxLayout()
        vbox_csmf.addWidget(self.toolbar)
        vbox_csmf.addWidget(self.canvas)
        self.setLayout(vbox_csmf)
        if algorithm == "insilicova":
            self.plot_dot_whisker()
        else:
            self.plot()
        if save:
            try:
                self.figure.savefig(file_name)
            except (OSError, PermissionError):
                alert = QMessageBox()
                alert.setWindowTitle("openVA App")
                alert.setIcon(QMessageBox.Warning)
                alert.setText(
                    f"Unable to save {file_name}.\n" +
                    "(don't have permission or read-only file system)")
                alert.exec()
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
        age = self.age
        if self.age == "all deaths":
            age = None
        sex = self.sex
        if self.sex == "all deaths":
            sex = None
        # plt_series = self.results.get_csmf(top=self.n_top_causes)
        plt_series = utils.csmf(self.results, top=self.n_top_causes,
                                interva_rule=self.interva_rule,
                                age=age, sex=sex)
        plt_series.sort_values(ascending=True, inplace=True)
        cm_colors = get_cmap(self.colors)
        linspace_colors = linspace(0.5, 0.9, self.n_top_causes)
        colors = cm_colors(linspace_colors)
        self.ax.barh(plt_series.index.to_list(),
                     plt_series.to_list(),
                     color=colors)
        title = _make_title(age=self.age, sex=self.sex)
        self.ax.set(title=title)

    def plot_dot_whisker(self):
        plt_df = self.results.get_csmf(top=self.n_top_causes).copy()
        plt_df.sort_values(by="Median", ascending=True, inplace=True)
        errors = [plt_df["Lower"].to_list(), plt_df["Upper"].to_list()]
        cm_colors = get_cmap(self.colors)
        linspace_colors = linspace(0.5, 0.9, self.n_top_causes)
        colors = cm_colors(linspace_colors)
        for i in range(self.n_top_causes):
            clr = colors[i].tolist()
            self.ax.errorbar(x=plt_df["Median"].to_list()[i],
                             y=plt_df.index.to_list()[i],
                             xerr=[[errors[0][i]], [errors[1][i]]],
                             ecolor=clr,
                             markerfacecolor=clr, markeredgecolor=clr,
                             fmt="o",
                             capsize=5)
        self.ax.grid(alpha=0.5, linestyle=":")
        self.ax.set(title="Top CSMF Distribution")
        self.ax.set_xlabel("CSMF")
        self.ax.set_ylabel("Causes")


class TableDialog(QDialog):

    def __init__(self, results, parent=None, top=5,
                 age="all deaths", sex="all deaths", interva_rule=False):
        super(TableDialog, self).__init__(parent=parent)
        self.setWindowTitle("Cause-Specific Mortality Fraction")
        self.results = results
        self.n_top_causes = top
        self.interva_rule = interva_rule
        self.age = age
        self.sex = sex
        age = self.age
        if self.age == "all deaths":
            age = None
        sex = self.sex
        if self.sex == "all deaths":
            sex = None

        self.table = QTableView()
        self.table.setShowGrid(False)

        csmf = self.results.get_csmf(top=self.n_top_causes)
        if isinstance(csmf, pd.DataFrame):
            csmf_df = csmf.sort_values(by="Mean", ascending=False).copy()
            csmf_df = csmf_df.reset_index()
            csmf_df.rename(columns={"index": "Cause", "Mean": "CSMF (Mean)"},
                           inplace=True)
        else:
            csmf = utils.csmf(self.results, top=self.n_top_causes,
                              interva_rule=self.interva_rule,
                              age=age, sex=sex)
            csmf.sort_values(ascending=False, inplace=True)
            csmf_df = csmf.reset_index()[0:self.n_top_causes]
            title = _make_title(age=self.age, sex=self.sex)
            csmf_df.rename(columns={"index": "Cause", 0: title},
                           inplace=True)
        self.model = TableModel(csmf_df.round(4))
        self.table.setModel(self.model)
        column_width_0 = self.table.sizeHintForColumn(0) + 100
        column_width_1 = self.table.sizeHintForColumn(1) + 100
        # self.table.resizeColumnToContents(0)
        self.table.setColumnWidth(0, column_width_0)
        self.table.setColumnWidth(1, column_width_1)


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


def save_plot(results, algorithm, top=5, file_name=None, plot_colors="Greys",
              age="all deaths", sex="all deaths", interva_rule=False):
    age_grp = age
    if age == "all deaths":
        age_grp = None
    sex_grp = sex
    if sex == "all deaths":
        sex_grp = None

    style.use("ggplot")
    figure = Figure(figsize=(7, 5), dpi=100, constrained_layout=True)
    ax = figure.add_subplot(111)
    if algorithm == "insilicova":
        plt_df = results.get_csmf(top=top).copy()
        plt_df.sort_values(by="Median", ascending=True, inplace=True)
        errors = [plt_df["Lower"].to_list(), plt_df["Upper"].to_list()]
        ax.errorbar(x=plt_df["Median"].to_list(),
                    y=plt_df.index.to_list(),
                    xerr=errors,
                    ecolor="black",
                    markerfacecolor="black", markeredgecolor="black",
                    fmt="o",
                    capsize=5)
        ax.grid(alpha=0.5, linestyle=":")
        ax.set(title="Top CSMF Distribution")
        ax.set_xlabel("CSMF")
        ax.set_ylabel("Causes")
    else:
        # plt_series = results.get_csmf(top=top)
        plt_series = utils.csmf(results, top=top,
                                interva_rule=interva_rule,
                                age=age_grp, sex=sex_grp)
        plt_series.sort_values(ascending=True, inplace=True)
        cm_colors = get_cmap(plot_colors)
        linspace_colors = linspace(0.5, 0.9, top)
        colors = cm_colors(linspace_colors)
        ax.barh(plt_series.index.to_list(),
                plt_series.to_list(),
                color=colors)
        title = _make_title(age=age_grp, sex=sex_grp)
        ax.set(title=title)
    try:
        figure.savefig(file_name)
    except (OSError, PermissionError):
        alert = QMessageBox()
        alert.setWindowTitle("openVA App")
        alert.setIcon(QMessageBox.Warning)
        alert.setText(
            f"Unable to save {file_name}.\n" +
            "(don't have permission or read-only file system)")
        alert.exec()


def _make_title(age, sex):
    title = "CSMF"
    if sex == "female" and age == "all deaths":
        title = "CSMF for females"
    if sex == "female" and age == "adult":
        title = "CSMF for female adults"
    if sex == "female" and age == "child":
        title = "CSMF for female children"
    if sex == "female" and age == "neonate":
        title = "CSMF for female neonates"
    if sex == "male" and age == "all deaths":
        title = "CSMF for males"
    if sex == "male" and age == "adult":
        title = "CSMF for male adults"
    if sex == "male" and age == "child":
        title = "CSMF for male children"
    if sex == "male" and age == "neonate":
        title = "CSMF for male neonates"
    if sex == "all deaths" and age == "adult":
        title = "CSMF for adults"
    if sex == "all deaths" and age == "child":
        title = "CSMF for children"
    if sex == "all deaths" and age == "neonate":
        title = "CSMF for neonates"
    return title
