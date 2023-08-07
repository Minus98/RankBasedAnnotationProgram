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
        """

        self.root = root
        self.img_src = img_src
        self.pop_out = ctk.CTkToplevel()
        self.pop_out.title(os.path.basename(img_src))

        self.image_data = ctk_utils.file_2_CTkImage(
            self.img_src, height=400)
        self.idx = 0

        w, h = self.image_data[self.idx]._size
        x, y = ctk_utils.center(self.root, w, h)

        self.pop_out.geometry('%dx%d+%d+%d' % (w, h, x, y))
        self.pop_out.columnconfigure(index=0, weight=1)
        self.pop_out.rowconfigure(index=0, weight=1)

        self.pop_out.bind(
            "<MouseWheel>", lambda event: self.on_image_scroll(event))
        self.pop_out.bind(
            "<Button-4>", lambda event: self.on_image_scroll_up())
        self.pop_out.bind(
            "<Button-5>", lambda event: self.on_image_scroll_down())

        self.image_label = ctk.CTkLabel(
            master=self.pop_out, image=self.image_data[self.idx], text="")
        self.image_label.grid(row=0, column=0)

    def on_image_scroll(self, event):
        print(event)
        if event.delta < 0:
            self.idx = max(self.idx-1, 0)

        elif event.delta > 0:
            self.idx = min(
                self.idx+1, len(self.image_data)-1)

        self.update_image()

    def on_image_scroll_up(self):
        self.idx = min(self.idx+1, len(self.image_data)-1)
        self.update_image()

    def on_image_scroll_down(self):
        self.idx = max(self.idx-1, 0)
        self.update_image()

    def update_image(self):
        self.image_label.configure(image=self.image_data[self.idx])
