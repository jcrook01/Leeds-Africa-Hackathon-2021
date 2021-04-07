#-----------------------------------------------------------------------------------------
# code to read any CMIP6 data
# inputs:
#   are strings that define the data (and directory to find it in) - see CMIP6 documentation online
#   CMIP6 data are split into different eras defined by time_range
# returns the iris cube containing the data requested
#-----------------------------------------------------------------------------------------
import warnings
import iris

def read_cmip6(activity_id, institute, model, experiment, variant, table_id, variable, grid, version, time_range):

    ncdir='/badc/cmip6/data/CMIP6/'+activity_id+'/'+institute+'/'+model+'/'+experiment+'/'+variant+'/'+table_id+'/'+variable+'/'+grid+'/'+version+'/'
    filename=variable+'_'+table_id+'_'+model+'_'+experiment+'_'+variant+'_'+grid+'_'+time_range+'.nc'
    varConstraint=iris.Constraint(cube_func=(lambda c: c.var_name == variable))
    #print('opening', filename)
    try:
        cube = iris.load_cube(ncdir+filename,varConstraint)

    except OSError as err:
        print(filename)
        raise err
    return cube

if __name__=='__main__':
    main()
