import math
import sys, os, time
import numpy as np 
from scipy import stats
from osgeo import gdal
from osgeo.gdalconst import GA_ReadOnly, GDT_Float32
import matplotlib.pyplot as plt


# referencia = "referencia_recortada.tif"
referencia = "D:/redd/referencia/P16_r52_2014057_utm16-RECORTADA.TIF"
# imagen_a_normalizar = "horaria_recortada.tif"
imagen_a_normalizar = imagen_a_normalizar = "D:/redd/img/LC09_L1TP_016052_20220123_20220124_02_T1-SALIDA/LC09_L1TP_016052_20220123_20220124_02_T1-HORARIA_RECORTADA.tif"
# fsfile = "horaria.tif"
fsfile = "D:/redd/img/LC09_L1TP_016052_20220123_20220124_02_T1-SALIDA/LC09_L1TP_016052_20220123_20220124_02_T1-HORARIA.tif"
# iMad = "imad.tif"
iMad = "D:/redd/img/LC09_L1TP_016052_20220123_20220124_02_T1-SALIDA/IMAD.TIF"
ncpThresh = 0.95
format_1GTiff_2PCIDSK_3HFA_4_ENVI = 1
# outfile = "radcal.tif"
outfile = "D:/redd/img/LC09_L1TP_016052_20220123_20220124_02_T1-SALIDA/RADCAL.TIF"
# fsoutfile = "radiometrica.tif"
fsoutfile = "D:/redd/img/LC09_L1TP_016052_20220123_20220124_02_T1-SALIDA/RADIOMETRICA.TIF"


# ---------------------
# orthogonal regression
# ---------------------

def orthoregress(x,y):
    Xm = np.mean(x)
    Ym = np.mean(y)
    s = np.cov(x,y)
    R = s[0,1]/math.sqrt(s[1,1]*s[0,0])
    lam,vs = np.linalg.eig(s)
    idx = np.argsort(lam)
    vs = vs[:,idx]      # increasing order, so
    b = vs[1,1]/vs[0,1] # first pc is second column
    return [b,Ym-b*Xm,R]


gdal.AllRegister()
     
#  reference image                   
inDataset1 = gdal.Open(referencia,GA_ReadOnly)     
cols = inDataset1.RasterXSize
rows = inDataset1.RasterYSize    
bands = inDataset1.RasterCount

pos1 = []
for i in range(bands):
    pos1.append(i+1)

dims = [0,0,cols,rows]

x10,y10,cols1,rows1 = dims
                
inDataset2 = gdal.Open(imagen_a_normalizar,GA_ReadOnly)     
cols = inDataset2.RasterXSize
rows = inDataset2.RasterYSize    
bands = inDataset2.RasterCount

pos2 = []
for i in range(bands):
    pos2.append(i+1)

dims=[0,0,cols,rows]

x20,y20,cols2,rows2 = dims

#  match dimensions       
bands = len(pos2)
if (rows1 != rows2) or (cols1 != cols2) or (len(pos1) != bands):
    sys.stderr.write("Size mismatch")
    sys.exit(1)             
           
inDataset3 = gdal.Open(iMad,GA_ReadOnly)     
cols = inDataset3.RasterXSize
rows = inDataset3.RasterYSize    
imadbands = inDataset3.RasterCount

dims=[0,0,cols,rows]

x30,y30,cols,rows = dims
    
if (rows1 != rows) or (cols1 != cols):
    sys.stderr.write("Size mismatch")
    sys.exit(1)   
    
#  outfile
fmt = 'GTiff'
outfile = outfile.split('.tif')[0]
if format_1GTiff_2PCIDSK_3HFA_4_ENVI==1:
    fmt = 'GTiff'   
    outfile = outfile + '.tif' 
elif format_1GTiff_2PCIDSK_3HFA_4_ENVI==2:
    fmt = 'PCIDSK'
    outfile = outfile + '.pix'
elif format_1GTiff_2PCIDSK_3HFA_4_ENVI==3:
    fmt = 'HFA'
    outfile = outfile + '.img'
elif format_1GTiff_2PCIDSK_3HFA_4_ENVI==4:
    fmt = 'ENVI'
else: 
   fmt = 'GTiff'
   outfile = outfile + '.tif'
   
chisqr = inDataset3.GetRasterBand(imadbands).ReadAsArray(x30,y30,cols,rows).ravel()
ncp = 1 - stats.chi2.cdf(chisqr,[imadbands-1])
idx = np.where(ncp>ncpThresh)[0]
#  split train/test in ratio 2:1 
tmp = np.asarray(range(len(idx)))
tst = idx[np.where(np.mod(tmp,3) == 0)]
trn = idx[np.where(np.mod(tmp,3) > 0)]
         
driver = gdal.GetDriverByName(fmt)    
outDataset = driver.Create(outfile,cols,rows,bands,GDT_Float32) 
projection = inDataset1.GetProjection()
geotransform = inDataset1.GetGeoTransform()
if geotransform is not None:
    gt = list(geotransform)
    gt[0] = gt[0] + x10*gt[1]
    gt[3] = gt[3] + y10*gt[5]
    outDataset.SetGeoTransform(tuple(gt))
if projection is not None:
    outDataset.SetProjection(projection)      
aa = []
bb = []  
i = 1
for k in pos1:
    x = inDataset1.GetRasterBand(k).ReadAsArray(x10,y10,cols,rows).astype(float).ravel()
    y = inDataset2.GetRasterBand(k).ReadAsArray(x20,y20,cols,rows).astype(float).ravel() 
    b,a,R = orthoregress(y[trn],x[trn])
    aa.append(a)
    bb.append(b)   
    outBand = outDataset.GetRasterBand(i)
    outBand.WriteArray(np.resize(a+b*y,(rows,cols)),0,0) 
    outBand.FlushCache()
    if i <= 10:
        #plt.figure(i)    
        ymax = max(y[idx]) 
        xmax = max(x[idx])      
        #plt.plot(y[idx],x[idx],'k.',[0,ymax],[a,a+b*ymax],'k-')
        #plt.axis([0,ymax,0,xmax])
        #plt.title('Band '+str(k))
        #plt.xlabel('Target')
        #plt.ylabel('Reference')        
    i += 1
outDataset = None
print('Resultado archivado en: '+outfile ) 
if fsfile is not None:
    path = os.path.dirname(fsfile)
    basename = os.path.basename(fsfile)
    root, ext = os.path.splitext(basename)
    #fsoutfile = path+'/'+root+'_norm'+ext 

    print('Normalizando '+fsfile+'...') 

    fsDataset = gdal.Open(fsfile,GA_ReadOnly)
    cols = fsDataset.RasterXSize
    rows = fsDataset.RasterYSize    
    driver = fsDataset.GetDriver()
    outDataset = driver.Create(fsoutfile,cols,rows,bands,GDT_Float32)
    projection = fsDataset.GetProjection()
    geotransform = fsDataset.GetGeoTransform()
    if geotransform is not None:
        outDataset.SetGeoTransform(geotransform)
    if projection is not None:
        outDataset.SetProjection(projection) 
    j = 0
    for k in pos2:
        inBand = fsDataset.GetRasterBand(k)
        outBand = outDataset.GetRasterBand(j+1)
        for i in range(rows):
            y = inBand.ReadAsArray(0,i,cols,1)
            outBand.WriteArray(aa[j]+bb[j]*y,0,i) 
        outBand.FlushCache() 
        j += 1      
    outDataset = None 

