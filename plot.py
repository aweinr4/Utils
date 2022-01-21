import matplotlib.pyplot as plt 
import numpy as np 
import pandas as pd 
import scipy as sc
import datetime
from scipy import stats
from .DataHolder import DataHolder

class Plotters:

    def __init__(self, ratt, ratname):
        """ Initializes the 'ratt' as the object returned from the 
        DataCrunch(presses, session) class. 'ratname' will be the name of the rat 
        displayed on the plots. """
        self.rattitle = ratname
        self.rat = ratt

    def Tap1_vInterval(self):
        """ Gives a plot of the average 1st tap length and average ipi for each session """
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
        """ Gives a plot of the average 2nd tap length and average ipi for each session """
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


    def SuccessRate(self, error = 20):
        """ Displays the number of trials in each session where the IPI was within +-X % 
        of the target IPI. Error is to be entered in whole numbers ex. 10% is 'error = 10' 
        Default is +-20% """
        success = self.rat.Success(error)
        target = self.rat.SessionTargets()
        trials = range(1,len(target)+1)

        plt.style.use('default)')
        plt.scatter(trials, success, label="Successes")
        plt.plot(target, '-r', label="Target IPI")
        plt.xlabel('Session Number')
        plt.ylabel('Number of trials within {0}% of target IPI'.format(error))
        plt.title('{0} Success Rate'.format(self.rattitle))
        plt.legend()
        plt.show()