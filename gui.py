import customtkinter as ctk
from helper_functions import DiffLevel
from PIL import ImageTk, Image
import time
import numpy as np
import pickle


class TestGui():

    def __init__(self, sort_alg, comparison_size=2):

        self.sort_alg = sort_alg
        self.comparison_size = comparison_size

        ctk.set_appearance_mode('dark')
        ctk.set_default_color_theme("dark-blue")

        self.root = ctk.CTk()
        self.root.geometry("1640x720")
        self.root.title("Rank base annotation")

        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=2)
        self.root.grid_rowconfigure(2, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        self.images_frame = ctk.CTkFrame(master=self.root)
        self.images_frame.grid(row=1, column=0, padx=0, pady=0)

        self.init_image_frames()

        self.submit_button = ctk.CTkButton(
            master=self.root, text="Submit Ordering", width=280, height=60, command=self.submit_comparison, font=('Helvetica bold', 20))
        self.submit_button.grid(row=2, column=0, sticky="N")

        self.session_duration_label = ctk.CTkLabel(
            master=self.root, text="0", font=('Helvetica bold', 30))
        self.session_duration_label.grid(row=0, column=0)

    def run(self):
        self.session_start_time = time.time()
        self.root.after(1000, self.update_time)

        self.display_comparison(self.sort_alg.get_comparison("1"))
        self.root.mainloop()

    def init_image_frames(self):

        self.displayed_images = []

        for i in range(self.comparison_size):

            image_frame = ctk.CTkFrame(master=self.images_frame)
            image_frame.grid(row=0, column=i, padx=20, pady=20)

            displayed_image = ctk.CTkLabel(
                master=image_frame, text="")

            self.displayed_images.append(displayed_image)

            displayed_image.grid(row=0, column=0, columnspan=2,
                                 sticky="ew", padx=10, pady=10)

            left_button_state = ctk.NORMAL if i != 0 else ctk.DISABLED

            move_left_button = ctk.CTkButton(
                master=image_frame, text="<", width=120, height=36, font=('Helvetica bold', 20), command=lambda i=i: self.move_left(i), state=left_button_state)
            move_left_button.grid(row=1, column=0, padx=(5, 0), pady=(0, 10))

            right_button_state = ctk.NORMAL if i != self.comparison_size - 1 else ctk.DISABLED

            move_right_button = ctk.CTkButton(
                master=image_frame, text=">", width=120, height=36, font=('Helvetica bold', 20), command=lambda i=i: self.move_right(i), state=right_button_state)
            move_right_button.grid(row=1, column=1, padx=(0, 5), pady=(0, 10))

            image_frame.bind("<Button-1>", command=lambda event, image_frame=image_frame,
                             i=i: self.on_drag_start(event, image_frame, i))
            image_frame.bind("<B1-Motion>", command=lambda event, image_frame=image_frame,
                             i=i: self.on_drag_motion(event, image_frame, i))
            image_frame.bind("<ButtonRelease-1>", command=lambda event, image_frame=image_frame,
                             i=i: self.on_drag_stop(event, image_frame, i))

            displayed_image.bind("<Button-1>", command=lambda event,
                                 image_frame=image_frame, i=i: self.on_drag_start(event, image_frame, i))
            displayed_image.bind("<B1-Motion>", command=lambda event, image_frame=image_frame,
                                 i=i: self.on_drag_motion(event, image_frame, i))
            displayed_image.bind("<ButtonRelease-1>", command=lambda event, image_frame=image_frame,
                                 i=i: self.on_drag_stop(event, image_frame, i))

    def create_image_widget(self, image_idx):
        image_frame = ctk.CTkFrame(
            master=self.root)

        img = self.displayed_images[image_idx].cget("image")

        displayed_image = ctk.CTkLabel(
            master=image_frame, text="", image=img)

        displayed_image.grid(row=0, column=0, columnspan=2,
                             sticky="ew", padx=10, pady=10)

        move_left_button = ctk.CTkButton(
            master=image_frame, text="<", width=120, height=36, font=('Helvetica bold', 20), state=ctk.DISABLED)
        move_left_button.grid(row=1, column=0, padx=(5, 0), pady=(0, 10))

        move_right_button = ctk.CTkButton(
            master=image_frame, text=">", width=120, height=36, font=('Helvetica bold', 20), state=ctk.DISABLED)
        move_right_button.grid(row=1, column=1, padx=(0, 5), pady=(0, 10))

        return image_frame

    def display_comparison(self, keys):
        print(keys)
        self.images = [(img, ctk.CTkImage(Image.open(img), size=(250, 250)))
                       for img in keys]
        self.update_images()

    def update_images(self):

        for i, img_tuple in enumerate(self.images):
            self.displayed_images[i].configure(image=img_tuple[1])

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

    def on_drag_start(self, event, frame, idx):

        self.black_frame = ctk.CTkFrame(master=self.images_frame, width=frame.winfo_width(
        ), height=frame.winfo_height())

        self.black_frame.place(x=frame.winfo_x(), y=frame.winfo_y())

        pos_x = self.images_frame.winfo_x() + frame.winfo_x() + event.x
        pos_y = self.images_frame.winfo_y() + frame.winfo_y() + event.y

        dx = frame.winfo_width()//2
        dy = frame.winfo_height()//2

        frame_clone = self.create_image_widget(idx)
        frame_clone.place(x=pos_x-dx, y=pos_y-dy)
        frame_clone.focus_set()

        self.drag_frame = frame_clone

    def on_drag_motion(self, event, frame, idx):

        x = self.images_frame.winfo_x() + frame.winfo_x() + event.x - \
            self.drag_frame.winfo_width()//2

        y = self.images_frame.winfo_y() + frame.winfo_y() + event.y - \
            self.drag_frame.winfo_height()//2

        self.drag_frame.place(x=x, y=y)

    def on_drag_stop(self, event, frame, idx):

        # Check if inside images_frame
        # If not, we do not try to move

        self.drag_frame.place_forget()
        self.black_frame.place_forget()

    def submit_comparison(self):
        keys = [key for key, _ in self.images]
        diff_lvls = np.full(len(keys)-1, DiffLevel.normal)

        self.sort_alg.inference("1", keys, diff_lvls)

        f = open("state.pickle", "wb")

        pickle.dump(self.sort_alg, f)

        f.close()

        self.display_comparison(self.sort_alg.get_comparison("1"))
