# -*- coding: utf-8 -*-

"""
pyopenva.main
~~~~~~~~~~~~~~
This module creates user interface for the app.
"""
from PyQt5.QtWidgets import QApplication
import sys
from mode import Mode
from command_center import CommandCenter
from results import Results


class WindowManager:

    def __init__(self):
        super().__init__()
        self.mode = Mode()
        self.command_center = CommandCenter()
        self.results = Results()

        self.mode.btn_efficient.clicked.connect(self.show_efficient)
        self.mode.btn_advanced.clicked.connect(self.show_command_center)

        self.command_center.btn_user_mode.clicked.connect(self.show_mode)
        self.command_center.btn_algorithm_results.clicked.connect(
            self.show_results)

        self.results.btn_go_to_command_center.clicked.connect(
            self.results_to_command_center)

        self.results.btn_go_to_mode.clicked.connect(
        self.results_to_mode)

        self.mode.show()

    def show_efficient(self):
        pass

    def show_command_center(self):
        self.mode.hide()
        self.command_center.show()

    def show_mode(self):
        self.command_center.hide()
        self.mode.show()

    def show_results(self):
        self.command_center.hide()
        self.results.show()

    def results_to_command_center(self):
        self.results.hide()
        self.command_center.show()

    def results_to_mode(self):
        self.results.hide()
        self.mode.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    gui = WindowManager()
    sys.exit(app.exec_())
