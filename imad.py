import math, platform
import numpy as np  
from numpy.ctypeslib import ndpointer  
from scipy import linalg, stats 
from osgeo import gdal
from osgeo.gdalconst import GA_ReadOnly, GDT_Float32
import os, sys, time
import ctypes

# referencia = "referencia_recortada.tif"
referencia = "D:/redd/referencia/P16_r52_2014057_utm16-RECORTADA.TIF"
# imagen_a_normalizar = "horaria_recortada.tif"
imagen_a_normalizar = "D:/redd/img/LC09_L1TP_016052_20220123_20220124_02_T1-SALIDA/LC09_L1TP_016052_20220123_20220124_02_T1-HORARIA_RECORTADA.tif"
outfile = "D:/redd/img/LC09_L1TP_016052_20220123_20220124_02_T1-SALIDA/IMAD.tif"
penalization = 0.0
format_1GTiff_2PCIDSK_3HFA_4_ENVI = 1


if platform.system() == 'Windows':
    lib = ctypes.cdll.LoadLibrary('D:/Users/mfvargas/AppData/Roaming/QGIS/QGIS3/profiles/default/python/plugins/redd-costarica-scripts-qgis/prov_means.dll')
elif platform.system() == 'Linux':
    lib = ctypes.cdll.LoadLibrary('./libprov_means.so')
elif platform.system() == 'Darwin':
    lib = ctypes.cdll.LoadLibrary('libprov_means.dylib')
provmeans = lib.provmeans
provmeans.restype = None
c_double_p = ctypes.POINTER(ctypes.c_double)
provmeans.argtypes = [ndpointer(np.float64),
                      ndpointer(np.float64),
                      ctypes.c_int,
                      ctypes.c_int,
                      c_double_p,
                      ndpointer(np.float64),
                      ndpointer(np.float64)]
#----------------------------------------


class Cpm(object):
    '''Provisional means algorithm'''
    def __init__(self,N):
        self.mn = np.zeros(N)
        self.cov = np.zeros((N,N))
        self.sw = 0.0000001

    def update(self,Xs,Ws=None):
        n,N = np.shape(Xs)
        if Ws is None:
            Ws = np.ones(n)
        sw = ctypes.c_double(self.sw)
        mn = self.mn
        cov = self.cov
        provmeans(Xs,Ws,N,n,ctypes.byref(sw),mn,cov)
        self.sw = sw.value
        self.mn = mn
        self.cov = cov

    def covariance(self):
        c = np.mat(self.cov/(self.sw-1.0))
        d = np.diag(np.diag(c))
        return c + c.T - d

    def means(self):
        return self.mn
        
# ------------------------
# generalized eigenproblem
# ------------------------

def choldc(A):
# Cholesky-Banachiewicz algorithm,
# A is a numpy matrix
    L = A - A
    for i in range(len(L)):
        for j in range(i):
            sm = 0.0
            for k in range(j):
                sm += L[i,k]*L[j,k]
            L[i,j] = (A[i,j]-sm)/L[j,j]
        sm = 0.0
        for k in range(i):
            sm += L[i,k]*L[i,k]
        L[i,i] = math.sqrt(A[i,i]-sm)
    return L

def geneiv(A,B):
# solves A*x = lambda*B*x for numpy matrices A and B,
# returns eigenvectors in columns
    Li = np.linalg.inv(choldc(B))
    C = Li*A*(Li.transpose())
    C = np.asmatrix((C + C.transpose())*0.5,np.float32)
    eivs,V = np.linalg.eig(C)
    return eivs, Li.transpose()*V     


gdal.AllRegister()
       
inDataset1 = gdal.Open(referencia,GA_ReadOnly)     
cols = inDataset1.RasterXSize
rows = inDataset1.RasterYSize    
bands = inDataset1.RasterCount

pos1 = []
for i in range(bands):
    pos1.append(i+1)

dims = [0,0,cols,rows]

x10,y10,cols1,rows1 = dims

inDataset2 = gdal.Open(imagen_a_normalizar, GA_ReadOnly)     
cols = inDataset2.RasterXSize
rows = inDataset2.RasterYSize    
bands = inDataset2.RasterCount 

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

x20,y20,cols,rows = dims  

print('Normalizando, espere por favor')

#  match dimensions       
print("match dimensions")
bands = len(pos2)
if (rows1 != rows) or (cols1 != cols) or (len(pos1) != bands):
    sys.stderr.write("Size mismatch")
    sys.exit(1)           
#  iteration of MAD    
print("iteration of MAD")

print('       iMAD       ')       
print(time.asctime())     
print('Imagen1: ' + referencia)
print('Imagen2: ' + imagen_a_normalizar)   
print('Delta    [canonical correlations]')

cpm = Cpm(2*bands)    
delta = 1.0
oldrho = np.zeros(bands)     
itr = 0
tile = np.zeros((cols,2*bands))
sigMADs = 0
means1 = 0
means2 = 0
A = 0
B = 0
rasterBands1 = []
rasterBands2 = [] 

for b in pos1:
    rasterBands1.append(inDataset1.GetRasterBand(b)) 
for b in pos2:
    rasterBands2.append(inDataset2.GetRasterBand(b))  
    
while (delta > 0.001) and (itr < 100):   
#      spectral tiling for statistics
    print("spectral tiling for statistics", "delta:", delta, "itr:", itr)
    for row in range(rows):
        for k in range(bands):
            tile[:,k] = rasterBands1[k].ReadAsArray(x10,y10+row,cols,1)
            tile[:,bands+k] = rasterBands2[k].ReadAsArray(x20,y20+row,cols,1)
#          eliminate no-data pixels (assuming all zeroes)  
        #print "eliminate no-data pixels"
        tst1 = np.sum(tile[:,0:bands],axis=1) 
        tst2 = np.sum(tile[:,bands::],axis=1) 
        idx1 = set(np.where(  (tst1>0)  )[0]) 
        idx2 = set(np.where(  (tst2>0)  )[0]) 
        idx = list(idx1.intersection(idx2))    
        if itr>0:
            mads = np.asarray((tile[:,0:bands]-means1)*A - (tile[:,bands::]-means2)*B)
            chisqr = np.sum((mads/sigMADs)**2,axis=1)
            wts = 1-stats.chi2.cdf(chisqr,[bands])
            cpm.update(tile[idx,:],wts[idx])
        else:
            cpm.update(tile[idx,:])
#     weighted covariance matrices and means 
    print("weighted covariance matrices and means")
    S = cpm.covariance() 
    means = cpm.means()             
#     reset prov means object           
    print("reset prov means object")
    cpm.__init__(2*bands)  
    s11 = S[0:bands,0:bands]
    s11 = (1-penalization)*s11 + penalization*np.eye(bands)
    s22 = S[bands:,bands:] 
    s22 = (1-penalization)*s22 + penalization*np.eye(bands)
    s12 = S[0:bands,bands:]
    s21 = S[bands:,0:bands]        
    c1 = s12*linalg.inv(s22)*s21 
    b1 = s11
    c2 = s21*linalg.inv(s11)*s12
    b2 = s22 
#     solution of generalized eigenproblems 
    print("solution of generalized eigenproblems")
    if bands>1:
        mu2a,A = geneiv(c1,b1)                
        mu2b,B = geneiv(c2,b2)               
#          sort a   
        print("sort a")
        idx = np.argsort(mu2a)
        A = A[:,idx]        
#          sort b   
        print("sort b")
        idx = np.argsort(mu2b)
        B = B[:,idx] 
        mu2 = mu2b[idx]
    else:
        mu2 = c1/b1
        A = 1/np.sqrt(b1)
        B = 1/np.sqrt(b2)   
#      canonical correlations             
    print("canonical correlations")
    mu = np.sqrt(mu2)
    a2 = np.diag(A.T*A)
    b2 = np.diag(B.T*B)
    sigma = np.sqrt( (2-penalization*(a2+b2))/(1-penalization)-2*mu )
    rho=mu*(1-penalization)/np.sqrt( (1-penalization*a2)*(1-penalization*b2) )
#      stopping criterion
    print("stopping criterion")
    delta = max(abs(rho-oldrho))       
    
    oldrho = rho  
#      tile the sigmas and means 
    print("tile the sigmas and means")
    sigMADs = np.tile(sigma,(cols,1)) 
    means1 = np.tile(means[0:bands],(cols,1)) 
    means2 = np.tile(means[bands::],(cols,1))
#      ensure sum of positive correlations between X and U is positive
    print("ensure sum of positive correlations between X and U is positive")
    D = np.diag(1/np.sqrt(np.diag(s11)))  
    s = np.ravel(np.sum(D*s11*A,axis=0)) 
    A = A*np.diag(s/np.abs(s))          
#      ensure positive correlation between each pair of canonical variates 
    print("ensure positive correlation between each pair of canonical variates")
    cov = np.diag(A.T*s12*B)    
    B = B*np.diag(cov/np.abs(cov))          
    itr += 1     
    
# write results to disk
print("write results to disk")
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
driver = gdal.GetDriverByName(fmt) 

outDataset = driver.Create(outfile,cols,rows,bands+1,GDT_Float32)
projection = inDataset1.GetProjection()
geotransform = inDataset1.GetGeoTransform()
if geotransform is not None:
    gt = list(geotransform)
    gt[0] = gt[0] + x10*gt[1]
    gt[3] = gt[3] + y10*gt[5]
    outDataset.SetGeoTransform(tuple(gt))
if projection is not None:
    outDataset.SetProjection(projection)            
outBands = [] 
for k in range(bands+1):
    outBands.append(outDataset.GetRasterBand(k+1))   
for row in range(rows):
    for k in range(bands):
        tile[:,k] = rasterBands1[k].ReadAsArray(x10,y10+row,cols,1)
        tile[:,bands+k] = rasterBands2[k].ReadAsArray(x20,y20+row,cols,1)       
    mads = np.asarray((tile[:,0:bands]-means1)*A - (tile[:,bands::]-means2)*B)
    chisqr = np.sum((mads/sigMADs)**2,axis=1) 
    for k in range(bands):
        outBands[k].WriteArray(np.reshape(mads[:,k],(1,cols)),0,row)
    outBands[bands].WriteArray(np.reshape(chisqr,(1,cols)),0,row)                        
for outBand in outBands: 
    outBand.FlushCache()
outDataset = None
inDataset1 = None
inDataset2 = None 
