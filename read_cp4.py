#------------------------------------------------------
# Code to read CP4 data for present or future from the CEDA archive
# inputs:
#     explicit: if True this reads 4km  explicit data, otherwise reads the parameterised 25km data
#     temporal: the string '1hr' or 'mon'
#     variable: the variable to read eg tas
#     start_year, start_month, end_year and end_month define the time period for which data is returned
#     present data is for 1997/03 to 2007/02
#     future data is for 2095/03 to 2105/02
# returns the iris cube with requested data
#------------------------------------------------------------------
# History:
#     created by Julia Crook
#------------------------------------------------------------------

import warnings
import iris
from iris.experimental.equalise_cubes import equalise_attributes

def read_cp4(explicit, temporal, variable, start_year, start_month, end_year, end_month):

    if explicit:
        explicit_str='explicit-4km'
    else:
        explicit_str='param-25km'
    if start_year <=2007:
        present_future='present'
    else:
        present_future='future'
        
    # match variable names with longer names used in directory structure
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
    basedir='/badc/impala/data/'+explicit_str+'/'+present_future+'/'+temporal+'/'+var_directory[variable]+'/'
    all_cubes=iris.cube.CubeList()
    varConstraint=iris.Constraint(cube_func=(lambda c: c.var_name == variable))
    print('reading {res} {y:04d}/{m:02d} to {y2:04d}/{m2:02d}'.format(res=explicit_str,y=start_year,m=start_month,y2=end_year,m2=end_month))
    for y in range(start_year,end_year+1):
        if temporal=='mon':
            ncdir=basedir
            if y==start_year:
                first_month=start_month
            else:
                first_month=1
            if y==end_year:
                last_month=end_month
            else:
                last_month=nmonths_per_year
            first_date_str='{y:04d}{m:02d}-'.format(y=y,m=first_month)
            last_date_str='{y:04d}{m:02d}'.format(y=y,m=last_month)
            filename=variable+'_'+explicit_str+'_'+present_future+'_'+first_date_str+last_date_str+'.nc'
            #print('opening', filename)
            try:
                this_cube = iris.load_cube(ncdir+filename,varConstraint)
            except OSError as err:
                print(filename)
                raise err
            all_cubes.append(this_cube)
        else:
            for m in range(1,nmonths_per_year+1):
                if y==start_year and m<start_month:
                    continue
                if y==end_year and m>end_month:
                    break
                ncdir=basedir+'{y:04d}/{m:02d}/'.format(y=y, m=m)
                for d in range(ndays_per_month):
                    filename=variable+'_'+explicit_str+'_'+present_future+'_{y:04d}{m:02d}{d:02d}.nc'.format(y=y,m=m,d=d+1)
                    #print('opening', filename)
                    try:
                        this_cube = iris.load_cube(ncdir+filename,varConstraint)
                    except OSError as err:
                        print(filename)
                        raise err
                    all_cubes.append(this_cube)

    iris.util.unify_time_units(all_cubes)
    equalise_attributes(all_cubes)
    cubes = all_cubes.concatenate()

    return cubes[0]

if __name__=='__main__':
    main()
