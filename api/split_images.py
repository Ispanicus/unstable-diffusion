from PIL import Image
from itertools import product
from pathlib import Path
import os

def tile(filename, dir_in, dir_out, d):
    name, ext = os.path.splitext(filename)
    img = Image.open(os.path.join(dir_in, filename))
    w, h = img.size
    
    grid = product(range(0, h-h%d, d), range(0, w-w%d, d))
    for i, j in grid:
        box = (j, i, j+d, i+d)
        out = os.path.join(dir_out, f'{name}_{i}_{j}{ext}')
        img.crop(box).save(out)

data_folder = "text2imgdata"
data_folder_clean = "text2imgdata_clean"
dirs = os.listdir(data_folder)
for dir_ in dirs:
	dir_in = Path(data_folder,dir_)
	files = os.listdir(dir_in)
	dir_out = Path(data_folder_clean,dir_)
	dir_out.mkdir(parents=True,exist_ok=True)
	for file in files:
		tile(file,dir_in,dir_out,512)
