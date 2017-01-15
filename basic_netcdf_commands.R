#------------#
#-- author --#
#------------#
# Jason Schatz
# NM Dept of Health
# Created: 01/09/17
# Last modified: 01/09/17
# R v3.3.2


#-----------------#
#-- description --#
#-----------------#
## Basic commands for reading, processing, and writing netcdfs in R.
## Netcdfs are basically arrays with attribute information included.
## So once they are open, they can be processed like arrays. I have
## included some basic functions for data query, but to build other custom
## data queries, see R documentation for array structure and commands.


#----------------------#
#-- import libraries --#
#----------------------#
library(ncdf4)
library(raster)


#----------------------#
#-- define functions --#
#----------------------#
#### finds index of nearest value in array
## @param coordinate:  individual coordinate
## @param coordinate_matrix:  matrix of coordinates to search for nearest value
find_nearest <- function(coordinate, coordinate_matrix){
   diffs <- coordinate - coordinate_matrix
   nearest <- which(abs(diffs) == min(abs(diffs)))
   return(nearest)
}

#### returns time series of temperatures from a single specified set of coordinates
## @param latitude:  latitude of interest
## @param longitude:  longitude of interest
point_slice <- function(latitude, longitude){
   lon1 <- find_nearest(latitude, lats)
   lat1 <- find_nearest(longitude, lons)
   values <- data[lon1, lat1, 1:length(dates)]
   result <- data.frame(cbind(dates, values))
   return(result)
}

#### returns statewide temperature grid from specified dates(s)
## @param start_date:  first date of time slice (YYYYMMDD)
## @param end_date:  last date of time slice (YYYYMMDD)
time_slice <- function(start_date, end_date){
   indices <- which(dates >= start_date & dates <= end_date)
   values <- data[1:length(lons), 1:length(lats), indices]
   return(values)
}

#### returns time series of temperatures from a single specified set of coordinates and dates
## @param latitude:  latitude of interest
## @param longitude:  longitude of interest
## @param start_date:  first date of time slice (YYYYMMDD)
## @param end_date:  last date of time slice (YYYYMMDD)
point_time_slice <- function(latitude, longitude, start_date, end_date){
   lon1 <- find_nearest(latitude, lats)
   lat1 <- find_nearest(longitude, lons)
   indices <- which(dates >= start_date & dates <= end_date)
   values <- data[lon1, lat1, indices]
   result <- data.frame(cbind(dates[indices], values))
   return(result)
}

#### Create netcdfs from data slices
## @param outpath:  output file path (e.g. 'path/to/outfile.nc')
## @param data_slice:  time slice of array
make_ncdf <- function(outpath, data_slice){
   # define dimensions
   londim <- ncdim_def("lon", "degrees", as.double(lons)) 
   latdim <- ncdim_def("lat", "degrees", as.double(lats)) 
   date_slice <- dates[which(dates >= start_date & dates <= end_date)]
   timedim <- ncdim_def("time", "date (YYYYMMDD)", date_slice)

   # define variables
   data_def <- ncvar_def(name = "data", 
                         units = "degrees",
                         dim = list(londim, latdim, timedim))

   # create netCDF file and put arrays
   new_nc <- nc_create(outpath, data_def, force_v4=T)

   # write data slice to file
   ncvar_put(new_nc, data_def, data_slice)

   # close file/write data to disk
   nc_close(new_nc)
 }


#-----------------#
#-- read netcdf --#
#-----------------#
## define file path
filepath <- 'path/to/netcdf.nc'

## open netcdf
nc <- nc_open(filepath)

## get variable values
lats  <- ncvar_get(nc, 'latitude')   # decimal degrees
lons  <- ncvar_get(nc, 'longitude')   # decimal degrees
dates <- ncvar_get(nc, 'time')   # date in YYYYMMDD format (19810101 to 20161030)
data  <- ncvar_get(nc, 'data')   # returns a lons x lats x time shaped matrix (53x49x13087)


#------------------------------------#
#-- pre-defined basic data queries --#
#------------------------------------#
## (1) time series for a single point
# specify latitude/longitude
longitude <- -106
latitude  <- 35

# run process
result <- point_slice(latitude = latitude,
                      longitude = longitude)


## (2) time slice of single point
# specify longitude, latitude, start date, and end date
longitude  <- -106
latitude   <- 35
start_date <- 20160101 
end_date   <- 20160701

# run process
result <- point_time_slice(latitude = latitude,
                           longitude = longitude,
                           start_date = start_date,
                           end_date = end_date)


## (3) time slice of statewide grid
# specify start and end dates
start_date <- 20160101 
end_date   <- 20160701

# run process
result <- time_slice(start_date = start_date,
                     end_date = end_date)


#----------------------------------------#
#-- write time slice as smaller netcdf --#
#----------------------------------------#
## define parameters
start_date <- 20160101 
end_date   <- 20160701
outpath <- 'L:/test4.nc'

## slice data
data_slice <- time_slice(start_date = start_date,
                         end_date = end_date)

## create netcdf
make_ncdf(outpath = outpath,
          data_slice = data_slice)


#-------------------------------------------#
#-- write data from single date as raster --#
#-------------------------------------------#
## define variables (desired date and outpath for created raster)
date <- 20160704
outpath <- 'path/to/output_raster.tif'

## slice data to desired date
result <- time_slice(start_date = date, 
                     end_date = date)

## define raster parameters
r <- raster(apply(t(result), 2, rev),
            xmn = min(lons), 
            xmx = max(lons),
            ymn = min(lats), 
            ymx = max(lats), 
            crs = CRS("+proj=longlat +datum=WGS84 +no_defs +ellps=WGS84 +towgs84=0,0,0")
           )

## write raster to file
writeRaster(r, filename=outpath, format="GTiff", overwrite=TRUE)
