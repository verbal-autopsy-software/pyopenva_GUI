# -*- coding: utf-8 -*-

"""
pyopenva.results
~~~~~~~~~~~~~~
This module creates the window for displaying and saving results.
"""

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QCheckBox, QComboBox, QFileDialog, QGroupBox,
                             QHBoxLayout, QLabel, QMessageBox, QPushButton,
                             QSpinBox, QTabWidget, QVBoxLayout, QWidget)
from pyopenva.output import (DemTableDialog, PlotDialog, TableDialog,
                             save_plot, _insilicova_subpop, _make_title)
import os
import shutil
from pandas import DataFrame
from pandas import concat as pd_concat
from interva import utils


class Results(QWidget):

    def __init__(self):
        super().__init__()

        # self.setGeometry(400, 400, 500, 400)
        self.setWindowTitle("openVA GUI: Results")
        self.working_dir = ""
        self.original_data = None
        self.original_data_id = None
        self.insilicova_include_va_data = False
        self.insilicova_results = None
        self.insilicova_include_probs = True
        self.interva_include_va_data = False
        self.interva_results = None
        self.interva_include_probs = True
        self.interva_rule = True
        self.results_use_prop = False
        self.interva_tmp_dir = None
        self.options_sex = "all deaths"
        self.options_age = "all deaths"
        # self.smartva_results = None
        self.n_top_causes = 5
        self.plot_color = "Greys"
        self.results_v_box = QVBoxLayout()
        self.create_insilicova_panel()
        self.create_interva_panel()
        # self.create_smartva_panel()

        hbox_display_options = QHBoxLayout()
        self.spinbox_n_causes = QSpinBox()
        self.spinbox_n_causes.setRange(1, 61)
        self.spinbox_n_causes.setPrefix("Include ")
        self.spinbox_n_causes.setSuffix(" causes in the results")
        self.spinbox_n_causes.setValue(self.n_top_causes)
        self.spinbox_n_causes.valueChanged.connect(self.set_n_top_causes)
        self.spinbox_n_causes.setMaximumWidth(350)
        self.chbox_use_prop = QCheckBox("show CSMF as proportions")
        self.chbox_use_prop.setChecked(self.results_use_prop)
        self.chbox_use_prop.toggled.connect(self.set_results_use_prop)
        hbox_display_options.addWidget(self.spinbox_n_causes)
        # hbox_display_options.insertSpacing(1, 150)
        hbox_display_options.addWidget(self.chbox_use_prop)
        hbox_display_options.setAlignment(self.chbox_use_prop, Qt.AlignRight)


        # self.results_v_box.addWidget(self.spinbox_n_causes)
        self.results_v_box.addLayout(hbox_display_options)

        self.results_tabs = QTabWidget()
        self.results_tabs.addTab(self.insilicova_panel, "InSilicoVA")
        self.results_tabs.addTab(self.interva_panel, "InterVA")
        # self.results_tabs.addTab(self.smartva_panel, "SmartVA")
        self.results_v_box.addWidget(self.results_tabs)
        hbox_navigate = QHBoxLayout()
        self.btn_go_to_mode = QPushButton("Go Back to User Mode Selection")
        self.btn_go_to_command_center = QPushButton(
            "Go Back to the Command Center")
        self.btn_results_ui_exit = QPushButton("Exit")
        hbox_navigate.addWidget(self.btn_go_to_mode)
        hbox_navigate.addWidget(self.btn_go_to_command_center)
        hbox_navigate.addWidget(self.btn_results_ui_exit)
        self.results_v_box.addLayout(hbox_navigate)
        self.setLayout(self.results_v_box)

    # TODO: add option for comparison plot?
    # TODO: add option to group causes into aggregated categories?
    def create_insilicova_panel(self):

        gbox_dem = self.create_demographics_gbox()

        gbox_show = QGroupBox("Show Results")
        hbox_show = QHBoxLayout()
        self.btn_insilicova_table = QPushButton("Show \n CSMF Table")
        self.btn_insilicova_table.clicked.connect(
            self.insilicova_table)
        self.btn_insilicova_plot = QPushButton("Show \n CSMF Plot")
        self.btn_insilicova_plot.clicked.connect(
            self.insilicova_plot)
        self.btn_show_dem = QPushButton("Show \n Demographics")
        self.btn_show_dem.pressed.connect(
            lambda: self.run_table_dialog_dem("insilicova"))
        hbox_show.addWidget(self.btn_insilicova_table)
        hbox_show.addWidget(self.btn_insilicova_plot)
        hbox_show.addWidget(self.btn_show_dem)
        gbox_show.setLayout(hbox_show)

        gbox_save = QGroupBox("Save Results")
        vbox_save = QVBoxLayout()
        hbox_save_row1 = QHBoxLayout()
        hbox_save_row2 = QHBoxLayout()
        self.btn_save_insilicova_table = QPushButton("Save CSMF Table")
        self.btn_save_insilicova_table.clicked.connect(
            self.save_insilicova_table)
        self.btn_save_insilicova_plot = QPushButton("Save CSMF Plot")
        self.btn_save_insilicova_plot.clicked.connect(
            self.save_insilicova_plot)
        self.btn_save_insilicova_indiv = QPushButton(
            "Save Individual \n Cause Assignments")
        self.btn_save_insilicova_indiv.clicked.connect(
            self.save_insilicova_indiv)
        self.btn_save_insilicova_all_cod = QPushButton(
            "Save All \n Cause Assignments")
        self.btn_save_insilicova_all_cod.clicked.connect(
            self.save_insilicova_indiv_all)
        hbox_save_row1.addWidget(self.btn_save_insilicova_table)
        hbox_save_row1.addWidget(self.btn_save_insilicova_plot)
        hbox_save_row2.addWidget(self.btn_save_insilicova_indiv)
        hbox_save_row2.addWidget(self.btn_save_insilicova_all_cod)
        vbox_save.addLayout(hbox_save_row1)
        vbox_save.addLayout(hbox_save_row2)

        self.chbox_insilicova_include_probs = QCheckBox(
            "Include probability of top cause (with individual CODs)")
        self.chbox_insilicova_include_probs.setChecked(
            self.insilicova_include_probs)
        self.chbox_insilicova_include_probs.toggled.connect(
            self.set_insilicova_include_probs)
        self.chbox_insilicova_include_va_data = QCheckBox(
            "Include VA data (with individual CODs)")
        self.chbox_insilicova_include_va_data.setChecked(
            self.insilicova_include_va_data)
        self.chbox_insilicova_include_va_data.toggled.connect(
            self.set_insilicova_include_va_data)
        vbox_save.addWidget(self.chbox_insilicova_include_probs)
        vbox_save.addWidget(self.chbox_insilicova_include_va_data)
        gbox_save.setLayout(vbox_save)

        layout = QVBoxLayout()
        layout.addWidget(gbox_dem)
        layout.addWidget(gbox_show)
        layout.addWidget(gbox_save)
        # layout.addWidget(self.chbox_insilicova_include_probs)
        layout.insertSpacing(1, 50)
        layout.insertSpacing(3, 50)
        # layout.insertSpacing(5, 50)
        self.insilicova_panel = QWidget()
        self.insilicova_panel.setLayout(layout)

    def create_interva_panel(self):

        self.chbox_interva_rule = QCheckBox(
            "Count uncertain assignments as 'Undetermined'")
        self.chbox_interva_rule.setChecked(self.interva_rule)
        self.chbox_interva_rule.toggled.connect(self.set_interva_rule)
        gbox_dem = self.create_demographics_gbox()
        gbox_show = QGroupBox("Show Results")
        hbox_show = QHBoxLayout()
        self.btn_interva_table = QPushButton("Show \n CSMF Table")
        self.btn_interva_table.clicked.connect(self.interva_table)
        self.btn_interva_plot = QPushButton("Show \n CSMF Plot")
        self.btn_interva_plot.clicked.connect(self.interva_plot)
        self.btn_show_dem = QPushButton("Show \n Demographics")
        self.btn_show_dem.pressed.connect(
            lambda: self.run_table_dialog_dem("interva"))
        hbox_show.addWidget(self.btn_interva_table)
        hbox_show.addWidget(self.btn_interva_plot)
        hbox_show.addWidget(self.btn_show_dem)
        gbox_show.setLayout(hbox_show)

        gbox_save = QGroupBox("Save Results")
        vbox_save = QVBoxLayout()
        hbox_save = QHBoxLayout()
        self.btn_save_interva_table = QPushButton("Save CSMF Table")
        self.btn_save_interva_table.clicked.connect(
            self.save_interva_table)
        self.btn_save_interva_plot = QPushButton("Save CSMF Plot")
        self.btn_save_interva_plot.clicked.connect(self.save_interva_plot)
        self.btn_save_interva_indiv = QPushButton(
            "Save Individual \n Cause Assignments")
        self.btn_save_interva_indiv.clicked.connect(
            self.save_interva_indiv)
        hbox_save.addWidget(self.btn_save_interva_table)
        hbox_save.addWidget(self.btn_save_interva_plot)
        vbox_save.addLayout(hbox_save)
        vbox_save.addWidget(self.btn_save_interva_indiv)

        # self.chbox_interva_rule = QCheckBox(
        #     "Use InterVA Rule (this will include 'Undetermined' as a cause)")
        # self.chbox_interva_rule.setChecked(True)
        # self.chbox_interva_rule.toggled.connect(
        #     self.set_interva_rule)
        self.chbox_interva_include_probs = QCheckBox(
            "Include probability of top cause (with individual CODs)")
        self.chbox_interva_include_probs.setChecked(
            self.interva_include_probs)
        self.chbox_interva_include_probs.toggled.connect(
            self.set_interva_include_probs)
        self.chbox_interva_include_va_data = QCheckBox(
            "Include VA data (with individual CODs)")
        self.chbox_interva_include_va_data.setChecked(
            self.interva_include_va_data)
        self.chbox_interva_include_va_data.toggled.connect(
            self.set_interva_include_va_data)
        vbox_save.addWidget(self.chbox_interva_include_probs)
        vbox_save.addWidget(self.chbox_interva_include_va_data)
        gbox_save.setLayout(vbox_save)

        layout = QVBoxLayout()
        layout.addWidget(self.chbox_interva_rule)
        layout.addWidget(gbox_dem)
        layout.addWidget(gbox_show)
        layout.addWidget(gbox_save)
        layout.insertSpacing(1, 15)
        layout.insertSpacing(3, 50)
        layout.insertSpacing(5, 50)
        self.interva_panel = QWidget()
        self.interva_panel.setLayout(layout)

    # def create_smartva_panel(self):
    #     layout = QVBoxLayout()
    #
    #     vbox_table = QVBoxLayout()
    #     self.btn_smartva_table = QPushButton("Show \n CSMF Table")
    #     self.btn_smartva_table.clicked.connect(self.smartva_table)
    #     self.btn_save_smartva_table = QPushButton("Save CSMF Table")
    #     self.btn_save_smartva_table.clicked.connect(self.save_smartva_table)
    #     vbox_table.addWidget(self.btn_smartva_table)
    #     vbox_table.addWidget(self.btn_save_smartva_table)
    #
    #     vbox_plot = QVBoxLayout()
    #     self.btn_smartva_plot = QPushButton("Show \n CSMF Plot")
    #     self.btn_smartva_plot.clicked.connect(self.smartva_plot)
    #     self.btn_save_smartva_plot = QPushButton("Save CSMF Plot")
    #     self.btn_save_smartva_plot.clicked.connect(self.save_smartva_plot)
    #     vbox_plot.addWidget(self.btn_smartva_plot)
    #     vbox_plot.addWidget(self.btn_save_smartva_plot)
    #
    #     hbox = QHBoxLayout()
    #     hbox.addLayout(vbox_table)
    #     hbox.addLayout(vbox_plot)
    #     layout.addLayout(hbox)
    #     self.btn_save_smartva_indiv = QPushButton(
    #         "Save \n Individual Cause Assignments")
    #     self.btn_save_smartva_indiv.clicked.connect(self.save_smartva_indiv)
    #     layout.addWidget(self.btn_save_smartva_indiv)
    #     self.smartva_panel = QWidget()
    #     self.smartva_panel.setLayout(layout)

    def create_demographics_gbox(self):
        gbox_dem = QGroupBox("Select demographic groups")
        hbox_demographics = QHBoxLayout()
        age_option_set = ["all deaths",
                          "adult",
                          "child",
                          "neonate"]
        label_age = QLabel("age:")
        label_age.setMaximumWidth(30)
        self.options_combo_age = QComboBox()
        self.options_combo_age.addItems(age_option_set)
        self.options_combo_age.setCurrentIndex(
            age_option_set.index(self.options_age))
        self.options_combo_age.currentTextChanged.connect(
            self.set_options_age)
        sex_option_set = ["all deaths",
                          "female",
                          "male"]
        label_sex = QLabel("sex:")
        label_sex.setMaximumWidth(30)
        self.options_combo_sex = QComboBox()
        self.options_combo_sex.addItems(sex_option_set)
        self.options_combo_sex.setCurrentIndex(
            sex_option_set.index(self.options_sex))
        self.options_combo_sex.currentTextChanged.connect(
            self.set_options_sex)
        hbox_demographics.addWidget(label_age)
        hbox_demographics.addWidget(self.options_combo_age)
        hbox_demographics.addWidget(label_sex)
        hbox_demographics.addWidget(self.options_combo_sex)
        gbox_dem.setLayout(hbox_demographics)
        return gbox_dem

    def interva_plot(self):
        if self.interva_results is None:
            alert = QMessageBox()
            alert.setWindowTitle("openVA App")
            alert.setText(
                "Need to run InterVA5 first.")
            alert.exec()
        else:
            empty = self._check_empty_results("interva")
            if empty:
                alert = QMessageBox()
                alert.setWindowTitle("openVA App")
                alert.setText(
                    "There are no VA records for the selected group:\n"
                    f"age: {self.options_age},   sex: {self.options_sex}")
                alert.exec()
            else:
                self.interva_plot_dialog = PlotDialog(
                    results=self.interva_results,
                    algorithm="interva",
                    top=self.n_top_causes,
                    colors=self.plot_color,
                    age=self.options_age,
                    sex=self.options_sex,
                    interva_rule=self.interva_rule,
                    use_prop=self.results_use_prop)
                self.interva_plot_dialog.exec()

    def interva_table(self):
        if self.interva_results is None:
            alert = QMessageBox()
            alert.setWindowTitle("openVA App")
            alert.setText(
                "Need to run InterVA5 first.")
            alert.exec()
        else:
            empty = self._check_empty_results("interva")
            if empty:
                alert = QMessageBox()
                alert.setWindowTitle("openVA App")
                alert.setText(
                    "There are no VA records for the selected group:\n"
                    f"age: {self.options_age},   sex: {self.options_sex}")
                alert.exec()
            else:
                self.interva_table = TableDialog(
                    results=self.interva_results,
                    parent=self,
                    top=self.n_top_causes,
                    age=self.options_age,
                    sex=self.options_sex,
                    interva_rule=self.interva_rule,
                    use_prop=self.results_use_prop)
                self.interva_table.resize(self.interva_table.table.width(),
                                          self.interva_table.table.height())
                self.interva_table.exec()

    def save_interva_table(self):
        prop_scale = 100
        if self.results_use_prop:
            prop_scale = 1
        if self.interva_results is None:
            alert = QMessageBox()
            alert.setWindowTitle("openVA App")
            alert.setText(
                "Need to run InterVA5 first.")
            alert.exec()
        else:
            empty = self._check_empty_results("interva")
            if empty:
                alert = QMessageBox()
                alert.setWindowTitle("openVA App")
                alert.setText(
                    "There are no VA records for the selected group:\n"
                    f"age: {self.options_age},   sex: {self.options_sex}")
                alert.exec()
            else:
                age = self.options_age
                if self.options_age == "all deaths":
                    age = None
                sex = self.options_sex
                if self.options_sex == "all deaths":
                    sex = None
                csmf = utils.csmf(self.interva_results,
                                  top=self.n_top_causes,
                                  age=age,
                                  sex=sex,
                                  interva_rule=self.interva_rule)
                csmf.sort_values(ascending=False, inplace=True)
                csmf_df = csmf.reset_index()[0:self.n_top_causes]
                csmf_df.iloc[:, 1] *= prop_scale
                title = _make_title(age=self.options_age,
                                    sex=self.options_sex)
                csmf_df.rename(columns={"index": "Cause",
                                        0: title},
                               inplace=True)
                results_file_name = self._make_results_file_name("interva",
                                                                 "table")
                path = QFileDialog.getSaveFileName(self,
                                                   "Save CSMF (csv)",
                                                   results_file_name,
                                                   "CSV Files (*.csv)")
                if path != ("", ""):
                    # os.remove(path[0])
                    try:
                        csmf_df.round(4).to_csv(path[0], index=False)
                        # TODO: check when file was written if it existed
                        # previously
                        if os.path.isfile(path[0]):
                            alert = QMessageBox()
                            alert.setWindowTitle("openVA App")
                            alert.setText("results saved to" + path[0])
                            alert.exec()
                        else:
                            alert = QMessageBox()
                            alert.setWindowTitle("openVA App")
                            alert.setText(
                                f"ERROR: unable to save results to\n"
                                f"{path[0]}")
                            alert.exec()
                    except (OSError, PermissionError):
                        alert = QMessageBox()
                        alert.setWindowTitle("openVA App")
                        alert.setIcon(QMessageBox.Warning)
                        alert.setText(
                            f"Unable to save {path[0]}.\n" +
                            "(don't have permission or read-only file system)")
                        alert.exec()

    def save_interva_plot(self):
        if self.interva_results is None:
            alert = QMessageBox()
            alert.setWindowTitle("openVA App")
            alert.setText(
                "Need to run InterVA5 first.")
            alert.exec()
        else:
            empty = self._check_empty_results("interva")
            if empty:
                alert = QMessageBox()
                alert.setWindowTitle("openVA App")
                alert.setText(
                    "There are no VA records for the selected group:\n"
                    f"age: {self.options_age},   sex: {self.options_sex}")
                alert.exec()
            else:
                # results_file_name = "interva5_csmf.pdf"
                results_file_name = self._make_results_file_name("interva",
                                                                 "plot")
                path = QFileDialog.getSaveFileName(self,
                                                   "Save CSMF plot (pdf)",
                                                   results_file_name,
                                                   "PDF Files (*.pdf)")
                if path != ("", ""):
                    # os.remove(path[0])
                    try:
                        save_plot(
                            results=self.interva_results,
                            algorithm="interva",
                            top=self.n_top_causes,
                            file_name=path[0],
                            plot_colors=self.plot_color,
                            age=self.options_age,
                            sex=self.options_sex,
                            interva_rule=self.interva_rule,
                            use_prop=self.results_use_prop)
                        if os.path.isfile(path[0]):
                            alert = QMessageBox()
                            alert.setWindowTitle("openVA App")
                            alert.setText("results saved to" + path[0])
                            alert.exec()
                        else:
                            alert = QMessageBox()
                            alert.setWindowTitle("openVA App")
                            alert.setText(
                                "ERROR: unable to save results to\n" + path[0])
                            alert.exec()
                    except (OSError, PermissionError):
                        alert = QMessageBox()
                        alert.setWindowTitle("openVA App")
                        alert.setIcon(QMessageBox.Warning)
                        alert.setText(
                            f"Unable to save {path[0]}.\n" +
                            "(don't have permission or read-only file system)")
                        alert.exec()

    def save_interva_indiv(self):
        if self.interva_results is None:
            alert = QMessageBox()
            alert.setWindowTitle("openVA App")
            alert.setText(
                "Need to run InterVA5 first.")
            alert.exec()
        else:
            empty = self._check_empty_results("interva")
            if empty:
                alert = QMessageBox()
                alert.setWindowTitle("openVA App")
                alert.setText(
                    "There are no VA records for the selected group:\n"
                    f"age: {self.options_age},   sex: {self.options_sex}")
                alert.exec()
            else:
                # results_file_name = "interva5_individual_cod.csv"
                results_file_name = self._make_results_file_name("interva",
                                                                 "indiv")
                path = QFileDialog.getSaveFileName(self,
                                                   "Save CSMF (csv)",
                                                   results_file_name,
                                                   "CSV Files (*.csv)")
                if path != ("", ""):
                    how_to_merge = "outer"
                    keep = utils._get_cod_with_dem(self.interva_results)
                    if self.options_age != "all deaths":
                        keep = keep[keep["age"] == self.options_age]
                        how_to_merge = "inner"
                    if self.options_sex != "all deaths":
                        keep = keep[keep["sex"] == self.options_sex]
                        how_to_merge = "inner"
                    keep_id = keep["ID"]
                    out = self.interva_results.results["VA5"].copy()
                    out = out.drop(["WHOLEPROB"], axis=1)
                    if self.interva_include_probs is False:
                        out = out.drop(
                            ["PREGLIK", "LIK1", "LIK2", "LIK3", "INDET"],
                            axis=1)
                    out = out[out["ID"].isin(keep_id)]
                    if self.original_data_id in (None, "no ID column"):
                        out["ID"] = out["ID"].astype("int64")
                    if self.interva_include_va_data:
                        tmp_data = self._add_id_to_input_data()
                        tmp_data.columns = [col.split("-")[-1]
                                            for col in tmp_data.columns]
                        out = out.merge(tmp_data, how=how_to_merge, on="ID")
                    try:
                        out.to_csv(path[0], index=False)
                        if os.path.isfile(path[0]):
                            alert = QMessageBox()
                            alert.setWindowTitle("openVA App")
                            alert.setText("results saved to" + path[0])
                            alert.exec()
                        else:
                            alert = QMessageBox()
                            alert.setWindowTitle("openVA App")
                            alert.setText(
                                "ERROR: unable to save results to\n" + path[0])
                            alert.exec()
                    except (OSError, PermissionError):
                        alert = QMessageBox()
                        alert.setWindowTitle("openVA App")
                        alert.setIcon(QMessageBox.Warning)
                        alert.setText(
                            f"Unable to save {path[0]}.\n" +
                            "(don't have permission or read-only file system)")
                        alert.exec()

    def insilicova_plot(self):
        if self.insilicova_results is None:
            alert = QMessageBox()
            alert.setWindowTitle("openVA App")
            alert.setText(
                "Need to run InSilicoVA first.")
            alert.exec()
        else:
            empty = self._check_empty_results("insilicova")
            if empty:
                alert = QMessageBox()
                alert.setWindowTitle("openVA App")
                alert.setText(
                    "There are no VA records for the selected group:\n"
                    f"age: {self.options_age},   sex: {self.options_sex}")
                alert.exec()
            else:
                self.insilicova_plot_dialog = PlotDialog(
                    results=self.insilicova_results,
                    algorithm="insilicova",
                    parent=self,
                    top=self.n_top_causes,
                    colors=self.plot_color,
                    age=self.options_age,
                    sex=self.options_sex,
                    use_prop=self.results_use_prop)
                self.insilicova_plot_dialog.exec()

    def insilicova_table(self):
        if self.insilicova_results is None:
            alert = QMessageBox()
            alert.setWindowTitle("openVA App")
            alert.setText(
                "Need to run InSilicoVA first.")
            alert.exec()
        else:
            empty = self._check_empty_results("insilicova")
            if empty:
                alert = QMessageBox()
                alert.setWindowTitle("openVA App")
                alert.setText(
                    "There are no VA records for the selected group:\n"
                    f"age: {self.options_age},   sex: {self.options_sex}")
                alert.exec()
            else:
                self.insilicova_table = TableDialog(
                    self.insilicova_results,
                    self,
                    top=self.n_top_causes,
                    age=self.options_age,
                    sex=self.options_sex,
                    use_prop=self.results_use_prop)
                self.insilicova_table.resize(
                    self.insilicova_table.table.width(),
                    self.insilicova_table.table.height())
                self.insilicova_table.exec()

    def save_insilicova_table(self):
        prop_scale = 100
        if self.results_use_prop:
            prop_scale = 1
        no_subpop = (self.options_age == "all deaths" and
                     self.options_sex == "all deaths")
        if self.insilicova_results is None:
            alert = QMessageBox()
            alert.setWindowTitle("openVA App")
            alert.setText(
                "Need to run InSilicoVA first.")
            alert.exec()
        elif self._check_empty_results("insilicova"):
            alert = QMessageBox()
            alert.setWindowTitle("openVA App")
            alert.setText(
                "There are no VA records for the selected "
                f"group:\n age: {self.options_age},   "
                f"sex: {self.options_sex}")
            alert.exec()
        else:
            # results_file_name = "insilicova_csmf.csv"
            results_file_name = self._make_results_file_name("insilicova",
                                                             "table")
            path = QFileDialog.getSaveFileName(self,
                                               "Save CSMF (csv)",
                                               results_file_name,
                                               "CSV Files (*.csv)")
            if path != ("", ""):
                # os.remove(path[0])
                try:
                    n_top_causes = self.n_top_causes
                    csmf = self.insilicova_results.get_csmf(
                        top=n_top_causes)
                    if no_subpop:
                        csmf_df = csmf.sort_values(by="Mean",
                                                   ascending=False).copy()
                    else:
                        csmf_df = _insilicova_subpop(self.insilicova_results,
                                                     self.options_age,
                                                     self.options_sex,
                                                     self.n_top_causes)
                        csmf_df = csmf_df.sort_values(ascending=False)
                        csmf_df.name = "Mean"
                    csmf_df = csmf_df.reset_index()
                    csmf_df.rename(columns={"index": "Cause",
                                            "Mean": "CSMF (Mean)"},
                                   inplace=True)
                    csmf_df.iloc[:, 1:] *= prop_scale
                    csmf_df.round(4).to_csv(path[0], index=False)
                    if os.path.isfile(path[0]):
                        alert = QMessageBox()
                        alert.setWindowTitle("openVA App")
                        alert.setText("results saved to" + path[0])
                        alert.exec()
                    else:
                        alert = QMessageBox()
                        alert.setWindowTitle("openVA App")
                        alert.setText(
                            "ERROR: unable to save results to" + path[0])
                        alert.exec()
                except (OSError, PermissionError):
                    alert = QMessageBox()
                    alert.setWindowTitle("openVA App")
                    alert.setIcon(QMessageBox.Warning)
                    alert.setText(
                        f"Unable to save {path[0]}.\n" +
                        "(don't have permission or read-only file system)")
                    alert.exec()

    def save_insilicova_plot(self):
        if self.insilicova_results is None:
            alert = QMessageBox()
            alert.setWindowTitle("openVA App")
            alert.setText(
                "Need to run InSilicoVA first.")
            alert.exec()
        elif self._check_empty_results("insilicova"):
            alert = QMessageBox()
            alert.setWindowTitle("openVA App")
            alert.setText(
                "There are no VA records for the selected "
                f"group:\n age: {self.options_age},   "
                f"sex: {self.options_sex}")
            alert.exec()
        else:
            # results_file_name = "insilicova_csmf.pdf"
            results_file_name = self._make_results_file_name("insilicova",
                                                             "plot")
            path = QFileDialog.getSaveFileName(self,
                                               "Save CSMF plot (pdf)",
                                               results_file_name,
                                               "PDF Files (*.pdf)")
            if path != ("", ""):
                # os.remove(path[0])
                save_plot(results=self.insilicova_results,
                          algorithm="insilicova",
                          top=self.n_top_causes,
                          file_name=path[0],
                          plot_colors=self.plot_color,
                          age=self.options_age,
                          sex=self.options_sex,
                          use_prop=self.results_use_prop)
                if os.path.isfile(path[0]):
                    alert = QMessageBox()
                    alert.setWindowTitle("openVA App")
                    alert.setText("results saved to" + path[0])
                    alert.exec()
                else:
                    alert = QMessageBox()
                    alert.setWindowTitle("openVA App")
                    alert.setText(
                        "ERROR: unable to save results to" + path[0])
                    alert.exec()

    def save_insilicova_indiv(self):
        if self.insilicova_results is None:
            alert = QMessageBox()
            alert.setWindowTitle("openVA App")
            alert.setText(
                "Need to run InSilicoVA first.")
            alert.exec()
        elif self._check_empty_results("insilicova"):
            alert = QMessageBox()
            alert.setWindowTitle("openVA App")
            alert.setText(
                "There are no VA records for the selected "
                f"group:\n age: {self.options_age},   "
                f"sex: {self.options_sex}")
            alert.exec()
        else:
            # results_file_name = "insilicova_individual_cod.csv"
            results_file_name = self._make_results_file_name("insilicova",
                                                             "indiv")
            path = QFileDialog.getSaveFileName(self,
                                               "Save CSMF (csv)",
                                               results_file_name,
                                               "CSV Files (*.csv)")
            if path != ("", ""):
                try:
                    out = self.prepare_insilicova_indiv_cod(
                        self.insilicova_results)
                    out.to_csv(path[0], index=False)
                    if os.path.isfile(path[0]):
                        alert = QMessageBox()
                        alert.setWindowTitle("openVA App")
                        alert.setText("results saved to" + path[0])
                        alert.exec()
                    else:
                        alert = QMessageBox()
                        alert.setWindowTitle("openVA App")
                        alert.setText(
                            "ERROR: unable to save results to" + path[0])
                        alert.exec()
                except (OSError, PermissionError):
                    alert = QMessageBox()
                    alert.setWindowTitle("openVA App")
                    alert.setIcon(QMessageBox.Warning)
                    alert.setText(
                        f"Unable to save {path[0]}.\n" +
                        "(don't have permission or read-only file system)")
                    alert.exec()

    def prepare_insilicova_indiv_cod(self, results):
        all_results = []
        how_to_merge = "outer"
        for i in range(results.indiv_prob.shape[0]):
            row = results.indiv_prob.iloc[i].copy()
            top_causes = row.sort_values(ascending=False)[0:self.n_top_causes]
            if self.insilicova_include_probs:
                labels = ["Cause", "Prob"] * self.n_top_causes
                numbers = []
                [numbers.extend([str(a)]*2) for a in
                 range(1, self.n_top_causes + 1)]
                col_names = [a + b for a, b in zip(labels, numbers)]
                values = [i for j in top_causes.items() for i in j]
                all_results.append(
                    DataFrame([values], columns=col_names, index=[row.name]))
            else:
                col_names = ["Cause" + str(i) for i in
                             range(1, self.n_top_causes + 1)]
                all_results.append(
                    DataFrame([top_causes.index.tolist()],
                              columns=col_names,
                              index=[row.name]))
        indiv_cod = pd_concat(all_results)
        indiv_cod = indiv_cod.reset_index(names="ID")
        if (self.options_age != "all deaths" or
                self.options_sex != "all deaths"):
            how_to_merge = "inner"
            age_groups = []
            sex_groups = []
            if self.options_age == "all deaths":
                age_groups = ["neonate", "child", "adult"]
            else:
                age_groups.append(self.options_age)
            if self.options_sex == "all deaths":
                sex_groups = ["female", "male"]
            else:
                sex_groups.append(self.options_sex)

            dem_groups = self.insilicova_results.data_checked.apply(
                utils._get_dem_groups, axis=1)
            # dem_groups = DataFrame(list(dem_groups)).set_index("ID")
            dem_groups = DataFrame(list(dem_groups))
            # indiv_cod = pd_concat([indiv_cod, dem_groups], axis=1)
            indiv_cod = indiv_cod.merge(dem_groups, on="ID")
            subpop_index = (indiv_cod["age"].isin(age_groups)) & (
                indiv_cod["sex"].isin(sex_groups))
            indiv_cod = indiv_cod[subpop_index]
            indiv_cod = indiv_cod.drop(columns=["age", "sex"])

        if self.insilicova_include_va_data:
            tmp_data = self._add_id_to_input_data()
            tmp_data.columns = [col.split("-")[-1] for col in tmp_data.columns]
            indiv_cod = indiv_cod.merge(tmp_data, how=how_to_merge, on="ID")

        if (self.options_age == "all deaths" and
                self.options_sex == "all deaths"):
            if self.original_data_id in (None, "no ID column"):
                indiv_cod = indiv_cod.sort_values(by="ID")
            else:
                indiv_cod = indiv_cod.set_index("ID")
                indiv_cod = indiv_cod.reindex(
                    self.original_data[self.original_data_id])
                indiv_cod = indiv_cod.reset_index(names="ID")

        return indiv_cod

    def save_insilicova_indiv_all(self):
        how_to_merge = "outer"
        if self.insilicova_results is None:
            alert = QMessageBox()
            alert.setWindowTitle("openVA App")
            alert.setText(
                "Need to run InSilicoVA first.")
            alert.exec()
        elif self._check_empty_results("insilicova"):
            alert = QMessageBox()
            alert.setWindowTitle("openVA App")
            alert.setText(
                "There are no VA records for the selected "
                f"group:\n age: {self.options_age},   "
                f"sex: {self.options_sex}")
            alert.exec()
        else:
            # results_file_name = "insilicova_individual_cod.csv"
            results_file_name = self._make_results_file_name("insilicova",
                                                             "indiv")
            path = QFileDialog.getSaveFileName(self,
                                               "Save CSMF (csv)",
                                               results_file_name,
                                               "CSV Files (*.csv)")
            if path != ("", ""):
                try:
                    out = self.insilicova_results.indiv_prob.copy()
                    if self.original_data_id in (None, "no ID column"):
                        out = out.sort_index()
                    else:
                        out = out.reindex(
                            self.original_data[self.original_data_id])
                    # out = out.reset_index(names="ID")
                    indiv_cod = self.prepare_insilicova_indiv_cod_all(out)
                    indiv_cod.to_csv(path[0], index=False)
                    if os.path.isfile(path[0]):
                        alert = QMessageBox()
                        alert.setWindowTitle("openVA App")
                        alert.setText("results saved to" + path[0])
                        alert.exec()
                    else:
                        alert = QMessageBox()
                        alert.setWindowTitle("openVA App")
                        alert.setText(
                            "ERROR: unable to save results to" + path[0])
                        alert.exec()
                except (OSError, PermissionError):
                    alert = QMessageBox()
                    alert.setWindowTitle("openVA App")
                    alert.setIcon(QMessageBox.Warning)
                    alert.setText(
                        f"Unable to save {path[0]}.\n" +
                        "(don't have permission or read-only file system)")
                    alert.exec()

    def prepare_insilicova_indiv_cod_all(self, results):
        how_to_merge = "outer"
        indiv_cod = results.reset_index(names="ID")
        if (self.options_age != "all deaths" or
                self.options_sex != "all deaths"):
            how_to_merge = "inner"
            age_groups = []
            sex_groups = []
            if self.options_age == "all deaths":
                age_groups = ["neonate", "child", "adult"]
            else:
                age_groups.append(self.options_age)
            if self.options_sex == "all deaths":
                sex_groups = ["female", "male"]
            else:
                sex_groups.append(self.options_sex)

            dem_groups = self.insilicova_results.data_checked.apply(
                utils._get_dem_groups, axis=1)
            # dem_groups = DataFrame(list(dem_groups)).set_index("ID")
            dem_groups = DataFrame(list(dem_groups))
            # indiv_cod = pd_concat([results, dem_groups], axis=1)
            indiv_cod = indiv_cod.merge(dem_groups, on="ID")
            subpop_index = (indiv_cod["age"].isin(age_groups)) & (
                indiv_cod["sex"].isin(sex_groups))
            indiv_cod = indiv_cod[subpop_index]
            indiv_cod = indiv_cod.drop(columns=["age", "sex"])

        if self.insilicova_include_va_data:
            tmp_data = self._add_id_to_input_data()
            tmp_data.columns = [col.split("-")[-1] for col in tmp_data.columns]
            indiv_cod = indiv_cod.merge(tmp_data, how=how_to_merge, on="ID")

        if (self.options_age == "all deaths" and
                self.options_sex == "all deaths"):
            if self.original_data_id in (None, "no ID column"):
                indiv_cod = indiv_cod.sort_values(by="ID")
            else:
                indiv_cod = indiv_cod.set_index("ID")
                indiv_cod = indiv_cod.reindex(
                    self.original_data[self.original_data_id])
                indiv_cod = indiv_cod.reset_index(names="ID")

        return indiv_cod

    # def smartva_plot(self):
    #     alert = QMessageBox()
    #     alert.setWindowTitle("openVA App")
    #     alert.setText("SmartVA is not available (it is based on Python 2" +
    #                   "which is no longer supported by the Python Software " +
    #                   "Foundation).  It will be included when a version " +
    #                   "based on Python 3 is released.")
    #     alert.exec()

    # def smartva_table(self):
    #     alert = QMessageBox()
    #     alert.setWindowTitle("openVA App")
    #     alert.setText("SmartVA is not available (it is based on Python 2" +
    #                   "which is no longer supported by the Python Software " +
    #                   "Foundation).  It will be included when a version " +
    #                   "based on Python 3 is released.")
    #     alert.exec()

    # def save_smartva_plot(self):
    #     alert = QMessageBox()
    #     alert.setWindowTitle("openVA App")
    #     alert.setText("SmartVA is not available (it is based on Python 2" +
    #                   "which is no longer supported by the Python Software " +
    #                   "Foundation).  It will be included when a version " +
    #                   "based on Python 3 is released.")
    #     alert.exec()
    #
    # def save_smartva_table(self):
    #     alert = QMessageBox()
    #     alert.setWindowTitle("openVA App")
    #     alert.setText("SmartVA is not available (it is based on Python 2" +
    #                   "which is no longer supported by the Python Software " +
    #                   "Foundation).  It will be included when a version " +
    #                   "based on Python 3 is released.")
    #     alert.exec()

    # def save_smartva_indiv(self):
    #     alert = QMessageBox()
    #     alert.setWindowTitle("openVA App")
    #     alert.setText("SmartVA is not available (it is based on Python 2" +
    #                   "which is no longer supported by the Python Software " +
    #                   "Foundation).  It will be included when a version " +
    #                   "based on Python 3 is released.")
    #     alert.exec()

    def run_table_dialog_dem(self, algorithm):
        if algorithm == "interva":
            results = self.interva_results
        else:
            results = self.insilicova_results
        if results is None:
            alert = QMessageBox()
            alert.setWindowTitle("openVA App")
            alert.setText(
                "No results available.  Please load data in the expected "
                "format and/or run a VA algorithm.")
            alert.exec()
        else:
            if algorithm == "interva":
                dem_results = utils._get_cod_with_dem(results)
                self.table_dialog = DemTableDialog(dem_results, self)
                self.table_dialog.resize(self.table_dialog.view.width(),
                                         self.table_dialog.view.height())
                self.table_dialog.exec()
            else:
                dem_results = results.data_checked.apply(
                    utils._get_dem_groups,
                    axis=1)
                dem_results = DataFrame(list(dem_results))
                self.table_dialog = DemTableDialog(dem_results, self)
                self.table_dialog.resize(self.table_dialog.view.width(),
                                         self.table_dialog.view.height())
                self.table_dialog.exec()

    def update_interva_results(self, new_interva_results):
        self.interva_results = new_interva_results

    def update_interva_tmp_dir(self, tmp_dir):
        self.interva_tmp_dir = tmp_dir

    def update_insilicova(self, new_insilicova_results):
        self.insilicova_results = new_insilicova_results

    # def update_smartva(self, new_smartva_results):
    #     self.smartva_results = new_smartva_results

    def set_n_top_causes(self, n):
        self.n_top_causes = n

    def set_results_use_prop(self, checked):
        if checked:
            self.results_use_prop = True
        else:
            self.results_use_prop = False

    def set_options_sex(self, sex):
        self.options_sex = sex

    def set_options_age(self, age):
        self.options_age = age

    def set_plot_color(self, color):
        self.plot_color = color

    def set_insilicova_include_probs(self, checked):
        if checked:
            self.insilicova_include_probs = True
        else:
            self.insilicova_include_probs = False

    def set_insilicova_include_va_data(self, checked):
        if checked:
            self.insilicova_include_va_data = True
        else:
            self.insilicova_include_va_data = False

    def set_interva_rule(self, checked):
        if checked:
            self.interva_rule = True
        else:
            self.interva_rule = False

    def set_interva_include_probs(self, checked):
        if checked:
            self.interva_include_probs = True
        else:
            self.interva_include_probs = False

    def set_interva_include_va_data(self, checked):
        if checked:
            self.interva_include_va_data = True
        else:
            self.interva_include_va_data = False

    def _check_empty_results(self, algorithm):
        empty = True
        if algorithm == "insilicova":
            if self.insilicova_results is not None:
                out = self.insilicova_results.data_checked.apply(
                    utils._get_dem_groups,
                    axis=1)
                out = DataFrame(list(out))
        else:
            if self.interva_results is not None:
                out = utils._get_cod_with_dem(self.interva_results)
        if self.options_age != "all deaths":
            out = out[out["age"] == self.options_age]
        if self.options_sex != "all deaths":
            out = out[out["sex"] == self.options_sex]
        empty = out.shape[0] == 0
        return empty

    def _make_results_file_name(self, algorithm, fnc):
        results_file_name = f"{algorithm}"
        if self.options_age != "all deaths":
            results_file_name += f"_{self.options_age}"
        if self.options_sex != "all deaths":
            results_file_name += f"_{self.options_sex}"
        if fnc == "plot":
            results_file_name += "_csmf.pdf"
        elif fnc == "table":
            results_file_name += "_csmf.csv"
        else:
            results_file_name += "_individual_cod.csv"
        if self.working_dir != "":
            results_file_name = os.path.join(self.working_dir,
                                             results_file_name)
        return results_file_name

    def _add_id_to_input_data(self):
        tmp_data = self.original_data.copy()
        if self.original_data_id in (None, "no ID column"):
            tmp_data["ID"] = [i + 1 for i in self.original_data.index]
        else:
            tmp_data["ID"] = tmp_data[self.original_data_id].copy()
        return tmp_data
