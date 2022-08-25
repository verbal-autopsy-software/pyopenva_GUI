# -*- coding: utf-8 -*-

"""
pyopenva.main
~~~~~~~~~~~~~~
This module creates user interface for the app.
"""
from PyQt5.QtWidgets import QMainWindow, QWidget, QApplication, QStackedLayout
import sys
from efficient import Efficient
from mode import Mode
from command_center import CommandCenter
from results import Results


class WindowManager(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setGeometry(350, 350, 800, 600)
        self.setWindowTitle("Select Mode")
        self.efficient = Efficient()
        self.mode = Mode()
        self.command_center = CommandCenter()
        self.results = Results()

        self.stacked_layout = QStackedLayout()
        self.stacked_layout.addWidget(self.mode)
        self.stacked_layout.addWidget(self.command_center)
        self.stacked_layout.addWidget(self.results)
        self.stacked_layout.addWidget(self.efficient)
        self.stacked_layout.setCurrentIndex(0)
        widget = QWidget()
        widget.setLayout(self.stacked_layout)
        self.setCentralWidget(widget)

        # window management
        self.efficient.btn_go_to_mode.clicked.connect(
            self.show_mode)

        self.mode.btn_efficient.clicked.connect(self.show_efficient)
        self.mode.btn_advanced.clicked.connect(self.show_command_center)

        self.command_center.btn_user_mode.clicked.connect(self.show_mode)
        self.command_center.btn_algorithm_results.clicked.connect(
            self.show_results)

        self.results.btn_go_to_command_center.clicked.connect(
            self.show_command_center)

        self.results.btn_go_to_mode.clicked.connect(
            self.show_mode)

        # update results
        self.command_center.btn_interva_run.clicked.connect(
            lambda: self.update_interva_results(
                self.command_center.interva_results))

        self.command_center.btn_insilico_run.clicked.connect(
            lambda: self.update_insilico_results(
                self.command_center.insilico_results))

        self.command_center.btn_smartva_run.clicked.connect(
            lambda: self.update_smartva_results(
                self.command_center.smartva_results))

    def show_efficient(self):
        self.stacked_layout.setCurrentIndex(3)
        self.setWindowTitle("Efficient Mode")

    def show_command_center(self):
        self.stacked_layout.setCurrentIndex(1)
        self.setWindowTitle("Command Center")

    def show_mode(self):
        self.stacked_layout.setCurrentIndex(0)
        self.setWindowTitle("Select Mode")

    def show_results(self):
        self.stacked_layout.setCurrentIndex(2)
        self.setWindowTitle("Results")

    def update_interva_results(self, new_results):
        self.results.update_interva(new_results)

    def update_insilico_results(self, new_results):
        self.results.update_insilico(new_results)

    def update_smartva_results(self, new_results):
        self.results.update_smartva(new_results)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    gui = WindowManager()
    gui.show()
    sys.exit(app.exec_())
