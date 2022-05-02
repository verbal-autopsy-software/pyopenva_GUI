# -*- coding: utf-8 -*-

"""
pyopenva.efficient
~~~~~~~~~~~~~~
This module creates a stacked layout to walk through the analysis step-by-step.
"""

from PyQt5.QtWidgets import (QComboBox, QHBoxLayout, QLabel, QPushButton,
                             QStackedLayout, QVBoxLayout, QWidget)


class Efficient(QWidget):

    def __init__(self):
        super().__init__()
        self.setGeometry(400, 400, 500, 400)
        self.setWindowTitle("Efficient Mode: Data")
        self.data_page = QWidget()
        self.data_ui()
        self.select_algorithm_page = QWidget()
        self.algorithm_ui()
        self.insilico_page = QWidget()
        self.interva_page = QWidget()
        self.smartva_page = QWidget()
        self.results_page = QWidget()
        self.stacked_layout = QStackedLayout()
        self.stacked_layout.addWidget(self.data_page)
        self.stacked_layout.addWidget(self.select_algorithm_page)
        self.stacked_layout.addWidget(self.insilico_page)
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
        layout.addStretch(2)
        layout.addWidget(label_data_format)
        layout.addWidget(self.btn_data_format)
        layout.addStretch(2)
        layout.addLayout(h_box)
        self.data_page.setLayout(layout)

    def algorithm_ui(self):
        layout = QVBoxLayout()
        label_select_algorithm = QLabel("Select which algorithm to use:")
        self.btn_efficient_insilico = QPushButton("Use InSilicoVA")
        self.btn_efficient_interva = QPushButton("Use InterVA")
        self.btn_efficient_smartva = QPushButton("Use SmartVA")
        self.btn_go_to_data_page = QPushButton("Back")
        self.btn_go_to_data_page.pressed.connect(self.show_data_page)
        layout.addWidget(label_select_algorithm)
        layout.addWidget(self.btn_efficient_insilico)
        layout.addStretch(1)
        layout.addWidget(self.btn_efficient_interva)
        layout.addStretch(1)
        layout.addWidget(self.btn_efficient_smartva)
        layout.addStretch(1)
        layout.addWidget(self.btn_go_to_data_page)

        self.select_algorithm_page.setLayout(layout)

    def show_select_algorithm_page(self):
        self.stacked_layout.setCurrentIndex(1)
        self.setWindowTitle("Efficient Mode: Select Algorithm")

    def show_data_page(self):
        self.stacked_layout.setCurrentIndex(0)
        self.setWindowTitle("Efficient Mode: Data")
