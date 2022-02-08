
from .simple import *
import pandas as pd


class DataAvgs:
    """ Class for inputting multiple rat press data files """


    def __init__(self, ratlist):
        """Initialization stores two dataframes in the class, one with information about specific presses 
        and one with the general information of each session. 

        Parameters
        --- 
        ratlist : list
            List of DataHolder objects. 
        Returns
        --- 
        None. Creates an object. 
        """

        datalist = [] 
        # pull the dataframes from the DataHolder object list
        for rat in ratlist:
            frame = rat.df 
            datalist.append(frame)

        # assume that all of the rats have the same list of targets 
        # just pull the first rat's targets
        targets = (ratlist[0].set_of('target')).tolist()
        # sort the targets from largest to smallest so 
        # they are always pulled in the same order. 
        (targets).sort(reverse=True) 
        self.targets = targets

        # do the preprocessing 
        targetlist = self._preprocessing(datalist)

        # get the list of cutoff values
        cutofflist = self._find_cutoff_values(targetlist)
        # make it into a self-referencing variable
        self.cuts = cutofflist

        # average the rats into a single dataframe per target
        targetframe = self._averaging(targetlist) 
        # make it into a self-referencing variable
        self.targetframe = targetframe 


    def _frames_by_target(self, datalist):
        """ Internal Function. Groups the dataframes by each of the targets contained. 
        Parameters 
        --- 
        datalist : list
            nested list of dataframes
        targets : list
            list of the targets used in the training 
        
        Returns 
        --- 
        targetlist : list 
            nested list of dataframes sorted by target 
        """
        # make empty lists for the things being seperated by targets
        targetframes = []
        dataframes = []
        # for each target, 
        for target in self.targets:
            # for each of the rats, 
            for frame in datalist:
                # grab the entries that have a specific target
                data = frame.loc[frame["target"]==target]
                data = data.reset_index()
                # append that data to the dataframe 
                dataframes.append(data)
            # append the dataframe for the whole target group to the targetframe 
            targetframes.append(dataframes)
            # reset the dataframe for the next target group 
            dataframes = []
        return targetframes 
        # TARGET COLUMN MIGHT BE LOST HERE. 


    def __getitem__(self,key):
        """ Python Internal. 
        Indexing method of the class"""

        # Check that the key is an interger 
        if isinstance(key,int):
            # if yes, return that number press
            return self.presses.iloc[key]

        # Check that the key has two items
        elif isinstance(key,tuple):
            # key must be formatted as [number, column title]
            n,col = key
            # pull the nth press out 
            row = self.presses.iloc[n]

            # if the column title exists in the press data, 
            if col in self.presses:
                # return that column
                return row[col]

            # if the column title exists in the session data, ex  "target" or "upper" 
            elif col in self.sessions:
                # run get sess params function to return the column from session data 
                return self.get_sess_params(int(row.name[0]))[col]
        
        # Check that the key is only a string,
        elif isinstance(key,str):

            # if the column title exists in the press data, 
            if key in self.presses.columns:
                # return all rows from that column 
                return self.presses[key]

            # if the column title exists in the session data, 
            elif key in self.sessions:
                # return all rows from that column 
                return self.sessions[key]
            
            # if the column title is "n_sess" or "n_in_sess".
            elif key in self.presses.index.names:
                # return all rows from that column 
                return self.presses.index.get_level_values(key)
            
            else: # if the column title is none of the above, 
                raise Exception(f"{key} is not valid")

        else: # if the format of the key is none of the above
            raise Exception(f"{type(key)} is an invalid type")
    

    def _preprocessing(self, datalist):
        """ Internal Function. Crop the dataframes to include only specific columns & sort by 
        target value.
        Parameters 
        --- 
        datalist : list
            nested list of dataframes
        targets : list
            list of the targets used in the training 
        
        Returns 
        --- 
        targetlist : list 
            nested list of dataframes sorted by target 
        """

        # assume that all of the dataframes have the same targets witin each rat group
        # Seperate the data by target group 
        targetframes = self._frames_by_target(datalist)
        # create blank targetlist for storing the new dataframes and blank dataframes for iterating over 
        targetlist = []
        dataframes = []
        # for each of the target groups, 
        for target in targetframes:
            # for each of the dataframes within the target group, 
            for frame in target:
                # grab only the columns that we want to average over
                press = frame.copy()[["interval", "tap_1_len", "tap_2_len", "ratio", "loss"]]
                # append them onto the dataframe
                dataframes.append(press)
            # append each full dataframe to the target group dataframe
            targetlist.append(dataframes)
            # reset the dataframes list for the next target group
            dataframes = []
        return targetlist  


    def _find_cutoff_values(self, targetlist):
        """ Internal Function. Finds the 'cutoff' values -- where the avg will go from having N rats to N-1 rats. 

        Parameters 
        --- 
        targetlist : list
            nested list of dataframes seperated by target. 
        
        Returns 
        --- 
        cutofflist : list 
            nested list of lists of cutoff values for each target group 
        """
        # create blank arrays for the cutoff value list and a blank array for use in the for loops
        cutoff = [] 
        cutofflist = []
        # for each of the target groups, 
        for target in targetlist:
            # for each of the rats within the target groups, 
            for frame in target:
                # append the length of the dataframe to the cutoff list 
                cutoff.append(frame.shape[0])
            # append the list of cutoffs for each dataframe within the target group 
            cutoff.sort()
            cutofflist.append(cutoff)
            # reset the blank array for the next target group 
            cutoff = [] 
        # return the full cutoff list of all target groups. 
        return cutofflist  


    def _averaging(self, targetlist):
        """ Internal Function. Output will be a list of averaged dataframes, length of which will be the number of target ipi's used in training. 
        Parameters 
        --- 
        targetlist : list
            nested list of dataframes seperated by target. 
        
        Returns 
        --- 
        targetframe : list 
            nested list of averaged dataframes for each target group
        """ 
        
        # initiate the iteration variable at 0 
        i = 0
        # make a blank targetframe for the averaged dataframes. 
        targetframe = [] 
        # while there are still targetlists to go over, 
        while i < len(targetlist): 
            target = self.targets[i]
            # grab the datframes by the target group
            data = targetlist[i]         
            # concatenate the data
            newpress = pd.concat(data)
            # use builtin .groupby() to stack the frames and then average. 
            avg = newpress.groupby(level=0).mean()
            # reset the indicies to be from 0 to N
            avg.reset_index()
            # automatically gets rid of the target column if we had it, so add that on for future reference 
            avg['target'] = np.full(avg.shape[0], target)
            # append the data entry to the single averaged dataframe. 
            targetframe.append(avg) 
            # step up i
            i += 1 
        # return the list of averaged dataframes. 
        return targetframe


    def Find_TargetFrame(self, target):
        # have to find the targetframe that needs to be pulled 
        i=0 
        # while i is less than the number of targets,
        while i < len(self.targetframe):
            if (self.targetframe[i]).iloc[0,5] == target:
                break
            else: 
                i += 1
        
        return self.targetframe[i]


    def Find_i(self, target):
        # have to find the targetframe that needs to be pulled 
        i=0 
        # while i is less than the number of targets,
        while i < len(self.targetframe):
            if (self.targetframe[i]).iloc[0,5] == target:
                break
            else: 
                i += 1
        
        return i
        

    """ --------------------------------------------------------------------------------------------------"""

    
    def ShowOverview(self):
        """ Returns overview of the data. 
        
        Params 
        --- 
        None
        
        Returns
        info : print 
            Info about how many presses, targets, and rats included. 
        """
        numrat = "error" # len(self.cuts[0])
        targets = []
        for frame in self.targetframe:
            length = frame.shape[0]
            target = frame.loc[0,"target"]
            targets.append(target)
        text = f"Number of Rats: {numrat} ... Number of Trials: {length} ... Targets: {targets} "
        return text 
        

    def CutoffValues(self):
        return self.cuts 


    def TrialSuccess(self, target, error, avgwindow = 1000):
        """ Returns an array with the number of successes in each session where the trial IPI was 
        +- error % away from the target IPI. 
        
        Parameters 
        -------
        dataframe : dataframe 
            averaged dataframe for a specific target. 
        error : int
            The numerical value of the percentage bounds from target desired. 
        avgwindow : int
            The number of sessions that should be used to calculate the moving average. 
            Default is a window of 5 
        
        Returns 
        ------
        successes : np.array
            Contains the number of succcesses for each session
        avg : np.array
            Contains the moving average of the successes per session

        """
        
        data = self.Find_TargetFrame(target)

        # grab the percentage error for each trial 
        loss = (data['loss']).to_numpy()
        # define upper and lower bounds
        upper = error/100
        lower = -error/100 

        #convert a bool array of whether or not losses are in between bounds to integer array 
        success = ((loss <= upper) & (lower <= loss)).astype(int)

        # make the data into a dataframe
        df = pd.DataFrame(success, columns = ['Success'])
        # use the pandas built-in 'rolling' to calculate the moving average. 
        # and assign it to 'avgs'
        avgs = (df.rolling(avgwindow, min_periods=10).mean())*100
        # return the averages
        return avgs


    def Avgd_Interval(self, target, avgwindow = 1000, minwin = 1):
        """ Returns an array with the number of successes in each session where the trial IPI was 
        +- error % away from the target IPI. 
        
        Parameters 
        -------
        dataframe : dataframe 
            averaged dataframe for a specific target. 
        error : int
            The numerical value of the percentage bounds from target desired. 
        avgwindow : int
            The number of sessions that should be used to calculate the moving average. 
            Default is a window of 5 
        
        Returns 
        ------
        successes : np.array
            Contains the number of succcesses for each session
        avg : np.array
            Contains the moving average of the successes per session

        """
 
        data = self.Find_TargetFrame(target)

        # grab the percentage error for each trial 
        intervals = data[['interval']]

        # use the pandas built-in 'rolling' to calculate the moving average. 
        # and assign it to 'avgs'
        avgs = (intervals.rolling(avgwindow, min_periods=minwin).mean())
        # convert to a numpy array
        # return the averages
        return avgs

    def MovingAverage(self, column, win = 1000, minwin = 1):
        if column in self.columns


    def Variation(self, target, avgwindow = 100, boxcar = 300): 
        """ Returns an array with the coefficient of variation in each group by target IPI 
        
        Parameters 
        -------
        dataframe : dataframe 
            averaged dataframe for a specific target. 
            
        avgwindow : int
            The number of sessions that should be used to calculate the moving coefficient of variation. 
            Default is a window of 100
        
        boxcar : int 
            The number of sessions that is used to smooth the Coefficient of variation data. 
            Default is a window of 300
        
        Returns 
        ------
        cv : np.array
            Contains the coefficient of variation for each tap

        i : int 
            The number in the targetframe that we are using (based on target wanted)

        """

        data = self.Find_TargetFrame(target)
        i = self.Find_i(target)

        # grab the interval column from the prespecificied dataframe. 
        ipi = data['interval']

        # find the average for the intervals. 
        avg = (ipi.rolling(avgwindow, min_periods=1).mean())
        # find the standard deviation for the intervals 
        sdev = (ipi.rolling(avgwindow, min_periods=1).std())
        # define the rough coefficient of variation as the standard deviation divided by the mean. 
        roughcv = sdev/avg
        # smooth the coefficient of variation with the moving average 
        cv = (roughcv.rolling(boxcar, min_periods=1).mean())
        # make sure any not a numbers are numpy not a number so they aren't plotted and don't break the matplotlib
        cv = cv.replace(pd.NA, np.NaN)

        # return the dataframe as a numpy array, along with the index of the targetframe. 
        return cv.to_numpy(), i 



    def CutByRat(self, dataframe, i, cv): 
        """ Returns an array with the coefficient of variation in each group by target IPI 
        
        Parameters 
        -------
        dataframe : dataframe 
            averaged dataframe for a specific target.

        i : int 
            The number in the targetframe that we are using (based on target wanted) 
            
        cv : np.array
            Contains the coefficient of variation for each tap

        Returns 
        ------
        ints : dict
            Dictionary of the cv data split up by the rat

        taps : dict
            Dictionary of the tap numbers split up by the rat         

        """

        # grab the list of cuts from the targetframe dataframe that was given as an argument
        cuts = dataframe.cuts[i]
        # find the number of cuts (ie. the number of rats in that frame) 
        leng = len(cuts)
        # initiate a dictionary
        ints = dict()
        # The first "cut" will be from the 0th trial to the first cut -- where all of the rats are averaged. 
        cutt = cv[:cuts[0]]
        # update the dictionary to include this value. 
        ints.update({'0': cutt})
        # for the number of rats in this frame, 
        for i in range(leng-1):
            # make another slice of the data from the ith to the ith+1 cut values 
            # each subsequent slice will be where there is one less rat being averaged over. 
            cutt = cv[cuts[i]:cuts[i+1]]
            # add that slice to the dictionary 
            ints.update({f'{i+1}': cutt}) 

        # initiate a dictionary for the taps
        taps = dict()
        # make a dictionary entry of a range of values from 0 to the first cut 
        # will be used for plotting so the 1st entry in the ints dictionary are the values for the 
        # taps in the 1st entry of the taps dictionary 
        taps.update({'0':range(cuts[0])}) 
        # for the number of rats, 
        for i in range(leng-1):
            # keep adding dictionary entries -- each one will be a range from XX to YY where there is a different 
            # number of rats being averaged over. These tap trial numbers match up to the ints dictionary
            taps.update({f'{i+1}':range(cuts[i], cuts[i+1])}) 
        
        # return both the ints and the taps for plotting. 
        return ints, taps 