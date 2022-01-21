
from .simple import *
import pandas as pd

#this class is designed to make sorting through the press data files easier
class DataHolder:

    #the initialization stores two dataframes in the class, one with information about specific presses and one with the general information of each session
    def __init__(self,press_info = "get",sess_info="get"):
        """Initialization stores two dataframes in the class, one with information about specific presses 
        and one with the general information of each session. 
        If there is a drop after argument, all of the sessions after that number will be dropped 
        from the output array. """

        # If the initialization of the class is left blank, 
        # open a file dialog to make the user chose the press info file. 
        if press_info == "get":
            self.press_dir = get_file()
        # If the user already indicated a file, use it.
        else:
            self.press_dir = press_info

        # If the initialization of the class is left blank, 
        # open a file dialog to make the user chose the press info file.
        if sess_info == "get":
            self.sess_dir = get_file()
        # If the user already indicated a file, use it.
        else:
            self.sess_dir = sess_info

        self._press_info_from_csv()
        self._sess_info_from_csv()
        

    def __getitem__(self,key):
        """ Python Internal. 
        Indexing method of the class"""

        # Check that the key is an interger 
        if isinstance(key,int):
            # if yes, return that number press
            return self.press_info.iloc[key]

        # Check that the key has two items
        elif isinstance(key,tuple):
            # key must be formatted as [number, column title]
            n,col = key
            # pull the nth press out 
            row = self.press_info.iloc[n]

            # if the column title exists in the press data, 
            if col in self.press_info:
                # return that column
                return row[col]

            # if the column title exists in the session data, ex  "target" or "upper" 
            elif col in self.sess_info:
                # run get sess params function to return the column from session data 
                return self.get_sess_params(int(row.name[0]))[col]
        
        # Check that the key is only a string,
        elif isinstance(key,str):

            # if the column title exists in the press data, 
            if key in self.press_info.columns:
                # return all rows from that column 
                return self.press_info[key]

            # if the column title exists in the session data, 
            elif key in self.sess_info:
                # return all rows from that column 
                return self.sess_info[key]
            
            # if the column title is "n_sess" or "n_in_sess".
            elif key in self.press_info.index.names:
                # return all rows from that column 
                return self.press_info.index.get_level_values(key)
            
            else: # if the column title is none of the above, 
                raise Exception(f"{key} is not valid")

        else: # if the format of the key is none of the above
            raise Exception(f"{type(key)} is an invalid type")
    

    #list of columns in pressinfo, includes index columns
    @property
    def columns(self):
        """ Returns a list of all of the columns in the press data."""
        # the n_sess and n_in_sess 'columns' are really indicies 
        return list(self.press_info.columns) + list(self.press_info.index.names)
        
    def _press_info_from_csv(self):
        """ Internal Function. 
        Changes indexing method from arbitrary 0,1,2,3,etc to session and number within session. 
        Drops "n_sess" and "n_in_sess" columns and creates two indexing columns titled the same. 
        Changes time column from strings to datetime objects """
        # Import csv 
        inpd = pd.read_csv(self.press_dir)
        # new dataframe with columns "n_sess" and "n_in_sess"
        indexcols = inpd[['n_sess',"n_in_sess"]]
        # drop columns "n_sess" and "n_in_sess" from og dataframe
        self.press_info = inpd.drop(['n_sess','n_in_sess'],axis=1)
        # changes the index of og dataframe to columns "n_sess" and "n_in_sess"
        self.press_info.index = pd.MultiIndex.from_frame(indexcols)
        # checks to see if there is a time column, 
        # if so, replace string dates to datetime objects
        if "time" in self.press_info:
            self.press_info['time'] = pd.to_datetime(self.press_info['time'])
    
    def _sess_info_from_csv(self):
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
        self.sess_info = inpd.copy()
        # add one to the indicies to have indicies = session number 
        self.sess_info.index+=1

        
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
        for col in self.sess_info.columns:
            # check if the conditional string includes that column name. 
            if col in conditional_string:
                # if so, change the input conditional string to one that pandas can read
                # pandas needs dataframe.loc[dataframe['column']>x]
                conditional_string = sreplace(conditional_string,col,f"self['{col}']",count_as_alpha=['_'])

        # use pandas to apply formated conditional string and extract sessions
        return self.sess_info.loc[eval(conditional_string)]

    #get all presses that match specific criteria
    def press_is(self,press_conditions = 'slice(None)',sess_conditions = 'slice(None)',column = slice(None),return_starts = False):
        #get indices of all sessions that match session criteria
        sess_indices = np.sort(list(set(self.sess_is(sess_conditions).index) & set([i[0] for i in self.press_info.index])))

        #replaces the way user writes conditions with conditions that pandas can use
        for col in self.columns:
            if col in press_conditions:
                press_conditions = sreplace(press_conditions,col,f"self['{col}']",count_as_alpha=['_'])
        outval = self.press_info.loc[eval(press_conditions)].loc[sess_indices]

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
        return self.sess_info.loc[n,col]

    #get all presses within a specific session
    def get_sess(self,n_sess):
        return self.press_info.loc[n_sess]

    #change a target in sesion data
    def change_target(self,old,new,save = False):
        targets = []
        for i in self.sess_info['target']:
            if i==old:
                targets.append(new)
            else:
                targets.append(i)
        self.sess_info['target'] = targets

        if save:
            self.overwrite_sess()
    
    #delete a session
    def drop_sess(self,n,save = False):
        if isinstance(n,int):
            n = [n]
        for i in n:
            self.press_info = self.press_info.loc[~(self.press_info.index.get_level_values(0)==i)]
            self.sess_info.loc[i]['sess_size'] = 0

        if save:
            self.overwrite_press()
            self.overwrite_sess()


   

    #compute percent errors for each trial and add it as a column
    def compute_loss(self,save = False):

        targets = np.array([self.get_sess_params(i,'target') for i in self['n_sess']])
        self.press_info['loss'] = (self['interval'] - targets)/targets

        if save:
            self.overwrite_press()

    #add session column for target of next session
    def compute_next_target(self,save = False):
        self.sess_info['next_target'] =  self.sess_info['target'].to_list()[1:] + [pd.NA]
        if save:
            self.overwrite_sess()
        
    # add session column for target of previous session
    def compute_prev_target(self,save = False):
        self.sess_info['prev_target'] =  [pd.NA] + self.sess_info['target'].to_list()[0:-1]
        if save:
            self.overwrite_sess()
        
        
    #overwrite the actual csv files so adjustments are saved for next time
    def overwrite_sess(self):
        self.sess_info.to_csv(self.sess_dir,index = False)

    def overwrite_press(self):
        self.press_info.to_csv(self.press_dir)
        
    