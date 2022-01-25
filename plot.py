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
        taps = self.rat.AvgTaps()
        target = self.rat.SessionTargets()
        interval = (taps["interval"]).to_numpy()
        tap1 = (taps["tap_1_len"]).to_numpy()
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
        target = self.rat.SessionTargets()
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


    def SuccessRate(self, error = 20, window = 5):
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
        data = self.rat.Success(error, avgwindow = window)
        # pull out the successes and convert to numpy
        success = (data['NumSuccess']).to_numpy()
        # pull out the moving average and convert to numpy 
        avgs = (data['MovingAvg']).to_numpy()
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


    def SuccessRate(self, error = 20, window = 5, width = 5, height = 3):
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
        # define the structure of the figure 
        fig, axs = plt.subplots(grid, grid, figsize = (width*grid, height*grid) )

        # for each of the rats, 
        for ax, i in zip(axs.flat, range(num)): 
            # find the data of the rat using the success function
            success, avgs = (self.rat[i]).Success(error, avgwindow = window)
            target = (self.rat[i]).SessionTargets()
            # define the name of the rat for later
            ratname = self.ratname[i]
            trials = range(1,len(target)+1)
            ax.scatter(trials, success, label="Successes")
            ax.plot(trials, avgs, '-k', label="Moving Avg of {0} Sessions".format(window))
            ax.set_xlabel('Session Number')
            ax.set_ylabel('Number of trials within {0}% of target IPI'.format(error))
            ax.set_title('{0} Success Rate'.format(ratname))
            ax.legend()

        plt.show()