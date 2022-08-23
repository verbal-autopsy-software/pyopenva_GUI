# -*- coding: utf-8 -*-

"""
pyopenva.command_center
~~~~~~~~~~~~~~
This module creates the window for loading data and setting algorithm options.
"""

import csv
import sys
from contextlib import contextmanager
from io import StringIO
import logging
from pandas import DataFrame
from PyQt5.QtCore import Qt, QDate, QTime
from PyQt5.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QGroupBox,
                             QLabel, QPushButton, QComboBox, QFileDialog,
                             QMessageBox, QLineEdit, QInputDialog, 
                             QTableView, QCheckBox)

from edit_window import EditData, EditableHeaderView
from insilico import InSilicoDialog
from interva import InterVADialog
from load import LoadData
from smartva import SmartVADialog
from pycrossva.transform import transform


class CommandCenter(QWidget):

    def __init__(self):
        super().__init__()
        self.raw_data = None
        self.raw_data_loaded = False
        self.pycrossva_data = None
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
        self.btn_pycrossva = QPushButton("Run pyCrossVA")
        self.btn_data_check = QPushButton("Data Check")
        self.btn_edit_data = QPushButton("Edit Check")
        self.btn_edit_data.setEnabled(False)
        self.btn_user_mode = QPushButton("Go Back to User Mode Selection")
        data_panel_v_box.addWidget(self.btn_load_data)
        data_panel_v_box.addWidget(label_data_format)
        data_panel_v_box.addWidget(self.btn_data_format)
        data_panel_v_box.addWidget(self.btn_pycrossva)
        data_panel_v_box.addWidget(self.btn_data_check)
        data_panel_v_box.addWidget(self.btn_edit_data)
        data_panel_v_box.addStretch(2)
        data_panel_v_box.addWidget(self.btn_user_mode)
        self.data_panel = QGroupBox("Data")
        self.data_panel.setLayout(data_panel_v_box)
        self.btn_load_data.clicked.connect(self.load_data)
        self.btn_edit_data.clicked.connect(self.create_edit_window)
        self.btn_pycrossva.clicked.connect(self.show_pycrossva)


    def load_data(self):
        """Set up window for loading csv data."""
        
        self.load_window = LoadData()
        if self.load_window.fname != '':
            self.btn_edit_data.setEnabled(True)


    @contextmanager
    def _capture_stdout(self, output):
        stdout = sys.stdout
        sys.stdout = output
        try:
            yield
        finally:
            sys.stdout = stdout

    def run_pycrossva(self):
        df = DataFrame(self.load_window.data[1:],
                       columns=self.load_window.data[0])
        pycrossva_stdout = StringIO()
        with self._capture_stdout(pycrossva_stdout):
            self.pycrossva_data = transform(("2016WHOv151", "InterVA5"), df)
        logging.info(pycrossva_stdout.getvalue())
        self.pycrossva_messages = pycrossva_stdout.getvalue()

    def show_pycrossva(self):
        self.msg = QMessageBox()
        self.msg.setIcon(QMessageBox.Information)
        self.run_pycrossva()

        self.msg.setText("Results for pyCrossVA")
        self.msg.setWindowTitle("pyCrossVA Results")
        self.msg.setDetailedText(self.pycrossva_messages)
        self.msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        self.msg.show()
        
    def create_edit_window(self):
        """Set up window for editing provided csv data or show error if data is N/A."""
        
        self.edit_window = EditData(self.load_window.data)
        self.editable_header = self.edit_window.table.horizontalHeader()
        self.editable_header = EditableHeaderView(Qt.Horizontal, self.edit_window)
        self.edit_window.table.setHorizontalHeader(self.editable_header)
        self.edit_window.table.setEditTriggers(QTableView.NoEditTriggers)
        self.edit_window.table.setRowHidden(0, True)
        self.edit_window.table.resizeColumnsToContents()
        
        edit_panel_h_box_1 = QHBoxLayout()
        self.checkbox_col_editing = QCheckBox("Editable Header Fields (Column Names)")
        self.checkbox_row_data_editing = QCheckBox("Editable Row Data")
        self.btn_save = QPushButton("Save Data")
        self.btn_cancel = QPushButton("Cancel")
        edit_panel_h_box_1.addWidget(self.checkbox_col_editing)
        edit_panel_h_box_1.addWidget(self.checkbox_row_data_editing)
        edit_panel_h_box_1.addWidget(self.btn_save)
        edit_panel_h_box_1.addWidget(self.btn_cancel)
        
        self.col_search_results = []
        self.col_search_results_counter = -1
        self.col_search_index = -1
        edit_panel_h_box_2 = QHBoxLayout()
        self.col_search_bar = QLineEdit()
        self.col_search_bar.setPlaceholderText("Search for Column Name")
        self.col_search_results_counter = QLabel(str(self.col_search_results_counter + 1) + "/" + str(len(self.col_search_results)))
        edit_panel_h_box_2.addWidget(self.col_search_bar)
        edit_panel_h_box_2.addWidget(self.col_search_results_counter)
        edit_panel_h_box_3 = QHBoxLayout()
        self.btn_previous_col =  QPushButton("Previous")
        self.btn_next_col =  QPushButton("Next")
        self.btn_close_col_find =  QPushButton("Clear Column Selection")
        edit_panel_h_box_3.addWidget(self.btn_previous_col)
        edit_panel_h_box_3.addWidget(self.btn_next_col)
        edit_panel_h_box_3.addWidget(self.btn_close_col_find)
        edit_panel_h_box_4 = QHBoxLayout()
        edit_panel_h_box_4.addLayout(edit_panel_h_box_2)
        edit_panel_h_box_4.addLayout(edit_panel_h_box_3)
        
        self.cond_col = -1
        self.row_search_results = []
        self.row_search_results_counter = -1
        self.row_search_index = -1
        edit_panel_h_box_5 = QHBoxLayout()
        self.row_search_bar = QLineEdit()
        self.row_search_bar.setPlaceholderText("Select a Column to Search by Row")
        self.row_search_results_counter = QLabel(str(self.row_search_results_counter + 1) + "/" + str(len(self.row_search_results)))
        edit_panel_h_box_5.addWidget(self.row_search_bar)
        edit_panel_h_box_5.addWidget(self.row_search_results_counter)
        edit_panel_h_box_6 = QHBoxLayout()
        self.btn_previous_row =  QPushButton("Previous")
        self.btn_next_row =  QPushButton("Next")
        self.btn_close_row_find =  QPushButton("Clear Row Selection")
        edit_panel_h_box_6.addWidget(self.btn_previous_row)
        edit_panel_h_box_6.addWidget(self.btn_next_row)
        edit_panel_h_box_6.addWidget(self.btn_close_row_find)
        edit_panel_h_box_7 = QHBoxLayout()
        edit_panel_h_box_7.addLayout(edit_panel_h_box_5)
        edit_panel_h_box_7.addLayout(edit_panel_h_box_6)
        
        edit_panel_h_box_8 = QHBoxLayout()
        self.sort_column = QLabel("No column selected to sort in ")
        self.sort_by = QComboBox()
        self.sort_by.addItems(("Original Order", "Ascending Order", "Descending Order"))
        self.btn_sort = QPushButton("Sort")
        edit_panel_h_box_8.addWidget(self.sort_column)
        edit_panel_h_box_8.addWidget(self.sort_by)
        edit_panel_h_box_8.addWidget(self.btn_sort)
        # self.col_search_bar.setStyleSheet('font-size: 14px')
        
        edit_panel_v_box = QVBoxLayout()
        edit_panel_v_box.addLayout(edit_panel_h_box_1)
        edit_panel_v_box.addLayout(edit_panel_h_box_4)
        edit_panel_v_box.addLayout(edit_panel_h_box_7)
        edit_panel_v_box.addWidget(self.edit_window)
        edit_panel_v_box.addLayout(edit_panel_h_box_8)
        
        self.edit_panel = QGroupBox("")
        self.edit_panel.setLayout(edit_panel_v_box)
        self.edit_panel.setWindowTitle("openVA GUI: Edit Data")
        self.edit_panel.setGeometry(400, 400, 700, 600)
        self.edit_panel.show()
        
        self.checkbox_col_editing.stateChanged.connect(lambda:self.editing_state(self.checkbox_col_editing))
        self.checkbox_row_data_editing.stateChanged.connect(lambda:self.editing_state(self.checkbox_row_data_editing))
        self.btn_save.clicked.connect(self.save_data)
        self.btn_cancel.clicked.connect(self.cancel_data)
        
        self.col_search_bar.textChanged.connect(self.column_find)
        self.btn_previous_col.clicked.connect(self.prev_col_clicked)
        self.btn_next_col.clicked.connect(self.next_col_clicked)
        self.btn_close_col_find.clicked.connect(self.close_col_find_clicked)
        
        self.row_search_bar.textChanged.connect(self.row_find)
        self.btn_previous_row.clicked.connect(self.prev_row_clicked)
        self.btn_next_row.clicked.connect(self.next_row_clicked)
        self.btn_close_row_find.clicked.connect(self.close_row_find_clicked)
        
        self.edit_window.table.clicked.connect(self.change_column)
        self.btn_sort.clicked.connect(self.sort_by_column)
        self.edit_window.table.selectionModel().currentChanged.connect(self.change_column)

        # load_first_msg = QMessageBox().information(self, "Error finding data", "Please load a valid data file.", QMessageBox.Ok)

    def editing_state(self, checkbox):
        """Updates editing state of the data table."""
    
        if checkbox.text() == "Editable Header Fields (Column Names)":
            if checkbox.isChecked() == True:
                self.editable_header.sectionDoubleClicked.connect(self.editable_header.edit_header)
                self.editable_header.line.editingFinished.connect(self.editable_header.done_editing)
            else:
                self.editable_header.sectionDoubleClicked.disconnect(self.editable_header.edit_header)
                self.editable_header.line.editingFinished.disconnect(self.editable_header.done_editing)
        if checkbox.text() == "Editable Row Data":
            if checkbox.isChecked() == True:
                self.edit_window.table.setEditTriggers(QTableView.AllEditTriggers)
            else:
                self.edit_window.table.setEditTriggers(QTableView.NoEditTriggers)


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

    def column_find(self):
        """Finds a specific column based off a text search."""
        
        self.row_search_bar.setText("")
        col_search_bar_text = self.col_search_bar.text().lower()
        if len(col_search_bar_text) == 0:
            self.col_search_results_counter.setText("0/0")
            self.edit_window.table.clearSelection()
        else:
            header = self.load_window.header[0]
            self.col_search_results = [x for x in range(len(header)) if col_search_bar_text in (header[x]).lower()]
            self.col_search_index = 0
            if len(self.col_search_results) > self.col_search_index:
                self.cond_col = self.col_search_results[self.col_search_index]
                self.edit_window.table.selectColumn(self.col_search_results[self.col_search_index])
                self.col_search_results_counter.setText(str(self.col_search_index + 1) + "/" + str(len(self.col_search_results)))
            else:
                self.col_search_results_counter.setText("0/0")
                self.edit_window.table.clearSelection()
       
    def prev_col_clicked(self):
        """Goes to the previous column that matches the text search."""
        
        self.col_search_index -= 1
        if len(self.col_search_bar.text()) != 0 and len(self.col_search_results) > self.col_search_index and self.col_search_index >= 0:
            self.row_search_bar.setText("")
            col_index = self.col_search_results[self.col_search_index]
            self.cond_col = col_index
            self.edit_window.table.selectColumn(col_index)
            self.col_search_results_counter.setText(str(self.col_search_index + 1) + "/" + str(len(self.col_search_results)))
            col_name = self.edit_window.model.column_name(col_index, Qt.DisplayRole)
            self.row_search_bar.setPlaceholderText("Search for row content in the column \"" + col_name +"\" column")
        else:
            self.col_search_index += 1
            no_result_msg = QMessageBox()
            no_result_msg.setWindowTitle("No results")
            no_result_msg.setText("No previous search result available.")
            x = no_result_msg.exec_()
        
    def next_col_clicked(self):
        """Goes to the next column that matches the text search."""
        
        self.col_search_index += 1
        if len(self.col_search_bar.text()) != 0 and len(self.col_search_results) > self.col_search_index:
            self.row_search_bar.setText("")
            col_index = self.col_search_results[self.col_search_index]
            self.cond_col = col_index
            self.edit_window.table.selectColumn(col_index)
            self.col_search_results_counter.setText(str(self.col_search_index + 1) + "/" + str(len(self.col_search_results)))
            col_name = self.edit_window.model.column_name(col_index, Qt.DisplayRole)
            self.row_search_bar.setPlaceholderText("Search for row content in \"" + col_name +"\" column")
        else:
            self.col_search_index -= 1
            no_result_msg = QMessageBox()
            no_result_msg.setWindowTitle("No results")
            no_result_msg.setText("No next search result available.")
            x = no_result_msg.exec_()
        
    def close_col_find_clicked(self):
        """Clears the text search for a column."""
        
        if len(self.col_search_bar.text()) != 0:
            self.col_search_bar.setText("")
            self.row_search_bar.setText("")
        self.col_search_results_counter.setText("0/0")
        self.edit_window.table.clearSelection()
        self.row_search_bar.setPlaceholderText("Select a Column to Search by Row")

    def row_find(self):
        """Finds a specific row based off a text search and is conditional on column search."""
        
        row_search_bar_text = self.row_search_bar.text().lower()        
        if len(row_search_bar_text) == 0:
            self.row_search_results_counter.setText("0/0")
            self.edit_window.table.clearSelection()
        else:
            placeholder = self.row_search_bar.placeholderText()
            if placeholder[:6] == "Search":
                col_name = placeholder[27:-8]
                self.cond_col = self.load_window.header[0].index(col_name)
            else: # placeholder[:6] == "Select"
                self.cond_col = 0
            
            self.row_search_results = [x for x in range(1, len(self.load_window.data)) if row_search_bar_text in (self.load_window.data[x][self.cond_col]).lower()]
            self.row_search_index = 0
            if len(self.row_search_results) > self.row_search_index:
                self.edit_window.table.selectRow(self.row_search_results[self.row_search_index])
                self.row_search_results_counter.setText(str(self.row_search_index + 1) + "/" + str(len(self.row_search_results)))
            else:
                self.row_search_results_counter.setText("0/0")
                self.edit_window.table.clearSelection()

    def prev_row_clicked(self):
        """Goes to the previous row that matches the text search."""
        
        self.row_search_index -= 1
        if len(self.row_search_bar.text()) != 0 and self.row_search_index >= 0:
            self.edit_window.table.selectRow(self.row_search_results[self.row_search_index])
            self.row_search_results_counter.setText(str(self.row_search_index + 1) + "/" + str(len(self.row_search_results)))
        else:
            self.row_search_index += 1
            no_result_msg = QMessageBox()
            no_result_msg.setWindowTitle("No results")
            no_result_msg.setText("No previous search result available.")
            x = no_result_msg.exec_()
        
    def next_row_clicked(self):
        """Goes to the next column that matches the text search."""
        
        self.row_search_index += 1
        if len(self.row_search_bar.text()) != 0 and len(self.row_search_results) > self.row_search_index:
            self.edit_window.table.selectRow(self.row_search_results[self.row_search_index])
            self.row_search_results_counter.setText(str(self.row_search_index + 1) + "/" + str(len(self.row_search_results)))
        else:
            self.row_search_index -= 1
            no_result_msg = QMessageBox()
            no_result_msg.setWindowTitle("No results")
            no_result_msg.setText("No next search result available.")
            x = no_result_msg.exec_()
        
    def close_row_find_clicked(self):
        """Clears the text search for a column."""
        
        if len(self.row_search_bar.text()) != 0:
            self.row_search_bar.setText("")
        self.row_search_bar.setPlaceholderText("Select a Column to Search by Row")
        self.row_search_results_counter.setText("0/0")
        self.edit_window.table.clearSelection()
            
    def change_column(self):
        """Updates placeholder text for row search and the displayed column name for sorting."""
        
        curr_index_col = self.edit_window.table.currentIndex().column()
        if len(self.col_search_bar.text()) != 0 and len(self.col_search_results) != 0:
            curr_index_col = self.col_search_results[self.col_search_index]
        col_name = self.edit_window.model.column_name(curr_index_col, role=Qt.DisplayRole)
        self.sort_column.setText("Sort the \"" + col_name + "\" column in ")
        if len(self.row_search_bar.text()) == 0:
            self.row_search_bar.setPlaceholderText("Search for row content in \"" + col_name +"\" column")

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
