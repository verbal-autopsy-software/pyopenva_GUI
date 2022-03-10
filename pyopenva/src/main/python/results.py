# -*- coding: utf-8 -*-

"""
pyopenva.results
~~~~~~~~~~~~~~
This module creates the window for displaying and downloading results.
"""

from PyQt5.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QGroupBox,
                             QPushButton)

class Results(QWidget):

    def __init__(self):
        super().__init__()

        self.setGeometry(400, 400, 500, 400)
        self.setWindowTitle("openVA GUI: Results")
        self.results_v_box = QVBoxLayout()
        self.create_insilico_panel()
        self.create_interva_panel()
        self.create_smartva_panel()
        self.results_v_box.addWidget(self.insilico_panel)
        self.results_v_box.addWidget(self.interva_panel)
        self.results_v_box.addWidget(self.smartva_panel)
        self.btn_go_to_mode = QPushButton("Go Back to User Mode Selection")
        self.btn_go_to_command_center = QPushButton("Go Back to the Command Center")
        self.results_v_box.addWidget(self.btn_go_to_mode)
        self.results_v_box.addWidget(self.btn_go_to_command_center)
        self.setLayout(self.results_v_box)

    def create_insilico_panel(self):
        insilico_h_box = QHBoxLayout()
        self.btn_insilico_report = QPushButton("Report")
        self.btn_insilico_plots = QPushButton("Plots")
        insilico_h_box.addWidget(self.btn_insilico_report)
        insilico_h_box.addWidget(self.btn_insilico_plots)
        self.insilico_panel = QGroupBox("InSilicoVA")
        self.insilico_panel.setLayout(insilico_h_box)

    def create_interva_panel(self):
        interva_h_box = QHBoxLayout()
        self.btn_interva_report = QPushButton("Report")
        self.btn_interva_plots = QPushButton("Plots")
        interva_h_box.addWidget(self.btn_interva_report)
        interva_h_box.addWidget(self.btn_interva_plots)
        self.interva_panel = QGroupBox("InterVA")
        self.interva_panel.setLayout(interva_h_box)

    def create_smartva_panel(self):
        smartva_h_box = QHBoxLayout()
        self.btn_smartva_report = QPushButton("Report")
        self.btn_smartva_plots = QPushButton("Plots")
        smartva_h_box.addWidget(self.btn_smartva_report)
        smartva_h_box.addWidget(self.btn_smartva_plots)
        self.smartva_panel = QGroupBox("SmartVA")
        self.smartva_panel.setLayout(smartva_h_box)

