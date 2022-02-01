
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
        targets = ratlist[0].set_of('target') 

        # do the preprocessing 
        targetlist = self._preprocessing(datalist, targets)

        # get the list of cutoff values
        cutofflist = self._find_cutoff_values(targetlist)
        # make it into a self-referencing variable
        self.cuts = cutofflist

        # average the rats into a single dataframe per target
        targetframe = self._averaging(targetlist) 
        # make it into a self-referencing variable
        self.targetframe = targetframe 


    def _frames_by_target(self, datalist, targets):
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
        for target in targets:
            # for each of the rats, 
            for frame in datalist:
                # grab the entries that have a specific target
                data = frame.loc[frame["target"]==target]
                # append that data to the dataframe 
                dataframes.append(data)
            # append the dataframe for the whole target group to the targetframe 
            targetframes.append(dataframes)
            # reset the dataframe for the next target group 
            dataframes = []
        return targetframes 


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
    

    def _preprocessing(self, datalist, targets):
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
        targetframes = self._frames_by_target(datalist, targets)
        # create blank targetlist for storing the new dataframes and blank dataframes for iterating over 
        targetlist = []
        dataframes = []
        # for each of the target groups, 
        for target in targetframes:
            # for each of the dataframes within the target group, 
            for frame in target:
                # grab only the columns that we want to average over
                press = frame.copy()[["interval", "tap_1_len", "tap_2_len", "ratio", "loss", "target"]]
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
            # grab the datframes by the target group
            data = targetlist[i]         
            # concatenate the data
            newpress = pd.concat(data)
            # use builtin .groupby() to stack the frames and then average. 
            avg = newpress.groupby(level=0).mean()
            # append the data entry to the single averaged dataframe. 
            targetframe.append(avg) 
            # step up i
            i += 1 
        # return the list of averaged dataframes. 
        return targetframe


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

    