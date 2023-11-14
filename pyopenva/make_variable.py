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

        self.lab = QLabel("here is something cool")

        self.btn_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.btn_box.accepted.connect(self.accept)
        self.btn_box.rejected.connect(self.reject)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.lab)
        self.layout.addWidget(self.btn_box)
        self.setLayout(self.layout)
