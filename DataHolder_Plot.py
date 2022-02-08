# 21 January 2022 
# Maegan Jennings, Ozzy Weinreb 

from re import L
import matplotlib.pyplot as plt 
import numpy as np 
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
        


    def Plot(self, ptype = 'IPI', window = 1000, minwindow = 100, error = 10):
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


        

    def Tap_vIPI(self, tap, window, minwindow):
        """ Plots the Tap X & interpress interval versus the number of trials"""
    
        # define the plotting style 
        plt.style.use('default')
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
            plt.plot(trials, taps, label= f'{name}, Tap {tap}')
            plt.plot(trials, interval, label=f'{name}, IPI')
        # eliminate any doubles from the list of targets 
        #targets = set(targetlist.tolist()) 
        #plt.hlines(targets, 0, len(interval), 'xkcd:light grey', label="target")

        # add things to the plot that only need to be added once. 
        plt.xlabel('Trial Number')
        plt.ylabel('Time (ms)')
        plt.title(f'Tap {tap} & Interval')
        plt.legend()
        plt.show()



    
    def IPI(self, window, minwindow):
        """ Plots the Interpress interval versus the number of trials"""
    
        # define the plotting style 
        plt.style.use('default')
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
            plt.plot(trials, interval, label=f'{name}')
        # eliminate any doubles from the list of targets 
        #targets = set(targetlist.tolist()) 
        #plt.hlines(targets, 0, len(interval), 'xkcd:light grey', label="target")

        # add things to the plot that only need to be added once. 
        plt.xlabel('Trial Number')
        plt.ylabel('Time (ms)')
        plt.title(f'Interpress Interval over Trials')
        plt.legend()
        plt.show()
    

    def Success(self, error, window, minwindow):
        """ Plots the Success within +- error % of the IPI versus the number of trials"""
        
        # define the plotting style 
        plt.style.use('default')

        for rat, name in zip(self.rat, self.rattitle):
            # find the moving average of the interpress intervals
            success = rat.MovingAverage('success', win = window, minwin = minwindow, err = error)
            # find the moving average of the tap length
            
            # make a list for the trials 
            trials = range(len(success)) 

            # plot 
            plt.plot(trials, success, label=f'{name} Success Rate')

        # add things to the plot that only need to be added once. 
        plt.xlabel('Trial Number')
        plt.ylabel('Time (ms)')
        plt.ylim([0,100])
        plt.title(f'Success Rate of +-{error}% within IPI')
        plt.legend()
        plt.show()
