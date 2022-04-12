# -*- coding: utf-8 -*-

"""
pyopenva.command_center
~~~~~~~~~~~~~~
This module creates the window for loading data and setting algorithm options.
"""

from insilico import InSilicoDialog
from PyQt5.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QGroupBox,
                             QLabel, QPushButton, QComboBox, QFileDialog)

import csv

from edit_window import EditData
from load import LoadData

class CommandCenter(QWidget):

    def __init__(self):
        super().__init__()
        self.raw_data = None
        self.raw_data_loaded = False
        self.insilico_dialog = None

        self.setGeometry(400, 400, 700, 600)
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
        self.data_panel = QGroupBox("Data")
        self.data_panel.setLayout(data_panel_v_box)
        self.btn_load_data.clicked.connect(self.load_data)
        self.btn_edit_data.clicked.connect(self.create_edit_window)

    def load_data(self):
        """Set up window for loading csv data."""
        
        self.load_window = LoadData()
        
    def create_edit_window(self):
        """Set up window for editing provided csv data."""
        
        self.edit_window = EditData(self.load_window.data)
        self.edit_window.table.resizeColumnsToContents()
        self.btn_save = QPushButton("Save Data", self.edit_window)
        self.btn_cancel = QPushButton("Cancel", self.edit_window)
    
        edit_panel_v_box = QVBoxLayout()
        edit_panel_v_box.addWidget(self.btn_save)
        edit_panel_v_box.addWidget(self.btn_cancel)
        edit_panel_v_box.addWidget(self.edit_window)
        self.edit_panel = QGroupBox("Edit")
        self.edit_panel.setLayout(edit_panel_v_box)
        self.edit_panel.setWindowTitle("openVA GUI: Edit Data")
        self.edit_panel.setGeometry(400, 400, 700, 600)
        self.edit_panel.show()
        
        self.btn_save.clicked.connect(self.save_data)
        self.btn_cancel.clicked.connect(self.cancel_data)
       
    def save_data(self):
        """Set up window for saving data: replacing the provided csv file or saving the edited file to a new csv file."""

        updated_data = self.edit_window.model.data
        file_name = QFileDialog.getSaveFileName(self,"Save As", "","csv Files (*.csv)")
        fname = file_name[0]
        with open(fname, 'w', newline = '') as output_file:
            csvwriter = csv.writer(output_file) 
            for row in updated_data:
                csvwriter.writerow(row)
        self.edit_panel.close()
    
    def cancel_data(self):
        """Cancels any edit changes made to the data model."""
                
        header = []
        rows = []
        data = []
        with open(self.load_window.fname, 'r', newline = '') as file:
            csvreader = csv.reader(file)
            header.append(next(csvreader))
            for row in csvreader:
                rows.append(row)
            data += header + rows
        self.load_window.data = data
        self.edit_window = EditData(self.load_window.data)
        self.edit_panel.close()

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
        #self.btn_interva_options.clicked.connect(self.run_interva_dialog)
        #self.btn_smartva_options.clicked.connect(self.run_smartva_dialog)

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
        self.insilico_dialog = InSilicoDialog()
        self.insilico_dialog.exec()
