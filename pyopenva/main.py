# -*- coding: utf-8 -*-

"""
pyopenva.main
~~~~~~~~~~~~~~
This module creates user interface for the app.
"""
from PyQt5.QtWidgets import (QApplication, QMainWindow, QMessageBox,
                             QStackedLayout, QWidget)
import sys
from pyopenva.efficient import Efficient
from pyopenva.mode import Mode
from pyopenva.command_center import CommandCenter
from pyopenva.results import Results


class WindowManager(QMainWindow):

    def __init__(self):
        super().__init__()
        #self.setGeometry(200, 200, 500, 300)
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
        self.mode.btn_efficient.clicked.connect(self.show_efficient)
        self.mode.btn_advanced.clicked.connect(self.show_command_center)

        self.command_center.btn_user_mode.clicked.connect(self.show_mode)
        self.command_center.btn_algorithm_results.clicked.connect(
            self.show_results)

        self.results.btn_go_to_command_center.clicked.connect(
            self.show_command_center)

        self.results.btn_go_to_mode.clicked.connect(
            self.show_mode)

        # TODO: make this more efficient (it works, but probably a lot of
        #       redundancies!
        self.efficient.btn_go_to_mode.clicked.connect(
            self.show_mode)

        self.efficient.btn_go_to_data_page.clicked.connect(
            self.show_efficient_data_page)

        self.efficient.btn_algorithm.clicked.connect(
            self.show_efficient_select_algorithm_page)

        self.efficient.btn_insilicova.clicked.connect(
            self.show_efficient_insilicova_page)

        self.efficient.btn_interva.clicked.connect(
            self.show_efficient_interva_page)

        self.efficient.btn_smartva.clicked.connect(
            self.show_efficient_smartva_page)

        self.efficient.btn_insilicova_to_select_algorithm.clicked.connect(
            self.show_efficient_select_algorithm_from_algorithm)

        self.efficient.btn_interva_to_select_algorithm.clicked.connect(
            self.show_efficient_select_algorithm_from_algorithm)

        self.efficient.btn_smartva_to_select_algorithm.clicked.connect(
            self.show_efficient_select_algorithm_from_algorithm)

        self.efficient.btn_go_to_results_page.clicked.connect(
            self.show_efficient_results_page)

        self.efficient.btn_results_to_algorithm.clicked.connect(
            self.show_efficient_algorithm
        )

        # update results
        self.command_center.btn_interva_run.clicked.connect(
            lambda: self.update_interva_results(
                self.command_center.interva_results,
                self.command_center.interva_tmp_dir))

        self.command_center.btn_insilicova_run.clicked.connect(
            lambda: self.update_insilicova_results(
                self.command_center.insilicova_results))

        self.command_center.btn_smartva_run.clicked.connect(
            lambda: self.update_smartva_results(
                self.command_center.smartva_results))

        # self.results.btn_save_insilicova_log.clicked.connect()

    def show_efficient(self):
        self.stacked_layout.setCurrentIndex(3)
        self.setWindowTitle("openVA App: load and prepare data")

    def show_command_center(self):
        self.stacked_layout.setCurrentIndex(1)
        self.setWindowTitle("Command Center")

    def show_mode(self):
        self.stacked_layout.setCurrentIndex(0)
        self.setWindowTitle("Select Mode")

    def show_results(self):
        self.stacked_layout.setCurrentIndex(2)
        self.setWindowTitle("Results")

    def show_efficient_data_page(self):
        self.efficient.show_data_page()
        self.setWindowTitle("openVA App: load and prepare data")

    def show_efficient_select_algorithm_page(self):
        self.efficient.show_select_algorithm_page()
        self.setWindowTitle("openVA App: select algorithm")

    def show_efficient_select_algorithm_from_algorithm(self):
        self.efficient.show_select_algorithm_page()
        self.setWindowTitle("openVA App: select algorithm")

    def show_efficient_algorithm(self):
        if self.efficient.chosen_algorithm == "insilicova":
            self.show_efficient_insilicova_page()
        elif self.efficient.chosen_algorithm == "interva":
            self.show_efficient_interva_page()
        else:
            self.show_efficient_smartva_page()

    def show_efficient_insilicova_page(self):
        self.efficient.show_insilicova_page()
        self.setWindowTitle("openVA App: InSilicoVA")
        # alert = QMessageBox()
        # alert.setText("InSilicoVA currently unavailable, but coming soon!")
        # alert.exec()

    def show_efficient_interva_page(self):
        self.efficient.show_interva_page()
        self.setWindowTitle("openVA App: InterVA")

    def show_efficient_smartva_page(self):
        # self.efficient.show_smartva_page()
        # self.setWindowTitle("openVA App: SmartVA")
        alert = QMessageBox()
        alert.setText("SmartVA is not available (it is based on Python 2" +
                      "which is no longer supported by the Python Software " +
                      "Foundation).  It will be included when a verison " +
                      "based on Python 3 is released.")
        alert.exec()

    def show_efficient_results_page(self):
        self.efficient.show_results_page()
        self.setWindowTitle("openVA App: results")

    def update_interva_results(self, new_results, tmp_dir):
        self.results.update_interva(new_results, tmp_dir)

    def update_insilicova_results(self, new_results):
        self.results.update_insilicova(new_results)

    def update_smartva_results(self, new_results):
        self.results.update_smartva(new_results)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    gui = WindowManager()
    gui.show()
    sys.exit(app.exec_())
