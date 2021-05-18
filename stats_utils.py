#------------------------------------------------------
# File: stats_utils
# contains functions for calculating percentiles and stats related to high impact weather
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
#    tasmax - a numpy array [nt,nlat,nlon] containing daily tasmax to test
#    tas90th - a numpy array [nlat,nlon] containing the 90th percentile of tas against which to test tasmax
#    nconsecutive_days - the number of consecutive days used to define a heatwave - often 3
# 
# returns:
#    heatwave - a numpy array [nt,nlat,nlon] set to 1 where there is a heatwave
#    length_heatwave - a numpy array [nt,nlat,nlon] where at t=start of each heatwave this gives the length of the heatwave in days
#    count_heatwave - a numpy array [nlat,nlon] that gives the number of heatwaves in each grid box
#------------------------------------------------------------------
# History:
#     created by Julia Crook based on code by Rory Fitzpatrick
#------------------------------------------------------------------
def get_heatwave(tasmax, tas90th, nconsecutive_days):
    shape=np.shape(tasmax)
    nt=shape[0]
    nlat=shape[1]
    nlon=shape[2]

    heatwave=np.zeros((nt,nlat,nlon), int)
    length_heatwave=np.zeros((nt,nlat,nlon), int)
    count_heatwave=np.zeros((nlat,nlon), int)
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
            print(len_heat)
            for i in range(nstart):
                if len_heat[i] >= nconsecutive_days:
                    heatwave[start_hot[i]:end_hot[i],y,x]=1
                    length_heatwave[start_hot[i], y,x]=len_heat[i]
                    count_heatwave[y,x]=count_heatwave[y,x]+nstart

    return heatwave, length_heatwave, count_heatwave

#------------------------------------------------------
# Code to calculate when there is a dry spell defined by number of consecutive days of accumulated preciptation below given threshold
#   pr is summed over nconsecutive_days and if the sum is < threshold these days are considered a dry spell
#   Note that pr read from model is usually rainrate per hour. This needs to be turned into a daily accumulation.
#
# inputs:
#    pr - a numpy array [nt,nlat,nlon] containing daily accumulated precipitation to test
#    threshold - the precipitation threshold to use
#    nconsecutive_days - the number of consecutive days over which to test the precipitation threshold
# 
# returns:
#    dryspell - a numpy array [nt,nlat,nlon] set to 1 where there is a dryspell
#    length_dryspell - a numpy array [nt,nlat,nlon] where at t=start of each dry spell this gives the length of the dry spell in days
#    count_dryspell - a numpy array [nlat,nlon] that gives the number of dryspells in each grid box
#------------------------------------------------------------------
# History:
#     created by Julia Crook based on code by Rory Fitzpatrick
#------------------------------------------------------------------
def get_dryspell(pr, threshold, nconsecutive_days):
    shape=np.shape(pr)
    nt=shape[0]
    nlat=shape[1]
    nlon=shape[2]

    dryspell=np.zeros((nt,nlat,nlon), int)
    length_dryspell=np.zeros((nt,nlat,nlon), int)
    count_dryspell=np.zeros((nlat,nlon), int)
    
    dry=np.zeros((nt+2,nlat,nlon)) # add an element at beginning and end compared to pr
    for t in range(0,nt-nconsecutive_days):
        this_sum=np.sum(pr[t:t+nconsecutive_days,:,:], axis=0)
        ix=np.where(this_sum < float(threshold))
        iys=ix[0]
        ixs=ix[1]
        nx=len(ixs)
        ny=len(iys)
        for y in range(ny):
            for x in range(nx):
                dry[t+1:t+nconsecutive_days+1,iys[y],ixs[x]] = 1
                dryspell[t:t+nconsecutive_days,iys[y],ixs[x]]=1

    diffs=np.diff(dry, axis=0) # this is 1 where it becomes dry and -1 where it becomes wet and 0 where it stays the same
    # get indices where changes occur
    for y in range(nlat):
        for x in range(nlon):
            start_dry=np.where(diffs[:,y,x]>0)[0]
            end_dry=np.where(diffs[:,y,x]<0)[0]
            nstart=len(start_dry)
            nend=len(end_dry)
            length_dryspell[start_dry, y,x]=end_dry-start_dry
            count_dryspell[y,x]=count_dryspell[y,x]+nstart

    return dryspell, length_dryspell, count_dryspell

#------------------------------------------------------
# Code to calculate the monsoon onset
#   this is defined as having >= day_one_threshold on day t and >= two_day_theshold over day t and t+1 and
#   no dry spells (defined by nconsective_days_dryspell and dry_threshold) starting in the next ndryspell_days
#
# inputs:
#    pr - a numpy array [nt,nlat,nlon] containing daily precipitation in mm/day
#    days - a numpy array [nt] of the day of the year corresponding to pr data
#    day_one_threshold - defaults to 1.0 mm
#    two_day_theshold - defaults to 20.0 mm
#    dry_theshold - defaults to 5.0 mm
#    nconsecutive_days_dryspell - defaults to 7 days
#    ndryspell_days - defaults to 15 days
# 
# returns:
#    onsets - a numpy array [nlat,nlon] with day of the year when onset occured
#------------------------------------------------------------------
# History:
#     created by Julia Crook based on code by Rory Fitzpatrick
#------------------------------------------------------------------
def get_onsets(pr, days, day_one_threshold=1.0,two_day_theshold=20.0, dry_threshold=5.0, nconsecutive_days_dryspell=7, ndryspell_days=15):
    shape=np.shape(pr)
    nt=shape[0]
    nlat=shape[1]
    nlon=shape[2]

    ndays_to_test=ndryspell_days+nconsecutive_days_dryspell   
    onsets=np.zeros((nlat,nlon), int)
    
    for y in range(nlat):
        for x in range(nlon):
            for t in range(nt-ndays_to_test):
                if (pr[t,y,x] >= day_one_threshold and np.sum(pr[t:t+2,y,x]) >= two_day_theshold):
                    # this x and y had heavy enough rain
                    # see if rainfall summed over nconsecutive_days_dryspell days is below dry_threshold
                    # in the next ndryspell_days days
                    low_rain=False
                    for t1 in range(t+2,t+ndryspell_days):
                        if np.sum(pr[t1:t1+nconsecutive_days_dryspell,y,x]) < dry_threshold:
                            low_rain=True
                            break
                    if low_rain == False:
                        # we have found the onset
                        onsets[y,x] = days[t]
                        break
    return onsets

if __name__=='__main__':
    main()
