#------------------------------------------------------------------
# Code to calculate 50th percentile of the CP4 data for each month
#     RUN THIS OUTSIDE THE NOTEBOOK
#------------------------------------------------------------------
# History:
#     created by Julia Crook
#------------------------------------------------------------------
from get_lon_lat_str import *
from stats_utils import *
from iris.experimental.equalise_cubes import equalise_attributes
import os.path

#------------------------------------------------------------------
# get daily data for requested month for all years
# Inputs:
#    explicit: if True use explicit 4km data, otherwise use the parameterised 25km data
#    present: if True use present data, otherwise use future data
#    lonlat_str: the region string used to find daily data 
#    varConstraint: irisConstraint used to read the data
#    varname: the more common varname used in directory names, eg tasmax
#------------------------------------------------------------------
def get_cp4_daily_data_for_month(explicit, present, lonlat_str, varConstraint, varname, month):
    if explicit:
        explicit_str='explicit-4km'
    else:
        explicit_str='param-25km'
    if present:
        present_future='present'
        start_year =1997
        start_month=3
        end_year=2007
        end_month=2
    else:
        present_future='future'
        start_year =2095
        start_month=3
        end_year=2105
        end_month=2

    ncdir='/gws/pw/j05/cop26_hackathons/leeds/CP4/'+explicit_str+'/'+present_future+'/'+varname+'/'
    filebase=explicit_str+'_daily_'+varname+'_'
    data_cube_list=iris.cube.CubeList()
    for y in range(start_year,end_year+1):
        if y==start_year and month<start_month:
            continue
        if y==end_year and month>end_month:
            break
        filename=filebase+'{y:04d}{m:02d}_'.format(y=y,m=month)+lonlat_str+'.nc'
        #print('reading', ncdir+filename)
        try:
            this_cube = iris.load_cube(ncdir+filename, varConstraint)
        except OSError as err:
            print(filename)
            raise err
        data_cube_list.append(this_cube)

    iris.util.unify_time_units(data_cube_list)
    equalise_attributes(data_cube_list)
    conc_cubes = data_cube_list.concatenate()
    return conc_cubes[0]

#------------------------------------------------------------------
# for each month, calculate nth percentile and save in netcdf
# Inputs:
#    explicit: if True use explicit 4km data, otherwise use the parameterised 25km data
#    present: if True use present data, otherwise use future data
#    lonlat_str: the region string used to find daily data and to use in output files
#    varConstraint: irisConstraint used to read the data
#    varname: the more common varname used in directory names, eg tasmax
#    percentile: the percentile to calculate
#------------------------------------------------------------------
def get_cp4_nth_percentile(explicit, present, lonlat_str, varConstraint, varname, percentile):

    if explicit:
        explicit_str='explicit-4km'
    else:
        explicit_str='param-25km'
    if present:
        present_future='present'
    else:
        present_future='future'

    nmonths_per_year=12
    ncdir='/gws/pw/j05/cop26_hackathons/leeds/CP4/'+explicit_str+'/'+present_future+'/'+varname+'/'
    filebase=explicit_str+'_daily_'+varname+'_'
    for m in range(1,nmonths_per_year+1):
        cp4_data=get_cp4_daily_data_for_month(explicit, present, lonlat_str, varConstraint, varname, m)
        outfile=ncdir+filebase+'{p:0d}th_percentile_{m:02d}_'.format(p=percentile,m=m)+lonlat_str+'.nc'
        if os.path.isfile(outfile):
            print(outfile, 'exists')
        else:
            create_data_nth_percentile(cp4_data, percentile, outfile)

#------------------------------------------------------------------
#------------------------------------------------------------------
def main():
    min_lon=-20
    max_lon=20
    min_lat=0
    max_lat=25
    lat_range=[min_lat,max_lat]
    lon_range=[min_lon,max_lon]
    lonlat_str=get_lon_lat_str(lat_range, lon_range)
    nmonths_per_year=12

    explicit=True
    explicit_str='explicit-4km'
    #-----------------
    #  Do for tasmax and pr
    #-----------------
    stash_codes=['m01s03i236','m01s04i203'] # daily data needs to be read with stash code
    varnames=['tasmax','pr']
    nvars=len(varnames)
    nvars=1
    
    for n in range(nvars):
        varConstraint = iris.AttributeConstraint(STASH=stash_codes[n])
        #----------------------------------------------------------------------------
        # create 50th percentile of future  
        #----------------------------------------------------------------------------
        present=False
        get_cp4_nth_percentile(explicit, present, lonlat_str, varConstraint, varnames[n], 50)

        #----------------------------------------------------------------------------
        # create 50th percentile of current 
        #----------------------------------------------------------------------------
        present=True
        get_cp4_nth_percentile(explicit, present, lonlat_str, varConstraint, varnames[n], 50)
    
        #----------------------------------------------------------------------------
        # create where 50th percentile of future sits within historical 
        #----------------------------------------------------------------------------
        outdir='/gws/pw/j05/cop26_hackathons/leeds/CP4/'+explicit_str+'/future/'+varnames[n]+'/'
        outfile_fc_vs_cc=outdir+explicit_str+'_daily_'+varnames[n]+'_as_cc_percentile_'
        outfile_fc=outdir+explicit_str+'_daily_'+varnames[n]+'_50th_percentile_'
        for m in range(1,nmonths_per_year+1):
            this_file_fc=outfile_fc+'{m:02d}_'.format(m=m)+lonlat_str+'.nc'
            this_cc_data=get_cp4_daily_data_for_month(explicit, present, lonlat_str, varConstraint, varnames[n], m)
            this_outfile=outfile_fc_vs_cc+'{m:02d}_'.format(m=m)+lonlat_str+'.nc'
            if os.path.isfile(this_outfile):
                print(this_outfile, 'exists')
            else:
                create_future_data_as_percentile_of_current(this_file_fc, varConstraint, this_cc_data, this_outfile)


if __name__=='__main__':
    main()