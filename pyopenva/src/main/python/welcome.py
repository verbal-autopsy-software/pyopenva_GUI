from fbs_runtime.application_context.PyQt5 import ApplicationContext
from PyQt5.QtWidgets import (QWidget, QLabel, QPushButton, QFileDialog,
                             QGridLayout, QComboBox, QMessageBox, QGroupBox,
                             QVBoxLayout, QSlider, QProgressDialog)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPixmap
import sys
import os

class WelcomeWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('pyopenva GUI')
        openva_pixmap = QPixmap('src/main/icons/openva-logo.png')
        self.label_openva = QLabel()
        self.label_openva.setPixmap(openva_pixmap.scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation))

        self.resize(500, 500)
