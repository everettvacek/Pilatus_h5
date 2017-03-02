import h5py
import numpy as np
from Pilatus_h5 import *
import datetime

path = 'C:/users/everett/research/hdf5/fly009'
scan_meta = collect_tiff_meta(path)
scan_data = collect_tiff_data(path)

f = h5py.File('Ptycho.cxi','w')
f.create_dataset('cxi_version', data = 150)

num_images = 100
tiff = np.ndarray(shape = (num_images,619,487), dtype = float)
translations = np.ndarray(shape = (num_images,3), dtype = float)

#create all folders and sub folders 
entry_1 = f.create_group('entry_1')

sample_1 = entry_1.create_group('sample_1')
geometry_1 = sample_1.create_group('geometry_1')
beam_xy = geometry_1.create_dataset('beam_xy', data = scan_meta['001']['Beam_xy'][0])

image_1 = entry_1.create_group('image_1')
#data = image_1.create_dataset('data')
process_1 = image_1.create_group('process_1')
date = process_1.create_dataset('date', data = datetime.datetime.now().isoformat())
note_1 = process_1.create_group('note_1')
for line in scan_meta:
	folder = note_1.create_group('metadata_' + line)
	for key in scan_meta[line]:
		other_meta = folder.create_dataset( key, data = scan_meta[line][key])


translation = geometry_1.create_dataset('translation', data = translations) #256x3 array of translations (m)
translation.attrs['Units'] = 'meters'
angle_increment = geometry_1.create_dataset('angle_increment', data = scan_meta['001']['Angle_increment'][0])

for line in scan_meta:
	start_angle = geometry_1.create_dataset('start_angle_' + line, data = scan_meta[line]['Start_angle'])


data_1 = entry_1.create_group('data_1')
data_1["translation"] = h5py.SoftLink('/entry_1/sample_1/geometry_1/translation')

instrument_1 = entry_1.create_group('instrument_1')
source_1 = instrument_1.create_group('source_1')
flux = source_1.create_dataset('flux', data = scan_meta['001']['Flux'][0])
attenuator_1 = instrument_1.create_group('attenuator_1')
filter_transmission = attenuator_1.create_dataset('filter_transmission', data = scan_meta['001']['Filter_transmission'])

energy_range = source_1.create_dataset('incident_energy_range', data = scan_meta['001']['Energy_range'][0])
wavelength = source_1.create_dataset('incident_wavelength', data = scan_meta['001']['Wavelength'][0])
polarization = source_1.create_dataset('incident_polarization', data = scan_meta['001']['Polarization'][0])
detector_1 = instrument_1.create_group('detector_1')
detector_1['translation'] = h5py.SoftLink('/entry_1/sample_1/geometry_1/translation')
distance = detector_1.create_dataset('distance', data = scan_meta['001']['Detector_distance'][0])
count_cutoff = detector_1.create_dataset('count_cutoff', data = scan_meta['001']['Count_cutoff'][0])
gain_setting = detector_1.create_dataset('gain_setting', data = scan_meta['001']['Gain_setting:'][0])
v_offset = detector_1.create_dataset('v_offset', data = scan_meta['001']['Detector_Voffset'][0])


for line in scan_data:
	data = detector_1.create_dataset('data_' + line, data = scan_data[line]) #Image stack with size tiffxlayers
	data.attrs['Axes'] = "translation:y:x" 
	data_1['data_' + line] = h5py.SoftLink('/entry_1/instrument_1/detector_1/data_' + line)

	


log_1 = detector_1.create_group('log')
Retrigger_mode = log_1.create_dataset('retrigger_mode', data = int(scan_meta['001']['Retrigger_mode:'][0]))
exposure_time = log_1.create_dataset('exposure_time', data = scan_meta['001']['Exposure_time'][0])
exposure_period = log_1.create_dataset('exposure_period', data = scan_meta['001']['Exposure_period'][0])