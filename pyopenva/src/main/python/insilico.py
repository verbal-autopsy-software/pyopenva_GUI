# -*- coding: utf-8 -*-

"""
pyopenva.insilico
~~~~~~~~~~~~~~
This module creates a dialog for setting InSilicoVA options.
"""

from PyQt5.QtWidgets import (QDialog, QGroupBox, QSlider, QLabel, QVBoxLayout)
from PyQt5.QtCore import Qt


class InSilicoDialog(QDialog):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("InSilicoVA Options")
        self.n_iterations = 3000
        self.groupbox_n_iterations = QGroupBox('Number of Iterations')
        self.n_iterations_slider = QSlider(Qt.Horizontal,
                                           self.groupbox_n_iterations)
        self.n_iterations_label = QLabel('value: 3000')
        self.setup_n_iterations_groupbox()

        # self.layout = QVBoxLayout()
        # message = QLabel("Something happened, is that OK?")
        # self.layout.addWidget(message)
        # self.layout.addWidget(self.buttonBox)
        # self.setLayout(self.layout)

    def setup_n_iterations_groupbox(self):
        self.n_iterations_slider.setRange(1000, 10000)
        self.n_iterations_slider.setValue(3000)
        self.n_iterations_slider.valueChanged.connect(self.set_n_iterations)
        layout = QVBoxLayout()
        layout.addWidget(self.n_iterations_slider)
        layout.addWidget(self.n_iterations_label)
        layout.addStretch(1)
        self.groupbox_n_iterations.setLayout(layout)

    def set_n_iterations(self):
        self.n_iterations = self.n_iterations_slider.value()
        self.n_iterations_label.setText(f'value: {self.n_iterations}')
