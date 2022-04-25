# -*- coding: utf-8 -*-

"""
pyopenva.command_center
~~~~~~~~~~~~~~
This module creates the window for loading data and setting algorithm options.
"""

from insilico import InSilicoDialog
from interva import InterVADialog
from smartva import SmartVADialog
from PyQt5.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QGroupBox,
                             QLabel, QPushButton, QComboBox)
from numpy.random import default_rng


class CommandCenter(QWidget):

    def __init__(self):
        super().__init__()
        self.raw_data = None
        self.raw_data_loaded = False
        self.insilico_dialog = None
        self.interva_dialog = None

        self.setGeometry(400, 400, 700, 600)
        self.setWindowTitle("openVA GUI: Command Center")
        self.data_algorithm_h_box = QHBoxLayout()
        self.create_data_panel()
        self.create_algorithm_panel()
        self.data_algorithm_h_box.addWidget(self.data_panel)
        self.data_algorithm_h_box.addWidget(self.algorithm_panel)
        self.setLayout(self.data_algorithm_h_box)

        # initialize InSilico parameters
        self.n_iterations = 3000
        self.jump_scale = 0.1
        self.auto_extend = True
        self.seed = 653

        # initialize InterVA parameters
        self.hiv = "low"
        self.malaria = "low"

        # initialize SmartVA parameters
        self.smartva_country = "Unknown"
        self.smartva_hiv = "False"
        self.smartva_malaria = "False"
        self.smartva_hce = "True"
        self.smartva_freetext = "True"

    def create_data_panel(self):
        """Set up data panel for loading, editing, and checking the data."""

        data_panel_v_box = QVBoxLayout()
        self.btn_load_data = QPushButton("Load Data (.csv)")
        label_data_format = QLabel("Data Format:")
        self.btn_data_format = QComboBox()
        self.btn_data_format.addItems(("WHO 2016 (v151)",
                                       "WHO 2012",
                                       "PHMRC"))
        self.btn_data_check = QPushButton("Data Check")
        self.btn_edit_data = QPushButton("Edit Check")
        self.btn_user_mode = QPushButton("Go Back to User Mode Selection")
        data_panel_v_box.addWidget(self.btn_load_data)
        data_panel_v_box.addWidget(label_data_format)
        data_panel_v_box.addWidget(self.btn_data_format)
        data_panel_v_box.addWidget(self.btn_data_check)
        data_panel_v_box.addWidget(self.btn_edit_data)
        data_panel_v_box.addStretch(2)
        data_panel_v_box.addWidget(self.btn_user_mode)
        self.data_panel = QGroupBox("Data")
        self.data_panel.setLayout(data_panel_v_box)

    def create_algorithm_panel(self):
        """Set up (right) panel for choosing VA algorithms."""

        algorithm_panel_v_box = QVBoxLayout()

        self.create_insilico_box()
        self.create_interva_box()
        self.create_smartva_box()
        self.btn_algorithm_results = QPushButton("Results")

        algorithm_panel_v_box.addWidget(self.insilico_box)
        algorithm_panel_v_box.addStretch(1)
        algorithm_panel_v_box.addLayout(self.interva_box)
        algorithm_panel_v_box.addStretch(1)
        algorithm_panel_v_box.addLayout(self.smartva_box)
        algorithm_panel_v_box.addStretch(1)
        algorithm_panel_v_box.addWidget(self.btn_algorithm_results)
        self.algorithm_panel = QGroupBox("Algorithms")
        self.algorithm_panel.setLayout(algorithm_panel_v_box)
        self.btn_insilico_options.clicked.connect(self.run_insilico_dialog)
        self.btn_interva_options.clicked.connect(self.run_interva_dialog)
        self.btn_smartva_options.clicked.connect(self.run_smartva_dialog)
        self.btn_insilico_run.clicked.connect(self.print_insilico)
        self.btn_interva_run.clicked.connect(self.print_interva)
        self.btn_smartva_run.clicked.connect(self.print_smartva)
        # self.btn_interva_options.clicked.connect(self.run_interva_dialog)
        # self.btn_smartva_options.clicked.connect(self.run_smartva_dialog)

    def create_insilico_box(self):
        """Set up box of widgets for InSilicoVA."""

        self.insilico_box = QGroupBox("InSilicoVA")
        insilico_vbox = QVBoxLayout()
        insilico_hbox = QHBoxLayout()
        self.btn_insilico_options = QPushButton("Set Options")
        self.btn_insilico_run = QPushButton("Run Algorithm")
        insilico_hbox.addWidget(self.btn_insilico_options)
        insilico_hbox.addWidget(self.btn_insilico_run)
        label_insilico_progress = QLabel("InSilico Progress Bar goes here")
        insilico_vbox.addLayout(insilico_hbox)
        insilico_vbox.addWidget(label_insilico_progress)
        self.insilico_box.setLayout(insilico_vbox)

    def create_interva_box(self):
        """Set up box of widgets for InterVA."""

        self.interva_box = QVBoxLayout()
        interva_label = QLabel("InterVA")
        interva_hbox = QHBoxLayout()
        self.btn_interva_options = QPushButton("Set Options")
        self.btn_interva_run = QPushButton("Run Algorithm")
        interva_hbox.addWidget(self.btn_interva_options)
        interva_hbox.addWidget(self.btn_interva_run)
        label_interva_progress = QLabel("InterVA Progress Bar goes here")
        self.interva_box.addWidget(interva_label)
        self.interva_box.addLayout(interva_hbox)
        self.interva_box.addWidget(label_interva_progress)

    def create_smartva_box(self):
        """Set up box of widgets for SmartVA."""

        self.smartva_box = QVBoxLayout()
        smartva_label = QLabel("SmartVA")
        smartva_hbox_2 = QHBoxLayout()
        self.btn_smartva_options = QPushButton("Set Options")
        self.btn_smartva_run = QPushButton("Run Algorithm")
        smartva_hbox_2.addWidget(self.btn_smartva_options)
        smartva_hbox_2.addWidget(self.btn_smartva_run)
        label_smartva_progress = QLabel("SmartVA Progress Bar goes here")
        self.smartva_box.addWidget(smartva_label)
        self.smartva_box.addLayout(smartva_hbox_2)
        self.smartva_box.addWidget(label_smartva_progress)

    def run_insilico_dialog(self):
        self.insilico_dialog = InSilicoDialog(self,
                                              self.seed,
                                              self.auto_extend,
                                              self.jump_scale,
                                              self.n_iterations)
        self.insilico_dialog.exec()

    def update_insilico_n_iterations(self, updated_n_iterations):
        self.n_iterations = updated_n_iterations

    def update_insilico_jump_scale(self, updated_jump_scale):
        self.jump_scale = updated_jump_scale

    def update_insilico_auto_extend(self, updated_auto_extend):
            self.auto_extend = updated_auto_extend

    def update_insilico_seed(self, updated_seed):
        self.seed = updated_seed

    def run_insilico(self):
        rng = default_rng(self.seed)
        # pass rng to the insilico function to make results reproducible
        pass

    def run_interva_dialog(self):
        self.interva_dialog = InterVADialog(self, self.hiv, self.malaria)
        self.interva_dialog.exec()

    def update_interva_hiv(self, updated_hiv):
        self.hiv = updated_hiv

    def update_interva_malaria(self, updated_malaria):
        self.malaria = updated_malaria

    def run_smartva_dialog(self):
        self.smartva_dialog = SmartVADialog(self,
                                            self.smartva_country,
                                            self.smartva_hiv,
                                            self.smartva_malaria,
                                            self.smartva_hce,
                                            self.smartva_freetext)
        self.smartva_dialog.exec()

    def update_smartva_country(self, updated_country):
        self.smartva_country = updated_country

    def update_smartva_hiv(self, updated_hiv):
        self.smartva_hiv = updated_hiv

    def update_smartva_malaria(self, updated_malaria):
        self.smartva_malaria = updated_malaria

    def update_smartva_hce(self, updated_hce):
        self.smartva_hce = updated_hce

    def update_smartva_freetext(self, updated_freetext):
        self.smartva_freetext = updated_freetext

    def print_insilico(self):
        print(self.n_iterations)
        print(self.auto_extend)
        print(self.jump_scale)
        print(self.seed)

    def print_interva(self):
        print(self.hiv)
        print(self.malaria)

    def print_smartva(self):
        print(self.smartva_country)
        print(self.smartva_hiv)
        print(self.smartva_malaria)
        print(self.smartva_hce)
        print(self.smartva_freetext)
