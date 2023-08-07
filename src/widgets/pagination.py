import math
from typing import List, Optional

import customtkinter as ctk

import utils.ctk_utils as ctk_utils
from pop_outs.image_pop_out import ImagePopOut


class Pagination(ctk.CTkFrame):
    """
    A widget used to display images using pagination.
    """

    def __init__(
            self, root: ctk.CTk, master: ctk.CTkBaseClass, data: List[str],
            src_dir: str, images_per_row: int = 5, images_per_page: int = 15,
            image_width=130, image_label: Optional[int] = None):
        """
        Initialize the Pagination.

        Args:
            root (CTk): The root cutom tkinter object.
            master (ctk.CtkBaseClass): The parent ctk widget.
            data (List[str]): A list containint the filenames of the images that are to 
                              be shown.
            src_dir (str): The path to the directory containing the images.
            images_per_row (int): The amount of images that should be shown on a single 
                                  row.
            images_per_page (int): The amount of images that should be contained within
                                   one page.
            image_width (int): The width each image should have.
            image_label (Optional[int]): The label the images should have in the bottom
                                         left corner. Defaults to displaying the rank of
                                         the elements in the provided list.
        """

        ctk.CTkFrame.__init__(self, master)

        self.root = root
        self.master = master
        self.data = data
        self.src_dir = src_dir
        self.images_per_page = images_per_page
        self.images_per_row = images_per_row
        self.last_page = math.ceil(len(data) / self.images_per_page)
        self.image_width = image_width

        self.image_label = image_label

        self.current_page = ctk.StringVar(value=1)

        self.configure(fg_color=master.cget('fg_color'))

        self.current_page = ctk.StringVar(value=1)

        self.images_frame = ctk.CTkFrame(master=self)

        self.create_pagination_controls()

        for i in range(self.images_per_row):
            self.images_frame.columnconfigure(
                i, weight=1, uniform="images_frame")

        for i in range(math.ceil(self.images_per_page/self.images_per_row)):
            self.images_frame.rowconfigure(
                i, weight=1, uniform="images_frame")

        self.images_frame.grid(row=0, column=0, pady=5)
        self.pagination_controls.grid(row=1, column=0, pady=5)

        self.load_page(1)

    def load_page(self, page_number: int):
        """
        Loads the list of images corresponding to the pagenumber.

        Args:
            page_number (int): The page of images that should be shown.
        """

        for child in self.images_frame.winfo_children():
            child.destroy()

        start_index = self.images_per_page*(page_number-1)

        images_to_show = self.data[start_index: start_index +
                                   self.images_per_page]

        for index, img_src in enumerate(images_to_show):
            full_img_path = self.src_dir + "/" + img_src
            image = ctk_utils.file_2_CTkImage(
                full_img_path, width=self.image_width)[0]

            preview_image_frame = ctk.CTkFrame(self.images_frame)

            preview_image = ctk.CTkLabel(
                preview_image_frame, image=image, text="")
            preview_image.grid(row=0, column=0, padx=5, pady=5)
            preview_image_frame.grid(row=index//self.images_per_row,
                                     column=index % self.images_per_row, padx=3, pady=3)

            preview_image.bind(
                "<Button-1>", command=lambda event,
                full_img_path=full_img_path: self.on_image_press(
                    event, full_img_path))

            if self.image_label is not None:
                label = self.image_label
            else:
                label = start_index + index + 1

            img_label = ctk.CTkLabel(
                master=preview_image, text=label,
                font=('Helvetica bold', 18),
                width=25, height=25, bg_color=preview_image_frame.cget(
                    'fg_color'))
            img_label.place(relx=0, rely=1,
                            anchor="sw")

    def on_image_press(self, event, full_img_path):
        ImagePopOut(self.root, full_img_path)

    def create_pagination_controls(self):
        """
        Creates the pagination control buttons and entry field.
        """

        self.pagination_controls = ctk.CTkFrame(
            master=self)

        previous_page_button = ctk.CTkButton(
            master=self.pagination_controls, text="<", width=35, height=35,
            font=('Helvetica bold', 20),
            command=self.decrement_page)

        next_page_button = ctk.CTkButton(
            master=self.pagination_controls, text=">", width=35, height=35,
            font=('Helvetica bold', 20),
            command=self.increment_page)

        vcmd = (self.register(self.validate_number), '%P')

        current_page_entry = ctk.CTkEntry(
            master=self.pagination_controls, width=35, height=35,
            font=('Helvetica bold', 16), justify="center", validate='key',
            validatecommand=vcmd,
            textvariable=self.current_page)

        current_page_entry.bind("<Return>", lambda event: self.page_changed())

        self.max_page_label = ctk.CTkLabel(
            master=self.pagination_controls, text="of " + str(self.last_page),
            font=('Helvetica bold', 16))

        previous_page_button.grid(row=0, column=0, padx=5, pady=3)
        current_page_entry.grid(row=0, column=1, padx=(5, 2), pady=3)
        self.max_page_label.grid(row=0, column=2, padx=(2, 5), pady=3)
        next_page_button.grid(row=0, column=3, padx=5, pady=3)

    def validate_number(self, value: str):
        """
        Validation function used to see if entry contains an integer.

        Args:
            value (str): The string that is to be validated.
        """
        return value.isnumeric() or not value

    def increment_page(self):
        """
        Increases the current page number by 1.
        """

        self.current_page.set(
            int(self.current_page.get()) + 1)

        self.page_changed()

    def decrement_page(self):
        """
        Decreases the current page number by 1.
        """

        self.current_page.set(
            int(self.current_page.get()) - 1)

        self.page_changed()

    def page_changed(self):
        """
        Corrects non-compatible page numbers and loads the correct page.
        """

        page = int(self.current_page.get())

        if page < 1:
            self.current_page.set(1)
            page = 1
        elif page > self.last_page:
            self.current_page.set(self.last_page)
            page = self.last_page

        self.load_page(page)

    def change_data(self, data: List[str], image_label: Optional[int] = None):
        """
        Changes the images that the widget displays.

        Args:
            data (List[str]): The filenames of the images that should be shown.
            image_label (Optional[int]): The number that should be displayed in the
                                         bottom left corner.
        """

        self.data = data
        self.last_page = math.ceil(len(data) / self.images_per_page)
        self.max_page_label.configure(text="of " + str(self.last_page))
        self.image_label = image_label

        self.current_page.set(1)
        self.load_page(1)
