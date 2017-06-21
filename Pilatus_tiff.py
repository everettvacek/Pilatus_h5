"""
Collects all data and metadata from Pilatus tiff output and puts them into organized dictionaries
All files must be in the format fly###_###_#####.tif where the first set of  numbers represent the dataset number (001-999)
the second set of numbers represent the scanline (001-999), and the third set of numbers represents the image number (00000-99999)
i.e. flydataset_line_image.tif


"""

import os
import tifffile as tf
import h5py

__all__ = [ 'collect_tif_meta', 'collect_tif_data', 'create_master', 'create_cxi']

class cd:
    """Context manager for changing the current working directory"""
	
    def __init__(self, newPath):
        self.newPath = os.path.expanduser(newPath)

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)


def collect_tif_meta(line):
	"""Collects tif metadata and loads it into a python dictionary"""

	#create dictionary
	scan_meta = {}

	#create sub-dictionary for each scanline
	important_meta = {
	'Filename': [], 'Date_Time':[], 'Pixel_size': [], 'Silicon sensor, thickness' : [], 'Exposure_time': [], 'Exposure_period': [],
	'Tau' : [], 'Count_cutoff': [], 'Threshold_setting:': [], 'Gain_setting:' : [], 'N_excluded_pixels' : [], 
	'Excluded_pixels:' : [], 'Flat_field:' : [], 'Trim_file:' : [], 'Image_path:': [], 'Ratecorr_lut_directory:' : [], 
	'Retrigger_mode:': [], 'Wavelength': [], 'Energy_range': [], 'Detector_distance': [], 'Detector_Voffset': [],
	'Detector_Voffset': [], 'Beam_xy': [], 'Flux': [], 'Filter_transmission' : [], 'Start_angle': [], 'Detector_2theta' : [],
	'Angle_increment': [], 'Polarization' : [], 'Alpha' : [], 'Kappa' : [], 'Phi' : [], 'Phi_increment' : [], 'Chi' : [],
	'Chi_increment' : [], 'Oscillation_axis' : [], 'N_oscillations' : []
	}
	for filename in os.listdir(os.getcwd()):
		if filename.endswith(".tif") and filename.startswith(line,7):
			name = os.path.splitext(filename)[0]
			
			#get image structure information 
			image = tf.imread(filename)
			
			#read auxillary metadata
			file = open(filename, 'rb')
			data = file.read()
			
			#store data in dictionary
			important_meta['Filename'].append(name)
			important_meta['Date_Time'].append(data[30:34] + '-' + data[35:37] + '-' + data[38:40] + 'T' + data[41:49]+'-0600')
			for key in important_meta:
				if key == 'Filename' or key == 'Date_Time':
					pass
				else:
					start = data.find(key)+len(key)+1
					end = data.find('\r\n', start)
					important_meta[key].append(data[start:end])
	scan_meta[line] = important_meta
	return scan_meta

def collect_tif_data(line):
	"""Collects tif data and loads it into python dictionary"""
	import numpy as np

	scan_data = {}
	data_array = []
	for filename in os.listdir(os.getcwd()):
		if filename.endswith(".tif") and filename.startswith(line, 7):
			name = os.path.splitext(filename)[0]
			data_array.append(tf.imread(filename))
	scan_data[line] = np.asarray(data_array, order = 'C')
	return scan_data


def create_master(dir, overwrite = False):
	"""Creates master file with external links to each line.cxi file"""


	mode = 'a'
	if overwrite:
		mode = 'w'

	with cd(dir):
		line_file = list(sorted(set([filename for filename in os.listdir(dir) if filename.endswith('.cxi') and filename.startswith('fly') and not filename.endswith('master.cxi')])))
		print(line_file)
		m = h5py.File( line_file[0][0:6] + '_master.cxi', mode)

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
		entry_m.create_dataset('experiment_description', dtype = dt)
		entry_m.create_dataset('experiment_identifier', dtype = dt)
		
		#Populate groups with each lines data and metadata
		for i in range(len(line_file)):
			line = line_file[i][7:10]
			m[data_m.name + u'/' + unicode(line)] = h5py.ExternalLink(line_file[i], '/entry_1/instrument_1/detector_1/data')
			m[metadata_m.name + u'/' + unicode(line)] =  h5py.ExternalLink(line_file[i], '/entry_1/image_1/process_1/note_1/metadata')

		m.close()		 


def create_cxi(dir):
	'''Creates .cxi file for each scanline in a directory'''
	import numpy as np
	
	with cd(dir):
		#Create sorted list of scan line strings	
		scan_line = list(sorted(set([filename[7:10] for filename in os.listdir(dir) if filename.endswith('.tif') and filename.startswith('fly')])))
		
		#Create .cxi file for each scan line in the list
		index = 0	
		for line in scan_line:
			index = index + 1

			# Collect tif data and metadata
			scan_meta = collect_tif_meta(line)
			scan_data = collect_tif_data(line)

			#Create .cxi file 
			filename = scan_meta[line]['Filename'][0][0:10]+'.cxi'
			f = h5py.File(filename ,'w')
			f.create_dataset('cxi_version', data = 150)
			
			num_images = len(scan_meta[line]['Filename']) 
			translations = np.ndarray(shape = (num_images,3), dtype = float)

			#Populate .cxi file with groups and datasets
			entry_1 = f.create_group('entry_1')
			entry_1.create_dataset('start_time', data = scan_meta[line]['Date_Time'][0])
			dt = h5py.special_dtype(vlen=unicode)
			entry_1.create_dataset('experiment_description', dtype = dt)
			entry_1.create_dataset('experiment_identifier', dtype = dt)
		
			sample_1 = entry_1.create_group('sample_1')
			geometry_1 = sample_1.create_group('geometry_1')
			geometry_1.create_dataset('beam_xy', data = scan_meta[line]['Beam_xy'])

			image_1 = entry_1.create_group('image_1')

			process_1 = image_1.create_group('process_1')
			process_1.create_dataset('date', data = scan_meta[line]['Date_Time'][0])
			note_1 = process_1.create_group('note_1')
			folder = note_1.create_group('metadata')
			for key in scan_meta[line]:
				folder.create_dataset( key, data = scan_meta[line][key])


			translation = geometry_1.create_dataset('translation', data = translations) #256x3 array of translations (m)
			translation.attrs['Units'] = 'meters'
			geometry_1.create_dataset('angle_increment', data = scan_meta[line]['Angle_increment'])

			geometry_1.create_dataset('start_angle_' + line, data = scan_meta[line]['Start_angle'])

			data_1 = entry_1.create_group('data_1')
			data_1["translation"] = h5py.SoftLink(translation.name)

			instrument_1 = entry_1.create_group('instrument_1')

			source_1 = instrument_1.create_group('source_1')
			source_1.create_dataset('flux', data = scan_meta[line]['Flux'])

			attenuator_1 = instrument_1.create_group('attenuator_1')
			attenuator_1.create_dataset('filter_transmission', data = scan_meta[line]['Filter_transmission'])

			source_1.create_dataset('incident_energy_range', data = scan_meta[line]['Energy_range'])
			source_1.create_dataset('incident_wavelength', data = scan_meta[line]['Wavelength'])
			source_1.create_dataset('incident_polarization', data = scan_meta[line]['Polarization'])
			detector_1 = instrument_1.create_group('detector_1')
			detector_1.create_dataset('description', data = 'Pilatus3')
			detector_1['translation'] = h5py.SoftLink(translation.name)
			detector_1.create_dataset('distance', data = scan_meta[line]['Detector_distance'])
			detector_1.create_dataset('count_cutoff', data = scan_meta[line]['Count_cutoff'])
			detector_1.create_dataset('gain_setting', data = scan_meta[line]['Gain_setting:'])
			detector_1.create_dataset('v_offset', data = scan_meta[line]['Detector_Voffset'])

			#image data is stored here

			length = len(scan_data)
			data = detector_1.create_dataset('data', data = scan_data[line], chunks = (1,619,487)) #Image stack with size tifxlayers
			data.attrs['Axes'] = "translation:y:x" 
			data_1['data'] = h5py.SoftLink('/entry_1/instrument_1/detector_1/data')

			log_1 = detector_1.create_group('log')
			log_1.create_dataset('retrigger_mode', data = [int(i) for i in scan_meta[line]['Retrigger_mode:']])
			log_1.create_dataset('exposure_time', data = scan_meta[line]['Exposure_time'])
			log_1.create_dataset('exposure_period', data = scan_meta[line]['Exposure_period'])


			f.close()
