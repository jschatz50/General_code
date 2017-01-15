#------------#
#-- author --#
#------------#
# Jason Schatz 
# created: 01/09/17


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


#----------------------#
#-- define functions --#
#----------------------#
#### returns position in matrix whose value is closest to a specified value
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

#### returns statewide temperature grid from specified dates(s)
## @param start_date:  first date of time slice (YYYYMMDD)
## @param end_date:  last date of time slice (YYYYMMDD)
time_slice <- function(start_date, end_date){
   indices <- which(dates >= start_date & dates <= end_date)
   values <- data[1:length(lons), 1:length(lats), indices]
   return(values)
}


#-----------------#
#-- read netcdf --#
#-----------------#
## define file path
filepath <- 'path_to_netcdf'
filepath <- 'L:/NLDAS/Daily/Tair_daily_maxes.nc'

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
## time series for a single point
longitude <- -106
latitude  <- 35

result <- point_slice(latitude = latitude,
                      longitude = longitude)


## time slice of single point
longitude  <- -106
latitude   <- 35
start_date <- 20160101 
end_date   <- 20160701

result <- point_time_slice(latitude = latitude,
                           longitude = longitude,
                           start_date = start_date,
                           end_date = end_date)


## time slice of statewide grid
start_date <- 20160101 
end_date   <- 20160701

result <- time_slice(start_date = start_date,
                     end_date = end_date)


#---------------------#
#-- write as raster --#
#---------------------#
## example of writing a single time slice fo statewide grid to a gtiff
single_date <- time_slice(20160704, 20160704)
r <-raster(apply(t(single_date), 2, rev),
           xmn=min(lons), xmx=max(lons),
           ymn=min(lats), ymx=max(lats), 
           crs=CRS("+proj=longlat +datum=WGS84 +no_defs +ellps=WGS84 +towgs84=0,0,0")
           )

writeRaster(r, filename="outname.tif", format="GTiff", overwrite=TRUE)
