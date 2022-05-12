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

        self.farben = ['xkcd:slate grey', 'xkcd:deep green', 'xkcd:greyish green', 'xkcd:cool grey', 'xkcd:slate grey', 'xkcd:deep green', 'xkcd:greyish green', 'xkcd:cool grey']
        self.colors = ['xkcd:wine red', 'xkcd:grape', 'xkcd:dark lavender', 'xkcd:blueberry', 'xkcd:ocean blue', 'xkcd:turquoise', 'xkcd:light teal', 'xkcd:sage green', 'xkcd:yellow ochre', 'xkcd:pumpkin', 'xkcd:burnt umber']
    
    def _xlabel(self, value, tick_number=None):
        if abs(value) < 1000:
            num = 0 
        else:
            num = ma.floor(ma.log10(abs(value))/3)
        value = round(value / 1000**num, 2)
        return f'{value:g}'+' KM'[num]
   

    def Plot(self, ptype = 'IPI', target = 700, window = 1000, minwindow = 100, error = 10, boxcar = 300, savepath = None, ymin = 0, ymax = False, target2 = 500, norm = False):
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
            self.IPI(target, window, minwindow, mine = ymin, save = savepath, max = ymax)

        # Graph of Success vs. trials 
        elif ptype == ("Success" or "success"):
            self.Success(target, error, window, minwindow, save = savepath)

        elif ptype == ("CV" or "cv"):
            self.CV(target, window, minwindow, boxcar, mine = minwindow, save = savepath)

        elif ptype == ("DeltaIPI" or "deltaIPI" or "Delta IPI"):
            self.DelIPI(target, target2, window, minwindow, savepath, norm) 


    def DelIPI(self, target1, target2, win, minwindow, save, norm = False): 
        """ Plots the change in interval produced for the averaged data. """
        # check to see if the rats are in a list. If not, that means there is only one rat in the list. 
        if not isinstance(self.rat, list): 
            # make the item into a "list" so it can be iterated over the same code. 
            self.rat = [self.rat] 
        
        # make a list of numbers to iterate over for the colors. 
        cols = np.arange(len(self.rat)) 

        # define the plotting style
        plt.style.use('default') 

        # now that all posibilities of self.rat are lists, 
        for rat, name, c in zip(self.rat, self.names, cols): 
            delipi = rat.DeltaIPI(target1, target2, norm, window = win, minwin = minwindow)
            if delipi == False: 
                break 
            trials = range(len(delipi))

            plt.plot(trials, delipi, color = self.colors[c], label = f'{name}')

        plt.ylim((-50,target2-target1))
        frame = plt.legend(loc='upper left', bbox_to_anchor=(0, -0.15), fancybox=True, ncol=3).get_frame()
        frame.set_edgecolor("black")
        frame.set_boxstyle('square')
        plt.xlabel("Tap Number")
        plt.ylabel(r'$\Delta$IPI (ms)') 
        plt.title(r'$\Delta$IPI' + f' between {target1}ms and {target2}ms Trials') 

        if save != None: 
            plt.savefig(save, bbox_extra_artists=(frame,), bbox_inches = 'tight') 
        plt.show() 


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


    def IPI(self, target, window, minwindow, mine = 0, save = None, max = None):
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

        if max == False:
            plt.ylim((mine, target+100))
        if max != False:
            plt.ylim((mine, max)) 
        
        plt.xlabel('Trials', loc = "right")
        # code from stackoverflow for formatting the axis as #'s of k 
        ax.xaxis.set_major_formatter(plt.FuncFormatter(self._xlabel))
        
        frame = plt.legend(loc='upper left', bbox_to_anchor=(0, -0.15), fancybox=True, ncol=2).get_frame()
        frame.set_edgecolor("black")
        frame.set_boxstyle('square')
        
        plt.ylabel(f' Interval (miliseconds)')
        plt.title(f'IPI for {target}ms target IPI')
        if save != None:
            fig.savefig(save, bbox_extra_artists=(frame,), bbox_inches = 'tight') 
        plt.show() 


    def Success(self, target, error, window, minwindow, save = None): 
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
        for r, name in zip(range(len(self.rat)), self.names):
            # find the coefficient of variation for this rat and then plot it. 
            success = self.rat[r].MovingAverage(target, "Success", win = window, minwin = minwindow, err = error)
            
            # define the x axis based on the length of the successes
            trials = range(success.shape[0])
            # plot with a different color for each rat in the ratlist. 
            ax.plot(trials, success, label=f'{name} group', color = self.farben[r])

        # Aesthetic Changes ________________________________________________

        plt.ylim((0,100))
        
        plt.xlabel('Trials', loc = "right")
        # code from stackoverflow for formatting the axis as #'s of k 
        ax.xaxis.set_major_formatter(plt.FuncFormatter(self._xlabel))
        
        frame = plt.legend(loc='upper left', bbox_to_anchor=(0, -0.15), fancybox=True, ncol=2).get_frame()
        frame.set_edgecolor("black")
        frame.set_boxstyle('square')
        
        plt.ylabel(f'Percent of trials within limit (moving {window} trial window) ')
        plt.title(f'Success Rate within +-{error}% of {target}ms target IPI')
        if save != None:
            fig.savefig(save, bbox_extra_artists=(frame,), bbox_inches = 'tight') 
        plt.show() 


    def CV(self, target, window, minwindow, box, mine = 0, save = None): 
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

        ylimit = np.max(height) + 0.02
        plt.ylim((mine,ylimit))
        
        plt.xlabel('Trials', loc = "right")
        # code from stackoverflow for formatting the axis as #'s of k 
        ax.xaxis.set_major_formatter(plt.FuncFormatter(self._xlabel))
        
        frame = plt.legend(loc='upper left', bbox_to_anchor=(0, -0.15), fancybox=True, ncol=3).get_frame()
        frame.set_edgecolor("black")
        frame.set_boxstyle('square')

        plt.ylabel('Coefficient of Variation')
        plt.title(f'Coefficient of Variation for {target}ms target IPI')
        if save != None:
            fig.savefig(save, bbox_extra_artists=(frame,), bbox_inches = 'tight') 
        plt.show()





class Rat2000:

    def __init__(self, rats, labels):
        self.rats = rats 
        self.labels = labels

        self.farben = ['xkcd:slate grey', 'xkcd:deep green', 'xkcd:greyish green', 'xkcd:cool grey', 'xkcd:slate grey', 'xkcd:deep green', 'xkcd:greyish green', 'xkcd:cool grey']
        self.pattern = ['-', '-', '-', '-', ":", ":", ":", ":"]


    def Plot(self, ptype = "IPI", target = 700, error = 20, save = False):

        # Graph of IPI vs. trials 
        if ptype == ("IPI" or "interval" or "Interval"):
            self.IPI(target, self.labels, save)

        # Graph of Success vs. trials 
        elif ptype == ("Success" or "success"):
            self.Success(target, error, self.labels, save)

        elif ptype == ("CV" or "cv"):
            self.CV(target, self.labels, save)


    def IPI(self, target, labels, save):
        ipis = []
        tar = f'{target}'
        for rat in self.rats:
            ipis.append(rat.df.loc[tar].to_numpy()[0])
        
        plt.style.use('default') 
        
        for i in range(len(self.rats)): 
            plt.bar(i+1, height = self.rats[i].df.loc[tar].to_numpy()[0], label = labels[i], color = self.farben[i])
        
        for i in range(len(self.rats)):
            ys = (self.rats[i].IPIs)[0]
            xs = np.full(len(ys), i+1)
            plt.scatter(xs, ys, s=6, c='black')

        ys = (self.rats[2].IPIs)[1]
        xs = np.full(len(ys), 3)
        plt.scatter(xs, ys, s=6, c='black', label = "Individual Rats' Performance")
        
        plt.xticks(np.arange(len(self.rats))+1, labels)
        plt.ylim((0, target+100))
        frame = plt.legend(loc='upper left', bbox_to_anchor=(0, -0.15), fancybox=True, ncol=2).get_frame()
        frame.set_edgecolor("black")
        frame.set_boxstyle('square')
        plt.title(f'Mean IPI for last 2000 trials -- {target}ms Target IPI')
        plt.ylabel("Interpress Interval (miliseconds)")
        plt.xlabel("Rat Groups") 

        if save != False:
            plt.savefig(save, bbox_extra_artists=(frame,), bbox_inches = 'tight') 
            plt.show()
        else:
            plt.show()


    def Success(self, target, error, labels, save):
        tar = f'{target}'
        
        plt.style.use('default') 

        for i in range(len(self.rats)): 
            plt.bar(i+1, height = self.rats[i].df.loc[tar].to_numpy()[2], label = labels[i], color = self.farben[i])
        
        for i in range(len(self.rats)):
            ys = (self.rats[i].SRs)[0]
            xs = np.full(len(ys), i+1)
            plt.scatter(xs, ys, s=6, c='black')
        
        ys = (self.rats[2].SRs)[1]
        xs = np.full(len(ys), 3)
        plt.scatter(xs, ys, s=6, c='black', label = "Individual Rats' Performance")

        plt.xticks(np.arange(len(self.rats))+1, labels)
        plt.ylim((0,100))
        frame = plt.legend(loc='upper left', bbox_to_anchor=(0, -0.15), fancybox=True, ncol=2).get_frame()
        frame.set_edgecolor("black")
        frame.set_boxstyle('square')
        plt.title(f'Mean Success Rate for last 2000 trials -- {target}ms Target IPI')
        plt.ylabel(f'Percent of Rats within {error}% of target IPI')
        plt.xlabel("Rat Groups")

        if save != False:
            plt.savefig(save, bbox_extra_artists=(frame,), bbox_inches = 'tight') 
            plt.show()
        else:
            plt.show()


    def CV(self, target, labels, save):
        cvs = []
        tar = f'{target}'
        for rat in self.rats:
            cvs.append(rat.df.loc[tar].to_numpy()[1])
        
        plt.style.use('default') 
        
        for i in range(len(self.rats)): 
            plt.bar(i+1, height = self.rats[i].df.loc[tar].to_numpy()[1], label = labels[i], color = self.farben[i])
        
        
        for i in range(len(self.rats)):
            ys = (self.rats[i].CVs)[0]
            xs = np.full(len(ys), i+1)
            plt.scatter(xs, ys, s=6, c='black')

        ys = (self.rats[2].CVs)[1]
        xs = np.full(len(ys), 3)
        plt.scatter(xs, ys, s=6, c='black', label = "Individual Rats' last 2000 trial avg")
        
        plt.xticks(np.arange(len(self.rats))+1, labels)
        plt.ylim((0,0.35))
        frame = plt.legend(loc='upper left', bbox_to_anchor=(0, -0.15), fancybox=True, ncol=2).get_frame()
        frame.set_edgecolor("black")
        frame.set_boxstyle('square')
        plt.title(f'Mean CV for last 2000 trials -- {target}ms Target IPI')
        plt.ylabel("Coefficient of Variation")
        plt.xlabel("Rat Groups") 

        if save != False:
            plt.savefig(save, bbox_extra_artists=(frame,), bbox_inches = 'tight') 
            plt.show()
        else:
            plt.show()

