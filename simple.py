#this document contains all of the simple (few lines) functions I made for this project

from tkinter import filedialog
import tkinter as tk
import numpy as np
import datetime
from scipy import stats

#opens file explorer to select a file
def get_file():
    #establish a root ui and remove the window
    root = tk.Tk()
    root.withdraw()

    #open file explorer
    loc = filedialog.askopenfilename()

    #return file location as string
    return loc

# check if integer is odd
def isodd(n):
    if not isinstance(n,int):
        raise Exception(f'type {type(n)} is invalid, must be integer')
    return n%2 > 0

#returns rounded number as integer
def rndnt(n):
    return int(np.floor(n+0.5))

#returns closest integer rounding up
def cnt(n):
    return int(np.ceil(n))

#closest integer rounding down
def fnt(n):
    return int(np.floor(n))

#replaces all instances of repl inside instr with replwith, checks that repl is not part of a larger word
def sreplace(instr,repl,replwith,max_iterations=100,count_as_alpha = []):
    checkalpha = lambda x:(x.isalpha() or (x in count_as_alpha))
    #add that blank incase the thing i want to replace is at the end
    outstr = instr + ' '
    strt = 0
    i=0
    #keep looping if thing needing to be replaced is still in the string
    while outstr[strt:].find(repl)!=-1:
        i+=1

        #the first index of repl in the part of the string that hasnt yet been looked at
        strt = outstr[strt:].index(repl) + strt
        #the last index of the thing
        end = strt + len(repl)

        #check if word is part of another word
        if not (checkalpha(outstr[strt-1]) or checkalpha(outstr[end])):

            #make the replacement
            outstr = outstr[0:strt] + replwith + outstr[end:]
            #move start location for next pass
            strt = strt + len(replwith)
        else:
            strt = end

        if i>=max_iterations:
            raise Exception('timed out')

    # the [0:-1] removes that space i put at the end
    return outstr[0:-1]

#apply a function to subsets of size divsize of a larger list 
#return list of function applied to each subset
# may provide x values to have those returned for the central x value of each subset
#manage extras choses what to do if list cannot be subdivided exactly by divsize
def func_on_subsets(vals,divsize,func,manage_extras = "auto",xs = None):
    #if list does not subdivide exactly chose what to do with extra value
    manage_extras = {"auto":rndnt,"keep":cnt,"drop":fnt}[manage_extras]
    #compute the unsupplied value or give error if both or neither were given
    n = manage_extras(len(vals)/divsize)

    outlist = []
    if not isinstance(xs,type(None)):
        outxs = []
    for i in range(n):
        #starting index
        start = i*divsize
        #ending index
        end = min((i+1)*divsize,len(vals))
        #add computed value to list
        outlist.append(func(vals[start:end]))
        if not isinstance(xs,type(None)):
            outxs.append(xs[rndnt((start+end)/2) - 1])
        
    if not isinstance(xs,type(None)):
        return outlist,outxs

    return outlist

#convolve a function over a list you can include a list of x values to get those returned
def func_convolve(vals,func,divsize,xs = None):
    if not isodd(divsize):
        raise Exception('divsize must be odd')
    outlist = [func(vals[i:i+divsize]) for i in range(0,len(vals)-divsize+1)]
    if not isinstance(xs,type(None)):
        start =int((divsize/2) - 0.5)
        end = int((-divsize/2) + 0.5)
        xs = xs[start:end]
        return outlist,xs
    return outlist

#returns the variation of each  of n sub-divisions of a dataset, variation values are normalized using the variation of the whole set
def sub_variation(vals,n):
    set_var = stats.variation(vals)
    divsize = rndnt(len(vals)/n)
    return func_on_subsets(vals,divsize,lambda x:stats.variation(x)/set_var)

#simple boxcar filter
def boxcar(vals,divsize,**kwargs):
    return func_on_subsets(vals,divsize,np.mean,**kwargs)

#performs a linear fit and returns the datapoints and the slope/intercept
def lin_fit(ys,xs = "Default"):
    if xs == "Default":
        xs = range(len(ys))
    m,b=np.polyfit(xs,ys,1)
    fitys = m*xs + b
    return xs,fitys,m,b

#return the slope of convergence subdivisions in a dataset
def var_convergence(vals,n = 4):
    sub_vars = sub_variance(vals,n)
    m = lin_fit(sub_vars)[2]
    return m

#percentage of values within a range
def perc_within(vals,lower,upper):
    n = len(vals)
    s = sum(1 for i in vals if upper>=i >= lower)
    return s/n

#convert from matlab ordinal date to normal date
def OrdToDate(ord,rnd = 'hour'):
    outdate = datetime.datetime.combine(datetime.datetime.min.date(), datetime.datetime.min.time())
    outdate = outdate + datetime.timedelta(days =(ord - 367) )
    return rnddate(outdate,rnd)

#round a date to the nearest value specified by rnd
def rnddate(date,rnd = 'hour'):
    outdate = date
    if rnd  in ['second','hour','minute']:     
        outdate = outdate.replace(second = rndnt(outdate.second + (outdate.microsecond * 1e-6)),microsecond=0)
    if rnd  in ['hour','minute']:
        outdate = outdate.replace(minute = rndnt(outdate.minute + (outdate.second/60)),second=0)
    if rnd  in ['hour']:
        outdate = outdate.replace(hour = rndnt(outdate.hour + (outdate.minute/60)),minute=0)
    return outdate
