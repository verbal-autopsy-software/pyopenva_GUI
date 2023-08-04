# -*- coding: utf-8 -*-

"""
pyopenva.insilicova
~~~~~~~~~~~~~~
This module creates a dialog for setting InSilicoVA options.
"""

from PyQt5.QtWidgets import (QCheckBox, QDialog, QDialogButtonBox,
                             QGroupBox, QLabel, QSlider,
                             QSpinBox, QVBoxLayout)
from PyQt5.QtCore import Qt


class InSilicoVADialog(QDialog):

    def __init__(self, parent=None, seed=None, auto_extend=True,
                 jump_scale=0.1, n_iterations=3000):
        super(InSilicoVADialog, self).__init__(parent=parent)
        self.setWindowTitle("InSilicoVA Options")
        self.auto_extend = auto_extend
        self.jump_scale = jump_scale
        self.n_iterations = n_iterations
        self.seed = seed
        self.n_burn_in = round(n_iterations/2)
        self.groupbox_n_iterations = QGroupBox("Number of Iterations")
        self.n_iterations_slider = QSlider(Qt.Horizontal,
                                           self.groupbox_n_iterations)
        self.n_iterations_label = QLabel(f"value: {self.n_iterations}")
        self.setup_n_iterations_groupbox()

        self.btn_auto_extend = QCheckBox("Automatically increase chain \n"
                                         "length until convergence")
        self.btn_auto_extend.setChecked(self.auto_extend)
        self.btn_auto_extend.toggled.connect(self.set_auto_extend)

        self.groupbox_jump_scale = QGroupBox("Jump Scale")
        self.jump_scale_slider = QSlider(Qt.Horizontal,
                                         self.groupbox_jump_scale)
        self.jump_scale_label = QLabel(f"value: {self.jump_scale}")
        self.setup_jump_scale_groupbox()

        self.seed_qspin_label = QLabel("Set Seed (1 to 2000)")
        self.seed_qspin = QSpinBox()
        self.seed_qspin.setRange(1, 2000)
        self.seed_qspin.setValue(self.seed)
        self.seed_qspin.valueChanged.connect(self.set_seed)

        self.btn_box = QDialogButtonBox(QDialogButtonBox.Cancel |
                                        QDialogButtonBox.Ok)
        self.btn_box.accepted.connect(self.accept)
        self.btn_box.accepted.connect(
            lambda:
            self.parent().update_insilicova_n_iterations(self.n_iterations))
        self.btn_box.accepted.connect(
            lambda:
            self.parent().update_insilicova_jump_scale(self.jump_scale))
        self.btn_box.accepted.connect(
            lambda:
            self.parent().update_insilicova_auto_extend(self.auto_extend))
        self.btn_box.accepted.connect(
            lambda:
            self.parent().update_insilicova_seed(self.seed))
        self.btn_box.rejected.connect(self.reject)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.groupbox_n_iterations)
        self.layout.addWidget(self.btn_auto_extend)
        self.layout.addWidget(self.groupbox_jump_scale)
        self.layout.addWidget(self.seed_qspin_label)
        self.layout.addWidget(self.seed_qspin)
        self.layout.addWidget(self.btn_box)
        self.setLayout(self.layout)

    def setup_n_iterations_groupbox(self):
        # self.n_iterations_slider.setRange(400, 10000)
        self.n_iterations_slider.setRange(4, 100)
        self.n_iterations_slider.setValue(int(self.n_iterations/100))
        self.n_iterations_slider.valueChanged.connect(self.set_n_iterations)
        layout = QVBoxLayout()
        layout.addWidget(self.n_iterations_slider)
        layout.addWidget(self.n_iterations_label)
        layout.addStretch(1)
        self.groupbox_n_iterations.setLayout(layout)

    def setup_jump_scale_groupbox(self):
        self.jump_scale_slider.setRange(1, 2000)
        self.jump_scale_slider.setSingleStep(1)
        self.jump_scale_slider.setValue(int(self.jump_scale * 1000))
        self.jump_scale_slider.valueChanged.connect(self.set_jump_scale)
        layout = QVBoxLayout()
        layout.addWidget(self.jump_scale_slider)
        layout.addWidget(self.jump_scale_label)
        layout.addStretch(1)
        self.groupbox_jump_scale.setLayout(layout)

    def set_n_iterations(self):
        self.n_iterations = self.n_iterations_slider.value() * 100
        self.n_iterations_label.setText(f'value: {self.n_iterations}')

    def set_jump_scale(self):
        self.jump_scale = self.jump_scale_slider.value()/1000
        self.jump_scale_label.setText(f'value: {self.jump_scale}')

    def set_auto_extend(self):
        self.auto_extend = self.btn_auto_extend.isChecked()

    def set_seed(self, new_seed_value):
        self.seed = new_seed_value
