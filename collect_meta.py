"""Read filename information for all tiffs in a directory"""


import os

class cd:
    """Context manager for changing the current working directory"""
	
    def __init__(self, newPath):
        self.newPath = os.path.expanduser(newPath)

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)


def Tiff_meta(dir):
	
	import tifffile as tf
	with cd(dir):
		
		meta_dir = dir + '/Metadata'
		#create new directory for metadata
		try:
			os.stat(meta_dir)
		except:
			os.mkdir(meta_dir)
		
		for filename in os.listdir(dir):
			if filename.endswith(".tif") or filename.endswith(".tiff"):
				name = os.path.splitext(filename)[0]
				a,b,c = name.split("_")
				
				#get image structure information
				image = tf.imread(filename)
				
				#read auxillary metadata
				file = open(filename, 'rb')
				data = file.read()
				start = data.find('#')
				end = data.find('N_oscillations 1', start)+22
				aux_meta = data[start:end]
				
				#compile data
				lines = a," ",b," ",c," \n(y,x): ", str(image.shape), "\n", str(aux_meta)

				#create metadata text file
				txt_doc = open(meta_dir + "/" + name + ".txt", "w")
				txt_doc.writelines(lines)
				txt_doc.close()