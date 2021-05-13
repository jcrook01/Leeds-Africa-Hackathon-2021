#------------------------------------------------------
# Code to plot 50th percentile of daily max temperature in requested month from requested CMIP6 institute, model,
# and variant for requested region.
# Plots the fc_experiment (future scenario) for fc_version over fc_year_range, the cc_experiment (historical) for
# cc_version over cc_year_range, the difference between the two and the fc_experiment median as a percentile of historical
#
# inputs:
#    institute, model, fc_experiment, cc_experiment, variant, fc_version, cc_version - define the model and scenarios
#    lat_range, lon_range - define the region
#    fc_year_range, cc_year_range - define the years over which the percentiles were calculated
#    month - month to plot (1-12)
#    levels_diff - the levels used to plot the difference between the two, e.g. np.arange(4., 9.5, 0.5)
#-----------------------------------------------------------
# History:
#   created by Julia Crook based on code by Rory Fitzpatrick
#-----------------------------------------------------------
import warnings
import numpy as np
import pdb
import matplotlib.pyplot as plt
import mpl_toolkits.basemap as bm
import iris
from get_lon_lat_str import *

def plot_cmip6_tasmax_50th_percentile(institute, model, fc_experiment, cc_experiment, variant, fc_version, cc_version, lat_range, lon_range, fc_year_range, cc_year_range, month, levels_diff):

    outdir_base='/gws/pw/j05/cop26_hackathons/leeds/CMIP6/'+institute+'/'+model+'/'
    outdir_fc=outdir_base+fc_experiment+'/'+variant+'/'+fc_version+'/tasmax/'
    outdir_cc=outdir_base+cc_experiment+'/'+variant+'/'+cc_version+'/tasmax/'
    lonlat_str=get_lon_lat_str(lat_range, lon_range)
    filebase_fc=outdir_fc+'tasmax_50th_percentile_{y1}-{y2}_'.format(y1=fc_year_range[0], y2=fc_year_range[1])
    filebase_cc=outdir_cc+'tasmax_50th_percentile_{y1}-{y2}_'.format(y1=cc_year_range[0], y2=cc_year_range[1])
    filebase_fc_vs_cc=outfile_fc=outdir_fc+'tasmax_{y1}-{y2}_as_cc_percentile_{y3}-{y4}_'.format(y1=fc_year_range[0], y2=fc_year_range[1], y3=cc_year_range[0], y4=cc_year_range[1])
    outfile_base='plots/'+model+'_'+fc_experiment+'_tasmax_50th_percentile_{y1}-{y2}_'.format(y1=fc_year_range[0], y2=fc_year_range[1])
    
    KtoC=273.14

    mnthname = ['January','February','March','April','May','June','July','August','September','October','November','December']
    this_mnthname=mnthname[month-1]
    mnth='{m:02d}'.format(m=month)
    this_ncfile_fc=filebase_fc+mnth+'_'+lonlat_str+'.nc'
    this_ncfile_cc=filebase_cc+mnth+'_'+lonlat_str+'.nc'
    this_ncfile_fc_vs_cc=filebase_fc_vs_cc+mnth+'_'+lonlat_str+'.nc'
    this_outfile=outfile_base+mnth+'_'+lonlat_str+'.png'
    fc_tasmax = iris.load_cube(this_ncfile_fc)
    lons = fc_tasmax.coord('longitude').points
    lats = fc_tasmax.coord('latitude').points
    cc_tasmax = iris.load_cube(this_ncfile_cc)
    fc_as_cc_percent = iris.load_cube(this_ncfile_fc_vs_cc)
    
    plt.figure(figsize = (8,6))
    plt.clf()
    cmap = plt.get_cmap('nipy_spectral')
    levels_cp = np.arange(13,55,2)
    plt.subplot(2,2,1)
    m = bm.Basemap(projection='cyl',llcrnrlat = lats[0], urcrnrlat = lats[-1], llcrnrlon = lons[0], urcrnrlon = lons[-1],  resolution = 'l')
    m.drawcountries(linewidth = 1)
    m.drawcoastlines(linewidth = 2)
    cd = plt.contourf(lons, lats, cc_tasmax.data-KtoC, levels_cp, extend = 'min',cmap = cmap)
    cb = plt.colorbar(cd, orientation = 'vertical')
    cb.set_label('($^\circ$C)', fontsize=10)
    plt.title('(a) CC', loc='left', fontsize = 12)
    plt.subplot(2,2,2)
    m = bm.Basemap(projection='cyl',llcrnrlat = lats[0], urcrnrlat = lats[-1], llcrnrlon = lons[0], urcrnrlon = lons[-1],  resolution = 'l')
    m.drawcountries(linewidth = 1)
    m.drawcoastlines(linewidth = 2)
    cd = plt.contourf(lons, lats, fc_tasmax.data-KtoC, levels_cp,extend = 'min', cmap = cmap)
    cb = plt.colorbar(cd, orientation = 'vertical')
    cb.set_label('($^\circ$C)', fontsize=10)
    plt.title('(b) FC', loc='left', fontsize = 12)

    plt.subplot(2,2,3)
    diff_cp = fc_tasmax.data - cc_tasmax.data
    m = bm.Basemap(projection='cyl',llcrnrlat = lats[0], urcrnrlat = lats[-1], llcrnrlon = lons[0], urcrnrlon = lons[-1],  resolution = 'l')
    m.drawcountries(linewidth = 1)
    m.drawcoastlines(linewidth = 2)
    cd = plt.contourf(lons, lats, diff_cp, levels_diff,extend = 'both', cmap = cmap)
    cb = plt.colorbar(cd, orientation = 'vertical')
    cb.set_label('($^\circ$C)', fontsize=10)
    plt.title('(c) FC - CC', loc='left', fontsize = 12)

    plt.subplot(2,2,4)
    # read the future climate 50th percentile relative to CC
    pallette = plt.get_cmap('Set1')
    pallette.set_over('w')
    pallette.set_under('b')
    levels_percentile = [50,75,80,85,90,95,99.9]
    m = bm.Basemap(projection='cyl',llcrnrlat = lats[0], urcrnrlat = lats[-1], llcrnrlon = lons[0], urcrnrlon = lons[-1],  resolution = 'l')
    m.drawcountries(linewidth = 1)
    m.drawcoastlines(linewidth = 2)
    cd = plt.contourf(lons, lats, fc_as_cc_percent.data, levels_percentile,extend = 'both', cmap = pallette)
    cb = plt.colorbar(cd, orientation = 'vertical')
    cb.set_label('percentile position')
    plt.title('(d) FC 50th %ile position', loc='left', fontsize = 12)
    
    year_str=' {y1}-{y2} vs {y3}-{y4}'.format(y1=fc_year_range[0], y2=fc_year_range[1], y3=cc_year_range[0], y4=cc_year_range[1])
    plt.suptitle(model+' '+str(mnthname[month-1])+year_str)
    plt.subplots_adjust(wspace=0.2, hspace=0.05)
    plt.savefig(this_outfile, bbox_inches = 'tight')
    plt.show()
    plt.close()

if __name__=='__main__':
    main()
