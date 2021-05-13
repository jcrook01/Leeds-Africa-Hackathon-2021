#----------------------------------------------------------
# Code to create a string for the region eg 20W20E_10S10N
#
# inputs:
#    lat_range - [minlat, maxlat]
#    lon_range - [minlon, maxlon]
#    delimiter - the character that separates lons and lats, defaults to '_'
# returns
#    lonlat_str
#-----------------------------------------------------------
# History:
#   created by Julia Crook
#-----------------------------------------------------------

def get_lat_str(lat):
    if lat<0:
        lat_str='{l:02d}S'.format(l=abs(lat))
    else:
        lat_str='{l:02d}N'.format(l=lat)
    return lat_str
def get_lon_str(lon):
    if lon<0:
        lon_str='{l:02d}W'.format(l=abs(lon))
    else:
        lon_str='{l:02d}E'.format(l=lon)
    return lon_str

def get_lon_lat_str(lat_range, lon_range, delimiter='_'):
    minlat_str=get_lat_str(lat_range[0])
    maxlat_str=get_lat_str(lat_range[1])
    minlon_str=get_lon_str(lon_range[0])
    maxlon_str=get_lon_str(lon_range[1])
    lonlat_str=minlon_str+maxlon_str+delimiter+minlat_str+maxlat_str
    return lonlat_str
        
    
if __name__=='__main__':
    main()
