"""
_questions_screen.py
11.04.2024

It's literally in the file name, what did you expect?

Author:
Nilusink
"""

import customtkinter as ctk
from icecream import ic
import typing as tp
import random as r
import asyncio
from PIL import ImageTk
from wordcloud import WordCloud
from ._utils import timing
import matplotlib.figure as mpf
import matplotlib.backends.backend_tkagg as mptk


class ResultsCanvas(ctk.CTkFrame):
    def __init__(
            self,
            parent,
            event_loop: asyncio.AbstractEventLoop,
            *args,
            **kwargs
    ) -> None:
        super().__init__(
            parent,
            *args,
            corner_radius=30,
            border_width=0,
            **kwargs
        )
        self.parent = parent
        self._loop = event_loop
        
        # internal ref to wordcloud image, as tk doesn't keep a reference
        self._wc_image: ImageTk.PhotoImage | None = None
        self._wc_image_sprite: int = 0

        # color used as canvas bg, queried from frame color
        self._canvas_bg_color: str = ""
        self._canvas_bg_color_hex: str = ""
        # color used for text, queried from a lable element
        self._canvas_text_color: str = ""
        self._canvas_text_color_hex: str = ""

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # initialize tkinter stuff
        self._init_ui()
    
    def _update_colors(self) -> None:
        """
        Queries the colors from the ctk widgets to figure out what
        to use for a "transparent" canvas and text color in the current
        theme and mode
        """
        fg_color = self._fg_color
        if isinstance(fg_color, str):
            self._canvas_bg_color = fg_color
        else:
            mode = ctk.get_appearance_mode()
            if mode == "Light":
                self._canvas_bg_color = fg_color[0]
            elif mode == "Dark":
                self._canvas_bg_color = fg_color[1]

        if hasattr(self, "_sad_text"):  # not jet initialized right at the beginning
            text_color = self._sad_text._text_color
            if isinstance(text_color, str):
                self._canvas_text_color = text_color
            else:
                mode = ctk.get_appearance_mode()
                if mode == "Light":
                    self._canvas_text_color = text_color[0]
                elif mode == "Dark":
                    self._canvas_text_color = text_color[1]

        # grab color + convert to hex because PIL doesn't know all tkinter color words
        if self._canvas_bg_color != "":
            tuple_color = tuple(c // 255 for c in self.winfo_rgb(self._canvas_bg_color))
            self._canvas_bg_color_hex = "#%02x%02x%02x" % tuple_color
        if self._canvas_text_color != "":
            tuple_color = tuple(c // 255 for c in self.winfo_rgb(self._canvas_text_color))
            self._canvas_text_color_hex = "#%02x%02x%02x" % tuple_color

    def _init_ui(self) -> None:
        """
        create and initialize all ctk widgets
        """
        self._update_colors()

        # Canvas for wordcloud
        self._cloud_canvas = ctk.CTkCanvas(
            self,
            highlightthickness=0,
            bg=self._canvas_bg_color
        )

        # bargraph
        self._bar_figure = mpf.Figure(figsize = (5, 5), dpi = 100) 
        # adding the subplot 
        self._bar_plot = self._bar_figure.add_subplot(111) 
        # plotting the example values  
        #self._bar_plot.barh(["a", "b", "c"], [1, 2, 3])
        # create plotting area on tk window
        self._bar_canvas = mptk.FigureCanvasTkAgg(self._bar_figure, master=self)

        # sad text
        self._sad_text = ctk.CTkLabel(
            self,
            text="=(",
            font=("Arial", 45)
        )
    
    def _place_view(self, canvas: ctk.CTkCanvas | mptk.FigureCanvasTkAgg | ctk.CTkLabel) -> None:
        if canvas is self._cloud_canvas:
            self._sad_text.pack_forget()
            self._bar_canvas.get_tk_widget().pack_forget()
            self._cloud_canvas.pack(
                expand=True,
                fill="both",
                padx=20,
                pady=20
            )
        elif canvas is self._bar_canvas:
            self._sad_text.pack_forget()
            self._cloud_canvas.pack_forget()
            self._bar_canvas.get_tk_widget().pack(
                expand=True,
                fill="both",
                padx=20,
                pady=20
            )
        elif canvas is self._sad_text:
            self._bar_canvas.get_tk_widget().pack_forget()
            self._cloud_canvas.pack_forget()
            self._sad_text.pack(
                expand=True,
                fill="both",
                padx=20,
                pady=20
            )

    def _remove_all_sprites(self) -> None:
        """
        removes all canvas sprites
        """
        for item in self._cloud_canvas.find_all():
            self._cloud_canvas.delete(item)

    def display_word_cloud(self, answers: list[str], valid_answers: list[str]) -> None:
        """
        Generates and displays a weighted word cloud for text answers
        """
        async def defer() -> None:
            # show word canvas
            self._place_view(self._cloud_canvas)
            # get size of canvas
            self._cloud_canvas.update()
            c_width = self._cloud_canvas.winfo_width()
            c_height = self._cloud_canvas.winfo_height()

            # update color values in case theme changed
            self._update_colors()

            # delete any previous image if it is still there
            if self._wc_image_sprite != 0:
                self._cloud_canvas.delete(self._wc_image_sprite)
                self._cloud_canvas.update()
                self._wc_image_sprite = 0
            self._remove_all_sprites()  # all other sprites like text

            # count the frequency of each answer
            words: dict[str, float] = {}
            for a in answers:
                if a in words:
                    words[a] += 1.0
                else:
                    words[a] = 1.0
            ic(words)

            # create new image
            wc = WordCloud(
                background_color=self._canvas_bg_color_hex,
                max_words=1000,
                width=c_width,
                height=c_height - 40    # text is 32
            )
            #wc.generate_from_frequencies({
            #    "hi": 0.5,
            #    "ho": 0.6,
            #    "dfwa": 5.0
            #})

            # https://github.com/amueller/word_cloud/issues/285 
            # order might influence size more then frequency, if max font size is too large
            wc.generate_from_frequencies(words, max_font_size=c_height / 6)

            # convert to tk image and draw on canvas
            self._wc_image = ImageTk.PhotoImage(wc.to_image())
            self._wc_image_sprite = self._cloud_canvas.create_image(
                c_width / 2,        # div 2 because relative to center
                c_height / 2 + 20,  # 20 is half of 40 which is the top border
                image=self._wc_image
            )
            # write the correct answers to the top
            if len(valid_answers) == 0:
                self._cloud_canvas.create_text(c_width / 2, 16, text="(there was no right way)", font=('Arial 32'), fill=self._canvas_text_color)
            if len(valid_answers) == 1:
                self._cloud_canvas.create_text(c_width / 2, 16, text=f"Correct answer: {valid_answers[0]}", font=('Arial 32'), fill=self._canvas_text_color)
            else:
                self._cloud_canvas.create_text(c_width / 2, 16, text=f"Correct answers: {", ".join(valid_answers)}", font=('Arial 32'), fill=self._canvas_text_color)
            
            # just for good measure some update
            self._cloud_canvas.update()
        self._loop.create_task(defer())
    
    def display_bar_graph(self, answers: list[str], possible_answers: list[str], valid_answers: list[str]) -> None:
        """
        Generates and displays a weighted bar chart for selection answers
        """
        async def defer() -> None:
            self._update_colors()

            # count the frequency of each answer
            words: dict[str, int] = {
                p: (answers.count(p)) 
                for p in possible_answers
            }
            ic(words)
            ic(valid_answers)

            # show bar canvas
            self._place_view(self._bar_canvas)
            self._bar_plot.clear()
            barlist = self._bar_plot.barh(
                list(words.keys()),
                list(words.values())
            )
            # maybe wrap text in the future: https://stackoverflow.com/questions/15740682/wrapping-long-y-labels-in-matplotlib-tight-layout-using-setp

            # hide x axis ans top/right/bottom spines
            self._bar_plot.get_xaxis().set_visible(False)
            self._bar_plot.spines["top"].set_visible(False)
            self._bar_plot.spines["right"].set_visible(False)
            self._bar_plot.spines["bottom"].set_visible(False)
            self._bar_plot.spines['left'].set_position(('outward', 10))
            self._bar_plot.spines['left'].set_color(self._canvas_text_color_hex)

            # adjust spacing, color and other formatting
            self._bar_figure.subplots_adjust(left=0.3, right=0.95, top=0.95, bottom=0.05)
            self._bar_plot.tick_params(axis="both", labelsize=32, pad=10, color=self._canvas_text_color_hex, length=0)
            tick_labels = self._bar_plot.get_yticklabels()
            self._bar_plot.set_facecolor(self._canvas_bg_color_hex)
            self._bar_figure.set_facecolor(self._canvas_bg_color_hex)

            # make the correct answers green
            for bar, label in zip(barlist, tick_labels):
                if label.get_text() in valid_answers:  # Adjust the condition based on your needs
                    label.set_color("green")
                    bar.set_color("green")
                else:
                    label.set_color(self._canvas_text_color_hex)
                    bar.set_color("#1f77b4")    # matplotlib default blue

            # add value labels
            for bar in barlist:
                width = bar.get_width()
                ypos = bar.get_y() + bar.get_height() / 2
                self._bar_plot.text(
                    0,
                    ypos,
                    f'   {int(width)}',
                    ha='left',
                    va='center', 
                    color='white', 
                    fontweight='bold',
                    fontsize=32
                )

            
            self._bar_canvas.draw()

        self._loop.create_task(defer())
    
    def display_sad_face(self, valid_answers: list[str]) -> None:
        """
        displays sad face because no one is answering
        """
        self._place_view(self._sad_text)

        if len(valid_answers) == 0:
            self._sad_text.configure(text=f"Awwww =( 😢 nobody answered :(((( 😢\nOh... the correct answer seems to have been lost.\nMaybe it has been consumed by Marco?")
        if len(valid_answers) == 1:
            self._sad_text.configure(text=f"Awwww =( 😢 nobody answered, not even Daniel :(((( 😢\nCorrect answer would have been:\n{valid_answers[0]}")
        else:
            self._sad_text.configure(text=f"Awwww =( 😢 nobody answered, please stay with me Mr. Signitzer :(((( 😢\nCorrect answers would have been:\n{", ".join(valid_answers)}")
