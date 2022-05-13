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
from matplotlib import pyplot
from numpy import linspace

import os
os.chdir("src/main/python/")
from pandas import read_csv
va_input = read_csv("randomva5.csv")


class InterVA5:

    # TODO: add subsetting (e.g., neonates)
    def __init__(self, va_input):
        self.va_input = va_input
        #self.progress_bar = progress_bar
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
        self.csmf = self.causes["cause"].value_counts(normalize=True,
                                                      sort=True,
                                                      ascending=False)

    def plot(self, top_causes):
        csmf_top_n = self.csmf[0:top_causes]
        plt_df = csmf_top_n.sort_values(ascending=True)
        pyplot.style.use("ggplot")
        cm_greys = pyplot.get_cmap("Greys")
        linspace_greys = linspace(0.5, 0.9, top_causes)
        colors = cm_greys(linspace_greys)
        plt = plt_df.plot.barh(title="CSMF", color=colors)
        return plt
