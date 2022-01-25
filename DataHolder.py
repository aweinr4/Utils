
from .simple import *
import pandas as pd


class DataHolder:
    """ Class for holding the rat press data files """


    def __init__(self, presses = "get", sessions = "get", dropafter = 0):
        """Initialization stores two dataframes in the class, one with information about specific presses 
        and one with the general information of each session. 
        If there is a drop after argument, all of the sessions after that number will be dropped 
        from the output array. """

        # If the initialization of the class is left blank, 
        # open a file dialog to make the user chose the press info file. 
        if presses == "get":
            self.press_dir = get_file()
        # If the user already indicated a file, use it.
        else:
            self.press_dir = presses

        # If the initialization of the class is left blank, 
        # open a file dialog to make the user chose the press info file.
        if sessions == "get":
            self.sess_dir = get_file()
        # If the user already indicated a file, use it.
        else:
            self.sess_dir = sessions

        # do preprocessing of the dataframes. 
        self._presses_from_csv()
        self._sessions_from_csv()

        # if a dropafter command is entered, then run the dropping function. 
        # otherwise default value is 0 so the if statement will be false. 
        if dropafter != 0:
            self._drop_after(dropafter)


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
    

    def _drop_after(self, drop):
        """ Internal Function. 
        Drops sessions from the data after the desired session number X. 
        Changes both the presses info to eliminate all presses after session X, 
        And gets rid of all session summaries after session X"""
        # doesn't really "drop" anything, just selects for rows below the final session index. 
        # select the rows out of the session data where the index is greater than the dropping value
        self.sessions = self.sessions[self.sessions.index<=drop]
        # select the rows out of the press data where the number of the session is greater than drop value. 
        self.presses = self.presses[self["n_sess"]<=drop]


    def _presses_from_csv(self):
        """ Internal Function. 
        Changes indexing method from arbitrary 0,1,2,3,etc to session and number within session. 
        Drops "n_sess" and "n_in_sess" columns and creates two indexing columns titled the same. 
        Changes time column from strings to datetime objects """
        # Import csv, make n_sess and n_in_sess columns as index
        self.presses = pd.read_csv(self.press_dir,index_col=['n_sess','n_in_sess'])
        # checks to see if there is a time column, 
        # if so, replace string dates to datetime objects
        if "time" in self.presses:
            self.presses['time'] = pd.to_datetime(self.presses['time'])
    

    def _sessions_from_csv(self):
        """ Internal Function. 
        Changes time column from strings to datetime objects. 
         """
        # Import csv
        self.sessions = pd.read_csv(self.sess_dir, index_col='n_sess')
        # checks to see if there is a time column, 
        # if so, replace string dates to datetime objects
        if 'starttime' in self.sessions:
            self.sessions['starttime'] = pd.to_datetime(self.sessions['starttime'])


        #return index of first press in each session within a list of presses
    def _sess_start_indices(self,presslist):
        sesslist = np.sort(list(set(presslist.index.get_level_values(0))))
        indexlist = [len(presslist.loc[0:i]) for i in sesslist]
        return (sesslist,indexlist)

        
    def get_by_target(self,target,col =slice(None)):
        """ Returns all of the presses that have a particular target. 
    
        Parameters
        ----------
        target : int
            integer value of the interpress interval target
        col : str, optional
            string of specific column desired, default includes all columns. 

        Returns
        -------
        out : dataframe or series
            dataframe containing presses that have the desired target and desired columns.
        """
        # calls press_is function to return the dataframe. 
        return self.press_is(sess_conditions=f"target == {target}",column=col)


    def set_of(self,col):
        """ Returns list of all data within specified column without duplicates. 
    
        Parameters
        ----------
        col : str
            string of specific column info desired. 

        Returns
        -------
        out : list
        """
        return list(set(self[col]))


    def sess_is(self, conditional_string):
        """ Returns numbered list of all sessions whose columns meet particular values
    
        Parameters
        ----------
        conditional_string : str
            Conditional string describing parameters. 
            Column name options limited to columns in session info 

        Returns
        -------
        out : dataframe

        Examples
        --------
        DataHolder.sess_is("target > 700") or DataHolder.sess_is("700 < target")
            returns dataframe with all sessions whose target value is greater than 700 
        DataHolder.sess_is("(target >= 500) & (sess_size > 10)")
            returns dataframe with all sessions whose target is greater than or equal to 500 with a session size larger than 10
        """
        
        # for all of the columns in the session info dataframe,
        for col in self.sessions.columns:
            # check if the conditional string includes that column name. 
            if col in conditional_string:
                # if so, change the input conditional string to one that pandas can read
                # pandas needs dataframe.loc[dataframe['column']>x]
                conditional_string = sreplace(conditional_string,col,f"self['{col}']",count_as_alpha=['_'])

        # use pandas to apply formated conditional string and extract sessions
        return self.sessions.loc[eval(conditional_string)]

    def press_is(self, press_conditions = 'slice(None)', sess_conditions = 'slice(None)', column = slice(None), return_starts = False):
        """ Get all presses that mach specific criteria
        
        Parameters 
        ----
        press_conditions : string 
            String of conditions for the presses. Operates on the columns of the presses csv.

        sess_conditions : string 
            String of conditions for the sessions. Operates on the columns of the session csv.

        column : string 
            String for the column name desired.  

        return_starts : 
            ? 

        Returns
        ---
        outval : dataframe
            Dataframe with only the data that matches the input criteria.
        """
        #get indices of all sessions that match session criteria
        sess_indices = np.sort(list(set(self.sess_is(sess_conditions).index) & set([i[0] for i in self.presses.index])))

        #replaces the way user writes conditions with conditions that pandas can use
        for col in self.columns:
            if col in press_conditions:
                press_conditions = sreplace(press_conditions,col,f"self['{col}']",count_as_alpha=['_'])
        outval = self.presses.loc[eval(press_conditions)].loc[sess_indices]

        #record start index for each session incase it is requested
        starts = self._sess_start_indices(outval)

        #restrict to a specific column if requested
        if column == 'n_in_sess':
            outval =  outval.index.get_level_values(1)
        elif column == 'n_sess':
            outval =  outval.index.get_level_values(0)
        else:
            outval = outval[column]
            
        if return_starts:
            outval = (outval,starts)
        return outval




    #get first press that matches specific criteria
    def get_first_press(self,press_conditions = 'slice(None)',sess_conditions = 'slice(None)'):
        return self.press_is(press_conditions=press_conditions,sess_conditions=sess_conditions).iloc[0]

    #get the information about a specific session        
    def get_sess_params(self,n,col = slice(None)):
        return self.sessions.loc[n,col]

    #get all presses within a specific session
    def get_sess(self,n_sess):
        return self.presses.loc[n_sess]

    #change a target in sesion data
    def change_target(self,old,new,save = False):
        targets = []
        for i in self.sessions['target']:
            if i==old:
                targets.append(new)
            else:
                targets.append(i)
        self.sessions['target'] = targets

        if save:
            self.overwrite_sess()
    
    #delete a session
    def drop_sess(self,n,save = False):
        if isinstance(n,int):
            n = [n]
        for i in n:
            self.presses = self.presses.loc[~(self.presses.index.get_level_values(0)==i)]
            self.sessions.drop(i,inplace = True)

        if save:
            self.overwrite_press()
            self.overwrite_sess()

    def stats(self, stat, column, save = False):
        """ Add a column of statistics about a column from presses
    
        Parameters
        ----------
        stat : str
            statistic you want taken, can be mean,median,mode,max,min, or std

        column : str
            name of column from presses

        save: Boolean, optional
            wether or not to overwrite the csv

        Returns
        -------
        None

        """

        statcol = []
        for i in self.sessions.index:
            try:
                row = self.get_sess(i)[column].to_numpy()
                statcol.append(eval(f"row.{stat}()"))
            except KeyError:
                statcol.append(pd.NA)
        self.sessions[column + "_" + stat] = statcol

        if save:
            self.overwrite_press()


    def PercentDiff(self): 
        """ Function to pull the target ipi, actual ipi, and percent difference 
        from the target for each press within the sessions.
        Output is a dataframe with target ipi/ ipi/ %difference columns with length of the number of trials."""
        # pull the target ipi from the sessionlist and add another column to the presslist dataframe. 
        # this is because the target ipi will vary depending on the session. 

        data = self.presses[["n_sess","interval","ratio","loss"]]
        return data 


    def AllTargets(self):
        """ Outputs a dataframe with the target ipi for every trial. 
        Used for plotting purposes. """
        # initialize the framedata array 
        framedata = []
        # make a dataframe for the targets for every press trial. 
        for i in range(1, self.sessions.shape[0]+1): 
            # pull the target from the session dataframe
            # find the row with the index the same as i, and pull target from it 
            # convert that to numpy, and then take the 0th item (there is only one item) 
            target = ((self.sessions[self.sessions.index==i]['target']).to_numpy())[0]
            data = self.presses[self.presses["n_sess"]==i]
            # make a numpy array the length of the number of trials in the session
            # with the values being the target interval of that session. 
            targets = np.full(data.shape[0], target)

            # append each session's data to the frame 
            framedata = np.append(framedata, targets, axis=0)

        targetframe = pd.DataFrame(framedata, columns=['target'])

        # Return the data and the target frame
        return targetframe

    def SessionTargets(self):
        """ Outputs a dataframe with the target ipi for every session. 
        Used for plotting purposes. """
        return self.sessions["target"]

    def Taps(self): 
        """ Outputs a data frame with the tap lengths and interval for each trial"""
        return self.presses[["interval","tap_1_len","tap_2_len"]]


    def Success(self, error, avgwindow = 5):
        """ Returns an array with the number of successes in each session where the trial IPI was 
        +- error % away from the target IPI. 
        
        Parameters 
        -------
        error : int
            The numerical value of the percentage bounds from target desired. 
        avgwindow : int
            The number of sessions that should be used to calculate the moving average. 
            Default is a window of 5 
        
        Returns 
        ------
        successes : dataframe
            Contains the number of succcesses for each session and the moving average of successes. 

        """
        # create blank array for the session successes. 
        success = [] 
        # iterate through all of the sessions 
        for i in range(1, self.sessions.shape[0]+1):
            # error in the csv is in decimal form, so convert to upper and lower bounds. 
            upper = error/100 
            lower = -error/100
            # pull out a dataframe of the sessions that are between the bounds for each session i 
            data = self.press_is(press_conditions = f'(loss <= {upper}) & (loss >= {lower}) & (n_sess == {i})')
            # append the number of successes for that session
            success.append(data.shape[0])
        # create a new dataframe with the successes
        df = pd.DataFrame(success, columns = ['NumSuccess'])
        # use the pandas built-in 'rolling' to calculate the moving average. 
        # and add a column to the dataframe with the moving averages. 
        df['MovingAvg'] = df.rolling(avgwindow, min_periods=1).mean()

        # return the dataframe.
        return df

    #overwrite the actual csv files so adjustments are saved for next time
    def overwrite_sess(self):
        self.sessions.to_csv(self.sess_dir)

    #not working at the moment, need to account for indexing method
    def overwrite_press(self):
        self.presses.to_csv(self.press_dir)
