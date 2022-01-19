
from .simple import *
import pandas as pd

#this class is designed to make sorting through the press data files easier
class press_data:

    #the initialization stores two dataframes in the class, one with information about specific presses and one with the general information of each session
    def __init__(self,press_info = "get",sess_info="get"):
        #open gui to select press data file
        if press_info == "get":
            self.press_dir = get_file()
        else:
            self.press_dir = press_info

        self._press_info_from_csv()
        #open gui to select session info data file
        if sess_info == "get":
            self.sess_dir = get_file()
        else:
            self.sess_dir = sess_info

        self._sess_info_from_csv()
        

    #indexing method of this class
    def __getitem__(self,key):
        #a number returns that row
        if isinstance(key,int):
            return self.press_info.iloc[key]

        # a number and string returns information about that trial
        elif isinstance(key,tuple):
            n,col = key
            row = self.press_info.iloc[n]
            if col in self.press_info:
                return row[col]

            #asking for session info like "target" or "upper" will return the information from the relevant session
            elif col in self.sess_info:
                return self.get_sess_params(int(row.name[0]))[col]
            elif col == "loss":
                self.compute_loss(save = True)
                return self[key]
        
        elif isinstance(key,str):

            if key in self.press_info.columns:
                return self.press_info[key]
            elif key in self.sess_info:
                return self.sess_info[key]
            elif key in self.press_info.index.names:
                return self.press_info.index.get_level_values(key)
            else:
                raise Exception(f"{key} is not valid")
        else:
            raise Exception(f"{type(key)} is an invalid type")
    
    #list of columns in pressinfo, includes index columns
    @property
    def columns(self):
        return list(self.press_info.columns) + list(self.press_info.index.names)
        
    def _press_info_from_csv(self):
        inpd = pd.read_csv(self.press_dir)
        indexcols = inpd[['n_sess',"n_in_sess"]]
        self.press_info = inpd.drop(['n_sess','n_in_sess'],axis=1)
        self.press_info.index = pd.MultiIndex.from_frame(indexcols)
        if "time" in self.press_info:
            self.press_info['time'] = pd.to_datetime(self.press_info['time'])
    
    def _sess_info_from_csv(self):
        inpd = pd.read_csv(self.sess_dir)
        if 'starttime' in inpd:
            inpd['starttime'] = pd.to_datetime(inpd['starttime'])
        self.sess_info = inpd.copy()
        self.sess_info.index+=1

        
    def get_by_target(self,target,col =slice(None)):
        return self.press_is(sess_conditions=f"target == {target}",column=col)

    #return all possible values of a particular column without duplicates
    def set_of(self,col):
        return list(set(self[col]))

    #returns numbered list of all sessions whose columns meet particular values, input is conditional string
    def sess_is(self,conditional_string):
        for col in self.sess_info.columns:
            if col in conditional_string:
                conditional_string = sreplace(conditional_string,col,f"self['{col}']",count_as_alpha=['_'])

       
        return self.sess_info.loc[eval(conditional_string)]

    #return index of first press in each session within a list of presses
    def _sess_start_indices(self,presslist):
        sesslist = np.sort(list(set(presslist.index.get_level_values(0))))
        indexlist = [len(presslist.loc[0:i]) for i in sesslist]
        return (sesslist,indexlist)

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
        
    