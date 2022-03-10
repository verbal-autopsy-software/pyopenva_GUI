# -*- coding: utf-8 -*-

"""
pyopenva.command_center
~~~~~~~~~~~~~~
This module creates the window for loading data and setting algorithm options.
"""

from PyQt5.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QGroupBox,
                             QCheckBox, QLabel, QPushButton, QComboBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPixmap, QIcon
import sys
import os
from itertools import product


class CommandCenter(QWidget):

    def __init__(self):
        super().__init__()
        self.raw_data = None
        self.raw_data_loaded = False

        self.setGeometry(400, 400, 500, 400)
        self.setWindowTitle("openVA GUI: Command Center")
        self.data_algorithm_h_box = QHBoxLayout()
        self.create_data_panel()
        self.create_algorithm_panel()
        self.data_algorithm_h_box.addWidget(self.data_panel)
        self.data_algorithm_h_box.addWidget(self.algorithm_panel)
        self.setLayout(self.data_algorithm_h_box)

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
        self.data_panel = QGroupBox("DATA")
        self.data_panel.setLayout(data_panel_v_box)

    def create_algorithm_panel(self):
        """Set up (right) panel for choosing VA algorithms."""

        algorithm_panel_v_box = QVBoxLayout()
        self.btn_insilico = QCheckBox("InSilico")
        label_insilico_progress = QLabel("InSilico Progress Bar goes here")
        self.btn_interva = QCheckBox("InterVA")
        label_interva_progress = QLabel("InterVA Progress Bar goes here")
        self.btn_smartva = QCheckBox("SmartVA")
        label_smartva_progress = QLabel("SmartVA Progress Bar goes here")
        self.btn_algorithm_run = QPushButton("Run")
        self.btn_algorithm_results = QPushButton("Results")
        algorithm_panel_v_box.addWidget(self.btn_insilico)
        algorithm_panel_v_box.addWidget(label_insilico_progress)
        algorithm_panel_v_box.addWidget(self.btn_interva)
        algorithm_panel_v_box.addWidget(label_interva_progress)
        algorithm_panel_v_box.addWidget(self.btn_smartva)
        algorithm_panel_v_box.addWidget(label_smartva_progress)
        algorithm_panel_v_box.addWidget(self.btn_algorithm_run)
        algorithm_panel_v_box.addWidget(self.btn_algorithm_results)

        self.algorithm_panel = QGroupBox("algorithm")
        self.algorithm_panel.setLayout(algorithm_panel_v_box)
