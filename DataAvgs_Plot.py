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
import math as ma 



class AveragedRats:

    # all of the colors for the plotting. We'll have issues if there are more than 8 rat groups compared simultaneously. 
    farben= ['xkcd:dark red','xkcd:burnt orange', 'xkcd:goldenrod', 'xkcd:forest green', 'xkcd:royal blue','xkcd:dark purple', 'xkcd:violet', 'xkcd:rose']

    def __init__(self, ratdata, ratname):
        """ Class for plotting the rat data. This works on a single rat group's data, or a few rat groups' data. 
        Interacts with the DataAvgs objects. 
        
        Parameters 
        ---- 
        ratdata : object or list
            Name(s) of the object returned from the DataAvgs class
        ratname : string or list
            Name(s) of the rat to be displayed on the plots. 
        """
                   
        self.names = ratname
        self.rat = ratdata


    
    def _xlabel(self, value, tick_number=None):
        if abs(value) < 1000:
            num = 0 
        else:
            num = ma.floor(ma.log10(abs(value))/3)
        value = round(value / 1000**num, 2)
        return f'{value:g}'+' KM'[num]


    def _pretty(self, ax, targets = False, ylim = False):
        # Aesthetic Changes ________________________________________________

        if ylim != False:
            plt.ylim((0, ylim)) 
        else: 
            ylim = np.max(targets)+100
            plt.ylim((0,ylim))
        
        plt.xlabel('Trials', loc = "right")
        # code from stackoverflow for formatting the axis as #'s of k 
        ax.xaxis.set_major_formatter(plt.FuncFormatter(self._xlabel))
        
        frame = plt.legend(loc='upper left', bbox_to_anchor=(0, -0.15), fancybox=True, ncol=3).get_frame()
        frame.set_edgecolor("black")
        frame.set_boxstyle('square')


    def Plot(self, ptype = 'IPI', target = 700, window = 1000, minwindow = 100, error = 10, boxcar = 300):
        """ Returns a plot of the average 1st tap length and average IPI for each session. 
        
        Parameters 
        ---- 
        ptype : str
            REQUIRED
            Name of the plot that you want to make. 
            allowed strings: "IPI", "Success", "Tap1", "Tap2" 

        target : int 
            REQUIRED
            Number value of the target IPI desired 
            Default is 700 
        
        window : int 
            REQUIRED
            Number for the window for moving average calculatons 
            Default is 1000 

        minwindow : int 
            REQUIRED
            Number for the minimum window for moving average calculatons 
            Default is 100
        
        error : int
            Only required for Success plots
            Number for the error margins for the Success plots. 
            Default is 10% 

        boxcar : int
            Only required for the coefficient of variation plots
            Number for the window length for the moving average "smoothing" function
            Default is 300
        
        Returns 
        ---- 
        unnamed : matplotlib plot 
        """
        
        
        # Graph of Tap1 & IPI vs. trials 
        if ptype == ("Tap1" or "tap1"):
            self.Tap_vIPI(1, target, window, minwindow)

        # Graph of Tap2 & IPI vs. trials 
        elif ptype == ("Tap2" or "tap2"):
            self.Tap_vIPI(2, target, window, minwindow) 

        # Graph of IPI vs. trials 
        elif ptype == ("IPI" or "interval" or "Interval"):
            self.IPI(target, window, minwindow)

        # Graph of Success vs. trials 
        elif ptype == ("Success" or "success"):
            self.Success(target, error, window, minwindow)

        elif ptype == ("CV" or "cv"):
            self.CV(target, window, minwindow, boxcar)



    def Tap_vIPI(self, tap, target, window, minwindow):
        """ Here """
        # check to see if the rats are in a list. If not, that means there is only one rat in the list. 
        if not isinstance(self.rat, list): 
            # make the item into a "list" so it can be iterated over the same code. 
            self.rat = [self.rat] 

        # define the plotting style 
        plt.style.use('default')
        fig, ax = plt.subplots()
        # blank array for the length of the trials
        length = []
        
        # now that all posibilities of self.rat are lists
        for rat, name in zip(self.rat, self.names):
        
            # define the interval 
            interval = rat.MovingAverage(target, 'interval', win = window, minwin = minwindow)
            # find the moving average of the tap length
            if tap == 1:
                taps = rat.MovingAverage(target, 'tap_1_len', win = window, minwin = minwindow)
            else:
                taps = rat.MovingAverage(target, 'tap_2_len', win = window, minwin = minwindow) 
            
            # make a list for the trials 
            trials = range(len(interval))
            length.append(trials[-1])

            # plot 
            ax.plot(trials, taps, label= f'{name}, Tap {tap}')
            ax.plot(trials, interval, label=f'{name}, IPI')
        
        # plot a line at where the target should be. 
        ax.hlines(target, 0, np.max(length), colors = ['xkcd:grey'], linestyles = ":", label="Target")

        self._pretty(ax, ylim = target +100)

        plt.ylabel(' Time (ms)')
        plt.title(f'Tap {tap} & Interval')
        plt.show()


    def IPI(self, target, window, minwindow):
        """ Returns a plot of the coefficient of variation for all of the rats that you give it 

        Params 
        --- 
        ratlist : list of dataframes
        List of the averaged dataframes that come from DataAvgs

        target : int
        Number of the target you're looking at

        window : int
        The number of sessions that should be used to calculate the moving coefficient of variation. 
        Default is a window of 100

        boxcar : int 
        The number of sessions that is used to smooth the Coefficient of variation data. 
        Default is a window of 300
        """

        # check to see if the rats are in a list. If not, that means there is only one rat in the list. 
        if not isinstance(self.rat, list): 
            # make the item into a "list" so it can be iterated over the same code. 
            self.rat = [self.rat] 

        # So plots show up on a dark background VSCode
        plt.style.use('default')
        fig, ax = plt.subplots()
        length = []

        # for each of the rats being plotted, 
        for r in range(len(self.rat)): 
            # find the coefficient of variation for this rat and then plot it. 
            interval = self.rat[r].MovingAverage(target, "interval", win = window, minwin = minwindow)
            
            # define the x axis based on the length of the successes
            trials = range(interval.shape[0])
            length.append(trials[-1])
            # plot with a different color for each rat in the ratlist. 
            ax.plot(trials, interval, color = self.farben[r], label=f'{self.names[r]} group')
        
        ax.hlines(target, 0, np.max(length), 'xkcd:grey', ":", label = "Target") 

        self._pretty(ax, ylim = target + 100)
        
        plt.ylabel(f' Interval (miliseconds')
        plt.title(f'IPI for {target}ms target IPI')
        plt.show() 


    def Success(self, target, error, window, minwindow): 
        """ Returns a plot of the coefficient of variation for all of the rats that you give it 
        
        Params 
        --- 
        ratlist : list of dataframes
            List of the averaged dataframes that come from DataAvgs
        
        target : int
            Number of the target you're looking at
        
        window : int
            The number of sessions that should be used to calculate the moving coefficient of variation. 
            Default is a window of 100
        
        boxcar : int 
            The number of sessions that is used to smooth the Coefficient of variation data. 
            Default is a window of 300
        
        Returns 
        --- 
        plot
        """

        # check to see if the rats are in a list. If not, that means there is only one rat in the list. 
        if not isinstance(self.rat, list): 
            # make the item into a "list" so it can be iterated over the same code. 
            self.rat = [self.rat] 
       
        # So plots show up on a dark background VSCode
        plt.style.use('default')
        fig, ax = plt.subplots()

        # for each of the rats being plotted, 
        for rat, name in zip(self.rat, self.names):
            # find the coefficient of variation for this rat and then plot it. 
            success = rat.MovingAverage(target, "Success", win = window, minwin = minwindow, err = error)
            
            # define the x axis based on the length of the successes
            trials = range(success.shape[0])
            # plot with a different color for each rat in the ratlist. 
            ax.plot(trials, success, label=f'{name} group')

        self._pretty(ax, ylim = 100)
        
        plt.ylabel(f'Percent of trials within limit (moving {window} trial window) ')
        plt.title(f'Success Rate within +-{error}% of {target}ms target IPI')
        plt.show() 


    def CV(self, target, window, minwindow, box): 
        """ Returns a plot of the coefficient of variation for all of the rats that you give it 
        
        Params 
        --- 
        ratlist : list of dataframes
            List of the averaged dataframes that come from DataAvgs
        
        target : int
            Number of the target you're looking at
        
        window : int
            The number of sessions that should be used to calculate the moving coefficient of variation. 
            Default is a window of 100

        minwindow : int
            OPTIONAL
            The number of sessions used to calculate a single average. Ex. minwindow = 20 will 
            Wait until the 20th row before calculating an average and place NaN in the first 19 rows.
            Default is a window of 10
        
        boxcar : int 
            The number of sessions that is used to smooth the Coefficient of variation data. 
            Default is a window of 300
        
        Returns 
        --- 
        plot
        """

       # check to see if the rats are in a list. If not, that means there is only one rat in the list. 
        if not isinstance(self.rat, list): 
            # make the item into a "list" so it can be iterated over the same code. 
            self.rat = [self.rat] 
        
        plt.style.use('default')
        fig, ax = plt.subplots()

        # make an array for the max height
        height = []
        

        for r in range(len(self.rat)): 
            # find the coefficient of variation for this rat and then plot it. 
            cv = self.rat[r].MovingAverage(target, "CV", win = window, minwin = minwindow, boxcar = box)
            trials = range(cv.shape[0])

            max = np.nanmax(cv)
            height.append(max)

            # plot with a different color for each rat in the ratlist. 
            ax.plot(trials, cv, color = self.farben[r], label=f'{self.names[r]} group')

        ylimit = np.max(height) + 0.1
        self._pretty(ax, ylim = ylimit) 

        plt.ylabel('Coefficient of Variation')
        plt.title(f'Coefficient of Variation for {target}ms target IPI')
        plt.show()


