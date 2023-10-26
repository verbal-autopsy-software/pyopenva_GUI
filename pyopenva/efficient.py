# -*- coding: utf-8 -*-

"""
pyopenva.efficient
~~~~~~~~~~~~~~
This module creates a stacked layout to walk through the analysis step-by-step.
"""

import os
import sys
from contextlib import contextmanager
from io import StringIO
import shutil
import tempfile
from interva import utils
from insilicova.diag import csmf_diag
from insilicova.api import InSilicoVA
# from pyopenva.data import COUNTRIES
from pandas import DataFrame, read_csv
from pandas import concat as pd_concat
from pandas.errors import EmptyDataError, ParserError
from pycrossva.transform import transform
from PyQt5.QtWidgets import (QCheckBox, QComboBox, QFileDialog, QGroupBox,
                             QHBoxLayout, QMessageBox, QLabel, QProgressBar,
                             QPushButton, QScrollArea, QSpinBox,
                             QStackedLayout, QTextEdit, QVBoxLayout, QWidget)
from PyQt5.QtCore import Qt, QThread
from pyopenva.output import (PlotDialog, TableDialog, DemTableDialog,
                             save_plot, _insilicova_subpop, _make_title)
from pyopenva.workers import InSilicoVAWorker, InterVAWorker


class Efficient(QWidget):

    def __init__(self, insilicova_limit):
        super().__init__()
        # self.setGeometry(400, 400, 500, 400)
        self.working_dir = ""
        self.data_page = QWidget()
        self.data = None
        self.data_loaded = False
        self.data_id_col = None
        self.prev_data_id_col = None
        self.pycrossva_data = None
        self.data_ui()
        self.include_va_data = False
        self.select_algorithm_page = QWidget()
        self.select_algorithm_ui()
        self.chosen_algorithm = "insilicova"
        self.insilicova_limit = insilicova_limit
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
        self.interva_rule = True
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
        self.btn_save_plot = None
        self.btn_save_table = None
        self.btn_save_individual_results = None
        self.n_top_causes = 5
        self.options_sex = "all deaths"
        self.options_age = "all deaths"
        self.results_use_prop = False
        self.results_ui()
        self.plot_color = "Greys"
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
        # self.btn_insilicova.pressed.connect(self.disable_age_options)
        self.btn_interva = QPushButton("InterVA")
        self.btn_interva.setMaximumWidth(400)
        self.btn_interva.pressed.connect(
            lambda: self.set_chosen_algorithm("interva"))
        # self.btn_interva.pressed.connect(self.enable_age_options)
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
        gbox_options = QGroupBox("Set Options")
        layout_options = QVBoxLayout()
        layout_n_iter = QHBoxLayout()
        # layout_auto = QHBoxLayout()
        # layout_seed = QHBoxLayout()
        label_n_iter = QLabel("Number of Iterations:")
        spinbox_n_iter = QSpinBox()
        spinbox_n_iter.setRange(4000, 40000)
        spinbox_n_iter.setSingleStep(1000)
        spinbox_n_iter.setAlignment(Qt.AlignCenter)
        spinbox_n_iter.setValue(self.insilicova_n_sim)
        spinbox_n_iter.valueChanged.connect(self.set_insilicova_n_sim)
        spinbox_n_iter.setMaximumWidth(150)
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
        self.insilicova_pycva_tedit = QTextEdit()
        self.insilicova_pycva_tedit.setText("(pyCrossVA messages...)")
        self.insilicova_pycva_tedit.setEnabled(False)
        self.insilicova_pycva_tedit.setMaximumHeight(100)
        self.btn_check_convergence = QPushButton("Check convergence")
        self.btn_check_convergence.setEnabled(False)
        self.btn_check_convergence.clicked.connect(self.check_convergence)
        self.btn_save_insilicova_log = QPushButton(
            "Save log from data checks")
        self.btn_save_insilicova_log.setEnabled(False)
        self.btn_save_insilicova_log.clicked.connect(self.save_log)

        self.btn_insilicova_to_select_algorithm = QPushButton("Back")
        self.btn_insilicova_go_to_results_page = QPushButton("Show Results")
        self.btn_insilicova_go_to_results_page.pressed.connect(
            self.show_results_page)
        self.btn_insilicova_ui_exit = QPushButton("Exit")

        layout_n_iter.addWidget(label_n_iter)
        layout_n_iter.addWidget(spinbox_n_iter)
        # layout_auto.addWidget(label_auto_length)
        # layout_auto.addWidget(self.insilicova_combo_auto)
        # layout_seed.addWidget(label_seed)
        # layout_seed.addWidget(spinbox_seed)
        layout_options.addLayout(layout_n_iter)
        # layout_options.addLayout(layout_auto)
        # layout_options.addLayout(layout_seed)
        gbox_options.setLayout(layout_options)
        layout.addWidget(gbox_options)
        layout.addStretch(1)
        layout.addWidget(self.btn_insilicova_run)
        layout.addWidget(self.insilicova_pbar)
        layout.addWidget(self.label_insilicova_progress)
        layout.addWidget(self.btn_insilicova_stop)
        layout.addStretch(1)
        layout.addWidget(self.insilicova_pycva_tedit)
        layout.addStretch(1)
        h_box_checks = QHBoxLayout()
        h_box_checks.addWidget(self.btn_check_convergence)
        h_box_checks.addWidget(self.btn_save_insilicova_log)
        layout.addLayout(h_box_checks)
        layout.addStretch(1)
        h_box = QHBoxLayout()
        h_box.addWidget(self.btn_insilicova_to_select_algorithm)
        h_box.addWidget(self.btn_insilicova_go_to_results_page)
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
        self.interva_pycva_tedit = QTextEdit()
        self.interva_pycva_tedit.setText("(pyCrossVA messages...)")
        self.interva_pycva_tedit.setEnabled(False)
        self.interva_pycva_tedit.setMaximumHeight(100)
        self.btn_save_interva_log = QPushButton(
            "Save Log from data checks")
        self.btn_save_interva_log.setEnabled(False)
        self.btn_save_interva_log.clicked.connect(self.save_log)
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
        layout.addWidget(self.interva_pycva_tedit)
        layout.addStretch(1)
        layout.addWidget(self.btn_save_interva_log)
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
        gbox_options = QGroupBox("Options")
        vbox_options = QVBoxLayout()
        hbox_options = QHBoxLayout()
        self.spinbox_n_causes = QSpinBox()
        self.spinbox_n_causes.setRange(1, 61)
        self.spinbox_n_causes.setPrefix("Include ")
        self.spinbox_n_causes.setSuffix(" causes in the results")
        self.spinbox_n_causes.setValue(self.n_top_causes)
        self.spinbox_n_causes.valueChanged.connect(self.set_n_top_causes)
        self.spinbox_n_causes.setMaximumWidth(250)
        # Leaving this in case we want to turn of interva rule in
        # efficient mode -- if so, just need to add checkbox to this ui
        self.chbox_interva_rule = QCheckBox(
            "Count uncertain assignments as 'Undetermined'")
        self.chbox_interva_rule.setChecked(self.interva_rule)
        self.chbox_interva_rule.toggled.connect(self.set_interva_rule)
        self.chbox_use_prop = QCheckBox("show CSMF as proportions")
        self.chbox_use_prop.setChecked(self.results_use_prop)
        self.chbox_use_prop.toggled.connect(self.set_results_use_prop)
        hbox_options.addWidget(self.spinbox_n_causes)
        # hbox_options.addWidget(self.chbox_interva_rule)
        # hbox_options.setAlignment(self.chbox_interva_rule, Qt.AlignRight)
        hbox_options.addWidget(self.chbox_use_prop)
        hbox_options.setAlignment(self.chbox_use_prop, Qt.AlignRight)
        vbox_options.addLayout(hbox_options)
        # vbox_options.addWidget(self.chbox_use_prop)
        self.label_dem_results = QLabel("Select demographic groups")
        self.label_dem_results.setAlignment(Qt.AlignCenter)
        vbox_options.addWidget(self.label_dem_results)

        hbox_demographics = QHBoxLayout()
        age_option_set = ["all deaths",
                          "adult",
                          "child",
                          "neonate"]
        label_age = QLabel("age:")
        label_age.setMaximumWidth(30)
        self.options_combo_age = QComboBox()
        self.options_combo_age.addItems(age_option_set)
        self.options_combo_age.setCurrentIndex(
            age_option_set.index(self.options_age))
        self.options_combo_age.currentTextChanged.connect(self.set_options_age)
        sex_option_set = ["all deaths",
                          "female",
                          "male"]
        label_sex = QLabel("sex:")
        label_sex.setMaximumWidth(30)
        self.options_combo_sex = QComboBox()
        self.options_combo_sex.addItems(sex_option_set)
        # self.options_combo_sex.setEditable(True)
        # self.options_combo_sex.lineEdit().setAlignment(Qt.AlignCenter)
        # self.options_combo_sex.setStyleSheet(
        #     "QComboBox { background-color: grey; }")
        self.options_combo_sex.setCurrentIndex(
            sex_option_set.index(self.options_sex))
        self.options_combo_sex.currentTextChanged.connect(
            self.set_options_sex)
        hbox_demographics.addWidget(label_age)
        hbox_demographics.addWidget(self.options_combo_age)
        hbox_demographics.addWidget(label_sex)
        hbox_demographics.addWidget(self.options_combo_sex)
        hbox_demographics.insertSpacing(2, 50)

        vbox_options.insertSpacing(1, 25)
        vbox_options.insertSpacing(3, 15)
        vbox_options.addLayout(hbox_demographics)
        gbox_options.setLayout(vbox_options)

        gbox_show = QGroupBox("Show Results")
        hbox_show = QHBoxLayout()
        self.btn_show_table = QPushButton("Show \n CSMF Table")
        self.btn_show_table.pressed.connect(self.run_table_dialog)
        self.btn_show_plot = QPushButton("Show \n CSMF Plot")
        self.btn_show_plot.pressed.connect(self.run_plot_dialog)
        self.btn_show_dem = QPushButton("Show \n Demographics")
        self.btn_show_dem.pressed.connect(self.run_table_dialog_dem)
        hbox_show.addWidget(self.btn_show_table)
        hbox_show.addWidget(self.btn_show_plot)
        hbox_show.addWidget(self.btn_show_dem)
        gbox_show.setLayout(hbox_show)

        gbox_save = QGroupBox("Save Results")
        vbox_save = QVBoxLayout()
        hbox_save = QHBoxLayout()
        self.btn_save_table = QPushButton("Save Table")
        self.btn_save_table.clicked.connect(self.save_csmf_table)
        self.btn_save_plot = QPushButton("Save Plot")
        self.btn_save_plot.clicked.connect(self.save_csmf_plot)
        self.btn_save_individual_results = QPushButton(
            "Save \n Individual Cause Assignments")
        self.btn_save_individual_results.clicked.connect(
            self.save_indiv_cod
        )
        self.chbox_insilicova_include_probs = QCheckBox(
            "Include probability of top cause (with individual CODs)")
        self.chbox_insilicova_include_probs.toggled.connect(
            self.set_insilicova_include_probs)
        self.chbox_include_va_data = QCheckBox(
            "Include VA data (with individual CODs)")
        self.chbox_include_va_data.toggled.connect(
            self.set_include_va_data)
        hbox_save.addWidget(self.btn_save_table)
        hbox_save.addWidget(self.btn_save_plot)
        vbox_save.addLayout(hbox_save)
        vbox_save.addWidget(self.btn_save_individual_results)
        if self.chosen_algorithm == "insilicova":
            vbox_save.addWidget(self.chbox_insilicova_include_probs)
        vbox_save.addWidget(self.chbox_include_va_data)
        gbox_save.setLayout(vbox_save)

        hbox_navigate = QHBoxLayout()
        self.btn_results_to_algorithm = QPushButton("Back")
        self.btn_results_ui_exit = QPushButton("Exit")
        hbox_navigate.addWidget(self.btn_results_to_algorithm)
        hbox_navigate.addWidget(self.btn_results_ui_exit)
        layout.addWidget(gbox_options)
        layout.addStretch(1)
        layout.addWidget(gbox_show)
        layout.addStretch(1)
        layout.addWidget(gbox_save)
        layout.addStretch(1)
        layout.addLayout(hbox_navigate)
        self.results_page.setLayout(layout)

    def load_data(self):
        path = QFileDialog.getOpenFileName(self,
                                           "Open a CSV file",
                                           # "",
                                           self.working_dir,
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
                self.data_id_col = None
                self.prev_data_id_col = None
                # reset app
                self._reset_results()
                # self.label_insilicova_progress.setText(
                #     "(no results)")
                # self.insilicova_warnings = None
                # self.insilicova_errors = None
                # self.insilicova_results = None
                # self.label_interva_progress.setText(
                #     "(no results)")
                # self.insilicova_pbar.setValue(0)
                # self.interva_log = None
                # self.interva_results = None
                # self.interva_pbar.setValue(0)
                # self.pycrossva_data = None
                # self.interva_pycva_tedit.setText("(pyCrossVA messages...)")
                # self.insilicova_pycva_tedit.setText(
                # "(pyCrossVA messages...)")
            except UnicodeDecodeError as exc:
                alert = QMessageBox()
                alert.setWindowTitle("openVA App")
                alert.setIcon(QMessageBox.Warning)
                exc_slice = slice((exc.start - 20), (exc.end + 20))
                msg = ("Unable to read in CSV file "
                       f"{path[0].split('/')[-1]}.\n\n"
                       "File contains unexpected characters:\n\n"
                       f"{exc.object[exc_slice]}.")
                alert.setText(msg)
                alert.exec()
            except ParserError:
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
        # Note: don't need to check duplicate column names because read_csv
        # will rename to unique names, e.g., ID & ID.1
        if self.pycrossva_data is not None:
            qmbox_yn = QMessageBox()
            msg = ("You have created pyCrossVA data and/or COD results.\n\n"
                   "Changing the column ID will DELETE these results.\n\n"
                   "Do you want to change the ID?")
            ans = qmbox_yn.question(self, "", msg, qmbox_yn.Yes | qmbox_yn.No)
            if ans == qmbox_yn.Yes:
                self.data_id_col = id_col
                self.prev_data_id_col = id_col
                self._reset_results()
                if self.data_id_col not in (None, "no ID column"):
                    if self.data[self.data_id_col].is_unique is False:
                        alert = QMessageBox()
                        alert.setWindowTitle("openVA App")
                        alert.setIcon(QMessageBox.Warning)
                        alert.setText(
                            "ID column does not have a unique value "
                            "for every row")
                        alert.exec()
            else:
                if self.prev_data_id_col is None:
                    prev_index = self.combo_data_id_col.findText(
                        "no ID column")
                else:
                    prev_index = self.combo_data_id_col.findText(
                        self.prev_data_id_col)
                self.combo_data_id_col.blockSignals(True)
                self.combo_data_id_col.setCurrentIndex(prev_index)
                self.combo_data_id_col.blockSignals(False)
        else:
            self.data_id_col = id_col
            self.prev_data_id_col = id_col
            if self.data_id_col not in (None, "no ID column"):
                if self.data[self.data_id_col].is_unique is False:
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

    def set_include_va_data(self, checked):
        if checked:
            self.include_va_data = True
            if self.data_id_col not in ("no ID column", None):
                if self.data[self.data_id_col].is_unique is False:
                    alert = QMessageBox()
                    alert.setWindowTitle("openVA App")
                    alert.setIcon(QMessageBox.Warning)
                    alert.setText(
                        "Unable to save individual cause assignments with"
                        "VA data (ID column does not have unique values).")
                    alert.exec()
                    self.include_va_data = False
                    self.chbox_include_va_data.setChecked(False)
        else:
            self.include_va_data = False

    def run_pycrossva(self):
        raw_data_col_id = self.data_id_col
        if self.data_id_col == "no ID column":
            raw_data_col_id = None
        pycrossva_stdout = StringIO()
        with self._capture_stdout(pycrossva_stdout):
            self.pycrossva_data = transform(
                mapping=("2016WHOv151", "InterVA5"),
                raw_data=self.data,
                raw_data_id=raw_data_col_id,
                lower=True)
        if (self.pycrossva_data.iloc[:, 1:] == ".").all(axis=None):
            alert = QMessageBox()
            alert.setWindowTitle("openVA App")
            alert.setText(
                "Problem converting data to openVA format:\n"
                "ALL VALUES ARE MISSING"
                "\nThe data have an unexpected format and cannot be "
                "processed.  Please reload data in the expected format.")
            alert.exec()
        if self.chosen_algorithm == "insilicova":
            self.insilicova_pycva_tedit.setEnabled(True)
        else:
            self.interva_pycva_tedit.setEnabled(True)
        pycrossva_msg = pycrossva_stdout.getvalue()
        if len(pycrossva_msg) == 0:
            pycrossva_msg = "All good!"
        pycrossva_msg = "pyCrossVA finished.\n\n" + pycrossva_msg
        if self.chosen_algorithm == "insilicova":
            self.insilicova_pycva_tedit.setText(pycrossva_msg)
            self.insilicova_pycva_tedit.setReadOnly(True)
        else:
            self.interva_pycva_tedit.setText(pycrossva_msg)
            self.interva_pycva_tedit.setReadOnly(True)

    @contextmanager
    def _capture_stdout(self, output):
        stdout = sys.stdout
        sys.stdout = output
        try:
            yield
        finally:
            sys.stdout = stdout

    def set_insilicova_n_sim(self, n_sim: int):
        self.insilicova_n_sim = n_sim

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
        if self.chosen_algorithm == "interva":
            self.chbox_interva_rule.setEnabled(True)
        else:
            self.chbox_interva_rule.setEnabled(False)

    def set_n_top_causes(self, n):
        self.n_top_causes = n

    def set_interva_rule(self, checked):
        if checked:
            self.interva_rule = True
        else:
            self.interva_rule = False

    def set_options_sex(self, sex):
        self.options_sex = sex

    def set_options_age(self, age):
        self.options_age = age

    # def disable_age_options(self):
    #     self.label_dem_results.setText(
    #         "Select demographic groups \n (only available with InterVA)")
    #     self.options_combo_age.setEnabled(False)
    #     self.options_combo_sex.setEnabled(False)
    #     self.btn_show_dem.setEnabled(False)

    # def enable_age_options(self):
    #     self.label_dem_results.setText("Select demographic groups")
    #     self.options_combo_age.setEnabled(True)
    #     self.options_combo_sex.setEnabled(True)
    #     self.btn_show_dem.setEnabled(True)

    def set_plot_color(self, color):
        self.plot_color = color

    def set_results_use_prop(self, checked):
        if checked:
            self.results_use_prop = True
        else:
            self.results_use_prop = False

    # TODO: need to clean these up (window management handled in main)
    def show_data_page(self):
        self.stacked_layout.setCurrentIndex(0)

    def show_algorithm_page(self):
        if self.chosen_algorithm == "insilicova":
            self.show_insilicova_page()
        # elif self.chosen_algorithm == "interva":
        else:
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
        self.btn_save_insilicova_log.setEnabled(False)
        self.btn_check_convergence.setEnabled(False)
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
            self.btn_save_insilicova_log.setEnabled(False)
            self.btn_check_convergence.setEnabled(False)
        else:
            self.run_pycrossva()
            tmp_ins = InSilicoVA(self.pycrossva_data, run=False)
            tmp_ins._remove_bad(is_numeric=False)
            n_valid = tmp_ins.data.shape[0]
            n_removed = self.pycrossva_data.shape[0] - n_valid
            if self.pycrossva_data["ID"].is_unique:
                index_removed = (~self.pycrossva_data.ID.isin(tmp_ins.data.ID))
                id_removed = self.pycrossva_data.ID[index_removed].astype("str")
            del tmp_ins
            if n_valid < self.insilicova_limit:
                msg = ("InSilicoVA is unavailable.  At least "
                       f"{self.insilicova_limit} deaths are needed for "
                       "reliable results.\n\nData check removed"
                       f" {n_removed} deaths because of missing data.")
                if self.pycrossva_data["ID"].is_unique:
                    msg += "  IDs are listed below."
                msg += "\n(InterVA is available.)\n\n"
                alert = ScrollMessageBox("openVA App: InSilicoVA message",
                                         msg, id_removed)
                alert.exec()
                self.btn_insilicova_run.setEnabled(True)
                self.btn_load_data.setEnabled(True)
                self.btn_save_insilicova_log.setEnabled(True)
                self.btn_check_convergence.setEnabled(True)
            else:
                if self.insilicova_auto == "True":
                    auto_extend = True
                burnin = max(int(self.insilicova_n_sim / 2), 1)
                thin = 10
                self.insilicova_thread = QThread()
                self.insilicova_worker = InSilicoVAWorker(
                    data=self.pycrossva_data,
                    data_type="WHO2016",
                    n_sim=self.insilicova_n_sim,
                    thin=thin,
                    burnin=burnin,
                    auto_length=auto_extend,
                    # n_sim=200,
                    # thin=20,
                    # burnin=5,
                    # auto_length=False,
                    seed=self.insilicova_seed,
                    gui_ctrl=self.insilicova_ctrl)
                self.insilicova_worker.moveToThread(self.insilicova_thread)
                self.insilicova_thread.started.connect(
                    self.insilicova_worker.run)
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
                    lambda: self.btn_save_insilicova_log.setEnabled(True))
                self.insilicova_thread.finished.connect(
                    lambda: self.btn_check_convergence.setEnabled(True))

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
        self.btn_save_interva_log.setEnabled(False)
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
            self.btn_save_interva_log.setEnabled(True)
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
            self.update_interva_progress_label(
                "(running algorithm)")
            # TODO: clear old error log if it exists?
            self.interva_tmp_dir = tempfile.TemporaryDirectory()
            self.run_pycrossva()
            tmp_ins = InSilicoVA(self.pycrossva_data, run=False)
            tmp_ins._remove_bad(is_numeric=False)
            n_valid = tmp_ins.data.shape[0]
            n_removed = self.pycrossva_data.shape[0] - n_valid
            if self.pycrossva_data["ID"].is_unique:
                index_removed = (~self.pycrossva_data.ID.isin(tmp_ins.data.ID))
                id_removed = self.pycrossva_data.ID[index_removed].astype(
                    "str")
            del tmp_ins
            msg = (f"Data check removed {n_removed} deaths "
                   "because of missing data.")
            if self.pycrossva_data["ID"].is_unique:
                msg += "  IDs are listed below."
            alert = ScrollMessageBox("openVA App: InterVA message",
                                     msg, id_removed)
            alert.exec()
            self.btn_insilicova_run.setEnabled(True)
            self.btn_load_data.setEnabled(True)
            self.btn_save_insilicova_log.setEnabled(True)
            self.btn_check_convergence.setEnabled(True)
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
                lambda: self.btn_save_interva_log.setEnabled(True))

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
            empty = self._check_empty_results()
            if empty:
                alert = QMessageBox()
                alert.setWindowTitle("openVA App")
                alert.setText(
                    "There are no VA records for the selected group:\n"
                    f"age: {self.options_age},   sex: {self.options_sex}")
                alert.exec()
            else:
                self.plot_dialog = PlotDialog(
                    results=results,
                    algorithm=self.chosen_algorithm,
                    parent=self,
                    top=self.n_top_causes,
                    colors=self.plot_color,
                    age=self.options_age,
                    sex=self.options_sex,
                    interva_rule=self.interva_rule,
                    use_prop=self.results_use_prop)
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
            empty = self._check_empty_results()
            if empty:
                alert = QMessageBox()
                alert.setWindowTitle("openVA App")
                alert.setText(
                    "There are no VA records for the selected group:\n"
                    f"age: {self.options_age},   sex: {self.options_sex}")
                alert.exec()
            else:
                self.table_dialog = TableDialog(
                    results,
                    parent=self,
                    top=self.n_top_causes,
                    age=self.options_age,
                    sex=self.options_sex,
                    interva_rule=self.interva_rule,
                    use_prop=self.results_use_prop)
                self.table_dialog.resize(self.table_dialog.table.width(),
                                         self.table_dialog.table.height())
                self.table_dialog.exec()

    def run_table_dialog_dem(self):
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
        # elif self.chosen_algorithm == "insilicova":
        #     alert = QMessageBox()
        #     alert.setWindowTitle("openVA App")
        #     alert.setText("Demographics only available with InterVA")
        #     alert.exec()
        else:
            if self.chosen_algorithm == "interva":
                dem_results = utils._get_cod_with_dem(results)
                self.table_dialog = DemTableDialog(dem_results, self)
                self.table_dialog.resize(self.table_dialog.view.width(),
                                         self.table_dialog.view.height())
                self.table_dialog.exec()
            else:
                dem_results = results.data_checked.apply(
                    utils._get_dem_groups,
                    axis=1)
                dem_results = DataFrame(list(dem_results))
                self.table_dialog = DemTableDialog(dem_results, self)
                self.table_dialog.resize(self.table_dialog.view.width(),
                                         self.table_dialog.view.height())
                self.table_dialog.exec()

    def save_csmf_table(self):
        prop_scale = 100
        if self.results_use_prop:
            prop_scale = 1
        if self.chosen_algorithm == "insilicova":
            results = self.insilicova_results
            no_subpop = (self.options_age == "all deaths" and
                         self.options_sex == "all deaths")
        else:
            results = self.interva_results
        if results is None:
            alert = QMessageBox()
            alert.setWindowTitle("openVA App")
            alert.setText(
                "No results available.  Please load data in the expected "
                "format and/or run a VA algorithm.")
            alert.exec()
        elif self._check_empty_results():
            alert = QMessageBox()
            alert.setWindowTitle("openVA App")
            alert.setText(
                "There are no VA records for the selected "
                f"group:\n age: {self.options_age},   "
                f"sex: {self.options_sex}")
            alert.exec()
        else:
            # results_file_name = f"{self.chosen_algorithm}_csmf.csv"
            results_file_name = self._make_results_file_name("table")
            path = QFileDialog.getSaveFileName(self,
                                               "Save CSMF (csv)",
                                               results_file_name,
                                               "CSV Files (*.csv)")
            if path != ("", ""):
                n_top_causes = self.n_top_causes
                csmf = results.get_csmf(top=n_top_causes)
                if isinstance(csmf, DataFrame):
                    if no_subpop:
                        csmf_df = csmf.sort_values(
                            by="Mean", ascending=False).copy()
                    else:
                        csmf_df = _insilicova_subpop(results,
                                                     self.options_age,
                                                     self.options_sex,
                                                     self.n_top_causes)
                        csmf_df = csmf_df.sort_values(ascending=False)
                        csmf_df.name = "Mean"
                    csmf_df = csmf_df.reset_index()
                    csmf_df.rename(columns={"index": "Cause",
                                            "Mean": "CSMF (Mean)"},
                                   inplace=True)
                else:
                    age = self.options_age
                    if self.options_age == "all deaths":
                        age = None
                    sex = self.options_sex
                    if self.options_sex == "all deaths":
                        sex = None
                    csmf = utils.csmf(results,
                                      top=n_top_causes,
                                      interva_rule=self.interva_rule,
                                      age=age,
                                      sex=sex)
                    csmf.sort_values(ascending=False, inplace=True)
                    csmf_df = csmf.reset_index()[0:n_top_causes]
                    title = _make_title(age=self.options_age,
                                        sex=self.options_sex)
                    csmf_df.rename(columns={"index": "Cause",
                                            0: title},
                                   inplace=True)
                try:
                    csmf_df.iloc[:, 1:] *= prop_scale  # ok for std error (sqrt (a * var[x]))
                    csmf_df.to_csv(path[0], index=False)
                except (OSError, PermissionError):
                    alert = QMessageBox()
                    alert.setWindowTitle("openVA App")
                    alert.setIcon(QMessageBox.Warning)
                    alert.setText(
                        f"Unable to save {path[0]}.\n" +
                        "(don't have permission or read-only file system)")
                    alert.exec()
                if os.path.isfile(path[0]):
                    alert = QMessageBox()
                    alert.setWindowTitle("openVA App")
                    alert.setText("results saved to" + path[0])
                    alert.exec()
                else:
                    alert = QMessageBox()
                    alert.setWindowTitle("openVA App")
                    alert.setText(
                        "ERROR: unable to save results to" + path[0])
                    alert.exec()

    def save_csmf_plot(self):
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
        elif self._check_empty_results():
            alert = QMessageBox()
            alert.setWindowTitle("openVA App")
            alert.setText(
                "There are no VA records for the selected "
                f"group:\n age: {self.options_age},   "
                f"sex: {self.options_sex}")
            alert.exec()
        else:
            # results_file_name = f"{self.chosen_algorithm}_csmf.pdf"
            results_file_name = self._make_results_file_name("plot")
            path = QFileDialog.getSaveFileName(self,
                                               "Save CSMF plot (pdf)",
                                               results_file_name,
                                               "PDF Files (*.pdf)")
            if path != ("", ""):
                # save_plot has try/except for OS & Permission errors
                save_plot(results=results,
                          algorithm=self.chosen_algorithm,
                          top=self.n_top_causes,
                          file_name=path[0],
                          plot_colors=self.plot_color,
                          age=self.options_age,
                          sex=self.options_sex,
                          interva_rule=self.interva_rule,
                          use_prop=self.results_use_prop)
                if os.path.isfile(path[0]):
                    alert = QMessageBox()
                    alert.setWindowTitle("openVA App")
                    alert.setText("results saved to" + path[0])
                    alert.exec()
                else:
                    alert = QMessageBox()
                    alert.setWindowTitle("openVA App")
                    alert.setText(
                        "ERROR: unable to save results to" + path[0])
                    alert.exec()

    def save_indiv_cod(self):
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
        elif self._check_empty_results():
            alert = QMessageBox()
            alert.setWindowTitle("openVA App")
            alert.setText(
                "There are no VA records for the selected "
                f"group:\n age: {self.options_age},   "
                f"sex: {self.options_sex}")
            alert.exec()
        else:
            # results_file_name = f"{self.chosen_algorithm}_individual_cod.csv"
            results_file_name = self._make_results_file_name("indiv")
            path = QFileDialog.getSaveFileName(self,
                                               "Save CSMF (csv)",
                                               results_file_name,
                                               "CSV Files (*.csv)")
            if path != ("", ""):
                if self.chosen_algorithm == "insilicova":
                    out = self.prepare_insilicova_indiv_cod(results)
                else:
                    how_to_merge = "outer"
                    keep = utils._get_cod_with_dem(results)
                    if self.options_age != "all deaths":
                        keep = keep[keep["age"] == self.options_age]
                        how_to_merge = "inner"
                    if self.options_sex != "all deaths":
                        keep = keep[keep["sex"] == self.options_sex]
                        how_to_merge = "inner"
                    keep_id = keep["ID"]
                    out = results.results["VA5"]
                    out = out.drop(["WHOLEPROB"], axis=1)
                    if self.n_top_causes in [1, 2]:
                        out = out.drop(["CAUSE3", "LIK3"], axis=1)
                    if self.n_top_causes == 1:
                        out = out.drop(["CAUSE2", "LIK2"], axis=1)
                    out = out[out["ID"].isin(keep_id)]
                    if self.data_id_col in (None, "no ID column"):
                        out["ID"] = out["ID"].astype("int64")
                    if self.include_va_data:
                        tmp_data = self._add_id_to_input_data()
                        tmp_data.columns = [col.split("-")[-1] for
                                            col in tmp_data.columns]
                        out = out.merge(tmp_data, how=how_to_merge, on="ID")
                try:
                    out.to_csv(path[0], index=False)
                    if os.path.isfile(path[0]):
                        alert = QMessageBox()
                        alert.setWindowTitle("openVA App")
                        alert.setText("results saved to" + path[0])
                        alert.exec()
                    else:
                        alert = QMessageBox()
                        alert.setWindowTitle("openVA App")
                        alert.setText(
                            "ERROR: unable to save results " + path[0])
                        alert.exec()
                except (OSError, PermissionError):
                    alert = QMessageBox()
                    alert.setWindowTitle("openVA App")
                    alert.setIcon(QMessageBox.Warning)
                    alert.setText(
                        f"Unable to save {path[0]}.\n" +
                        "(don't have permission or read-only file system)")
                    alert.exec()

    # def prepare_insilicova_indiv_cod(self, results):
    #     top_cause = results.indiv_prob.idxmax(axis=1)
    #     indiv_cod = top_cause.reset_index()
    #     indiv_cod = indiv_cod.set_index("index", drop=False)
    #     indiv_cod.columns = ["ID", "Top Cause"]
    #     how_to_merge = "outer"
    #     if self.insilicova_include_probs is True:
    #         top_prob = results.indiv_prob.max(axis=1)
    #         indiv_cod["Probability"] = top_prob
    #
    #     if (self.options_age != "all deaths" or
    #             self.options_sex != "all deaths"):
    #         how_to_merge = "inner"
    #         age_groups = []
    #         sex_groups = []
    #         if self.options_age == "all deaths":
    #             age_groups = ["neonate", "child", "adult"]
    #         else:
    #             age_groups.append(self.options_age)
    #         if self.options_sex == "all deaths":
    #             sex_groups = ["female", "male"]
    #         else:
    #             sex_groups.append(self.options_sex)
    #
    #         dem_groups = results.data_checked.apply(utils._get_dem_groups,
    #                                                 axis=1)
    #         dem_groups = DataFrame(list(dem_groups)).set_index("ID")
    #         indiv_cod = concat([indiv_cod, dem_groups], axis=1)
    #         subpop_index = (indiv_cod["age"].isin(age_groups)) & (
    #             indiv_cod["sex"].isin(sex_groups))
    #         indiv_cod = indiv_cod[subpop_index]
    #         indiv_cod = indiv_cod.drop(columns=["age", "sex"])
    #
    #     if self.include_va_data:
    #         tmp_data = self._add_id_to_input_data()
    #         indiv_cod = indiv_cod.merge(tmp_data, how=how_to_merge, on="ID")
    #
    #     if self.data_id_col is None:
    #         indiv_cod = indiv_cod.sort_values(by="ID")
    #     else:
    #         indiv_cod = indiv_cod.set_index("ID")
    #         indiv_cod = indiv_cod.reindex(self.data[self.data_id_col])
    #         indiv_cod = indiv_cod.reset_index(names="ID")
    #
    #     return indiv_cod

    def prepare_insilicova_indiv_cod(self, results):
        all_results = []
        how_to_merge = "outer"
        for i in range(results.indiv_prob.shape[0]):
            row = results.indiv_prob.iloc[i].copy()
            top_causes = row.sort_values(ascending=False)[0:self.n_top_causes]
            if self.insilicova_include_probs:
                labels = ["Cause", "Prob"] * self.n_top_causes
                numbers = []
                [numbers.extend([str(a)]*2) for a in
                 range(1, self.n_top_causes + 1)]
                col_names = [a + b for a, b in zip(labels, numbers)]
                values = [i for j in top_causes.items() for i in j]
                all_results.append(
                    DataFrame([values], columns=col_names, index=[row.name]))
            else:
                col_names = ["Cause" + str(i) for i in
                             range(1, self.n_top_causes + 1)]
                all_results.append(
                    # DataFrame([top_causes["index"].tolist()],
                    DataFrame([top_causes.index.tolist()],
                              columns=col_names,
                              index=[row.name]))
        indiv_cod = pd_concat(all_results)
        indiv_cod = indiv_cod.reset_index(names="ID")
        if (self.options_age != "all deaths" or
                self.options_sex != "all deaths"):
            how_to_merge = "inner"
            age_groups = []
            sex_groups = []
            if self.options_age == "all deaths":
                age_groups = ["neonate", "child", "adult"]
            else:
                age_groups.append(self.options_age)
            if self.options_sex == "all deaths":
                sex_groups = ["female", "male"]
            else:
                sex_groups.append(self.options_sex)

            dem_groups = self.insilicova_results.data_checked.apply(
                utils._get_dem_groups, axis=1)
            # dem_groups = DataFrame(list(dem_groups)).set_index("ID")
            dem_groups = DataFrame(list(dem_groups))
            # indiv_cod = pd_concat([indiv_cod, dem_groups], axis=1)
            indiv_cod = indiv_cod.merge(dem_groups, on="ID")
            subpop_index = (indiv_cod["age"].isin(age_groups)) & (
                indiv_cod["sex"].isin(sex_groups))
            indiv_cod = indiv_cod[subpop_index]
            indiv_cod = indiv_cod.drop(columns=["age", "sex"])

        if self.include_va_data:
            tmp_data = self._add_id_to_input_data()
            tmp_data.columns = [col.split("-")[-1] for col in tmp_data.columns]
            indiv_cod = indiv_cod.merge(tmp_data, how=how_to_merge, on="ID")

        if (self.options_age == "all deaths" and
                self.options_sex == "all deaths"):
            if self.data_id_col is None:
                indiv_cod = indiv_cod.sort_values(by="ID")
            else:
                indiv_cod = indiv_cod.set_index("ID")
                indiv_cod = indiv_cod.reindex(
                    self.data[self.data_id_col])
                indiv_cod = indiv_cod.reset_index(names="ID")

        return indiv_cod

    def save_log(self):
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
            log_file_name = os.path.join(self.working_dir,
                                         log_file_name)
            path = QFileDialog.getSaveFileName(self,
                                               "Save log (txt)",
                                               log_file_name,
                                               "Text Files (*.txt)")
            if path != ("", ""):
                try:
                    if self.chosen_algorithm == "interva":
                        tmp_log = os.path.join(self.interva_tmp_dir.name,
                                               "errorlogV5.txt")
                        shutil.copyfile(tmp_log, path[0])
                    else:
                        with open(path[0], "w") as f_out:
                            f_out.write(
                                f"Log file from {self.chosen_algorithm}")
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
                    else:
                        alert = QMessageBox()
                        alert.setWindowTitle("openVA App")
                        alert.setText(
                            "ERROR: unable to save log to" + path[0])
                        alert.exec()
                except (OSError, PermissionError):
                    alert = QMessageBox()
                    alert.setWindowTitle("openVA App")
                    alert.setIcon(QMessageBox.Warning)
                    alert.setText(
                        f"Unable to save {path[0]}.\n" +
                        "(don't have permission or read-only file system)")
                    alert.exec()

    def check_convergence(self):
        conv = csmf_diag(self.insilicova_results)
        failed_conv = conv[(conv["Halfwidth test"] == "failed") |
                           (conv["Stationarity test"] == "failed")].index
        alert = QMessageBox()
        alert.setWindowTitle("openVA App")
        if len(failed_conv) == 0:
            alert.setText("All causes with CSMF > 0.02 converged")
        else:
            alert.setText(
                "The following causes with CSMF > 0.02 did not converge:\n\n"
                f"{', '.join(failed_conv.to_list())}"
                "\n\n (convergence can be achieved by increasing the "
                "number of simulations)")
        alert.exec()

    def _check_empty_results(self):
        empty = True
        if self.chosen_algorithm == "insilicova":
            if self.insilicova_results is not None:
                out = self.insilicova_results.data_checked.apply(
                    utils._get_dem_groups,
                    axis=1)
                out = DataFrame(list(out))
        else:
            if self.interva_results is not None:
                out = utils._get_cod_with_dem(self.interva_results)
        if self.options_age != "all deaths":
            out = out[out["age"] == self.options_age]
        if self.options_sex != "all deaths":
            out = out[out["sex"] == self.options_sex]
        empty = out.shape[0] == 0
        return empty

    def _make_results_file_name(self, fnc):
        results_file_name = f"{self.chosen_algorithm}"
        if self.options_age != "all deaths":
            results_file_name += f"_{self.options_age}"
        if self.options_sex != "all deaths":
            results_file_name += f"_{self.options_sex}"
        if fnc == "plot":
            results_file_name += "_csmf.pdf"
        elif fnc == "table":
            results_file_name += "_csmf.csv"
        else:
            results_file_name += "_individual_cod.csv"
        if self.working_dir != "":
            results_file_name = os.path.join(self.working_dir,
                                             results_file_name)
        return results_file_name

    def _add_id_to_input_data(self):
        tmp_data = self.data.copy()
        if self.data_id_col in (None, "no ID column"):
            tmp_data["ID"] = [i + 1 for i in self.data.index]
        else:
            tmp_data["ID"] = tmp_data[self.data_id_col].copy()
        return tmp_data

    def _reset_results(self):
        self.pycrossva_data = None
        self.interva_pycva_tedit.setText("(pyCrossVA messages...)")
        self.insilicova_pycva_tedit.setText("(pyCrossVA messages...)")
        self.label_insilicova_progress.setText("(no results)")
        self.insilicova_warnings = None
        self.insilicova_errors = None
        self.insilicova_results = None
        self.label_interva_progress.setText("(no results)")
        self.insilicova_pbar.setValue(0)
        self.interva_log = None
        self.interva_results = None
        self.interva_pbar.setValue(0)
        self.label_interva_chosen_options.setText("")
        self.label_interva_chosen_malaria.setText("")
        self.label_interva_chosen_hiv.setText("")


class ScrollMessageBox(QMessageBox):

    def __init__(self, title, msg, msg_list, *args, **kwargs):
        QMessageBox.__init__(self, *args, **kwargs)
        self.setWindowTitle(title)
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        self.content = QWidget()
        scroll.setWidget(self.content)
        lay = QVBoxLayout(self.content)
        lay.addWidget(QLabel(msg, self))
        for item in msg_list:
            lay.addWidget(QLabel(item, self))
        self.layout().addWidget(scroll)
        self.setStyleSheet("QScrollArea{min-width:500 px; min-height: 400px}")
