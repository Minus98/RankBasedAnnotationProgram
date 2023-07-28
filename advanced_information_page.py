import ast
import json
import os
import sys
from typing import Any, Callable, Optional, Tuple

import customtkinter as ctk
import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import convergence as conv
import ctk_utils
import utils


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
            save_obj (dict): The save object containing various parameters.
            menu_callback (function): Callback function to return to the main 
            menu.
        """

        self.root = root
        self.menu_callback = menu_callback
        self.save_obj = save_obj

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

        self.dir_rel_path = ""

        if os.path.isdir(utils.get_full_path(
                self.save_obj["image_directory"])):
            self.dir_rel_path = self.save_obj["image_directory"]
        elif self.selected_user:
            if self.selected_user in self.save_obj['user_directory_dict']:
                rel_path = self.save_obj['user_directory_dict'][
                    self.selected_user]

                if os.path.isdir(utils.get_full_path(rel_path)):
                    self.dir_rel_path = rel_path

        if self.dir_rel_path:
            self.save_image_count_value.bind(
                "<Button-1>", command=lambda event,
                path=self.dir_rel_path: self.open_folder(path))

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

        alg = type(self.sort_alg).__name__
        if alg == "TrueSkill":
            self.display_current_ordering()
        elif alg == "RatingAlgorithm":
            self.display_rating_distribution()
        elif alg == "HybridTrueSkill":
            self.display_rating_distribution()
            if not self.sort_alg.is_rating:
                self.display_current_ordering()

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

    def display_current_ordering(self):
        """
        Displays the current ordering tab.
        """

        self.tab_view.tab("Current Ordering").columnconfigure(0, weight=1)
        self.tab_view.tab("Current Ordering").rowconfigure(0, weight=5)
        self.tab_view.tab("Current Ordering").rowconfigure(0, weight=1)

        self.images_frame.grid(row=0, column=0)

    def display_rating_distribution(self):
        """
        Displays the rating distribution tab.
        """

        self.tab_view.tab("Rating Distribution").columnconfigure(0, weight=1)
        self.tab_view.tab("Rating Distribution").rowconfigure(0, weight=1)
        self.tab_view.tab("Rating Distribution").rowconfigure(1, weight=5)

        self.ratings_menu.grid(row=0, column=0, sticky="e")
        self.ratings_frame.grid(row=1, column=0)

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
        full_path = utils.get_full_path(rel_path)
        if os.path.isdir(full_path):
            if sys.platform == "linux" or sys.platform == "linux2":
                os.system('xdg-open "%s"' % full_path)
            elif sys.platform == "Darwin" or sys.platform == "darwin":
                os.system('open "%s"' % full_path)
            else:
                os.startfile(full_path)

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

    def update_annot(self, ind):
        """

        """
        x, y = self.line.get_data()
        self.annot.xy = (x[ind["ind"][0]], y[ind["ind"][0]])
        x_value = int(x[ind["ind"]][0])
        y_value = y[ind["ind"]][0]
        self.annot.set_text("({0}, {1:.2f})".format(x_value, y_value))
        self.annot.get_bbox_patch().set_alpha(0.7)

    def generate_convergence_plot(self):

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
        # fig.subplots_adjust(hspace=10)

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

        self.images_frame = ctk.CTkFrame(
            master=self.tab_view.tab("Current Ordering"))

        pagination_widget = self.create_pagination_widget()
        pagination_widget.grid(row=1, column=0)
        self.load_page(1)

    def create_pagination_widget(self):

        pagination_frame = ctk.CTkFrame(
            master=self.tab_view.tab("Current Ordering"))

        self.current_page = ctk.StringVar(value=1)

        previous_page_button = ctk.CTkButton(
            master=pagination_frame, text="<", width=35, height=35,
            font=('Helvetica bold', 20),
            command=self.decrement_page)

        next_page_button = ctk.CTkButton(
            master=pagination_frame, text=">", width=35, height=35,
            font=('Helvetica bold', 20),
            command=self.increment_page)

        vcmd = (self.root.register(self.validate_number), '%P')

        current_page_entry = ctk.CTkEntry(
            master=pagination_frame, width=35, height=35,
            font=('Helvetica bold', 16), justify="center", validate='key',
            validatecommand=vcmd,
            textvariable=self.current_page)

        current_page_entry.bind("<Return>", lambda event: self.page_changed())

        max_page_label = ctk.CTkLabel(
            master=pagination_frame, text="of " + str(self.last_page),
            font=('Helvetica bold', 16))

        previous_page_button.grid(row=0, column=0, padx=5, pady=3)
        current_page_entry.grid(row=0, column=1, padx=(5, 2), pady=3)
        max_page_label.grid(row=0, column=2, padx=(2, 5), pady=3)
        next_page_button.grid(row=0, column=3, padx=5, pady=3)

        return pagination_frame

    def validate_number(self, value: str):
        """
        Validation function used to see if entry contains an integer.

        Args:
            value (str): The string that is to be validated.
        """
        return value.isnumeric() or not value

    def increment_page(self):
        self.current_page.set(

            int(self.current_page.get()) + 1)

        self.page_changed()

    def decrement_page(self):
        self.current_page.set(
            int(self.current_page.get()) - 1)

        self.page_changed()

    def page_changed(self):

        page = int(self.current_page.get())

        if page < 1:
            self.current_page.set(1)
            page = 1
        elif page > self.last_page:
            self.current_page.set(self.last_page)
            page = self.last_page

        self.load_page(page)

    def load_page(self, page_number):

        for child in self.images_frame.winfo_children():
            child.destroy()

        ordered_results = self.sort_alg.get_result()

        start_index = self.images_per_page*(page_number-1)

        images_to_show = ordered_results[start_index: start_index +
                                         self.images_per_page]

        dir_path = utils.get_full_path(self.dir_rel_path)
        image_height = self.root.winfo_screenheight()/8

        for index, img_src in enumerate(images_to_show):
            full_img_path = dir_path + "/" + img_src
            image = ctk_utils.file_2_CTkImage(
                full_img_path, image_height)[0]
            preview_image = ctk.CTkLabel(
                self.images_frame, image=image, text="")
            preview_image.grid(row=index//self.images_per_row,
                               column=index % self.images_per_row, padx=3, pady=3)

            img_label = ctk.CTkLabel(
                master=preview_image, text=start_index + index + 1,
                font=('Helvetica bold', 18),
                width=25, height=25, bg_color=self.images_frame.cget(
                    'fg_color'))
            img_label.place(relx=0, rely=1,
                            anchor="sw")

    def generate_rating_distribution(self):

        if "custom_ratings" in self.save_obj:
            self.custom_ratings = self.save_obj["custom_ratings"]
        else:
            with open('prompts.json', 'r') as file:
                prompts = json.load(file)
            self.custom_ratings = prompts['rating_buttons']

        self.ratings_menu = ctk.CTkOptionMenu(
            self.tab_view.tab("Rating Distribution"),
            values=self.custom_ratings,
            command=lambda event: self.load_rating_page(1))

        self.ratings_frame = ctk.CTkFrame(
            self.tab_view.tab("Rating Distribution"))

        # pd.read_csv()
        csv_path = utils.get_full_path(self.save_obj["path_to_save"] + ".csv")
        df = pd.read_csv(csv_path, converters={"result": ast.literal_eval})

        ratings_df = df[(df["type"] == "Rating") & (~df["undone"])]

        self.ratings = ratings_df["result"].to_list()
        self.load_rating_page(1)

    def load_rating_page(self, page_number):

        for child in self.ratings_frame.winfo_children():
            child.destroy()

        current_selection = self.ratings_menu.get()
        current_rating = self.custom_ratings.index(current_selection)

        filtered_ratings = [
            rating[0] for rating in self.ratings
            if rating[1] == current_rating]

        start_index = self.images_per_page*(page_number-1)

        images_to_show = filtered_ratings[start_index: start_index +
                                          self.images_per_page]

        dir_path = utils.get_full_path(self.dir_rel_path)
        image_height = self.root.winfo_screenheight()/8

        for index, img_src in enumerate(images_to_show):
            full_img_path = dir_path + "/" + img_src
            image = ctk_utils.file_2_CTkImage(
                full_img_path, image_height)[0]
            preview_image = ctk.CTkLabel(
                self.ratings_frame, image=image, text="")
            preview_image.grid(row=index//self.images_per_row,
                               column=index % self.images_per_row, padx=3, pady=3)

            img_label = ctk.CTkLabel(
                master=preview_image, text=current_rating,
                font=('Helvetica bold', 18),
                width=25, height=25, bg_color=self.ratings_frame.cget(
                    'fg_color'))
            img_label.place(relx=0, rely=1,
                            anchor="sw")
