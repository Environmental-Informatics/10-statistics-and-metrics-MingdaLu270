#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 10 11:48:18 2020

@author: lu270
"""

# This script servesa as the solution set for assignment-10 on descriptive
# statistics and environmental informatics.  See the assignment documention 
# and repository at:
# https://github.com/Environmental-Informatics/assignment-10.git for more
# details about the assignment.
#
import pandas as pd
import scipy.stats as stats
import numpy as np

def ReadData( fileName ):
    """This function takes a filename as input, and returns a dataframe with
    raw data read from that file in a Pandas DataFrame.  The DataFrame index
    should be the year, month and day of the observation.  DataFrame headers
    should be "agency_cd", "site_no", "Date", "Discharge", "Quality". The 
    "Date" column should be used as the DataFrame index. The pandas read_csv
    function will automatically replace missing values with np.NaN, but needs
    help identifying other flags used by the USGS to indicate no data is 
    availabiel.  Function returns the completed DataFrame, and a dictionary 
    designed to contain all missing value counts that is initialized with
    days missing between the first and last date of the file."""
    
    # define column names
    colNames = ['agency_cd', 'site_no', 'Date', 'Discharge', 'Quality']

    # open and read the file
    DataDF = pd.read_csv(fileName, header=1, names=colNames,  
                         delimiter=r"\s+",parse_dates=[2], comment='#',
                         na_values=['Eqp'])
    DataDF = DataDF.set_index('Date')
    
    # quantify the number of missing values
    MissingValues = DataDF["Discharge"].isna().sum()
    
    return( DataDF, MissingValues )

def ClipData( DataDF, startDate, endDate ):
    """This function clips the given time series dataframe to a given range 
    of dates. Function returns the clipped dataframe and and the number of 
    missing values."""
    
    # locate the required data
    DataDF=DataDF.loc[startDate:endDate]
    
    # Missing values for the specific period of data
    MissingValues=DataDF["Discharge"].isna().sum()
    
    return( DataDF, MissingValues )

def CalcTqmean(Qvalues):
    """This function computes the Tqmean of a series of data, typically
       a 1 year time series of streamflow, after filtering out NoData
       values.  Tqmean is the fraction of time that daily streamflow
       exceeds mean streamflow for each year. Tqmean is based on the
       duration rather than the volume of streamflow. The routine returns
       the Tqmean value for the given data array."""

    # filtering out NoData Values
    Qvalues=Qvalues.dropna()
   
    # Total time
    T=len(Qvalues)
   
    # Tqmean calculateion
    Tqmean=(Qvalues>Qvalues.mean()).sum()/T
    
    return ( Tqmean )

def CalcRBindex(Qvalues):
    """This function computes the Richards-Baker Flashiness Index
       (R-B Index) of an array of values, typically a 1 year time
       series of streamflow, after filtering out the NoData values.
       The index is calculated by dividing the sum of the absolute
       values of day-to-day changes in daily discharge volumes
       (pathlength) by total discharge volumes for each year. The
       routine returns the RBindex value for the given data array."""

    # filtering out NoData Values
    Qvalues=Qvalues.dropna()
    
    # day-to-day streamflow change
    sfc=Qvalues.diff()
   
    # sum of absolute values
    Qs=abs(sfc).sum()
   
    # total streamflow
    Qt=Qvalues.sum()
   
    #R-B index calculation
    RBindex=Qs/Qt
    
    return ( RBindex )

def Calc7Q(Qvalues):
    """This function computes the seven day low flow of an array of 
       values, typically a 1 year time series of streamflow, after 
       filtering out the NoData values. The index is calculated by 
       computing a 7-day moving average for the annual dataset, and 
       picking the lowest average flow in any 7-day period during
       that year.  The routine returns the 7Q (7-day low flow) value
       for the given data array."""
      
    # filtering out NoData Values
    Qvalues=Qvalues.dropna()
   
    # 7 day period, pick the minimum values
    val7Q=Qvalues.rolling(window=7).mean().min
     
    return ( val7Q )

def CalcExceed3TimesMedian(Qvalues):
    """This function computes the number of days with flows greater 
       than 3 times the annual median flow. The index is calculated by 
       computing the median flow from the given dataset (or using the value
       provided) and then counting the number of days with flow greater than 
       3 times that value.   The routine returns the count of events greater 
       than 3 times the median annual flow value for the given data array."""

    # filtering out NoData Values
    Qvalues=Qvalues.dropna()
   
    # median*3, sum all values larger than median*3
    median3x=(Qvalues>3*Qvalues.median()).sum()
       
       
    return ( median3x )

def GetAnnualStatistics(DataDF):
    """This function calculates annual descriptive statistcs and metrics for 
    the given streamflow time series.  Values are retuned as a dataframe of
    annual values for each water year.  Water year, as defined by the USGS,
    starts on October 1."""
    
    # build similar table as the given output
    
    # define column names
    colNames=['site_no','Mean_Flow','Peak_Flow','Median','Coeff_Var','Skew','TQmean','R-B Index','7Q','3xMedian']
    
    # water year <- OCT 1st to next Sep 30th
    wateryear=DataDF.resample('AS-OCT')
    
    # build dataframe
    data=wateryear.mean()
    
    WYDataDF=pd.DataFrame(0,index=data.index,columns=colNames)
    
    # Write Table
    WYDataDF['site_no']=wateryear['site_no'].mean()
    
    WYDataDF['Mean_Flow']=wateryear['Discharge'].mean()
    
    WYDataDF['Peak_Flow']=wateryear['Discharge'].max()
    
    WYDataDF['Median']=wateryear['Discharge'].median()
    
    sd=wateryear['Discharge'].std()
    
    WYDataDF['Coeff_Var']=(sd/wateryear['Discharge'].mean())*100
    
    WYDataDF['Skew']=wateryear.apply({'Discharge':lambda x: stats.skew(x)},raw=True)
    
    WYDataDF['TQmean']=wateryear.apply({'Discharge': lambda x: CalcTqmean(x)})
    
    WYDataDF['R-B Index']=wateryear.apply({'Discharge': lambda x: CalcRBindex(x)})
    
    WYDataDF['7Q']=wateryear.apply({'Discharge': lambda x: Calc7Q(x)})
    
    WYDataDF['3xMedian']=wateryear.apply({'Discharge': lambda x: CalcExceed3TimesMedian(x)})
    
    return ( WYDataDF )

def GetMonthlyStatistics(DataDF):
    """This function calculates monthly descriptive statistics and metrics 
    for the given streamflow time series.  Values are returned as a dataframe
    of monthly values for each year."""

    # define column names
    colNames=['site_no','Mean_Flow','Coeff_Variantion','TQmean','R-B Index']
   
    # resample for monthly data
    monthly=DataDF.resample('M')
        
    # build dataframe
    data=monthly.mean()
        
    MoDataDF=pd.DataFrame(0,index=data.index,columns=colNames)
    
    # Write Table
    MoDataDF['site_no']=monthly['site_no'].mean()
    
    MoDataDF['Mean_Flow']=monthly['Discharge'].mean()
    
    sd=monthly['Discharge'].std()
    
    MoDataDF['Coeff_Variantion']=(sd/monthly['Discharge'].mean())*100
    
    MoDataDF['TQmean']=monthly.apply({'Discharge': lambda x: CalcTqmean(x)})
    
    MoDataDF['R-B Index']=monthly.apply({'Discharge': lambda x: CalcRBindex(x)})
        
    
    return ( MoDataDF )

def GetAnnualAverages(WYDataDF):
    """This function calculates annual average values for all statistics and
    metrics.  The routine returns an array of mean values for each metric
    in the original dataframe."""
    
    # mean for all values in WYDataDF
    AnnualAverages=WYDataDF.mean(axis=0)    
    
    return( AnnualAverages )

def GetMonthlyAverages(MoDataDF):
    """This function calculates annual average monthly values for all 
    statistics and metrics.  The routine returns an array of mean values 
    for each metric in the original dataframe."""
    
    # mean for all values in MoDataDf
    # MonthlyAverages=MoDataDF.mean(axis=0) ???
    
    # define column names
    colNames=['site_no','Mean_Flow','Coeff_Variantion','TQmean','R-B Index']
    
    # build Dataframe
    
    MonthlyAverages=pd.DataFrame(0,index=range(1,13),columns=colNames)
    
    
    for n in range(0,12):
        MonthlyAverages.iloc[n,0]=MoDataDF['site_no'][::12].mean()
    
    
    index=[(0,3),(1,4),(2,5),(3,6),(4,7),(5,8),(6,9),(7,10),(8,11),(9,0),(10,1),(11,2)]
    
    for (n,m) in index:
        MonthlyAverages.iloc[n,1]=MoDataDF['Mean_Flow'][m::12].mean()
    for (n,m) in index:
        MonthlyAverages.iloc[n,2]=MoDataDF['Coeff_Variantion'][m::12].mean()
    for (n,m) in index:
        MonthlyAverages.iloc[n,3]=MoDataDF['TQmean'][m::12].mean()
    for (n,m) in index:
        MonthlyAverages.iloc[n,4]=MoDataDF['R-B Index'][m::12].mean()

        
    
    return( MonthlyAverages )

# the following condition checks whether we are running as a script, in which 
# case run the test code, otherwise functions are being imported so do not.
# put the main routines from your code after this conditional check.

if __name__ == '__main__':

    # define filenames as a dictionary
    # NOTE - you could include more than jsut the filename in a dictionary, 
    #  such as full name of the river or gaging site, units, etc. that would
    #  be used later in the program, like when plotting the data.
    fileName = { "Wildcat": "WildcatCreek_Discharge_03335000_19540601-20200315.txt",
                 "Tippe": "TippecanoeRiver_Discharge_03331500_19431001-20200315.txt" }
    
    # define blank dictionaries (these will use the same keys as fileName)
    DataDF = {}
    MissingValues = {}
    WYDataDF = {}
    MoDataDF = {}
    AnnualAverages = {}
    MonthlyAverages = {}
    
    # process input datasets
    for file in fileName.keys():
        
        print( "\n", "="*50, "\n  Working on {} \n".format(file), "="*50, "\n" )
        
        DataDF[file], MissingValues[file] = ReadData(fileName[file])
        print( "-"*50, "\n\nRaw data for {}...\n\n".format(file), DataDF[file].describe(), "\n\nMissing values: {}\n\n".format(MissingValues[file]))
        
        # clip to consistent period
        DataDF[file], MissingValues[file] = ClipData( DataDF[file], '1969-10-01', '2019-09-30' )
        print( "-"*50, "\n\nSelected period data for {}...\n\n".format(file), DataDF[file].describe(), "\n\nMissing values: {}\n\n".format(MissingValues[file]))
        
        # calculate descriptive statistics for each water year
        WYDataDF[file] = GetAnnualStatistics(DataDF[file])
        
        # calcualte the annual average for each stistic or metric
        AnnualAverages[file] = GetAnnualAverages(WYDataDF[file])
        
        print("-"*50, "\n\nSummary of water year metrics...\n\n", WYDataDF[file].describe(), "\n\nAnnual water year averages...\n\n", AnnualAverages[file])

        # calculate descriptive statistics for each month
        MoDataDF[file] = GetMonthlyStatistics(DataDF[file])

        # calculate the annual averages for each statistics on a monthly basis
        MonthlyAverages[file] = GetMonthlyAverages(MoDataDF[file])
        
        print("-"*50, "\n\nSummary of monthly metrics...\n\n", MoDataDF[file].describe(), "\n\nAnnual Monthly Averages...\n\n", MonthlyAverages[file])


    # Build .csv files
    WC=WYDataDF['Wildcat']
    WC['Station']='Wildcat'
    
    TP=WYDataDF['Tippe']
    TP['Station']='Tippe'
    
    WC=WC.append(TP)
    
    WC.to_csv('Annual_Metrics.csv',sep=',',index=True)
    
    WC1=MoDataDF['Wildcat']
    WC1['Station']='Wildcat'
    
    TP1=MoDataDF['Tippe']
    TP1['Station']='Tippe'
    
    WC1=WC1.append(TP1)
    
    WC1.to_csv('Monthly_Metrics.csv',sep=',',index=True)
    
    #build .txt files
    WCave=AnnualAverages['Wildcat']
    WCave['Station']='Wildcat'
    
    TPave=AnnualAverages['Tippe']
    TPave['Station']='Tippe'
    
    WCave=WCave.append(TPave)
    
    WCave.to_csv('Average_Annual_Metrics.txt',sep='\t',index=True)
    
    WCave1=MonthlyAverages['Wildcat']
    WCave1['Station']='Wildcat'
    
    TPave1=MonthlyAverages['Tippe']
    TPave1['Station']='Tippe'
    
    WCave1=WCave1.append(TPave1)
    
    WCave1.to_csv('Average_Monthly_Metrics.txt',sep='\t',index=True)
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    