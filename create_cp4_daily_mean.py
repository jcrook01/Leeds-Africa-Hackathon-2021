#------------------------------------------------------------------
# Code to calculate daily mean from hourly CP4 data on the BADC archive
#    ONLY RUN THIS ON LOTUS BATCH PROCESSING!!
# Inputs:
#    explicit: if True use explicit 4km data, otherwise use the parameterised 25km data
#    present: if True use present data, otherwise use future data
#    lat_range - [min_lat,max_lat] )   defines the region over which to calculate data
#    lon_range - [min_lon,max_lon] )
#------------------------------------------------------------------
# History:
#     created by Julia Crook
#------------------------------------------------------------------
import iris
from iris.experimental.equalise_cubes import equalise_attributes
from get_lon_lat_str import *

def create_cp4_daily_mean(explicit, present, varname, lat_range, lon_range):
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
        
    intersection = {'latitude': lat_range, 'longitude': lon_range}
    lonlat_str=get_lon_lat_str(lat_range, lon_range)

    outdir='/gws/pw/j05/cop26_hackathons/leeds/CP4/'+explicit_str+'/'+present_future+'/'+varname+'/'
    filebase=explicit_str+'_daily_'+varname+'_'
    var_directory=dict()
    var_directory['psl']='mean_sea_level_pressure'
    var_directory['prsn']='snowfall'
    var_directory['huss']='near_surface_air_specific_humidity'
    var_directory['hfls']='surface_latent_heat_flux'
    var_directory['tas']='near_surface_air_temperature'
    var_directory['ps']='surface_pressure'
    var_directory['rlut']='outgoing_longwave_radiation'
    var_directory['hfss']='surface_sensible_heat_flux'
    var_directory['pr']='precipitation'

    nmonths_per_year=12
    ndays_per_month=30
    basedir='/badc/impala/data/'+explicit_str+'/'+present_future+'/'+temporal+'/'+var_directory[varname]+'/'
    varConstraint=iris.Constraint(cube_func=(lambda c: c.var_name == varname))
    if explicit:
        # open a 25km file to regrid to
        nc25dir='/badc/impala/data/param-25km/present/1hr/'+var_directory[varname]+'/{y:04d}/{m:02d}/'.format(y=start_year, m=start_month)
        filename=varname+'_param-25km_present_{y:04d}{m:02d}{d:02d}.nc'.format(y=start_year,m=start_month,d=1)
        try:
            cube_25km = iris.load_cube(nc25dir+filename,varConstraint)
        except OSError as err:
            print(filename)
            raise err
        # take region of interest
        cube_25km=cube_25km.intersection(**intersection)
        
    for y in range(start_year,end_year+1):
        for m in range(1,nmonths_per_year+1):
            if y==start_year and month<start_month:
                continue
            if y==end_year and month>end_month:
                break
            ncdir=basedir+'{y:04d}/{m:02d}/'.format(y=y, m=m)
            data_mean_cube_list=iris.cube.CubeList()
            for d in range(ndays_per_month):
                filename=variable+'_'+explicit_str+'_'+present_future+'_{y:04d}{m:02d}{d:02d}.nc'.format(y=y,m=m,d=d+1)
                #print('opening', filename)
                try:
                    this_cube = iris.load_cube(ncdir+filename,varConstraint)
                except OSError as err:
                    print(filename)
                    raise err
                # take region of interest
                this_cube=this_cube.intersection(**intersection)
                if explicit:
                    # regrid to 25km
                    this_cube = this_cube.regrid(cube_25km, iris.analysis.Linear())
                # take the mean for this day
                this_cube = this_cube.collapsed('time', iris.analysis.MEAN)
                data_mean_cube_list.append(this_cube)

            iris.util.unify_time_units(data_mean_cube_list)
            equalise_attributes(data_mean_cube_list)
            data_mean_cubes = data_mean_cube_list.merge()
            out_filename=filebase+'{y:04d}{m:02d}_'.format(y=y,m=m)+lonlat_str+'.nc'
            iris.save(data_mean_cubes, outfile)
            
            
if __name__=='__main__':
    main()