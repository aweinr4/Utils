# 21 January 2022 
# Maegan Jennings, Ozzy Weinreb 

import matplotlib.pyplot as plt
import matplotlib 
import numpy as np 
import math as ma
import pandas as pd 
import scipy as sc
import datetime
from scipy import stats
from .DataHolder import DataHolder
from .simple import ceil


class RawRats:
    # FOR THE DATA HOLDER CLASS

    def __init__(self, ratdata, ratname):
        """ Class for plotting the rat data. This works on a single rat's data, or a few rat's data. 
        The rats' data are plotted without averaging. 
        Interacts with the DataHolder objects
        
        Parameters 
        ---- 
        ratdata : object 
            Name of the object returned from the DataHolder(presses, session) class
        ratname : string 
            Name of the rat to be displayed on the plots. 
        """

        # check to see if the rat names are in a list. If not, that means there is only one rat name in the list. 
        if not isinstance(ratname, list): 
            # make the item into a "list" so it can be iterated over the same code. 
            self.rattitle = [ratname]       
        else: 
            self.rattitle = ratname 

        # check to see if the rat data is in a list. If not, that means there is only one rat data in the list 
        if not isinstance(ratdata, list):
            # make the item into a "list" so it can be iterated over the same code 
            self.rat = [ratdata] 
        else:
            # if the item is already a list, then make it a self. object
            self.rat = ratdata  


    def _xlabel(self, value, tick_number=None):
        if abs(value) < 1000:
            num = 0 
        else:
            num = ma.floor(ma.log10(abs(value))/3)
        value = round(value / 1000**num, 2)
        return f'{value:g}'+' KM'[num]


    def _pretty(self, ax, targets, ylim = False):
        # Aesthetic Changes ________________________________________________

        if ylim != False:
            plt.ylim((0, ylim)) 
        else: 
            ylim = np.max(targets)+100
            plt.ylim((0,ylim))
        
        plt.xlabel('Trials', labelpad = -10, loc = "right")
        # code from stackoverflow for formatting the axis as #'s of k 
        ax.xaxis.set_major_formatter(plt.FuncFormatter(self._xlabel))
        
        frame = plt.legend(loc='upper left', bbox_to_anchor=(0, -0.1), fancybox=True, ncol=3).get_frame()
        frame.set_edgecolor("black")
        frame.set_boxstyle('square')


    def Plot(self, ptype = 'IPI', window = 1000, minwindow = 100, error = 10, boxcar = 300):
        """ Returns a plot of the average 1st tap length and average IPI for each session. 
        
        Parameters 
        ---- 
        ptype : str
            REQUIRED
            Name of the plot that you want to make. 
            allowed strings: "IPI", "Success", "Tap1", "Tap2" 
        
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
        
        Returns 
        ---- 
        unnamed : matplotlib plot 
        """
        
        
        # Graph of Tap1 & IPI vs. trials 
        if ptype == ("Tap1" or "tap1"):
            self.Tap_vIPI(1, window, minwindow)

        # Graph of Tap2 & IPI vs. trials 
        elif ptype == ("Tap2" or "tap2"):
            self.Tap_vIPI(2, window, minwindow) 

        # Graph of IPI vs. trials 
        elif ptype == "IPI":
            self.IPI(window, minwindow)

        # Graph of Success vs. trials 
        elif ptype == "Success":
            self.Success(error, window, minwindow)
        
        elif ptype == ("CV" or "cv"):
            self.CV(window, minwindow, boxcar)


    def Tap_vIPI(self, tap, window, minwindow):
        """ Plots the Tap X & interpress interval versus the number of trials"""
    
        # define the plotting style 
        plt.style.use('default')
        fig, ax = plt.subplots()
        # make an array for the targets used 
        targetlist = [] 

        for rat, name in zip(self.rat, self.rattitle):
            # find the moving average of the interpress intervals
            interval = rat.MovingAverage('interval', win = window, minwin = minwindow)
            # find the moving average of the tap length
            if tap == 1:
                taps = rat.MovingAverage('tap_1_len', win = window, minwin = minwindow)
            else:
                taps = rat.MovingAverage('tap_2_len', win = window, minwin = minwindow) 

            # make a list for the trials 
            trials = range(len(interval)) 

            # Pull the session targets. 
            targets = rat.set_of('target')
            targetlist.append(targets) 

            # plot 
            ax.plot(trials, taps, label= f'{name}, Tap {tap}')
            ax.plot(trials, interval, label=f'{name}, IPI')
        # pull the targets
        targets = [item for sublist in targetlist for item in sublist]
        ax.hlines(targets, 0, len(interval), 'xkcd:grey', label="target")

        self._pretty(ax, targets)

        plt.ylabel('Interpress Interval (ms)', labelpad = 10)
        plt.title(f'Tap {tap} & Interval', y=1.02)
        plt.show()


    def IPI(self, window, minwindow):
        """ Plots the Interpress interval versus the number of trials"""
    
        # define the plotting style 
        plt.style.use('default')
        fig, ax = plt.subplots()
        # make an array for the targets used 
        targetlist = [] 

        for rat, name in zip(self.rat, self.rattitle):
            # find the moving average of the interpress intervals
            interval = rat.MovingAverage('interval', win = window, minwin = minwindow)
            # find the moving average of the tap length
            
            # make a list for the trials 
            trials = range(len(interval)) 

            # Pull the session targets. 
            targets = rat.set_of('target')
            targetlist.append(targets) 

            # plot 
            ax.plot(trials, interval, label=f'{name}')

        # eliminate any doubles from the list of targets 
        targets = [item for sublist in targetlist for item in sublist]
        ax.hlines(targets, 0, len(interval), 'xkcd:grey', label="target")

        self._pretty(ax, targets) 

        plt.ylabel('Interpress Interval (miliseconds)', labelpad = 10)
        plt.title(f'Interpress Interval over Trials', y=1.02)
        
        plt.show()
    

    def Success(self, error, window, minwindow):
        """ Plots the Success within +- error % of the IPI versus the number of trials"""
        
        # define the plotting style 
        plt.style.use('default')
        fig, ax = plt.subplots()

        for rat, name in zip(self.rat, self.rattitle):
            # find the moving average of the interpress intervals
            success = rat.MovingAverage('success', win = window, minwin = minwindow, err = error)
            # find the moving average of the tap length
            
            # make a list for the trials 
            trials = range(len(success)) 

            # plot 
            ax.plot(trials, success, label=f'{name}')

        self._pretty(ax, [0])
        
        plt.ylabel('Percent of trials within error bounds')
        plt.title(f'Success Rate of +-{error}% within IPI')
        plt.show()


    def CV(self, window, minwindow, boxcar): 
        """ Returns a plot of the coefficient of variation for all of the rats that you give it 
        
        Params 
        --- 
        ratlist : list of dataframes
            List of the averaged dataframes that come from DataAvgs
        
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
        
        plt.style.use('default')
        fig, ax = plt.subplots()
        # make an array for the max height
        height = []

        for rat, name in zip(self.rat, self.rattitle):
            # find the coefficient of variation for this rat and then plot it. 
            cv = rat.MovingAverage("CV", win = window, minwin = minwindow, box = boxcar)
            trials = range(cv.shape[0])
            max = np.nanmax(cv)
            height.append(max)
            # plot with a different color for each rat in the ratlist. 
            ax.plot(trials, cv, label=f'{name} CV')
        ylimit = np.max(height) + 0.1

        self._pretty(ax, [0], ylim = ylimit)

        plt.ylabel('Coefficient of Variation')
        plt.title(f'Coefficient of Variation for target IPI')
        plt.show()