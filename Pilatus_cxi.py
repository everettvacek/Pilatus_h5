import Pilatus_tiff as pt
import os

path = os.getcwd() + '/fly009'

#Create a .cxi file per scanline
pt.create_cxi(path)

#Create master .cxi  file with links to each scanline
pt.create_master(path, overwrite = False)
