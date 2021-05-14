#------------------------------------------------------------------
# Code to calculate 50th percentile of CMIP6 data for each month
#    this is done for HadGEM3-GC31-LL historical and ssp585, 
#    for the specified region and years
#    the 50th percentile future as percentile of historical is also calculated
#
#    RUN THIS OUTSIDE THE NOTEBOOK
#------------------------------------------------------------------
# History:
#     created by Julia Crook
#------------------------------------------------------------------
import iris
import iris.coord_categorisation
from read_cmip6 import *
from stats_utils import *
from get_lon_lat_str import *
import os.path

outdir_base='/gws/pw/j05/cop26_hackathons/leeds/CMIP6/'

# define Africa region
lon_range=[-20,55]
lat_range=[-30,30]
intersection = {'latitude': lat_range, 'longitude': lon_range}
lonlat_str=get_lon_lat_str(lat_range, lon_range)
nmonths_per_year=12

#----------------------------------------------------------------------
# create 50th percentile for future scenario tasmax for HadGEM3-GC31-LL
#----------------------------------------------------------------------
institute='MOHC'
model='HadGEM3-GC31-LL'
experiment='ssp585'
variant='r1i1p1f3'
version='v20200114'
start_year=2050
end_year=2079
varname='tasmax'
# read ssp585 tasmax from 2050 to 2079 for Africa
tasmax_fc=read_cmip6('ScenarioMIP',institute,model,experiment,variant,'day',varname,'gn',version,'20500101-21001230')
iris.coord_categorisation.add_year(tasmax_fc,'time',name='year')
time_constraint=iris.Constraint(year = lambda cell: start_year <= cell <= end_year)
tasmax_fc=tasmax_fc.intersection(**intersection)
tasmax_fc=tasmax_fc.extract(time_constraint)

outdir_fc=outdir_base+institute+'/'+model+'/'+experiment+'/'+variant+'/'+version+'/'+varname+'/'
outfile_fc=outdir_fc+'tasmax_50th_percentile_{y1}-{y2}_'.format(y1=start_year, y2=end_year)
iris.coord_categorisation.add_month_number(tasmax_fc,'time',name='month_number')
for m in range(1,nmonths_per_year+1):
    this_tasmax=tasmax_fc.extract(iris.Constraint(month_number = lambda cell: cell == int(m)))
    this_outfile=outfile_fc+'{m:02d}_'.format(m=m)+lonlat_str+'.nc'
    if os.path.isfile(this_outfile):
        print(this_outfile, 'exists')
    else:
        create_data_nth_percentile(this_tasmax, 50, this_outfile)

#----------------------------------------------------------------------
# create 50th percentile for historical scenario tasmax for HadGEM3-GC31-LL
#----------------------------------------------------------------------
experiment='historical'
version='v20190624'
start_year2=1985
end_year2=2014
tasmax_cc=read_cmip6('CMIP',institute,model,experiment,variant,'day',varname,'gn',version,'19500101-20141230')
# read historical tasmax from 1985-2014 for Africa 
iris.coord_categorisation.add_year(tasmax_cc,'time',name='year')
time_constraint=iris.Constraint(year = lambda cell: start_year2 <= cell <= end_year2)
tasmax_cc=tasmax_cc.intersection(**intersection)
tasmax_cc=tasmax_cc.extract(time_constraint)
outdir_cc=outdir_base+institute+'/'+model+'/'+experiment+'/'+variant+'/'+version+'/'+varname+'/'
outfile_cc=outdir_cc+'tasmax_50th_percentile_{y1}-{y2}_'.format(y1=start_year2, y2=end_year2)
iris.coord_categorisation.add_month_number(tasmax_cc,'time',name='month_number')
for m in range(1,nmonths_per_year+1):
    this_tasmax=tasmax_cc.extract(iris.Constraint(month_number = lambda cell: cell == int(m)))
    this_outfile=outfile_cc+'{m:02d}_'.format(m=m)+lonlat_str+'.nc'
    if os.path.isfile(this_outfile)==False:
        print(this_outfile, exists)
    else:
        create_data_nth_percentile(this_tasmax, 50, this_outfile)

#----------------------------------------------------------------------------
# create where 50th percentile of future tasmax sits within historical tasmax
#----------------------------------------------------------------------------
outfile_fc_vs_cc=outdir_fc+'tasmax_{y1}-{y2}_as_cc_percentile_{y3}-{y4}_'.format(y1=start_year, y2=end_year, y3=start_year2, y4=end_year2)
for m in range(1,nmonths_per_year+1):
    this_file_fc=outfile_fc+'{m:02d}_.nc'.format(m=m)+lonlat_str
    this_cc_data=tasmax_cc.extract(iris.Constraint(month_number = lambda cell: cell == int(m)))
    this_outfile=outfile_fc_vs_cc+'{m:02d}_'.format(m=m)+lonlat_str+'.nc'
    varConstraint=iris.Constraint(cube_func=(lambda c: c.var_name == varname))
    if os.path.isfile(this_outfile):
        print(this_outfile, 'exists')
    else:
        create_future_data_as_percentile_of_current(this_file_fc, varConstraint, this_cc_data, this_outfile)