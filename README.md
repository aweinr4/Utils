# About Wolff_Data_Utils:

DataHolder.py: 
Takes in the raw press.csv and session.csv data from each rat and does preprocessing on it. 

DataHolder_Plot.py
Takes in objects produced by the DataHolder class and creates plots (IPI, CV, SR, etc.) 

DataAvgs.py:
Takes in multiple DataHolder objects and averages them by group. 

DataAvgs_Plot.py
Takes in objects produced by the DataAvgs class and creates plots (IPI, CV, SR, etc.) 

__init__.py, process_csv.py, and simple.py: 
Referenced in the above files, each does behind-the-scenes work. 
