import os
from typing import List, Tuple

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
        img = Image.open(img_src)
        if height:
            size = (height, height)
        elif width:
            size = (width, width)
        else:
            size = (img.width, img.height)
        return [ctk.CTkImage(img, size=size)]


def center(root: ctk.CTk, w: int, h: int) -> Tuple[int, int]:
    """
    Calculates the x and y coordinates to center the CTk root window.

    Args:
        root (CTk): The root cutom tkinter object.
        w (int): The width of the window.
        h (int): The height of the window.

    Returns:
        The x and y coordinates to center the window.
    """

    # get screen width and height
    ws = root.winfo_screenwidth()  # width of the screen
    hs = root.winfo_screenheight()  # height of the screen

    # calculate x and y coordinates for the Tk root window
    x = (ws/2) - (w/2)
    y = (hs/2) - (h/2) - 40

    return x, y


def remove_hover(widget: ctk.CTkBaseClass):

    widget.unbind("<Enter>")
    widget.unbind("<Leave>")

    for child in widget.winfo_children():
        remove_hover(child)


def add_hover(widget: ctk.CTkBaseClass):
    """
    Add hover effect to the widget and its children.

    Args:
        widget (CTkBaseClass): The widget to add the hover effect to.
    """

    add_hover_to_children(widget, widget)


def add_hover_to_children(widget: ctk.CTkBaseClass,
                          child_widget: ctk.CTkBaseClass):
    """
    Add hover effect to the child ctk widget and its children.

    Args:
        widget: The parent ctk widget.
        child_widget: The child ctk widget to add the hover effect to.
    """

    child_widget.bind("<Enter>", lambda event, widget=widget,
                      color=widget.cget("fg_color"): highlight(widget, color))
    child_widget.bind(
        "<Leave>", lambda event, widget=widget,
        color=widget.cget("fg_color"): remove_highlight(widget, color))

    for child in child_widget.winfo_children():
        add_hover_to_children(widget, child)


def highlight(widget: ctk.CTkBaseClass, og_color: List[str]):
    """
    Add highlight effect to the ctk widget by changing its foreground color.

    Args:
        widget: The ctk widget to highlight.
        color: The original foreground color of the widget.
    """
    gray_color = int(og_color[1][-2:]) + 10

    if gray_color > 100:
        gray_color = 100

    widget.configure(fg_color='gray' + str((gray_color)))


def remove_highlight(widget: ctk.CTkBaseClass, og_color: List[str]):
    """
    Remove highlight effect from the ctk widget by restoring its original 
    foreground color.

    Args:
        widget: The ctk widget to remove the highlight effect from.
        color: The original foreground color of the widget.

    """
    widget.configure(fg_color=og_color)


def highlight_label(label: ctk.CTkLabel):
    """
    Highlight the label by adjusting its text color.

    Args:
        label (CTkLabel): The widget containing the label to be highlighted.
    """

    hex = label.cget("text_color")

    rgb = [int(hex[i:i+2], 16) for i in (1, 3, 5)]
    for i in range(len(rgb)):
        rgb[i] = min(rgb[i]+50, 255)

    new_hex = '#{:02x}{:02x}{:02x}'.format(rgb[0], rgb[1], rgb[2])
    label.configure(text_color=new_hex)


def remove_highlight_label(label: ctk.CTkLabel):
    """
    Remove the highlight from the label by setting its text color to a 
    default value.

    Args:
        label (CTkLabel): The label from which to remove the highlight.
    """

    label.configure(text_color="#777777")
