# -*- coding: utf-8 -*-

"""
pyopenva.mode
~~~~~~~~~~~~~~
This module creates the welcome screen where users select the mode.
"""
from PyQt5.QtWidgets import (QWidget, QLabel, QPushButton, QGridLayout)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPixmap


class Mode(QWidget):
    def __init__(self):
        super().__init__()
        self.setGeometry(400, 400, 500, 400)

        #self.setWindowTitle("openVA GUI")
        openva_pixmap = QPixmap("../icons/openva-logo.png")
        self.label_logo = QLabel()
        self.label_logo.setPixmap(
            openva_pixmap.scaled(96, 96,
                                 Qt.KeepAspectRatio,
                                 Qt.SmoothTransformation))
        self.label_openva = QLabel("openVA GUI App")
        self.label_openva.setFont(QFont("Arial", 48, QFont.Bold))
        self.grid = QGridLayout(self)
        self.grid.addWidget(self.label_logo, 0, 0)
        self.grid.addWidget(self.label_openva, 0, 2)

        self.btn_efficient = QPushButton("Efficient Mode")
        self.grid.addWidget(self.btn_efficient, 2, 1)

        self.btn_advanced = QPushButton("Advanced Mode")
        self.grid.addWidget(self.btn_advanced, 3, 1)
