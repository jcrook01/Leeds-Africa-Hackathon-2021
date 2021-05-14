#------------------------------------------------------
# File: stats_utils
# contains functions for calculating percentiles
#------------------------------------------------------------------


#------------------------------------------------------------------
# Code to calculate nth percentile of the data provided and store in netcdf
#
# inputs:
#    data - an iris cube of the data for the required period and region of interest
#    percentile - the percentile required e.g. 50
#    outfile - where to write the netcdf output files
#
#------------------------------------------------------------------
# History:
#    created by Julia Crook based on code written by Rory Fitzpatrick for Fitzpatrick et al. Climatic Change 2020
#------------------------------------------------------------------
import warnings
import iris

def create_data_nth_percentile(data, percentile, outfile):

    this_percentile = data.collapsed('time', iris.analysis.PERCENTILE, percent = percentile)
    print('saving ', outfile)
    iris.save(this_percentile, outfile)
    
#------------------------------------------------------
# Code to calculate where the future climate sits within the current climate
#
# inputs:
#    file_fc - this is the filename for the eg 50th percentile netcdf for future climate
#    varConstraint - the irisConstraint to specify variable we are reading
#    cc_data - an iris cube of the current climate daily data
#    outfile - where to write the netcdf output file
#
#------------------------------------------------------------------
# History:
#     created by Julia Crook based on code by Rory Fitzpatrick for Fitzpatrick et al. Climatic Change 2020
#------------------------------------------------------------------
import numpy as np
import iris
import scipy.stats as stat

def create_future_data_as_percentile_of_current(file_fc, varConstraint, cc_data, outfile):

    fc_data = iris.load_cube(file_fc, varConstraint)
    nlat=fc_data.shape[0]
    nlon=fc_data.shape[1]
    percents = np.zeros((nlat, nlon),float)
    for y in range(nlat):
        for x in range(nlon):
            percents[y,x] = stat.percentileofscore(cc_data.data[:,y,x],fc_data[y,x].data,kind="rank")
    percents_cube=iris.cube.Cube(percents, var_name='percentile_of_cc', units='%', dim_coords_and_dims=[(cc_data.coord('latitude'), 0),(cc_data.coord('longitude'), 1)])
    print('saving ', outfile)
    iris.save(percents_cube, outfile)
import numpy as np


#------------------------------------------------------
# Code to calculate when there is a heatwave defined by number of consecutive days of temperature above the 90th percentile
#
# inputs:
#    tasmax - a numpy array [nt,nlat,nlon] containing tasmax to test
#    tas90th - a numpy array [nlat,nlon] containing the 90th percentile of tas against which to test tasmax
#    nconsecutive_days - the number of consecutive days used to define a heatwave - often 3
# 
# returns:
#    heatwave - a numpy array [nt,nlat,nlon] set to 1 where there is a heatwave
#------------------------------------------------------------------
# History:
#     created by Julia Crook based on code by Rory Fitzpatrick
#------------------------------------------------------------------
def get_heatwave(tasmax, tas90th, nconsecutive_days):
    shape=np.shape(tasmax)
    nt=shape[0]
    nlat=shape[1]
    nlon=shape[2]

    heatwave=np.zeros((nt,nlat,nlon))
    for y in range(nlat):
        for x in range(nlon):
            hot=np.zeros(nt+2) # add an element at beginning and end compared to tasmax
            # where is the tasmax greater than or equal to the 90th percentile tas
            hotix=np.where(tasmax[:,y,x] >= tas90th[y,x])
            hot[hotix[0]+1]=1
            diffs=np.diff(hot) # this is 1 where it becomes hot and -1 where it becomes cold and 0 where it stays the same
            # get indices where changes occur
            start_hot=np.where(diffs>0)[0]
            end_hot=np.where(diffs<0)[0]
            nstart=len(start_hot)
            nend=len(end_hot)
            len_heat=end_hot-start_hot
            for i in range(nstart):
                if len_heat[i] >= nconsecutive_days:
                    heatwave[start_hot[i]:end_hot[i],y,x]=1

    return heatwave

if __name__=='__main__':
    main()
