#parse experiment type

import os
import re
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
#import pyvttbl as pt
#import statsmodels
import statsmodels.api as sm
from statsmodels.formula.api import ols
from scipy import stats as st
from statsmodels.stats.multicomp import pairwise_tukeyhsd
from statsmodels.stats.multicomp import MultiComparison

from lib import FR_Buddy as frb
from lib import sc_assess as sca



class EXparse:
    def __init__(self):
        self.test = "test"

    def parse_settings(self, excel_file):
        """
        goes to the intro tab in the excel file and pulls out the important
        settings then returns those settings
        """
        intro_frame = excel_file.parse(sheet_name = "Intro")
        if ", " in intro_frame["Sheets"][0]:
            sheets_to_return = intro_frame["Sheets"][0].split(", ")
        else:
            sheets_to_return = intro_frame["Sheets"][0]
        return (intro_frame["Experiment"][0],
                 intro_frame["Stats"][0],
                 sheets_to_return)

    def processFile(self):
        cwd = os.getcwd()
        files = os.listdir(cwd)
        txtRe = re.compile('(?P<file>\w+).xlsx', re.I)
        for file in files:
            match = txtRe.match(file)
            if match:
                excel_file = pd.ExcelFile(file)
                if (excel_file.sheet_names[0]=="Intro") and (["Experiment", "Stats", "Sheets"] == excel_file.parse(sheet_name = "Intro").columns.tolist()):
                    print(file)
                    experiment, stats, list_of_sheets = (
                                               self.parse_settings(excel_file))

                    if experiment == "Sucrose Consumption":
                        temp = sca.SC(file)
                        temp.pointplot()
                        temp.boxplot()
                        # This is likely a good place to do the stats if you're
                        # going to do this on a per study basis.

                    if experiment == "Self Administration":
                        temp = frb.PR(file)
                        temp.PR_pointplot(pooled=False,save=True )
                        temp.PR_boxplot(pooled=False, save=True)
                        # This is likely a good place to do the stats on a per
                        # study basis.
                else:
                    pass
            else:
                pass
