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
        openva_pixmap = QPixmap("../icons/openva-logo.png")
        self.logo_openva = QLabel()
        self.logo_openva.setPixmap(
            openva_pixmap.scaled(192, 192,
                                 Qt.KeepAspectRatio,
                                 Qt.SmoothTransformation))
        self.label_openva = QLabel("openVA App    ")
        self.label_openva.setFont(QFont("Arial", 48, QFont.Bold))
        d4h_pixmap = QPixmap("../icons/d4h.jpg")
        self.logo_d4h = QLabel()
        self.logo_d4h.setPixmap(
            d4h_pixmap.scaled(192, 192,
                              Qt.KeepAspectRatio,
                              Qt.SmoothTransformation))
        vital_strategies_pixmap = QPixmap("../icons/vital_strategies.png")
        self.logo_vital_strategies = QLabel()
        self.logo_vital_strategies.setPixmap(
            vital_strategies_pixmap.scaled(128, 128,
                                           Qt.KeepAspectRatio,
                                           Qt.SmoothTransformation))
        self.btn_efficient = QPushButton("Start")
        self.btn_advanced = QPushButton("Advanced Mode")

        self.grid = QGridLayout(self)
        self.grid.addWidget(self.logo_openva, 0, 0)
        self.grid.addWidget(self.label_openva, 0, 2)
        self.grid.addWidget(self.btn_efficient, 1, 2)
        self.grid.addWidget(self.btn_advanced, 2, 2)
        self.grid.addWidget(self.logo_d4h, 3, 0)
        self.grid.addWidget(self.logo_vital_strategies, 3, 1)
        # self.grid.addWidget(self.logo_openva, 3, 0)
        # self.grid.addWidget(self.label_openva, 0, 1)
        # self.grid.addWidget(self.btn_efficient, 1, 1)
        # self.grid.addWidget(self.btn_advanced, 2, 1)
        # self.grid.addWidget(self.logo_d4h, 3, 1)
        # self.grid.addWidget(self.logo_vital_strategies, 3, 2)
        # self.grid.addWidget(self.logo_openva, 0, 0)
        # #self.grid.addWidget(self.label_openva, 0, 1)
        # self.grid.addWidget(self.btn_efficient, 0, 1)
        # self.grid.addWidget(self.btn_advanced, 0, 2)
        # self.grid.addWidget(self.logo_d4h, 3, 0)
        # self.grid.addWidget(self.logo_vital_strategies, 3, 2)

