# -*- coding: utf-8 -*-

"""
pyopenva.efficient
~~~~~~~~~~~~~~
This module creates a stacked layout to walk through the analysis step-by-step.
"""

import os
import shutil
import tempfile
from insilicova.api import InSilicoVA
from insilicova.structures import InSilico
from insilicova.exceptions import HaltGUIException, InSilicoVAException
from interva.interva5 import InterVA5
from pyopenva.data import COUNTRIES
from pandas import read_csv, DataFrame
from pandas.errors import EmptyDataError, ParserError
from pycrossva.transform import transform
from PyQt5.QtWidgets import (QCheckBox, QComboBox, QFileDialog, QGroupBox,
                             QHBoxLayout, QMessageBox, QLabel, QProgressBar,
                             QPushButton, QSpinBox, QStackedLayout,
                             QVBoxLayout, QWidget)
from PyQt5.QtCore import Qt, QObject, QThread, pyqtSignal
from pyopenva.output import PlotDialog, TableDialog, save_plot
from pyopenva.workers import InSilicoVAWorker, InterVAWorker


class Efficient(QWidget):

    def __init__(self):
        super().__init__()
        # self.setGeometry(400, 400, 500, 400)
        self.data_page = QWidget()
        self.data = None
        self.data_loaded = False
        self.data_id_col = None
        self.pycrossva_data = None
        self.data_ui()
        self.select_algorithm_page = QWidget()
        self.select_algorithm_ui()
        self.chosen_algorithm = "insilicova"
        self.insilicova_results = None
        self.insilicova_warnings = None
        self.insilicova_errors = None
        self.insilicova_page = QWidget()
        self.insilicova_n_sim: int = 4000
        self.insilicova_auto: str = "True"
        self.insilicova_seed: int = 1
        self.insilicova_include_probs = False
        self.insilicova_pbar = QProgressBar()
        self.label_insilicova_progress = QLabel("(no results)")
        self.insilicova_ctrl = {"break": False}
        self.insilicova_ui()
        self.interva_results = None
        self.interva_log = None
        self.interva_page = QWidget()
        self.interva_hiv = "low"
        self.interva_malaria = "low"
        self.interva_pbar = QProgressBar()
        self.label_interva_progress = QLabel("(no results)")
        self.interva_ctrl = {"break": False}
        self.interva_ui()
        # self.smartva_page = QWidget()
        # self.smartva_country = "Unknown"
        # self.smartva_hiv = "True"
        # self.smartva_malaria = "True"
        # self.smartva_hce = "True"
        # self.smartva_freetext = "True"
        # self.smartva_ui()
        self.results_page = QWidget()
        self.btn_show_plot = None
        self.btn_show_table = None
        self.results_figure = None
        self.btn_download_plot = None
        self.btn_download_table = None
        self.btn_download_individual_results = None
        self.n_top_causes = 5
        self.results_ui()
        self.stacked_layout = QStackedLayout()
        self.stacked_layout.addWidget(self.data_page)
        self.stacked_layout.addWidget(self.select_algorithm_page)
        self.stacked_layout.addWidget(self.insilicova_page)
        self.stacked_layout.addWidget(self.interva_page)
        # self.stacked_layout.addWidget(self.smartva_page)
        self.stacked_layout.addWidget(self.results_page)

        self.main_layout = QVBoxLayout()
        self.main_layout.addLayout(self.stacked_layout)
        self.setLayout(self.main_layout)

    def data_ui(self):
        """Set up page for loading, editing, and checking the data."""

        layout = QVBoxLayout()

        load_groupbox = QGroupBox("Load Data")
        load_vbox = QVBoxLayout()
        label_data_info = QLabel(
            "Select the file with VA data from an ODK export")
        self.btn_load_data = QPushButton("Load Data (.csv)")
        self.btn_load_data.setMaximumWidth(350)
        self.btn_load_data.clicked.connect(self.load_data)
        self.label_data = QLabel("(no data loaded)")
        self.label_data.setMaximumWidth(350)
        self.label_data_fname = QLabel("")
        self.label_data_fname.setMaximumWidth(350)
        self.label_data_n_records = QLabel("")
        self.label_data_n_records.setMaximumWidth(350)
        label_data_id_col = QLabel("Select ID column in data")
        self.combo_data_id_col = QComboBox()
        self.combo_data_id_col.currentTextChanged.connect(
            self.set_data_id_col)
        self.combo_data_id_col.setMaximumWidth(350)
        # load_vbox.insertSpacing(0, 20)
        load_vbox.addWidget(label_data_info)
        load_vbox.addWidget(self.btn_load_data)
        load_vbox.addWidget(self.label_data)
        load_vbox.addWidget(self.label_data_fname)
        load_vbox.addWidget(self.label_data_n_records)
        load_vbox.insertSpacing(5, 5)
        load_vbox.insertSpacing(6, 50)
        load_vbox.addWidget(label_data_id_col)
        load_vbox.addWidget(self.combo_data_id_col)
        load_groupbox.setLayout(load_vbox)

        form_groupbox = QGroupBox("Data Format")
        form_vbox = QVBoxLayout()
        label_data_format = QLabel(
            "Select the ODK form used for data collection")
        self.btn_data_format = QComboBox()
        # TODO: use format in argument for pycrossva (need a setter function
        #       with a dictionary for mapping options to pycrossva parameters)
        self.btn_data_format.addItems(("WHO 2016",))
                                       # "WHO 2012",
                                       # "PHMRC"))
        self.btn_data_format.setMaximumWidth(350)
        form_vbox.addWidget(label_data_format)
        form_vbox.addWidget(self.btn_data_format)
        form_groupbox.setLayout(form_vbox)

        h_box_btns = QHBoxLayout()
        self.btn_go_to_mode = QPushButton("Back")
        self.btn_algorithm = QPushButton("Next")
        self.btn_data_ui_exit = QPushButton("Exit")
        h_box_btns.addWidget(self.btn_go_to_mode)
        h_box_btns.addWidget(self.btn_algorithm)
        h_box_btns.addWidget(self.btn_data_ui_exit)

        layout.addWidget(load_groupbox)
        layout.addStretch(2)
        layout.addWidget(form_groupbox)
        layout.addStretch(2)
        layout.addLayout(h_box_btns)
        self.data_page.setLayout(layout)

    def select_algorithm_ui(self):
        layout = QVBoxLayout()
        label_select_algorithm = QLabel("Select which algorithm to use:")
        self.btn_insilicova = QPushButton("InSilicoVA")
        self.btn_insilicova.setMaximumWidth(400)
        self.btn_insilicova.pressed.connect(
            lambda: self.set_chosen_algorithm("insilicova"))
        self.btn_interva = QPushButton("InterVA")
        self.btn_interva.setMaximumWidth(400)
        self.btn_interva.pressed.connect(
            lambda: self.set_chosen_algorithm("interva"))
        # self.btn_smartva = QPushButton("SmartVA")
        # self.btn_smartva.setMaximumWidth(400)
        # self.btn_smartva.pressed.connect(
        #     lambda: self.set_chosen_algorithm("smartva"))
        layout.addStretch(1)
        layout.addWidget(label_select_algorithm)
        layout.addWidget(self.btn_insilicova)
        layout.addStretch(1)
        layout.addWidget(self.btn_interva)
        layout.addStretch(1)
        # layout.addWidget(self.btn_smartva)
        # layout.addStretch(1)
        hbox = QHBoxLayout()
        self.btn_go_to_data_page = QPushButton("Back")
        self.btn_algorithm_ui_exit = QPushButton("Exit")
        hbox.addWidget(self.btn_go_to_data_page)
        hbox.addWidget(self.btn_algorithm_ui_exit)
        # layout.addWidget(self.btn_go_to_data_page)
        layout.addLayout(hbox)
        self.select_algorithm_page.setLayout(layout)

    def insilicova_ui(self):
        layout = QVBoxLayout()
        # gbox_options = QGroupBox("Set Options")
        # layout_options = QVBoxLayout()
        # layout_n_iter = QHBoxLayout()
        # layout_auto = QHBoxLayout()
        # layout_seed = QHBoxLayout()
        # label_n_iter = QLabel("Number of Iterations (range: 400 - 8000):")
        # spinbox_n_iter = QSpinBox()
        # spinbox_n_iter.setRange(400, 8000)
        # spinbox_n_iter.setSingleStep(100)
        # spinbox_n_iter.setAlignment(Qt.AlignCenter)
        # spinbox_n_iter.setValue(self.insilicova_n_sim)
        # spinbox_n_iter.valueChanged.connect(self.set_insilicova_n_sim)
        # spinbox_n_iter.setMaximumWidth(150)
        # label_auto_length = QLabel("Automatically increase chain length")
        # option_set = ["True", "False"]
        # self.insilicova_combo_auto = QComboBox()
        # self.insilicova_combo_auto.addItems(option_set)
        # self.insilicova_combo_auto.setEditable(True)
        # self.insilicova_combo_auto.lineEdit().setReadOnly(True)
        # self.insilicova_combo_auto.lineEdit().setAlignment(Qt.AlignCenter)
        # self.insilicova_combo_auto.setMaximumWidth(150)
        # self.insilicova_combo_auto.setCurrentIndex(
        #     option_set.index(self.insilicova_auto))
        # self.insilicova_combo_auto.currentTextChanged.connect(
        #     self.set_insilicova_auto)
        # label_seed = QLabel("Set Seed:")
        # spinbox_seed = QSpinBox()
        # spinbox_seed.setRange(1, 10000)
        # spinbox_seed.setAlignment(Qt.AlignCenter)
        # spinbox_seed.setValue(self.insilicova_seed)
        # spinbox_seed.valueChanged.connect(self.set_insilicova_seed)
        # spinbox_seed.setMaximumWidth(150)
        self.btn_insilicova_run = QPushButton("Run InSilicoVA")
        self.btn_insilicova_run.setMaximumWidth(300)
        self.btn_insilicova_run.clicked.connect(self.run_insilicova)
        self.btn_insilicova_stop = QPushButton("Stop")
        self.btn_insilicova_stop.setMaximumWidth(150)
        self.btn_insilicova_stop.setEnabled(False)
        self.btn_insilicova_stop.clicked.connect(self.stop_insilicova)
        self.btn_download_insilicova_log = QPushButton(
            "Download log from data checks")
        self.btn_download_insilicova_log.setEnabled(False)
        self.btn_download_insilicova_log.clicked.connect(self.download_log)

        self.btn_insilicova_to_select_algorithm = QPushButton("Back")
        self.btn_go_to_results_page = QPushButton("Show Results")
        self.btn_go_to_results_page.pressed.connect(
            self.show_results_page)
        self.btn_insilicova_ui_exit = QPushButton("Exit")

        # layout_n_iter.addWidget(label_n_iter)
        # layout_n_iter.addWidget(spinbox_n_iter)
        # layout_auto.addWidget(label_auto_length)
        # layout_auto.addWidget(self.insilicova_combo_auto)
        # layout_seed.addWidget(label_seed)
        # layout_seed.addWidget(spinbox_seed)
        # layout_options.addLayout(layout_n_iter)
        # layout_options.addLayout(layout_auto)
        # layout_options.addLayout(layout_seed)
        # gbox_options.setLayout(layout_options)
        # layout.addWidget(gbox_options)
        layout.addStretch(1)
        layout.addWidget(self.btn_insilicova_run)
        layout.addWidget(self.insilicova_pbar)
        layout.addWidget(self.label_insilicova_progress)
        layout.addWidget(self.btn_insilicova_stop)
        layout.addStretch(1)
        layout.addWidget(self.btn_download_insilicova_log)
        layout.addStretch(1)
        h_box = QHBoxLayout()
        h_box.addWidget(self.btn_insilicova_to_select_algorithm)
        h_box.addWidget(self.btn_go_to_results_page)
        h_box.addWidget(self.btn_insilicova_ui_exit)
        layout.addLayout(h_box)
        self.insilicova_page.setLayout(layout)

    def interva_ui(self):
        layout = QVBoxLayout()
        gbox_options = QGroupBox("Set Options")
        layout_options = QVBoxLayout()
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
        self.btn_interva_run.setMaximumWidth(300)
        self.btn_interva_run.clicked.connect(self.run_interva)
        self.label_interva_chosen_options = QLabel("")
        self.label_interva_chosen_hiv = QLabel("")
        self.label_interva_chosen_malaria = QLabel("")
        self.btn_interva_stop = QPushButton("Stop")
        self.btn_interva_stop.setEnabled(False)
        self.btn_interva_stop.setMaximumWidth(150)
        self.btn_interva_stop.clicked.connect(self.stop_interva)
        self.btn_download_interva_log = QPushButton(
            "Download Log from data checks")
        self.btn_download_interva_log.setEnabled(False)
        self.btn_download_interva_log.clicked.connect(self.download_log)
        self.btn_interva_to_select_algorithm = QPushButton("Back")
        self.btn_go_to_results_page = QPushButton("Show Results")
        self.btn_go_to_results_page.clicked.connect(
            self.show_results_page)
        self.btn_interva_ui_exit = QPushButton("Exit")

        layout_options.addWidget(label_hiv)
        layout_options.addWidget(self.interva_combo_hiv)
        layout_options.addWidget(label_malaria)
        layout_options.addWidget(self.interva_combo_malaria)
        gbox_options.setLayout(layout_options)

        layout.addWidget(gbox_options)
        layout.addStretch(1)
        layout.addWidget(self.btn_interva_run)
        hbox_chosen_options = QHBoxLayout()
        hbox_chosen_options.addWidget(self.label_interva_chosen_options)
        hbox_chosen_options.addWidget(self.label_interva_chosen_hiv)
        hbox_chosen_options.addWidget(self.label_interva_chosen_malaria)
        layout.addLayout(hbox_chosen_options)
        layout.addWidget(self.interva_pbar)
        layout.addWidget(self.label_interva_progress)
        layout.addWidget(self.btn_interva_stop)
        layout.addStretch(1)
        layout.addWidget(self.btn_download_interva_log)
        layout.addStretch(1)
        h_box = QHBoxLayout()
        h_box.addWidget(self.btn_interva_to_select_algorithm)
        h_box.addWidget(self.btn_go_to_results_page)
        h_box.addWidget(self.btn_interva_ui_exit)
        layout.addLayout(h_box)
        self.interva_page.setLayout(layout)

    # def smartva_ui(self):
    #     layout = QVBoxLayout()
    #     label_country = QLabel("Data origin country")
    #     self.smartva_combo_country = QComboBox()
    #     self.smartva_combo_country.addItems(COUNTRIES)
    #     self.smartva_combo_country.setCurrentIndex(
    #         COUNTRIES.index(self.smartva_country))
    #     self.smartva_combo_country.currentTextChanged.connect(
    #         self.set_smartva_country)
    #     option_set = ["True", "False"]
    #     label_hiv = QLabel("Data is from an HIV region")
    #     self.smartva_combo_hiv = QComboBox()
    #     self.smartva_combo_hiv.addItems(option_set)
    #     self.smartva_combo_hiv.setCurrentIndex(
    #         option_set.index(self.smartva_hiv))
    #     self.smartva_combo_hiv.currentTextChanged.connect(
    #         self.set_smartva_hiv)
    #     label_malaria = QLabel("Data is from a Malaria region")
    #     self.smartva_combo_malaria = QComboBox()
    #     self.smartva_combo_malaria.addItems(option_set)
    #     self.smartva_combo_malaria.setCurrentIndex(
    #         option_set.index(self.smartva_malaria))
    #     self.smartva_combo_malaria.currentTextChanged.connect(
    #         self.set_smartva_malaria)
    #     label_hce = QLabel("Use Health Care Experience (HCE) variables")
    #     self.smartva_combo_hce = QComboBox()
    #     self.smartva_combo_hce.addItems(option_set)
    #     self.smartva_combo_hce.setCurrentIndex(
    #         option_set.index(self.smartva_hce))
    #     self.smartva_combo_hce.currentTextChanged.connect(
    #         self.set_smartva_hce)
    #     label_freetext = QLabel("Use 'free text' variables")
    #     self.smartva_combo_freetext = QComboBox()
    #     self.smartva_combo_freetext.addItems(option_set)
    #     self.smartva_combo_freetext.setCurrentIndex(
    #         option_set.index(self.smartva_freetext))
    #     self.smartva_combo_freetext.currentTextChanged.connect(
    #         self.set_smartva_freetext)
    #     self.btn_smartva_run = QPushButton("Run SmartVA")
    #     self.btn_smartva_to_select_algorithm = QPushButton("Back")
    #     self.btn_go_to_results_page = QPushButton("Show Results")
    #     self.btn_go_to_results_page.pressed.connect(
    #         self.show_results_page)
    #     self.btn_smartva_ui_exit = QPushButton("Exit")
    #
    #     layout.addWidget(label_country)
    #     layout.addWidget(self.smartva_combo_country)
    #     layout.addWidget(label_hiv)
    #     layout.addWidget(self.smartva_combo_hiv)
    #     layout.addWidget(label_malaria)
    #     layout.addWidget(self.smartva_combo_malaria)
    #     layout.addWidget(label_hce)
    #     layout.addWidget(self.smartva_combo_hce)
    #     layout.addWidget(label_freetext)
    #     layout.addWidget(self.smartva_combo_freetext)
    #     layout.addWidget(self.btn_smartva_run)
    #     layout.addStretch(1)
    #     h_box = QHBoxLayout()
    #     h_box.addWidget(self.btn_smartva_to_select_algorithm)
    #     h_box.addWidget(self.btn_go_to_results_page)
    #     h_box.addWidget(self.btn_smartva_ui_exit)
    #     layout.addLayout(h_box)
    #     self.smartva_page.setLayout(layout)

    def results_ui(self):
        layout = QVBoxLayout()
        gbox_top_causes = QGroupBox("Number of top causes")
        hbox_top = QHBoxLayout()
        self.spinbox_n_causes = QSpinBox()
        self.spinbox_n_causes.setRange(1, 64)
        self.spinbox_n_causes.setPrefix("Include ")
        self.spinbox_n_causes.setSuffix(" causes in the results")
        self.spinbox_n_causes.setValue(self.n_top_causes)
        self.spinbox_n_causes.valueChanged.connect(self.set_n_top_causes)
        self.spinbox_n_causes.setMaximumWidth(250)
        hbox_top.addWidget(self.spinbox_n_causes)
        gbox_top_causes.setLayout(hbox_top)

        gbox_show = QGroupBox("Show Results")
        hbox_show = QHBoxLayout()
        self.btn_show_table = QPushButton("Show \n CSMF table")
        self.btn_show_table.pressed.connect(self.run_table_dialog)
        self.btn_show_plot = QPushButton("Show \n CSMF plot")
        self.btn_show_plot.pressed.connect(self.run_plot_dialog)
        hbox_show.addWidget(self.btn_show_table)
        hbox_show.addWidget(self.btn_show_plot)
        gbox_show.setLayout(hbox_show)

        gbox_download = QGroupBox("Download Results")
        vbox_download = QVBoxLayout()
        hbox_download = QHBoxLayout()
        self.btn_download_table = QPushButton("Download Table")
        self.btn_download_table.clicked.connect(self.download_csmf_table)
        self.btn_download_plot = QPushButton("Download Plot")
        self.btn_download_plot.clicked.connect(self.download_csmf_plot)
        self.btn_download_individual_results = QPushButton(
            "Download \n Individual Cause Assignments")
        self.btn_download_individual_results.clicked.connect(
            self.download_indiv_cod
        )
        self.chbox_insilicova_include_probs = QCheckBox(
            "Include probability of top cause (with individual CODs)")
        self.chbox_insilicova_include_probs.toggled.connect(
            self.set_insilicova_include_probs)
        # self.btn_download_log = QPushButton("Download log from data checks")
        # self.btn_download_log.clicked.connect(self.download_log)
        hbox_download.addWidget(self.btn_download_table)
        hbox_download.addWidget(self.btn_download_plot)
        vbox_download.addLayout(hbox_download)
        vbox_download.addWidget(self.btn_download_individual_results)
        if self.chosen_algorithm == "insilicova":
            vbox_download.addWidget(self.chbox_insilicova_include_probs)
        # vbox_download.addWidget(self.btn_download_log)
        gbox_download.setLayout(vbox_download)

        hbox_navigate = QHBoxLayout()
        self.btn_results_to_algorithm = QPushButton("Back")
        self.btn_results_ui_exit = QPushButton("Exit")
        hbox_navigate.addWidget(self.btn_results_to_algorithm)
        hbox_navigate.addWidget(self.btn_results_ui_exit)
        layout.addWidget(gbox_top_causes)
        layout.addStretch(1)
        layout.addWidget(gbox_show)
        layout.addStretch(1)
        layout.addWidget(gbox_download)
        layout.addStretch(1)
        # layout.addWidget(self.btn_results_to_algorithm)
        layout.addLayout(hbox_navigate)
        self.results_page.setLayout(layout)

    def load_data(self):
        path = QFileDialog.getOpenFileName(self,
                                           "Open a CSV file",
                                           "",
                                           "csv(*.csv)")
        if path != ("", ""):
            try:
                self.data = read_csv(path[0])
                f_name = path[0].split("/")[-1]
                n_records = self.data.shape[0]
                self.label_data.setAlignment(Qt.AlignLeft)
                self.label_data.setText("Data loaded:")
                self.label_data_fname.setAlignment(Qt.AlignCenter)
                self.label_data_fname.setText(f"{f_name}")
                self.label_data_n_records.setAlignment(Qt.AlignCenter)
                self.label_data_n_records.setText(f"({n_records} records)")
                self.data_loaded = True
                self.combo_data_id_col.blockSignals(True)
                self.combo_data_id_col.clear()
                self.combo_data_id_col.addItems(
                    ["no ID column"] + list(self.data)
                )
                self.combo_data_id_col.blockSignals(False)
                self.combo_data_id_col.setCurrentIndex(0)
                # reset app
                # TODO: create method for clearing results
                self.label_insilicova_progress.setText(
                    "(no results)")
                self.insilicova_warnings = None
                self.insilicova_errors = None
                self.insilicova_results = None
                self.label_interva_progress.setText(
                    "(no results)")
                self.insilicova_pbar.setValue(0)
                self.interva_log = None
                self.interva_results = None
                self.interva_pbar.setValue(0)
                self.pycrossva_data = None
            except (ParserError, UnicodeDecodeError):
                alert = QMessageBox()
                alert.setWindowTitle("openVA App")
                alert.setIcon(QMessageBox.Warning)
                alert.setText(
                    f"Unable to read in CSV file {path[0]}.\n" +
                    "Please check it is formatted as an ODK export.")
                alert.exec()
            except EmptyDataError:
                alert = QMessageBox()
                alert.setWindowTitle("openVA App")
                alert.setIcon(QMessageBox.Warning)
                alert.setText(
                    f"Unable to read in CSV file {path[0]}.\n" +
                    "File appears to be empty.")
                alert.exec()
            except PermissionError:
                alert = QMessageBox()
                alert.setWindowTitle("openVA App")
                alert.setIcon(QMessageBox.Warning)
                alert.setText(
                    f"Unable to read in CSV file {path[0]}.\n" +
                    "User does not have permission to access the file.")
                alert.exec()

    def set_data_id_col(self, id_col):
        self.data_id_col = id_col
        if self.data_id_col != "no ID column":
            if self.data[self.data_id_col].nunique() != self.data.shape[0]:
                alert = QMessageBox()
                alert.setWindowTitle("openVA App")
                alert.setIcon(QMessageBox.Warning)
                alert.setText(
                    "ID column does not have a unique value for every row")
                alert.exec()

    def set_insilicova_include_probs(self, checked):
        if checked:
            self.insilicova_include_probs = True
        else:
            self.insilicova_include_probs = False

    def run_pycrossva(self):
        raw_data_col_id = self.data_id_col
        if self.data_id_col == "no ID column":
            raw_data_col_id = None
        self.pycrossva_data = transform(
            mapping=("2016WHOv151", "InterVA5"),
            raw_data=self.data,
            raw_data_id=raw_data_col_id)
        if (self.pycrossva_data.iloc[:, 1:] == ".").all(axis=None):
            alert = QMessageBox()
            alert.setWindowTitle("openVA App")
            alert.setText(
                "Problem converting data to openVA format:\n"
                "ALL VALUES ARE MISSING"
                "\nThe data have an unexpected format and cannot be "
                "processed.  Please reload data in the expected format.")
            alert.exec()

    # def set_insilicova_n_sim(self, n_sim: int):
    #     self.insilicova_n_sim = n_sim
    #
    # def set_insilicova_auto(self, auto: str):
    #     self.insilicova_auto = auto
    #
    # def set_insilicova_seed(self, seed: int):
    #     self.insilicova_seed = seed

    def set_interva_hiv(self, updated_hiv):
        self.interva_hiv = updated_hiv

    def set_interva_malaria(self, updated_malaria):
        self.interva_malaria = updated_malaria

    # def set_smartva_country(self, updated_country):
    #     self.smartva_country = updated_country
    #
    # def set_smartva_hiv(self, updated_hiv):
    #     self.smartva_hiv = updated_hiv
    #
    # def set_smartva_malaria(self, updated_malaria):
    #     self.smartva_malaria = updated_malaria
    #
    # def set_smartva_hce(self, updated_hce):
    #     self.smartva_hce = updated_hce
    #
    # def set_smartva_freetext(self, updated_freetext):
    #     self.smartva_freetext = updated_freetext
    #
    def set_chosen_algorithm(self, updated_choice):
        self.chosen_algorithm = updated_choice

    def set_n_top_causes(self, n):
        self.n_top_causes = n

    # TODO: need to clean these up (window management handled in main)
    def show_data_page(self):
        self.stacked_layout.setCurrentIndex(0)

    def show_algorithm_page(self):
        if self.chosen_algorithm == "insilicova":
            self.show_insilicova_page()
        elif self.chosen_algorithm == "interva":
            self.show_interva_page()
        # else:
        #     self.show_smartva_page()

    def show_select_algorithm_page(self):
        self.stacked_layout.setCurrentIndex(1)

    def show_insilicova_page(self):
        self.stacked_layout.setCurrentIndex(2)

    def show_interva_page(self):
        self.stacked_layout.setCurrentIndex(3)

    # def show_smartva_page(self):
    #     self.stacked_layout.setCurrentIndex(4)

    def show_results_page(self):
        if self.chosen_algorithm == "insilicova":
            self.chbox_insilicova_include_probs.show()
        else:
            self.chbox_insilicova_include_probs.hide()
        # self.stacked_layout.setCurrentIndex(5)
        self.stacked_layout.setCurrentIndex(4)

    def run_insilicova(self):
        self.insilicova_ctrl["break"] = False
        self.btn_insilicova_run.setEnabled(False)
        self.btn_load_data.setEnabled(False)
        self.btn_download_insilicova_log.setEnabled(False)
        self.insilicova_warnings = None
        self.insilicova_errors = None
        self.insilicova_results = None
        if self.data_loaded is False:
            alert = QMessageBox()
            alert.setWindowTitle("openVA App")
            alert.setText("Please load data first.")
            alert.exec()
            self.btn_insilicova_run.setEnabled(True)
            self.btn_load_data.setEnabled(True)
            self.btn_download_insilicova_log.setEnabled(True)
        else:
            self.run_pycrossva()
            auto_extend = False
            if self.insilicova_auto == "True":
                auto_extend = True
            burnin = max(int(self.insilicova_n_sim/2), 1)
            thin = 10
            self.insilicova_thread = QThread()
            self.insilicova_worker = InSilicoVAWorker(
                data=self.pycrossva_data,
                data_type="WHO2016",
                n_sim=self.insilicova_n_sim,
                thin=thin,
                burnin=burnin,
                auto_length=auto_extend,
                seed=self.insilicova_seed,
                gui_ctrl=self.insilicova_ctrl)
            self.insilicova_worker.moveToThread(self.insilicova_thread)
            self.insilicova_thread.started.connect(self.insilicova_worker.run)
            self.insilicova_worker.finished.connect(
                self.insilicova_thread.quit)
            self.insilicova_worker.finished.connect(
                self.insilicova_worker.deleteLater)
            self.insilicova_thread.finished.connect(
                self.insilicova_thread.deleteLater)
            self.insilicova_worker.progress.connect(
                self.update_insilicova_progress)
            self.insilicova_worker.state.connect(
                self.update_insilicova_progress_label)
            self.insilicova_worker.insilicova_errors.connect(
                self.update_insilicova_errors)
            self.insilicova_worker.insilicova_warnings.connect(
                self.update_insilicova_warnings)
            self.insilicova_worker.insilicova_results.connect(
                self.update_insilicova_results)
            self.insilicova_thread.start()
            self.btn_insilicova_stop.setEnabled(True)

            self.btn_insilicova_run.setEnabled(False)
            self.insilicova_thread.finished.connect(
                lambda: self.btn_insilicova_run.setEnabled(True))
            self.insilicova_thread.finished.connect(
                lambda: self.btn_insilicova_stop.setEnabled(False))
            self.insilicova_thread.finished.connect(
                lambda: self.btn_load_data.setEnabled(True))
            self.insilicova_thread.finished.connect(
                lambda: self.btn_download_insilicova_log.setEnabled(True))

    def update_insilicova_progress(self, n):
        self.insilicova_pbar.setValue(n)

    def update_insilicova_progress_label(self, msg):
        self.label_insilicova_progress.setText(msg)

    def update_insilicova_warnings(self, msg):
        self.insilicova_warnings = msg

    def update_insilicova_errors(self, msg):
        self.insilicova_errors = msg

    def update_insilicova_results(self, results):
        self.insilicova_results = results

    def stop_insilicova(self):
        self.insilicova_ctrl["break"] = True
        self.btn_insilicova_stop.setEnabled(False)

    def run_interva(self):
        self.interva_ctrl["break"] = False
        self.btn_interva_run.setEnabled(False)
        self.btn_load_data.setEnabled(False)
        self.btn_download_interva_log.setEnabled(False)
        self.interva_combo_hiv.setEnabled(False)
        self.interva_combo_malaria.setEnabled(False)
        self.label_interva_chosen_options.setText(
            "Latest InterVA results run with:")
        self.label_interva_chosen_malaria.setText(
            f"Malaria set to {self.interva_malaria}")
        self.label_interva_chosen_hiv.setText(
            f"HIV set to {self.interva_hiv}")
        if self.data_loaded is False:
            alert = QMessageBox()
            alert.setWindowTitle("openVA App")
            alert.setText("Please load data first.")
            alert.exec()
            self.btn_interva_run.setEnabled(True)
            self.btn_load_data.setEnabled(True)
            self.btn_download_interva_log.setEnabled(True)
            self.interva_combo_hiv.setEnabled(True)
            self.interva_combo_malaria.setEnabled(True)
            self.label_interva_chosen_options.setText(
                "Latest InterVA results run with:")
            self.label_interva_chosen_malaria.setText(
                f"Malaria set to {self.interva_malaria}")
            self.label_interva_chosen_hiv.setText(
                f"HIV set to {self.interva_hiv}")
        else:
            self.interva_log = None
            self.interva_results = None
            # TODO: clear old error log if it exists?
            self.interva_tmp_dir = tempfile.TemporaryDirectory()
            self.run_pycrossva()
            self.interva_thread = QThread()
            self.interva_worker = InterVAWorker(
                self.pycrossva_data,
                hiv=self.interva_hiv[0],
                malaria=self.interva_malaria[0],
                directory=self.interva_tmp_dir.name,
                gui_ctrl=self.interva_ctrl)
            self.interva_worker.moveToThread(self.interva_thread)
            self.interva_thread.started.connect(self.interva_worker.run)
            self.interva_worker.finished.connect(self.interva_thread.quit)
            self.interva_worker.finished.connect(
                self.interva_worker.deleteLater)
            self.interva_thread.finished.connect(
                self.interva_thread.deleteLater)
            self.interva_worker.progress.connect(
                self.update_interva_progress)
            self.interva_worker.state.connect(
                self.update_interva_progress_label)
            self.interva_worker.log.connect(
                self.update_interva_log)
            self.interva_worker.interva_results.connect(
                self.update_interva_results)
            self.interva_thread.start()
            self.btn_interva_stop.setEnabled(True)

            self.btn_interva_run.setEnabled(False)
            self.interva_thread.finished.connect(
                lambda: self.btn_interva_run.setEnabled(True))
            self.interva_thread.finished.connect(
                lambda: self.btn_interva_stop.setEnabled(False))
            self.interva_thread.finished.connect(
                lambda: self.btn_load_data.setEnabled(True))
            self.interva_thread.finished.connect(
                lambda: self.interva_combo_hiv.setEnabled(True))
            self.interva_thread.finished.connect(
                lambda: self.interva_combo_malaria.setEnabled(True))
            self.interva_thread.finished.connect(
                lambda: self.btn_download_interva_log.setEnabled(True))

    def update_interva_progress(self, n):
        self.interva_pbar.setValue(n)

    def update_interva_progress_label(self, msg):
        self.label_interva_progress.setText(msg)

    def update_interva_log(self, msg):
        self.interva_log = msg

    def update_interva_results(self, interva5):
        self.interva_results = interva5

    def stop_interva(self):
        self.interva_ctrl["break"] = True
        self.btn_interva_stop.setEnabled(False)

    def run_plot_dialog(self):
        if self.chosen_algorithm == "insilicova":
            results = self.insilicova_results
        else:
            results = self.interva_results
        if results is None:
            alert = QMessageBox()
            alert.setWindowTitle("openVA App")
            alert.setText(
                "No results available.  Please load data in the expected "
                "format and/or run a VA algorithm.")
            alert.exec()
        else:
            self.plot_dialog = PlotDialog(results=results,
                                          algorithm=self.chosen_algorithm,
                                          parent=self,
                                          top=self.n_top_causes)
            self.plot_dialog.exec()

    def run_table_dialog(self):
        if self.chosen_algorithm == "insilicova":
            results = self.insilicova_results
        else:
            results = self.interva_results
        if results is None:
            alert = QMessageBox()
            alert.setWindowTitle("openVA App")
            alert.setText(
                "No results available.  Please load data in the expected "
                "format and/or run a VA algorithm.")
            alert.exec()
        else:
            self.table_dialog = TableDialog(results,
                                            self,
                                            top=self.n_top_causes)
            self.table_dialog.resize(self.table_dialog.table.width(),
                                     self.table_dialog.table.height())
            self.table_dialog.exec()

    def download_csmf_table(self):
        if self.chosen_algorithm == "insilicova":
            results = self.insilicova_results
        else:
            results = self.interva_results
        if results is None:
            alert = QMessageBox()
            alert.setWindowTitle("openVA App")
            alert.setText(
                "No results available.  Please load data in the expected "
                "format and/or run a VA algorithm.")
            alert.exec()
        else:
            results_file_name = f"{self.chosen_algorithm}_csmf.csv"
            path = QFileDialog.getSaveFileName(self,
                                               "Save CSMF (csv)",
                                               results_file_name,
                                               "CSV Files (*.csv)")
            if path != ("", ""):
                with open(path[0], "w", newline="") as f:
                    n_top_causes = self.n_top_causes
                    csmf = results.get_csmf(top=n_top_causes)
                    if isinstance(csmf, DataFrame):
                        csmf_df = csmf.sort_values(
                            by="Mean", ascending=False).copy()
                        csmf_df = csmf_df.reset_index()
                        csmf_df.rename(columns={"index": "Cause",
                                                "Mean": "CSMF (Mean)"},
                                       inplace=True)
                    else:
                        csmf.sort_values(ascending=False, inplace=True)
                        csmf_df = csmf.reset_index()[0:n_top_causes]
                        csmf_df.rename(columns={"index": "Cause", 0: "CSMF"},
                                       inplace=True)
                    csmf_df.to_csv(f, index=False)
                if os.path.isfile(path[0]):
                    alert = QMessageBox()
                    alert.setWindowTitle("openVA App")
                    alert.setText("results saved to" + path[0])
                    alert.exec()

    def download_csmf_plot(self):
        if self.chosen_algorithm == "insilicova":
            results = self.insilicova_results
        else:
            results = self.interva_results
        if results is None:
            alert = QMessageBox()
            alert.setWindowTitle("openVA App")
            alert.setText(
                "No results available.  Please load data in the expected "
                "format and/or run a VA algorithm.")
            alert.exec()
        else:
            results_file_name = f"{self.chosen_algorithm}_csmf.pdf"
            path = QFileDialog.getSaveFileName(self,
                                               "Save CSMF plot (pdf)",
                                               results_file_name,
                                               "PDF Files (*.pdf)")
            if path != ("", ""):
                save_plot(results=results,
                          algorithm=self.chosen_algorithm,
                          top=self.n_top_causes,
                          file_name=path[0])
                if os.path.isfile(path[0]):
                    alert = QMessageBox()
                    alert.setWindowTitle("openVA App")
                    alert.setText("results saved to" + path[0])
                    alert.exec()

    def download_indiv_cod(self):
        if self.chosen_algorithm == "insilicova":
            results = self.insilicova_results
        else:
            results = self.interva_results
        if results is None:
            alert = QMessageBox()
            alert.setWindowTitle("openVA App")
            alert.setText(
                "No results available.  Please load data in the expected "
                "format and/or run a VA algorithm.")
            alert.exec()
        else:
            results_file_name = f"{self.chosen_algorithm}_individual_cod.csv"
            path = QFileDialog.getSaveFileName(self,
                                               "Save CSMF (csv)",
                                               results_file_name,
                                               "CSV Files (*.csv)")
            if path != ("", ""):
                with open(path[0], "w", newline="") as f:
                    if self.chosen_algorithm == "insilicova":
                        out = self.prepare_insilico_indiv_cod(results)
                        out.to_csv(f, index=False)
                    else:
                        out = results.out["VA5"]
                        out.drop("WHOLEPROB", axis=1, inplace=True)
                        out.to_csv(f, index=False)
                if os.path.isfile(path[0]):
                    alert = QMessageBox()
                    alert.setWindowTitle("openVA App")
                    alert.setText("results saved to" + path[0])
                    alert.exec()

    def prepare_insilico_indiv_cod(self, results):
        top_cause = results.indiv_prob.idxmax(axis=1)
        indiv_cod = top_cause.reset_index()
        indiv_cod = indiv_cod.set_index("index", drop=False)
        indiv_cod.columns = ["ID", "Top Cause"]
        if self.insilicova_include_probs is True:
            top_prob = results.indiv_prob.max(axis=1)
            indiv_cod["Probability"] = top_prob
        return indiv_cod

    def download_log(self):
        if self.chosen_algorithm == "insilicova":
            errors = self.insilicova_errors
            log = self.insilicova_errors
            warnings = self.insilicova_warnings
        else:
            log = self.interva_log
        if log is None:
            alert = QMessageBox()
            alert.setWindowTitle("openVA App")
            alert.setText(
                "No results available.  Please load data in the expected "
                "format and/or run a VA algorithm.")
            alert.exec()
        else:
            log_file_name = f"{self.chosen_algorithm}_log.txt"
            path = QFileDialog.getSaveFileName(self,
                                               "Save log (txt)",
                                               log_file_name,
                                               "Text Files (*.txt)")
            if path != ("", ""):
                if self.chosen_algorithm == "interva":
                    tmp_log = os.path.join(self.interva_tmp_dir.name,
                                           "errorlogV5.txt")
                    shutil.copyfile(tmp_log, path[0])
                else:
                    # with open(log_file_name, "w") as f_out:
                    with open(path[0], "w") as f_out:
                        f_out.write(f"Log file from {self.chosen_algorithm}")
                        if len(errors) > 0:
                            f_out.write(
                                "\n\nThe following records are incomplete "
                                "and excluded from further processing\n\n")
                            errors_list = [str(k) + " - " + i for k, v in
                                           errors.items() for i in v]
                            f_out.write("\n".join(errors_list))
                        # if isinstance(warnings, dict):
                        if len(warnings) > 1:
                            f_out.write("\n \n first pass \n \n")
                            f_out.write("\n".join(warnings["first_pass"]))
                            f_out.write("\n \n second pass \n \n")
                            f_out.write("\n".join(warnings["second_pass"]))
                        else:
                            f_out.write("\n\n" + warnings["msg"])
                if os.path.isfile(path[0]):
                    alert = QMessageBox()
                    alert.setWindowTitle("openVA App")
                    alert.setText("log saved to" + path[0])
                    alert.exec()
