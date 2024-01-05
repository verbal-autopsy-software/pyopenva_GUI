# -*- coding: utf-8 -*-

"""
pyopenva.main
~~~~~~~~~~~~~~
This module creates user interface for the app.
"""

import os
import sys
from PyQt5.QtWidgets import (QAction, QApplication, QFileDialog,
                             QMainWindow, QMessageBox, QStackedLayout, QWidget)
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage
from PyQt5.QtGui import QDesktopServices
from pandas import DataFrame, read_csv
from pyopenva.efficient import Efficient
from pyopenva.mode import Mode
from pyopenva.command_center import CommandCenter
from pyopenva.results import Results
from pyopenva.load import LoadData
from pyopenva.__version__ import (__description__, __license__, __url__,
                                  __version__)


class CustomWebEnginePage(QWebEnginePage):

    def acceptNavigationRequest(self, url, _type, is_main_frame):
        not_host = url.host() != ""
        if _type == QWebEnginePage.NavigationTypeLinkClicked and not_host:
            QDesktopServices.openUrl(url)
            return False
        return super().acceptNavigationRequest(url, _type, is_main_frame)


class WindowManager(QMainWindow):

    def __init__(self):
        super().__init__()
        # self.setGeometry(200, 200, 500, 300)
        self.setWindowTitle("Select Mode")
        self.insilicova_limit = 100
        self.efficient = Efficient(self.insilicova_limit)
        self.mode = Mode()
        # self.command_center = CommandCenter()
        self.command_center = CommandCenter(self)
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
        self.mode.btn_exit.clicked.connect(self.close)
        self.mode.btn_about.clicked.connect(self.show_about)

        self.command_center.btn_user_mode.clicked.connect(self.show_mode)
        self.command_center.btn_algorithm_results.clicked.connect(
            self.show_results)
        self.command_center.btn_command_center_exit.clicked.connect(self.close)

        self.results.btn_go_to_command_center.clicked.connect(
            self.show_command_center)
        self.results.btn_go_to_mode.clicked.connect(
            self.show_mode)
        self.results.btn_results_ui_exit.clicked.connect(self.close)

        # TODO: make this more efficient (it works, but probably a lot of
        #       redundancies!)
        self.efficient.btn_go_to_mode.clicked.connect(
            self.show_mode)

        self.efficient.btn_go_to_data_page.clicked.connect(
            self.show_efficient_data_page)

        self.efficient.btn_data_ui_exit.clicked.connect(self.close)

        self.efficient.btn_algorithm.clicked.connect(
            self.show_efficient_select_algorithm_page)

        self.efficient.btn_algorithm_ui_exit.clicked.connect(self.close)

        self.efficient.btn_insilicova.clicked.connect(
            self.show_efficient_insilicova_page)

        self.efficient.btn_interva.clicked.connect(
            self.show_efficient_interva_page)

        # self.efficient.btn_smartva.clicked.connect(
        #     self.show_efficient_smartva_page)

        self.efficient.btn_insilicova_to_select_algorithm.clicked.connect(
            self.show_efficient_select_algorithm_from_algorithm)

        self.efficient.btn_insilicova_ui_exit.clicked.connect(self.close)

        self.efficient.btn_interva_to_select_algorithm.clicked.connect(
            self.show_efficient_select_algorithm_from_algorithm)

        self.efficient.btn_interva_ui_exit.clicked.connect(self.close)

        # self.efficient.btn_smartva_to_select_algorithm.clicked.connect(
        #     self.show_efficient_select_algorithm_from_algorithm)
        #
        # self.efficient.btn_smartva_ui_exit.clicked.connect(self.close)

        self.efficient.btn_insilicova_go_to_results_page.clicked.connect(
            self.show_efficient_results_page)

        self.efficient.btn_go_to_results_page.clicked.connect(
            self.show_efficient_results_page)

        self.efficient.btn_results_to_algorithm.clicked.connect(
            self.show_efficient_algorithm
        )

        self.efficient.btn_results_ui_exit.clicked.connect(self.close)

        # update results
        self.command_center.btn_interva_run.clicked.connect(
            lambda: self.update_interva_results(
                self.command_center.interva_results))
        self.command_center.btn_interva_run.clicked.connect(
            lambda: self.update_interva_tmp_dir(
                self.command_center.interva_tmp_dir))

        self.command_center.btn_insilicova_run.clicked.connect(
            lambda: self.update_insilicova_results(
                self.command_center.insilicova_results))

        # self.command_center.btn_smartva_run.clicked.connect(
        #     lambda: self.update_smartva_results(
        #         self.command_center.smartva_results))

        # actions for menu bar
        act_about = QAction("About openVA App", self)
        act_about.triggered.connect(self.show_about)
        act_setwd = QAction("Set working directory", self)
        act_setwd.triggered.connect(self.select_working_dir)
        act_close = QAction("Exit", self)
        act_close.triggered.connect(self.close)
        act_goto_eff = QAction("Wizard mode", self)
        act_goto_eff.triggered.connect(self.show_efficient)
        act_goto_cc = QAction("Customizable mode", self)
        act_goto_cc.triggered.connect(self.show_command_center)
        act_load_ex_data_efficient = QAction("Wizard mode", self)
        act_load_ex_data_efficient.triggered.connect(
            self.load_example_data_efficient)
        act_load_ex_data_command_center = QAction("Customizable mode", self)
        act_load_ex_data_command_center.triggered.connect(
            self.load_example_data_command_center)
        # color_list = ["Greys", "Blues", "Greens", "Oranges", "Reds",
        #               "viridis", "plasma", "inferno"]
        act_color_greys = QAction("Greys", self)
        act_color_greys.triggered.connect(
            lambda: self.set_plot_color("Greys"))
        act_color_blues = QAction("Blues", self)
        act_color_blues.triggered.connect(
            lambda: self.set_plot_color("Blues"))
        act_color_greens = QAction("Greens", self)
        act_color_greens.triggered.connect(
            lambda: self.set_plot_color("Greens"))
        act_color_oranges = QAction("Oranges", self)
        act_color_oranges.triggered.connect(
            lambda: self.set_plot_color("Oranges"))
        act_color_reds = QAction("Reds", self)
        act_color_reds.triggered.connect(
            lambda: self.set_plot_color("Reds"))
        act_color_viridis = QAction("viridis", self)
        act_color_viridis.triggered.connect(
            lambda: self.set_plot_color("viridis"))
        act_color_plasma = QAction("plasma", self)
        act_color_plasma.triggered.connect(
            lambda: self.set_plot_color("plasma"))
        act_color_inferno = QAction("inferno", self)
        act_color_inferno.triggered.connect(
            lambda: self.set_plot_color("inferno"))
        act_help = QAction("Help contents...", self)
        act_help.triggered.connect(self.show_help)

        # setup menu bar
        menu = self.menuBar()
        menu_file = menu.addMenu("&File")
        menu_nav = menu.addMenu("&Navigate")
        menu_data = menu.addMenu("&Data")
        menu_plot = menu.addMenu("&Plot")
        menu_help = menu.addMenu("&Help")

        menu_file.addAction(act_about)
        menu_file.addAction(act_setwd)
        menu_file.addAction(act_close)
        menu_nav_go = menu_nav.addMenu("Go to... ")
        menu_nav_go.addAction(act_goto_eff)
        menu_nav_go.addSeparator()
        menu_nav_go.addAction(act_goto_cc)
        menu_data_load = menu_data.addMenu("Load example data in...")
        menu_data_load.addAction(act_load_ex_data_efficient)
        menu_data_load.addSeparator()
        menu_data_load.addAction(act_load_ex_data_command_center)
        menu_plot_color = menu_plot.addMenu("Choose color scheme...")
        menu_plot_color_blind = menu_plot_color.addMenu("Colorblind-Friendly")
        menu_plot_color.addSeparator()
        menu_plot_color_alt = menu_plot_color.addMenu("Alternates")
        menu_plot_color_blind.addAction(act_color_greys)
        menu_plot_color_blind.addAction(act_color_blues)
        menu_plot_color_blind.addAction(act_color_greens)
        menu_plot_color_blind.addAction(act_color_oranges)
        menu_plot_color_blind.addAction(act_color_reds)
        menu_plot_color_alt.addAction(act_color_viridis)
        menu_plot_color_alt.addAction(act_color_plasma)
        menu_plot_color_alt.addAction(act_color_inferno)
        menu_help.addAction(act_help)

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
            self.setWindowTitle("openVA App: InSilicoVA")
        elif self.efficient.chosen_algorithm == "interva":
            self.show_efficient_interva_page()
            self.setWindowTitle("openVA App: InterVA")
        # else:
        #     self.show_efficient_smartva_page()

    def show_efficient_insilicova_page(self):
        sample_size_limit = False
        if self.efficient.data is not None:
            n_records = self.efficient.data.shape[0]
            if n_records < self.insilicova_limit:
                sample_size_limit = True
        if sample_size_limit:
            alert = QMessageBox()
            alert.setText(
                f"InSilicoVA is unavailable.  At least {self.insilicova_limit}"
                " deaths are needed for reliable results.\n\n"
                "(InterVA is available.)")
            alert.exec()
        else:
            self.efficient.show_insilicova_page()
            self.setWindowTitle("openVA App: InSilicoVA")

    def show_efficient_interva_page(self):
        self.efficient.show_interva_page()
        self.setWindowTitle("openVA App: InterVA")

    # def show_efficient_smartva_page(self):
    #     # self.efficient.show_smartva_page()
    #     # self.setWindowTitle("openVA App: SmartVA")
    #     alert = QMessageBox()
    #     alert.setWindowTitle("openVA App: SmartVA")
    #     alert.setText("SmartVA is not available (it is based on Python 2" +
    #                   "which is no longer supported by the Python " +
    #                   "Software Foundation).  It will be included when " +
    #                   "a version based on Python 3 is released.")
    #     alert.exec()

    def show_efficient_results_page(self):
        self.efficient.show_results_page()
        if self.efficient.chosen_algorithm == "insilicova":
            self.setWindowTitle("openVA App: InSilicoVA Results")
        else:
            self.setWindowTitle("openVA App: InterVA Results")

    # def update_interva_results(self, new_results, tmp_dir):
    #     self.results.update_interva(new_results, tmp_dir)

    def update_interva_results(self, new_results):
        self.results.update_interva_results(new_results)

    def update_interva_tmp_dir(self, tmp_dir):
        self.results.update_interva_tmp_dir(tmp_dir)

    def update_insilicova_results(self, new_results):
        self.results.update_insilicova(new_results)
        self.command_center.update_insilicova_results(new_results)

    # def update_smartva_results(self, new_results):
    #     self.results.update_smartva(new_results)

    def load_example_data_efficient(self):
        path = self.find_data_file("data/who151_odk_export.csv")
        self.efficient.data = read_csv(path)
        f_name = "example data set"
        n_records = self.efficient.data.shape[0]
        self.efficient.label_data.setAlignment(Qt.AlignLeft)
        self.efficient.label_data.setText("Data loaded:")
        self.efficient.label_data_fname.setAlignment(Qt.AlignCenter)
        self.efficient.label_data_fname.setText(f"{f_name}")
        self.efficient.label_data_n_records.setAlignment(Qt.AlignCenter)
        self.efficient.label_data_n_records.setText(f"({n_records} records)")
        self.efficient.data_loaded = True
        self.efficient.combo_data_id_col.blockSignals(True)
        self.efficient.combo_data_id_col.clear()
        self.efficient.combo_data_id_col.addItems(
            ["no ID column"] + list(self.efficient.data)
        )
        self.efficient.combo_data_id_col.blockSignals(False)
        self.efficient.combo_data_id_col.setCurrentIndex(0)
        # reset app
        # TODO: create method for clearing results
        self.efficient.label_insilicova_progress.setText(
            "(no results)")
        self.efficient.insilicova_warnings = None
        self.efficient.insilicova_errors = None
        self.efficient.insilicova_results = None
        self.efficient.label_interva_progress.setText(
            "(no results)")
        self.efficient.insilicova_pbar.setValue(0)
        self.efficient.interva_log = None
        self.efficient.interva_results = None
        self.efficient.interva_pbar.setValue(0)
        self.efficient.pycrossva_data = None
        self.show_efficient()

    def load_example_data_command_center(self):
        path = self.find_data_file("data/who151_odk_export.csv")
        self.command_center.load_window = LoadData(input_fname=path)
        df = DataFrame(self.command_center.load_window.data[1:],
                       columns=self.command_center.load_window.data[0])
        self.results.original_data = df
        self.command_center.btn_edit_data.setEnabled(True)
        n_records = len(self.command_center.load_window.data) - 1
        f_name = self.command_center.load_window.fname.split("/")[-1]
        self.command_center.label_data.setAlignment(Qt.AlignLeft)
        self.command_center.label_data.setText("Data loaded:")
        self.command_center.label_data_fname.setAlignment(Qt.AlignCenter)
        self.command_center.label_data_fname.setText(f"{f_name}")
        self.command_center.label_data_n_records.setAlignment(Qt.AlignCenter)
        self.command_center.label_data_n_records.setText(
            f"({n_records} records)")
        self.command_center.label_pycrossva_status.setText(
            "(need to run pyCrossVA)")
        self.command_center.combo_data_id_col.blockSignals(True)
        self.command_center.combo_data_id_col.clear()
        self.command_center.combo_data_id_col.addItems(
            ["no ID column"] + self.command_center.load_window.header[0])
        self.command_center.combo_data_id_col.blockSignals(False)
        self.command_center.combo_data_id_col.setCurrentIndex(0)

        self.command_center.btn_pycrossva.setEnabled(True)
        self.command_center.pycrossva_data = None
        self.command_center.insilicova_results = None
        self.command_center.label_insilicova_progress.setText("")
        self.command_center.insilicova_pbar.setValue(0)
        self.command_center.insilicova_warnings = None
        self.command_center.insilicova_errors = None
        self.command_center.interva_results = None
        self.command_center.interva_log = None
        self.command_center.label_interva_progress.setText("")
        self.command_center.interva_pbar.setValue(0)
        self.show_command_center()

    def set_plot_color(self, plt_color):
        self.efficient.set_plot_color(plt_color)
        self.results.set_plot_color(plt_color)

    @staticmethod
    def find_data_file(file_name):
        if getattr(sys, "frozen", False):
            datadir = os.path.dirname(sys.executable)
        else:
            datadir = os.path.dirname(__file__)
        return os.path.join(datadir, file_name)

    def closeEvent(self, event):
        close = QMessageBox()
        close.setWindowTitle("openVA App")
        close.setIcon(QMessageBox.Question)
        close.setText("Close openVA App?")
        close.setStandardButtons(QMessageBox.Yes | QMessageBox.Cancel)
        close = close.exec()
        if close == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    @staticmethod
    def show_about():
        info = QMessageBox()
        info.setWindowTitle("openVA App")
        info.setIcon(QMessageBox.Information)
        info.setText(f"{__description__}\n" +
                     f"Version: {__version__}\n" +
                     f"License: {__license__}\n" +
                     f"Website: {__url__}")
        info.exec()

    def show_help(self):
        # help_path = os.path.join(os.path.dirname(__file__),
        #                          "docs", "index.html")
        index_name = os.path.join("docs", "index.html")
        help_path = self.find_data_file(index_name)
        self.browser = QWebEngineView()
        self.browser.setPage(CustomWebEnginePage(self))
        self.browser.setUrl(QUrl.fromLocalFile(help_path))
        self.browser.setGeometry(200, 200, 1017, 800)
        self.browser.show()

    def select_working_dir(self):
        file = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        self.command_center.working_dir = file
        self.efficient.working_dir = file
        self.results.working_dir = file


if __name__ == '__main__':
    app = QApplication(sys.argv)
    gui = WindowManager()
    gui.show()
    sys.exit(app.exec_())
