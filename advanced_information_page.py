import os
import random
import sys
from typing import Callable, Optional, Tuple

import customtkinter as ctk
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from utils import get_full_path


class AdvancedInformationPage():
    """
    Class representing the more advanced information pagewhich allows the user 
    to visualize more information regarding the algorithm
    """

    def __init__(
            self, root: ctk.CTk, save_obj: dict, menu_callback: Callable):
        """
        Initializes the AdvancedInformationPage instance.

        Args:
            root (CTk): The root cutom tkinter object.
            menu_callback (function): Callback function to return to the main 
            menu.
        """

        self.root = root
        self.menu_callback = menu_callback
        self.save_obj = save_obj

        font = {'weight': 'bold',
                'size': 14}

        matplotlib.rc('font', **font)

        self.general_info_frame = ctk.CTkFrame(self.root)

        self.tab_view = ctk.CTkTabview(self.root)
        self.tab_view._segmented_button.configure(
            font=('Helvetica bold', 18))

        self.tab_view.add("Convergence")
        self.tab_view.add("Current Ordering")

        self.save_name_label = ctk.CTkLabel(
            self.general_info_frame, text=self.save_obj["name"],
            font=('Helvetica bold', 24))

        self.sort_alg = self.save_obj["sort_alg"]

        self.save_algorithm_label = ctk.CTkLabel(
            self.general_info_frame, text="Algorithm:",
            font=('Helvetica bold', 20))

        self.save_algorithm_value = ctk.CTkLabel(
            self.general_info_frame, text=type(self.sort_alg).__name__,
            font=('Helvetica bold', 20))

        self.save_image_count_label = ctk.CTkLabel(
            self.general_info_frame, text="Images:",
            font=('Helvetica bold', 20))

        self.save_image_count_value = ctk.CTkLabel(
            self.general_info_frame, text=str(len(self.sort_alg.data)),
            font=('Helvetica bold', 20))

        dir_rel_path = ""

        if os.path.isdir(get_full_path(self.save_obj["image_directory"])):
            dir_rel_path = self.save_obj["image_directory"]
        elif self.selected_user:
            if self.selected_user in self.save_obj['user_directory_dict']:
                rel_path = self.save_obj['user_directory_dict'][
                    self.selected_user]

                if os.path.isdir(get_full_path(rel_path)):
                    dir_rel_path = rel_path

        if dir_rel_path:
            self.save_image_count_value.bind(
                "<Button-1>", command=lambda event,
                path=dir_rel_path: self.open_folder(path))
            """
            og_color = self.save_image_count_value.cget("text_color")
            self.save_image_count_value.bind(
                "<Enter>", lambda event,
                og_color=og_color: self.highlight_label(
                    self.save_image_count_value, og_color))
            self.save_image_count_value.bind(
                "<Leave>", lambda event,
                og_color=og_color: self.remove_highlight_label(
                    self.save_image_count_value, og_color))
            """

        comp_count = self.sort_alg.get_comparison_count()

        max_count = self.sort_alg.get_comparison_max()

        self.save_status_label = ctk.CTkLabel(
            self.general_info_frame, text="Status:",
            font=('Helvetica bold', 20))

        text, text_color = self.get_status(comp_count, max_count)

        self.save_status_value = ctk.CTkLabel(
            self.general_info_frame, text=text,
            text_color=text_color, font=('Helvetica bold', 20))

        self.save_comp_count_label = ctk.CTkLabel(
            self.general_info_frame, text="Annotations made:",
            font=('Helvetica bold', 20))

        self.save_comp_count_value = ctk.CTkLabel(
            self.general_info_frame, text=str(comp_count) + "/" + str(max_count),
            font=('Helvetica bold', 20))

        self.save_convergence_label = ctk.CTkLabel(
            master=self.tab_view.tab("Convergence"), text="Convergence",
            font=('Helvetica bold', 22))

        self.generate_convergence_plot()

        self.menu_button = ctk.CTkButton(
            master=self.root, text="Back to menu", width=250,
            height=45, font=('Helvetica bold', 20),
            command=self.menu_callback)

    def display(self):

        self.root.columnconfigure(0, weight=2, uniform="information_page")
        self.root.columnconfigure(1, weight=3, uniform="information_page")
        self.root.rowconfigure(0, weight=8, uniform="information_page")
        self.root.rowconfigure(1, weight=1, uniform="information_page")

        self.general_info_frame.grid(
            row=0, column=0, padx=(20, 10), pady=20, sticky="nesw")

        self.tab_view.grid(
            row=0, column=1, padx=(10, 20), pady=20, sticky="nesw")

        self.display_general_information()

        self.display_convergence()

        self.menu_button.grid(row=1, column=0, columnspan=2)

    def display_general_information(self):

        self.general_info_frame.grid_columnconfigure(
            0, weight=1, uniform="save_info")
        self.general_info_frame.grid_columnconfigure(
            1, weight=1, uniform="save_info")

        self.save_name_label.grid(row=0, column=0, columnspan=2, pady=20)
        self.save_algorithm_label.grid(
            row=1, column=0, pady=10, padx=5, sticky="e")
        self.save_algorithm_value.grid(
            row=1, column=1, pady=10, padx=5, sticky="w")
        self.save_image_count_label.grid(
            row=2, column=0, pady=10, padx=5, sticky="e")
        self.save_image_count_value.grid(
            row=2, column=1, pady=10, padx=5, sticky="w")
        self.save_status_label.grid(
            row=3, column=0, pady=10, padx=5, sticky="e")
        self.save_status_value.grid(
            row=3, column=1, pady=10, padx=5, sticky="w")
        self.save_comp_count_label.grid(
            row=4, column=0, pady=10, padx=5, sticky="e")
        self.save_comp_count_value.grid(
            row=4, column=1, pady=10, padx=5, sticky="w")

    def display_convergence(self):

        self.tab_view.tab("Convergence").columnconfigure(0, weight=1)

        self.save_convergence_label.grid(
            row=0, column=0, pady=(10, 5),
            columnspan=2)

        self.place_holder_frame.grid(
            row=1, column=0, pady=(5, 10))

        # Not a fan of this workaround, but the canvas has not necessarily been drawn
        # when placed on the display, could not find any event to await so instead we
        # use a placeholder for the first 100ms...
        self.root.after(100, lambda: self.replace_placeholder(
            self.place_holder_frame, self.canvas_widget))

    def get_status(self, count: int, max_count: int) -> Tuple[str,
                                                              Optional[str]]:
        """
        Fetches the status of a save in the form of a string as well as color 
        information for that string. 

        Args:
            count (int): The amount of comparisons made.
            max_count (int): The total amount of comparisons allowed.
        Returns:
            Tuple[str, Optional[str]]: The text corresponding to the status of the save
                                       as well as potentially a specific color for the
                                       text.
        """

        if count >= max_count:
            return "Finished", "green"

        return "Ongoing", None

    def replace_placeholder(self, placeholder: ctk.CTkFrame,
                            canvas: ctk.CTkCanvas):
        """
        Function to replace the placeholder frame for flickering workaround.

        Args:
            placeholder (ctk.CTkFrame): The placeholder frame that is to be removed.
            canvas (ctk.CTkCanvas): The Canvas that is to be placed instead.
        """
        placeholder.grid_remove()
        canvas.grid(
            row=1, column=0, pady=(5, 10))

    def open_folder(self, rel_path: str):
        """
        Opens a folder in the file explorer of the operating system. If the provided 
        folder does not exist, nothing happens.

        Args:
            rel_path (str): The relative path to the folder that is to be opened. 
        """
        full_path = get_full_path(rel_path)
        if os.path.isdir(full_path):
            if sys.platform == "linux" or sys.platform == "linux2":
                os.system('xdg-open "%s"' % full_path)
            elif sys.platform == "Darwin":
                os.system('open "%s"' % full_path)
            else:
                os.startfile(full_path)

    def hover(self, event):
        vis = self.annot.get_visible()
        if event.inaxes == self.ax:
            cont, ind = self.line.contains(event)
            if cont:
                self.update_annot(ind)
                self.annot.set_visible(True)
                self.line.set_linewidth(2)
                self.canvas_widget.config(cursor="tcross")
                self.fig.canvas.draw_idle()
            else:
                if vis:
                    self.annot.set_visible(False)
                    self.line.set_linewidth(1)
                    self.canvas_widget.config(cursor="arrow")
                    self.fig.canvas.draw_idle()

    def update_annot(self, ind):
        x, y = self.line.get_data()
        self.annot.xy = (x[ind["ind"][0]], y[ind["ind"][0]])
        x_value = int(x[ind["ind"]][0])
        y_value = y[ind["ind"]][0]
        self.annot.set_text("({0}, {1:.2f})".format(x_value, y_value))
        self.annot.get_bbox_patch().set_alpha(0.7)

    def generate_convergence_plot(self):

        fig, ax = plt.subplots()
        fig.set_size_inches(6, 4)
        fig.set_facecolor("#212121")
        fig.canvas.mpl_connect("motion_notify_event", self.hover)
        ax.set_facecolor("#1a1a1a")
        self.fig = fig
        self.ax = ax
        self.annot = ax.annotate(
            "", xy=(0, 0),
            xytext=(-20, 20),
            textcoords="offset points", bbox=dict(
                boxstyle="round", fc="#1f538d"),
            arrowprops=dict(arrowstyle="simple"))
        self.annot.set_visible(False)

        place_holder_values = [random.randint(1, 6) / np.log(i)
                               for i in np.arange(1.1, 3, 0.1)]

        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.set_xlabel("Comparisons")
        ax.set_ylabel("RMSE")
        plt.subplots_adjust(bottom=0.15)
        # fig.subplots_adjust(hspace=10)

        self.line, = ax.plot(place_holder_values)

        canvas = FigureCanvasTkAgg(
            fig, master=self.tab_view.tab("Convergence"))
        canvas.draw()

        self.canvas_widget = canvas.get_tk_widget()

        width, height = canvas.get_width_height()
        self.place_holder_frame = ctk.CTkFrame(
            master=self.tab_view.tab("Convergence"),
            width=width, height=height, corner_radius=0, fg_color="#1a1a1a")
