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
        # take averages of interpress interval for each session
        interval = self.rat.stats("mean", "interval")
        # take average of tap 1 length for each session
        tap1 = self.rat.stats("mean", "tap_1_len")
        # Pull the session targets. 
        trials = self.rat.set_of('n_sess')
        target = [self.rat.get_sess_params(i,'target') for i in trials]

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

        # take averages of interpress interval for each session
        interval = self.rat.stats("mean", "interval")
        # take average of tap 1 length for each session
        tap2 = self.rat.stats("mean", "tap_2_len")
        # Pull the session targets. 
        trials = self.rat.set_of('n_sess')
        target = [self.rat.get_sess_params(i,'target') for i in trials]

        plt.style.use('default')
        plt.scatter(trials, tap2, label="2nd Tap Length")
        plt.scatter(trials, interval, label="IPI")
        plt.plot(target, '-r', label="Target IPI")
        # ax h line @ozzy ? 
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
        target = self.rat.all_sessions('target')
        trials = self.rat.set_of('n_sess')

        plt.style.use('default')
        plt.scatter(trials, success, label="Successes")
        plt.plot(trials, avgs, '-k', label="Moving Avg of {0} Sessions".format(window))
        plt.xlabel('Session Number')
        plt.ylabel('Percentage of trials within {0}% of target IPI'.format(error))
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
        target = self.rat.df['target']
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
                target = (self.rat[i])['target']
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
                target = (self.rat[i]).all_sessions('target')
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

    
    def IntervalByGroup(self, target, window): 
        """ Plot showing the avg data by numbers of rat averaged
               
        Parameters 
        ---- 
        group : DataAvg Object
            name of the rat group

        target : int
            value of the target ipi wanted

        window : int
            The number of sessions that should be used to calculate the moving average. 
            Default is a window of 5 

        
        Returns
        --- 
        unnamed : matplotlib plot
        
        """

        # have to find the targetframe that needs to be pulled 
        i=0 
        # while i is less than the number of targets,
        while i < len(self.rat.targetframe):
            if (self.rat.targetframe[i]).iloc[0,5] == target:
                break
            else: 
                i += 1
        
        data = self.rat.targetframe[i]
        intervals = self.rat.Avgd_Interval(data, avgwindow = window)


        cuts = self.rat.cuts[i]
        leng = len(cuts)
        avgint = dict()
        cutt = (intervals['interval'].to_numpy())[:cuts[0]]
        avgint.update({'0': cutt})
        for i in range(leng-1):
            cutt = (intervals['interval'].to_numpy())[cuts[i]:cuts[i+1]]
            avgint.update({f'{i+1}': cutt}) 

        taps = dict()
        taps.update({'0':range(cuts[0])}) 
        for i in range(leng-1):
            taps.update({f'{i+1}':range(cuts[i], cuts[i+1])}) 

        farben= ['xkcd:dark red','xkcd:burnt orange', 'xkcd:goldenrod', 'xkcd:forest green', 'xkcd:royal blue','xkcd:dark purple', 'xkcd:violet', 'xkcd:rose']
        #styles = ['solid', 'solid', 'solid', 'solid', (0, (1, 10)), (0, (1, 10)), (0, (1, 10)), (0, (1, 10))]

        plt.style.use('default')
        for i in range(leng):
            intervals = avgint[f'{i}']
            trials = taps[f'{i}']
            plt.plot(trials, intervals, color = farben[i], label=f'{leng-i} rat')
        plt.xlabel('Trial Number')
        plt.ylabel('Average IPI (3000 trial window)')
        plt.title(f'Avg IPI {self.name} rat group')
        plt.legend()
        plt.show()



    def CofVariation(self, target, window, boxcar): 
        """ Plot showing the avg data by numbers of rat averaged
               
        Parameters 
        ---- 
        group : DataAvg Object
            name of the rat group

        target : int
            value of the target ipi wanted

        window : int
            The number of sessions that should be used to calculate the moving average. 
            Default is a window of 5 

        
        Returns
        --- 
        unnamed : matplotlib plot
        
        """

        cv, i = self.rat.Variation(self.rat, target, avgwindow = window, boxcar = boxcar)

        ints, taps = self.rat.CutByRat(self.rat, i, cv)        

        farben= ['xkcd:dark red','xkcd:burnt orange', 'xkcd:goldenrod', 'xkcd:forest green', 'xkcd:royal blue','xkcd:dark purple', 'xkcd:violet', 'xkcd:rose']
        #styles = ['solid', 'solid', 'solid', 'solid', (0, (1, 10)), (0, (1, 10)), (0, (1, 10)), (0, (1, 10))]

        plt.style.use('default')
        for i in range(len(ints)):
            intervals = ints[f'{i}']
            trials = taps[f'{i}']
            plt.plot(trials, intervals, color = farben[i], label=f'{len(ints)-i} rat')
        plt.xlabel('Trial Number')
        plt.ylabel('Coefficient of Variation')
        plt.title(f'Coefficient of Variation {self.name} rat group')
        plt.ylim([0,1])
        plt.legend()
        plt.show()


class AllPlot():

    def __init__(self, ratlist, ratnames):
        """
        Params 
        --- 
        ratlist : list of dataframes
            List of the averaged dataframes that come from DataAvgs

        ratnames : list of names 
            List of names for the rat groups
         """

        self.ratlist = ratlist 
        self.names = ratnames 

    def CofVar(self, target, window, boxcar): 
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
       
        # all of the colors for the plotting. We'll have issues if there are more than 8 rat groups compared simultaneously. 
        farben= ['xkcd:dark red','xkcd:burnt orange', 'xkcd:goldenrod', 'xkcd:forest green', 'xkcd:royal blue','xkcd:dark purple', 'xkcd:violet', 'xkcd:rose']

        plt.style.use('default')
        for r in range(len(self.ratlist)): 
            # find the coefficient of variation for this rat and then plot it. 
            cv, i = self.ratlist[r].Variation(target, avgwindow = window, boxcar = boxcar)
            trials = range(cv.shape[0])
            # plot with a different color for each rat in the ratlist. 
            plt.plot(trials, cv, color = farben[r], label=f'{self.names[r]} group')
        plt.xlabel('Trial Number')
        plt.ylabel('Coefficient of Variation')
        plt.title(f'Coefficient of Variation for all Groups')
        plt.ylim([0,0.4])
        plt.legend()
        plt.show() 


    def SuccessRate(self, target, error, window): 
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
       
        # all of the colors for the plotting. We'll have issues if there are more than 8 rat groups compared simultaneously. 
        farben= ['xkcd:dark red','xkcd:burnt orange', 'xkcd:goldenrod', 'xkcd:forest green', 'xkcd:royal blue','xkcd:dark purple', 'xkcd:violet', 'xkcd:rose']
        # So plots show up on a dark background VSCode
        plt.style.use('default')

        # for each of the rats being plotted, 
        for r in range(len(self.ratlist)): 
            # find the coefficient of variation for this rat and then plot it. 
            success = self.ratlist[r].TrialSuccess(target, error, avgwindow = window)
            # crop the first 10 trials because some start at 100% and then plummet which makes the graph look wonky.
            success = success[10:]
            # define the x axis based on the length of the successes
            trials = range(10,success.shape[0]+10)
            # plot with a different color for each rat in the ratlist. 
            plt.plot(trials, success, color = farben[r], label=f'{self.names[r]} group')
        # just making the plot look nice
        plt.xlabel('Trial Number')
        plt.ylabel(f'Percent of trials within limit (moving {window} trial window) ')
        plt.title(f'Success Rate within +-{error}% of IPI for all Groups')
        plt.legend()
        plt.show() 