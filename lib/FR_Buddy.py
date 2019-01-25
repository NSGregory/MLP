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
from scipy import stats as st
import datetime

class PR:
    #Currently specifying these labels, though a way to detect the differences
    #between labels automatically is likely feasable.  This approach isn't
    #easily scalable.
    male_treatment_labels = ["M-U50", "M-Pain", "M-Ctrl"]
    female_treatment_labels = ["F-U50", "F-Pain", "F-Ctrl"]

    def __init__(self, filename):
        self.filename = filename
        self.excel = pd.ExcelFile(filename)
        self.experiment_type, self.statistics, self.sheet_names = (
                                               self.parse_settings(self.excel)
                                               )
        self.base_frame = self.pull_selfAdmin_data(self.excel)
        self.pr_columns = ["PR_0", "PR_1", "PR_7", "PR_14", "PR_21", "PR_28"]
        self.seaborn_frame = self.make_PR_seaborn()
        self.df_dropna = self.seaborn_frame.dropna(axis='index', how='any')

    def parse_settings(self, excel_file):
        """
        This goes to the intro tab in the excel file and pulls out the
        important settings and then returns those settings.
        """
        intro_frame = excel_file.parse(sheet_name = "Intro")
        if ", " in intro_frame["Sheets"][0]:
            sheets_to_return = intro_frame["Sheets"][0].split(", ")
        else:
            sheets_to_return = intro_frame["Sheets"][0]
        return (intro_frame["Experiment"][0],
                 intro_frame["Stats"][0],
                 sheets_to_return)



    def pull_selfAdmin_data(self, excel_file):
        """Assumes that the data is stored in an excel sheet
        and does some basic verification
        input: pandas.ExcelFile() object
        output: dataframe compatible with seaborn plotting"""
        base_frame = excel_file.parse(sheet_name = "Correct")

        if len(base_frame.columns) != 20:
            print ("There is a problem, incorrect number of columns supplied")
        else:
            return base_frame

    def build_seaborn_dataframe(base_frame):
        """
        This assumes the first two columns are dedicated to identifying the
        treatment and animal.
        input: data frame
        output: plotting viable data frame
        """
        in_range_frame = base_frame.iloc[:,2:len(base_frame.columns)-1]
        raw_data_columns = in_range_frame.columns
        time_point = 1
        output = pd.DataFrame(columns=["Treatment", "Time Point", "Count"])
        for column in raw_data_columns:
            temp_frame = pd.DataFrame()
            temp_frame["Treatment"] = base_frame["Treatment"]
            temp_frame["Time Point"] = time_point
            temp_frame["Count"] = base_frame[column]
            output = pd.merge_ordered(output, temp_frame, fill_method='ffill')
            time_point += 1
        return output
        return in_range_frame

    def selective_seaborn_dataframe(base_frame, treatment):
        """
        This assumes the first two columns are dedicated to identifying the
        treatment and animal.
        input: data frame
        output: plottable data frame
        """
        in_range_frame = base_frame.iloc[:,2:len(base_frame.columns)-1]
        raw_data_columns = in_range_frame.columns
        time_point = 1
        output = pd.DataFrame(columns=["Treatment", "Time Point", "Count"])
        for column in raw_data_columns:
            temp_frame = pd.DataFrame()
            temp_frame["Treatment"] = base_frame["Treatment"]
            temp_frame["Time Point"] = time_point
            temp_frame["Count"] = base_frame[column]
            output = pd.merge_ordered(output, temp_frame, fill_method='ffill')
            time_point += 1
        return output.loc[output["Treatment"] == treatment]


    def get_treatment_names(sheet):
        #TODO: Determine if this function is still necessary.
        """
        Takes a sheet and finds the unique values under the Treatment column.
        """
        base_frame = self.excel.parse(sheet_name=sheet)
        return set(base_frame["Sheets"])

    def build_dataframe_across_sheets(treatment):
        #TODO: Determine if this function is still necessary.
        """
        Takes a treatment/experimental group name and looks for it across the
        listed sheets and combines them into a single dataframe which is
        returned.
        """

        output = pd.DataFrame(columns=["Treatment", "Time Point", "Count"])
        for current in self.sheet_names:
            temp_frame = selective_seaborn_dataframe(
                self.excel.parse(sheet_name=current),
                treatment
                )
            temp_frame["Treatment"] = treatment+"-"+current

            output = pd.merge_ordered(output, temp_frame, fill_method='ffill')
        return output

    def build_graphs_by_treatment():
        #TODO: Determine if this function is still necessary.
        """
        Pulls the names of all the treatments and then uses them to make
        individual graphs by treatment.
        intput: none (does require global variables to be defined currently)
        output: graphs from dataframes
        """
        treatment_list = get_treatment_names(self.sheet_names[0])
        sub_plots = len(treatment_list)
        fig, ax = plt.subplots(1,sub_plots)
        plot_counter = 0
        for treatment in treatment_list:
            graph_frame = build_dataframe_across_sheets(treatment)
            sns.catplot(x="Time Point",
                        y="Count",
                        hue="Treatment",
                        data = graph_frame,
                        ax=ax[plot_counter],
                        kind="point",
                        capsize=0.3)
            ax[plot_counter].legend(loc='upper left', frameon=False)
            plot_counter +=1
        fig.set_size_inches(12, 5)
        plt.show(block=False)



    def make_PR_seaborn(self,sex="Both"):
        column_keys = self.pr_columns
        df = self.excel.parse(sheet_name=self.sheet_names)
        output = pd.DataFrame(columns=["Treatment", "Time Point", "Count"])
        for column in column_keys:
            temp_frame = pd.DataFrame()
            temp_frame["Treatment"] = df["Treatment"]
            temp_frame["Time Point"] = column
            temp_frame["Count"] = df[column]
            output = pd.merge_ordered(output, temp_frame, fill_method='ffill')

        return output

    def make_df_prism_ready(dataframe):
        return dataframe

    def PR_pointplot(self, pooled=True, save=True):
        """
        Takes the PR columns and puts them in a graph.
        Requires make_PR_seaborn(sheet)
        """
        temp = self.make_PR_seaborn()
        temp = temp.dropna(axis="index", how="any")
        temp_na_timepoints = set(temp["Time Point"])
        output_columns = [value for value in self.pr_columns
                          if value in temp_na_timepoints]
        if pooled:
            plt.figure()
            ax = sns.pointplot(x="Time Point",
                               y="Count",
                               data=temp,
                               hue="Treatment",
                               ci="sd",
                               order=output_columns)
            handles, labels = ax.get_legend_handles_labels()
            ax.legend(handles[:6], labels[:6])
            plt.show(block=False)


        else:
            fig, axes = plt.subplots(1,2, sharex='col', sharey='row')

            males = (temp
            .loc[temp['Treatment']
            .isin(self.male_treatment_labels)])

            females = (temp
            .loc[temp['Treatment']
            .isin(self.female_treatment_labels)])

            ax1 = sns.pointplot(x="Time Point",
                                y="Count",
                                data=males,
                                hue="Treatment",
                                ci=68,
                                order=output_columns,
                                ax=axes[0],capsize=0.1)
            ax2 = sns.pointplot(x="Time Point",
                                y="Count",
                                data=females,
                                hue="Treatment",
                                ci=68,
                                order=output_columns,
                                ax=axes[1],capsize=0.1)
            handles, labels = ax2.get_legend_handles_labels()
            ax2.legend(handles[:6], labels[:6])
            plt.show(block=False)
        if save:
            plt.savefig(self.filename.split(".")[0]
                        +"_Self_Administration-pointplot_"
                        +datetime.datetime.today().strftime('%Y-%m-%d')
                        +".png")
            plt.close()
    def PR_boxplot(self, pooled=True, save=True):
        """
        Takes the PR columns and puts them in a graph.
        Requires make_PR_seaborn(sheet)
        """
        temp = self.make_PR_seaborn()
        temp = temp.dropna(axis="index", how="any")
        temp_na_timepoints = set(temp["Time Point"])
        output_columns = [value for value in self.pr_columns
                          if value in temp_na_timepoints]
        if pooled:
            plt.figure()
            #treatment_list = get_treatment_names("Intro")
            ax = sns.swarmplot(x="Time Point",
                               y="Count",
                               data=temp,
                               hue="Treatment",
                               order=output_columns,
                               size=5, dodge=True,
                               linewidth=0.5,
                               edgecolor="black")

            ax = sns.boxplot(x="Time Point",
                            y="Count",
                            data=temp,
                            hue="Treatment",
                            order=output_columns)

            handles, labels = ax.get_legend_handles_labels()
            ax.legend(handles[:6], labels[:6])
            plt.show(block=False)

        #This else block is for plotting male and female data separately.
        else:
            fig, axes = plt.subplots(1,2, sharex='col', sharey='row')

            males = (temp
                     .loc[temp['Treatment']
                     .isin(self.male_treatment_labels)])
            females = (temp
                       .loc[temp['Treatment']
                       .isin(self.female_treatment_labels)])
            #ax1 represents the graph plotting the male data.
            ax1 = sns.boxplot(x="Time Point",
                              y="Count",
                              data=males,
                              hue="Treatment",
                              order=output_columns,
                              ax=axes[0])
            ax1 = sns.swarmplot(x="Time Point",
                                y="Count",
                                data=males,
                                hue="Treatment",
                                order=output_columns,
                                ax=axes[0],
                                size=5,
                                dodge=True,
                                linewidth=0.5,
                                edgecolor="black")
            #ax2 represents the graph plotting the female data.
            ax2 = sns.boxplot(x="Time Point",
                              y="Count",
                              data=females,
                              hue="Treatment",
                              order=output_columns,
                              ax=axes[1])
            ax2 = sns.swarmplot(x="Time Point",
                                y="Count",
                                data=females,
                                hue="Treatment",
                                order=output_columns,
                                ax=axes[1],
                                size=5,
                                dodge=True,
                                linewidth=0.5,
                                edgecolor="black")
            handles2, labels2 = ax2.get_legend_handles_labels()
            ax2.legend(handles2[:3], labels2[:3])
            handles1, labels1 = ax1.get_legend_handles_labels()
            ax1.legend(handles1[:3], labels1[:3])
            plt.show(block=False)
        if save:
            plt.savefig(self.filename.split(".")[0]
                        +"_Self_Administration-boxplot_"
                        +datetime.datetime.today().strftime('%Y-%m-%d')
                        +".png")
            plt.close()

    def PR_stats(sheet):
        """
        This is currently in development and will eventually:
        Do the appropriate statistics on the progressive ratio experiment.
        """
        #TODO: Support T-test
        #TODO: Support ANOVA
        #TODO: Support Two Way Anova
        print (sheet)

    def ANOVA_TimePoints(self, combine_sexes=True):
        """
        Hardcoded to use count as the parameter and treatment as the grouping
        identifier. This is a limitation due to these values being in a string,
        can work around this later by building a string according to the format
        below.
        """
        mc_results_to_return = []
        summary_to_return = []
        if combine_sexes:
            for timepoint in self.pr_columns:
                print("Time point: " + timepoint)
                df_timepoint = self.df_dropna.loc[self.df_dropna['Time Point'] == timepoint]
                results = ols ('Count ~ C(Treatment)', data=df_timepoint).fit()
                print (results.summary())
                mc = MultiComparison(df_timepoint['Count'],
                                    df_timepoint['Treatment'])
                mc_results = mc.tukeyhsd()
                print (mc_results)
                summary_to_return.append(results)
                mc_results_to_return.append(mc_results)

        elif not combine_sexes:
            for timepoint in self.pr_columns:
                print("Time point: " + timepoint)
                df_timepoint = self.df_dropna.loc[(self.df_dropna['Time Point'] == timepoint) & (self.df_dropna['Treatment'].isin(self.male_treatment_labels))]
                results = ols ('Count ~ C(Treatment)', data=df_timepoint).fit()
                print (results.summary())
                mc = MultiComparison(df_timepoint['Count'],
                                    df_timepoint['Treatment'])
                mc_results = mc.tukeyhsd()
                print (mc_results)
                summary_to_return.append(results)
                mc_results_to_return.append(mc_results)

            for timepoint in self.pr_columns:
                print("Time point: " + timepoint)
                df_timepoint = self.df_dropna.loc[(self.df_dropna['Time Point'] == timepoint) & (self.df_dropna['Treatment'].isin(self.female_treatment_labels))]
                results = ols ('Count ~ C(Treatment)', data=df_timepoint).fit()
                print (results.summary())
                mc = MultiComparison(df_timepoint['Count'],
                                    df_timepoint['Treatment'])
                mc_results = mc.tukeyhsd()
                print (mc_results)
                summary_to_return.append(results)
                mc_results_to_return.append(mc_results)

            return summary_to_return, mc_results_to_return
        else:
            print ("Did not understand parameters for which stats to do here. Looking for True or False")
