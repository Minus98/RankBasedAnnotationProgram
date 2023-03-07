from pathlib import Path
import os
import random
import shutil

im_dir = "Images/"  # whereever you want to get files from
dst_dir = "ImagesSubSet/"  # destination folder
paths = list(Path(im_dir).glob('**/*.jpg'))

for src in random.sample(paths, 20):
    # f1.relative_to(f2) gets relative path from the f2 to f1
    f = str(src.relative_to(im_dir))
    dst = dst_dir + f

    # checks if location exists else it makes a new one
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copy(src, dst)  # copy the file from src to dst
