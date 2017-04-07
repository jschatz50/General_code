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
## writing, and manipulating vector geometry files


#----------------------#
#-- import libraries --#
#----------------------#
import fiona
import geopandas as gpd
import json
import matplotlib.pyplot as plt
import ogr
import osr
import pandas as pd
from PIL import Image, ImageDraw
import shapely
import pprint


#---------------#
#-- read file --#
#---------------#
filepath = "C:/Users/jason.schatz/Documents/Code/Python code/sample_data/Spatial_data/NM_counties.shp"
shape1 = fiona.open(filepath, 'r')


#----------------#
#-- write file --#
#----------------#
## this example opens a shapefile, collects its features, and writes it as a geojson
filepath = "C:/Users/jason.schatz/Documents/Code/Python code/sample_data/Spatial_data/NM_counties.shp"

features = []
with fiona.collection(filepath, "r") as source:
    for feat in source:
        features.append(feat)

my_layer = {
    "type": "FeatureCollection",
    "features": features,
    "crs": {
        "type": "name", 
        "properties": {"name": "EPSG:4326"} }}

with open("L:/my_layer.json", "w") as f:
    f.write(json.dumps(my_layer))


#-------------------------#
#-- convert driver type --#
#-------------------------#
## in shell
ogr2ogr -nlt POLYGON output_name.shape input_name.geojson OGRGeoJson

## convert to GeoJSON from shapefile, e.g.
ogr2ogr -f "GeoJSON" P:\Jason\GIS\Political_boundaries\NM_counties\NM_test.json P:\Jason\GIS\Political_boundaries\NM_counties\NM_counties.shp


#---------------------#
#-- get object info --#
#---------------------#
dir(shape1)
len(shape1)   # number of features
shape1.bounds   # bounding box
shape1.crs   # coordinate reference system
shape1.schema   # feature attributes


#--------------------------#    
#-- query features by ID --#
#--------------------------#
src = fiona.open("P:/Jason/GIS/Political_boundaries/NM_counties/NM_counties.shp")
filtered = filter(lambda f: f['properties']['NAME'] == 'Hidalgo', src)


#--------------#
#-- plotting --#
#--------------#
## simple geometry plot
plt.figure()
for shape in shape1.shapeRecords():
    x = [i[0] for i in shape.shape.points[:]]
    y = [i[1] for i in shape.shape.points[:]]
    plt.plot(x,y)
plt.show()

## chloropleth map (geopandas)
vrbl = 'HOMEVAL'
vmin, vmax = np.min(merged[vrbl]), np.max(merged[vrbl])
ax = merged.plot(column=vrbl, cmap='viridis', vmin=vmin, vmax=vmax)

fig = ax.get_figure()
cax = fig.add_axes([0.9, 0.1, 0.03, 0.8])
sm = plt.cm.ScalarMappable(cmap='viridis', norm=plt.Normalize(vmin=vmin, vmax=vmax))
sm._A = []
fig.colorbar(sm, cax=cax)

plt.show()


#----------------------#
#-- rasterize vector --#
#----------------------#
## in shell
gdal_rasterize -b 1 -i -burn -32678 -l layername input.shp input.tif

## in Python
from osgeo import ogr
from osgeo import gdal

def new_raster_from_base(base, outputURI, format, nodata, datatype):
    cols = base.RasterXSize
    rows = base.RasterYSize
    projection = base.GetProjection()
    geotransform = base.GetGeoTransform()
    bands = base.RasterCount

    driver = gdal.GetDriverByName(format)

    new_raster = driver.Create(str(outputURI), cols, rows, bands, datatype)
    new_raster.SetProjection(projection)
    new_raster.SetGeoTransform(geotransform)

    for i in range(bands):
        new_raster.GetRasterBand(i + 1).SetNoDataValue(nodata)
        new_raster.GetRasterBand(i + 1).Fill(nodata)

    return new_raster

template_path = 'P:/Jason/GIS/_CODE/sample_data/NM_temperature_raster.tif'  # template raster for extents, resolutions
shape_path = 'P:/Jason/GIS/_CODE/sample_data/NM_counties.geojson'
raster_out = 'P:/Jason/GIS/_CODE/sample_data/county_raster.tif'

template_raster = gdal.Open(template_path)
shape_datasource = ogr.Open(shape_path)
shape_layer = shape_datasource.GetLayer()

raster_dataset = new_raster_from_base(template_raster, 
                                      raster_out, 
                                     'GTiff',
                                     -1, 
                                     gdal.GDT_Int32)
band = raster_dataset.GetRasterBand(1)
nodata = band.GetNoDataValue()

band.Fill(nodata)
["ATTRIBUTE=AWATER"]

## specify which attribute to use for dn values
gdal.RasterizeLayer(raster_dataset, [1], shape_layer, None, None, [1], 
                    ['ALL_TOUCHED=TRUE', 'ATTRIBUTE=AWATER'])
raster_dataset.FlushCache()
del(raster_dataset)


#--------------------#
#-- attribute join --#
#--------------------#
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np

geom = gpd.read_file('P:/Jason/GIS/Census/geometries/NM_tracts.shp')
df = pd.read_csv('P:/Jason/GIS/Census/tabular_data/tract_data.csv')
df['GEOID'] = df['GEOID'].astype(str)   # needed for this example
merged = geom.merge(df, on='GEOID')


#-------------------#
#-- spatial joins --#
#-------------------#
#### identify polygon in which point falls
from shapely.geometry import Point

## read in polygon
counties = gpd.read_file('P:/Jason/Geocoder/geographies/counties.shp')

## read in or create points geodataframe
points = {'lon': [-106, -107, -107, -106],
          'lat': [33, 34, 35, 36]
         }
points = pd.DataFrame(points)
crs = {'init': u'epsg:4326'}
geometry = [Point(xy) for xy in zip(points.lon, points.lat)]
geo_df = gpd.GeoDataFrame(points, crs=crs, geometry=geometry)

points['county'] = gpd.sjoin(geo_df, counties, how="left", op='intersects')['NAME']


#-----------------------#
#-- change projection --#
#-----------------------#
## using Python
from functools import partial
import pyproj
from shapely.ops import transform

project = partial(pyproj.transform,
                  pyproj.Proj(init="epsg:4326"),    #source crs
                  pyproj.Proj(init="epsg:26913"))   #desination crs

shape2 = transform(project,shape1)                
                  
driver = ogr.GetDriverByName('ESRI Shapefile')
dataSource = driver.Open(filename,0)
layer = dataSource.GetLayer()

## using shell
ogr2ogr P:\Jason\GIS\Political_boundaries\NM_counties\output.shp -t_srs "EPSG:26913" P:\Jason\GIS\Political_boundaries\NM_counties\NM_counties.shp

