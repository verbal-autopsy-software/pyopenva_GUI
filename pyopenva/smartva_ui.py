# -*- coding: utf-8 -*-

"""
pyopenva.smartva
~~~~~~~~~~~~~~
This module creates a dialog for setting SmartVA options.
"""

from pyopenva.data import COUNTRIES
from PyQt5.QtWidgets import (QComboBox, QDialog, QDialogButtonBox,
                             QLabel, QVBoxLayout)


class SmartVADialog(QDialog):

    def __init__(self, parent=None, country="Unknown", hiv="True",
                 malaria="True", hce="True", freetext="True"):
        super(SmartVADialog, self).__init__(parent=parent)
        self.setWindowTitle("SmartVA Options")
        self.smartva_country = country
        self.smartva_hiv = hiv
        self.smartva_malaria = malaria
        self.smartva_hce = hce
        self.smartva_freetext = freetext

        country_option_set = COUNTRIES
        self.combo_country_label = QLabel("Data origin country")
        self.combo_country = QComboBox()
        self.combo_country.addItems(country_option_set)
        self.combo_country.setCurrentIndex(
            country_option_set.index(self.smartva_country))
        self.combo_country.currentTextChanged.connect(self.set_country)
        option_set = ["True", "False"]
        self.combo_hiv_label = QLabel("Data are from an HIV region")
        self.combo_hiv = QComboBox()
        self.combo_hiv.addItems(option_set)
        self.combo_hiv.setCurrentIndex(option_set.index(self.smartva_hiv))
        self.combo_hiv.currentTextChanged.connect(self.set_hiv)

        self.combo_malaria_label = QLabel("Data are from a Malaria region")
        self.combo_malaria = QComboBox()
        self.combo_malaria.addItems(option_set)
        self.combo_malaria.setCurrentIndex(
            option_set.index(self.smartva_malaria))
        self.combo_malaria.currentTextChanged.connect(self.set_malaria)

        self.combo_hce_label = \
            QLabel("Use Health Care Experience (HCE) variables")
        self.combo_hce = QComboBox()
        self.combo_hce.addItems(option_set)
        self.combo_hce.setCurrentIndex(
            option_set.index(self.smartva_hce))
        self.combo_hce.currentTextChanged.connect(self.set_hce)

        self.combo_freetext_label = QLabel("Use 'free text' variables")
        self.combo_freetext = QComboBox()
        self.combo_freetext.addItems(option_set)
        self.combo_freetext.setCurrentIndex(
            option_set.index(self.smartva_freetext))
        self.combo_freetext.currentTextChanged.connect(self.set_freetext)

        self.btn_box = QDialogButtonBox(QDialogButtonBox.Cancel |
                                        QDialogButtonBox.Ok)
        self.btn_box.accepted.connect(self.accept)
        self.btn_box.accepted.connect(
            lambda:
            self.parent().update_smartva_country(self.smartva_country))
        self.btn_box.rejected.connect(self.reject)
        self.btn_box.accepted.connect(
            lambda:
            self.parent().update_smartva_hiv(self.smartva_hiv))
        self.btn_box.accepted.connect(
            lambda:
            self.parent().update_smartva_malaria(self.smartva_malaria))
        self.btn_box.rejected.connect(self.reject)
        self.btn_box.accepted.connect(
            lambda:
            self.parent().update_smartva_hce(self.smartva_hce))
        self.btn_box.rejected.connect(self.reject)
        self.btn_box.accepted.connect(
            lambda:
            self.parent().update_smartva_freetext(self.smartva_freetext))
        self.btn_box.rejected.connect(self.reject)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.combo_country_label)
        self.layout.addWidget(self.combo_country)
        self.layout.addWidget(self.combo_hiv_label)
        self.layout.addWidget(self.combo_hiv)
        self.layout.addWidget(self.combo_malaria_label)
        self.layout.addWidget(self.combo_malaria)
        self.layout.addWidget(self.combo_hce_label)
        self.layout.addWidget(self.combo_hce)
        self.layout.addWidget(self.combo_freetext_label)
        self.layout.addWidget(self.combo_freetext)
        self.layout.addWidget(self.btn_box)
        self.setLayout(self.layout)

    def set_country(self, updated_country):
        self.smartva_country = updated_country

    def set_hiv(self, updated_hiv):
        self.smartva_hiv = updated_hiv

    def set_malaria(self, updated_malaria):
        self.smartva_malaria = updated_malaria

    def set_hce(self, updated_hce):
        self.smartva_hce = updated_hce

    def set_freetext(self, updated_freetext):
        self.smartva_freetext = updated_freetext
