# -*- coding: utf-8 -*-

"""
pyopenva.efficient
~~~~~~~~~~~~~~
This module creates a stacked layout to walk through the analysis step-by-step.
"""

import os

from insilicova.api import InSilicoVA
from insilicova.structures import InSilico
from insilicova.exceptions import HaltGUIException, InSilicoVAException
from interva.interva5 import InterVA5
from PyQt5.QtCore import QObject, pyqtSignal


class InSilicoVAWorker(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(int)
    state = pyqtSignal(str)
    insilicova_results = pyqtSignal(InSilico)
    insilicova_errors = pyqtSignal(dict)
    insilicova_warnings = pyqtSignal(dict)

    def __init__(self, data, data_type, n_sim, burnin, thin, auto_length,
                 seed, gui_ctrl):
        super().__init__()
        self.input = data
        self.data_type = data_type
        self.n_sim = n_sim
        self.burnin = burnin
        self.thin = thin
        self.auto_length = auto_length
        self.seed = seed
        self.gui_ctrl = gui_ctrl

    def run(self):
        try:
            insilicova_out = InSilicoVA(self.input,
                                        data_type=self.data_type,
                                        n_sim=self.n_sim,
                                        thin=self.thin,
                                        burnin=self.burnin,
                                        auto_length=self.auto_length,
                                        seed=self.seed,
                                        openva_app=self.progress,
                                        state=self.state,
                                        gui_ctrl=self.gui_ctrl)
            try:
                results = insilicova_out.get_results()
                self.insilicova_results.emit(results)
                self.insilicova_errors.emit(results.errors)
                self.insilicova_warnings.emit(results.warnings)
                msg = "InSilicoVA results are ready"
                n_failed = (insilicova_out.original_data.shape[0] -
                            len(insilicova_out.results.id))
                if n_failed > 0:
                    msg += f" ({n_failed} deaths failed data checks)"
                self.state.emit(msg)
                self.finished.emit()
            except InSilicoVAException:
                self.insilicova_errors.emit(insilicova_out._error_log)
                self.insilicova_warnings.emit(insilicova_out._warning)
                if hasattr(insilicova_out, "_data_check") is False:
                    self.insilicova_warnings.emit(
                        {"msg": "No valid records for data consistency check"})
                self.state.emit(
                    "Data do not have any valid VA records (no results "
                    "available).\nPlease reload data in the expected format.")
                self.finished.emit()
        except HaltGUIException:
            self.state.emit("InSilicoVA stopped (no results).")
            self.progress.emit(0)
            self.finished.emit()


class InterVAWorker(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(int)
    state = pyqtSignal(str)
    log = pyqtSignal(str)
    interva_results = pyqtSignal(InterVA5)

    def __init__(self, data, hiv, malaria, directory, gui_ctrl):
        super().__init__()
        self.input = data
        self.hiv = hiv
        self.malaria = malaria
        self.directory = directory
        self.gui_ctrl = gui_ctrl

    def run(self):
        try:
            iv5_out = InterVA5(self.input,
                               hiv=self.hiv,
                               malaria=self.malaria,
                               write=True,
                               directory=self.directory,
                               openva_app=self.progress,
                               gui_ctrl=self.gui_ctrl)
            try:
                os.getcwd()
            except FileNotFoundError:
                os.chdir(self.directory)
            iv5_out.run()
            self.log.emit("ready")
            if (iv5_out.results["VA5"] is None or
                    len(iv5_out.results) == 0):
                self.state.emit(
                    "Data do not have any valid VA records (no results "
                    "available).\nPlease reload data in the expected format.")
                self.finished.emit()
            else:
                self.interva_results.emit(iv5_out)
                n_failed = (iv5_out.va_input.shape[0] -
                            iv5_out.results["VA5"].shape[0])
                msg = "InterVA5 results are ready"
                if n_failed > 0:
                    msg += f" ({n_failed} deaths failed data checks)"
                self.state.emit(msg)
                self.finished.emit()
        except RuntimeError:
            self.state.emit("InterVA stopped (no results).")
            self.progress.emit(0)
            self.finished.emit()
        except KeyError:
            self.state.emit(
                "ERROR: InterVA not able to assign any causes.\n"
                "Please check you have valid VA records.")
            self.progress.emit(0)
            self.finished.emit()
