# -*- coding: utf-8 -*-

"""
pyopenva.interva
~~~~~~~~~~~~~~
This module creates a dialog for setting InterVA options.
"""

from PyQt5.QtWidgets import (QComboBox, QDialog, QDialogButtonBox,
                             QLabel, QVBoxLayout)


class InterVADialog(QDialog):

    def __init__(self, parent=None, hiv="low", malaria="low"):
        super(InterVADialog, self).__init__(parent=parent)
        self.setWindowTitle("InterVA Options")
        self.hiv = hiv
        self.malaria = malaria

        option_set = ["high", "low", "very low"]
        self.combo_hiv_label = QLabel("HIV")
        self.combo_hiv = QComboBox()
        self.combo_hiv.addItems(option_set)
        self.combo_hiv.setCurrentIndex(option_set.index(self.hiv))
        self.combo_hiv.currentTextChanged.connect(self.set_hiv)

        self.combo_malaria_label = QLabel("Malaria")
        self.combo_malaria = QComboBox()
        self.combo_malaria.addItems(option_set)
        self.combo_malaria.setCurrentIndex(option_set.index(self.malaria))
        self.combo_malaria.currentTextChanged.connect(self.set_malaria)

        self.btn_box = QDialogButtonBox(QDialogButtonBox.Cancel |
                                        QDialogButtonBox.Ok)
        self.btn_box.accepted.connect(self.accept)
        self.btn_box.accepted.connect(
            lambda:
            self.parent().update_interva_hiv(self.hiv))
        self.btn_box.accepted.connect(
            lambda:
            self.parent().update_interva_malaria(self.malaria))
        self.btn_box.rejected.connect(self.reject)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.combo_hiv_label)
        self.layout.addWidget(self.combo_hiv)
        self.layout.addWidget(self.combo_malaria_label)
        self.layout.addWidget(self.combo_malaria)
        self.layout.addWidget(self.btn_box)
        self.setLayout(self.layout)

    def set_hiv(self, updated_hiv):
        self.hiv = updated_hiv

    def set_malaria(self, updated_malaria):
        self.malaria = updated_malaria
