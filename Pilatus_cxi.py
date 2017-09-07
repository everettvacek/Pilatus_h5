import Pilatus_tiff as pt
import os


path = os.getcwd() + '/fly009'

#Create an .h5 file per scanline
pt.create_line_h5(path)

#Create master .cxi  file with links to each scanline
#If overwrite is True all entries will be deleted
pt.create_master(path)
