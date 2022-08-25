# -*- coding: utf-8 -*-

"""
pyopenva.efficient
~~~~~~~~~~~~~~
This module creates a stacked layout to walk through the analysis step-by-step.
"""

from algorithms import InterVA5
from data import COUNTRIES
from pandas import read_csv
from PyQt5.QtCore import QAbstractTableModel, Qt
from PyQt5.QtWidgets import (QApplication, QComboBox, QDialog, QFileDialog,
                             QHBoxLayout, QLabel, QProgressBar, QPushButton,
                             QStackedLayout, QTableView, QVBoxLayout, QWidget)
from matplotlib.backends.backend_qt5agg import (FigureCanvasQTAgg,
                                                NavigationToolbar2QT)
from matplotlib.figure import Figure
from matplotlib import style


class MplCanvas(FigureCanvasQTAgg):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)


class Efficient(QWidget):

    def __init__(self):
        super().__init__()
        self.setGeometry(400, 400, 500, 400)
        self.setWindowTitle("Efficient Mode: Data")
        self.data_page = QWidget()
        self.data = None
        self.data_loaded = False
        self.data_ui()
        self.select_algorithm_page = QWidget()
        self.select_algorithm_ui()
        self.chosen_algorithm = "insilicova"
        self.insilicova_page = QWidget()
        self.insilicova_ui()
        self.interva_results = None
        self.interva_page = QWidget()
        self.interva_hiv = "low"
        self.interva_malaria = "low"
        self.interva_progress_bar = QProgressBar()
        self.interva_ui()
        self.smartva_page = QWidget()
        self.smartva_country = "Unknown"
        self.smartva_hiv = "True"
        self.smartva_malaria = "True"
        self.smartva_hce = "True"
        self.smartva_freetext = "True"
        self.smartva_ui()
        self.results_page = QWidget()
        self.btn_show_plot = None
        self.btn_show_table = None
        self.results_figure = None
        self.btn_download_plot = None
        self.btn_download_table = None
        self.btn_download_individual_results = None
        self.results_ui()
        self.stacked_layout = QStackedLayout()
        self.stacked_layout.addWidget(self.data_page)
        self.stacked_layout.addWidget(self.select_algorithm_page)
        self.stacked_layout.addWidget(self.insilicova_page)
        self.stacked_layout.addWidget(self.interva_page)
        self.stacked_layout.addWidget(self.smartva_page)
        self.stacked_layout.addWidget(self.results_page)

        self.main_layout = QVBoxLayout()
        self.main_layout.addLayout(self.stacked_layout)
        self.setLayout(self.main_layout)

    def data_ui(self):
        """Set up page for loading, editing, and checking the data."""

        layout = QVBoxLayout()
        self.btn_load_data = QPushButton("Load Data (.csv)")
        self.btn_load_data.clicked.connect(self.load_data)
        self.label_data = QLabel('(no data loaded)')

        label_data_format = QLabel("Data Format:")
        self.btn_data_format = QComboBox()
        self.btn_data_format.addItems(("WHO 2016 (v151)",
                                       "WHO 2012",
                                       "PHMRC"))
        self.btn_data_check = QPushButton("Data Check")

        h_box = QHBoxLayout()
        self.btn_go_to_mode = QPushButton("Back")
        self.btn_algorithm = QPushButton("Next")
        h_box.addWidget(self.btn_go_to_mode)
        h_box.addWidget(self.btn_algorithm)
        self.btn_algorithm.pressed.connect(self.show_select_algorithm_page)

        layout.addWidget(self.btn_load_data)
        layout.addWidget(self.label_data)
        layout.addStretch(2)
        layout.addWidget(label_data_format)
        layout.addWidget(self.btn_data_format)
        layout.addStretch(2)
        layout.addLayout(h_box)
        self.data_page.setLayout(layout)

    def select_algorithm_ui(self):
        layout = QVBoxLayout()
        label_select_algorithm = QLabel("Select which algorithm to use:")
        self.btn_insilicova = QPushButton("InSilicoVA")
        self.btn_insilicova.pressed.connect(self.show_insilicova_page)
        self.btn_insilicova.pressed.connect(
            lambda: self.set_chosen_algorithm("insilicova"))
        self.btn_interva = QPushButton("InterVA")
        self.btn_interva.pressed.connect(self.show_interva_page)
        self.btn_interva.pressed.connect(
            lambda: self.set_chosen_algorithm("interva"))
        self.btn_smartva = QPushButton("SmartVA")
        self.btn_smartva.pressed.connect(self.show_smartva_page)
        self.btn_smartva.pressed.connect(
            lambda: self.set_chosen_algorithm("smartva"))
        self.btn_go_to_data_page = QPushButton("Back")
        self.btn_go_to_data_page.pressed.connect(self.show_data_page)
        layout.addWidget(label_select_algorithm)
        layout.addWidget(self.btn_insilicova)
        layout.addStretch(1)
        layout.addWidget(self.btn_interva)
        layout.addStretch(1)
        layout.addWidget(self.btn_smartva)
        layout.addStretch(1)
        layout.addWidget(self.btn_go_to_data_page)

        self.select_algorithm_page.setLayout(layout)

    def insilicova_ui(self):
        layout = QVBoxLayout()
        label_iterations = QLabel("Number of Iterations")
        label_auto_length = QLabel("Automatically increase chain length")
        label_seed = QLabel("Set Seed")
        self.btn_insilicova_run = QPushButton("Run InSilicoVA")

        self.btn_go_to_select_algorithm_page = QPushButton("Back")
        self.btn_go_to_select_algorithm_page.pressed.connect(
            self.show_select_algorithm_page)
        self.btn_go_to_results_page = QPushButton("Show Results")
        self.btn_go_to_results_page.pressed.connect(
            self.show_results_page)

        layout.addWidget(label_iterations)
        layout.addWidget(label_auto_length)
        layout.addWidget(label_seed)
        layout.addWidget(self.btn_insilicova_run)
        layout.addStretch(1)
        h_box = QHBoxLayout()
        h_box.addWidget(self.btn_go_to_select_algorithm_page)
        h_box.addWidget(self.btn_go_to_results_page)
        layout.addLayout(h_box)
        self.insilicova_page.setLayout(layout)

    def interva_ui(self):
        layout = QVBoxLayout()
        option_set = ["high", "low", "very low"]
        label_hiv = QLabel("HIV")
        self.interva_combo_hiv = QComboBox()
        self.interva_combo_hiv.addItems(option_set)
        self.interva_combo_hiv.setCurrentIndex(
            option_set.index(self.interva_hiv))
        self.interva_combo_hiv.currentTextChanged.connect(
            self.set_interva_hiv)
        label_malaria = QLabel("Malaria")
        self.interva_combo_malaria = QComboBox()
        self.interva_combo_malaria.addItems(option_set)
        self.interva_combo_malaria.setCurrentIndex(
            option_set.index(self.interva_malaria))
        self.interva_combo_malaria.currentTextChanged.connect(
            self.set_interva_malaria)
        self.btn_interva_run = QPushButton("Run InterVA")
        self.btn_interva_run.pressed.connect(self.run_interva)
        self.btn_go_to_select_algorithm_page = QPushButton("Back")
        self.btn_go_to_select_algorithm_page.pressed.connect(
            self.show_select_algorithm_page)
        self.btn_go_to_results_page = QPushButton("Show Results")
        self.btn_go_to_results_page.pressed.connect(
            self.show_results_page)

        layout.addWidget(label_hiv)
        layout.addWidget(self.interva_combo_hiv)
        layout.addWidget(label_malaria)
        layout.addWidget(self.interva_combo_malaria)
        layout.addWidget(self.btn_interva_run)
        layout.addWidget(self.interva_progress_bar)
        layout.addStretch(1)
        h_box = QHBoxLayout()
        h_box.addWidget(self.btn_go_to_select_algorithm_page)
        h_box.addWidget(self.btn_go_to_results_page)
        layout.addLayout(h_box)
        self.interva_page.setLayout(layout)

    def smartva_ui(self):
        layout = QVBoxLayout()
        label_country = QLabel("Data origin country")
        self.smartva_combo_country = QComboBox()
        self.smartva_combo_country.addItems(COUNTRIES)
        self.smartva_combo_country.setCurrentIndex(
            COUNTRIES.index(self.smartva_country))
        self.smartva_combo_country.currentTextChanged.connect(
            self.set_smartva_country)
        option_set = ["True", "False"]
        label_hiv = QLabel("Data is from an HIV region")
        self.smartva_combo_hiv = QComboBox()
        self.smartva_combo_hiv.addItems(option_set)
        self.smartva_combo_hiv.setCurrentIndex(
            option_set.index(self.smartva_hiv))
        self.smartva_combo_hiv.currentTextChanged.connect(
            self.set_smartva_hiv)
        label_malaria = QLabel("Data is from a Malaria region")
        self.smartva_combo_malaria = QComboBox()
        self.smartva_combo_malaria.addItems(option_set)
        self.smartva_combo_malaria.setCurrentIndex(
            option_set.index(self.smartva_malaria))
        self.smartva_combo_malaria.currentTextChanged.connect(
            self.set_smartva_malaria)
        label_hce = QLabel("Use Health Care Experience (HCE) variables")
        self.smartva_combo_hce = QComboBox()
        self.smartva_combo_hce.addItems(option_set)
        self.smartva_combo_hce.setCurrentIndex(
            option_set.index(self.smartva_hce))
        self.smartva_combo_hce.currentTextChanged.connect(
            self.set_smartva_hce)
        label_freetext = QLabel("Use 'free text' variables")
        self.smartva_combo_freetext = QComboBox()
        self.smartva_combo_freetext.addItems(option_set)
        self.smartva_combo_freetext.setCurrentIndex(
            option_set.index(self.smartva_freetext))
        self.smartva_combo_freetext.currentTextChanged.connect(
            self.set_smartva_freetext)
        self.btn_smartva_run = QPushButton("Run SmartVA")
        self.btn_go_to_select_algorithm_page = QPushButton("Back")
        self.btn_go_to_select_algorithm_page.pressed.connect(
            self.show_select_algorithm_page)
        self.btn_go_to_results_page = QPushButton("Show Results")
        self.btn_go_to_results_page.pressed.connect(
            self.show_results_page)

        layout.addWidget(label_country)
        layout.addWidget(self.smartva_combo_country)
        layout.addWidget(label_hiv)
        layout.addWidget(self.smartva_combo_hiv)
        layout.addWidget(label_malaria)
        layout.addWidget(self.smartva_combo_malaria)
        layout.addWidget(label_hce)
        layout.addWidget(self.smartva_combo_hce)
        layout.addWidget(label_freetext)
        layout.addWidget(self.smartva_combo_freetext)
        layout.addWidget(self.btn_smartva_run)
        layout.addStretch(1)
        h_box = QHBoxLayout()
        h_box.addWidget(self.btn_go_to_select_algorithm_page)
        h_box.addWidget(self.btn_go_to_results_page)
        layout.addLayout(h_box)
        self.smartva_page.setLayout(layout)

    def results_ui(self):
        layout = QVBoxLayout()

        vbox_table = QVBoxLayout()
        self.btn_show_table = QPushButton("Show CSMF table")
        self.btn_show_table.pressed.connect(self.run_table_dialog)
        self.btn_download_table = QPushButton("Download Table")
        vbox_table.addWidget(self.btn_show_table)
        vbox_table.addWidget(self.btn_download_table)

        vbox_plot = QVBoxLayout()
        self.btn_show_plot = QPushButton("Show CSMF plot")
        self.btn_show_plot.pressed.connect(self.run_plot_dialog)
        self.btn_download_plot = QPushButton("Download Plot")
        vbox_plot.addWidget(self.btn_show_plot)
        vbox_plot.addWidget(self.btn_download_plot)

        hbox = QHBoxLayout()
        hbox.addLayout(vbox_table)
        hbox.addLayout(vbox_plot)

        layout.addLayout(hbox)
        self.btn_download_individual_results = QPushButton(
            "Download Individual Cause Assignments")
        self.btn_go_to_algorithm_page = QPushButton("Back")
        self.btn_go_to_algorithm_page.pressed.connect(
            self.show_algorithm_page)
        layout.addWidget(self.btn_download_individual_results)
        layout.addStretch(1)
        layout.addWidget(self.btn_go_to_algorithm_page)
        self.results_page.setLayout(layout)

    def load_data(self):
        path = QFileDialog.getOpenFileName(self,
                                           "Open a CSV file", "",
                                           "All Files(*.*)")
        if path != ("", ""):
            self.data = read_csv(path[0])
            n_records = self.data.shape[0]
            self.label_data.setText(f'Data loaded: {n_records} deaths')
            self.data_loaded = True

    def set_interva_hiv(self, updated_hiv):
        self.interva_hiv = updated_hiv

    def set_interva_malaria(self, updated_malaria):
        self.interva_malaria = updated_malaria

    def set_smartva_country(self, updated_country):
        self.smartva_country = updated_country

    def set_smartva_hiv(self, updated_hiv):
        self.smartva_hiv = updated_hiv

    def set_smartva_malaria(self, updated_malaria):
        self.smartva_malaria = updated_malaria

    def set_smartva_hce(self, updated_hce):
        self.smartva_hce = updated_hce

    def set_smartva_freetext(self, updated_freetext):
        self.smartva_freetext = updated_freetext

    def set_chosen_algorithm(self, updated_choice):
        self.chosen_algorithm = updated_choice

    def show_data_page(self):
        self.stacked_layout.setCurrentIndex(0)
        self.setWindowTitle("Efficient Mode: Data")

    def show_algorithm_page(self):
        if self.chosen_algorithm == "insilicova":
            self.show_insilicova_page()
        elif self.chosen_algorithm == "interva":
            self.show_interva_page()
        else:
            self.show_smartva_page()

    def show_select_algorithm_page(self):
        self.stacked_layout.setCurrentIndex(1)
        self.setWindowTitle("Efficient Mode: Select Algorithm")

    def show_insilicova_page(self):
        self.stacked_layout.setCurrentIndex(2)
        self.setWindowTitle("Efficient Mode: InSilicoVA")

    def show_interva_page(self):
        self.stacked_layout.setCurrentIndex(3)
        self.setWindowTitle("Efficient Mode: InterVA")

    def show_smartva_page(self):
        self.stacked_layout.setCurrentIndex(4)
        self.setWindowTitle("Efficient Mode: SmartVA")

    def show_results_page(self):
        self.stacked_layout.setCurrentIndex(5)
        self.setWindowTitle("Efficient Mode: Results")

    def run_interva(self):
        self.interva_results = InterVA5(self.data, self)
        self.interva_results.assign_causes()

    def run_plot_dialog(self):
        self.plot_dialog = PlotDialog(self.interva_results,
                                      self,
                                      top=10)
        self.plot_dialog.exec()

    def run_table_dialog(self):
        self.table_dialog = TableDialog(self.interva_results,
                                        self,
                                        top=10)
        self.table_dialog.resize(self.table_dialog.table.width(),
                                 self.table_dialog.table.height())
        self.table_dialog.exec()


class PlotDialog(QDialog):

    def __init__(self, results, parent=None, top=5):
        super(PlotDialog, self).__init__(parent=parent)
        self.setWindowTitle("Cause-Specific Mortality Fraction")
        self.results = results
        self.n_top_cause = top
        style.use("ggplot")
        self.figure = Figure(figsize=(7, 5), dpi=100, constrained_layout=True)
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.toolbar = NavigationToolbar2QT(self.canvas, self)

        vbox_csmf = QVBoxLayout()
        vbox_csmf.addWidget(self.toolbar)
        vbox_csmf.addWidget(self.canvas)
        self.setLayout(vbox_csmf)

        self.results.plot(top_causes=self.n_top_cause, ax=self.ax)
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


class TableDialog(QDialog):

    def __init__(self, results, parent=None, top=5):
        super(TableDialog, self).__init__(parent=parent)
        self.setWindowTitle("Cause-Specific Mortality Fraction")
        self.results = results
        self.n_top_cause = top

        self.table = QTableView()
        self.table.setShowGrid(False)
        csmf_df = results.csmf.reset_index()[0:top]
        csmf_df.rename(columns={"index": "Cause", "cause": "CSMF"},
                       inplace=True)
        self.model = TableModel(csmf_df)
        self.table.setModel(self.model)
        column_width = self.table.sizeHintForColumn(0) + 100
        #self.table.resizeColumnToContents(0)
        self.table.setColumnWidth(0, column_width)

        clipboard = QApplication.clipboard()
        self.btn_copy = QPushButton("Copy table to clipboard")
        self.btn_copy.pressed.connect(lambda: clipboard.setText(csmf_df.to_csv(index=False)))

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
