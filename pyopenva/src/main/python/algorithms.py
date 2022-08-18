# -*- coding: utf-8 -*-

"""
pyopenva.algorithms
~~~~~~~~~~~~~~
This module provides mock versions of the algorithms.
"""

from data import CAUSETEXTV5
from random import choices, sample
from time import sleep
from pandas import concat, DataFrame
from matplotlib.pyplot import gca, get_cmap
from numpy import linspace
from PyQt5.QtWidgets import QApplication

# import os
# os.getcwd()
# os.chdir("src/main/python/")
# from pandas import read_csv
# va_input = read_csv("randomva5.csv")


class InterVA5:

    # TODO: add subsetting (e.g., neonates)
    def __init__(self, va_input, app_instance):
        self.va_input = va_input
        self.app_instance = app_instance
        self.causes = DataFrame({"cause": [], "code": []})
        cod_dict = {key: value for key, value in CAUSETEXTV5.items() if
                    "a_" not in key and "c_" not in key}
        self.cod = cod_dict
        self.csmf = None

    def assign_causes(self):
        n_deaths = self.va_input.shape[0]
        csmf_weights = sample([1, 100, 500, 1000, 1500],
                              counts=[40, 10, 5, 4, 2],
                              k=61)
        for i in range(n_deaths):
            sleep(.03)
            next_id = self.va_input['ID'][i]
            next_cause = choices(list(self.cod.values()),
                                 weights=csmf_weights)[0]
            next_row = DataFrame(next_cause, index=[next_id])
            self.causes = concat([self.causes, next_row])
            progress = int(100 * i/n_deaths)
            self.app_instance.interva_progress_bar.setValue(progress)
            QApplication.processEvents()

        self.csmf = self.causes["cause"].value_counts(normalize=True,
                                                      sort=True,
                                                      ascending=False)
        self.app_instance.interva_progress_bar.setValue(100)
        QApplication.processEvents()

    def plot(self, top_causes=5, ax=None):
        csmf_top_n = self.csmf[0:top_causes]
        plt_series = csmf_top_n.sort_values(ascending=True)
        # style.use("ggplot")
        cm_greys = get_cmap("Greys")
        linspace_greys = linspace(0.5, 0.9, top_causes)
        colors = cm_greys(linspace_greys)
        if ax is None:
            ax = gca()
        ax.barh(plt_series.index.to_list(),
                plt_series.to_list(),
                color=colors)
        ax.set(title="CSMF")
        #plt.setp(labels, rotation=45, horizontalalignment='right')
        return ax

        #pyplot.style.use("ggplot")
        #cm_greys = pyplot.get_cmap("Greys")
        #linspace_greys = linspace(0.5, 0.9, top_causes)
        #colors = cm_greys(linspace_greys)
        #plt = plt_df.plot.barh(title="CSMF", color=colors)
        #return plt

# interva = InterVA5(va_input)
# interva.assign_causes()
# csmf_plot = interva.plot()
