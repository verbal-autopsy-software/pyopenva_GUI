# -*- coding: utf-8 -*-

"""
pyopenva.output
~~~~~~~~~~~~~~
This module creates displays for the algorithm results.
"""
from PyQt5.QtCore import QAbstractTableModel, Qt
from PyQt5.QtWidgets import (QApplication, QCheckBox, QComboBox, QDialog,
                             QLabel, QMessageBox, QPushButton, QTableView,
                             QHBoxLayout, QVBoxLayout)
from matplotlib.backends.backend_qt5agg import (FigureCanvasQTAgg,
                                                NavigationToolbar2QT)
from matplotlib.figure import Figure
from matplotlib import style
from matplotlib.pyplot import get_cmap
from numpy import array, linspace, reshape
from pandas import crosstab, DataFrame, concat
from interva import utils


class PlotDialog(QDialog):

    def __init__(self, results, algorithm, parent=None, top=5, save=False,
                 file_name=None, colors="Greys", age="all deaths",
                 sex="all deaths", interva_rule=True, use_prop=False):
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
        self.prop_scale = 100  # show results as %
        if use_prop:
            self.prop_scale = 1

        vbox_csmf = QVBoxLayout()
        vbox_csmf.addWidget(self.toolbar)
        vbox_csmf.addWidget(self.canvas)
        self.setLayout(vbox_csmf)
        if algorithm == "insilicova":
            if self.age == "all deaths" and self.sex == "all deaths":
                self.plot_dot_whisker()
            else:
                self.plot_subpop()
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
        plt_series = self.prop_scale * plt_series
        cm_colors = get_cmap(self.colors)
        linspace_colors = linspace(0.5, 0.9, self.n_top_causes)
        colors = cm_colors(linspace_colors)
        self.ax.barh(plt_series.index.to_list(),
                     plt_series.to_list(),
                     color=colors)
        title = _make_title(age=self.age, sex=self.sex)
        self.ax.set(title=title)

    def plot_subpop(self):

        plt_series = _insilicova_subpop(self.results,
                                        self.age,
                                        self.sex,
                                        self.n_top_causes)
        plt_series = self.prop_scale * plt_series
        n_max = len(plt_series)
        cm_colors = get_cmap(self.colors)
        linspace_colors = linspace(0.5, 0.9, n_max)
        colors = cm_colors(linspace_colors)
        self.ax.barh(plt_series.index.to_list(),
                     plt_series.to_list(),
                     color=colors)
        title = _make_title(age=self.age, sex=self.sex)
        self.ax.set(title=title)

    def plot_dot_whisker(self):
        plt_df = self.results.get_csmf(top=self.n_top_causes).copy()
        plt_df.sort_values(by="Median", ascending=True, inplace=True)
        errors = [(plt_df["Median"] - plt_df["Lower"]).to_list(),
                  (plt_df["Upper"] - plt_df["Median"]).to_list()]
        cm_colors = get_cmap(self.colors)
        linspace_colors = linspace(0.5, 0.9, self.n_top_causes)
        colors = cm_colors(linspace_colors)
        for i in range(self.n_top_causes):
            clr = colors[i].tolist()
            self.ax.errorbar(x=self.prop_scale * plt_df["Median"].to_list()[i],
                             y=plt_df.index.to_list()[i],
                             xerr=[[self.prop_scale * errors[0][i]],
                                   [self.prop_scale * errors[1][i]]],
                             ecolor=clr,
                             markerfacecolor=clr, markeredgecolor=clr,
                             fmt="o",
                             capsize=5)
        self.ax.grid(alpha=0.5, linestyle=":")
        self.ax.set(title="Top CSMF Distribution")
        self.ax.set_xlabel("CSMF")
        self.ax.set_ylabel("Causes")


class TableDialog(QDialog):

    def __init__(self, results, parent=None, top=5, age="all deaths",
                 sex="all deaths", interva_rule=True, use_prop=False):
        super(TableDialog, self).__init__(parent=parent)
        self.setWindowTitle("Cause-Specific Mortality Fraction")
        self.results = results
        self.n_top_causes = top
        self.interva_rule = interva_rule
        self.prop_scale = 100  # show results as %
        if use_prop:
            self.prop_scale = 1
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
        if isinstance(csmf, DataFrame):
            if self.age == "all deaths" and self.sex == "all deaths":
                csmf_df = csmf.sort_values(by="Mean", ascending=False).copy()
            else:
                csmf_df = _insilicova_subpop(self.results,
                                             self.age,
                                             self.sex,
                                             self.n_top_causes)
                csmf_df = csmf_df.sort_values(ascending=False)
                csmf_df.name = "Mean"
            csmf_df = csmf_df.reset_index()
            title = _make_title(age=self.age, sex=self.sex)
            csmf_df.rename(columns={"index": "Cause",
                                    "Mean": title},
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
        csmf_df.iloc[:, 1:] *= self.prop_scale  # ok for std error (sqrt (a * var[x]))
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


class DemTableDialog(QDialog):

    def __init__(self, results: DataFrame, parent=None):
        super(DemTableDialog, self).__init__(parent=parent)
        self.setWindowTitle("Demographic Table (age x sex)")
        self.results = results
        self.view = QTableView()
        self.view.setShowGrid(False)
        self.table_type = "counts"
        self.proportions = False
        self.margins = True
        self.table = self._make_table()

        self.model = TableModel(self.table)
        self.view.setModel(self.model)
        column_width_0 = self.view.sizeHintForColumn(0) + 100
        column_width_1 = self.view.sizeHintForColumn(1) + 100
        # self.table.resizeColumnToContents(0)
        self.view.setColumnWidth(0, column_width_0)
        self.view.setColumnWidth(1, column_width_1)

        options_type = ["counts", "% row", "% col", "% grand total"]
        label_table_type = QLabel("Type of table:")
        self.table_type_combo = QComboBox()
        self.table_type_combo.addItems(options_type)
        self.table_type_combo.setCurrentIndex(
            options_type.index(self.table_type))
        self.table_type_combo.currentTextChanged.connect(
            self.set_table_type)
        self.table_type_combo.currentTextChanged.connect(
            lambda: self._make_table()
        )
        self.check_margins = QCheckBox()
        self.check_margins.setChecked(True)
        self.check_margins.setText("Include margins")
        self.check_margins.stateChanged.connect(
            lambda: self.set_margins(self.check_margins))
        self.check_proportions = QCheckBox()
        self.check_proportions.setChecked(False)
        self.check_proportions.setEnabled(False)
        self.check_proportions.setText("Use proportions")
        self.check_proportions.stateChanged.connect(
            lambda: self.set_proportions(self.check_proportions))

        hbox_format = QHBoxLayout()
        hbox_format.addWidget(label_table_type)
        hbox_format.addWidget(self.table_type_combo)
        hbox_format.addWidget(self.check_margins)
        hbox_format.addWidget(self.check_proportions)

        clipboard = QApplication.clipboard()
        self.btn_copy = QPushButton("Copy table to clipboard")
        self.btn_copy.pressed.connect(
            lambda: clipboard.setText(self.table.to_csv(index=False)))

        vbox_csmf = QVBoxLayout()
        vbox_csmf.addWidget(self.view)
        vbox_csmf.addLayout(hbox_format)
        vbox_csmf.addWidget(self.btn_copy)
        self.setLayout(vbox_csmf)

    def _make_table(self):
        pct = 100
        if self.proportions or self.table_type == "counts":
            pct = 1
        normalize_dict = {"counts": False, "% row": "index",
                          "% col": "columns", "% grand total": "all"}
        normalize = normalize_dict[self.table_type]
        table = crosstab(self.results["sex"], self.results["age"],
                         normalize=normalize, margins=self.margins,
                         margins_name="Total") * pct
        if self.table_type == "% row" and self.margins:
            table["Total"] = table.sum(axis=1)
        elif self.table_type == "% col" and self.margins:
            table.loc[len(table.index)] = [1.0 * pct] * 4
            table = table.rename(index={2: "Total"})
        if self.proportions:
            table = table.round(3)
        elif self.proportions is False and self.table_type != "counts":
            table = table.round(1)
            table["adult"] = table["adult"].astype(str) + "%"
            table["child"] = table["child"].astype(str) + "%"
            table["neonate"] = table["neonate"].astype(str) + "%"
            if "Total" in table.columns:
                table["Total"] = table["Total"].astype(str) + "%"
        table = table.reset_index()
        return table

    def set_table_type(self, type_of_table):
        self.table_type = type_of_table
        if self.table_type == "counts":
            self.check_proportions.setEnabled(False)
        else:
            self.check_proportions.setEnabled(True)
        self.table = self._make_table()
        self.model = TableModel(self.table)
        self.view.setModel(self.model)

    def set_margins(self, check_btn):
        if check_btn.isChecked():
            self.margins = True
        else:
            self.margins = False
        self.table = self._make_table()
        self.model = TableModel(self.table)
        self.view.setModel(self.model)

    def set_proportions(self, check_btn):
        if check_btn.isChecked():
            self.proportions = True
        else:
            self.proportions = False
        self.table = self._make_table()
        self.model = TableModel(self.table)
        self.view.setModel(self.model)


class TableModel(QAbstractTableModel):

    def __init__(self, data):
        super(TableModel, self).__init__()
        self._data = data

    def data(self, index, role):
        if role == Qt.DisplayRole:
            value = self._data.iloc[index.row(), index.column()]
            return str(value)
        elif role == Qt.TextAlignmentRole:
            return Qt.AlignCenter

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
              age="all deaths", sex="all deaths", interva_rule=True,
              use_prop=False):
    age_grp = age
    if age == "all deaths":
        age_grp = None
    sex_grp = sex
    if sex == "all deaths":
        sex_grp = None
    prop_scale = 100  # show results as %
    if use_prop:
        prop_scale = 1

    style.use("ggplot")
    figure = Figure(figsize=(7, 5), dpi=100, constrained_layout=True)
    ax = figure.add_subplot(111)
    if algorithm == "insilicova":
        if age == "all deaths" and sex == "all deaths":
            plt_df = results.get_csmf(top=top).copy()
            plt_df.sort_values(by="Median", ascending=True, inplace=True)
            errors = [(plt_df["Median"] - plt_df["Lower"]).to_list(),
                      (plt_df["Upper"] - plt_df["Median"]).to_list()]
            cm_colors = get_cmap(plot_colors)
            linspace_colors = linspace(0.5, 0.9, top)
            colors = cm_colors(linspace_colors)
            for i in range(top):
                clr = colors[i].tolist()
                ax.errorbar(x=prop_scale * plt_df["Median"].to_list()[i],
                            y=plt_df.index.to_list()[i],
                            xerr=[[prop_scale * errors[0][i]],
                                  [prop_scale * errors[1][i]]],
                            ecolor=clr,
                            markerfacecolor=clr, markeredgecolor=clr,
                            fmt="o",
                            capsize=5)
            ax.grid(alpha=0.5, linestyle=":")
            ax.set(title="Top CSMF Distribution")
            ax.set_xlabel("CSMF")
            ax.set_ylabel("Causes")
        else:
            plt_series = _insilicova_subpop(results, age, sex, top)
            plt_series = prop_scale * plt_series
            n_max = len(plt_series)
            cm_colors = get_cmap(plot_colors)
            linspace_colors = linspace(0.5, 0.9, n_max)
            colors = cm_colors(linspace_colors)
            ax.barh(plt_series.index.to_list(),
                    plt_series.to_list(),
                    color=colors)
            title = _make_title(age=age, sex=sex)
            ax.set(title=title)

    else:
        # plt_series = results.get_csmf(top=top)
        plt_series = utils.csmf(results, top=top,
                                interva_rule=interva_rule,
                                age=age_grp, sex=sex_grp)
        plt_series.sort_values(ascending=True, inplace=True)
        plt_series = prop_scale * plt_series
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


def _insilicova_subpop(results, age, sex, n_top):
    age_groups = []
    sex_groups = []
    if age == "all deaths":
        age_groups = ["neonate", "child", "adult"]
    else:
        age_groups.append(age)
    if sex == "all deaths":
        sex_groups = ["female", "male"]
    else:
        sex_groups.append(sex)

    dem_groups = results.data_checked.apply(utils._get_dem_groups, axis=1)
    dem_groups = DataFrame(list(dem_groups)).set_index("ID")
    subpop_results = concat([results.indiv_prob, dem_groups], axis=1)
    subpop_index = (subpop_results["age"].isin(age_groups)) & (
        subpop_results["sex"].isin(sex_groups))
    subpop_results = subpop_results[subpop_index]

    subpop_results = subpop_results.drop(columns=["age", "sex"])
    csmf = subpop_results.mean(axis=0)
    csmf.sort_values(ascending=False, inplace=True)
    n_max = sum(csmf > 1e-5)
    if n_max > n_top:
        n_max = n_top
    csmf = csmf[range(n_max)]
    csmf.sort_values(ascending=True, inplace=True)

    return csmf
