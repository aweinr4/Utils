
from .simple import *
import pandas as pd

class DataHolder:
    """ Class for holding the rat press data files """


    def __init__(self, presses = "get", sessions = "get", dropafter = 0):
        """ Initialization takes two csv files, one with press informaion and one with session information. 
        A single dataframe is created that stores all the information about each press.
        If there is a drop after argument, all of the sessions after that number will be dropped 
        from the output array.  
    
        Parameters
        ----------
        presses : str, optional
            string containing the directory of the csv with press info, by default will open a ui to select file.
        sessions : str, optional
            string containing the directory of the csv with session info, by default will open a ui to select file.
        dropafter : int, optional
            defaults to 0, this won't drop anything 

        Returns
        -------
        out : Dataholder
            instance of DataHolder class, essentially a dataframe
        """

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
        self._init_df(dropafter)



    def __getitem__(self,key):
        """ Python Internal. 
        Indexing method of the class"""

        if isinstance(key,str):
            return self.df[key]
        else:
            return self.df.loc[key]
    
    def _project_cols(self, df1, df2, projection_col, omit_col = None):
        """ add a column in df1 containing values from rows in df2 that share the same value of the argument "projection_col".
        
            Parameters
            ----------
            df1 : DataFrame
                DataFrame to project onto
            df2 : DataFrame
                Dataframe to copy values from
            projection_col : str
                column to use for matching the dataframes, column must exist in both dataframes
            omit_col : str, list, optional
                column or list of columns to ignore from df2, defaults to None. 

            Returns
            -------
            outdf : DataFrame
                copy of df1 with column added for each column in df2
            """

        outdf = df1.copy()
        copy_cols = list(df2.columns)
        if not isinstance(omit_col,type(None)):
            for col in omit_col:
                copy_cols.remove(col)
        
        for col in copy_cols:
            outdf[col] = pd.NA
            for n in df2.index:
                row = df2.loc[n]
                outdf.loc[df1[projection_col] == row[projection_col],col] = row[col]
                
        return outdf

    def _init_df(self,drop):
        """
        Initialize the dataframe with presses and sessions, uses the values for self.press_dir and self.sess_dir to make dataframes.

        Parameters
        ----------
        drop : int,optional
            drops sessions passed this number, ignores if drop = 0."""
        presses = pd.read_csv(self.press_dir)
        sessions = pd.read_csv(self.sess_dir)
        self.sess_cols = sessions.drop(['starttime','sess_size'],axis=1).columns
        self.press_cols = presses.columns
        if not drop == 0:
            presses = presses.loc[presses['n_sess'] <= drop]
            sessions = sessions.loc[sessions['n_sess'] <= drop]
        self.df = self._project_cols(presses,sessions,'n_sess',['starttime','sess_size'])

        #return index of first press in each session within a list of presses
    def _sess_start_indices(self,presslist):
        sesslist = np.sort(list(set(presslist['n_sess'])))
        indexlist = [0]
        for sess in sesslist[1:]:
            indexlist.append(indexlist[-1] + len(presslist.loc[presslist['n_sess'] == sess]))
        return (sesslist,indexlist)

    def _optimize_dtypes(self):

        typedict = {
            'reward' : 'category',
            'n_sess' : 'category'
        }

    @property
    def columns(self):
        return self.df.columns
        
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
        return self.df.loc[self.df['target'] == target][col]

    def set_of(self,col,sort = True):
        """ Returns list of all data within specified column without duplicates. 
    
        Parameters
        ----------
        col : str
            string of specific column info desired. 

        sort : bool, optional
            wether or not to sort output, defaults to true.
        
        Returns
        -------
        out : list
        """

        if sort:
            return np.sort(list(set(self[col])))

        else: 
            return list(set(self[col]))


    def press_is(self, conditional_string):
        """ Returns numbered list of all presses whose columns meet particular values
    
        Parameters
        ----------
        conditional_string : str
            Conditional string describing parameters. 
            Column name options limited to columns in df

        Returns
        -------
        out : dataframe

        Examples
        --------
        DataHolder.press_is("target > 700") or DataHolder.sess_is("700 < target")
            returns dataframe with all presses whose target value is greater than 700 
        DataHolder.press_is("(target >= 500) & (interval > 10)")
            returns dataframe with all presses whose target is greater than or equal to 500 with an interval larger than 10
        """
        
        # for all of the columns in the dataframe,
        for col in self.df.columns:
            # check if the conditional string includes that column name. 
            if col in conditional_string:
                # if so, change the input conditional string to one that pandas can read
                # pandas needs dataframe.loc[dataframe['column']>x]
                conditional_string = sreplace(conditional_string,col,f"self.df['{col}']",count_as_alpha=['_'])

        # use pandas to apply formated conditional string and extract presses
        return self.df.loc[eval(conditional_string)]

    def get_first_press(self,conditional_string):
        """ Get the row of the first press that matches specific criteria
        
        Parameters 
        ----
        conditional_string : str
            Conditional string describing parameters. 
            Column name options limited to columns in df
        Returns
        ---
        outval : series
        """
        return self.press_is(conditional_string).iloc[0]

       
    def get_sess_params(self, n, col = slice(None)):
        """ Get the paramaters for a specific session
        
        Parameters 
        ----
        n : int
            number of session
        
        col : str, optional
            specific column if desired

        Returns
        ---
        outval : series
            row for the requestion session
        """
        return self.get_first_press(f"n_sess == {n}")[self.sess_cols][col]

    def all_sessions(self,col):
        """ get the value of a parameter for all sessions
        
        Parameters 
        ----
        col : str, optional
            specific column you want the value for

        Returns
        ---
        outval : list
            the value of the column in every session
        """
        return [self.get_sess_params(i)[col] for i in self.set_of('n_sess')]
    
    def get_sess(self, n_sess):
        """ Get all presses within a particular session
        
        Parameters 
        ----
        n_sess : int
            number of session

        Returns
        ---
        outval : dataframe
            all presses within the requested session
        """
        return self.df[self.df['n_sess'] == n_sess]


    def change_target(self, old, new, save = False):
        """ change the target interval wherever it appears
        
        Parameters 
        ----
        old : int
            value of interval to be changed

        new : int
            value of new interval
        
        save : boolean
            wether or not to permenantly change csv. Default is false.

        Returns
        ---
        none
        """
        self.df[self.df['target'] == old,'target'] = new

        if save:
            self.overwrite_sess()
    

    def drop_sess(self, n, save = False):
        """ delete a session
        
        Parameters 
        ----
        n : int or list
            number or list of numbers of sessions to be deleted
        
        save : boolean
            wether or not to permenantly change csv. Default is false.

        Returns
        ---
        none
        """

        #if integer, insert it into a list, this allows interger or list as input
        if isinstance(n,int):
            n = [n]
        
        #iterate through list of n values
        for i in n:
            self.df = self.df[~(self.df['n_sess'].isin(n))]

        if save:
            self.overwrite_press()
            self.overwrite_sess()

    def stats(self, stat, column, save = False):
        """ Compute a column of session statistics about a column from presses
    
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
        for i in self.set_of('n_sess'):
            try:
                row = self.get_sess(i)[column].to_numpy()
                statcol.append(eval(f"row.{stat}()"))
            except KeyError:
                statcol.append(pd.NA)

        if save:
            self.overwrite_sess(**{column + "_" + stat : statcol})

        return statcol

    def TrialSuccess(self, error, avgwindow = 100):
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
        successes : np.array
            Contains the number of succcesses for each session
        avg : np.array
            Contains the moving average of the successes per session

        """
 
        # grab the percentage error for each trial 
        loss = (self.df['loss']).to_numpy()
        # define upper and lower bounds
        upper = error/100
        lower = -error/100 

        #convert a bool array of wether or not losses are in between bounds to integer array 
        success = ((loss <= upper) & (lower <= loss)).astype(int)
        # make the data into a dataframe
        df = pd.DataFrame(success, columns = ['Success'])
        # use the pandas built-in 'rolling' to calculate the moving average. 
        # and assign it to 'avgs'
        avgs = (df.rolling(avgwindow, min_periods=1).mean())*100
        # return the averages
        return avgs

    def SessionSuccess(self, error, avgwindow = 5):
        """ Returns an array with the percentage of successes in each session where the trial IPI was 
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
        successes : np.array
            Contains the number of succcesses for each session
        avg : np.array
            Contains the moving average of the successes per session

        """
        # create blank array for the session successes. 
        success = [] 
        # iterate through all of the sessions whose number of trials isn't zero.
        for i in self.set_of('n_sess'):
            # error in the csv is in decimal form, so convert to upper and lower bounds. 
            upper = error/100 
            lower = -error/100
            # pull all presses for a particular session
            data = self.get_sess(i)['loss']
            # perc_within returns percentage of values between lower and upper within data
            data = perc_within(data,lower,upper) * 100
            # append the number of successes for that session
            success.append(data)
        # create a new dataframe with the successes
        df = pd.DataFrame(success, columns = ['Success'])
        # use the pandas built-in 'rolling' to calculate the moving average. 
        # and add a column to the dataframe with the moving averages. 
        movingavg = df.rolling(avgwindow, min_periods=1).mean()
        avgs = movingavg.to_numpy()
        # return the two numpy lists.
        return success, avgs

    def overwrite_sess(self,**kwargs):
        """ overwrite the session csv using the location given when the class was instantiated
        
        Parameters 
        ----
        none

        Returns
        ---
        none
        """
        sessions = pd.read_csv(self.sess_dir)
        sessions = sessions.loc[sessions['n_sess'].isin(self.set_of('n_sess'))]
        sessions.sort(['n_sess'],inplace = True)
        for col in self.sess_cols:
            sessions[col] = self.df[col]

        if kwargs:
            for key,val in kwargs.items():
                sessions[key] = val
        sessions.to_csv(self.sess_dir)

    def overwrite_press(self):
        """ overwrite the presses csv using the location given when the class was instantiated
        
        Parameters 
        ----
        none

        Returns
        ---
        none
        """
        presses = pd.read_csv(self.press_dir)
        presses = presses.loc[presses['n_sess'].isin(self.set_of('n_sess'))]
        presses.sort_values(['n_sess','n_in_sess'],inplace=True)
        for col in self.press_cols:
            presses[col] = self.df[col]
        self.presses.to_csv(self.press_dir)

