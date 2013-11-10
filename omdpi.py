#!/usr/bin/env python


import numpy as np
from pydap.client import open_url
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import matplotlib.font_manager as font_manager
import matplotlib.image as img
import Image
import requests
import json
import threading
import time
import ftplib
import datetime
import os
import thread
import config
import gdal2tiles

figsize = 4

fontsize= figsize*4
fontsize_meteo= figsize*6

list_of_maps_to_send = []


def log(message) :
    print datetime.datetime.now().strftime("[%d/%m/%Y-%H:%M:%S]") , message


def find_nearest_index2D(array, value):
    idx = np.array([np.linalg.norm(x+y) for (x,y) in array-value]).argmin()
    return idx

def find_nearest_index1D(array,value):
    idx = (np.abs(array-value)).argmin()
    return idx


class OMDThread(threading.Thread):
    def __init__(self ,cfg  ):
        self.cfg = cfg
        self.lastrun = ""
        self.lat = None
        self.lon = None
        self.latidx = None
        self.latidy = None
        self.mapGrid = {}
        self.BB = dict(   lon=[ float(cfg.blipmap_boundingbox.split(",")[0]), float(cfg.blipmap_boundingbox.split(",")[2])],
                          lat=[ float(cfg.blipmap_boundingbox.split(",")[1]), float(cfg.blipmap_boundingbox.split(",")[3])] )
        self._stop = threading.Event()
        threading.Thread.__init__(self)

    def stop(self):
        self._stop.set()
    
    def stopped(self):
        return self._stop.isSet()
     
    def run(self):
        while not self._stop.isSet():
            try:
                (status,run,date) = self.getCurrentRun()
                if ( status == "complete" and run != self.lastrun):
                    self.ProcessRun(run,date )
                    self.lastrun = run
            except:
                log("Error in processing %s %s" % (run,date))
            log("Sleeping ...")
            time.sleep(300)
            
    def getLastRun(self):
        return self.lastrun
    
    def getCurrentRun(self):
        
        url = self.cfg.statusUrl + "?contact=" + self.cfg.contact
        json_data = requests.get(url, timeout=10).json()
        
        #print json.dumps(json_data["france"][0], sort_keys=False,indent=4) 
        status = ""
        i = 0
        while status != "complete" and i < len(json_data["france"]):
            status =  json_data["france"][i]["status"]
            run =  json_data["france"][i]["run"]
            day =  json_data["france"][i]["day"]
            i = i + 1
        if ( status  == "complete"):
            return (status ,run , day)
        else:
            return None
        

    

 
    def loadGrid(self,dataset,param):
        return dataset[param].array[self.latidx.min():self.latidx.max()+1,self.lonidx.min():self.lonidx.max()+1]
    
            
    def plot2D_parameter(self,grid,filename):
      
        fig = plt.figure(figsize=(figsize,figsize),dpi=self.cfg.map_dpi)
        
        Lon,Lat = np.meshgrid(self.lon, self.lat)
       
        map = Basemap(llcrnrlon=self.BB['lon'][0],llcrnrlat=self.BB['lat'][0],urcrnrlon=self.BB['lon'][1],urcrnrlat=self.BB['lat'][1],
                      rsphere=(6378137.00,6356752.3142), resolution='l',projection='merc')
    
        x, y = map(Lon, Lat)
        cs2 = map.contourf(x,y,grid,512)
        
        plt.subplots_adjust(left=0.0, right=figsize, top=figsize, bottom=0.0)
        
        self.saveplot(plt,filename)
        plt.close()

        fig1 = plt.figure(figsize=(11,11),dpi=100)
        cb = map.colorbar(cs2,"bottom", size="5%", pad="100%")
        
        name = filename + '_legend.jpg' 
        plt.savefig("maps/"+name, dpi=100,bbox_inches='tight',transparent=False)
        plt.close()
        list_of_maps_to_send.append("maps/"+name)

        img1 = Image.open("maps/"+name)
        w, h = img1.size
        box = (20, h-70, w-10, h-10)
        area = img1.crop(box)
        area.save("maps/"+name,'jpeg')
        plt.close()

    def plot2D_field(self,gridu,gridv,module,direction,filename):
      
        fig = plt.figure(figsize=(figsize,figsize),dpi=self.cfg.map_dpi)
        
        Lon,Lat = np.meshgrid(self.lon, self.lat)
        
        map = Basemap(llcrnrlon=self.BB['lon'][0],llcrnrlat=self.BB['lat'][0],urcrnrlon=self.BB['lon'][1],urcrnrlat=self.BB['lat'][1],
                      rsphere=(6378137.00,6356752.3142), resolution='l',projection='merc')
    
        
        x, y = map(Lon, Lat)
        cs2 = map.contourf(x,y,module,512)
        
#        barbs = map.barbs(x,y,gridu,gridv,length=8,barbcolor='k',flagcolor='r',linewidth=0.5)
#         barbs = map.quiver(x,y,gridu,gridv,scale=100)
#         qk = plt.quiverkey(barbs, 0.1, 0.1, 20, '20 m/s', labelpos='W')

        lw =  lw = 1 + 4*module/module.max()
        map.streamplot(x,y,gridu,gridv, density=3, color='k', linewidth=lw , arrowsize=2 )

        plt.subplots_adjust(left=0.0, right=figsize, top=figsize, bottom=0.0)
        
        self.saveplot(plt,filename)
        plt.close()

        
        fig1 = plt.figure(figsize=(11,11),dpi=100)
        cb = map.colorbar(cs2,"bottom", size="5%", pad="100%")
        
        name = filename + '_legend.jpg' 
        plt.savefig("maps/"+name, dpi=100,bbox_inches='tight',transparent=False)
        plt.close()
        list_of_maps_to_send.append("maps/"+name)

        
        img1 = Image.open("maps/"+name)
        w, h = img1.size
        box = (20, h-70, w-10, h-10)
        area = img1.crop(box)
        area.save("maps/"+name, 'jpeg')
        plt.close()
        
    def plot_convergence(self,gridWBLMAXMIN,gridUSFC,gridVSFC,filename):
      
        module = (np.sqrt(gridUSFC*gridUSFC+gridVSFC*gridVSFC))*3.6
        
        fig = plt.figure(figsize=(figsize,figsize),dpi=self.cfg.map_dpi)
        
        Lon,Lat = np.meshgrid(self.lon, self.lat)
        
        map = Basemap(llcrnrlon=self.BB['lon'][0],llcrnrlat=self.BB['lat'][0],urcrnrlon=self.BB['lon'][1],urcrnrlat=self.BB['lat'][1],
                      rsphere=(6378137.00,6356752.3142), resolution='l',projection='merc')
    
        
        x, y = map(Lon, Lat)
        cs2 = map.contourf(x,y,gridWBLMAXMIN,512)
        
        
        #print cs2.colors
        
        
        lw = 1 + 4*module/50
        map.streamplot(x,y,gridUSFC,gridVSFC, density=3, color='k', linewidth=lw , arrowsize=2 )
        

        for ix in np.arange(0,module.shape[1],2):
            for iy in np.arange(0,module.shape[0],2):
                #print ix,iy
                ilon = self.lon[ix]
                ilat = self.lat[iy]      
                a,b = map(ilon,  ilat)
                plt.text(a,b  ,int(module[iy,ix]),fontsize=fontsize,fontweight='bold', ha='center',va='center',color='r')
         
        plt.subplots_adjust(left=0.0, right=figsize, top=figsize, bottom=0.0)
        
        self.saveplot(plt,filename)
        plt.close()
        
        fig1 = plt.figure(figsize=(11,11),dpi=100)
        cb = map.colorbar(cs2,"bottom", size="5%", pad="100%")
        
        name = filename + '_legend.jpg' 
        plt.savefig("maps/"+name, dpi=100,bbox_inches='tight',transparent=False)
        plt.close()
        list_of_maps_to_send.append("maps/"+name)

        img1 = Image.open("maps/"+name)
        w, h = img1.size
        box = (20, h-70, w-10, h-10)
        area = img1.crop(box)
        area.save("maps/"+name, 'jpeg')
        plt.close()

    def plot_topBL(self,datagrid,ugrid,vgrid,filename):
      
        module = (np.sqrt(ugrid*ugrid+vgrid*vgrid))*3.6
        
        fig = plt.figure(figsize=(figsize,figsize),dpi=self.cfg.map_dpi)
        
        Lon,Lat = np.meshgrid(self.lon, self.lat)
        
        map = Basemap(llcrnrlon=self.BB['lon'][0],llcrnrlat=self.BB['lat'][0],urcrnrlon=self.BB['lon'][1],urcrnrlat=self.BB['lat'][1],
                      rsphere=(6378137.00,6356752.3142), resolution='l',projection='merc')
    
        x, y = map(Lon, Lat)
        cs2 = map.contourf(x,y,datagrid,512)
        
        levels = np.arange(0, 5000, 100)
        CS = map.contour(x,y,datagrid, levels, linewidths=0.01,colors = 'k')
        plt.clabel(CS,inline=1,fmt='%d')

        lw = 1 + 4*module/50
        map.streamplot(x,y,ugrid,vgrid, density=3, color='k', linewidth=lw , arrowsize=2 )

        for ix in np.arange(0,module.shape[1],2):
            for iy in np.arange(0,module.shape[0],2):
                #print ix,iy
                ilon = self.lon[ix]
                ilat = self.lat[iy]      
                a,b = map(ilon,  ilat)
                plt.text(a,b  ,int(module[iy,ix]),fontsize=fontsize,fontweight='bold', ha='center',va='center',color='r')

        plt.subplots_adjust(left=0.0, right=figsize, top=figsize, bottom=0.0)
        
        self.saveplot(plt,filename)
        plt.close()
        
        
        # Legend
        fig1 = plt.figure(figsize=(11,11),dpi=100)
        cb = map.colorbar(cs2,"bottom", size="5%", pad="100%")
        
        
        name = filename + '_legend.jpg' 
        plt.savefig("maps/"+name, dpi=100,bbox_inches='tight',transparent=False)
        plt.close()
        list_of_maps_to_send.append("maps/"+name)

        
        img1 = Image.open("maps/"+name)
        w, h = img1.size
        box = (20, h-70, w-10, h-10)
        area = img1.crop(box)
        area.save("maps/"+name, 'jpeg')
        plt.close()

    def saveplot(self,plt,filename):
        name = filename + '_map.png' 
        plt.savefig("maps/"+name, dpi=self.cfg.map_dpi,bbox_inches='tight',transparent=True)
        plt.close()
        img1 = Image.open("maps/"+name)
        x,y = img1.size
        wf  = open("maps/" + filename + '_map.wld',"w")
        px = ( self.BB['lon'][1] - self.BB['lon'][0] ) / ( x - 1)
        wf.writelines(  "%.8f\n" %  px ) 
        wf.writelines(  "0\n") 
        wf.writelines(  "0\n") 
        py = ( self.BB['lat'][0]- self.BB['lat'][1] ) / ( y - 1)
        wf.writelines( "%.8f\n" % py  )      
        wf.writelines( "%f\n" % ( self.BB['lon'][0])  ) 
        wf.writelines( "%f\n" % ( self.BB['lat'][1])  ) 
        wf.close()     
        
        
        
        if ( not self.cfg.use_tiles):
            list_of_maps_to_send.append("maps/"+name)
        else:
            cwd = os.getcwd()
            infile = os.path.join(cwd,"maps",name)
            outdir = os.path.join(cwd,"maps",filename + "_map")
            outdir_rel = os.path.join("maps",filename + "_map")
            args = ["-w","none","--s_srs","EPSG:4326","-z",self.cfg.tiles_zooms,infile,outdir ] # -w none
            g2t = gdal2tiles.GDAL2Tiles(args )
            g2t.process()
            list_of_maps_to_send.append(outdir_rel)

    def plot_clouds(self,gridCFRACL,gridCFRACM,gridCFRACH,gridRAINTOT,gridSFCSUN,filename)  :
        
        fontpath = 'img/meteocons.ttf'
        prop = font_manager.FontProperties(fname=fontpath)
        
        # constants
#        dpi = 72; 
#        imageSize = (256,256)
#        # read in our png file
#        im = img.imread("./img/smile.png")
#        

        
        module = ( gridCFRACL + gridCFRACM  ) / 2
        #module = ( gridCFRACL + gridCFRACM + gridCFRACH ) / 3 
        #module = gridSFCSUN
        
        fig = plt.figure(figsize=(figsize,figsize),dpi=self.cfg.map_dpi)
        
        
        Lon,Lat = np.meshgrid(self.lon, self.lat)
        
        map = Basemap(llcrnrlon=self.BB['lon'][0],llcrnrlat=self.BB['lat'][0],urcrnrlon=self.BB['lon'][1],urcrnrlat=self.BB['lat'][1],
                      rsphere=(6378137.00,6356752.3142), resolution='l',projection='merc')
        
        x, y = map(Lon, Lat)
        
        contour_levels = np.arange(10, 100, 1)
        cs2 = map.contourf(x,y,module,contour_levels,vmin=10)
         
# - pioviggine < 1 mm/h
# - pioggia debole 1-2- mm/h
# - pioggia moderata 2-6 mm/h
# - pioggia forte > 6 mm/h
# - rovescio >10 mm/h ma limitato nella durata
# - nubifragio > 30 mm/h 
         
        for ix in np.arange(0,module.shape[1],1):
            for iy in np.arange(0,module.shape[0],1):
                #print ix,iy
                ilon = self.lon[ix]
                ilat = self.lat[iy]      
                a,b = map(ilon,  ilat)
                if ( gridRAINTOT[iy,ix] > 6 ) : 
                    plt.text(a,b ,"8",fontsize=fontsize_meteo,fontproperties=prop, ha='center',va='center',color='r')
                elif ( gridRAINTOT[iy,ix] > 2 ) :
                    plt.text(a,b ,"!",fontsize=fontsize_meteo,fontproperties=prop, ha='center',va='center',color='r')
                elif ( gridRAINTOT[iy,ix] > 0.1 ) :
                    plt.text(a,b ,"7",fontsize=fontsize_meteo,fontproperties=prop, ha='center',va='center',color='r')
                elif ( gridCFRACH[iy,ix] > 10 ) :
                    plt.text(a,b ,"E",fontsize=fontsize_meteo,fontproperties=prop, ha='center',va='center',color='r')    
                elif ( gridCFRACM[iy,ix] > 10 or gridCFRACL[iy,ix] > 10 ) :
                    plt.text(a,b ,"N",fontsize=fontsize_meteo,fontproperties=prop, ha='center',va='center',color='r')

                
        plt.subplots_adjust(left=0.0, right=figsize, top=figsize, bottom=0.0)
        
        
        
        self.saveplot(plt,filename)
        plt.close()
        
        
        
        # Legend
        fig1 = plt.figure(figsize=(11,11),dpi=100)
        cb = map.colorbar(cs2,"bottom", size="5%", pad="100%")
        
        
        name = filename + '_legend.jpg' 
        plt.savefig("maps/"+name, dpi=100,bbox_inches='tight',transparent=False)
        plt.close()
        list_of_maps_to_send.append("maps/"+name)
        
        
        img1 = Image.open("maps/"+name)
        w, h = img1.size
        box = (20, h-70, w-10, h-10)
        area = img1.crop(box)
        area.save("maps/"+name, 'jpeg')
        plt.close()


    def plot_sun(self,gridSUN,gridRAINC,filename)  :
      
      
        module = gridSUN
        
        fig = plt.figure(figsize=(figsize,figsize),dpi=self.cfg.map_dpi)
        
        Lon,Lat = np.meshgrid(self.lon, self.lat)
        
        map = Basemap(llcrnrlon=self.BB['lon'][0],llcrnrlat=self.BB['lat'][0],urcrnrlon=self.BB['lon'][1],urcrnrlat=self.BB['lat'][1],
                      rsphere=(6378137.00,6356752.3142), resolution='l',projection='merc')
    
        x, y = map(Lon, Lat)
 
        #contour_levels = np.arange(10, 100, 1)
        cs2 = map.contourf(x,y,module,512,vmin=10)
         
        plt.subplots_adjust(left=0.0, right=figsize, top=figsize, bottom=0.0)
        
        self.saveplot(plt,filename)
        plt.close()

        
        
        # Legend
        fig1 = plt.figure(figsize=(11,11),dpi=100)
        cb = map.colorbar(cs2,"bottom", size="5%", pad="100%")
        
        
        name = filename + '_legend.jpg' 
        plt.savefig("maps/"+name, dpi=100,bbox_inches='tight',transparent=False)
        plt.close()
        list_of_maps_to_send.append("maps/"+name)

        
        img1 = Image.open("maps/"+name)
        w, h = img1.size
        box = (20, h-70, w-10, h-10)
        area = img1.crop(box)
        area.save("maps/"+name, 'jpeg')
        plt.close()

    def ProcessRun(self,run,date ):
        

        
        
        try:
        # This will create a new file or **overwrite an existing file**.
            f = open("./maps/boundingbox.js", "w")
            line = "    var imageBounds = new google.maps.LatLngBounds("
            f.writelines(line + "\n") 
            line = "    new google.maps.LatLng(%s, %s)," % ( self.cfg.blipmap_boundingbox.split(",")[1],self.cfg.blipmap_boundingbox.split(",")[0]) 
            f.writelines(line + "\n") 
            line = "    new google.maps.LatLng(%s,%s));" % ( self.cfg.blipmap_boundingbox.split(",")[3],self.cfg.blipmap_boundingbox.split(",")[2])  
            f.writelines(line+ "\n") 
            if self.cfg.use_tiles :
                val = "true"
            else:
                val = "false"
            line = "    var use_tiles = %s;" % val
            f.writelines(line + "\n") 
            line = "    var zoom_min = %s;" % self.cfg.tiles_zooms.split("-")[0]
            f.writelines(line + "\n")
            line = "    var zoom_max = %s;" % self.cfg.tiles_zooms.split("-")[1]
            f.writelines(line + "\n")
            line = "    var run = %s;" % run
            f.writelines(line + "\n")
            line = "    var date = %s;" % date
            f.writelines(line + "\n")
            f.close()
        except Exception,e: 
            print str(e)
            pass       
    
        list_of_maps_to_send.append("maps/boundingbox.js")
        
        parameters_2D = [u'SFCSUN', u'PBLTOP', u'WBLMAXMIN', u'ZBLCLMASK', u'V1000',  u'RAINC', u'BLTOPVARIAB', 
                          u'WSTAR', u'ZSFCLCLMASK',   u'CFRACH', u'BLWINDSHEAR', 
                          u'ZBLCLDIFF', u'CFRACM', u'CFRACL', u'ZBLCL',  u'ZWBLMAXMIN', 
                          u'ZSFCLCL',  u'PBLH', u'V2000', u'SLP',  u'TC2',
                          u'U1000',  u'PBLTOPVARIAB',   u'BSRATIO', 
                          u'TER', u'RAINTOT', u'WSFC10', u'ZSFCLCLDIFF',  u'WSFC30', u'RAINNC', u'U2000'  ]
        parameters_Field2D =  [ [ u'UBLAVG',u'VBLAVG'] , [ u'UBLTOP',u'VBLTOP' ] , [ u'USFC', u'VSFC' ]]
        parameters_Field3D =  [ [ u'UMET',u'VMET' ] ]
        parameters_3D  = [ u'TD',u'TC',u'P',u'Z']
        
        
#         for parameter in parameters_2D:
#             print  "{text: \""+parameter.lower()+"\", value:\""+parameter.lower()+"\"}," 
#         for parameter in parameters_Field2D:
#             print  "{text: \""+parameter[1].lower()+"\", value:\""+parameter[1].lower()+"\"},"                       
#         exit()
        
        parameters_2D = [u'WSTAR']
        parameters_Field2D =  [ ]
        
        
  
        for  ttt in self.cfg.hours_to_process.split(','):
            try:
                theTime = int(ttt)
                timezone = time.timezone
                utc_time = theTime + time.timezone / 3600
                gridurl =  'http://dap001.teclib.omd-infra.net/a/rasp-france/%s-%s-%s_%s/%s_%s-%s-%s_%.2d:00:00.nc?contact=%s' % ( run[:4],run[4:6],run[6:8],run[8:10],self.cfg.domain,date[:4],date[4:6],date[6:8],utc_time,self.cfg.contact)
                log( "Processing : Run : %s  - Day %s  - theTime : %s - file : %s" % ( run,date, str(theTime),gridurl))
                dataset   = open_url(gridurl) 
                
                if ( self.lat == None or self.lon == None):
                    # Get all data from lat and lon
                    self.lat=dataset['XLAT'].array[:,0].transpose()[0]
                    self.lon=dataset['XLONG'].array[0,:][0]
                    (self.latidx,) = np.logical_and(self.lat >= self.BB['lat'][0], self.lat < self.BB['lat'][1]).nonzero()
                    (self.lonidx,) = np.logical_and(self.lon >= self.BB['lon'][0], self.lon < self.BB['lon'][1]).nonzero()
                    self.lat = self.lat[self.latidx]
                    self.lon = self.lon[self.lonidx]
                                
                          
                log( "Plotting convergence  %s @ %s"  % ( date, str(theTime) ) )
                gridUSFC  = self.loadGrid(dataset,'USFC')
                gridVSFC  = self.loadGrid(dataset,'VSFC')
                gridWBLMAXMIN = self.loadGrid(dataset,'WBLMAXMIN')   
                filename = "%s%s%s_%.2d_convergence" % (date[6:8],date[4:6],date[:4],theTime) 
                self.plot_convergence(gridWBLMAXMIN,gridUSFC,gridVSFC,filename)
                
                log(  "Plotting topbl   %s @ %s"  % ( date, str(theTime) ) )
                gridUBLTOP  = self.loadGrid(dataset,'UBLTOP')
                gridVBLTOP  = self.loadGrid(dataset,'VBLTOP')
                gridPBLH  = self.loadGrid(dataset,'PBLH')
                filename = "%s%s%s_%.2d_topbl" % (date[6:8],date[4:6],date[:4],theTime) 
                self.plot_topBL(gridPBLH,gridUBLTOP,gridVBLTOP,filename)                
                
                log(  "Plotting clouds   %s @ %s"  % ( date, str(theTime) ) )
                gridCFRACL  = self.loadGrid(dataset,'CFRACL')
                gridCFRACM  = self.loadGrid(dataset,'CFRACM') 
                gridCFRACH  = self.loadGrid(dataset,'CFRACH')
                gridRAINTOT = self.loadGrid(dataset,'RAINTOT')
                gridSFCSUN = self.loadGrid(dataset,'SFCSUN')
                filename = "%s%s%s_%.2d_clouds" % (date[6:8],date[4:6],date[:4],theTime) 
                self.plot_clouds(gridCFRACL,gridCFRACM,gridCFRACH,gridRAINTOT,gridSFCSUN,filename)          
                
                for parameter in parameters_2D:
                    log(   "Plotting %s %s @ %s"  % (  parameter ,date, str(theTime) ) )
                    grid  = dataset[parameter].array[self.latidx.min():self.latidx.max()+1,self.lonidx.min():self.lonidx.max()+1]
                    filename = "%s%s%s_%.2d_%s" % (date[6:8],date[4:6],date[:4],theTime,parameter.lower()) 
                    self.plot2D_parameter(grid,filename)
                    
                for parameter in parameters_Field2D:
                    log(   "Plotting %s %s @ %s"  % (  parameter ,date, str(theTime) ) )
                    gridu  = dataset[parameter[0]].array[self.latidx.min():self.latidx.max()+1,self.lonidx.min():self.lonidx.max()+1]
                    gridv  = dataset[parameter[1]].array[self.latidx.min():self.latidx.max()+1,self.lonidx.min():self.lonidx.max()+1]
                    module = (np.sqrt(gridu*gridu+gridv*gridv))*3.6
                    direction = (np.arctan2(gridu, gridv)/3.14159265358979 + 1)*180
                    filename = "%s%s%s_%.2d_%s" % (date[6:8],date[4:6],date[:4],theTime,parameter[1].lower())
                    self.plot2D_field(gridu,gridv,module,direction,filename)
                    
            except Exception,e: 
                print "Error in Run : %s  - Day %s  - time : %s" % ( run,date, str(theTime))
                print str(e)
                pass       
                
            self.lastrun = run
    


class FTPThread(threading.Thread):

    def __init__(self  ,ftpserver,ftpserverdestfolder,ftpserverlogin,ftpserverpassword,delete):
        self.ftpserver = ftpserver
        self.ftpserverdestfolder = ftpserverdestfolder
        self.ftpserverlogin = ftpserverlogin
        self.ftpserverpassword = ftpserverpassword
        self.delete = delete
        self._stop = threading.Event()
        threading.Thread.__init__(self)

    def stop(self):
        self._stop.set()
    
    def stopped(self):
        return self._stop.isSet()
     
    def run(self):
        while 1:
            if ( len(list_of_maps_to_send) != 0)  :
                map = list_of_maps_to_send.pop(0)
                if os.path.isfile(map):
                    log("Sending file [%d] %s to FTP Server" % (len(list_of_maps_to_send),map ) )
                    self.sendFileToFTPServer(map)
                elif os.path.isdir(map):
                    log("Sending folder [%d] %s to FTP Server" % (len(list_of_maps_to_send),map ) )
                    self.sendFolderToFTPServer(map)
            else:
                time.sleep(10)
    def  sendFolderToFTPServer(self,forder):
        try:
            server_folder = ""
            s = ftplib.FTP(self.ftpserver,self.ftpserverlogin,self.ftpserverpassword,timeout=60)     # Connect
            for current_dir, dirs, files in os.walk(forder):
                for this_file in files:
                    filepath = os.path.join(current_dir, this_file)
                    #self.sendFileToFTPServer(filepath) 
                    f = open(filepath,'rb')                # file to send
                    if ( server_folder != current_dir ) :
                        server_folder = current_dir
                        try:
                            s.mkd(self.ftpserverdestfolder+current_dir)
                        except:
                            pass
                        s.cwd(self.ftpserverdestfolder+current_dir)
                    s.storbinary('STOR ' + this_file, f)         # Send the file
                    f.close()                                # Close file and FTP
                    #log("Sent file to server : " + this_file)
                    if self.delete : 
                        os.remove(this_file)
                        log("Deleted file : " + this_file )
            s.quit() 
            log("Sent folder to server : " + forder)
            if self.delete : 
                os.rmdir(forder)
                log("Deleted folder : " + forder )
            return True            
        except Exception, err:
            print "Exception"
            print '%s' % str(err)    
            log("Error sending  folder to server : " + forder)
            return False                   
                    
                
    def sendFileToFTPServer(self,filename):
        try:
            path,file=os.path.split(filename)
            s = ftplib.FTP(self.ftpserver,self.ftpserverlogin,self.ftpserverpassword,timeout=60)     # Connect
            f = open(filename,'rb')                # file to send
            try:
                s.mkd(self.ftpserverdestfolder+path)
            except:
                pass
            s.cwd(self.ftpserverdestfolder+path)
            s.storbinary('STOR ' + file, f)         # Send the file
            f.close()                                # Close file and FTP
            s.quit() 
            log("Sent file to server : " + filename)
            if self.delete : 
                os.remove(filename)
                log("Deleted file : " + filename )
            return True
        except Exception, err:
            print "Exception"
            print '%s' % str(err)    
            log("Error sending  file to server : " + filename)
            if self.delete : 
                os.remove(filename)
                log("Deleted file : " + filename )
            return False
            
    def add(self,map):
        self.list.append(map)
    
    
 
if __name__ == '__main__':    
    
    
    cfg = config.config("./omdpi.cfg")


    
    if (cfg.sent_to_server):
        ftp = FTPThread(cfg.ftpserver,cfg.ftpserverdestfolder,cfg.ftpserverLogin,cfg.ftpserverPassowd,cfg.delete_after_sent)
        ftp.start()
    
    omd = OMDThread(cfg)
    
    #omd.ProcessRun(run,date )
    #exit()
    
    omd.run()
    




print "Finished"



