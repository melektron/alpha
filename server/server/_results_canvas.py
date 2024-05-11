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
import asyncio
from PIL import ImageTk
from wordcloud import WordCloud
from ._utils import timing


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

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # initialize tkinter stuff
        self._init_ui()
    
    def _update_bg_color(self) -> None:
        """
        Queries the bg color from the frame to figure out what
        to use for a "transparent" canvas
        """
        color = self._fg_color
        if isinstance(color, str):
            self._canvas_bg_color = color
        else:
            mode = ctk.get_appearance_mode()
            if mode == "Light":
                self._canvas_bg_color = color[0]
            elif mode == "Dark":
                self._canvas_bg_color = color[1]

    def _init_ui(self) -> None:
        """
        create and initialize all ctk widgets
        """
        self._update_bg_color()
        self._results_canvas = ctk.CTkCanvas(
            self,
            highlightthickness=0,
            bg=self._canvas_bg_color
        )
        self._results_canvas.pack(
            expand=True, 
            fill="both", 
            padx=20, 
            pady=20
        )

    def remove_all_sprites(self) -> None:
        """
        removes all canvas sprites
        """
        for item in self._results_canvas.find_all():
            self._results_canvas.delete(item)

    def display_word_cloud(self, answers: list[str] = []) -> None:
        """
        Generates and displays a weighted word cloud for text answers
        """
        async def defer() -> None:
            # get size of canvas
            self._results_canvas.update()
            c_width = self._results_canvas.winfo_width()
            c_height = self._results_canvas.winfo_height()

            # grab color + convert to hex because PIL doesn't know all tkinter color words
            self._update_bg_color()
            tuplecolor = tuple(c // 255 for c in self.winfo_rgb(self._canvas_bg_color))
            hexcolor = "#%02x%02x%02x" % tuplecolor

            # delete any previous image if it is still there
            #if self._wc_image_sprite != 0:
            #    self._results_canvas.delete(self._wc_image_sprite)
            #    self._results_canvas.update()
            #    self._wc_image_sprite = 0
            
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
                background_color=hexcolor,
                max_words=1000,
                width=c_width,
                height=c_height
            )
            #wc.generate_from_frequencies({
            #    "hi": 0.5,
            #    "ho": 0.6,
            #    "dfwa": 5.0
            #})

            # https://github.com/amueller/word_cloud/issues/285 
            # order mgiht influence size more then frequency, if max font size is too large
            wc.generate_from_frequencies(words, max_font_size=c_height / 6)

            # convert to tk image and draw on canvas
            self._wc_image = ImageTk.PhotoImage(wc.to_image())
            self._wc_image_sprite = self._results_canvas.create_image(
                c_width / 2,    # div 2 because relative to center
                c_height / 2,
                image=self._wc_image
            )
            # just for good measure some update
            self._results_canvas.update()
        self._loop.create_task(defer())
