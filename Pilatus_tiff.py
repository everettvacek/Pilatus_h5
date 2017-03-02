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
