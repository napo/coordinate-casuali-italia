
# coding: utf-8

# # creazione di un elenco di punti casuali dentro il confine italiano

# ## prima necessità: avere i confini dell'italia
# ISTAT offre i limiti amministrativi di regioni, province e comuni ed altro ancora.<br/><br/>
# Questi dati sono disponibili qui <br/>
# https://www.istat.it/it/archivio/104317#accordions<br/><br/>
# Non esiste però il file con i confini italiani.<br/>
# A tale scopo andremo a crearli partendo dalla base territoriale offerta da ISTAT più grande quella delle 
# macro ripartizioni territoriali (= sud, centro, nord-est,nord-ovest ed isole)
# 

# i file sono distribuiti in formato shapefile archiviati dentro un file zip.<br/>
# Il file di nostro interesse si trova a questo indirizzo<br/>
# http://www.istat.it/storage/cartografia/confini_amministrativi/non_generalizzati/Limiti01012018.zip

# In[155]:


import requests, zipfile, io
zip_file_url = 'http://www.istat.it/storage/cartografia/confini_amministrativi/non_generalizzati/Limiti01012018.zip'
#richiesa del file
r = requests.get(zip_file_url)
z = zipfile.ZipFile(io.BytesIO(r.content))
#estrazione del file
z.extractall()


# In[156]:


# navigazione della directory aperta dallozip fino al file di nostro interesse 
# Limiti01012018/RipGeo01012018/RipGeo01012018_WGS84.shp
import os
os.chdir('Limiti01012018')
os.chdir('RipGeo01012018')


# Il file è in formato ESRI Shapefile, per aprirlo usiamo il pacchetto fiona

# In[168]:


import fiona
ripgeoshp='RipGeo01012018_WGS84.shp'
aree_italia = fiona.open(ripgeoshp)


# le geometrie contenute possono essere elaborate con il pacchetto shapely

# In[170]:


from shapely.geometry import Polygon, MultiPolygon, shape

#unisco le aree per fare i confini
italia_utm32 = None
for area in aree_italia:
    geom = MultiPolygon(shape(area['geometry']))
    if italia_utm32 == None:
        italia_utm32 = geom
    else:
        italia_utm32 = italia_utm32.union(geom)


# In[172]:


#correggo la geometria non valida
italia_utm32 = italia_utm32.buffer(0)


# I dati ISTAT sono forniti in proiezione WGS84-UTM32N (epsg:32632), occorre convertire in WGS84 (epsg:4326) per avere il sistema di riferimento usato dai GPS

# In[173]:


italia_utm32


# In[174]:


# librerie necessaarie per la conversione
from functools import partial
import pyproj
from shapely.ops import transform


# In[175]:


project = partial(
    pyproj.transform,
    pyproj.Proj(init='epsg:32632'), # source coordinate system
    pyproj.Proj(init='epsg:4326')) # destination coordinate system

italia = transform(project, italia_utm32)  # apply projection


# ora abbiamo i confini d'Italia proiettati in latitudine e longitudine 

# In[94]:


italia


# ## calcolo dei punti sul confine italiano
# per fare questa operazione è necessario avere gli estremi del rettangolo che contiene l'Italia<br/>
# Da qui poi si andrà a creare numeri casuali secondo l'asse X (longitudine) e l'asse Y (latitudine) che contengono il confine italiano<br/>
# Per verificare che ciascun punto sia all'interno del confine italiano, si farà una verifica geospaziale vedendo se il punto è contenuto nel confine.

# In[177]:


minx = italia.bounds[0]
miny = italia.bounds[1] 
maxx = italia.bounds[2] 
maxy = italia.bounds[3] 


# In[178]:


import random
from shapely.geometry import Point


# In[179]:


max_points = 10 # variabile con cui definire quanti punti casuali si vogliono avere
points = []
while len(points) < max_points: 
    lng = random.uniform(minx, maxx)
    lat = random.uniform(miny, maxy)
    point = Point(lng, lat)
    if italia.contains(point):
        points.append(point)


# In[180]:


#stampa a video dei punti
for point in points:
    print(point.x, point.y)


# ## note conclusive
# - onde evitare il calcolo dei confini d'Italia per successive operazioni, è sufficiente salvare la geometria ottenuta in un file (meglio se si usa fiona). 
# - l'elenco dei punti può essere salvato in vari formati a seconda dell'esigenza (fiona supporta molti formati)
