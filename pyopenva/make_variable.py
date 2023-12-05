# -*- coding: utf-8 -*-

"""
pyopenva.make_variable
~~~~~~~~~~~~~~
This module creates displays for the algorithm results.
"""
from PyQt5.QtWidgets import (QApplication, QCheckBox, QComboBox, QDialog,
                             QDialogButtonBox,
                             QLabel, QMessageBox, QPushButton, QTableView,
                             QHBoxLayout, QVBoxLayout)


class MakeVariable(QDialog):

    def __init__(self, parent=None):
        super(MakeVariable, self).__init__(parent=parent)
        self.setWindowTitle("openVA: Create a New Variable")
        self.prev_data_var_name = None
        self.data_var_name = None
        self.data_var_type = None

        label_select_var = QLabel("Select variable for recoding")
        self.combo_select_var = QComboBox()
        self.set_variable_names()
        self.combo_select_var.currentTextChanged.connect(
            self.set_select_var)

        self.btn_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.btn_box.accepted.connect(self.accept)
        self.btn_box.rejected.connect(self.reject)

        self.layout = QVBoxLayout()
        self.layout.addWidget(label_select_var)
        self.layout.addWidget(self.combo_select_var)
        self.layout.addWidget(self.btn_box)
        self.setLayout(self.layout)

    def set_variable_names(self):
        data_col_names = self.parent().original_data.columns
        data_col_names = [i.replace(".", "-") for i in data_col_names]
        data_col_names = [i.split("-")[-1] for i in data_col_names]
        self.combo_select_var.blockSignals(True)
        self.combo_select_var.addItems(
            ["no variable selected"] + data_col_names
        )
        self.combo_select_var.blockSignals(False)
        self.combo_select_var.setCurrentIndex(0)
    
    def set_select_var(self, var_name):
        var_name_check = [i for i in self.parent().original_data.columns if i == var_name]
        if len(var_name_check) > 1:
            alert = QMessageBox()
            alert.setWindowTitle("openVA App")
            alert.setIcon(QMessageBox.Warning)
            alert.setText(
                f"There are multiple columns named {var_name}."
                "Please choose a unique column name or change the duplicate "
                "column names to unique names.")
            alert.exec()
            if self.prev_data_var_name is None:
                prev_index = self.combo_select_var.findText(
                    "no variable selected")
            else:
                prev_index = self.combo_select_var.findText(
                    self.prev_data_var_name)
            self.combo_select_var.blockSignals(True)
            self.combo_select_var.setCurrentIndex(prev_index)
            self.combo_select_var.blockSignals(False)
        else:
            self.data_var_name = var_name
            self.prev_data_var_name = var_name
            # try pd.to_numeric(variable)
