# 21 January 2022 
# Maegan Jennings, Ozzy Weinreb 

import matplotlib.pyplot as plt 
import numpy as np 
import pandas as pd 
import scipy as sc
import datetime
from scipy import stats
from .DataHolder import DataHolder
from .simple import ceil

class PlotSingle:

    def __init__(self, ratdata, ratname):
        """ Class for graphs! 
        
        Parameters 
        ---- 
        ratdata : object 
            Name of the object returned from the DataHolder(presses, session) class
        ratname : string 
            Name of the rat to be displayed on the plots. 
        """
        self.rattitle = ratname
        self.rat = ratdata

    def Tap1_vInterval(self):
        """ Returns a plot of the average 1st tap length and average IPI for each session. 
        
        Parameters 
        ---- 
        None
        
        Returns 
        ---- 
        unnamed : matplotlib plot 
        """
        # add the average interpress interval to the sessions data and pull it 
        self.rat.stats("mean", "interval")
        interval = self.rat.sessions["interval_mean"]
        # add the average tap 1 length to the sessions data and pull it 
        self.rat.stats("mean", "tap_1_len")
        tap1 = self.rat.sessions["tap_1_len_mean"] 
        # Pull the session targets. 
        target = self.rat.SessionTargets()
        trials = range(1,len(tap1)+1)

        plt.style.use('default')
        plt.scatter(trials, tap1, label="1st Tap Length")
        plt.scatter(trials, interval, label="IPI")
        plt.plot(target, '-r', label="Target IPI")
        # ax h line @ozzy ? 
        plt.xlabel('Session Number')
        plt.ylabel('Time (ms)')
        plt.title('{0} Taps & Interval'.format(self.rattitle))
        plt.legend()
        plt.show()

    def Tap2_vInterval(self):
        """ Returns a plot of the average 2nd tap length and average ipi for each session    

        Parameters 
        ---- 
        None
        
        Returns 
        ---- 
        unnamed : matplotlib plot 
        """

        taps = self.rat.AvgTaps()
        target = self.rat.AllTargets()
        interval = (taps["interval"]).to_numpy()
        tap2 = (taps["tap_2_len"]).to_numpy()
        trials = range(1,len(tap2)+1)

        plt.style.use('default')
        plt.scatter(trials, tap2, label="2nd Tap Length")
        plt.scatter(trials, interval, label="IPI")
        plt.plot(target, '-r', label="Target IPI")
        plt.xlabel('Session Number')
        plt.ylabel('Time (ms)')
        plt.title('{0} Taps & Interval'.format(self.rattitle))
        plt.legend()
        plt.show()


    def S_SuccessRate(self, error = 20, window = 5):
        """ Returns a plot with number of trials in each session where the IPI was within +-X % 
        of the target IPI. 
        
        Parameters 
        ---- 
        error : int
            Whole number value of the percentage bounds. 
            ex. 10% is 'error = 10'. Default is +-20%
        avgwindow : int
            The number of sessions that should be used to calculate the moving average. 
            Default is a window of 5 
        
        Returns
        --- 
        unnamed : matplotlib plot
        """
        # get the success & averaged success from the data
        success, avgs = self.rat.SessionSuccess(error, avgwindow = window)
        # pull the targets for each session
        target = self.rat.SessionTargets()
        trials = range(1,len(target)+1)

        plt.style.use('default')
        plt.scatter(trials, success, label="Successes")
        plt.plot(trials, avgs, '-k', label="Moving Avg of {0} Sessions".format(window))
        plt.xlabel('Session Number')
        plt.ylabel('Number of trials within {0}% of target IPI'.format(error))
        plt.title('{0} Success Rate'.format(self.rattitle))
        plt.legend()
        plt.show()


    def T_SuccessRate(self, error = 20, window = 100):
        """ Returns a plot with number of trials where the IPI was within +-X % of the target IPI. 
        
        Parameters 
        ---- 
        error : int
            Whole number value of the percentage bounds. 
            ex. 10% is 'error = 10'. Default is +-20%
        avgwindow : int
            The number of sessions that should be used to calculate the moving average. 
            Default is a window of 5 
        
        Returns
        --- 
        unnamed : matplotlib plot
        """

        avgs = self.rat.TrialSuccess(error, avgwindow = window)
        target = self.rat.TrialTargets()
        trials = range(1,len(target)+1)

        plt.style.use('default')
        plt.plot(trials, avgs, '-k', label="Moving Avg of {0} Trials".format(window))
        plt.xlabel('Trial Number')
        plt.ylabel('Percent of trials within {0}% of target IPI'.format(error))
        plt.title('{0} Trial Success Rate'.format(self.rattitle))
        plt.ylim([0,100])
        plt.legend()
        plt.show()



class PlotMultiple:

    def __init__(self, rats, ratnames):
        """ Class for graphs! 
        
        Parameters 
        ---- 
        rats : list 
            List of the of the object returned from the DataHolder(presses, session) class
        ratnames : list
            List of the names of the rat to be displayed on the plots. 
        """

        self.rat = rats
        self.ratname = ratnames

    def T_SuccessRate(self, error = 20, window = 100, width = 7, height = 5):
        """ Returns a plot with number of trials where the IPI was within +-X % of the target IPI. 
        
        Parameters 
        ---- 
        error : int
            Whole number value of the percentage bounds. 
            ex. 10% is 'error = 10'. Default is +-20%
        avgwindow : int
            The number of sessions that should be used to calculate the moving average. 
            Default is a window of 5 
        width : int
            Preset width for one graph 
        height : int
            Preset height for one graph
        
        Returns
        --- 
        unnamed : matplotlib plot
        """
        # the number of graphs needed is the number of rats inputted. 
        num = len(self.rat)
        # use a grid determined by the integer above the square root of the 
        # number of rats -> 5 rats will be a 3x3 grid. 
        grid = ceil(np.sqrt(num)) 
        
        # for each of the rats, 
        with plt.style.context('default'):
        # define the structure of the figure 
            fig, axs = plt.subplots(grid, grid, figsize = (width*grid, height*grid) )
            for ax, i in zip(axs.flat, range(num)): 
                # find the data of the rat using the success function
                avgs = (self.rat[i]).TrialSuccess(error, avgwindow = window)
                target = (self.rat[i]).TrialTargets()
                # define the name of the rat for later
                ratname = self.ratname[i]
                trials = range(1,len(target)+1)

                ax.plot(trials, avgs, '-k', label="Moving Avg of {0} Trials".format(window))

                ax.set_xlabel('Trial Number')
                ax.set_ylabel('Percent of trials within {0}% of target IPI'.format(error))
                ax.set_title('{0} Trial Success Rate'.format(ratname))
                ax.set_ylim([0,100])
                ax.legend()

        # change the spacing between the plots for more room for the labels. 
        plt.subplots_adjust(wspace = 0.25, hspace = 0.25)
        # show the plot
        plt.show()

    def S_SuccessRate(self, error = 20, window = 5, width = 7, height = 5):
        """ Returns a plot with number of trials in each session where the IPI was within +-X % 
        of the target IPI. 
        
        Parameters 
        ---- 
        error : int
            Whole number value of the percentage bounds. 
            ex. 10% is 'error = 10'. Default is +-20%
        avgwindow : int
            The number of sessions that should be used to calculate the moving average. 
            Default is a window of 5 
        width : int
            Preset width for one graph 
        height : int
            Preset height for one graph
        
        Returns
        --- 
        unnamed : matplotlib plot
        """
        # the number of graphs needed is the number of rats inputted. 
        num = len(self.rat)
        # use a grid determined by the integer above the square root of the 
        # number of rats -> 5 rats will be a 3x3 grid. 
        grid = ceil(np.sqrt(num)) 
        

        # for each of the rats, 
        with plt.style.context('default'):
        # define the structure of the figure 
            fig, axs = plt.subplots(grid, grid, figsize = (width*grid, height*grid) )
            for ax, i in zip(axs.flat, range(num)): 
                # find the data of the rat using the success function
                success, avgs = (self.rat[i]).SessionSuccess(error, avgwindow = window)
                target = (self.rat[i]).SessionTargets()
                # define the name of the rat for later
                ratname = self.ratname[i]
                trials = range(1,len(target)+1)
                ax.scatter(trials, success, label="Successes")
                ax.plot(trials, avgs, '-k', label="Moving Avg of {0} Sessions".format(window))
                ax.set_xlabel('Session Number')
                ax.set_ylabel('Percent of trials within {0}% of target IPI'.format(error))
                ax.set_title('{0} Session Success Rate'.format(ratname))
                ax.set_ylim([0,100])
                ax.legend()

        # change the spacing between the plots for more room for the labels. 
        plt.subplots_adjust(wspace = 0.25, hspace = 0.25)
        # show the plot
        plt.show()



class PlotAvgs:

    def __init__(self, ratt, groupname):
        """ Class for graphs! 
        
        Parameters 
        ---- 
        ratt : object
            The object returned from the DataAvgs(presses, session) class
        groupname : str
            Name of the group of the rats
        """

        self.rat = ratt
        self.name = groupname 

    def T_SuccessRate(self, error = 20, window = 100, width = 7, height = 5):
        """ Returns a plot with number of trials where the IPI was within +-X % of the target IPI. 
        
        Parameters 
        ---- 
        error : int
            Whole number value of the percentage bounds. 
            ex. 10% is 'error = 10'. Default is +-20%
        avgwindow : int
            The number of sessions that should be used to calculate the moving average. 
            Default is a window of 5 
        width : int
            Preset width for one graph 
        height : int
            Preset height for one graph
        
        Returns
        --- 
        unnamed : matplotlib plot
        """
        # the number of graphs needed for the different targets.
        num = len(self.rat)
        
        # find the data of the rat using the success function
        target = (self.rat).TrialTargets()
        avgs = (self.rat).TrialSuccess(error, avgwindow = window)

        # for each of the rats, 
        with plt.style.context('default'):
        # define the structure of the figure 
            fig, axs = plt.subplots(1, num, figsize = (width*num, height) )
            for ax, i in zip(axs.flat, range(num)):
                # split the data by the cutoffs for different colors by #rat averaged

                # grab the cuts for that target and sort from small to large
                cuts = (self.cuts[i]).sort()
                
                # 
                # 
                # 
                # 
                # 
                #  
                ipi = target[i][0]
                trials = range(1,len(target[i])+1)
                ax.plot(trials, avgs[i], '-k', label=f"Moving Avg of {window} Trials")
                ax.set_xlabel('Trial Number')
                ax.set_ylabel(f'Percent of trials within {error}% of target IPI')
                ax.set_title(f'{self.name} Trial Success Rate at {ipi} IPI')
                ax.set_ylim([0,100])
                ax.legend()

        # change the spacing between the plots for more room for the labels. 
        plt.subplots_adjust(wspace = 0.25, hspace = 0.25)
        # show the plot
        plt.show()

