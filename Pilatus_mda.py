
import os
from collections import OrderedDict
import subprocess


class cd:
#    """Context manager for changing the current working directory"""
	def __init__(self, newPath):
        	self.newPath = os.path.expanduser(newPath)
	def __enter__(self):
		self.savedPath = os.getcwd()
		os.chdir(self.newPath)
	def __exit__(self, etype, value, traceback):
		os.chdir(self.savedPath)

def mdatree2ascii(dir, filename = None):
	"""
	Requires mdautils from https://www3.aps.anl.gov/bcda/mdautils/index.html installation directions are there
	dir: directory containing the MDA file(s).
	filename: MDA file to be extracted. Default None will open all mda files in directory.
	"""

	with cd(dir):
		if filename == None:
			filename = [f for f in os.listdir(os.getcwd()) if f.endswith('.mda')]
			for f in filename:
				#create directory for extracted ascii files
				ascii_f = os.path.splitext(f)[0] + '_asc'

				#increment directory name if it already exists
				if os.path.exists(ascii_f):
					i = 1
					while os.path.exists( os.path.splitext(f)[0] + '_asc_%s' % i):
						i += 1
					ascii_f = os.path.splitext(f)[0] + '_asc_%s' % i

				ascii_dir = os.getcwd() + '/' + ascii_f
				os.mkdir(ascii_f)
					
		else:
			for f in filename:
				#create directory for extracted ascii files
				ascii_f = os.path.splitext(f)[0] + '_asc'
				ascii_dir = os.getcwd() + '/' + ascii_f
				os.mkdir(ascii_f)
		
		#use mdautils in bash to collect data from mda file
		bashCommand = ['mdatree2ascii', os.getcwd(), ascii_dir]
		subprocess.call(bashCommand)

'''
def parse_asc(dir, filename = None):
	"""
	Parse ascii files created by mdatree2ascii. Returns dictionary of elements
	"""
	with cd(dir):

#		if filename == None:
#			filename = [f for f in os.listdir(os.getcwd()) if f.endswith('.mda')]
#			parsed_f = parse_filename('MDA_ASCII', filename) 
		
		Extra_PV = OrderedDict([])
		#collect keys
		
		file = open(filename, 'rb')
		#read enough data to capture header
		data = file.read()
		
		Extra_PV_start = data.find('Extra PV')
		Extra_PV_end = data.find('\n\n\n', Extra_PV_start)
		
		
		start = data.find(key)+len(key)+1
		end = data.find('\r\n', start)
		scan_meta[key].append(data[start:end])
		#collect scan_line data

		
		2D_Scan_Point = OrderDict([('Current point', ), ('Scanner', ), ('Scan time', ), ('Colum Descriptions', Colum_Descriptions)])
		


		MDA_keys = OrderedDict([
			('mda2ascii version', []), ('MDA File Version', []), ('Scan number', []), ('Overall scan dimension', []), ('Extra PV', Extra_PV), ('2-D Scan Point', 2D_Scan_Point) 
		#collect master data
'''	
