"""Read filename information for all tiffs in a directory"""

import os
import tifffile as tf
import h5py

#__all__ = [ 'Pilatus_to_hdf5' ]

class cd:
    """Context manager for changing the current working directory"""
	
    def __init__(self, newPath):
        self.newPath = os.path.expanduser(newPath)

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)


def collect_tiff_meta(dir):
	"""Collects tiff metadata and loads it into a python dictionary"""
	with cd(dir):

		#create dictionary
		scan_meta = {}
		scan_line = list(sorted(set([filename[7:10] for filename in os.listdir(dir) if filename.endswith('.tif')])))

		#search directory for tif files and collect metadata
		for line in scan_line:
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
			for filename in os.listdir(dir):
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

def collect_tiff_data(dir):
	"""Collects tiff data and loads it into python dictionary"""
	import numpy as np
	with cd(dir):

		scan_line = list(sorted(set([filename[7:10] for filename in os.listdir(dir) if filename.endswith('.tif')])))
		scan_data = {}
		for line in scan_line:
			data_array = []
			#scan_line_arrays = {}
			for filename in os.listdir(dir):
				if filename.endswith(".tif") and filename.startswith(line, 7):
					name = os.path.splitext(filename)[0]
					data_array.append(tf.imread(filename))
					#data_array = tf.imread(filename) 
					#scan_line_arrays[filename] = data_array
			#scan_data[line] = scan_line_arrays
			scan_data[line] = np.asarray(data_array, order = 'C')
	return scan_data	

"""	
def collect_tiff_data_cix(dir):
	import numpy as np
	with cd(dir):
		
		scan_line = list(sorted(set([filename[7:10] for filename in os.listdir(dir) if filename.endswith('.tif')])))
		scan_data = np.ndarray( shape
		for line in scan_line:
			for filename in os.listdir(os.getcwd()):
				if filename.endswith(".tif") and filename.startswith(line, 7):
					name = os.path.splitext(filename)[0]
					data_array = tf.imread(filename)
					scan_line_arrays[filename] = data_array
"""


'''def Pilatus_to_hdf5(dir):
	"""
	USE Pilatus_cxi.py INSTEAD
	Uses data and metadata dictionaries to construct HDF5 file
	
	Parameters
	----------
	dir : str
		Directory containing the tiff files
	"""
	
	with cd(dir):
		# Import data and meta data
		scan_meta = collect_tiff_meta(dir)
		scan_data = collect_tiff_data(dir)
		
		# Create a new file using default properties.
		file = h5py.File(scan_meta['001']['Filename'][0][0:6] + '.h5','w')
		try:
			meta_group = file.create_group('Metadata')
			data_group = file.create_group('Scan Data')
		except:
			pass
		#define metadata datatype as variable-length string.
		variable_len_string = h5py.special_dtype(vlen=bytes)
		
		index = 0
		for line in scan_meta:
		
		#create group for scanline data	
			for key in scan_data[line]:
				#check for pre-existing group
				try:
					data_subgroup = data_group.create_group(line)
				except:
					pass
				# Create a dataset under the Root group using float type.		
				something = data_subgroup.create_dataset(key, scan_data[line][key].shape, dtype = float)
				something[...] = scan_data[line][key]		
			for key in scan_meta[line]:
				#check for pre-existing group
				try:
					meta_subgroup = meta_group.create_group(line)
				except:
					pass
				# Create a metadataset under the Root group using variable-length string type.		
				metadataset = meta_subgroup.create_dataset(key,(len(scan_meta[line][key]),), dtype = variable_len_string)
				metadataset[...] = tuple(scan_meta[line][key])

		# Close the file before exiting
		file.close()
'''