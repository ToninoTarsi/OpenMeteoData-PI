###########################################################################
#     Sint Wind PI
#     Copyright 2012 by Tonino Tarsi <tony.tarsi@gmail.com>
#   
#     Please refer to the LICENSE file for conditions 
#     Visit http://www.vololiberomontecucco.it
# 
##########################################################################
"""Classes and methods for handling configurationn file."""

import sys
import ConfigParser
import os

def str2bool(v):
	return str(v).lower() in ("yes", "true", "t", "1")

class myConfigParser(ConfigParser.SafeConfigParser):
	"""Class extendig  ConfigParser."""

	def __init__(self,verbose=False):
		self.verbose = verbose
		ConfigParser.SafeConfigParser.__init__(self)


	def setboolean(self,section, option,value):
		if ( not ConfigParser.SafeConfigParser.has_section(self,section) ):
			ConfigParser.SafeConfigParser.add_section(self,section)
		if str2bool(value):
			ConfigParser.SafeConfigParser.set(self,section, option,"True")
		else:
			ConfigParser.SafeConfigParser.set(self,section, option,"False")

	def setstr(self,section, option,value):
		if ( not ConfigParser.SafeConfigParser.has_section(self,section) ):
			ConfigParser.SafeConfigParser.add_section(self,section)
		ConfigParser.SafeConfigParser.set(self,section, option,value)	

	def setint(self,section, option,value):
		if ( not ConfigParser.SafeConfigParser.has_section(self,section) ):
			ConfigParser.SafeConfigParser.add_section(self,section)
		ConfigParser.SafeConfigParser.set(self,section, option,str(value))		

	def setfloat(self,section, option,value):
		if ( not ConfigParser.SafeConfigParser.has_section(self,section) ):
			ConfigParser.SafeConfigParser.add_section(self,section)
		ConfigParser.SafeConfigParser.set(self,section, option,str(value))	

	def get(self,section, option,default="None"):
		if ( not ConfigParser.SafeConfigParser.has_section(self,section) ):
			ConfigParser.SafeConfigParser.add_section(self,section)
		try:
			ret = ConfigParser.SafeConfigParser.get(self,section, option)
			if ( self.verbose ): print "Config : " + section + "-" + option + " : " +  ret
			return ret
		except:
			ConfigParser.SafeConfigParser.set(self,section, option,default)
			if ( self.verbose ): print "Config : " + section + "-" + option + " : " +  default
			return default

	def getboolean(self,section, option,default=False):
		if ( not ConfigParser.SafeConfigParser.has_section(self,section) ):
			ConfigParser.SafeConfigParser.add_section(self,section)
			
		try:
			return ConfigParser.SafeConfigParser.getboolean(self,section, option)
		except:
			ConfigParser.SafeConfigParser.set(self,section, option,str(default))
			return default
		
	def getint(self,section, option,default=0):
		if ( not ConfigParser.SafeConfigParser.has_section(self,section) ):
			ConfigParser.SafeConfigParser.add_section(self,section)
			
		try:
			return ConfigParser.SafeConfigParser.getint(self,section, option)
		except:
			ConfigParser.SafeConfigParser.set(self,section, option,str(default))
			return default
			
	def getfloat(self,section, option,default=0):
		if ( not ConfigParser.SafeConfigParser.has_section(self,section) ):
			ConfigParser.SafeConfigParser.add_section(self,section)
			
		try:
			return ConfigParser.SafeConfigParser.getfloat(self,section, option)
		except:
			ConfigParser.SafeConfigParser.set(self,section, option,str(default))
			return default


class config(object):
	"""Class defining software configuration."""
	def __init__(self, filename,verbose=False):
		
		self.cfgName = filename
		self.readCfg(verbose)
		
	def readCfg(self,verbose=False):
		
		config = myConfigParser(verbose)
		
		if (  os.path.isfile(self.cfgName) ):
			config.read(self.cfgName)

		#[General]
		self.server = config.get('General', 'server',"http://dap001.teclib.omd-infra.net/a/rasp-france/")
		self.domain = config.get('General', 'domain',"rasp-france")
		self.run = config.get('General', 'run',"2013102400")
		self.date = config.get('General', 'date',"20131024")
		self.start = config.getint('General', 'start',11)
		self.end = config.getint('General', 'end',19)
		self.windgram_places = config.get('General', 'windgram_places',"Monte Cucco,43.349704,12.773246,1200;Fabriano,43.361297607422,12.776489257812,600")
		self.blipmap_boundingbox = config.get('General', 'blipmap_boundingbox',"12.00, 42.5 ,13.75 , 44.0")
		self.contact = config.get('General', 'contact',"you@gmail.com")
		self.statusUrl = config.get('General', 'statusUrl',"http://data2.rasp-france.org/status.php")
		self.use_tiles = config.getboolean('General', 'use_tiles',False)
		self.tiles_zooms = config.get('General', 'tiles_zooms',"9-12")
		self.map_dpi = config.getint('General', 'map_dpi',50)
		self.hours_to_process = config.get('General', 'hours_to_process',"11,12,13,14,15,16,17.18")



		# [ftp]
		self.sent_to_server = config.getboolean('ftp', 'sent_to_server',True)
		self.ftpserver = config.get('ftp', 'ftpserver',"ftp.yoursite.it")
		self.ftpserverdestfolder = config.get('ftp', 'ftpserverdestfolder',"yoursite.it/img")
		self.ftpserverLogin = config.get('ftp', 'ftpserverLogin',"xxxxxxxxx")
		self.ftpserverPassowd = config.get('ftp', 'ftpserverPassowd',"xxxxxxxxxx")
		self.use_thread_for_sending_to_server = config.getboolean('ftp', 'use_thread_for_sending_to_server',False)
		self.delete_after_sent = config.getboolean('ftp', 'delete_after_sent',False)


		
		f = open(self.cfgName,"w")
		config.write(f)					


	def writeCfg(self):

		config = myConfigParser()
		
		
		#[General]
		config.setstr('General', 'server',self.server)
		config.setstr('General', 'domain',self.domain)
		config.setstr('General', 'run',self.run)
		config.setstr('General', 'date',self.date)
		config.setint('General', 'start',self.start)
		config.setint('General', 'end',self.end)
		config.setstr('General', 'windgram_places',self.windgram_places)
		config.setstr('General', 'blipmap_boundingbox',self.blipmap_boundingbox)
		config.setstr('General', 'contact',self.contact)
		config.setstr('General', 'statusUrl',self.statusUrl)
		config.setboolean('General', 'use_tiles',self.use_tiles)
		config.setstr('General', 'tiles_zooms',self.tiles_zooms)
		config.setint('General', 'map_dpi',self.map_dpi)
		config.setstr('General', 'hours_to_process',self.hours_to_process)




		# [ftp]
		config.setboolean('ftp', 'sent_to_server',self.sent_to_server)		
		config.setstr('ftp', 'ftpserver',self.ftpserver)
		config.setstr('ftp', 'ftpserverdestfolder',self.ftpserverdestfolder)
		config.setstr('ftp', 'ftpserverLogin',self.ftpserverLogin)
		config.setstr('ftp', 'ftpserverPassowd',self.ftpserverPassowd)
		config.setboolean('ftp', 'use_thread_for_sending_to_server',self.use_thread_for_sending_to_server)		
		config.setboolean('ftp', 'delete_after_sent',self.delete_after_sent)		




		f = open(self.cfgName,"w")
		config.write(f)			


		
		
if __name__ == '__main__':
	pass