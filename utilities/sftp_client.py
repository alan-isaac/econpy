'''
Adds setting up the socket to the functionality in paramiko\sftp_client.py

:note: Based in part on Cyberdeck's Borne a vin
:note: mostly just a wrapper for the paramiko SFTP client:
:requires: paramiko, which requires pycrypt
:see: http://www.cs.colostate.edu/helpdocs/ftp.html for standard ftp commands (not all implemented!)
:see: http://www.lag.net/paramiko/
:see: http://www.amk.ca/python/code/crypto.html
:see: http://www.voidspace.org.uk/python/modules.shtml#pycrypto (prebuilt binaries!)
'''

import sys, os, base64, getpass, socket, traceback, select
import paramiko 
import logging

class SFTP_wrapper:
	"""
	variable declarations
	"""
	_t = None
	_chan = None
	_sftp = None

	"""
	utility functions
	"""

	def __init__(self,hostname=None,username=None,password=None,port=22):
		self.hostname = hostname
		self.username = username
		self.password = password
		self.port = port
	###  method:  charger la clef from the.  ----------------------------
	def __load_host_keys():
		#if systeme == LINUX
		#filename = os.environ['HOME'] + '/.ssh/known_hosts'
		#if systeme == WINDOWS
		filename = os.environ['USERPROFILE']+ '\key'
		#ifdef windows
		keys = {}
		try:
			f = open(filename, 'r')
		except Exception, e:
			logging.warning('Unable to open host keys file (%s)' % filename)
			return
		for line in f:
			keylist = line.split(' ')
			if len(keylist) != 3:
				continue
			hostlist, keytype, key = keylist
			hosts = hostlist.split(',')
			for host in hosts:
				if not keys.has_key(host):
					keys[host] = {}
				if keytype == 'ssh-rsa':
					keys[host][keytype] = paramiko.RSAKey(data=base64.decodestring(key))
				elif keytype == 'ssh-dss':
					keys[host][keytype] = paramiko.DSSKey(data=base64.decodestring(key))
		f.close()
		return keys
	### END load_host_keys()

	###  method:  open a connection
	def open_connection(self):
		paramiko.util.log_to_file('log.xml')
		# connection parameters
		# (get key if know, but usually it is not)
		hostkeytype = None
		hostkey = None
		hkeys = self.__load_host_keys
	##	if hkeys.has_key(hostname):
	##		hostkeytype = hkeys[hostname].keys()[0]
	##		hostkey = hkeys[hostname][hostkeytype]
	##		print 'Using host key of type %s' % hostkeytype
		# CONNECT (use paramiko Transport (SSH2))
		try:
			#preliminaries
			sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			sock.settimeout(20)
			sock.connect((self.hostname, self.port)) 
			self._t = paramiko.Transport(sock)
			self._t.connect(hostkey=None ,username=self.username, password=self.password, pkey=None)
			self._chan = self._t.open_session()
			self._chan.get_pty()
			self._chan.invoke_shell()
			#finally: create SFTP link via established transport
			self._sftp = paramiko.SFTP.from_transport(self._t)
			return 'ok'
		except Exception, e:
			print '*** Caught exception: ' + str(e.__class__) + ': ' + str(e)
			traceback.print_exc()
			if len(str(e))!=0:
				logging.warning("Exception: "+str(e))
			try:
				self._t.close()
			except:
				pass
				return 'error'
			return 'error'

	### END of open_connection()


	### method: close the connection
	def bye(self):
		try:
			if self._chan != None:
				self._chan.close()
##		time.sleep(0.2)
			if self._t != None:
					self._t.close()
##		time.sleep(0.2) 
		except Exception, e:
			if len(str(e))!=0:
				logging.warning("Exception: "+str(e))
##	Exception, e:
##			print '*** Caught exception: ' + str(e.__class__) + ': ' + str(e)
##			traceback.print_exc()
##		try:
##		self._t.close()
##		except:
##		pass

	### END of bye  ------------------------------------------------------

	### method:  change directory
	def cd(self,path):
		self._sftp.chdir(path)
	### method:  list files in directory
	def ls(self,path = './'):
		try:
			if self._sftp != None:
				liste = self._sftp.listdir(path)
				print liste
				return liste
		except Exception, e:
			if len(str(e))!=0:
				logging.warning("Exception: "+str(e))
	### END of ls  -----------------------------------------------------------------

	### method:  verifier l'existance d'a file dans le serveur -----------------
	def existe(self,nom_fichier):
		try:
			f = self._sftp.open(nom_fichier, mode='rb')
			f.close()
			return True
		except Exception, e:
			return False	
	
#-------------------------------------------------------------------------------
				
	### method:  creer une repertoire ------------------------------------------
	def mk_dir(self,repertoire = 'dir_defaut'):
		try:
			if self._sftp != None:
				self._sftp.mkdir(repertoire, mode=777)
		except Exception, e:
			if len(str(e))!=0:
				logging.warning("Exception: "+str(e))
	### END of mk_dir  -------------------------------------------------------------

	### method:  supprimer une repertoire --------------------------------------
	def rm_dir(self,repertoire = None):
		try:
			if repertoire != None:
			   if self._sftp != None:
					self._sftp.rmdir(repertoire)
		except Exception, e:
			if len(str(e))!=0:
				logging.warning("Exception: "+str(e))
	### END of rm_dir  -------------------------------------------------------------

	### method:  supprimer une repertoire --------------------------------------
	def rm_file(self,fichier = None):
		try:
			if fichier != None:
				if self._sftp != None:
					self._sftp.remove(fichier)
		except Exception, e:
			if len(str(e))!=0:
				logging.warning("Exception: "+str(e))
	### END of rm_dir  -------------------------------------------------------------

##	### method:  enregistrer l'exception dans le fichier  ------------------
##	def log(self,message='erreur inconnue'):
##		if len(message)>5:
##			f = open('log.xml', 'a')
##			f.write("<message>\n<time>%s</time>\n <erreur> [exception] %s </erreur>\n</message>\n"%(time.strftime('[%Y%m%d-%H:%M:%S]',time.localtime()) ,message))
##			f.close
##	### END log  -------------------------------------------------------------------

	### method:  update a file to the server -----------------------------
	def put(self,local_file_name,remote_file_name = None):
		if remote_file_name == None:
			remote_file_name = local_file_name
		try:
			assert(self._sftp != None)
			self._sftp.put(local_file_name, remote_file_name)
			s = self._sftp.stat(remote_file_name)
			print ""
			print "%s uploaded: %d bytes"%(local_file_name, s.st_size)
			print ""
		except	Exception, e:
			print '*** Caught exception: ' + str(e.__class__) + ': ' + str(e)
			traceback.print_exc()
			if len(str(e))!=0:
				logging.warning("Exception: "+str(e))
			try:
				self._t.close()
			except:
				pass
	### END put()

	### method:  download a file from the server
	def get(self,remote_file_name,local_file_name=None):
		if local_file_name == None:
			local_file_name = remote_file_name
		try:
			f = open(local_file_name, 'wb')  
			if self._sftp != None:
				sf = self._sftp.open(remote_file_name,'rb')
				block = sf.read(sf._get_size())		
				f.write(block)
				f.close()
				sf.close()  
#				print "fichier %s download fini"%(remote_file_name)
		except Exception, e:
##		print '*** Caught exception: ' + str(e.__class__) + ': ' + str(e)
##		traceback.print_exc()
			if len(str(e))!=0:
				logging.warning("Exception: "+str(e))
		try:
			self._t.close()
		except:
			pass
	### END get()

