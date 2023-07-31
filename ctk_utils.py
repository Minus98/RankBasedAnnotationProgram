import os
from typing import List

import customtkinter as ctk
import nibabel as nib
import numpy as np
from PIL import Image


def file_2_CTkImage(img_src: str, height=None, width=None) -> List[ctk.CTkImage]:
    """
    Convert an image file to a list of CTkImage objects.

    Args:
        img_src (str): The path to the image file.

    Returns:
        List[CTkImage]: The list of CTkImage objects.

    Raises:
        FileNotFoundError: If the image file is not found.
    """

    # img_src = os.path.relpath(self.image_directory + "/" + img_src)

    _, extension = os.path.splitext(img_src)

    if extension == '.nii':
        ctk_imgs = []
        nib_imgs = nib.load(img_src).get_fdata()
        for i in range(nib_imgs.shape[2]):
            img = nib_imgs[:, :, i]
            if height:
                resize_factor = height / img.shape[1]
            elif width:
                resize_factor = width / img.shape[0]
            else:
                resize_factor = 1
            new_shape = (
                int(img.shape[0] * resize_factor),
                int(img.shape[1] * resize_factor))
            ctk_imgs.append(
                ctk.CTkImage(
                    Image.fromarray(np.rot90(img)).resize(
                        new_shape, resample=2),
                    size=(new_shape)))
        return ctk_imgs
    else:
        if height:
            size = (height, height)
        elif width:
            size = (width, width)
        return [ctk.CTkImage(Image.open(img_src), size=size)]
