"""Collects all data and metadata from Pilatus tiff output and puts them into organized dictionaries"""

import os
import tifffile as tf
import h5py

__all__ = [ 'collect_tiff_meta', 'collect_tiff_data' ]

class cd:
    """Context manager for changing the current working directory"""
	
    def __init__(self, newPath):
        self.newPath = os.path.expanduser(newPath)

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)


def collect_tiff_meta(line):
	"""Collects tiff metadata and loads it into a python dictionary"""
#	with cd(dir):

	#create dictionary
	scan_meta = {}
#		scan_line = list(sorted(set([filename[7:10] for filename in os.listdir(dir) if filename.endswith('.tif') and filename.startswith('fly')])))

	#search directory for tif files and collect metadata
#	for line in scan_line:
	#create sub-dictionary for each scanline
	important_meta = {
	'Filename': [], 'Pixel_size': [], 'Silicon sensor, thickness' : [], 'Exposure_time': [], 'Exposure_period': [],
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
			for key in important_meta:
				if key == 'Filename':
					pass
				else:
					start = data.find(key)+len(key)+1
					end = data.find('\r\n', start)
					important_meta[key].append(data[start:end])
	scan_meta[line] = important_meta
	return scan_meta

def collect_tiff_data(line):
	"""Collects tiff data and loads it into python dictionary"""
	import numpy as np
#	with cd(dir):

#		scan_line = list(sorted(set([filename[7:10] for filename in os.listdir(dir) if filename.endswith('.tif') and filename.startswith('fly')])))
	scan_data = {}
#	for line in scan_line:
	data_array = []
	#scan_line_arrays = {}
	for filename in os.listdir(os.getcwd()):
		if filename.endswith(".tif") and filename.startswith(line, 7):
			name = os.path.splitext(filename)[0]
			data_array.append(tf.imread(filename))
			#data_array = tf.imread(filename) 
			#scan_line_arrays[filename] = data_array
	#scan_data[line] = scan_line_arrays
	scan_data[line] = np.asarray(data_array, order = 'C')
	return scan_data

def create_cxi(dir = None):

	import datetime
	import numpy as np
	
	if dir == None:
		dir = '/raid/home/everett/Pilatus_h5/fly009/'
	else:
		dir = input('path: ')
	with cd(dir):
		
		scan_line = list(sorted(set([filename[7:10] for filename in os.listdir(dir) if filename.endswith('.tif') and filename.startswith('fly')])))
		
		filename = scan_meta[line]['Filename'][0][0:6] + '.cxi'
                master = h5py.File(filename ,'w')
		master.create_dataset('cxi_version', data = 150) 
		
		index = 0	
		for line in scan_line:
			index = index + 1
			scan_meta = collect_tiff_meta(line)
			scan_data = collect_tiff_data(line)
			filename = scan_meta[line]['Filename'][0][0:10]+'.cxi'
			f = h5py.File(filename ,'w')
			f.create_dataset('cxi_version', data = 150)
			
			num_images = len(scan_meta[line]['Filename']) #??????????????????????????????????????????????????????????????????????????????????????????????????
			tiff = np.ndarray(shape = (num_images,619,487), dtype = float)
			translations = np.ndarray(shape = (num_images,3), dtype = float)

			#create all folders and sub folders 
			entry_1 = f.create_group('entry_1')
			entry_m = master.create_group('entry_' + index)

			sample_1 = entry_1.create_group('sample_1')
			geometry_1 = sample_1.create_group('geometry_1')
			beam_xy = geometry_1.create_dataset('beam_xy', data = scan_meta[line]['Beam_xy'])

			sample_m = entry_1.create_group('sample_' + index)
			geometry_m = sample_1.create_group('geometry_' + index)
			beam_xy_m = geometry_1.create_dataset('beam_xy_' + index, data = scan_meta[line]['Beam_xy'])

			image_1 = entry_1.create_group('image_1')

			#data = image_1.create_dataset('data')
			process_1 = image_1.create_group('process_1')
			date = process_1.create_dataset('date', data = datetime.datetime.now().isoformat())
			note_1 = process_1.create_group('note_1')
#			for line in scan_meta:
			folder = note_1.create_group('metadata_' + line)
			for key in scan_meta[line]:
				other_meta = folder.create_dataset( key, data = scan_meta[line][key])


			translation = geometry_1.create_dataset('translation', data = translations) #256x3 array of translations (m)
			translation.attrs['Units'] = 'meters'
			angle_increment = geometry_1.create_dataset('angle_increment', data = scan_meta[line]['Angle_increment'])

#			for line in scan_meta:
			start_angle = geometry_1.create_dataset('start_angle_' + line, data = scan_meta[line]['Start_angle'])


			data_1 = entry_1.create_group('data_1')
			data_1["translation"] = h5py.SoftLink('/entry_1/sample_1/geometry_1/translation')

			instrument_1 = entry_1.create_group('instrument_1')
			source_1 = instrument_1.create_group('source_1')
			flux = source_1.create_dataset('flux', data = scan_meta[line]['Flux'])

			attenuator_1 = instrument_1.create_group('attenuator_1')
			filter_transmission = attenuator_1.create_dataset('filter_transmission', data = scan_meta[line]['Filter_transmission'])

			energy_range = source_1.create_dataset('incident_energy_range', data = scan_meta[line]['Energy_range'])
			wavelength = source_1.create_dataset('incident_wavelength', data = scan_meta[line]['Wavelength'])
			polarization = source_1.create_dataset('incident_polarization', data = scan_meta[line]['Polarization'])
			detector_1 = instrument_1.create_group('detector_1')
			detector_1['translation'] = h5py.SoftLink('/entry_1/sample_1/geometry_1/translation')
			distance = detector_1.create_dataset('distance', data = scan_meta[line]['Detector_distance'])
			count_cutoff = detector_1.create_dataset('count_cutoff', data = scan_meta[line]['Count_cutoff'])
			gain_setting = detector_1.create_dataset('gain_setting', data = scan_meta[line]['Gain_setting:'])
			v_offset = detector_1.create_dataset('v_offset', data = scan_meta[line]['Detector_Voffset'])

			#image data is stored here

			length = len(scan_data)
			data = detector_1.create_dataset('data', data = scan_data[line], chunks = (1,619,487)) #Image stack with size tiffxlayers
			data.attrs['Axes'] = "translation:y:x" 
			data_1['data'] = h5py.SoftLink('/entry_1/instrument_1/detector_1/data')
			data_1['scan_line_ref'] = h5py.SoftLink('/entry_1/instrument_1/detector_1/scan_line_ref')
			#scan_lines = detector_1.create_group('scan_lines')

#			ref_dtype =  h5py.special_dtype(ref=h5py.RegionReference) #define region ref datatype
#			image_ref = detector_1.create_dataset('scan_line_ref', (0,), dtype = ref_dtype,  maxshape = (len(scan_data[line]))

			log_1 = detector_1.create_group('log')
			Retrigger_mode = log_1.create_dataset('retrigger_mode', data = [int(i) for i in scan_meta[line]['Retrigger_mode:']])
			exposure_time = log_1.create_dataset('exposure_time', data = scan_meta[line]['Exposure_time'])
			exposure_period = log_1.create_dataset('exposure_period', data = scan_meta[line]['Exposure_period'])


#			for line in scan_data:
#				data.resize(len(data)+len(scan_data[line]), axis=0) #create space for scanline data
#				scan_line_ref.resize( len(scan_line_ref)+1 , axis = 0) #resize by 1 for each scanline

				#close and open file because of bug in .resize
#				f.close()
#				f = h5py.File(filename, 'r+')
#				data = f['/entry_1/instrument_1/detector_1/data']
#				scan_line_ref = f['/entry_1/instrument_1/detector_1/scan_line_ref']
				
#				
#				data[len(data)-len(scan_data[line]):len(data),:,:] = scan_data[line]  #Image stack with size tiffxlayers
#				line_ref = data.regionref[len(data)-len(scan_data[line]):len(data),] #Reference the scan line region
#				scan_line_ref[len(scan_line_ref)-1] = line_ref #store the line reference in the dataset

			f.close()
