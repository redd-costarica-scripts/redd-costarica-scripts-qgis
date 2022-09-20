##Auxiliares=group
##nubeSombra=name
##nubes=raster
##sombras=raster
##tif_0_img_1=number 1
##ns0=output raster
##nsnd=output raster


import sys
import numpy
import glob
from osgeo import gdal, ogr, osr, gdalconst


nubes = "D:/redd/img/LC09_L1TP_016052_20220123_20220124_02_T1-SALIDA/LC09_L1TP_016052_20220123_20220124_02_T1_Fmask4-NUBES-RECORTADA.tif"
sombras = "D:/redd/img/LC09_L1TP_016052_20220123_20220124_02_T1-SALIDA/LC09_L1TP_016052_20220123_20220124_02_T1_Fmask4-SOMBRAS-RECORTADA.tif"
tif_0_img_1 = 0
ns0 = "D:/redd/img/LC09_L1TP_016052_20220123_20220124_02_T1-SALIDA/NS0.tif"
nsnd = "D:/redd/img/LC09_L1TP_016052_20220123_20220124_02_T1-SALIDA/NSND.tif"

utm = 16

if tif_0_img_1==0:
	driver = gdal.GetDriverByName('GTiff')
else:
	driver = gdal.GetDriverByName('HFA')
driver.Register()

dataSourceNubes = gdal.Open(nubes, 0)
dataSourceSombras = gdal.Open(sombras, 0)

rows = dataSourceNubes.RasterYSize
cols = dataSourceNubes.RasterXSize

nubesBand = dataSourceNubes.GetRasterBand(1).ReadAsArray(0, 0, cols, rows)
sombrasBand = dataSourceSombras.GetRasterBand(1).ReadAsArray(0, 0, cols, rows)

outputNs0 = driver.CreateCopy(ns0, dataSourceNubes, 0)
outputNsnd = driver.Create(nsnd, cols, rows, 1, gdal.GDT_Int32)
outputNsnd.SetGeoTransform([outputNs0.GetGeoTransform()[0], outputNs0.GetGeoTransform()[1], outputNs0.GetGeoTransform()[2], outputNs0.GetGeoTransform()[3], outputNs0.GetGeoTransform()[4], outputNs0.GetGeoTransform()[5]])
srs = osr.SpatialReference()
srs.SetUTM(utm, 1)
srs.SetWellKnownGeogCS('WGS84')
outputNsnd.SetProjection(srs.ExportToWkt())
            
ns0Band = numpy.zeros((rows, cols), numpy.int8)
nsndBand = numpy.zeros((rows, cols), numpy.int32)
for rowIndex in range(rows):
    for colIndex in range(cols):
        ns0Band[rowIndex, colIndex] = (nubesBand[rowIndex, colIndex] - 1) * (sombrasBand[rowIndex, colIndex] - 1)
        nsndBand[rowIndex, colIndex] = (ns0Band[rowIndex, colIndex] - 1) * 99999
        
outputNs0.GetRasterBand(1).WriteArray(ns0Band)
outputNsnd.GetRasterBand(1).WriteArray(nsndBand)
