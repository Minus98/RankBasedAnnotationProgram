import ast
import json
import os
import sys
from typing import Any, Callable, Optional, Tuple

import customtkinter as ctk
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import utils.convergence as conv
import utils.saves_handler as saves_handler
from widgets.pagination import Pagination


class AdvancedInformationPage():
    """
    Class representing the more advanced information pagewhich allows the user 
    to visualize more information regarding the algorithm
    """

    def __init__(
            self, root: ctk.CTk, save_obj: dict, menu_callback: Callable,
            selected_user: str):
        """
        Initializes the AdvancedInformationPage instance.

        Args:
            root (CTk): The root cutom tkinter object.
            save_obj (dict): The save object containing various parameters.
            menu_callback (function): Callback function to return to the main 
            menu.
            selected_user (str): The currently selected user.
        """

        self.root = root
        self.menu_callback = menu_callback
        self.save_obj = save_obj
        self.selected_user = selected_user

        self.sort_alg = self.save_obj["sort_alg"]

        self.images_per_page = 15
        self.images_per_row = 5

        results = self.sort_alg.get_result()
        self.last_page = len(results) // self.images_per_page
        if len(results) % self.images_per_page > 0:
            self.last_page += 1

        font = {'weight': 'bold',
                'size': 14}

        matplotlib.rc('font', **font)

        self.highlighted_hist = None
        self.bar_label = None
        # self.bar_labels = None

        self.general_info_frame = ctk.CTkFrame(self.root)

        self.tab_view = ctk.CTkTabview(self.root)
        self.tab_view._segmented_button.configure(
            font=('Helvetica bold', 18))

        self.save_name_label = ctk.CTkLabel(
            self.general_info_frame, text=self.save_obj["name"],
            font=('Helvetica bold', 24))

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

        self.dir_path = ""

        if self.images_available(saves_handler.get_full_path(
                self.save_obj["image_directory"])):
            self.dir_path = saves_handler.get_full_path(
                self.save_obj["image_directory"])
        elif self.selected_user:
            if self.selected_user in self.save_obj['user_directory_dict']:
                path = self.save_obj['user_directory_dict'][
                    self.selected_user]

                if os.path.isdir(path):
                    self.dir_path = path

        if self.dir_path:
            self.save_image_count_value.bind(
                "<Button-1>", command=lambda event,
                path=self.dir_path: self.open_folder(path))

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
            self.general_info_frame, text=str(
                comp_count) + "/" + str(max_count),
            font=('Helvetica bold', 20))

        self.scroll_enabled_label = ctk.CTkLabel(
            self.general_info_frame, text="Scrolling:",
            font=('Helvetica bold', 20))

        scroll_text = "Disabled"

        if save_obj["scroll_allowed"]:
            scroll_text = "Enabled"

        self.scroll_enabled_value = ctk.CTkLabel(
            self.general_info_frame, text=scroll_text,
            font=('Helvetica bold', 20))

        self.tab_view.add("Convergence")
        self.generate_convergence_plot()

        alg = type(self.sort_alg).__name__

        if alg == "RatingAlgorithm" or alg == "HybridTrueSkill":
            self.tab_view.add("Rating Distribution")
            self.generate_rating_distribution()

        if alg == "TrueSkill":
            self.tab_view.add("Current Ordering")
            self.generate_ordering_frame()
        elif alg == "HybridTrueSkill":
            if not self.sort_alg.is_rating:
                self.tab_view.add("Current Ordering")
                self.generate_ordering_frame()

        self.menu_button = ctk.CTkButton(
            master=self.root, text="Back to menu", width=250,
            height=45, font=('Helvetica bold', 20),
            command=self.menu_callback)

    def display(self):
        """
        Displays all the fields that should be displayed.
        """

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
        """
        Displays all of the general information fields.
        """

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
        self.scroll_enabled_label.grid(
            row=5, column=0, pady=10, padx=5, sticky="e")
        self.scroll_enabled_value.grid(
            row=5, column=1, pady=10, padx=5, sticky="w")

    def display_convergence(self):
        """
        Displays the convergence tab, including the convergence graph.
        """

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

    def open_folder(self, path: str):
        """
        Opens a folder in the file explorer of the operating system. If the provided 
        folder does not exist, nothing happens.

        Args:
            path (str): The full path to the folder that is to be opened. 
        """
        if os.path.isdir(path):
            if sys.platform == "linux" or sys.platform == "linux2":
                os.system('xdg-open "%s"' % path)
            elif sys.platform == "Darwin" or sys.platform == "darwin":
                os.system('open "%s"' % path)
            else:
                os.startfile(path)

    def hover(self, event: Any):
        """
        Handles the hover effects over the convergence graph.

        Args:
            event (Any): The hover event. 
        """

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

    def update_annot(self, ind: dict):
        """
        Updates the text and location of the convergence graph annotation.

        Args:
            ind (dict): A dict containing information about the x coordinates that are
                        in proximity of the mouse.
        """

        x, y = self.line.get_data()
        self.annot.xy = (x[ind["ind"][0]], y[ind["ind"][0]])
        x_value = int(x[ind["ind"]][0])
        y_value = y[ind["ind"]][0]
        self.annot.set_text("({0}, {1:.2f})".format(x_value, y_value))
        self.annot.get_bbox_patch().set_alpha(0.7)

    def generate_convergence_plot(self):
        """
        Creates the convergence plot.
        """

        self.save_convergence_label = ctk.CTkLabel(
            master=self.tab_view.tab("Convergence"), text="Convergence",
            font=('Helvetica bold', 22))

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

        rmses = conv.get_convergence(self.save_obj)

        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.set_xlabel("Comparisons")
        ax.set_ylabel("RMSE")
        plt.subplots_adjust(bottom=0.15)

        self.line, = ax.plot(rmses)

        canvas = FigureCanvasTkAgg(
            fig, master=self.tab_view.tab("Convergence"))
        canvas.draw()

        self.canvas_widget = canvas.get_tk_widget()

        width, height = canvas.get_width_height()
        self.place_holder_frame = ctk.CTkFrame(
            master=self.tab_view.tab("Convergence"),
            width=width, height=height, corner_radius=0, fg_color="#1a1a1a")

    def generate_ordering_frame(self):
        """
        Creates the list of the current ordering of elements.
        """

        for child in self.tab_view.tab("Current Ordering").winfo_children():
            child.destroy()

        if self.images_available(self.dir_path):
            ordering_frame = Pagination(
                self.tab_view.tab("Current Ordering"),
                self.sort_alg.get_result(),
                self.dir_path,
                image_width=self.root.winfo_screenwidth() // 14)
            ordering_frame.grid(row=0, column=0)
        else:
            could_not_find_images_label = self.get_images_not_found_widget(
                self.tab_view.tab("Current Ordering"))
            could_not_find_images_label.grid(row=0, column=0)

        self.tab_view.tab("Current Ordering").columnconfigure(0, weight=1)
        self.tab_view.tab("Current Ordering").rowconfigure(0, weight=1)

    def generate_rating_distribution(self):
        """
        Creates the rating distribution view.
        """

        for child in self.tab_view.tab("Rating Distribution").winfo_children():
            child.destroy()

        if self.images_available(self.dir_path):

            if "custom_ratings" in self.save_obj:
                self.custom_ratings = self.save_obj["custom_ratings"]
            else:
                with open('prompts.json', 'r') as file:
                    prompts = json.load(file)
                self.custom_ratings = prompts['rating_buttons']

            self.custom_ratings = [
                rating + " (" + str(i) + ")" for i,
                rating in enumerate(self.custom_ratings)]

            color = self.tab_view.tab("Rating Distribution").cget("fg_color")
            ratings_tab_frame = ctk.CTkFrame(
                self.tab_view.tab("Rating Distribution"), fg_color=color)

            self.ratings_menu = ctk.CTkOptionMenu(
                ratings_tab_frame,
                values=self.custom_ratings,
                command=lambda event: self.rating_changed(), width=160)

            csv_path = saves_handler.get_path_to_save(self.save_obj) + ".csv"
            df = pd.read_csv(csv_path, converters={"result": ast.literal_eval})
            ratings_df = df[(df["type"] == "Rating") & (~df["undone"])]

            self.ratings = ratings_df["result"].to_list()
            hist_canvas_widget = self.create_histogram()

            self.rating_frame = Pagination(
                ratings_tab_frame,
                [], self.dir_path, images_per_page=10,
                image_width=self.root.winfo_screenwidth() // 14)

            self.rating_changed()

            self.tab_view.tab("Rating Distribution").rowconfigure(0, weight=4)
            self.tab_view.tab("Rating Distribution").rowconfigure(1, weight=5)

            hist_canvas_widget.grid(row=0, column=0)

            self.ratings_menu.grid(row=0, column=0, sticky="se")

            self.rating_frame.grid(row=1, column=0)
            ratings_tab_frame.grid(row=1, column=0)
        else:

            not_found_widget = self.get_images_not_found_widget(
                self.tab_view.tab("Rating Distribution"))
            not_found_widget.grid(row=0, column=0)

        self.tab_view.tab("Rating Distribution").columnconfigure(0, weight=1)
        self.tab_view.tab("Rating Distribution").rowconfigure(0, weight=1)

    def rating_changed(self):
        """
        Replaces the content of the list of images to match that of the currently 
        selected rating.
        """

        current_selection = self.ratings_menu.get()
        current_rating = self.custom_ratings.index(current_selection)

        filtered_ratings = [
            rating[0] for rating in self.ratings
            if rating[1] == current_rating]

        self.rating_frame.change_data(
            filtered_ratings, image_label=current_rating)

    def images_available(self, path: str) -> bool:
        """
        Checks if all the images of the sorting_algorithm could be found at the provided
        path.

        Args:
            path (str): The path that is to be checked.
        Returns:
            bool: True if all images were found in the provided directory, otherwise
                  false
        """

        return all([os.path.isfile(path + "/" + k)
                    for k in self.save_obj["sort_alg"].data])

    def get_images_not_found_widget(self, parent: ctk.CTkBaseClass):
        """
        Creates and returns a widget that can be used to select the directory containing
        the images of the sorting algorithm.

        Args:
            parent (ctk.CTkBaseClass): The parent widget that is to facilitate the 
                                       widget.
        Returns:
            ctk.CTkFrame: The constructed widget, including a label, a directory entry
                          and a submit button.
        """

        widget = ctk.CTkFrame(parent)

        ctk.CTkLabel(
            widget, text="Images not found", font=('Helvetica bold', 24)).grid(
            row=0, column=0, pady=10, padx=10)

        directory_var = ctk.StringVar()

        directory_entry = ctk.CTkEntry(
            master=widget, textvariable=directory_var,
            placeholder_text="select the directory which contains the files",
            width=500, height=40, font=('Helvetica bold', 16),
            state=ctk.DISABLED)

        submit_button = ctk.CTkButton(
            widget, text="Submit", font=('Helvetica bold', 20),
            command=lambda directory=directory_var: self.submit_directory(
                directory),
            state=ctk.DISABLED, width=160, height=40)

        directory_entry.bind(
            "<Button-1>", command=lambda event, image_directory=directory_var,
            button=submit_button: self.select_directory(
                image_directory, button))

        directory_entry.grid(row=1, column=0, pady=10, padx=10)

        submit_button.grid(row=3, column=0, pady=10, padx=10)

        return widget

    def select_directory(self, directory_var: ctk.StringVar,
                         submit_button: ctk.CTkButton):
        """
        Selects a directory using a file dialog.

        Args:
            event: The event that triggered the callback.
            root (CTk): The root Tk object.
            directory_var (StringVar): The directory.
        """

        directory = ctk.filedialog.askdirectory(
            parent=self.root, initialdir=directory_var.get())

        directory_var.set(directory)

        if self.images_available(directory):
            submit_button.configure(state=ctk.NORMAL)

    def submit_directory(self, directory_var: ctk.StringVar):
        """
        Saves the directory path to the user and refreshes the GUI so that the images
        are fetched.

        Args: 
            directory_var (ctk.StringVar): The string variable containing the path where
                                           the images are located.
        """

        path = directory_var.get()

        self.save_obj['user_directory_dict'][self.selected_user] = path
        saves_handler.save_algorithm_pickle(self.save_obj)

        self.dir_path = path

        alg = type(self.sort_alg).__name__

        if alg == "RatingAlgorithm" or alg == "HybridTrueSkill":
            self.generate_rating_distribution()

        if alg == "TrueSkill":
            self.generate_ordering_frame()
        elif alg == "HybridTrueSkill":
            if not self.sort_alg.is_rating:
                self.generate_ordering_frame()

    def create_histogram(self) -> ctk.CTkCanvas:
        """
        Creates a histogram of the rating distribution.

        Returns:
            Canvas: The generated plot in the form of a canvas. Note that this is
                    actually a tkinter canvas and not a ctk canvas. But the 
                    implementation in the libraries try to obscure this fact.
        """

        fig, ax = plt.subplots()
        fig.set_size_inches(5, 2)
        fig.set_facecolor("#212121")
        ax.set_facecolor("#1a1a1a")
        self.hist_fig = fig

        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.set_ylabel("Amount")
        plt.subplots_adjust(bottom=0.15)

        labels = np.array([r[1] for r in self.ratings])

        left_of_first_bin = -1/2
        right_of_last_bin = (len(self.custom_ratings) * 2 - 1) / 2

        _, _, patches = plt.hist(labels, np.arange(
            left_of_first_bin, right_of_last_bin + 1, 1),
            edgecolor='black', linewidth=1.2)

        plt.xticks(range(len(self.custom_ratings)))
        plt.locator_params(axis='y', nbins=4)

        fig.canvas.mpl_connect(
            "motion_notify_event", lambda event,
            patches=patches: self.hist_hover(event, patches))

        canvas = FigureCanvasTkAgg(
            fig, master=self.tab_view.tab("Rating Distribution"))
        canvas.draw()

        return canvas.get_tk_widget()

    def hist_hover(
            self, event: Any, patches: matplotlib.container.BarContainer):
        """
        Handles the hover effects of the histogram.

        Args:
            event (Any): The hover event.
            patches (matplotlib.container.BarContainer): The bars in the histogram that
                                                         are to be manipulated.
        """
        if event.xdata:
            closest_bin = round(event.xdata)

            if self.highlighted_hist is not None and (
                    closest_bin != self.highlighted_hist):
                patches[self.highlighted_hist].set_fc('#8dd3c7')
                if self.bar_label:
                    self.bar_label.remove()
                    self.bar_label = None
                self.highlighted_hist = None

            if closest_bin >= 0 and closest_bin < len(patches) and (
                    closest_bin != self.highlighted_hist):
                patches[closest_bin].set_fc('#9deddf')

                bar_labels = plt.bar_label(patches)

                for index, bar_label in enumerate(bar_labels):

                    if index != closest_bin:
                        bar_label.remove()
                    else:
                        self.bar_label = bar_label

                self.highlighted_hist = closest_bin
            self.hist_fig.canvas.draw_idle()
