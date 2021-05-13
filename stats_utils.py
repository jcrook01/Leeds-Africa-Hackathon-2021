#------------------------------------------------------
# File: stats_utils
# contains functions for calculating percentiles
#------------------------------------------------------------------


#------------------------------------------------------------------
# Code to calculate nth percentile of the data provided and store in netcdf for each month
#
# inputs:
#    data - an iris cube of the data for the required period and region of interest
#    percentile - the percentile required e.g. 50
#    outfile - where to write the netcdf output files - one is written for each month with month number appended to outfile
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
# Code to calculate where the future climate sits within the current climate for each month
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

if __name__=='__main__':
    main()
