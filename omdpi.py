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


DPI = 50
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
    def __init__(self ,server, domain, blipmap_boundingbox , windgram_places ,start,end ,contact , statusUrl ):
        self.lastrun = ""
        self.lat = None
        self.lon = None
        self.latidx = None
        self.latidy = None
        self.server = server
        self.domain = domain
        self.start = start
        self.end = end
        self.mapGrid = {}
        self.windgram_places = windgram_places
        self.BB = dict(   lon=[ float(blipmap_boundingbox.split(",")[0]), float(blipmap_boundingbox.split(",")[2])],
                          lat=[ float(blipmap_boundingbox.split(",")[1]), float(blipmap_boundingbox.split(",")[3])] )
        self.contact = contact
        self.statusUrl = statusUrl
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
        
        url = self.statusUrl + "?contact=" + self.contact
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
      
        fig = plt.figure(figsize=(5,5),dpi=DPI)
        
        Lon,Lat = np.meshgrid(self.lon, self.lat)
       
        map = Basemap(llcrnrlon=self.BB['lon'][0],llcrnrlat=self.BB['lat'][0],urcrnrlon=self.BB['lon'][1],urcrnrlat=self.BB['lat'][1],
                      rsphere=(6378137.00,6356752.3142), resolution='l',projection='merc')
    
        x, y = map(Lon, Lat)
        cs2 = map.contourf(x,y,grid,512)
        
        plt.subplots_adjust(left=0.0, right=5.0, top=5.0, bottom=0.0)
        
        name = filename + '_map.png' 
        plt.savefig("maps/"+name, dpi=DPI,bbox_inches='tight',transparent=True)
        plt.close()
        list_of_maps_to_send.append(name)

        fig1 = plt.figure(figsize=(11,11),dpi=100)
        cb = map.colorbar(cs2,"bottom", size="5%", pad="100%")
        
        name = filename + '_legend.jpg' 
        plt.savefig("maps/"+name, dpi=100,bbox_inches='tight',transparent=False)
        plt.close()
        list_of_maps_to_send.append(name)

        img1 = Image.open("maps/"+name)
        w, h = img1.size
        box = (20, h-70, w-10, h-10)
        area = img1.crop(box)
        area.save("maps/"+name,'jpeg')
        plt.close()

    def plot2D_field(self,gridu,gridv,module,direction,filename):
      
        fig = plt.figure(figsize=(5,5),dpi=DPI)
        
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

        plt.subplots_adjust(left=0.0, right=5.0, top=5.0, bottom=0.0)
        
        name = filename + '_map.png' 
        plt.savefig("maps/"+name, dpi=DPI,bbox_inches='tight',transparent=True)
        plt.close()
        list_of_maps_to_send.append(name)

        
        fig1 = plt.figure(figsize=(11,11),dpi=100)
        cb = map.colorbar(cs2,"bottom", size="5%", pad="100%")
        
        name = filename + '_legend.jpg' 
        plt.savefig("maps/"+name, dpi=100,bbox_inches='tight',transparent=False)
        plt.close()
        list_of_maps_to_send.append(name)

        
        img1 = Image.open("maps/"+name)
        w, h = img1.size
        box = (20, h-70, w-10, h-10)
        area = img1.crop(box)
        area.save("maps/"+name, 'jpeg')
        plt.close()
        
    def plot_convergence(self,gridWBLMAXMIN,gridUSFC,gridVSFC,filename):
      
        module = (np.sqrt(gridUSFC*gridUSFC+gridVSFC*gridVSFC))*3.6
        
        fig = plt.figure(figsize=(5,5),dpi=DPI)
        
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
                plt.text(a,b  ,int(module[iy,ix]),fontsize=18,fontweight='bold', ha='center',va='center',color='r')
         
        plt.subplots_adjust(left=0.0, right=5.0, top=5.0, bottom=0.0)
        
        name = filename + '_map.png' 
        plt.savefig("maps/"+name, dpi=DPI,bbox_inches='tight',transparent=True)
        plt.close()
        list_of_maps_to_send.append(name)
        
        
        fig1 = plt.figure(figsize=(11,11),dpi=100)
        cb = map.colorbar(cs2,"bottom", size="5%", pad="100%")
        
        
        name = filename + '_legend.jpg' 
        plt.savefig("maps/"+name, dpi=100,bbox_inches='tight',transparent=False)
        plt.close()
        list_of_maps_to_send.append(name)

        img1 = Image.open("maps/"+name)
        w, h = img1.size
        box = (20, h-70, w-10, h-10)
        area = img1.crop(box)
        area.save("maps/"+name, 'jpeg')
        plt.close()

    def plot_topBL(self,datagrid,ugrid,vgrid,filename):
      
        module = (np.sqrt(ugrid*ugrid+vgrid*vgrid))*3.6
        
        fig = plt.figure(figsize=(5,5),dpi=DPI)
        
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
                plt.text(a,b  ,int(module[iy,ix]),fontsize=18,fontweight='bold', ha='center',va='center',color='r')

        plt.subplots_adjust(left=0.0, right=5.0, top=5.0, bottom=0.0)
        
        name = filename + '_map.png' 
        plt.savefig("maps/"+name, dpi=DPI,bbox_inches='tight',transparent=True)
        plt.close()
        list_of_maps_to_send.append(name)

        
        
        # Legend
        fig1 = plt.figure(figsize=(11,11),dpi=100)
        cb = map.colorbar(cs2,"bottom", size="5%", pad="100%")
        
        
        name = filename + '_legend.jpg' 
        plt.savefig("maps/"+name, dpi=100,bbox_inches='tight',transparent=False)
        plt.close()
        list_of_maps_to_send.append(name)

        
        img1 = Image.open("maps/"+name)
        w, h = img1.size
        box = (20, h-70, w-10, h-10)
        area = img1.crop(box)
        area.save("maps/"+name, 'jpeg')
        plt.close()

    def plot_clouds(self,gridCFRACL,gridCFRACM,gridCFRACH,gridRAINTOT,gridSFCSUN,filename)  :
        
        fontpath = 'img/meteocons.ttf'
        prop = font_manager.FontProperties(fname=fontpath)
        
        # constants
        dpi = 72; 
        imageSize = (256,256)
        # read in our png file
        im = img.imread("./img/smile.png")
        

        
        module = ( gridCFRACL + gridCFRACM  ) / 2
        #module = ( gridCFRACL + gridCFRACM + gridCFRACH ) / 3 
        #module = gridSFCSUN
        
        fig = plt.figure(figsize=(5,5),dpi=DPI)
        
        
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
                    plt.text(a,b ,"8",fontsize=26,fontproperties=prop, ha='center',va='center',color='r')
                elif ( gridRAINTOT[iy,ix] > 2 ) :
                    plt.text(a,b ,"!",fontsize=26,fontproperties=prop, ha='center',va='center',color='r')
                elif ( gridRAINTOT[iy,ix] > 0.1 ) :
                    plt.text(a,b ,"7",fontsize=26,fontproperties=prop, ha='center',va='center',color='r')
                elif ( gridCFRACH[iy,ix] > 10 ) :
                    plt.text(a,b ,"E",fontsize=26,fontproperties=prop, ha='center',va='center',color='r')    
                elif ( gridCFRACM[iy,ix] > 10 or gridCFRACL[iy,ix] > 10 ) :
                    plt.text(a,b ,"N",fontsize=26,fontproperties=prop, ha='center',va='center',color='r')

                
        plt.subplots_adjust(left=0.0, right=5.0, top=5.0, bottom=0.0)
        
        
        
        name = filename + '_map.png' 
        plt.savefig("maps/"+name, dpi=DPI,bbox_inches='tight',transparent=True)
        plt.close()
        list_of_maps_to_send.append(name)
        
        
        
        # Legend
        fig1 = plt.figure(figsize=(11,11),dpi=100)
        cb = map.colorbar(cs2,"bottom", size="5%", pad="100%")
        
        
        name = filename + '_legend.jpg' 
        plt.savefig("maps/"+name, dpi=100,bbox_inches='tight',transparent=False)
        plt.close()
        list_of_maps_to_send.append(name)
        
        
        img1 = Image.open("maps/"+name)
        w, h = img1.size
        box = (20, h-70, w-10, h-10)
        area = img1.crop(box)
        area.save("maps/"+name, 'jpeg')
        plt.close()


    def plot_sun(self,gridSUN,gridRAINC,filename)  :
      
      
        module = gridSUN
        
        fig = plt.figure(figsize=(5,5),dpi=DPI)
        
        Lon,Lat = np.meshgrid(self.lon, self.lat)
        
        map = Basemap(llcrnrlon=self.BB['lon'][0],llcrnrlat=self.BB['lat'][0],urcrnrlon=self.BB['lon'][1],urcrnrlat=self.BB['lat'][1],
                      rsphere=(6378137.00,6356752.3142), resolution='l',projection='merc')
    
        x, y = map(Lon, Lat)
 
        #contour_levels = np.arange(10, 100, 1)
        cs2 = map.contourf(x,y,module,512,vmin=10)
         
        plt.subplots_adjust(left=0.0, right=5.0, top=5.0, bottom=0.0)
        
        name = filename + '_map.png' 
        plt.savefig("maps/"+name, dpi=DPI,bbox_inches='tight',transparent=True)
        plt.close()
        list_of_maps_to_send.append(name)

        
        
        # Legend
        fig1 = plt.figure(figsize=(11,11),dpi=100)
        cb = map.colorbar(cs2,"bottom", size="5%", pad="100%")
        
        
        name = filename + '_legend.jpg' 
        plt.savefig("maps/"+name, dpi=100,bbox_inches='tight',transparent=False)
        plt.close()
        list_of_maps_to_send.append(name)

        
        img1 = Image.open("maps/"+name)
        w, h = img1.size
        box = (20, h-70, w-10, h-10)
        area = img1.crop(box)
        area.save("maps/"+name, 'jpeg')
        plt.close()

    def ProcessRun(self,run,date ):
        
        
        
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
        
        for theTime in range(self.start,self.end+1):
            try:
                
                timezone = time.timezone
                utc_time = theTime + time.timezone / 3600
                gridurl =  'http://dap001.teclib.omd-infra.net/a/rasp-france/%s-%s-%s_%s/%s_%s-%s-%s_%.2d:00:00.nc?contact=%s' % ( run[:4],run[4:6],run[6:8],run[8:10],self.domain,date[:4],date[4:6],date[6:8],utc_time,self.contact)
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
                      
                      
                log(  "Plotting clouds   %s @ %s"  % ( date, str(theTime) ) )
                gridCFRACL  = self.loadGrid(dataset,'CFRACL')
                gridCFRACM  = self.loadGrid(dataset,'CFRACM') 
                gridCFRACH  = self.loadGrid(dataset,'CFRACH')
                gridRAINTOT = self.loadGrid(dataset,'RAINTOT')
                gridSFCSUN = self.loadGrid(dataset,'SFCSUN')
                filename = "%s%s%s_%.2d_clouds" % (date[6:8],date[4:6],date[:4],theTime) 
                self.plot_clouds(gridCFRACL,gridCFRACM,gridCFRACH,gridRAINTOT,gridSFCSUN,filename)                    
                                
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
                log("Sending [%d] %s to FTP Server" % (len(list_of_maps_to_send),map ) )
                self.sendFileToFTPServer(map)
            else:
                time.sleep(10)
                
    def sendFileToFTPServer(self,filename):
        try:
            s = ftplib.FTP(self.ftpserver,self.ftpserverlogin,self.ftpserverpassword,timeout=60)     # Connect
            f = open("maps/"+filename,'rb')                # file to send
            s.cwd(self.ftpserverdestfolder)
            s.storbinary('STOR ' + filename, f)         # Send the file
            f.close()                                # Close file and FTP
            s.quit() 
            log("Sent file to server : " + filename)
            if self.delete : 
                os.remove("maps/"+filename)
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

    try:
        # This will create a new file or **overwrite an existing file**.
        f = open("./maps/boundingbox.js", "w")
        try:
            line = "    var imageBounds = new google.maps.LatLngBounds("
            f.writelines(line + "\n") 
            line = "    new google.maps.LatLng(%s, %s)," % ( cfg.blipmap_boundingbox.split(",")[1],cfg.blipmap_boundingbox.split(",")[0]) 
            f.writelines(line + "\n") 
            line = "    new google.maps.LatLng(%s,%s));" % ( cfg.blipmap_boundingbox.split(",")[3],cfg.blipmap_boundingbox.split(",")[2])  
            f.writelines(line+ "\n") 
        finally:
            f.close()
    except IOError:
        pass
    
    list_of_maps_to_send.append("boundingbox.js")
    
    
    ftp = FTPThread(cfg.ftpserver,cfg.ftpserverdestfolder,cfg.ftpserverLogin,cfg.ftpserverPassowd,False)
    ftp.start()
    
    omd = OMDThread(cfg.server, cfg.domain, cfg.blipmap_boundingbox , cfg.windgram_places,cfg.start,cfg.end,cfg.contact , cfg.statusUrl )
    
    #omd.ProcessRun(run,date )
    #exit()
    
    omd.run()
    




print "Finished"



