import os
import tifffile as tf
import h5py
from collections import OrderedDict

class cd:
#    """Context manager for changing the current working directory"""
	def __init__(self, newPath):
        	self.newPath = os.path.expanduser(newPath)
	def __enter__(self):
		self.savedPath = os.getcwd()
		os.chdir(self.newPath)
	def __exit__(self, etype, value, traceback):
		os.chdir(self.savedPath)

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
			data = f.create_dataset(u'entry/instrument/detector/data', data = scan_data) #h5py.ExternalLink(line_file[i], '/entry_1/instrument_1/detector_1/data')

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
			h5_data = h5_file['entry/instrument/detector/data']
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
