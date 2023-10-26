# -*- coding: utf-8 -*-

"""
pyopenva.command_center
~~~~~~~~~~~~~~
This module creates the window for loading data and setting algorithm options.
"""

import csv
import tempfile
import sys
import os
import shutil
from contextlib import contextmanager
from io import StringIO
import logging
from pandas import DataFrame
from interva.interva5 import InterVA5
from insilicova.api import InSilicoVA
from insilicova.exceptions import InSilicoVAException
from insilicova.diag import csmf_diag
from insilicova.api import InSilicoVA
from PyQt5.QtCore import pyqtSignal, QObject, Qt, QDate, QThread, QTime
from PyQt5.QtWidgets import (QCheckBox, QComboBox, QDialog, QDialogButtonBox,
                             QFileDialog, QGroupBox, QHBoxLayout, QInputDialog,
                             QLabel, QLineEdit, QMessageBox, QProgressBar,
                             QPushButton, QScrollArea, QTableView, QVBoxLayout,
                             QWidget)

from pyopenva.edit_window import EditData, EditableHeaderView
from pyopenva.insilicova_ui import InSilicoVADialog
from pyopenva.interva_ui import InterVADialog
from pyopenva.load import LoadData
# from pyopenva.smartva_ui import SmartVADialog
from pyopenva.workers import InSilicoVAWorker, InterVAWorker
from pycrossva.transform import transform


class CommandCenter(QWidget):

    def __init__(self, parent=None):
        super().__init__()
        self.working_dir = ""
        self.raw_data = None
        self.raw_data_loaded = False
        self.label_data = None
        self.data_id_col = None
        self.prev_data_id_col = None
        self.pycrossva_data = None
        self.insilicova_dialog = None
        self.interva_dialog = None
        self.load_window = None
        self.parent = parent

        #self.setGeometry(400, 400, 700, 600)
        self.setWindowTitle("openVA GUI: Command Center")
        layout = QVBoxLayout()
        self.data_algorithm_h_box = QHBoxLayout()
        self.create_data_panel()
        self.create_algorithm_panel()
        self.data_algorithm_h_box.addWidget(self.data_panel)
        self.data_algorithm_h_box.addWidget(self.algorithm_panel)
        self.hbox_navigate = QHBoxLayout()
        self.btn_user_mode = QPushButton("Go Back to User Mode Selection")
        self.btn_algorithm_results = QPushButton("Results")
        self.btn_command_center_exit = QPushButton("Exit")
        self.hbox_navigate.addWidget(self.btn_user_mode)
        self.hbox_navigate.addWidget(self.btn_algorithm_results)
        self.hbox_navigate.addWidget(self.btn_command_center_exit)
        layout.addLayout(self.data_algorithm_h_box)
        # self.setLayout(self.data_algorithm_h_box)
        layout.addLayout(self.hbox_navigate)
        self.setLayout(layout)

        # initialize InSilico parameters
        self.insilicova_limit = 100
        self.n_iterations = 3000
        self.jump_scale = 0.1
        self.auto_extend = True
        self.seed = 653
        self.insilicova_results = None
        self.insilicova_warnings = None
        self.insilicova_errors = None
        self.insilicova_ctrl = {"break": False}

        # initialize InterVA parameters
        self.hiv = "low"
        self.malaria = "low"
        self.interva_results = None
        self.interva_tmp_dir = None
        self.interva_log = None
        self.interva_ctrl = {"break": False}

        # # initialize SmartVA parameters
        # self.smartva_country = "Unknown"
        # self.smartva_hiv = "False"
        # self.smartva_malaria = "False"
        # self.smartva_hce = "True"
        # self.smartva_freetext = "True"
        # self.smartva_results = None

    def create_data_panel(self):
        """Set up data panel for loading, editing, and checking the data."""

        data_panel_v_box = QVBoxLayout()
        self.btn_load_data = QPushButton("Load Data (.csv)")
        self.label_data = QLabel("(no data loaded)")
        self.label_data_fname = QLabel("")
        self.label_data_n_records = QLabel("")
        self.btn_edit_data = QPushButton("Edit Data")
        self.btn_edit_data.setEnabled(False)
        label_data_id_col = QLabel("Select ID column in data")
        self.combo_data_id_col = QComboBox()
        self.combo_data_id_col.currentTextChanged.connect(
            self.set_data_id_col)
        self.label_data.setAlignment(Qt.AlignCenter)
        label_data_format = QLabel("Data Format")
        # TODO: use format in argument for pycrossva (need a setter function
        #       with a dictionary for mapping options to pycrossva parameters)
        self.btn_data_format = QComboBox()
        self.btn_data_format.addItems(("WHO 2016",))
                                       # "WHO 2012",
                                       # "PHMRC"))
        label_pycrossva_info = QLabel("Convert data: ODK -> openVA format")
        self.btn_pycrossva = QPushButton("Run pyCrossVA")
        self.btn_pycrossva.setEnabled(False)
        self.label_pycrossva_status = QLabel("(no data loaded)")
        self.label_pycrossva_status.setAlignment(Qt.AlignCenter)
        self.btn_save_pycrossva = QPushButton("Save pyCrossVA Data (.csv)")
        self.btn_save_pycrossva.setEnabled(False)
        self.btn_save_pycrossva.clicked.connect(self.save_pycrossva)
        data_panel_v_box.addWidget(self.btn_load_data)
        data_panel_v_box.addWidget(self.label_data)
        data_panel_v_box.addWidget(self.label_data_fname)
        data_panel_v_box.addWidget(self.label_data_n_records)
        # data_panel_v_box.addStretch(1)
        data_panel_v_box.addWidget(self.btn_edit_data)
        data_panel_v_box.addStretch(1)
        data_panel_v_box.addWidget(label_data_id_col)
        data_panel_v_box.addWidget(self.combo_data_id_col)
        data_panel_v_box.addStretch(1)
        data_panel_v_box.addWidget(label_data_format)
        data_panel_v_box.addWidget(self.btn_data_format)
        data_panel_v_box.addStretch(1)
        data_panel_v_box.addWidget(label_pycrossva_info)
        data_panel_v_box.addWidget(self.btn_pycrossva)
        data_panel_v_box.addWidget(self.label_pycrossva_status)
        data_panel_v_box.addStretch(1)
        data_panel_v_box.addWidget(self.btn_save_pycrossva)
        data_panel_v_box.addStretch(2)
        # data_panel_v_box.addWidget(self.btn_user_mode)
        self.data_panel = QGroupBox("Data")
        self.data_panel.setLayout(data_panel_v_box)
        self.btn_load_data.clicked.connect(self.load_data)
        self.btn_load_data.clicked.connect(self.update_data)
        self.btn_edit_data.clicked.connect(self.create_edit_window)
        self.btn_pycrossva.clicked.connect(self.show_pycrossva)

    def load_data(self):
        """Set up window for loading csv data."""
        
        self.load_window = LoadData(working_dir=self.working_dir)
        if self.load_window.fname != "":
            self.btn_edit_data.setEnabled(True)
            n_records = len(self.load_window.data) - 1
            f_name = self.load_window.fname.split("/")[-1]
            self.label_data.setAlignment(Qt.AlignLeft)
            self.label_data.setText("Data loaded:")
            self.label_data_fname.setAlignment(Qt.AlignCenter)
            self.label_data_fname.setText(f"{f_name}")
            self.label_data_n_records.setAlignment(Qt.AlignCenter)
            self.label_data_n_records.setText(f"({n_records} records)")
            self.label_pycrossva_status.setText("(need to run pyCrossVA)")
            self.combo_data_id_col.blockSignals(True)
            self.combo_data_id_col.clear()
            self.combo_data_id_col.addItems(
                ["no ID column"] + self.load_window.header[0])
            self.combo_data_id_col.blockSignals(False)
            self.combo_data_id_col.setCurrentIndex(0)

            self.pycrossva_data = None
            self.insilicova_results = None
            self.label_insilicova_progress.setText("")
            self.insilicova_pbar.setValue(0)
            self.insilicova_warnings = None
            self.insilicova_errors = None
            self.interva_results = None
            self.interva_log = None
            self.label_interva_progress.setText("")
            self.interva_pbar.setValue(0)
            self.btn_pycrossva.setEnabled(True)
            # self.smartva_results = None
            # self.label_smartva_progress.setText("")
            data_problem = False
            try:
                df = DataFrame(self.load_window.data[1:],
                               columns=self.load_window.data[0])
                self.parent.results.original_data = df
                if df.shape[0] == 0:
                    data_problem = True
                    alert = QMessageBox()
                    alert.setWindowTitle("openVA App")
                    alert.setIcon(QMessageBox.Warning)
                    alert.setText(
                        f"Unable to read in CSV file {f_name}.\n" +
                        "File appears to be empty.")
                    alert.exec()
            except ValueError:
                data_problem = True
                alert = QMessageBox()
                alert.setWindowTitle("openVA App")
                alert.setText(
                    f"Error to processing the file {f_name}.\n"
                    "These data have an unexpected format.  Please load "
                    "data in the format of an ODK export.")
                alert.exec()
            if data_problem:
                self.parent.results.original_data = None
                self.btn_edit_data.setEnabled(False)
                self.raw_data = None
                self.raw_data_loaded = False
                self.label_data.setText("(no data loaded)")
                self.label_data_fname.setText("")
                self.label_data_n_records.setText("")
                self.data_id_col = None
                self.prev_data_id_col = None
                self.pycrossva_data = None
                self.load_window = None

    def update_data(self):
        """Update status of data."""
        pass

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
        if self.data_id_col == "no ID column":
            raw_data_id = None
        else:
            raw_data_id = self.data_id_col
        with self._capture_stdout(pycrossva_stdout):
            self.pycrossva_data = transform(
                mapping=("2016WHOv151", "InterVA5"),
                raw_data=df,
                raw_data_id=raw_data_id,
                lower=True)
        logging.info(pycrossva_stdout.getvalue())
        self.pycrossva_messages = pycrossva_stdout.getvalue()
        self.label_pycrossva_status.setText("(pyCrossVA finished)")

    def show_pycrossva(self):
        if self.load_window is None:
            alert = QMessageBox()
            alert.setWindowTitle("openVA App")
            alert.setText("Please load data before running pyCrossVA.")
            alert.exec()
        else:
            self.run_pycrossva()
            self.btn_save_pycrossva.setEnabled(True)
            self.pycva_diag = PyCrossVADialog()
            if self.pycrossva_messages == "":
                self.pycva_diag.set_text(
                    "Data successfully converted to openVA format")
            else:
                if (self.pycrossva_data.iloc[:, 1:] == ".").all(axis=None):
                    self.pycva_diag.set_text(
                        "ERROR: ALL VALUES ARE MISSING!\n"
                        "The data have an unexpected format and cannot be "
                        "processed. Please reload data in the expected format")
                else:
                    msg = "pyCrossVA returned message\n"
                    msg += self.pycrossva_messages
                    self.pycva_diag.set_text(msg)
            self.pycva_diag.exec()

    def save_pycrossva(self):
        if self.pycrossva_data is None:
            alert = QMessageBox()
            alert.setWindowTitle("openVA App")
            alert.setText(
                "No data available.  Please load data in the expected "
                "format and/or run pyCrossVA.")
            alert.exec()
        else:
            pycrossva_file_name = "pycrossva_output.csv"
            pycrossva_file_name = os.path.join(self.working_dir,
                                               pycrossva_file_name)
            path = QFileDialog.getSaveFileName(self,
                                               "Save pyCrossVA output (csv)",
                                               pycrossva_file_name,
                                               "CSV Files (*.csv)")
            if path != ("", ""):
                try:
                    self.pycrossva_data.to_csv(path[0], index=False)
                    if os.path.isfile(path[0]):
                        alert = QMessageBox()
                        alert.setWindowTitle("openVA App")
                        alert.setText("pyCrossVA output saved to" + path[0])
                        alert.exec()
                    else:
                        alert = QMessageBox()
                        alert.setWindowTitle("openVA App")
                        alert.setText(
                            "ERROR: unable to save pyCrossVA output to"
                            f"{path[0]}")
                        alert.exec()
                except (OSError, PermissionError):
                    alert = QMessageBox()
                    alert.setWindowTitle("openVA App")
                    alert.setIcon(QMessageBox.Warning)
                    alert.setText(
                        f"Unable to save {path[0]}.\n" +
                        "(don't have permission or read-only file system)")
                    alert.exec()
        
    def create_edit_window(self):
        """Set up window for editing provided csv data or show error if
        data is N/A."""
        
        self.edit_window = EditData(self.load_window.data)
        self.editable_header = self.edit_window.table.horizontalHeader()
        self.editable_header = EditableHeaderView(Qt.Horizontal,
                                                  self.edit_window)
        self.edit_window.table.setHorizontalHeader(self.editable_header)
        self.edit_window.table.setEditTriggers(QTableView.NoEditTriggers)
        self.edit_window.table.setRowHidden(0, True)
        self.edit_window.table.resizeColumnsToContents()
        
        edit_panel_h_box_1 = QHBoxLayout()
        self.checkbox_col_editing = QCheckBox(
            "Editable Header Fields (Column Names)")
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
        self.col_search_results_counter = QLabel(
            str(self.col_search_results_counter + 1) + "/" +
            str(len(self.col_search_results)))
        edit_panel_h_box_2.addWidget(self.col_search_bar)
        edit_panel_h_box_2.addWidget(self.col_search_results_counter)
        edit_panel_h_box_3 = QHBoxLayout()
        self.btn_previous_col = QPushButton("Previous")
        self.btn_next_col = QPushButton("Next")
        self.btn_close_col_find = QPushButton("Clear Column Selection")
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
        self.row_search_bar.setPlaceholderText(
            "Select a Column to Search by Row")
        self.row_search_results_counter = QLabel(
            str(self.row_search_results_counter + 1) + "/" +
            str(len(self.row_search_results)))
        edit_panel_h_box_5.addWidget(self.row_search_bar)
        edit_panel_h_box_5.addWidget(self.row_search_results_counter)
        edit_panel_h_box_6 = QHBoxLayout()
        self.btn_previous_row = QPushButton("Previous")
        self.btn_next_row = QPushButton("Next")
        self.btn_close_row_find = QPushButton("Clear Row Selection")
        edit_panel_h_box_6.addWidget(self.btn_previous_row)
        edit_panel_h_box_6.addWidget(self.btn_next_row)
        edit_panel_h_box_6.addWidget(self.btn_close_row_find)
        edit_panel_h_box_7 = QHBoxLayout()
        edit_panel_h_box_7.addLayout(edit_panel_h_box_5)
        edit_panel_h_box_7.addLayout(edit_panel_h_box_6)
        
        edit_panel_h_box_8 = QHBoxLayout()
        self.sort_column = QLabel("No column selected to sort in ")
        self.sort_by = QComboBox()
        self.sort_by.addItems(("Original Order",
                               "Ascending Order",
                               "Descending Order"))
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
        
        self.checkbox_col_editing.stateChanged.connect(
            lambda: self.editing_state(self.checkbox_col_editing))
        self.checkbox_row_data_editing.stateChanged.connect(
            lambda: self.editing_state(self.checkbox_row_data_editing))
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
        self.edit_window.table.selectionModel().currentChanged.connect(
            self.change_column)

        # load_first_msg = QMessageBox().information(self, "Error finding data", "Please load a valid data file.", QMessageBox.Ok)

    def editing_state(self, checkbox):
        """Updates editing state of the data table."""
    
        if checkbox.text() == "Editable Header Fields (Column Names)":
            if checkbox.isChecked() is True:
                self.editable_header.sectionDoubleClicked.connect(
                    self.editable_header.edit_header)
                self.editable_header.line.editingFinished.connect(
                    self.editable_header.done_editing)
            else:
                self.editable_header.sectionDoubleClicked.disconnect(
                    self.editable_header.edit_header)
                self.editable_header.line.editingFinished.disconnect(
                    self.editable_header.done_editing)
        if checkbox.text() == "Editable Row Data":
            if checkbox.isChecked() is True:
                self.edit_window.table.setEditTriggers(
                    QTableView.AllEditTriggers)
            else:
                self.edit_window.table.setEditTriggers(
                    QTableView.NoEditTriggers)

    def save_data(self):
        """Set up window for saving data and prompts for user's name."""

        name = ""
        text, ok = QInputDialog.getText(self.edit_panel,
                                        "Name Input",
                                        "Enter your name for save file name purposes:")
        while ok and len(text) == 0:
            load_first_msg = QMessageBox().information(
                self.edit_panel,
                "Length of text error",
                "Please type in your name, which must be more than 0 characters long.",
                QMessageBox.Ok)
            text, ok = QInputDialog.getText(
                self.edit_panel,
                "Name Input",
                "Enter your name for save file name purposes:")
        if ok and len(text) > 0:
            name += str(text).replace(" ", "-")
            date = QDate.currentDate().toString(Qt.ISODate)
            time = QTime.currentTime().toString("hh.mm.ss.zzz")
            # save file format: file-name_edited-by_name_date_time.csv
            file_name = QFileDialog.getSaveFileName(
                self,
                "Save As",
                self.working_dir + self.load_window.fname[:-4] +
                "_edited-by_" + name + "_" + date + "_" + time,
                "csv Files (*.csv)")

            fname = file_name[0]
            if file_name is not None and fname != "":
                self.load_window.fname = fname
                with open(fname, "w", newline = '') as output_file:
                    csvwriter = csv.writer(output_file) 
                    for row in self.edit_window.model.data:
                        csvwriter.writerow(row)
                    self.edit_panel.close()
            else:
                self.edit_panel.close()
                self.edit_panel.show()
    
    def cancel_data(self):
        """Set up window for canceling edits made to the data model."""
              
        confirm_cancel = QMessageBox(
            QMessageBox.Question,
            "Confirm Cancel",
            "Are you sure you want to remove your changes?")
        confirm_cancel.setWindowTitle("openVA App")
        confirm_cancel.addButton(QMessageBox.Yes)
        confirm_cancel.addButton(QMessageBox.No)
        reply = confirm_cancel.exec()
        if reply == QMessageBox.Yes:
            header = []
            rows = []
            data = []
            with open(self.load_window.fname, "r", newline="") as file:
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
            self.col_search_results = [
                x for x in range(len(header)) if
                col_search_bar_text in (header[x]).lower()]
            self.col_search_index = 0
            if len(self.col_search_results) > self.col_search_index:
                self.cond_col = self.col_search_results[self.col_search_index]
                self.edit_window.table.selectColumn(
                    self.col_search_results[self.col_search_index])
                self.col_search_results_counter.setText(
                    str(self.col_search_index + 1) + "/" +
                    str(len(self.col_search_results)))
            else:
                self.col_search_results_counter.setText("0/0")
                self.edit_window.table.clearSelection()

    def prev_col_clicked(self):
        """Goes to the previous column that matches the text search."""
        
        self.col_search_index -= 1
        if len(self.col_search_bar.text()) != 0 and \
                len(self.col_search_results) > self.col_search_index and \
                self.col_search_index >= 0:
            self.row_search_bar.setText("")
            col_index = self.col_search_results[self.col_search_index]
            self.cond_col = col_index
            self.edit_window.table.selectColumn(col_index)
            self.col_search_results_counter.setText(
                str(self.col_search_index + 1) + "/" +
                str(len(self.col_search_results)))
            col_name = self.edit_window.model.column_name(col_index,
                                                          Qt.DisplayRole)
            self.row_search_bar.setPlaceholderText(
                "Search for row content in the column \"" + col_name + "\" column")
        else:
            self.col_search_index += 1
            no_result_msg = QMessageBox()
            no_result_msg.setWindowTitle("openVA App: No results")
            no_result_msg.setText("No previous search result available.")
            x = no_result_msg.exec_()
        
    def next_col_clicked(self):
        """Goes to the next column that matches the text search."""
        
        self.col_search_index += 1
        if len(self.col_search_bar.text()) != 0 and \
                len(self.col_search_results) > self.col_search_index:
            self.row_search_bar.setText("")
            col_index = self.col_search_results[self.col_search_index]
            self.cond_col = col_index
            self.edit_window.table.selectColumn(col_index)
            self.col_search_results_counter.setText(
                str(self.col_search_index + 1) + "/" +
                str(len(self.col_search_results)))
            col_name = self.edit_window.model.column_name(col_index,
                                                          Qt.DisplayRole)
            self.row_search_bar.setPlaceholderText(
                "Search for row content in \"" + col_name +"\" column")
        else:
            self.col_search_index -= 1
            no_result_msg = QMessageBox()
            no_result_msg.setWindowTitle("openVA App: No results")
            no_result_msg.setText("No next search result available.")
            x = no_result_msg.exec_()
        
    def close_col_find_clicked(self):
        """Clears the text search for a column."""
        
        if len(self.col_search_bar.text()) != 0:
            self.col_search_bar.setText("")
            self.row_search_bar.setText("")
        self.col_search_results_counter.setText("0/0")
        self.edit_window.table.clearSelection()
        self.row_search_bar.setPlaceholderText(
            "Select a Column to Search by Row")

    def row_find(self):
        """Finds a specific row based off a text search and is conditional on
        column search."""
        
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
            
            self.row_search_results = [
                x for x in range(1, len(self.load_window.data)) if
                row_search_bar_text in
                (self.load_window.data[x][self.cond_col]).lower()]
            self.row_search_index = 0
            if len(self.row_search_results) > self.row_search_index:
                self.edit_window.table.selectRow(
                    self.row_search_results[self.row_search_index])
                self.row_search_results_counter.setText(
                    str(self.row_search_index + 1) + "/" +
                    str(len(self.row_search_results)))
            else:
                self.row_search_results_counter.setText("0/0")
                self.edit_window.table.clearSelection()

    def prev_row_clicked(self):
        """Goes to the previous row that matches the text search."""
        
        self.row_search_index -= 1
        if len(self.row_search_bar.text()) != 0 and self.row_search_index >= 0:
            self.edit_window.table.selectRow(self.row_search_results[
                                                 self.row_search_index])
            self.row_search_results_counter.setText(
                str(self.row_search_index + 1) + "/" +
                str(len(self.row_search_results)))
        else:
            self.row_search_index += 1
            no_result_msg = QMessageBox()
            no_result_msg.setWindowTitle("openVA App: No results")
            no_result_msg.setText("No previous search result available.")
            x = no_result_msg.exec_()
        
    def next_row_clicked(self):
        """Goes to the next column that matches the text search."""
        
        self.row_search_index += 1
        if len(self.row_search_bar.text()) != 0 and \
                len(self.row_search_results) > self.row_search_index:
            self.edit_window.table.selectRow(
                self.row_search_results[self.row_search_index])
            self.row_search_results_counter.setText(
                str(self.row_search_index + 1) + "/" +
                str(len(self.row_search_results)))
        else:
            self.row_search_index -= 1
            no_result_msg = QMessageBox()
            no_result_msg.setWindowTitle("openVA App: No results")
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
        """Updates placeholder text for row search and the displayed column
        name for sorting."""
        
        curr_index_col = self.edit_window.table.currentIndex().column()
        if len(self.col_search_bar.text()) != 0 and len(self.col_search_results) != 0:
            curr_index_col = self.col_search_results[self.col_search_index]
        col_name = self.edit_window.model.column_name(curr_index_col,
                                                      role=Qt.DisplayRole)
        self.sort_column.setText("Sort the \"" + col_name + "\" column in ")
        if len(self.row_search_bar.text()) == 0:
            self.row_search_bar.setPlaceholderText(
                "Search for row content in \"" + col_name +"\" column")

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

        self.create_insilicova_box()
        self.create_interva_box()
        # self.create_smartva_box()
        # self.btn_algorithm_results = QPushButton("Results")

        algorithm_panel_v_box.addWidget(self.insilicova_box)
        #algorithm_panel_v_box.addStretch(1)
        # algorithm_panel_v_box.addLayout(self.interva_box)
        algorithm_panel_v_box.addWidget(self.interva_box)
        #algorithm_panel_v_box.addStretch(1)
        # algorithm_panel_v_box.addLayout(self.smartva_box)
        # algorithm_panel_v_box.addWidget(self.smartva_box)
        #algorithm_panel_v_box.addStretch(1)
        # algorithm_panel_v_box.addWidget(self.btn_algorithm_results)
        self.algorithm_panel = QGroupBox("Algorithms")
        self.algorithm_panel.setLayout(algorithm_panel_v_box)
        self.btn_insilicova_options.clicked.connect(self.run_insilicova_dialog)
        self.btn_interva_options.clicked.connect(self.run_interva_dialog)
        # self.btn_smartva_options.clicked.connect(self.run_smartva_dialog)
        self.btn_insilicova_run.clicked.connect(self.run_insilicova)
        self.btn_interva_run.clicked.connect(self.run_interva)
        # self.btn_smartva_run.clicked.connect(self.run_smartva)
        # self.btn_interva_options.clicked.connect(self.run_interva_dialog)
        # self.btn_smartva_options.clicked.connect(self.run_smartva_dialog)

    def create_insilicova_box(self):
        """Set up box of widgets for InSilicoVA."""

        self.insilicova_box = QGroupBox("InSilicoVA")
        insilicova_vbox = QVBoxLayout()
        insilicova_hbox = QHBoxLayout()
        self.btn_insilicova_options = QPushButton("Set Options")
        self.btn_insilicova_run = QPushButton("Run InSilicoVA")
        insilicova_hbox.addWidget(self.btn_insilicova_options)
        insilicova_hbox.addWidget(self.btn_insilicova_run)
        self.insilicova_pbar = QProgressBar(self)
        self.label_insilicova_progress = QLabel("")
        self.btn_insilicova_stop = QPushButton("Stop")
        self.btn_insilicova_stop.setMaximumWidth(125)
        self.btn_insilicova_stop.setEnabled(False)
        self.btn_insilicova_stop.clicked.connect(self.stop_insilicova)
        self.btn_check_convergence = QPushButton("Check convergence")
        self.btn_check_convergence.setEnabled(False)
        self.btn_check_convergence.clicked.connect(self.check_convergence)
        self.btn_save_insilicova_log = QPushButton(
            "Save log file from data checks")
        self.btn_save_insilicova_log.setEnabled(False)
        self.btn_save_insilicova_log.clicked.connect(
            self.save_insilicova_log)
        insilicova_vbox.setAlignment(Qt.AlignCenter)
        insilicova_vbox.addLayout(insilicova_hbox)
        insilicova_vbox.addWidget(self.insilicova_pbar)
        insilicova_vbox.addWidget(self.label_insilicova_progress)
        insilicova_vbox.addWidget(self.btn_insilicova_stop)
        insilicova_vbox.addWidget(self.btn_check_convergence)
        insilicova_vbox.addWidget(self.btn_save_insilicova_log)
        self.insilicova_box.setLayout(insilicova_vbox)

    def create_interva_box(self):
        """Set up box of widgets for InterVA."""

        self.interva_box = QGroupBox("InterVA")
        interva_vbox = QVBoxLayout()
        interva_hbox = QHBoxLayout()
        self.btn_interva_options = QPushButton("Set Options")
        self.btn_interva_run = QPushButton("Run InterVA")
        interva_hbox.addWidget(self.btn_interva_options)
        interva_hbox.addWidget(self.btn_interva_run)
        self.interva_pbar = QProgressBar(self)
        self.label_interva_progress = QLabel("")
        self.btn_interva_stop = QPushButton("Stop")
        self.btn_interva_stop.setMaximumWidth(125)
        self.btn_interva_stop.setEnabled(False)
        self.btn_interva_stop.clicked.connect(self.stop_interva)
        interva_vbox.setAlignment(Qt.AlignCenter)
        interva_vbox.addLayout(interva_hbox)
        interva_vbox.addWidget(self.interva_pbar)
        interva_vbox.addWidget(self.label_interva_progress)
        interva_vbox.addWidget(self.btn_interva_stop)
        self.btn_save_interva_log = QPushButton(
            "Save log file from data checks")
        self.btn_save_interva_log.setEnabled(False)
        self.btn_save_interva_log.clicked.connect(
            self.save_interva_log)
        interva_vbox.addWidget(self.btn_save_interva_log)
        self.interva_box.setLayout(interva_vbox)

    # def create_smartva_box(self):
    #     """Set up box of widgets for SmartVA."""
    #
    #     # self.smartva_box = QVBoxLayout()
    #     # smartva_label = QLabel("SmartVA")
    #     # smartva_hbox_2 = QHBoxLayout()
    #     # self.btn_smartva_options = QPushButton("Set Options")
    #     # self.btn_smartva_run = QPushButton("Run SmartVA")
    #     # smartva_hbox_2.addWidget(self.btn_smartva_options)
    #     # smartva_hbox_2.addWidget(self.btn_smartva_run)
    #     # self.smartva_pbar = QProgressBar(self)
    #     # self.label_smartva_progress = QLabel("")
    #     # self.smartva_box.addWidget(smartva_label)
    #     # self.smartva_box.addLayout(smartva_hbox_2)
    #     # self.smartva_box.addWidget(self.smartva_pbar)
    #     # self.smartva_box.addWidget(self.label_smartva_progress)
    #     self.smartva_box = QGroupBox("SmartVA")
    #     smartva_vbox = QVBoxLayout()
    #     smartva_hbox = QHBoxLayout()
    #     self.btn_smartva_options = QPushButton("Set Options")
    #     self.btn_smartva_run = QPushButton("Run SmartVA")
    #     smartva_hbox.addWidget(self.btn_smartva_options)
    #     smartva_hbox.addWidget(self.btn_smartva_run)
    #     self.smartva_pbar = QProgressBar(self)
    #     self.label_smartva_progress = QLabel("")
    #     smartva_vbox.setAlignment(Qt.AlignCenter)
    #     smartva_vbox.addLayout(smartva_hbox)
    #     smartva_vbox.addWidget(self.smartva_pbar)
    #     smartva_vbox.addWidget(self.label_smartva_progress)
    #     self.smartva_box.setLayout(smartva_vbox)

    def run_insilicova_dialog(self):
        self.insilicova_dialog = InSilicoVADialog(self,
                                                  self.seed,
                                                  self.auto_extend,
                                                  self.jump_scale,
                                                  self.n_iterations)
        self.insilicova_dialog.exec()

    def update_insilicova_n_iterations(self, updated_n_iterations):
        self.n_iterations = updated_n_iterations

    def update_insilicova_jump_scale(self, updated_jump_scale):
        self.jump_scale = updated_jump_scale

    def update_insilicova_auto_extend(self, updated_auto_extend):
        self.auto_extend = updated_auto_extend

    def update_insilicova_seed(self, updated_seed):
        self.seed = updated_seed

    def run_insilicova(self):
        self.insilicova_ctrl["break"] = False
        self.btn_insilicova_options.setEnabled(False)
        self.btn_insilicova_run.setEnabled(False)
        self.btn_load_data.setEnabled(False)
        self.btn_pycrossva.setEnabled(False)
        self.combo_data_id_col.setEnabled(False)
        self.btn_data_format.setEnabled(False)
        self.btn_edit_data.setEnabled(False)
        self.btn_check_convergence.setEnabled(False)
        self.btn_save_insilicova_log.setEnabled(False)
        self.btn_insilicova_options.setEnabled(True)
        if self.pycrossva_data is None:
            alert = QMessageBox()
            alert.setWindowTitle("openVA App")
            alert.setText(
                "Data need to be loaded and/or prepared with pyCrossVA.")
            alert.exec()
            self.btn_insilicova_options.setEnabled(True)
            self.btn_insilicova_run.setEnabled(True)
            self.btn_load_data.setEnabled(True)
            self.btn_pycrossva.setEnabled(True)
            self.combo_data_id_col.setEnabled(True)
            self.btn_data_format.setEnabled(True)
            self.btn_edit_data.setEnabled(True)
            self.btn_check_convergence.setEnabled(False)
            self.btn_save_insilicova_log.setEnabled(False)
            self.btn_insilicova_options.setEnabled(True)
        else:
            n_records = self.pycrossva_data.shape[0]
            tmp_ins = InSilicoVA(self.pycrossva_data, run=False)
            tmp_ins._remove_bad(is_numeric=False)
            n_valid = tmp_ins.data.shape[0]
            n_removed = n_records - n_valid
            if self.pycrossva_data["ID"].is_unique:
                index_removed = (~self.pycrossva_data.ID.isin(tmp_ins.data.ID))
                id_removed = self.pycrossva_data.ID[index_removed].astype("str")
                id_removed_str = "\n".join(id_removed)
            del tmp_ins
            if n_valid < self.insilicova_limit:
                msg = ("InSilicoVA is unavailable.  At least "
                       f"{self.insilicova_limit} deaths are needed for "
                       "reliable results.")
                if n_removed > 0:
                    msg += (f"\n\nData check removed {n_removed} deaths "
                            "because of missing data.")
                    if self.pycrossva_data["ID"].is_unique:
                        # msg += f"  IDs are:\n\n{id_removed_str}"
                        msg += "  IDs are listed below."
                msg += "\n(InterVA is available.)\n\n"
                # alert = QMessageBox()
                # alert.setText(msg)
                alert = ScrollMessageBox("openVA App: InSilicoVA message",
                                         msg, id_removed)
                alert.exec()
                self.btn_insilicova_options.setEnabled(True)
                self.btn_insilicova_run.setEnabled(True)
                self.btn_load_data.setEnabled(True)
                self.btn_pycrossva.setEnabled(True)
                self.combo_data_id_col.setEnabled(True)
                self.btn_data_format.setEnabled(True)
                self.btn_edit_data.setEnabled(True)
                self.btn_check_convergence.setEnabled(False)
                self.btn_save_insilicova_log.setEnabled(False)
                self.btn_insilicova_options.setEnabled(True)
            else:
                self.insilicova_warnings = None
                self.insilicova_errors = None
                self.insilicova_results = None
                burnin = max(int(self.n_iterations / 2), 1)
                thin = 10
                self.insilicova_thread = QThread()
                self.insilicova_worker = InSilicoVAWorker(
                    self.pycrossva_data,
                    data_type="WHO2016",
                    n_sim=self.n_iterations,
                    thin=thin,
                    burnin=burnin,
                    auto_length=self.auto_extend,
                    seed=self.seed,
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
                    self.parent.update_insilicova_results)
                self.insilicova_thread.start()
                self.btn_insilicova_stop.setEnabled(True)

                self.btn_insilicova_options.setEnabled(False)
                self.btn_insilicova_run.setEnabled(False)
                self.insilicova_thread.finished.connect(
                    lambda: self.btn_insilicova_options.setEnabled(True))
                self.insilicova_thread.finished.connect(
                    lambda: self.btn_insilicova_run.setEnabled(True))
                self.insilicova_thread.finished.connect(
                    lambda: self.btn_insilicova_stop.setEnabled(False))
                self.insilicova_thread.finished.connect(
                    lambda: self.btn_load_data.setEnabled(True))
                self.insilicova_thread.finished.connect(
                    lambda: self.combo_data_id_col.setEnabled(True))
                self.insilicova_thread.finished.connect(
                    lambda: self.btn_data_format.setEnabled(True))
                self.insilicova_thread.finished.connect(
                    lambda: self.btn_pycrossva.setEnabled(True))
                self.insilicova_thread.finished.connect(
                    lambda: self.btn_edit_data.setEnabled(True))
                self.insilicova_thread.finished.connect(
                    lambda: self.btn_check_convergence.setEnabled(True))
                self.insilicova_thread.finished.connect(
                    lambda: self.btn_save_insilicova_log.setEnabled(True))
                self.insilicova_thread.finished.connect(
                    lambda: self.btn_insilicova_options.setEnabled(True))
            #     except InSilicoVAException as exc:
            #         alert = QMessageBox()
            #         alert.setWindowTitle("openVA App")
            #         alert.setText("ERROR: Failed to run InSilicoVA" + exc)
            #         alert.exec()
            #     try:
            #         self.insilicova_results = insilicova_out.get_results()
            #         self.insilicova_errors = insilicova_out._error_log
            #         self.insilicova_warnings = insilicova_out._warning
            #         self.label_insilicova_progress.setText(
            #             "InSilicoVA results are ready")
            #     except InSilicoVAException as exc:
            #         self.insilicova_errors = insilicova_out._error_log
            #         self.insilicova_warnings = insilicova_out._warning
            #         if hasattr(insilicova_out, "_data_check") is False:
            #             self.insilicova_warnings = (
            #                 "No valid records for data consistency check")
            #         self.label_insilicova_progress.setText(
            #             "Data do not have any valid VA records (no results "
            #             "available).  \nSee log file for more details.\n"
            #             "Please reload data in the expected format.")
            # self.btn_insilicova_run.setEnabled(True)

    def update_insilicova_progress(self, n):
        self.insilicova_pbar.setValue(n)

    def update_insilicova_progress_label(self, msg):
        self.label_insilicova_progress.setText(msg)

    def update_insilicova_warnings(self, msg):
        self.insilicova_warnings = msg

    def update_insilicova_errors(self, msg):
        self.insilicova_errors = msg

    def stop_insilicova(self):
        self.insilicova_ctrl["break"] = True
        self.btn_insilicova_stop.setEnabled(False)

    def update_insilicova_results(self, new_insilicova_results):
        self.insilicova_results = new_insilicova_results

    def run_interva_dialog(self):
        self.interva_dialog = InterVADialog(self, self.hiv, self.malaria)
        self.interva_dialog.exec()

    def update_interva_hiv(self, updated_hiv):
        self.hiv = updated_hiv

    def update_interva_malaria(self, updated_malaria):
        self.malaria = updated_malaria

    def run_interva(self):
        self.interva_ctrl["break"] = False
        self.btn_interva_run.setEnabled(False)
        self.btn_load_data.setEnabled(False)
        self.btn_pycrossva.setEnabled(False)
        self.combo_data_id_col.setEnabled(False)
        self.btn_data_format.setEnabled(False)
        self.btn_edit_data.setEnabled(False)
        self.btn_save_interva_log.setEnabled(False)
        self.btn_interva_run.setEnabled(False)
        self.btn_interva_options.setEnabled(False)
        if self.pycrossva_data is None:
            alert = QMessageBox()
            alert.setWindowTitle("openVA App")
            alert.setText(
                "Data need to be loaded and/or prepared with pyCrossVA.")
            alert.exec()
            self.btn_interva_run.setEnabled(True)
            self.btn_load_data.setEnabled(True)
            self.btn_pycrossva.setEnabled(True)
            self.combo_data_id_col.setEnabled(True)
            self.btn_data_format.setEnabled(True)
            self.btn_edit_data.setEnabled(True)
            self.btn_save_interva_log.setEnabled(True)
            self.btn_interva_options.setEnabled(True)
        else:
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
            self.interva_log = None
            self.interva_results = None
            self.interva_tmp_dir = tempfile.TemporaryDirectory()
            self.interva_thread = QThread()
            self.interva_worker = InterVAWorker(
                self.pycrossva_data,
                hiv=self.hiv[0],
                malaria=self.malaria[0],
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
                self.parent.update_interva_results)
            self.interva_worker.finished.connect(
                lambda: self.parent.update_interva_tmp_dir(
                    self.interva_tmp_dir))
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
                lambda: self.btn_interva_options.setEnabled(True))
            self.interva_thread.finished.connect(
                lambda: self.btn_save_interva_log.setEnabled(True))
            self.interva_thread.finished.connect(
                lambda: self.btn_pycrossva.setEnabled(True))
            self.interva_thread.finished.connect(
                lambda: self.combo_data_id_col.setEnabled(True))
            self.interva_thread.finished.connect(
                lambda: self.btn_data_format.setEnabled(True))
            self.interva_thread.finished.connect(
                lambda: self.btn_edit_data.setEnabled(True))
        #     iv5out.run()
        #     self.interva_log = "ready"
        #     if iv5out.out["VA5"] is None:
        #         self.label_interva_progress.setText(
        #             "Data do not have any valid VA records (no results "
        #             "available).\nPlease reload data in the expected format.")
        #     else:
        #         self.interva_results = iv5out
        #         self.label_interva_progress.setText(
        #             "InterVA5 results are ready")
        # self.btn_interva_run.setEnabled(True)

    def update_interva_progress(self, n):
        self.interva_pbar.setValue(n)

    def update_interva_progress_label(self, msg):
        self.label_interva_progress.setText(msg)

    def update_interva_log(self, msg):
        self.interva_log = msg

    def stop_interva(self):
        self.interva_ctrl["break"] = True
        self.btn_interva_stop.setEnabled(False)

    # def run_smartva_dialog(self):
    #     # self.smartva_dialog = SmartVADialog(self,
    #     #                                     self.smartva_country,
    #     #                                     self.smartva_hiv,
    #     #                                     self.smartva_malaria,
    #     #                                     self.smartva_hce,
    #     #                                     self.smartva_freetext)
    #     # self.smartva_dialog.exec()
    #     alert = QMessageBox()
    #     alert.setWindowTitle("openVA App")
    #     alert.setText("SmartVA is not available (it is based on Python 2" +
    #                   "which is no longer supported by the Python Software " +
    #                   "Foundation).  It will be included when a version " +
    #                   "based on Python 3 is released.")
    #     alert.exec()
        
    # def run_smartva(self):
    #     alert = QMessageBox()
    #     alert.setWindowTitle("openVA App")
    #     alert.setText("SmartVA is not available (it is based on Python 2" +
    #                   "which is no longer supported by the Python Software " +
    #                   "Foundation).  It will be included when a version " +
    #                   "based on Python 3 is released.")
    #     alert.exec()

    # def update_smartva_country(self, updated_country):
    #     self.smartva_country = updated_country
    #
    # def update_smartva_hiv(self, updated_hiv):
    #     self.smartva_hiv = updated_hiv
    #
    # def update_smartva_malaria(self, updated_malaria):
    #     self.smartva_malaria = updated_malaria
    #
    # def update_smartva_hce(self, updated_hce):
    #     self.smartva_hce = updated_hce
    #
    # def update_smartva_freetext(self, updated_freetext):
    #     self.smartva_freetext = updated_freetext

    def set_data_id_col(self, id_col):
        id_col_check = [i for i in self.load_window.data[0] if i == id_col]
        if len(id_col_check) > 1:
            alert = QMessageBox()
            alert.setWindowTitle("openVA App")
            alert.setIcon(QMessageBox.Warning)
            alert.setText(
                f"There are multiple columns named {id_col}."
                "Please choose a unique column name or change the duplicate "
                "column names to unique names.")
            alert.exec()
            if self.prev_data_id_col is None:
                prev_index = self.combo_data_id_col.findText(
                    "no ID column")
            else:
                prev_index = self.combo_data_id_col.findText(
                    self.prev_data_id_col)
            self.combo_data_id_col.blockSignals(True)
            self.combo_data_id_col.setCurrentIndex(prev_index)
            self.combo_data_id_col.blockSignals(False)
        elif self.pycrossva_data is not None:
            qmbox_yn = QMessageBox()
            msg = ("You have created pyCrossVA data and/or COD results.\n\n"
                   "Changing the column ID will DELETE these results.\n\n"
                   "Do you want to change the ID?")
            ans = qmbox_yn.question(self, "", msg, qmbox_yn.Yes | qmbox_yn.No)
            if ans == qmbox_yn.Yes:
                self.data_id_col = id_col
                self.parent.results.original_data_id = id_col
                self.prev_data_id_col = id_col
                self._reset_results()
                if self.data_id_col not in (None, "no ID column"):
                    df = DataFrame(self.load_window.data[1:],
                                   columns=self.load_window.data[0])
                    if df[self.data_id_col].is_unique is False:
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
            self.parent.results.original_data_id = id_col
            self.prev_data_id_col = id_col
            if self.data_id_col not in (None, "no ID column"):
                df = DataFrame(self.load_window.data[1:],
                               columns=self.load_window.data[0])
                if df[self.data_id_col].is_unique is False:
                    alert = QMessageBox()
                    alert.setWindowTitle("openVA App")
                    alert.setIcon(QMessageBox.Warning)
                    alert.setText(
                        "ID column does not have a unique value for every row")
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
                "\n\n (convergence can be achieved by increasing the number of"
                " simulations)")
        alert.exec()

    def save_insilicova_log(self):
        errors = self.insilicova_errors
        log = self.insilicova_errors
        warnings = self.insilicova_warnings
        if log is None:
            alert = QMessageBox()
            alert.setWindowTitle("openVA App")
            alert.setText(
                "No results available.  Please load data in the expected "
                "format and/or run a VA algorithm.")
            alert.exec()
        else:
            log_file_name = "insilicova_log.txt"
            log_file_name = os.path.join(self.working_dir,
                                         log_file_name)
            path = QFileDialog.getSaveFileName(self,
                                               "Save log (txt)",
                                               log_file_name,
                                               "Text Files (*.txt)")
            if path != ("", ""):
                try:
                    with open(path[0], "w") as f_out:
                        f_out.write(
                            "Log file from InSilicoVA")
                        if len(errors) > 0:
                            f_out.write(
                                "\n\nThe following records are incomplete "
                                "and excluded from further processing\n\n")
                            errors_list = [str(k) + " - " + i for k, v in
                                           errors.items() for i in v]
                            f_out.write("\n".join(errors_list))
                        # if isinstance(warnings, list):
                        if len(warnings) > 1:
                            f_out.write("\n \n first pass \n \n")
                            f_out.write("\n".join(warnings["first_pass"]))
                            f_out.write("\n \n second pass \n \n")
                            f_out.write("\n".join(warnings["second_pass"]))
                        else:
                            f_out.write("\n\n" + warnings)
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

    def save_interva_log(self):
        log = self.interva_log
        if log is None:
            alert = QMessageBox()
            alert.setWindowTitle("openVA App")
            alert.setText(
                "No results available.  Please load data in the expected "
                "format and/or run a VA algorithm.")
            alert.exec()
        else:
            log_file_name = "interva_log.txt"
            log_file_name = os.path.join(self.working_dir,
                                         log_file_name)
            path = QFileDialog.getSaveFileName(self,
                                               "Save log (txt)",
                                               log_file_name,
                                               "Text Files (*.txt)")
            if path != ("", ""):
                try:
                    tmp_log = os.path.join(self.interva_tmp_dir.name,
                                           "errorlogV5.txt")
                    shutil.copyfile(tmp_log, path[0])
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

    def _reset_results(self):
        self.pycrossva_data = None
        self.label_pycrossva_status.setText("(need to run pyCrossVA)")
        self.insilicova_results = None
        self.parent.results.insilicova_results = None
        self.label_insilicova_progress.setText("")
        self.insilicova_pbar.setValue(0)
        self.insilicova_warnings = None
        self.insilicova_errors = None
        self.interva_results = None
        self.parent.results.interva_results = None
        self.interva_log = None
        self.label_interva_progress.setText("")
        self.interva_pbar.setValue(0)


class PyCrossVADialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.label = QLabel("")
        self.setWindowTitle("openVA: pyCrossVA message")
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok)
        self.button_box.accepted.connect(self.accept)
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.button_box)
        self.setLayout(self.layout)

    def set_text(self, text):
        self.label.setText(text)


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
