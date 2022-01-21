
from .simple import *
import pandas as pd

#this class is designed to make sorting through the press data files easier
class DataHolder:

    #the initialization stores two dataframes in the class, one with information about specific presses and one with the general information of each session
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
        # Import csv 
        inpd = pd.read_csv(self.press_dir)
        # new dataframe with columns "n_sess" and "n_in_sess"
        indexcols = inpd[['n_sess',"n_in_sess"]]
        # drop columns "n_sess" and "n_in_sess" from og dataframe
        self.presses = inpd.drop(['n_sess','n_in_sess'],axis=1)
        # changes the index of og dataframe to columns "n_sess" and "n_in_sess"
        self.presses.index = pd.MultiIndex.from_frame(indexcols)
        # checks to see if there is a time column, 
        # if so, replace string dates to datetime objects
        if "time" in self.presses:
            self.presses['time'] = pd.to_datetime(self.presses['time'])
    
    def _sessions_from_csv(self):
        """ Internal Function. 
        Changes time column from strings to datetime objects. 
        Increments the indicies to have indicies = session number """
        # Import csv
        inpd = pd.read_csv(self.sess_dir)
        # checks to see if there is a time column, 
        # if so, replace string dates to datetime objects
        if 'starttime' in inpd:
            inpd['starttime'] = pd.to_datetime(inpd['starttime'])
        # pandas is weird, so make a copy of og dataframe. 
        self.sessions = inpd.copy()
        # add one to the indicies to have indicies = session number 
        self.sessions.index+=1

    @property
    def columns(self):
        """ Returns a list of all of the columns in the press data."""
        # the n_sess and n_in_sess 'columns' are really indicies 
        return list(self.presses.columns) + list(self.presses.index.names)
        
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

    #get all presses that match specific criteria
    def press_is(self,press_conditions = 'slice(None)',sess_conditions = 'slice(None)',column = slice(None),return_starts = False):
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

    #return index of first press in each session within a list of presses
    def _sess_start_indices(self,presslist):
        sesslist = np.sort(list(set(presslist.index.get_level_values(0))))
        indexlist = [len(presslist.loc[0:i]) for i in sesslist]
        return (sesslist,indexlist)



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
            self.sessions.loc[i]['sess_size'] = 0

        if save:
            self.overwrite_press()
            self.overwrite_sess()


    def FindStats(self): 
        """ Function to find the minimum, maximum, average, and standard deviation for the 
        interpress intervals of each session. Columns are added to the sessions dataframe."""
        # create a null framedata so the np.append later works correctly. 
        framedata = [[0,0,0,0,0,0,0]]
        # sessionlist.shape[0] gives the number of sessions there were starting at 0
        # But there is no session zero, so range from 1 to shape[0]+1
        for i in range(1, self.sessions.shape[0]+1):
            # find the rows within the dataframe that have the session number of the current iteration
            # create a new smaller dataframe with only that data ^^^ 
            data = self.get_sess(i)
            # some of the sessions are empty due to NaN rat presses,
            # filters for only sessions that aren't empty. 
            if not data.empty:
                # reassign the dataframe to be only a list of the interpress interval 
                # for each trial within the current session number
                data = data['interval'] 

                # change the pandas dataframe to a numpy array for the min/max analysis 
                intervals = data.to_numpy()
                # min, max, avg, and sdev 
                min = intervals.min()
                max = intervals.max()
                avg = intervals.mean()
                sdev = intervals.std()

                # format the data into an array 
                neu_data = np.array([min, max, avg, sdev], dtype=object)

                # append each session's data to the frame 
                framedata = np.append(framedata, [neu_data], axis=0)

        # once the frame is fully constructed, drop the null framedata entry 
        framedata = framedata[1::]

        #add columns in sessions for min,max,avg and sdev
        self.sessions['min'] = framedata[0:,0]
        self.sessions['max'] = framedata[0:,1]
        self.sessions['avg'] = framedata[0:,2]
        self.sessions['sdev'] = framedata[0:,3]
    
    def AvgTaps(self):
        """ Outputs a data frame with the average tap lengths and intervals for each session"""
        #self.presses[["interval","tap_1_len","tap_2_len"]]

        framedata = [[0,0,0]]
        # sessionlist.shape[0] gives the number of sessions there were starting at 0
        # But there is no session zero, so range from 1 to shape[0]+1
        for i in range(1, self.sessions.shape[0]+1):
            # find the rows within the dataframe that have the session number of the current iteration
            # create a new smaller dataframe with only that data ^^^ 
            data = self.get_sess(i)
            # some of the sessions are empty due to NaN rat presses,
            # filters for only sessions that aren't empty. 
            if not data.empty:
                # pull the interval, tap1 and tap2 info out of the dataframe, 
                interval = (data['interval']).to_numpy()
                tap1 = (data['tap_1_len']).to_numpy()
                tap2 = (data['tap_2_len']).to_numpy()

                # average the values,
                interval = interval.mean()
                tap1 = tap1.mean()
                tap2 = tap2.mean()

                # format the data into an array 
                neu_data = np.array([interval, tap1, tap2], dtype=object)

                # append each session's data to the frame 
                framedata = np.append(framedata, [neu_data], axis=0)

        # once the frame is fully constructed, drop the null framedata entry 
        framedata = framedata[1::]

        # format the output as a new pandas dataframe. 
        return pd.DataFrame(framedata, columns=['interval','tap_1_len', 'tap_2_len'])

    def stats(self, stat, column):
        """ Add a column of statistics about a column from presses
    
        Parameters
        ----------
        stat : str
            statistic you want taken, can be mean,median,mode,max,min, or std

        column : str
            name of column from presses

        Returns
        -------
        None

        """

        statcol = []
        for i in self.set_of('')


    #overwrite the actual csv files so adjustments are saved for next time
    def overwrite_sess(self):
        self.sessions.to_csv(self.sess_dir,index = False)

    #not working at the moment, need to account for indexing method
    def overwrite_press(self):
        self.presses.to_csv(self.press_dir)
        
    