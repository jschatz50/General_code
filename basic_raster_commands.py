#------------#
#-- author --#
#------------#
## Jason Schatz
## Created:  12.29.2016
## Modified: 01.09.2017


#-----------------#
#-- description --#
#-----------------#
## basic, frequently-used functions for reading,
## writing, and manipulating raster data


#----------------------#
#-- import libraries --#
#----------------------#
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import numpy as np
from numpy import meshgrid
import os
from osgeo import gdal, osr, gdalnumeric, ogr
from rasterstats import zonal_stats, point_query
from subprocess import call


#---------------#
#-- open file --#
#---------------#
filepath = "P:/Jason/GIS/_CODE/sample_data/NM_temperature_raster.tif"
dataset = gdal.Open(filepath)


#---------------------#
#-- get object info --#
#---------------------#
dataset.GetProjection()   # projection
dataset.RasterXSize	      # ncols
dataset.RasterYSize       # nrows
dataset.RasterCount	      # bands
dataset.GetDriver().LongName   # object type
band = dataset.GetRasterBand(1)       # isolate band
gdal.GetDataTypeName(band.DataType)   # band data type

attributes = dataset.GetGeoTransform()      # list of attributes
attributes[0]   # top left x 
attributes[1]   # w-e pixel resolution 
attributes[2]   # 0 
attributes[3]   # top left y 
attribites[4]   # 0 
attributes[5]   # n-s pixel resolution (negative value)


#-----------------------#
#-- mask raster/array --#
#-----------------------#
## open files
filepath1   = "P:/Jason/GIS/_CODE/sample_data/NM_temperature_raster.tif"
raster1     = gdal.Open(filepath1)
maskpath    = "P:/Jason/GIS/_CODE/sample_data/county_raster.tif"
mask_raster = gdal.Open(maskpath)

## get attributes
raster_xSize = raster1.RasterXSize
raster_ySize = raster1.RasterYSize
mask_xSize = mask_raster.RasterXSize
mask_ySize = mask_raster.RasterYSize

## mask array
raster_data = raster1.ReadAsArray(0, 0, raster_xSize, raster_ySize)
mask_data = mask_raster.ReadAsArray(0, 0, mask_xSize, mask_ySize)
masked_array = np.where(mask_data > 400000, raster_data, np.nan)

## write data
outpath     = "P:/Jason/GIS/_CODE/sample_data/masked_raster.tif"
driver = gdal.GetDriverByName("GTiff")
output = driver.CreateCopy(outpath, raster1)
output.GetRasterBand(1).WriteArray(masked_array)
del(output)


#------------------------------#
#-- clip raster with polygon --#
#------------------------------#
## using shell
gdalwarp -q -cutline shapefile_name.shp -crop_to_cutline -of GTiff input_raster.tif clipped_raster.tif

## e.g.
gdalwarp -cutline P:\Jason\GIS\_CODE\sample_data\santa_fe_poly.geojson -crop_to_cutline -of GTiff P:\Jason\GIS\_CODE\sample_data\NM_temperature_raster.tif P:\Jason\GIS\_CODE\sample_data\clipped_temperature_raster.tif


#---------------#
#-- reproject --#
#---------------#
## using shell
gdalwarp -t_srs "EPSG:_____" input.tif output.tif

## e.g.
gdalwarp -t_srs "EPSG:102003" P:\Jason\GIS\_CODE\sample_data\NM_temperature_raster.tif P:\Jason\GIS\_CODE\sample_data\reprojected_raster.tif


#--------------------------------#
#-- zonal stats/point sampling --#
#--------------------------------#
raster_path = 'P:/Jason/GIS/_CODE/sample_data/NM_temperature_raster.tif'
poly_path   = 'P:/Jason/GIS/_CODE/sample_data/NM_counties.geojson'
point_path  = 'P:/Jason/GIS/_CODE/sample_data/NM_county_centroids.geojson'
which_stats = ['mean', 'min', 'max', 'median', 'majority', 'sum',
               'count', 'std', 'unique', 'nodata', 'percentile_90']

stats = zonal_stats(poly_path,
                    raster_path,
                    stats=which_stats,
                    band=1, 
                    all_touched=True, 
                    geojson_out=True)

means  = [stats[j]['properties']['mean'] for j in range(len(stats))]
names  = [stats[j]['properties']['NAMELSAD'] for j in range(len(stats))]

stats = point_query(point_path,
                    raster_path)


#---------------------------------------#
#-- create/write geotiff from scratch --#
#---------------------------------------#
z = np.array([
       [0.1, 0.2, 0.3, 0.4],
       [0.2, 0.3, 0.4, 0.5],
       [0.3, 0.4, 0.5, 0.6],
       [0.4, 0.5, 0.6, 0.7]])
y = np.array([
       [10.0, 10.0, 10.0, 10.0],
       [9.5,  9.5,  9.5,  9.5],
       [9.0,  9.0,  9.0,  9.0],
       [8.5,  8.5,  8.5,  8.5]])
x = np.array([
       [20.0, 20.5, 21.0, 21.5],
       [20.0, 20.5, 21.0, 21.5],
       [20.0, 20.5, 21.0, 21.5],
       [20.0, 20.5, 21.0, 21.5]]) 

xmin, ymin, xmax, ymax = [np.min(x), np.min(y), np.max(x), np.max(y)]
nrows, ncols = np.shape(z)
xres = (xmax - xmin) / float(ncols)
yres = (ymax - ymin) / float(nrows)
geotransform = (xmin, xres, 0, ymax, 0, -yres)   

srs = osr.SpatialReference()
srs.ImportFromEPSG(4326)

outpath = 'P:/Jason/GIS/myraster.tif'
output_raster = gdal.GetDriverByName('GTiff').Create(outpath, ncols, nrows, 1, gdal.GDT_Float32)
output_raster.SetGeoTransform(geotransform)
output_raster.SetProjection(srs.ExportToWkt()) 
output_raster.GetRasterBand(1).WriteArray(z)
del(output_raster)


#------------------#
#-- change value --#
#------------------#
z = np.array([
       [0.1, 0.2, 0.3, 0.4],
       [0.2, 0.3, 0.4, 0.5],
       [0.3, 0.4, 0.5, 0.6],
       [0.4, 0.5, 0.6, 0.7]])

z[z > 0.5] = np.nan
z = np.where(z > 0.5, np.nan, z)   # or


#-------------------#
#-- masked arrays --#
#-------------------#
import numpy.ma as ma

## simple example
x = np.array([1, 2, 3, np.nan, 5])
x.mean()   # produces nan because of missing value

mask = np.where(np.isnan(x), 1, 0)
mx = ma.masked_array(x, mask=mask)
mx.mean()   # computes mean after masking missing value


#-------------------------------------------------#
#-- plot image with colorbar and vector overlay --#
#-------------------------------------------------#
## open raster
filepath = "P:/Jason/GIS/_CODE/sample_data/NM_temperature_raster.tif"
ds = gdal.Open(filepath)
data = ds.ReadAsArray()

## create meshgrid from original cooredinates
gt = ds.GetGeoTransform()
xres = gt[1]
yres = gt[5]

xmin = gt[0] + xres * 0.5   # add 0.5 resolution to get to grid cell center
xmax = gt[0] + (xres * ds.RasterXSize) + xres * 0.5
ymin = gt[3] + (yres * ds.RasterYSize) - yres * 0.5
ymax = gt[3] - yres * 0.5

lons = np.arange(xmin, xmax, xres)
lats = np.arange(ymin, ymax, -yres)
lons, lats = np.meshgrid(lons, lats)

## draw figure
fig = plt.figure(figsize=(12, 6))
m = Basemap(width=2000000, 
            height=1500000,
            resolution='l', 
            projection='stere',
            lat_ts=40, 
            lat_0=np.mean(np.array([ymin, ymax])), 
            lon_0=np.mean(np.array([xmin, xmax])))
xx, yy = m(lons, lats)   # convert original coordinates to map projection

m.drawparallels(np.arange(-80., 81., 10.), labels=[1,0,0,0], fontsize=10)
m.drawmeridians(np.arange(-180., 181., 10.), labels=[0,0,0,1], fontsize=10)
m.drawcoastlines()
m.drawcountries()
m.drawstates()
m.readshapefile('P:/Jason/GIS/Census/geometries/NM_counties', 
                'NM_counties', 
                color='black')
m.readshapefile('P:/Jason/GIS/Political_boundaries/NM_state_boundary/NM_state', 
                'NM_state', 
                color='black', 
                linewidth=3)

## define color and colorbar
cs = m.pcolor(xx, yy, np.squeeze(data))
cbar = m.colorbar(cs, location='bottom', pad='10%')

## title
plt.title('plot title')
plt.show()
