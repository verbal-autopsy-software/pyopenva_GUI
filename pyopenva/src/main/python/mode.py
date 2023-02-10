# -*- coding: utf-8 -*-

"""
pyopenva.mode
~~~~~~~~~~~~~~
This module creates the welcome screen where users select the mode.
"""
from PyQt5.QtWidgets import (QHBoxLayout, QLabel, QPushButton, QWidget,
                             QVBoxLayout)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPixmap
import os


class Mode(QWidget):
    def __init__(self):
        super().__init__()
        openva_pixmap = QPixmap(
            os.path.join(os.path.dirname(__file__), 
            "openva-logo.png"))
        self.logo_openva = QLabel()
        self.logo_openva.setPixmap(
            openva_pixmap.scaled(160, 160,
                                 Qt.KeepAspectRatio,
                                 Qt.SmoothTransformation))
        self.label_openva = QLabel("openVA App")
        self.label_openva.setFont(QFont("Arial", 36, QFont.Bold))
        d4h_pixmap = QPixmap(
            os.path.join(os.path.dirname(__file__),
            "logo-d4h.png"))
            #"d4h.png"))
        self.logo_d4h = QLabel()
        self.logo_d4h.setPixmap(
            d4h_pixmap.scaled(192, 192,
                              Qt.KeepAspectRatio,
                              Qt.SmoothTransformation))
        vital_strategies_pixmap = QPixmap(
            os.path.join(os.path.dirname(__file__),
            "vital_strategies.png"))
        self.logo_vital_strategies = QLabel()
        self.logo_vital_strategies.setPixmap(
            vital_strategies_pixmap.scaled(128, 128,
                                           Qt.KeepAspectRatio,
                                           Qt.SmoothTransformation))
        self.btn_efficient = QPushButton("Start")
        self.btn_efficient.setMaximumWidth(250)
        self.btn_advanced = QPushButton("Advanced Mode")
        self.btn_advanced.setMaximumWidth(250)
        self.vbox = QVBoxLayout()
        hbox = QHBoxLayout()
        hbox.addWidget(self.logo_openva)
        hbox.addWidget(self.label_openva)
        self.vbox.addLayout(hbox)
        #self.vbox.insertSpacing(1, 25)
        hbox_btn_eff = QHBoxLayout()
        hbox_btn_eff.addWidget(self.btn_efficient)
        self.vbox.addLayout(hbox_btn_eff)
        hbox_btn_adv = QHBoxLayout()
        hbox_btn_adv.addWidget(self.btn_advanced)
        self.vbox.addLayout(hbox_btn_adv)
        self.vbox.insertSpacing(4, 75)
        hbox_low = QHBoxLayout()
        hbox_low.addWidget(self.logo_d4h)
        hbox_low.addWidget(self.logo_vital_strategies)
        hbox_low.insertSpacing(1, 50)
        self.vbox.addLayout(hbox_low)
        self.vbox.setAlignment(Qt.AlignCenter)
        self.setLayout(self.vbox)
