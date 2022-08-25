# -*- coding: utf-8 -*-

"""
pyopenva.results
~~~~~~~~~~~~~~
This module creates the window for displaying and downloading results.
"""

from PyQt5.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QGroupBox,
                             QMessageBox, QPushButton, QFileDialog)
from output import PlotDialog, TableDialog, save_plot
import os


class Results(QWidget):

    def __init__(self):
        super().__init__()

        self.setGeometry(400, 400, 500, 400)
        self.setWindowTitle("openVA GUI: Results")
        self.results_v_box = QVBoxLayout()
        self.create_insilico_panel()
        self.create_interva_panel()
        self.create_smartva_panel()
        self.results_v_box.addWidget(self.insilico_panel)
        self.results_v_box.addWidget(self.interva_panel)
        self.results_v_box.addWidget(self.smartva_panel)
        self.btn_go_to_mode = QPushButton("Go Back to User Mode Selection")
        self.btn_go_to_command_center = QPushButton(
            "Go Back to the Command Center")
        self.results_v_box.addWidget(self.btn_go_to_mode)
        self.results_v_box.addWidget(self.btn_go_to_command_center)
        self.setLayout(self.results_v_box)

        self.insilico_results = None
        self.interva_results = None
        self.smartva_results = None

    #TODO: add slider for number of causes to include in the results
    #TODO: add option for comparison plot?
    #TODO: add option to group causes into aggregated categories?
    def create_insilico_panel(self):
        layout = QVBoxLayout()

        vbox_table = QVBoxLayout()
        self.btn_insilico_table = QPushButton("Show CSMF Table")
        self.btn_save_insilico_table = QPushButton("Download CSMF Table")
        vbox_table.addWidget(self.btn_insilico_table)
        vbox_table.addWidget(self.btn_save_insilico_table)

        vbox_plot = QVBoxLayout()
        self.btn_insilico_plot = QPushButton("Show CSMF Plot")
        self.btn_save_insilico_plot = QPushButton("Download CSMF Plot")
        vbox_plot.addWidget(self.btn_insilico_plot)
        vbox_plot.addWidget(self.btn_save_insilico_plot)

        hbox = QHBoxLayout()
        hbox.addLayout(vbox_table)
        hbox.addLayout(vbox_plot)
        layout.addLayout(hbox)
        self.btn_save_insilico_indiv = QPushButton(
            "Download Individual Cause Assignments")
        layout.addWidget(self.btn_save_insilico_indiv)
        self.insilico_panel = QGroupBox("InSilicoVA")
        self.insilico_panel.setLayout(layout)

    def create_interva_panel(self):
        layout = QVBoxLayout()

        vbox_table = QVBoxLayout()
        self.btn_interva_table = QPushButton("Show CSMF Table")
        self.btn_interva_table.clicked.connect(self.interva_table)
        self.btn_save_interva_table = QPushButton("Download CSMF Table")
        self.btn_save_interva_table.clicked.connect(
            self.download_interva_table)
        vbox_table.addWidget(self.btn_interva_table)
        vbox_table.addWidget(self.btn_save_interva_table)

        vbox_plot = QVBoxLayout()
        self.btn_interva_plot = QPushButton("Show CSMF Plot")
        self.btn_interva_plot.clicked.connect(self.interva_plot)
        self.btn_save_interva_plot = QPushButton("Download CSMF Plot")
        self.btn_save_interva_plot.clicked.connect(self.download_interva_plot)
        vbox_plot.addWidget(self.btn_interva_plot)
        vbox_plot.addWidget(self.btn_save_interva_plot)

        hbox = QHBoxLayout()
        hbox.addLayout(vbox_table)
        hbox.addLayout(vbox_plot)
        layout.addLayout(hbox)
        self.btn_save_interva_indiv = QPushButton(
            "Download Individual Cause Assignments")
        self.btn_save_interva_indiv.clicked.connect(
            self.download_interva_indiv)
        layout.addWidget(self.btn_save_interva_indiv)
        self.interva_panel = QGroupBox("InterVA")
        self.interva_panel.setLayout(layout)

    def create_smartva_panel(self):
        layout = QVBoxLayout()

        vbox_table = QVBoxLayout()
        self.btn_smartva_table = QPushButton("Show CSMF Table")
        self.btn_save_smartva_table = QPushButton("Download CSMF Table")
        vbox_table.addWidget(self.btn_smartva_table)
        vbox_table.addWidget(self.btn_save_smartva_table)

        vbox_plot = QVBoxLayout()
        self.btn_smartva_plot = QPushButton("Show CSMF Plot")
        self.btn_save_smartva_plot = QPushButton("Download CSMF Plot")
        vbox_plot.addWidget(self.btn_smartva_plot)
        vbox_plot.addWidget(self.btn_save_smartva_plot)

        hbox = QHBoxLayout()
        hbox.addLayout(vbox_table)
        hbox.addLayout(vbox_plot)
        layout.addLayout(hbox)
        self.btn_save_smartva_indiv = QPushButton(
            "Download Individual Cause Assignments")
        layout.addWidget(self.btn_save_smartva_indiv)
        self.smartva_panel = QGroupBox("SmartVA")
        self.smartva_panel.setLayout(layout)

    def interva_plot(self):
        if self.interva_results is None:
            alert = QMessageBox()
            alert.setText(
                "Need to run InterVA5 first.")
            alert.exec()
        else:
            self.interva_plot_dialog = PlotDialog(self.interva_results,
                                                  self,
                                                  top=10)
            self.interva_plot_dialog.exec()

    def interva_table(self):
        if self.interva_results is None:
            alert = QMessageBox()
            alert.setText(
                "Need to run InterVA5 first.")
            alert.exec()
        else:
            self.interva_table = TableDialog(self.interva_results,
                                             self,
                                             top=10)
            self.interva_table.resize(self.interva_table.table.width(),
                                      self.interva_table.table.height())
            self.interva_table.exec()

    def download_interva_table(self):
        if self.interva_results is None:
            alert = QMessageBox()
            alert.setText(
                "Need to run InterVA5 first.")
            alert.exec()
        else:
            results_file_name = "interva5_csmf.csv"
            path = QFileDialog.getSaveFileName(self,
                                               "Save CSMF (csv)",
                                               results_file_name,
                                               "CSV Files (*.csv)")
            if path != ("", ""):
                #os.remove(path[0])
                with open(path[0], "a") as f:
                    n_top_causes = 10
                    csmf = self.interva_results.get_csmf(top=n_top_causes)
                    csmf.sort_values(ascending=False, inplace=True)
                    csmf_df = csmf.reset_index()[0:n_top_causes]
                    csmf_df.rename(columns={"index": "Cause", 0: "CSMF"},
                                   inplace=True)
                    csmf_df.round(4).to_csv(f, index=False)
                if os.path.isfile(path[0]):
                    alert = QMessageBox()
                    alert.setText("results saved to" + path[0])
                    alert.exec()

    def download_interva_plot(self):
        if self.interva_results is None:
            alert = QMessageBox()
            alert.setText(
                "Need to run InterVA5 first.")
            alert.exec()
        else:
            results_file_name = "interva5_csmf.pdf"
            path = QFileDialog.getSaveFileName(self,
                                               "Save CSMF plot (pdf)",
                                               results_file_name,
                                               "PDF Files (*.pdf)")
            if path != ("", ""):
                #os.remove(path[0])
                save_plot(self.interva_results,
                          file_name=path[0])
                if os.path.isfile(path[0]):
                    alert = QMessageBox()
                    alert.setText("results saved to" + path[0])
                    alert.exec()

    def download_interva_indiv(self):
        if self.interva_results is None:
            alert = QMessageBox()
            alert.setText(
                "Need to run InterVA5 first.")
            alert.exec()
        else:
            results_file_name = "interva5_individual_cod.csv"
            path = QFileDialog.getSaveFileName(self,
                                               "Save CSMF (csv)",
                                               results_file_name,
                                               "CSV Files (*.csv)")
            if path != ("", ""):
                with open(path[0], "a") as f:
                    out = self.interva_results.get_indiv_prob(top=1)
                    out.to_csv(f, index=False)
                if os.path.isfile(path[0]):
                    alert = QMessageBox()
                    alert.setText("results saved to" + path[0])
                    alert.exec()

    def update_interva(self, new_interva_results):
        self.interva_results = new_interva_results

    def update_insilico(self, new_insilico_results):
        self.insilico_results = new_insilico_results

    def update_smartva(self, new_smartva_results):
        self.smartva_results = new_smartva_results
