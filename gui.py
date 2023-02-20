import customtkinter as ctk
from PIL import ImageTk, Image
import time
from pathlib import Path


class TestGui():

    def __init__(self):

        ctk.set_appearance_mode('dark')
        ctk.set_default_color_theme("dark-blue")

        img_paths = [str(path) for path in list(Path("Images").glob('*/*.jpg'))]

        image_ids = [90138, 159701, 161513, 164511]

        self.root = ctk.CTk()
        self.root.geometry("1640x720")
        self.root.title("Rank base annotation")

        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=2)
        self.root.grid_rowconfigure(2, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        self.images = [ctk.CTkImage(Image.open(
            img), size=(250, 250)) for img in img_paths[:4]]

        #self.images = [ctk.CTkImage(Image.open(
        #    "Images/" + str(idx) + ".jpg"), size=(250, 250)) for idx in image_ids]

        self.images_frame = ctk.CTkFrame(master=self.root)
        self.images_frame.grid(row=1, column=0, padx=0, pady=0)

        self.init_image_frames()

        self.submit_button = ctk.CTkButton(
            master=self.root, text="Submit Ordering", width=280, height=60, font=('Helvetica bold', 20))
        self.submit_button.grid(row=2, column=0, sticky="N")

        self.session_duration_label = ctk.CTkLabel(
            master=self.root, text="0", font=('Helvetica bold', 30))
        self.session_duration_label.grid(row=0, column=0)

        self.session_start_time = time.time()
        self.root.after(1000, self.update_time)

        self.root.mainloop()

    def init_image_frames(self):

        self.displayed_images = []

        for i, image in enumerate(self.images):

            image_frame = ctk.CTkFrame(master=self.images_frame)
            image_frame.grid(row=0, column=i, padx=20, pady=20)

            displayed_image = ctk.CTkLabel(
                master=image_frame, image=image, text="")

            self.displayed_images.append(displayed_image)

            displayed_image.grid(row=0, column=0, columnspan=2,
                                 sticky="ew", padx=10, pady=10)

            left_button_state = ctk.NORMAL if i != 0 else ctk.DISABLED

            move_left_button = ctk.CTkButton(
                master=image_frame, text="<", width=120, height=36, font=('Helvetica bold', 20), command=lambda i=i: self.move_left(i), state=left_button_state)
            move_left_button.grid(row=1, column=0, padx=(5, 0), pady=(0, 10))

            right_button_state = ctk.NORMAL if i != len(
                self.images) - 1 else ctk.DISABLED

            move_right_button = ctk.CTkButton(
                master=image_frame, text=">", width=120, height=36, font=('Helvetica bold', 20), command=lambda i=i: self.move_right(i), state=right_button_state)
            move_right_button.grid(row=1, column=1, padx=(0, 5), pady=(0, 10))

    def update_images(self):

        for i, image in enumerate(self.images):
            self.displayed_images[i].configure(image=image)

    def move_left(self, index):

        if index > 0:
            self.images[index], self.images[index -
                                            1] = self.images[index - 1], self.images[index]

        self.update_images()

    def move_right(self, index):

        if index < len(self.images) - 1:
            self.images[index], self.images[index +
                                            1] = self.images[index + 1], self.images[index]

        self.update_images()

    def update_time(self):

        current_time = time.time()

        elapsed = int(current_time - self.session_start_time)

        self.session_duration_label.configure(text=elapsed)
        self.root.after(1000, self.update_time)


TestGui()
