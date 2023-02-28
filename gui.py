import customtkinter as ctk
from helper_functions import DiffLevel
from PIL import ImageTk, Image
import time
import pandas as pd
import numpy as np
import os
import pickle
from pathlib import Path
from sorting_algorithms import *


class TestGui():

    def __init__(self, sort_alg, comparison_size=2):

        #self.sort_alg = sort_alg
        self.comparison_size = comparison_size

        ctk.set_appearance_mode('dark')
        ctk.set_default_color_theme("dark-blue")

        self.root = ctk.CTk()

        w = 1300
        h = 720
        x, y = self.center(w, h)

        self.root.geometry('%dx%d+%d+%d' % (w, h, x, y))
        self.root.title("Rank-Based Annotation")

    def run(self):

        self.populate_menu_screen()

        self.root.mainloop()

    def populate_menu_screen(self):

        self.paths = list(Path("Saves").glob('*.pickle'))

        for child in self.root.winfo_children():
            child.destroy()

        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)

        self.menu_frame = ctk.CTkFrame(master=self.root)
        self.menu_frame.grid(row=0, column=0)

        self.instructions_frame = ctk.CTkFrame(master=self.root)
        self.instructions_frame.grid(row=0, column=1)

        new_button = ctk.CTkButton(
            master=self.menu_frame, text="New Annotation", width=200, height=40, font=('Helvetica bold', 20), command=self.new_annotation)
        delete_button = ctk.CTkButton(
            master=self.menu_frame, text="Delete Annotation", width=200, height=40, font=('Helvetica bold', 20))

        new_button.grid(row=0, column=0, padx=(10, 5), pady=10)
        delete_button.grid(row=0, column=1, padx=(5, 10), pady=10)

        saved_annotations_frame = ctk.CTkScrollableFrame(
            master=self.menu_frame)

        saved_annotations_frame.grid(
            row=1, column=0, columnspan=2, sticky="ew", padx=10, pady=10)

        saved_annotations_frame.columnconfigure(0, weight=1)

        self.display_saves(saved_annotations_frame)

        b = "•"

        text = ctk.CTkLabel(master=self.instructions_frame, text="Welcome to the Rank-Based Annotation program \n   " +
                            b + " Order the images youngest to oldest, left to right \n     " +
                            b + " Specify the difference between two images using the radio buttons", font=('Helvetica bold', 20))

        text.grid(row=0, column=0, padx=10, pady=10)

    def display_saves(self, saved_annotations_frame):

        for i, path in enumerate(self.paths):
            filename, _ = os.path.splitext(os.path.basename(path))
            self.append_row(saved_annotations_frame, i, filename)

    def append_row(self, saved_annotations_frame, index, name):

        saved_annotations_row = ctk.CTkFrame(master=saved_annotations_frame)

        saved_annotations_row.bind(
            "<Button-1>", command=lambda event, i=index: self.load_save(i))

        saved_annotations_row.grid(row=index, column=0, sticky="ew", pady=3)

        save_name_label = ctk.CTkLabel(
            master=saved_annotations_row, text=name, font=('Helvetica bold', 20))
        save_name_label.grid(row=0, column=0, padx=5, pady=2)

    def new_annotation(self):
        pop_out = ctk.CTkToplevel()

        w = 700
        h = 400
        x, y = self.center(w, h)

        pop_out.geometry('%dx%d+%d+%d' % (w, h, x, y))
        pop_out.columnconfigure(index=0, weight=1)
        pop_out.columnconfigure(index=1, weight=2)
        pop_out.rowconfigure(index=0, weight=1)
        pop_out.rowconfigure(index=1, weight=1)
        pop_out.rowconfigure(index=2, weight=1)
        pop_out.rowconfigure(index=3, weight=1)

        self.selected_algorithm = ctk.StringVar()

        ctk.CTkLabel(master=pop_out, text="Name:", font=('Helvetica bold', 20)).grid(
            row=0, column=0, padx=10, pady=(10, 2), sticky="e")

        name = ctk.StringVar()

        ctk.CTkEntry(master=pop_out, textvariable=name,
                     placeholder_text="Enter the name of the annotation session", width=200, height=40, font=('Helvetica bold', 20)).grid(row=0, column=1, padx=10, pady=(10, 2), sticky="w")

        ctk.CTkLabel(master=pop_out, text="Algorithm:", font=('Helvetica bold', 20)).grid(
            row=1, column=0, padx=10, pady=2, sticky="e")

        comp_label = ctk.CTkLabel(
            master=pop_out, text="Comparison Size:", font=('Helvetica bold', 20))

        comp_label.grid(
            row=2, column=0, padx=10, pady=2, sticky="e")

        slider_frame = ctk.CTkFrame(
            master=pop_out, fg_color=pop_out.cget("fg_color"))
        slider_frame.grid(
            row=2, column=1, padx=10, pady=2, sticky="w")

        comparison_count_label = ctk.CTkLabel(master=slider_frame, font=(
            'Helvetica bold', 25))

        slider = ctk.CTkSlider(master=slider_frame, from_=2,
                               to=4, number_of_steps=2, command=lambda val, label=comparison_count_label: self.update_comparison_size(val, label))

        slider.set(2)

        slider.grid(row=0, column=0)

        comparison_count_label.configure(text=int(slider.get()))

        comparison_count_label.grid(row=0, column=1, padx=5)

        algorithm_selection = ctk.CTkOptionMenu(
            master=pop_out, values=["True Skill", "Merge Sort"], width=200, height=40, font=('Helvetica bold', 20), command=lambda value, slider=slider, label=comparison_count_label, comp_label=comp_label: self.algorithm_changed(value, slider, label, comp_label))

        algorithm_selection.grid(
            row=1, column=1, padx=10, pady=2, sticky="w")

        ctk.CTkLabel(master=pop_out, text="Image Directory:", font=('Helvetica bold', 20)).grid(
            row=3, column=0, padx=10, pady=(2, 10), sticky="e")

        image_directory = ctk.StringVar()
        image_directory.set("/Images")
        directory_entry = ctk.CTkEntry(
            master=pop_out, textvariable=image_directory, placeholder_text="select the directory which contains the files", width=400, height=40, font=('Helvetica bold', 16), state=ctk.DISABLED)

        directory_entry.bind("<Button-1>", command=lambda event,
                             image_directory=image_directory: self.select_directory(event, image_directory))

        directory_entry.grid(row=3, column=1, padx=10,
                             pady=(2, 10), sticky="w")

        button_frame = ctk.CTkFrame(
            master=pop_out, fg_color=pop_out.cget("fg_color"))
        button_frame.grid(row=4, column=0, columnspan=2,
                          sticky="ew", pady=(0, 10))

        create_button = ctk.CTkButton(
            master=button_frame, text="Create Annotation", width=200, height=40, font=('Helvetica bold', 20), command=lambda name=name, algorithm_selection=algorithm_selection, slider=slider, image_directory=image_directory, pop_out=pop_out: self.create_save(name, algorithm_selection, slider, image_directory, pop_out))
        delete_button = ctk.CTkButton(
            master=button_frame, text="Cancel", width=200, height=40, font=('Helvetica bold', 20), command=pop_out.destroy)

        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)

        create_button.grid(row=0, column=0, padx=(10, 5), pady=10)
        delete_button.grid(row=0, column=1, padx=(5, 10), pady=10)

        pop_out.grab_set()

    def create_save(self, name, algorithm, comparison_size, image_directory, pop_out):

        directory = image_directory.get()
        final_name = name.get()

        img_paths = [str(path)
                     for path in list(Path(directory).glob('*.jpg'))]
        random.shuffle(img_paths)

        alg = algorithm.get()

        if alg == "Merge Sort":
            sort_alg = MergeSort(data=img_paths)
        else:
            sort_alg = TrueSkill(
                data=img_paths, comparison_size=int(comparison_size.get()))

        file_name = name.get() + "_" + str(int(time.time()))
        save_obj = {"sort_alg": sort_alg, "name": final_name,
                    "image_directory": directory, "path_to_csv": file_name + ".csv"}

        f = open("Saves/" + file_name + ".pickle", "wb")
        pickle.dump(save_obj, f)
        f.close()

        pop_out.destroy()

        self.populate_menu_screen()

    def algorithm_changed(self, value, slider, label, comp_label):

        if value == "Merge Sort":
            slider.set(2)
            label.configure(text=2, state=ctk.DISABLED)
            comp_label.configure(state=ctk.DISABLED)
            slider.configure(state=ctk.DISABLED)
        else:
            slider.configure(state=ctk.NORMAL)
            label.configure(state=ctk.NORMAL)
            comp_label.configure(state=ctk.NORMAL)
            #pop_out.rowconfigure(index=1, weight=0)

    def update_comparison_size(self, val, label):
        label.configure(text=int(val))

    def select_directory(self, event, directory_var):
        directory = ctk.filedialog.askdirectory()
        directory_var.set(directory)
        print(directory)

    def load_save(self, index):
        file = open(self.paths[index], 'rb')

        self.save_obj = pickle.load(file)

        self.sort_alg = self.save_obj["sort_alg"]

        self.comparison_size = self.sort_alg.comparison_size

        self.populate_ordering_screen()

    def populate_ordering_screen(self):

        for child in self.root.winfo_children():
            child.destroy()

        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_rowconfigure(2, weight=2)
        self.root.grid_rowconfigure(3, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)

        self.images_frame = ctk.CTkFrame(master=self.root)
        self.images_frame.grid(row=2, column=0, columnspan=2, padx=0, pady=0)

        self.init_image_frames()

        self.int_diff_levels = [ctk.IntVar(None, 1)
                                for _ in range(self.comparison_size - 1)]

        header = ctk.CTkLabel(
            master=self.root, text="Rank-Based Annotation", font=('Helvetica bold', 40))

        header.grid(row=0, column=0, columnspan=2, sticky="S")

        self.submit_button = ctk.CTkButton(
            master=self.root, text="Submit Ordering", width=280, height=60, command=self.submit_comparison, font=('Helvetica bold', 20))
        self.submit_button.grid(row=3, column=0, columnspan=2, sticky="N")

        self.session_duration_label = ctk.CTkLabel(
            master=self.root, text="0:00", font=('Helvetica bold', 30))
        self.session_duration_label.grid(
            row=1, column=1, sticky='SE', padx=100)

        self.comp_count = 0
        self.comp_count_label = ctk.CTkLabel(
            master=self.root, text=f"Comparison count: {self.comp_count}", font=('Helvetica bold', 30))
        self.comp_count_label.grid(row=1, column=0, sticky='SW', padx=100)

        self.motion_allowed = True

        self.display_comparison(self.sort_alg.get_comparison("1"))

        self.init_diff_level_buttons()

        self.session_start_time = time.time()

        self.root.after(1000, self.update_time)

    def center(self, w, h):
        # get screen width and height
        ws = self.root.winfo_screenwidth()  # width of the screen
        hs = self.root.winfo_screenheight()  # height of the screen

        # calculate x and y coordinates for the Tk root window
        x = (ws/2) - (w/2)
        y = (hs/2) - (h/2) - 40

        return x, y

    def init_image_frames(self):

        self.displayed_images = []
        self.image_frames = []

        for i in range(self.comparison_size):

            image_frame = ctk.CTkFrame(master=self.images_frame)

            self.image_frames.append(image_frame)

            image_frame.grid(row=1, column=i, padx=20, pady=(5, 20))

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

    def init_diff_level_buttons(self):

        diff_levels_frame = ctk.CTkFrame(
            master=self.images_frame)

        diff_levels_frame.grid(
            row=0, column=0, columnspan=self.comparison_size, padx=(20 + 135), pady=(10, 0), sticky="ew")

        for i in range(len(self.int_diff_levels)):
            diff_levels_frame.columnconfigure(i, weight=1)

        for i, int_diff_level in enumerate(self.int_diff_levels):

            diff_level_frame = ctk.CTkFrame(
                master=diff_levels_frame)

            diff_level_frame.grid(row=0, column=i)

            r0 = ctk.CTkRadioButton(
                master=diff_level_frame, variable=int_diff_level, value=0, width=22, text="")
            r1 = ctk.CTkRadioButton(
                master=diff_level_frame, variable=int_diff_level, value=1, width=22, text="")
            r2 = ctk.CTkRadioButton(
                master=diff_level_frame, variable=int_diff_level, value=2, width=22, text="")

            r0.grid(row=1, column=0, padx=(12, 5), pady=2,
                    sticky="ew")
            r1.grid(row=1, column=1, padx=(12, 5), pady=2,
                    sticky="ew")
            r2.grid(row=1, column=2, padx=(12, 5), pady=2,
                    sticky="ew")

            diff_level_label = ctk.CTkLabel(
                text="", master=diff_level_frame, font=('Helvetica bold', 18))
            diff_level_label.grid(row=0, column=0, columnspan=3)

            int_diff_level.trace('w', lambda var, index, mode, int_diff_level=int_diff_level,
                                 label=diff_level_label: self.update_diff_labels(int_diff_level, label))

        diff_levels_frame.configure(
            fg_color=self.images_frame.cget("fg_color"))

    def reset_diff_levels(self):
        for int_diff_lvl in self.int_diff_levels:
            int_diff_lvl.set(1)

    def update_diff_labels(self, int_diff_level, label):
        if int_diff_level.get() == 0:
            label.configure(text="no difference")
        elif int_diff_level.get() == 2:
            label.configure(text="large difference")
        else:
            label.configure(text="")

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
        (min, sec) = divmod(elapsed, 60)
        (hours, min) = divmod(min, 60)

        if hours:
            text_input = '{:02}:{:02}:{:02}'.format(
                int(hours), int(min), int(sec))
        elif min < 10:
            text_input = '{:01}:{:02}'.format(int(min), int(sec))
        else:
            text_input = '{:02}:{:02}'.format(int(min), int(sec))

        self.session_duration_label.configure(text=text_input)

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

        self.drag_frame = frame_clone

    def allow_motion(self):
        self.motion_allowed = True

    def on_drag_motion(self, event, frame, idx):

        if not self.motion_allowed:
            return
        else:
            self.motion_allowed = False
            self.root.after(10, self.allow_motion)

        x = self.images_frame.winfo_x() + frame.winfo_x() + event.x - \
            self.drag_frame.winfo_width()//2

        y = self.images_frame.winfo_y() + frame.winfo_y() + event.y - \
            self.drag_frame.winfo_height()//2

        self.drag_frame.place(x=x, y=y)

        self.root.update_idletasks()

    def on_drag_stop(self, event, frame, idx):

        self.drag_frame.place_forget()
        self.black_frame.place_forget()

        index, row = self.images_frame.grid_location(
            frame.winfo_x() + event.x, event.y)

        if row != 1 or index < 0 or index >= len(self.images) or index == idx:
            return

        widget = self.image_frames[index]

        width = widget.winfo_width()

        # Change 20 to get padx of images_frame
        relative_x = frame.winfo_x() + event.x - widget.winfo_x() + 20

        from_right_bonus = 0

        if (idx > index):
            from_right_bonus = 1

        image_to_move = self.images.pop(idx)
        if relative_x < width // 3:
            self.images.insert(index - 1 + from_right_bonus, image_to_move)
        elif relative_x < 2*width // 3:
            # If you are coming from above, same as lower third
            # If you are coming from below, same as upper third
            if from_right_bonus:
                self.images.insert(index - 1 + from_right_bonus, image_to_move)
            else:
                self.images.insert(index + from_right_bonus, image_to_move)
        else:
            self.images.insert(index + from_right_bonus, image_to_move)

        self.update_images()
        self.reset_diff_levels()

    def submit_comparison(self):
        keys = [key for key, _ in self.images]

        diff_lvls = [DiffLevel(int_diff_lvl.get())
                     for int_diff_lvl in self.int_diff_levels]

        self.sort_alg.inference("1", keys, diff_lvls)

        f = open("Saves/state.pickle", "wb")
        pickle.dump(self.save_obj, f)
        f.close()

        self.save_to_csv_file(keys, diff_lvls)

        self.comp_count += 1
        self.comp_count_label.configure(
            text=f"Comparison count: {self.comp_count}")

        self.is_finished_check()
        self.display_comparison(self.sort_alg.get_comparison("1"))
        self.reset_diff_levels()

    def is_finished_check(self):
        if self.sort_alg.is_finished():
            pop_out = ctk.CTkToplevel()

            w = 700
            h = 300
            x, y = self.center(w, h)

            pop_out.geometry('%dx%d+%d+%d' % (w, h, x, y))
            pop_out.columnconfigure(index=0, weight=1)
            pop_out.columnconfigure(index=1, weight=1)
            pop_out.rowconfigure(index=0, weight=1)
            pop_out.rowconfigure(index=1, weight=1)

            label = ctk.CTkLabel(text="Hello! \n You are now done annotating thank you very much. \n What do you want to do next?",
                                 master=pop_out, font=('Helvetica bold', 30))
            label.grid(row=0, column=0, sticky='nsew', columnspan=2)

            menu_button = ctk.CTkButton(
                text="Return to menu", width=w//2-20, height=h//5, master=pop_out, font=('Helvetica bold', 30))
            menu_button.grid(row=1, column=0, sticky='sew',
                             pady=(0, 10), padx=(10, 5))
            quit_button = ctk.CTkButton(text="Quit", command=self.root.destroy,
                                        width=w//2-20, height=h//5, master=pop_out, font=('Helvetica bold', 30))
            quit_button.grid(row=1, column=1, sticky='sew',
                             pady=(0, 10), padx=(5, 10))

            pop_out.grab_set()

    def save_to_csv_file(self, keys, diff_lvls):
        df = pd.DataFrame({'result': [keys],
                           'diff_levels': [diff_lvls],
                           'time': [time.time()-self.session_start_time],
                           'session': [1],
                           'user': ["1"]})

        output_path = 'data.csv'
        df.to_csv(output_path, mode='a',
                  header=not os.path.exists(output_path))
