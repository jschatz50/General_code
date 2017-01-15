#------------#
#-- AUTHOR --#
#------------#
## Jason Schatz
## Created: 12/28/2016
## Last modified: 12/29/2016


#---------------#
#-- FILE INFO --#
#---------------#
## basic, frequently-used functions for reading,
## writing, and manipulating dataframes


#----------------------#
#-- IMPORT LIBRARIES --#
#----------------------#
import csv
import glob
import inspect
import numpy as np
import os
import pandas as pd


#--------------------------#
#-- object introspection --#
#--------------------------#
type()
dir()
id()
vars()
getattr()
hasattr()
globals()
locals()
callable()
inspect.getsource(function_name)
function_name?   (shortcut for help(function_name))
function_name??  ##source code


#----------------------#
#-- create dataframe --#
#----------------------#
## empty dataframe
columns = ['colname1', 'colname2', 'colname3']
index = range(20)
df1 = pd.DataFrame(index=index, columns=columns)

## from array
columns = ['colname1', 'colname2', 'colname3']
data = np.array([np.random.normal(10, 3, 20)] * 3).T   # [np.random.normal(mean, stdev, n)] * ncols
data = np.array([[3, 4, 2, 3], 
	             [2, 1, 3, 2], 
	             [3, 1, 3, 7]]).T
df1 = pd.DataFrame(data, columns = columns)

## from data dictionary
data = {'colname1': [3, 4, 2, 3],
        'colname2': [2, 1, 3, 2],
        'colname3': [3, 1, 3, 7]
       }
df1 = pd.DataFrame(data)


#-------------------#
#-- set directory --#
#-------------------#
path1 = "C:/Users/jason.schatz/Documents/Code/Python code/sample_data"
os.chdir(path1)   #set directory
os.getcwd()   #check directory


#------------------------#
#-- import/export data --#
#------------------------#
## read csv
df1 = pd.read_csv('CSV_file1.csv')

## read excel
xl = pd.ExcelFile("excel_spreadsheet1.xlsx")
xl.sheet_names
df = xl.parse("values")

## write csv
df1.to_csv(path1 + "written1.csv", index = False)


#---------------------#
#-- data attributes --#
#---------------------#
df1.dtypes    # returns data types for each column
df1.shape     # nrows, ncols
len(df1)      # nrows
len(df1.columns) # ncols
df1.head()    # top of dataframe
df1.tail()    # tail of dataframe
df1.columns   # column names
df1.describe()  # summarize values by column
df1.colname1.mean   # mean of colname1 in df1


#----------------------#
#-- (re)name columns --#
#----------------------#
df1.columns = ['colname1', 'colname2', 'colname3']          # rename all columns
df1.rename(columns = {'colname1': 'new_name'}, inplace = True)   # rename specific column
names = df1.columns.values   # pull column names from 1st data frame
df1.columns = names          # replace column names in 2nd data frame
df1.columns = map(str.upper, df1.columns)   # column names to uppercase
df1.columns = map(str.lower, df1.columns)   # column name to lowercase


#-----------------#
#-- subset data --#
#-----------------#
df1[(df1.colname1 == 'a')]
df1[(df1.colname2 < 5) & (df1.colname3 > 5)]
df1[df1['colname1'] > 1]
df1.query('colname2 < 5 & colname3 > 5')   # same as line above

df1['colname1']   # select by column name
df1[[1]]          # select by column index
df1.iloc[2]       # select by row index
df1.iloc[2:4]     # select by range of rows (not inclusive...returns row 2 and 3)
df1.at[0, 'colname2']    # label based lookup; [row, column]
df1.iat[3, 1]            # index based lookup; first is row, second is column


#------------------------#
#-- add/delete columns --#
#------------------------#
df1['col4'] = df1['colname2'] + df1['colname3']
df1['e'] = df1['colname1']
df1.drop('colname1', axis = 1, inplace = True)   # drop by column name
df1.drop(df2.columns[[3]], axis = 1)      # drop by index


#-------------------------#
#-- append rows/columns --#
#-------------------------#
names = df1.columns.values   #pull column names from 1st data frame
df2.columns = names   #replace column names in 2nd data frame
pd.concat([df1,df2], axis = 1)   #append columns
pd.concat([df1,df2], axis = 0)   #append rows


#---------------#
#-- sort data --#
#---------------#
df1.sort_values(by = 'colname1')              # sort vertically by column
df1.sort_index(axis = 1, ascending = False)   # sort horizontally by column


#----------------#
#-- merge data --#
#----------------#
## left/right merge of two dataframes
pd.merge(df1, df2, how = 'left',  left_on = ['colname2'], right_on = ['b'])   # keeps all x
pd.merge(df1, df2, how = 'right', left_on = ['colname2'], right_on = ['b'])   # keeps all y
pd.merge(df1, df2, how = 'inner', left_on = ['colname2'], right_on = ['b'])   # keeps only common indices
pd.merge(df1, df2, how = 'outer', left_on = ['colname2'], right_on = ['b'])   # keeps all

## merge many files left/right with common column name
import_list = glob.glob(path1 + '/*.csv')
file_list = [pd.read_csv(file) for file in import_list]
merged = reduce(lambda left, right: pd.merge(left, right, how='outer', on = 'a'), file_list)

## vertical merge files with same column names
import_list = glob.glob(path1 + '/*.csv')
file_list = [pd.read_csv(file) for file in import_list]
merged = pd.concat(file_list)


#--------------------#
#-- aggregate data --#
#--------------------#
df1.pivot_table(index = 'column1', values = 'values', aggfunc = np.mean)
counts = df1.groupby(['colname3']).agg(['count'])
counts.reset_index(inplace = True)  
counts.columns = counts.columns.droplevel()
counts.columns = ['group', 'agg1', 'agg2', 'agg3']


#------------------#
#-- reshape data --#
#------------------#
df = pd.DataFrame({'A': {0: 'a', 1: 'b', 2: 'c'},
                   'B': {0: 1, 1: 3, 2: 5},
                   'C': {0: 2, 1: 4, 2: 6}
                  })

## wide to long
pd.melt(df, id_vars=['A'], value_vars=['B', 'C'])
df = pd.melt(df, id_vars=['A'])   # leave value_vars arg empty to treat all columns as values

## long to wide
df = df.pivot(index='A', columns='variable', values='value') # for multiple indices, specify as a list
pd.DataFrame(df.to_records())


#------------------------------#
#-- replace specified values --#
#------------------------------#
df1[df1 == 1] = np.nan


#---------------------------#
#-- duplicate/unique data --#
#---------------------------#
df1.drop_duplicates('colname3', keep = 'first')   # keep first duplicate
df1.drop_duplicates('colname3', keep = 'last')    # keep last duplicate
df1.drop_duplicates('colname3', keep = False)     # remove all duplicates
df1[df1.duplicated('colname3',  keep = False)]    # return all duplicated rows
df1.colname3.unique()                             # return all unique elements/levels


#-----------------------#
#-- convert data type --#
#-----------------------#
df1['test'] = df1['colname1'].astype(str)
pd.to_numeric(df1['test'], errors='coerce')
