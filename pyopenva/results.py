# -*- coding: utf-8 -*-

"""
pyopenva.results
~~~~~~~~~~~~~~
This module creates the window for displaying and downloading results.
"""

from PyQt5.QtWidgets import (QCheckBox, QFileDialog, QGroupBox, QHBoxLayout,
                             QMessageBox, QPushButton, QSpinBox, QVBoxLayout,
                             QWidget)
from pyopenva.output import PlotDialog, TableDialog, save_plot
import os
import shutil
from pandas import DataFrame
from pandas import concat as pd_concat


class Results(QWidget):

    def __init__(self):
        super().__init__()

        #self.setGeometry(400, 400, 500, 400)
        self.setWindowTitle("openVA GUI: Results")
        self.insilicova_results = None
        self.interva_results = None
        self.interva_tmp_dir = None
        self.smartva_results = None
        self.n_top_causes = 5
        self.results_v_box = QVBoxLayout()
        self.create_insilicova_panel()
        self.create_interva_panel()
        self.create_smartva_panel()

        self.spinbox_n_causes = QSpinBox()
        self.spinbox_n_causes.setRange(1, 64)
        self.spinbox_n_causes.setPrefix("Include ")
        self.spinbox_n_causes.setSuffix(" causes in the results")
        self.spinbox_n_causes.setValue(self.n_top_causes)
        self.spinbox_n_causes.valueChanged.connect(self.set_n_top_causes)
        self.spinbox_n_causes.setMaximumWidth(350)
        self.results_v_box.addWidget(self.spinbox_n_causes)

        self.results_v_box.addWidget(self.insilicova_panel)
        #self.results_v_box.insertSpacing(1, 50)
        self.results_v_box.addWidget(self.interva_panel)
        #self.results_v_box.insertSpacing(3, 50)
        self.results_v_box.addWidget(self.smartva_panel)
        #self.results_v_box.insertSpacing(5, 50)
        self.btn_go_to_mode = QPushButton("Go Back to User Mode Selection")
        self.btn_go_to_command_center = QPushButton(
            "Go Back to the Command Center")
        self.results_v_box.addWidget(self.btn_go_to_mode)
        self.results_v_box.addWidget(self.btn_go_to_command_center)
        self.setLayout(self.results_v_box)

    #TODO: add option for comparison plot?
    #TODO: add option to group causes into aggregated categories?
    def create_insilicova_panel(self):
        layout = QVBoxLayout()

        vbox_table = QVBoxLayout()
        self.btn_insilicova_table = QPushButton("Show \n CSMF Table")
        self.btn_insilicova_table.clicked.connect(
            self.insilicova_table)
        self.btn_save_insilicova_table = QPushButton("Download CSMF Table")
        self.btn_save_insilicova_table.clicked.connect(
            self.download_insilicova_table)
        vbox_table.addWidget(self.btn_insilicova_table)
        vbox_table.addWidget(self.btn_save_insilicova_table)

        vbox_plot = QVBoxLayout()
        self.btn_insilicova_plot = QPushButton("Show \n CSMF Plot")
        self.btn_insilicova_plot.clicked.connect(
            self.insilicova_plot)
        self.btn_save_insilicova_plot = QPushButton("Download CSMF Plot")
        self.btn_save_insilicova_plot.clicked.connect(
            self.download_insilicova_plot)
        vbox_plot.addWidget(self.btn_insilicova_plot)
        vbox_plot.addWidget(self.btn_save_insilicova_plot)

        hbox = QHBoxLayout()
        hbox.addLayout(vbox_table)
        hbox.addLayout(vbox_plot)
        layout.addLayout(hbox)
        self.btn_save_insilicova_indiv = QPushButton(
            "Download \n Individual Cause Assignments")
        self.btn_save_insilicova_indiv.clicked.connect(
            self.download_insilicova_indiv)
        self.insilicova_include_probs = False
        self.chbox_insilicova_include_probs = QCheckBox(
            "Include probability of top cause (with individual CODs)")
        self.chbox_insilicova_include_probs.toggled.connect(
            self.set_insilicova_include_probs)
        self.btn_save_insilicova_log = QPushButton(
            "Download log file from data checks")
        self.btn_save_insilicova_log.clicked.connect(
            self.download_insilicova_log)
        layout.addWidget(self.btn_save_insilicova_indiv)
        layout.addWidget(self.chbox_insilicova_include_probs)
        layout.addWidget(self.btn_save_insilicova_log)

        self.insilicova_panel = QGroupBox("InSilicoVA")
        self.insilicova_panel.setLayout(layout)

    def create_interva_panel(self):
        layout = QVBoxLayout()

        vbox_table = QVBoxLayout()
        self.btn_interva_table = QPushButton("Show \n CSMF Table")
        self.btn_interva_table.clicked.connect(self.interva_table)
        self.btn_save_interva_table = QPushButton("Download CSMF Table")
        self.btn_save_interva_table.clicked.connect(
            self.download_interva_table)
        vbox_table.addWidget(self.btn_interva_table)
        vbox_table.addWidget(self.btn_save_interva_table)

        vbox_plot = QVBoxLayout()
        self.btn_interva_plot = QPushButton("Show \n CSMF Plot")
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
            "Download Individual \n Cause Assignments")
        self.btn_save_interva_indiv.clicked.connect(
            self.download_interva_indiv)
        self.btn_save_interva_log = QPushButton(
            "Download log file from data checks")
        self.btn_save_interva_log.clicked.connect(
            self.download_interva_log)
        # self.spinbox_n_causes = QSpinBox()
        # self.spinbox_n_causes.setRange(1, 64)
        # self.spinbox_n_causes.setPrefix("Include ")
        # self.spinbox_n_causes.setSuffix(" causes in the results")
        # self.spinbox_n_causes.setValue(self.n_top_causes)
        # self.spinbox_n_causes.valueChanged.connect(self.set_n_top_causes)
        # self.spinbox_n_causes.setMaximumWidth(350)
        layout.addWidget(self.btn_save_interva_indiv)
        layout.addWidget(self.btn_save_interva_log)
        # layout.addWidget(self.spinbox_n_causes)
        self.interva_panel = QGroupBox("InterVA")
        self.interva_panel.setLayout(layout)

    def create_smartva_panel(self):
        layout = QVBoxLayout()

        vbox_table = QVBoxLayout()
        self.btn_smartva_table = QPushButton("Show \n CSMF Table")
        self.btn_save_smartva_table = QPushButton("Download CSMF Table")
        vbox_table.addWidget(self.btn_smartva_table)
        vbox_table.addWidget(self.btn_save_smartva_table)

        vbox_plot = QVBoxLayout()
        self.btn_smartva_plot = QPushButton("Show \n CSMF Plot")
        self.btn_save_smartva_plot = QPushButton("Download CSMF Plot")
        vbox_plot.addWidget(self.btn_smartva_plot)
        vbox_plot.addWidget(self.btn_save_smartva_plot)

        hbox = QHBoxLayout()
        hbox.addLayout(vbox_table)
        hbox.addLayout(vbox_plot)
        layout.addLayout(hbox)
        self.btn_save_smartva_indiv = QPushButton(
            "Download \n Individual Cause Assignments")
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
                                                  top=self.n_top_causes)
            self.interva_plot_dialog.exec()

    def interva_table(self):
        if self.interva_results is None:
            alert = QMessageBox()
            alert.setText(
                "Need to run InterVA5 first.")
            alert.exec()
        else:
            self.interva_table = TableDialog(results=self.interva_results,
                                             algorithm="interva",
                                             parent=self,
                                             top=self.n_top_causes)
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
                with open(path[0], "w", newline="") as f:
                    n_top_causes = self.n_top_causes
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
                save_plot(results=self.interva_results,
                          algorithm="interva",
                          top=self.n_top_causes,
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
                with open(path[0], "w", newline="") as f:
                    out = self.interva_results.out["VA5"]
                    out.drop("WHOLEPROB", axis=1, inplace=True)
                    out.to_csv(f, index=False)
                if os.path.isfile(path[0]):
                    alert = QMessageBox()
                    alert.setText("results saved to" + path[0])
                    alert.exec()

    def download_interva_log(self):
        if self.interva_results is None:
            alert = QMessageBox()
            alert.setText(
                "Need to run InterVA first.")
            alert.exec()
        else:
            log_file_name = "interva_log.txt"
            path = QFileDialog.getSaveFileName(self,
                                               "Save log (txt)",
                                               log_file_name,
                                               "Text Files (*.txt)")
            if path != ("", ""):
                tmp_log = os.path.join(self.interva_tmp_dir.name,
                                       "errorlogV5.txt")
                shutil.copyfile(tmp_log, log_file_name)
                if os.path.isfile(path[0]):
                    alert = QMessageBox()
                    alert.setText("log saved to" + path[0])
                    alert.exec()

    def insilicova_plot(self):
        if self.insilicova_results is None:
            alert = QMessageBox()
            alert.setText(
                "Need to run InSilicoVA first.")
            alert.exec()
        else:
            self.insilicova_plot_dialog = PlotDialog(results=self.insilicova_results,
                                                     algorithm="insilicova",
                                                     parent=self,
                                                     top=self.n_top_causes)
            self.insilicova_plot_dialog.exec()

    def insilicova_table(self):
        if self.insilicova_results is None:
            alert = QMessageBox()
            alert.setText(
                "Need to run InSilicoVA first.")
            alert.exec()
        else:
            self.insilicova_table = TableDialog(self.insilicova_results,
                                                self,
                                                top=self.n_top_causes)
            self.insilicova_table.resize(self.insilicova_table.table.width(),
                                         self.insilicova_table.table.height())
            self.insilicova_table.exec()

    def download_insilicova_table(self):
        if self.insilicova_results is None:
            alert = QMessageBox()
            alert.setText(
                "Need to run InSilicoVA first.")
            alert.exec()
        else:
            results_file_name = "insilicova_csmf.csv"
            path = QFileDialog.getSaveFileName(self,
                                               "Save CSMF (csv)",
                                               results_file_name,
                                               "CSV Files (*.csv)")
            if path != ("", ""):
                #os.remove(path[0])
                with open(path[0], "w", newline="") as f:
                    n_top_causes = self.n_top_causes
                    csmf = self.insilicova_results.get_csmf(top=n_top_causes)
                    csmf_df = csmf.sort_values(by="Mean", ascending=False).copy()
                    csmf_df = csmf_df.reset_index()
                    csmf_df.rename(columns={"index": "Cause", "Mean": "CSMF (Mean)"},
                                   inplace=True)
                    csmf_df.round(4).to_csv(f, index=False)
                if os.path.isfile(path[0]):
                    alert = QMessageBox()
                    alert.setText("results saved to" + path[0])
                    alert.exec()

    def download_insilicova_plot(self):
        if self.insilicova_results is None:
            alert = QMessageBox()
            alert.setText(
                "Need to run InSilicoVA first.")
            alert.exec()
        else:
            results_file_name = "insilicova_csmf.pdf"
            path = QFileDialog.getSaveFileName(self,
                                               "Save CSMF plot (pdf)",
                                               results_file_name,
                                               "PDF Files (*.pdf)")
            if path != ("", ""):
                #os.remove(path[0])
                save_plot(results=self.insilicova_results,
                          algorithm="insilicova",
                          top=self.n_top_causes,
                          file_name=path[0])
                if os.path.isfile(path[0]):
                    alert = QMessageBox()
                    alert.setText("results saved to" + path[0])
                    alert.exec()

    def download_insilicova_indiv(self):
        if self.insilicova_results is None:
            alert = QMessageBox()
            alert.setText(
                "Need to run InSilicoVA first.")
            alert.exec()
        else:
            results_file_name = "insilicova_individual_cod.csv"
            path = QFileDialog.getSaveFileName(self,
                                               "Save CSMF (csv)",
                                               results_file_name,
                                               "CSV Files (*.csv)")
            if path != ("", ""):
                with open(path[0], "w", newline="") as f:
                    out = self.prepare_insilico_indiv_cod(
                        self.insilicova_results)
                    out.to_csv(f, index=False)
                if os.path.isfile(path[0]):
                    alert = QMessageBox()
                    alert.setText("results saved to" + path[0])
                    alert.exec()

    def prepare_insilico_indiv_cod(self, results):
        all_results = []
        for i in range(results.indiv_prob.shape[0]):
            row = results.indiv_prob.iloc[i].copy()
            top_causes = row.sort_values(ascending=False)[0:self.n_top_causes]
            top_causes = top_causes.reset_index()
            if self.insilicova_include_probs:
                labels = ["Cause", "Prob"] * self.n_top_causes
                numbers = []
                [numbers.extend([str(a)]*2) for a in
                 range(1, self.n_top_causes + 1)]
                col_names = [a + b for a, b in zip(labels, numbers)]
                top_causes = top_causes.unstack(level=0)
                top_causes = top_causes.droplevel(level=0)
                top_causes = top_causes.sort_index()
                values = top_causes.tolist()
                all_results.append(
                    DataFrame([values], columns=col_names, index=[row.name]))
            else:
                col_names = ["Cause" + str(i) for i in
                             range(1, self.n_top_causes + 1)]
                all_results.append(
                    DataFrame([top_causes["index"].tolist()],
                              columns=col_names,
                              index=[row.name]))
        indiv_cod = pd_concat(all_results)
        indiv_cod = indiv_cod.reset_index(names="ID")
        return indiv_cod

    def download_insilicova_log(self):
        results = self.insilicova_results
        if results is None:
            alert = QMessageBox()
            alert.setText(
                "Need to run InSilicoVA first.")
            alert.exec()
        else:
            log_file_name = "insilicova_log.txt"
            path = QFileDialog.getSaveFileName(self,
                                               "Save log (txt)",
                                               log_file_name,
                                               "Text Files (*.txt)")
            if path != ("", ""):
                with open(log_file_name, "w") as f_out:
                    f_out.write("Log file from InSilicoVA")
                    if len(results.errors) > 0:
                        f_out.write("The following records are incomplete "
                                    "and excluded from further processing\n\n")
                        f_out.write("\n".join(results.errors))
                    f_out.write("\n \n first pass \n \n")
                    f_out.write("\n".join(results.warnings["first_pass"]))
                    f_out.write("\n \n second pass \n \n")
                    f_out.write("\n".join(results.warnings["second_pass"]))
                if os.path.isfile(path[0]):
                    alert = QMessageBox()
                    alert.setText("log saved to" + path[0])
                    alert.exec()

    def update_interva(self, new_interva_results, tmp_dir):
        self.interva_results = new_interva_results
        self.interva_tmp_dir = tmp_dir

    def update_insilicova(self, new_insilicova_results):
        self.insilicova_results = new_insilicova_results

    def update_smartva(self, new_smartva_results):
        self.smartva_results = new_smartva_results

    def set_n_top_causes(self, n):
        self.n_top_causes = n

    def set_insilicova_include_probs(self, checked):
        if checked:
            self.insilicova_include_probs = True
        else:
            self.insilicova_include_probs = False
