#------------#
#-- author --#
#------------#
# Jason Schatz
# NM Dept of Health
# Created: 01/10/17
# Last modified: 01/10/17
# Python v2.7.12


#-----------------#
#-- description --#
#-----------------#
## Basic commands for reading, processing, and writing netcdfs in Python.
## Netcdfs are basically arrays with attribute information included. So 
## once they are open, they can be processed like arrays. I have included 
## some basic functions for data query, but to build custom data queries, 
## see the numpy documentation for array structure and commands.


#----------------------#
#-- import libraries --#
#----------------------#
import gdal
import numpy as np
import netCDF4
from netCDF4 import Dataset
import osr
import pandas as pd


#----------------------#
#-- define functions --#
#----------------------#
#### finds index of nearest value in array (sub-function of other functions)
## @param coordinate:  individual coordinate
## @param coordinate_matrix:  matrix of coordinates to search for nearest value
def find_nearest(coordinate, coordinate_matrix):
    idx = (np.abs(coordinate_matrix - coordinate)).argmin()
    return idx

#### returns time series of temperatures from a single specified set of coordinates
## @param latitude:  latitude of interest
## @param longitude:  longitude of interest
def point_slice(latitude, longitude):
    lon1 = find_nearest(latitude, lats)
    lat1 = find_nearest(longitude, lons)
    values = data[0:len(dates), lat1, lon1]
    result = pd.DataFrame({'values': values, 'dates': dates})
    return result

#### returns statewide temperature grid from specified dates(s)
## @param start_date:  first date of time slice (YYYYMMDD)
## @param end_date:  last date of time slice (YYYYMMDD)
def time_slice(start_date, end_date):
    indices = np.flatnonzero((dates >= start_date) & (dates <= end_date)).tolist()
    values = data[indices, 0:len(lats), 0:len(lons)]
    return values

#### returns time series of temperatures from a single specified set of coordinates and dates
## @param latitude:  latitude of interest
## @param longitude:  longitude of interest
## @param start_date:  first date of time slice (YYYYMMDD)
## @param end_date:  last date of time slice (YYYYMMDD)
def point_time_slice(latitude, longitude, start_date, end_date):
    lon1 = find_nearest(latitude, lats)
    lat1 = find_nearest(longitude, lons)
    indices = np.flatnonzero((dates >= start_date) & (dates <= end_date)).tolist()
    values = data[indices, lat1, lon1]
    result = pd.DataFrame({'values': values, 'dates': dates[indices]})
    return result

#### Create netcdfs from data slices
## @param outpath:  output file path (e.g. 'path/to/outfile.nc')
## @param data_slice:  time slice of array
def make_ncdf(outpath, data_slice):
    try:
        date_slice = dates[(dates >= start_date) & (dates <= end_date)]
        nc_new = Dataset(outpath, 'w', format ='NETCDF4_CLASSIC')
        nc_new.createDimension('longitude',  len(lons))
        nc_new.createDimension('latitude',  len(lats))
        nc_new.createDimension('time', len(date_slice))
        longitudes = nc_new.createVariable('longitude', np.float32, ('longitude',))
        latitudes  = nc_new.createVariable('latitude',  np.float32, ('latitude',))
        time       = nc_new.createVariable('time',      np.int, ('time',))
        data       = nc_new.createVariable('data',      np.float32, ('time', 'latitude', 'longitude'))
        nc_new.variables['latitude'][:]  = lats
        nc_new.variables['longitude'][:] = lons
        nc_new.variables['time'][:]      = date_slice
        nc_new.variables['data'][:]      = data_slice
    finally:
        # remove file from memory
        nc_new.close()


#-----------------#
#-- read netcdf --#
#-----------------#
## define file path
filepath = 'path/to/netcdf_file.nc'

## open netcdf
nc = Dataset(filepath, 'r')
nc.variables.keys()   # lists variables in netcdf

## get variable values
lons = nc.variables['longitude'][:]   # decimal degrees
lats = nc.variables['latitude'][:]   # decimal degrees
dates = nc.variables['time'][:]   # date in YYYYMMDD format (19810101 to 20161030)
data = nc.variables['data'][:]   # returns a lons x lats x time shaped matrix (53x49x13087)


#------------------------------------#
#-- pre-defined basic data queries --#
#------------------------------------#
## (1) complete time series for a single point
# specify lon/lat
longitude = -106
latitude  = 35

# run process
result = point_slice(latitude = latitude,
                     longitude = longitude)


## (2) time slice of single point
# specify lon, lat, start date, and end date
longitude  = -106
latitude   = 35
start_date = 20160101 
end_date   = 20160701

# run process
result = point_time_slice(latitude = latitude,
                          longitude = longitude,
                          start_date = start_date,
                          end_date = end_date)


## (3) time slice of statewide grid
# specify start and end date
start_date = 20160101 
end_date   = 20160701

# run process
result = time_slice(start_date = start_date,
                    end_date = end_date)


#----------------------------------------#
#-- write time slice as smaller netcdf --#
#----------------------------------------#
## define parameters
start_date = 20160101 
end_date   = 20160701
outpath = 'path/to/output_file.nc'

## slice data
data_slice = time_slice(start_date = start_date,
                        end_date = end_date)

## create netcdf
make_ncdf(outpath = outpath,
          data_slice = data_slice)


#-------------------------------------------#
#-- write data from single date as raster --#
#-------------------------------------------#
## define variables (desired date and outpath for created raster)
date = 20160704 
outpath = 'path/to/output_file.tif'   # define output file path

## get time slice of data
z = time_slice(start_date = date,
               end_date = date)

## define raster parameters
ntimes, nrows, ncols = np.shape(z)
xres = (xmax - xmin) / float(ncols)
yres = (ymax - ymin) / float(nrows)
geotransform = (xmin, xres, 0, ymax, 0, -yres)   
srs = osr.SpatialReference()
srs.ImportFromEPSG(4326)

## write raster to file
output_raster = gdal.GetDriverByName('GTiff').Create(outpath,ncols, nrows, 1, gdal.GDT_Float32)
output_raster.SetGeoTransform(geotransform)
output_raster.SetProjection(srs.ExportToWkt()) 
output_raster.GetRasterBand(1).WriteArray(np.flipud(z[0, :, :]))
del(output_raster)
