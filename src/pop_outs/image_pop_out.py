import os

import customtkinter as ctk

from utils import ctk_utils


class ImagePopOut():
    """Class representing an image pop-out window."""

    def __init__(
            self, root: ctk.CTk, img_src: str):
        """
        Initialize the ImagePopOut instance.

        Parameters:
            root (ctk.CTk): The root window to attach the pop-out to.
            img_src (str): The file path of the image to display in the pop-out.

        Returns:
            None
        """

        self.root = root
        self.img_src = img_src
        pop_out = ctk.CTkToplevel()
        pop_out.title(os.path.basename(img_src))

        image = ctk_utils.file_2_CTkImage(self.img_src, height=400)[0]
        w, h = image._size
        x, y = ctk_utils.center(self.root, w, h)

        pop_out.geometry('%dx%d+%d+%d' % (w, h, x, y))
        pop_out.columnconfigure(index=0, weight=1)
        pop_out.rowconfigure(index=0, weight=1)

        image_label = ctk.CTkLabel(master=pop_out, image=image, text="").grid(
            row=0, column=0)
