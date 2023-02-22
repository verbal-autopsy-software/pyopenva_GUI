# -*- coding: utf-8 -*-

"""
pyopenva.efficient
~~~~~~~~~~~~~~
This module creates a stacked layout to walk through the analysis step-by-step.
"""

from operator import ne
import os
from insilicova.api import InSilicoVA
from interva.interva5 import InterVA5
from pyopenva.data import COUNTRIES
from pandas import read_csv, DataFrame
from pycrossva.transform import transform
from PyQt5.QtWidgets import (QComboBox, QFileDialog, QGroupBox, QHBoxLayout,
                             QMessageBox, QLabel, QProgressBar, QPushButton,
                             QSpinBox, QStackedLayout, QVBoxLayout, QWidget)
from pyopenva.output import PlotDialog, TableDialog, save_plot


class Efficient(QWidget):

    def __init__(self):
        super().__init__()
        #self.setGeometry(400, 400, 500, 400)
        self.data_page = QWidget()
        self.data = None
        self.data_loaded = False
        self.data_id_col = None
        self.pycrossva_data = None
        self.data_ui()
        self.insilicova_results = None
        self.select_algorithm_page = QWidget()
        self.select_algorithm_ui()
        self.chosen_algorithm = "insilicova"
        self.insilicova_page = QWidget()
        self.insilicova_n_sim: int = 4000
        self.insilicova_auto: str = "True"
        self.insilicova_seed: int = 1
        self.insilicova_pbar = QProgressBar()
        self.label_insilicova_progress = QLabel("(no results)")
        self.insilicova_ui()
        self.interva_results = None
        self.interva_page = QWidget()
        self.interva_hiv = "low"
        self.interva_malaria = "low"
        self.interva_pbar = QProgressBar()
        self.label_interva_progress = QLabel("(no results)")
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
        self.n_top_causes = 5
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

        load_groupbox = QGroupBox("Load Data")
        load_vbox = QVBoxLayout()
        label_data_info = QLabel("Select the file with VA data from an ODK export")
        self.btn_load_data = QPushButton("Load Data (.csv)")
        self.btn_load_data.setMaximumWidth(350)
        self.btn_load_data.clicked.connect(self.load_data)
        self.label_data = QLabel("(no data loaded)")
        label_data_id_col = QLabel("Select ID column in data")
        self.combo_data_id_col = QComboBox()
        self.combo_data_id_col.currentTextChanged.connect(
            self.set_data_id_col)
        self.combo_data_id_col.setMaximumWidth(350)
        # load_vbox.insertSpacing(0, 20)
        load_vbox.addWidget(label_data_info)
        load_vbox.addWidget(self.btn_load_data)
        load_vbox.addWidget(self.label_data)
        load_vbox.insertSpacing(3, 50)
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
        self.btn_data_format.addItems(("WHO 2016 (v151)",
                                       "WHO 2012",
                                       "PHMRC"))
        self.btn_data_format.setMaximumWidth(350)
        form_vbox.addWidget(label_data_format)
        form_vbox.addWidget(self.btn_data_format)
        # load_vbox.insertSpacing(2, 50)
        form_groupbox.setLayout(form_vbox)

        # self.btn_run_pycrossva = QPushButton("Run pyCrossVA")
        # self.btn_run_pycrossva.clicked.connect(self.run_pycrossva)
        # self.label_run_pycrossva = QLabel('(no data loaded)')
        # self.btn_data_check = QPushButton("Data Check")
        h_box_btns = QHBoxLayout()
        self.btn_go_to_mode = QPushButton("Back")
        self.btn_algorithm = QPushButton("Next")
        h_box_btns.addWidget(self.btn_go_to_mode)
        h_box_btns.addWidget(self.btn_algorithm)
        # self.btn_algorithm.pressed.connect(self.show_select_algorithm_page)

        # layout.addWidget(self.btn_load_data)
        # layout.addWidget(self.label_data)
        # layout.addStretch(2)
        # layout.addWidget(label_data_format)
        # layout.addWidget(self.btn_data_format)
        # layout.addStretch(2)
        # layout.addWidget(self.btn_run_pycrossva)
        # layout.addWidget(self.label_run_pycrossva)
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
        # self.btn_insilicova.pressed.connect(self.show_insilicova_page)
        self.btn_insilicova.pressed.connect(
            lambda: self.set_chosen_algorithm("insilicova"))
        self.btn_interva = QPushButton("InterVA")
        # self.btn_interva.pressed.connect(self.show_interva_page)
        self.btn_interva.pressed.connect(
            lambda: self.set_chosen_algorithm("interva"))
        self.btn_smartva = QPushButton("SmartVA")
        # self.btn_smartva.pressed.connect(self.show_smartva_page)
        self.btn_smartva.pressed.connect(
            lambda: self.set_chosen_algorithm("smartva"))
        self.btn_go_to_data_page = QPushButton("Back")
        # self.btn_go_to_data_page.pressed.connect(self.show_data_page)
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
        spinbox_n_iter = QSpinBox()
        spinbox_n_iter.setRange(400, 8000)
        spinbox_n_iter.setPrefix("Number of Iterations: ")
        spinbox_n_iter.setValue(self.insilicova_n_sim)
        spinbox_n_iter.valueChanged.connect(self.set_insilicova_n_sim)
        spinbox_n_iter.setMaximumWidth(150)
        label_auto_length = QLabel("Automatically increase chain length")
        option_set = ["True", "False"]
        self.insilicova_combo_auto = QComboBox()
        self.insilicova_combo_auto.addItems(option_set)
        self.insilicova_combo_auto.setCurrentIndex(
            option_set.index(self.insilicova_auto))
        self.insilicova_combo_auto.currentTextChanged.connect(
            self.set_insilicova_auto)
        spinbox_seed = QSpinBox()
        spinbox_seed.setRange(1, 10000)
        spinbox_seed.setPrefix("Set Seed: ")
        spinbox_seed.setValue(self.insilicova_seed)
        spinbox_seed.valueChanged.connect(self.set_insilicova_seed)
        spinbox_seed.setMaximumWidth(250)
        self.btn_insilicova_run = QPushButton("Run InSilicoVA")
        self.btn_insilicova_run.clicked.connect(self.run_insilicova)

        self.btn_insilicova_to_select_algorithm = QPushButton("Back")
        # self.btn_go_to_select_algorithm_page = QPushButton("Back")
        # self.btn_go_to_select_algorithm_page.pressed.connect(
        #     self.show_select_algorithm_page)
        self.btn_go_to_results_page = QPushButton("Show Results")
        self.btn_go_to_results_page.pressed.connect(
            self.show_results_page)

        layout.addWidget(spinbox_n_iter)
        layout.addWidget(label_auto_length)
        layout.addWidget(self.insilicova_combo_auto)
        layout.addWidget(spinbox_seed)
        layout.addWidget(self.btn_insilicova_run)
        layout.addWidget(self.insilicova_pbar)
        layout.addWidget(self.label_insilicova_progress)
        layout.addStretch(1)
        h_box = QHBoxLayout()
        h_box.addWidget(self.btn_insilicova_to_select_algorithm)
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
        self.btn_interva_run.clicked.connect(self.run_interva)
        self.btn_interva_to_select_algorithm = QPushButton("Back")
        # self.btn_go_to_select_algorithm_page.clicked.connect(
        #     self.show_select_algorithm_page)
        self.btn_go_to_results_page = QPushButton("Show Results")
        self.btn_go_to_results_page.clicked.connect(
            self.show_results_page)

        layout.addWidget(label_hiv)
        layout.addWidget(self.interva_combo_hiv)
        layout.addWidget(label_malaria)
        layout.addWidget(self.interva_combo_malaria)
        layout.addWidget(self.btn_interva_run)
        layout.addWidget(self.interva_pbar)
        layout.addWidget(self.label_interva_progress)
        layout.addStretch(1)
        h_box = QHBoxLayout()
        h_box.addWidget(self.btn_interva_to_select_algorithm)
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
        self.btn_smartva_to_select_algorithm = QPushButton("Back")
        # self.btn_go_to_select_algorithm_page.pressed.connect(
        #     self.show_select_algorithm_page)
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
        h_box.addWidget(self.btn_smartva_to_select_algorithm)
        h_box.addWidget(self.btn_go_to_results_page)
        layout.addLayout(h_box)
        self.smartva_page.setLayout(layout)

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
        self.btn_download_table.clicked.connect(self.download_interva_table)
        self.btn_download_plot = QPushButton("Download Plot")
        self.btn_download_plot.clicked.connect(self.download_interva_plot)
        self.btn_download_individual_results = QPushButton(
            "Download \n Individual Cause Assignments")
        self.btn_download_individual_results.clicked.connect(
            self.download_interva_indiv
        )
        hbox_download.addWidget(self.btn_download_table)
        hbox_download.addWidget(self.btn_download_plot)
        vbox_download.addLayout(hbox_download)
        vbox_download.addWidget(self.btn_download_individual_results)
        gbox_download.setLayout(vbox_download)

        # vbox_table = QVBoxLayout()
        # self.btn_show_table = QPushButton("Show CSMF table")
        # self.btn_show_table.pressed.connect(self.run_table_dialog)
        # self.btn_download_table = QPushButton("Download Table")
        # self.btn_download_table.clicked.connect(self.download_interva_table)
        # vbox_table.addWidget(self.btn_show_table)
        # vbox_table.addWidget(self.btn_download_table)
        #
        # vbox_plot = QVBoxLayout()
        # self.btn_show_plot = QPushButton("Show CSMF plot")
        # self.btn_show_plot.pressed.connect(self.run_plot_dialog)
        # self.btn_download_plot = QPushButton("Download Plot")
        # self.btn_download_plot.clicked.connect(self.download_interva_plot)
        # vbox_plot.addWidget(self.btn_show_plot)
        # vbox_plot.addWidget(self.btn_download_plot)
        #
        # hbox = QHBoxLayout()
        # hbox.addLayout(vbox_table)
        # hbox.addLayout(vbox_plot)
        #
        # layout.addLayout(hbox)
        # self.btn_download_individual_results = QPushButton(
        #     "Download Individual Cause Assignments")
        # self.btn_download_individual_results.clicked.connect(
        #     self.download_interva_indiv
        # )

        #self.spinbox_n_causes.textChanged(self.set_n_top_causes_text)
        self.btn_results_to_algorithm = QPushButton("Back")
        # self.btn_go_to_algorithm_page.pressed.connect(
        #     self.show_algorithm_page)

        # layout.addWidget(self.btn_download_individual_results)
        # layout.addWidget(self.spinbox_n_causes)
        # layout.addStretch(1)
        layout.addWidget(gbox_top_causes)
        layout.addStretch(1)
        layout.addWidget(gbox_show)
        layout.addStretch(1)
        layout.addWidget(gbox_download)
        layout.addStretch(1)
        layout.addWidget(self.btn_results_to_algorithm)
        self.results_page.setLayout(layout)

    def load_data(self):
        path = QFileDialog.getOpenFileName(self,
                                           "Open a CSV file",
                                           "",
                                           "All Files(*.*)")
        if path != ("", ""):
            self.data = read_csv(path[0])
            n_records = self.data.shape[0]
            self.label_data.setText(f'Data loaded: {n_records} deaths')
            self.data_loaded = True
            self.combo_data_id_col.addItems(
                ["no ID column"] + list(self.data)
            )
            self.combo_data_id_col.setCurrentIndex(0)

    def set_data_id_col(self, id_col):
        self.data_id_col = id_col
        if self.data_id_col != "no ID column":
            if self.data[self.data_id_col].nunique() != self.data.shape[0]:
                alert = QMessageBox()
                alert.setIcon(QMessageBox.Warning)
                alert.setText(
                    "ID column does not have a unique value for every row")
                alert.exec()

    def run_pycrossva(self):
        if not self.data_loaded:
            alert = QMessageBox()
            alert.setText("Please load data before running pyCrossVA.")
            alert.exec()
        else:
            raw_data_col_id = self.data_id_col
            if self.data_id_col == "no ID column":
                raw_data_col_id = None
            self.pycrossva_data = transform(
                mapping=("2016WHOv151", "InterVA5"),
                raw_data=self.data,
                raw_data_id=raw_data_col_id)
            # self.label_run_pycrossva.setText("data are ready to go!")

    def set_insilicova_n_sim(self, n_sim: int):
        self.insilicova_n_sim = n_sim

    def set_insilicova_auto(self, auto: str):
        self.insilicova_auto = auto

    def set_insilicova_seed(self, seed: int):
        self.insilicova_seed = seed

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

    def set_n_top_causes(self, n):
        self.n_top_causes = n

    # TODO: need to clean these up (window management handled in main
    def show_data_page(self):
        self.stacked_layout.setCurrentIndex(0)

    def show_algorithm_page(self):
        if self.chosen_algorithm == "insilicova":
            self.show_insilicova_page()
        elif self.chosen_algorithm == "interva":
            self.show_interva_page()
        else:
            self.show_smartva_page()

    def show_select_algorithm_page(self):
        self.stacked_layout.setCurrentIndex(1)

    def show_insilicova_page(self):
        self.stacked_layout.setCurrentIndex(2)

    def show_interva_page(self):
        self.stacked_layout.setCurrentIndex(3)

    def show_smartva_page(self):
        self.stacked_layout.setCurrentIndex(4)

    def show_results_page(self):
        self.stacked_layout.setCurrentIndex(5)

    def run_insilicova(self):
        if self.data_loaded is None:
            alert = QMessageBox()
            alert.setText(
                # "Data need to be loaded and/or prepared with pyCrossVA.")
                "Data need to be loaded.")
            alert.exec()
        else:
            self.run_pycrossva()
            auto_extend = False
            # # the following msg is updated by InSilicoVA
            # msg = "Running InSilicoVA"
            if self.insilicova_auto == "True":
                auto_extend = True
            #     msg = "Running InSilicoVA: progress bar may reset several times (auto increase is True)"
            # self.label_insilicova_progress.setText(msg)
            burnin = max(int(self.insilicova_n_sim/2), 1)
            thin = 10
            insilico_out = InSilicoVA(self.pycrossva_data,
                                      data_type="WHO2016",
                                      n_sim=self.insilicova_n_sim,
                                      thin=thin,
                                      burnin=burnin,
                                      auto_length=auto_extend,
                                      seed=self.insilicova_seed,
                                      openva_app=self)
            self.insilicova_results = insilico_out.get_results()
            self.label_insilicova_progress.setText("InSilicoVA results are ready")

    def run_interva(self):
        if self.data_loaded is None:
            alert = QMessageBox()
            alert.setText(
                # "Data need to be loaded and/or prepared with pyCrossVA.")
                "Data need to be loaded.")
            alert.exec()
        else:
            self.run_pycrossva()
            iv5out = InterVA5(self.pycrossva_data,
                              hiv=self.interva_hiv[0],
                              malaria=self.interva_malaria[0],
                              write=False,
                              openva_app=self)
            iv5out.run()
            self.interva_results = iv5out
            self.label_interva_progress.setText("InterVA5 results are ready")

    def run_plot_dialog(self):
        if self.chosen_algorithm == "insilicova":
            results = self.insilicova_results
        else:
            results = self.interva_results
        if results is None:
            alert = QMessageBox()
            alert.setText(
                "Need to run VA algorithm first.")
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
            alert.setText(
                "Need to run VA algorithm first.")
            alert.exec()
        else:
            self.table_dialog = TableDialog(results,
                                            self,
                                            top=self.n_top_causes)
            self.table_dialog.resize(self.table_dialog.table.width(),
                                     self.table_dialog.table.height())
            self.table_dialog.exec()

    def download_interva_table(self):
        if self.chosen_algorithm == "insilicova":
            results = self.insilicova_results
        else:
            results = self.interva_results
        if results is None:
            alert = QMessageBox()
            alert.setText(
                "Need to run VA algorithm first.")
            alert.exec()
        else:
            results_file_name = f"{self.chosen_algorithm}_csmf.csv"
            path = QFileDialog.getSaveFileName(self,
                                               "Save CSMF (csv)",
                                               results_file_name,
                                               "CSV Files (*.csv)")
            if path != ("", ""):
                #os.remove(path[0])
                with open(path[0], "a", newline="") as f:
                    n_top_causes = self.n_top_causes
                    csmf = results.get_csmf(top=n_top_causes)
                    if isinstance(csmf, DataFrame):
                        csmf_df = csmf.sort_values(by="Mean", ascending=False).copy()
                        csmf_df = csmf_df.reset_index()
                        csmf_df.rename(columns={"index": "Cause", "Mean": "CSMF (Mean)"},
                                       inplace=True)
                    else:
                        csmf.sort_values(ascending=False, inplace=True)
                        csmf_df = csmf.reset_index()[0:n_top_causes]
                        csmf_df.rename(columns={"index": "Cause", 0: "CSMF"},
                                       inplace=True)
                    # csmf_df.round(4).to_csv(f, index=False)
                    csmf_df.to_csv(f, index=False)
                if os.path.isfile(path[0]):
                    alert = QMessageBox()
                    alert.setText("results saved to" + path[0])
                    alert.exec()

    def download_interva_plot(self):
        if self.chosen_algorithm == "insilicova":
            results = self.insilicova_results
        else:
            results = self.interva_results
        if results is None:
            alert = QMessageBox()
            alert.setText(
                "Need to run VA algorithm first.")
            alert.exec()
        else:
            results_file_name = f"{self.chosen_algorithm}_csmf.pdf"
            path = QFileDialog.getSaveFileName(self,
                                               "Save CSMF plot (pdf)",
                                               results_file_name,
                                               "PDF Files (*.pdf)")
            if path != ("", ""):
                #os.remove(path[0])
                save_plot(results=results,
                          algorithm=self.chosen_algorithm,
                          top=self.n_top_causes,
                          file_name=path[0])
                if os.path.isfile(path[0]):
                    alert = QMessageBox()
                    alert.setText("results saved to" + path[0])
                    alert.exec()

    def download_interva_indiv(self):
        if self.chosen_algorithm == "insilicova":
            results = self.insilicova_results
        else:
            results = self.interva_results
        if results is None:
            alert = QMessageBox()
            alert.setText(
                "Need to run VA algorithm first.")
            alert.exec()
        else:
            results_file_name = f"{self.chosen_algorithm}_individual_cod.csv"
            path = QFileDialog.getSaveFileName(self,
                                               "Save CSMF (csv)",
                                               results_file_name,
                                               "CSV Files (*.csv)")
            if path != ("", ""):
                with open(path[0], "a", newline="") as f:
                    if self.chosen_algorithm == "insilicova":
                        results.indiv_prob.to_csv(f)
                    else:
                        out = results.out["VA5"]
                        out.drop("WHOLEPROB", axis=1, inplace=True)
                        out.to_csv(f, index=False)
                if os.path.isfile(path[0]):
                    alert = QMessageBox()
                    alert.setText("results saved to" + path[0])
                    alert.exec()
