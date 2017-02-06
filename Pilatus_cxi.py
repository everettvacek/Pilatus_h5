import h5py
import numpy as np

f = h5py.File('Ptycho.cxi','w')
f.create_dataset('cxi_version', data = 130)

tiff = np.ndarray(shape = (619,487,10), dtype = float)
translations = np.ndarray(shape = (256,3), dtype = float)

entry_1 = f.create_group('entry_1')
sample_1 = entry_1.create_group('sample_1')
geometry_1 = sample_1.create_group('geometry_1')
translation = geometry_1.create_dataset('translation', data = translations) #256x3 array of translations (m)

data_1 = entry_1.create_group('data_1')
data_1["translation"] = h5py.SoftLink('/entry_1/sample_1/geometry_1/translation')
data_1["data"] = h5py.SoftLink('/entry_1/instrument_1/detector_1/data')

instrument_1 = entry_1.create_group('instrument_1')
source_1 = instrument_1.create_group('source_1')
energy = source_1.create_dataset('energy', data = 500) # ENERGY OF XRAYS   500eV

detector_1 = instrument_1.create_group('detector_1')
detector_1['translation'] = h5py.SoftLink('/entry_1/sample_1/geometry_1/translation')

distance = detector_1.create_dataset('distance', data = 0.15) # DISTANCE FROM DETECTOR 0.15m
data = detector_1.create_dataset('data', data = tiff) #Image stack with size tiffxlayers
data.attrs['Axes'] = "translation:y:x"