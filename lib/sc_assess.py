import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
#import pyvttbl as pt
#import statsmodels
import statsmodels.api as sm
from statsmodels.formula.api import ols
from statsmodels.stats.multicomp import pairwise_tukeyhsd
from statsmodels.stats.multicomp import MultiComparison
import datetime


class SC:

    def __init__(self, filename):
        self.filename = filename
        self.excel = pd.ExcelFile(filename)
        self.experiment_type, self.statistics, self.sheet_names =(
                                            self.parse_settings (self.excel))
        self.base_frame = self.pull_sucrose_data(self.excel)
        self.sc_columns = ["D1", "D7", "D14", "D21", "D28", "D35", "D42"]
        self.seaborn_frame = self.build_seaborn_dataframe()
        self.df_dropna = self.seaborn_frame.dropna(axis='index', how='any')


    def parse_settings(self, excel_file):
        """
        goes to the intro tab in the excel file and pulls out the
        important settings, returns those settings.
        """
        intro_frame = excel_file.parse(sheet_name = "Intro")
        if ", " in intro_frame["Sheets"][0]:
            sheets_to_return = intro_frame["Sheets"][0].split(", ")
        else:
            sheets_to_return = intro_frame["Sheets"][0]
        return (intro_frame["Experiment"][0],
                 intro_frame["Stats"][0],
                 sheets_to_return)

    def adjacent_difference(self, suffix):
        """
        data_frame= pandas.DataFrame() object
        suffix= string indicating which column should be queried
        returns a pandas.Series() object
        """
        col_1 = "Pre_"+suffix
        col_2 = "Post_"+suffix
        return self.base_frame[col_1]-self.base_frame[col_2]

    def pull_sucrose_data(self,excel_file):
        """
        input: pandas.ExcelFile() object
        output: dataframe compatible with seaborn plotting"""
        base_frame = excel_file.parse(sheet_name = self.sheet_names)
        return base_frame
        # I want to do a more robust check here but the rest of the structure
        # makes this less important at the moment.  When I remove those hard
        # coded checks in other areas, this would be a good place to improve
        # the robustness of the code.
        if len(base_frame.columns) != 8:
            print ("There is a problem, incorrect number of columns supplied")
        if base_frame.columns != required_column_names:
            print ("Uh oh, column names don't match!")
        else:
            return base_frame

    def build_seaborn_dataframe(self):
        """
        takes a dataframe and uses other functions to complete it
        input: pandas.DataFrame() object
        output: pandas.DataFrame() object - suitable for graphing
        """
        time_point = 0
        output = pd.DataFrame(columns=["Treatment", "Time Point", "volume"])
        for column in self.sc_columns:
            temp_frame = pd.DataFrame()
            temp_frame["Treatment"] = self.base_frame["Treatment"]
            temp_frame["Time Point"] = self.sc_columns[time_point]
            temp_frame["volume"] = self.adjacent_difference(column)
            output = pd.merge_ordered(output, temp_frame, fill_method='ffill')
            time_point += 1
        return output




    def pointplot(self, save=True):
        temp = self.seaborn_frame
        temp = temp.dropna(axis="index", how="any")
        temp_na_timepoints = set(temp["Time Point"])
        output_columns = [value for value in self.sc_columns
                          if value in temp_na_timepoints]
        plt.figure()
        ax = sns.pointplot(x="Time Point",
                           y="volume",
                           data=temp,
                           hue="Treatment",
                           ci=95,
                           order=output_columns,
                           capsize=0.1)
        handles, labels = ax.get_legend_handles_labels()
        ax.legend(handles[:6], labels[:6])
        plt.show()
        if save:
            plt.savefig(self.filename.split(".")[0]
                        +"_Sucrose_Consumption-pointplot_"
                        +datetime.datetime.today().strftime('%Y-%m-%d')
                        +".png")
            plt.close()

    def boxplot(self, save=True):
        """
        graph: a seaborn-style dataframe
        """
        temp = self.seaborn_frame
        temp = temp.dropna(axis="index", how="any")
        temp_na_timepoints = set(temp["Time Point"])
        output_columns = [value for value in self.sc_columns
                          if value in temp_na_timepoints]
        plt.figure()
        ax = sns.swarmplot(x="Time Point",
                           y="volume",
                           hue="Treatment",
                           data=temp,
                           size=5,
                           dodge=True,
                           order=output_columns,
                           linewidth=0.5,
                           edgecolor="black")
        ax = sns.boxplot(x="Time Point",
                         y="volume",
                         hue="Treatment",
                         data=temp,
                         order=output_columns)
        handles, labels = ax.get_legend_handles_labels()
        ax.legend(handles[:3], labels[:3])
        plt.show()
        if save:
            plt.savefig(self.filename.split(".")[0]
                        +"_Sucrose_Consumption-boxplot_"
                        +datetime.datetime.today().strftime('%Y-%m-%d')
                        +".png")
            plt.close()
    def ANOVA(self):
        """
        Hardcoded to use volume as the parameter and treatment as the grouping
        identifier. This is a limitation due to these values being in a string,
        can work around this later by building a string according to the format
        below.
        """


        results = ols ('volume ~ C(Treatment)', data=self.df_dropna).fit()
        print (results.summary())
        mc = MultiComparison(self.seaborn_frame['volume'],
                             self.seaborn_frame['Treatment'])
        mc_results = mc.tukeyhsd()
        print (mc_results)

    def ANOVA_TimePoints(self):
        """
        Hardcoded to use volume as the parameter and treatment as the grouping
        identifier. This is a limitation due to these values being in a string,
        can work around this later by building a string according to the format
        below.
        """
        for timepoint in self.sc_columns:
            print("Time point: " + timepoint)
            df_timepoint = self.df_dropna.loc[self.df_dropna['Time Point'] == timepoint]
            results = ols ('volume ~ C(Treatment)', data=df_timepoint).fit()
            print (results.summary())
            mc = MultiComparison(df_timepoint['volume'],
                                df_timepoint['Treatment'])
            mc_results = mc.tukeyhsd()
            print (mc_results)
