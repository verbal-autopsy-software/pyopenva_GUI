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
                             QLabel, QPushButton, QComboBox, QFileDialog, 
                             QMessageBox, QLineEdit, QInputDialog)
from PyQt5.QtCore import Qt, QDate, QTime

import csv

from edit_window import EditData
from load import LoadData

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
        self.btn_load_data.clicked.connect(self.load_data)
        self.btn_edit_data.clicked.connect(self.create_edit_window)

    def load_data(self):
        """Set up window for loading csv data."""
        
        self.load_window = LoadData()
        
    def create_edit_window(self):
        """Set up window for editing provided csv data or show error if data is N/A."""
        
        try:
            self.edit_window = EditData(self.load_window.data)
            self.search_results = []
            self.search_results_counter = -1
            self.search_index = -1
            self.edit_window.table.resizeColumnsToContents()
            
            edit_panel_h_box_1 = QHBoxLayout()
            self.btn_save = QPushButton("Save Data")
            self.btn_cancel = QPushButton("Cancel")
            edit_panel_h_box_1.addWidget(self.btn_save)
            edit_panel_h_box_1.addWidget(self.btn_cancel)
            
            edit_panel_h_box_2 = QHBoxLayout()
            self.search_bar = QLineEdit()
            self.search_bar.setPlaceholderText("Search for Column Name")
            self.search_results_counter = QLabel(str(self.search_results_counter + 1) + "/" + str(len(self.search_results)))
            edit_panel_h_box_2.addWidget(self.search_bar)
            edit_panel_h_box_2.addWidget(self.search_results_counter)
            edit_panel_h_box_3 = QHBoxLayout()
            self.btn_previous =  QPushButton("Previous")
            self.btn_next =  QPushButton("Next")
            self.btn_close_find =  QPushButton("Clear Search")
            edit_panel_h_box_3.addWidget(self.btn_previous)
            edit_panel_h_box_3.addWidget(self.btn_next)
            edit_panel_h_box_3.addWidget(self.btn_close_find)
            edit_panel_h_box_4 = QHBoxLayout()
            edit_panel_h_box_4.addLayout(edit_panel_h_box_2)
            edit_panel_h_box_4.addLayout(edit_panel_h_box_3)
            
            edit_panel_h_box_5 = QHBoxLayout()
            self.sort_column = QLabel("No column selected to sort in ")
            self.sort_by = QComboBox()
            self.sort_by.addItems(("Original Order", "Ascending Order", "Descending Order"))
            self.btn_sort = QPushButton("Sort")
            edit_panel_h_box_5.addWidget(self.sort_column)
            edit_panel_h_box_5.addWidget(self.sort_by)
            edit_panel_h_box_5.addWidget(self.btn_sort)
            # self.search_bar.setStyleSheet('font-size: 14px')
            
            edit_panel_v_box = QVBoxLayout()
            edit_panel_v_box.addLayout(edit_panel_h_box_1)
            edit_panel_v_box.addLayout(edit_panel_h_box_4)
            edit_panel_v_box.addWidget(self.edit_window)
            edit_panel_v_box.addLayout(edit_panel_h_box_5)
            
            self.edit_panel = QGroupBox("")
            self.edit_panel.setLayout(edit_panel_v_box)
            self.edit_panel.setWindowTitle("openVA GUI: Edit Data")
            self.edit_panel.setGeometry(400, 400, 700, 600)
            self.edit_panel.show()
            
            self.btn_save.clicked.connect(self.save_data)
            self.btn_cancel.clicked.connect(self.cancel_data)
            self.search_bar.textChanged.connect(self.column_find)
            self.btn_previous.clicked.connect(self.prev_clicked)
            self.btn_next.clicked.connect(self.next_clicked)
            self.btn_close_find.clicked.connect(self.close_find_clicked)
            self.edit_window.table.clicked.connect(self.change_column)
            self.btn_sort.clicked.connect(self.sort_by_column)
            self.edit_window.table.selectionModel().currentChanged.connect(self.change_column)
        except:
            load_first_msg = QMessageBox().information(self, "Error finding data", "Please load a valid data file.", QMessageBox.Ok)
            
    def change_column(self):
        """Updates the display name for the column to be sorted by."""
        
        index_col = self.edit_window.table.currentIndex().column()
        name = self.edit_window.model.column_name(index_col, Qt.DisplayRole)
        self.sort_column.setText("Sort the \"" + name + "\" column in ")

    def sort_by_column(self):
        """Sorts by column of the selected cell by the selected sort order."""
        
        index_col = self.edit_window.table.currentIndex().column()
        if self.sort_by.currentText() == "Original Order":
            index_col = -1
            self.edit_window.table.sortByColumn(index_col, Qt.AscendingOrder)
        elif self.sort_by.currentText() == "Ascending Order":
            self.edit_window.table.sortByColumn(index_col, Qt.AscendingOrder)
        elif self.sort_by.currentText() == "Descending Order":
            self.edit_window.table.sortByColumn(index_col, Qt.DescendingOrder)
        
    def prev_clicked(self):
        """Goes to the previous column that matches the text search."""
        
        self.search_index -= 1
        if len(self.search_bar.text()) != 0 and len(self.search_results) > self.search_index and self.search_index >= 0:
            self.edit_window.table.selectColumn(self.search_results[self.search_index])
            self.search_results_counter.setText(str(self.search_index + 1) + "/" + str(len(self.search_results)))
        else:
            self.search_index += 1
            no_result_msg = QMessageBox()
            no_result_msg.setWindowTitle("No results")
            no_result_msg.setText("No previous search result available.")
            x = no_result_msg.exec_()
        
    def next_clicked(self):
        """Goes to the next column that matches the text search."""
        
        self.search_index += 1
        if len(self.search_bar.text()) != 0 and len(self.search_results) > self.search_index:
            self.edit_window.table.selectColumn(self.search_results[self.search_index])
            self.search_results_counter.setText(str(self.search_index + 1) + "/" + str(len(self.search_results)))
        else:
            self.search_index -= 1
            no_result_msg = QMessageBox()
            no_result_msg.setWindowTitle("No results")
            no_result_msg.setText("No next search result available.")
            x = no_result_msg.exec_()
        
    def close_find_clicked(self):
        """Clears the text search for a column."""
        
        if len(self.search_bar.text()) != 0:
            self.search_bar.setText("")
        self.search_results_counter.setText("0/0")
       
    def column_find(self):
        """Finds a specific column based off a text search."""
        
        search_bar_text = self.search_bar.text().lower()
        if len(search_bar_text) == 0:
            self.search_results_counter.setText("0/0")
        header = self.load_window.header[0]
        self.search_results = [x for x in range(len(header)) if search_bar_text in (header[x]).lower()]
        self.search_index = 0
        if len(self.search_results) > self.search_index:
            self.edit_window.table.selectColumn(self.search_results[self.search_index])
            self.search_results_counter.setText(str(self.search_index + 1) + "/" + str(len(self.search_results)))
        
    def save_data(self):
        """Set up window for saving data and prompts for user's name."""

        name = ""
        text, ok = QInputDialog.getText(self.edit_panel, 'Name Input', 'Enter your name for save file name purposes:')
        while(ok and len(text) == 0):
            load_first_msg = QMessageBox().information(self.edit_panel, "Length of text error", "Please type in your name, which must be more than 0 characters long.", QMessageBox.Ok)
            text, ok = QInputDialog.getText(self.edit_panel, 'Name Input', 'Enter your name for save file name purposes:')
        if ok and len(text) > 0:
            name += str(text).replace(" ", "-")
            date = QDate.currentDate().toString(Qt.ISODate)
            time = QTime.currentTime().toString('hh.mm.ss.zzz')
            # save file format: file-name_edited-by_name_date_time.csv
            file_name = QFileDialog.getSaveFileName(self,"Save As", self.load_window.fname[:-4] + "_edited-by_" + name + "_" + date + "_" + time,"csv Files (*.csv)")
            fname = file_name[0]
            if file_name is not None and fname != "":
                self.load_window.fname = fname
                with open(fname, 'w', newline = '') as output_file:
                    csvwriter = csv.writer(output_file) 
                    for row in self.edit_window.model.data:
                        csvwriter.writerow(row)
                    self.edit_panel.close()
            else:
                self.edit_panel.close()
                self.edit_panel.show()
    
    def cancel_data(self):
        """Set up window for canceling edits made to the data model."""
              
        confirm_cancel = QMessageBox(QMessageBox.Question, "Confirm Cancel", "Are you sure you want to remove your changes?")
        confirm_cancel.addButton(QMessageBox.Yes)
        confirm_cancel.addButton(QMessageBox.No)
        reply = confirm_cancel.exec()
        if reply == QMessageBox.Yes:
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
