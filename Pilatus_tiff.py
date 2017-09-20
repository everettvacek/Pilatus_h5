"""
Collects all data and metadata from Pilatus tiff output and puts them into organized dictionaries
All files must be in the format fly###_###_#####.tif where the first set of  numbers represent the dataset number (001-999)
the second set of numbers represent the scanline (001-999), and the third set of numbers represents the image number (00000-99999)
i.e. flydataset_line_image.tif

"""

import os
import tifffile as tf
import h5py
from collections import OrderedDict
__all__ = [ 'collect_tif_meta', 'collect_tif_data', 'create_master', 'create_cxi', 'metadata_keys', 'parse_filename']

class cd:
#    """Context manager for changing the current working directory"""
	def __init__(self, newPath):
        	self.newPath = os.path.expanduser(newPath)
	def __enter__(self):
		self.savedPath = os.getcwd()
		os.chdir(self.newPath)
	def __exit__(self, etype, value, traceback):
		os.chdir(self.savedPath)


def metadata_keys(detector):
	'''
	dictionary of metadata keys for each detector
	Detector: Name of detector being used. This will specify how headers, filenames and other important metadata is handled
	Detector options: Pilatus 100k, Pilatus 300k
	'''
	if detector == 'Pilatus 100k':
		metadata_keys = OrderedDict([
		('Filename', []), ( 'Date_Time',[]), ( 'Pixel_size', []), ( 'Silicon sensor, thickness' , []), ( 'Exposure_time', []), ( 'Exposure_period', []),
		('Tau' , []), ( 'Count_cutoff', []), ( 'Threshold_setting:', []), ( 'Gain_setting:' , []), ( 'N_excluded_pixels' , []),
		('Excluded_pixels:' , []), ( 'Flat_field:' , []), ( 'Trim_file:' , []), ( 'Image_path:', []), ( 'Ratecorr_lut_directory:' , []),
		('Retrigger_mode:', []), ( 'Wavelength', []), ( 'Energy_range', []), ( 'Detector_distance', []), ( 'Detector_Voffset', []),
		('Detector_Voffset', []), ( 'Beam_xy', []), ( 'Flux', []), ( 'Filter_transmission', []), ( 'Start_angle', []), ( 'Detector_2theta', []),
		('Angle_increment', []), ( 'Polarization', []),( 'Alpha', []), ( 'Kappa', []), ( 'Phi',  []), ( 'Phi_increment',  []), ( 'Chi', []),
		('Chi_increment', []), ( 'Oscillation_axis', []), ( 'N_oscillations',  [])
		])

	return metadata_keys
def sort_by_filename(scan_meta):
	
	#zip the scan_meta values
	zipped_values = zip(*scan_meta.values())
	#sort them according to the filename then unzip
	unzipped_values = zip(*sorted(zipped_values, key = lambda index: index[0]))
	#store sorted values in dict
	key = iter(scan_meta)
	for i in range(len(scan_meta)):
		scan_meta[key.next()] = unzipped_values[i]
	return scan_meta


def parse_filename(filename_format, filename):
	'''
	NEED TO ADD FEATURE TO IDENTIFY AND REMOVE FILE EXTENSIONS 
	'''
	#define empty lists to store parced filename components
	
	scan, line, image = [], [], []
	if filename_format == 'Pilatus 100k' or 'Pilatus 300k':
		name_ext = list(os.path.splitext(x)[0] for x in filename)
		for i in range(len(filename)):
			parced = list(x.split('_') for x in name_ext)[i]
			if len(parced) == 3:
				scan[len(scan):], line[len(line):], image[len(image):] = [parced[0]], [parced[1]], [parced[2]]
			elif len(parced) == 2:
				scan[len(scan):], line[len(line):] = [parced[0]], [parced[1]]
		if image == []:
			a = OrderedDict([('scan', scan), ('line', line)])
		else:   
			a = OrderedDict([('scan', scan), ('line', line), ('image', image)])
	return a


def collect_tif_meta(line):
	"""Collects tif metadata and loads it into a python dictionary"""

	#create sub-dictionary for each scanline
	scan_meta = metadata_keys('Pilatus 100k')                                       #change to ask for detector

	for filename in os.listdir(os.getcwd()):
		if filename.endswith(".tif") and filename.startswith(line,7):
			name = os.path.splitext(filename)[0]
			
			#get image structure information 
			image = tf.imread(filename)
			
			#read auxillary metadata
			file = open(filename, 'rb')
			#read enough data to capture header
			data = file.read(5000)
			
			#store data in dictionary
			scan_meta['Filename'].append(name)
			scan_meta['Date_Time'].append(data[30:34] + '-' + data[35:37] + '-' + data[38:40] + 'T' + data[41:49]+'-0600')
			for key in scan_meta:
				if key == 'Filename' or key == 'Date_Time':
					pass
				else:
					start = data.find(key)+len(key)+1
					end = data.find('\r\n', start)
					scan_meta[key].append(data[start:end])
			file.close()
	return sort_by_filename(scan_meta)

def mdatree2ascii(dir, filename = None):
	import subprocess
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
				os.mkdir(ascii_dir)

				#use mdautils in bash to collect data from mda file
				bashCommand = ['mdatree2ascii', os.getcwd(), ascii_dir]
				subprocess.call(bashCommand)
					
		else:
			for f in filename:
				#create directory for extracted ascii files
				ascii_f = os.path.splitext(f)[0] + '_asc'
				ascii_dir = os.getcwd() + '/' + ascii_f
				os.mkdir(ascii_f)
				#use mdautils in bash to collect data from mda file
				bashCommand = ['mdatree2ascii', os.getcwd(), ascii_dir]
				subprocess.call(bashCommand)
			
def collect_tif_data(line):
	"""Collects tif data and loads it into python dictionary"""
	import numpy as np

	scan_data = OrderedDict([])
	data_array = []
	for filename in os.listdir(os.getcwd()):
		if filename.endswith(".tif") and filename.startswith(line, 7):
			name = os.path.splitext(filename)[0]
			data_array.append(tf.imread(filename))
	scan_data = np.asarray(data_array, order = 'C')
	return scan_data


def create_line_h5(dir, overwrite = False):
	"""Creates HDF5 file for each line of data"""


	mode = 'a'
	if overwrite:
		mode = 'w'

	with cd(dir):
		scan_line = list(sorted(set([filename[7:10] for filename in os.listdir(dir) if filename.endswith('.tif') and filename.startswith('fly')])))

		#Populate groups with each lines data and metadata
		for line in scan_line:
			scan_meta = collect_tif_meta(line)
			scan_data = collect_tif_data(line)
			
			sort_key = range(len(scan_meta['Filename']))
			sort_key.sort(key = scan_meta['Filename'].__getitem__)
			for key in scan_meta:
				scan_meta[key] = map(scan_meta[key].__getitem__, sort_key)
			filename = scan_meta['Filename'][0][0:10]+'.h5'
			f = h5py.File(filename, 'w')
			data = f.create_dataset(u'data/' + unicode(line),data = scan_data) #h5py.ExternalLink(line_file[i], '/entry_1/instrument_1/detector_1/data')

			data.attrs['Axes'] = "translation:y:x" 
			metadata = f.create_group( 'metadata') #[u'metadata/' + unicode(line)] =  scan_meta #h5py.ExternalLink(line_file[i], '/entry_1/image_1/process_1/note_1/metadata')
			for key in scan_meta:
				metadata.create_dataset( key, data = scan_meta[key])
			f.close()		 
'''
		e = True
		i = 0
		#Create new entry
		while e and not overwrite:
			i = i+1
			entry_num = '/entry_' + str(i)
			e = entry_num in m
		#Update/create 'number_of_entries' and 'cxi_version'	
		a = 'number_of_entries' in m
		b = 'cxi_version' in m
		if a and b:
			m['number_of_entries'][...] = i
			m['cxi_version'][...] = 150
		elif a:
			m['number_of_entries'][...] = i
			m['cxi_version'] = 150
		elif b:
			m['number_of_entries'] = i
			m['cxi_version'][...] = 150
		else:
			m['number_of_entries'] = i
			m['cxi_version'] = 150

		#Create metadata and data groups
		metadata_m = m.create_group(entry_num + '/metadata_1')
		data_m = m.create_group(entry_num + '/data_1')
		entry_m = m[entry_num]
		
		entry_m['start_time'] = h5py.ExternalLink(line_file[0], '/entry_1/start_time')
		dt = h5py.special_dtype(vlen=unicode)
		entry_m.create_dataset('experiment_description', (1,), dtype = dt)
		entry_m.create_dataset('experiment_identifier', (1,),  dtype = dt)
'''		




def create_master(dir):
	'''Creates master file in .cxi format from the line files'''
	import numpy as np
	
	with cd(dir):
		#Create sorted list of scan line strings	
		scan_file = list(sorted(set([filename for filename in os.listdir(dir) if filename.endswith('.h5') and filename.startswith('fly') and not filename.endswith('master.cxi')])))
		
		'''
		---------------------MOVE TO PARSE_FILENAME()----------------------
		split_scan_file = []
		for i in range(len(scan_file)):
			split_scan_file.append( os.path.splitext(scan_file[i])[0])

		---------------------MOVE TO PARSE_FILENAME()----------------------
		'''
		scan_filename = parse_filename('Pilatus 100k', scan_file)
		#Create .cxi file for each scan line in the list
		i = 0	
		
		filename = scan_filename['scan'][0]+'_master.cxi'
		f = h5py.File(filename ,'w')
		f.create_dataset('cxi_version', data = 150)

		for line in scan_filename['line']:

			#Create .cxi file 
			h5_file = h5py.File(scan_file[i], 'r')
			print(scan_file[i])
			h5_data = h5_file['/data']
			h5_meta = h5_file['/metadata']
			
			num_images = len(h5_meta['Filename']) 
			translations = np.ndarray(shape = (num_images,3), dtype = float)

			#Populate .cxi file with groups and datasets
			entry_1 = f.create_group('entry_'+str(i))
			entry_1['start_time'] = h5py.ExternalLink(scan_file[i],'/metadata/Date_Time')
			dt = h5py.special_dtype(vlen=unicode)
			entry_1.create_dataset('experiment_description', (1,), dtype = dt)
			entry_1.create_dataset('experiment_identifier', (1,), dtype = dt)
		
			sample_1 = entry_1.create_group('sample_1')
			geometry_1 = sample_1.create_group('geometry_1')
			geometry_1['beam_xy'] = h5py.ExternalLink(scan_file[i],'/metadata/Beam_xy')

			image_1 = entry_1.create_group('image_1')

			process_1 = image_1.create_group('process_1')
			process_1['date'] = h5py.ExternalLink(scan_file[i],'/metadata/Date_Time')
			note_1 = process_1.create_group('note_1')
			folder = note_1.create_group('metadata')
#			for key in scan_meta:
#				folder.create_dataset( key, data = scan_meta[key])


			translation = geometry_1.create_dataset('translation', data = translations) #256x3 array of translations (m)
			translation.attrs['Units'] = 'meters'
			geometry_1['angle_increment'] = h5py.ExternalLink(scan_file[i],'/metadata/Angle_increment')

			geometry_1['start_angle_'+ line] = h5py.ExternalLink(scan_file[i],'/metadata/Start_angle')

			data_1 = entry_1.create_group('data_1')
			data_1["translation"] = h5py.SoftLink(translation.name)

			instrument_1 = entry_1.create_group('instrument_1')

			source_1 = instrument_1.create_group('source_1')
			source_1['flux'] = h5py.ExternalLink(scan_file[i], '/metadata/Flux')

			attenuator_1 = instrument_1.create_group('attenuator_1')
			attenuator_1['filter_transmission'] = h5py.ExternalLink(scan_file[i], 'Filter_transmission')

			source_1['incident_energy_range'] = h5py.ExternalLink(scan_file[i], '/metadata/Energy_range')
			source_1['incident_wavelength'] = h5py.ExternalLink(scan_file[i], '/metadata/Wavelength')
			source_1['incident_polarization'] = h5py.ExternalLink(scan_file[i], '/metadata/Polarization')
			detector_1 = instrument_1.create_group('detector_1')
			detector_1.create_dataset('description', data = 'Pilatus3')
			detector_1['translation'] = h5py.SoftLink(translation.name)
			detector_1['distance'] = h5py.ExternalLink(scan_file[i], '/metadata/Detector_distance')
			detector_1['count_cutoff'] = h5py.ExternalLink(scan_file[i], '/metadata/Count_cutoff')
			detector_1['gain_setting'] = h5py.ExternalLink(scan_file[i], '/metadata/Gain_setting:')
			detector_1['v_offset'] = h5py.ExternalLink(scan_file[i], '/metadata/Detector_Voffset')

			#image data is stored here

#			length = len(h5_data['/'+line])
			detector_1['data'] = h5py.ExternalLink(scan_file[i], '/data/')  #Image stack with size tifxlayers
#			detector_1['data'].attrs['Axes'] = "translation:y:x" 
			data_1[line] = h5py.SoftLink('/entry_' + str(i) + '/instrument_1/detector_1/data/' + line)

			log_1 = detector_1.create_group('log')
#			log_1.create_dataset('retrigger_mode', data = [int(i) for i in scan_meta['Retrigger_mode:']])
#			log_1.create_dataset('exposure_time', data = scan_meta['Exposure_time'])
#			log_1.create_dataset('exposure_period', data = scan_meta['Exposure_period'])


			i = i+1
			h5_file.close()
	f.close()
