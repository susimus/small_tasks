from typing import Optional
from tkinter import (
    Tk,
    Canvas,
    PhotoImage,
    Label,
    Entry,
    Toplevel,
    Button,
    mainloop,
    NSEW)
from math import sin


class FuncDrawer:
    _root: Tk
    _setup_window: Toplevel

    _func_image: PhotoImage
    _func_image_label: Label
    _alpha_input_label: Label
    _beta_input_label: Label
    _a_input_label: Label
    _b_input_label: Label
    _c_input_label: Label
    _draw_button: Button

    _alpha_input_entry: Entry
    _beta_input_entry: Entry
    _a_input_entry: Entry
    _b_input_entry: Entry
    _c_input_entry: Entry

    _canvas: Canvas
    _canvas_height: int
    _canvas_width: int

    def __init__(self):
        self._root = Tk()

    def init_tkinter(self):
        self._init_setup_window()

        self._init_canvas()

        self._root.bind(
            "<Configure>", lambda event: self._redraw_func(event))

    def _init_canvas(self):
        self._canvas_width = 640
        self._canvas_height = 480

        self._canvas = Canvas(
            self._root,
            width=self._canvas_width,
            height=self._canvas_height,
            bg='grey80')

        self._root.grid_columnconfigure(1, weight=1)
        self._root.grid_rowconfigure(0, weight=1)

        self._canvas.grid(column=1, sticky=NSEW)

    def _init_setup_window(self):
        self._setup_window = Toplevel(master=self._root)

        self._setup_window.resizable(False, False)

        self._func_image = PhotoImage(file="task_1_func.png")
        self._func_image_label = Label(
            master=self._setup_window, image=self._func_image)

        # This fixes image disappearing
        self._func_image_label.image = self._func_image

        self._alpha_input_label = Label(
            master=self._setup_window, text="Ввод α")
        self._beta_input_label = Label(
            master=self._setup_window, text="Ввод β")
        self._a_input_label = Label(master=self._setup_window, text="Ввод a")
        self._b_input_label = Label(master=self._setup_window, text="Ввод b")
        self._c_input_label = Label(master=self._setup_window, text="Ввод c")

        self._alpha_input_entry = Entry(master=self._setup_window)
        self._beta_input_entry = Entry(master=self._setup_window)
        self._a_input_entry = Entry(master=self._setup_window)
        self._b_input_entry = Entry(master=self._setup_window)
        self._c_input_entry = Entry(master=self._setup_window)

        self._draw_button = Button(
            master=self._setup_window,
            text="Построить график",
            command=self._draw_new_func)

        self._func_image_label.grid(row=0)
        self._alpha_input_label.grid(row=1)
        self._alpha_input_entry.grid(row=2)
        self._beta_input_label.grid(row=3)
        self._beta_input_entry.grid(row=4)
        self._a_input_label.grid(row=5)
        self._a_input_entry.grid(row=6)
        self._b_input_label.grid(row=7)
        self._b_input_entry.grid(row=8)
        self._c_input_label.grid(row=9)
        self._c_input_entry.grid(row=10)
        self._draw_button.grid(row=11)

    # TODO: _draw_func
    def _draw_new_func(self):
        img = PhotoImage(width=self._canvas_width, height=self._canvas_height)

        self._canvas.create_image(
            (self._canvas_width / 2, self._canvas_height / 2),
            image=img,
            state="normal")

        self._canvas.image = img

        for x in range(4 * self._canvas_width):
            y = int(
                self._canvas_height / 2
                + self._canvas_height / 4 * sin(x / 80.0))

            img.put("#000000", (x // 4, y))

    # TODO: _redraw_func
    def _redraw_func(self, event):
        # TODO: If same width & height then do nothing

        # TODO: Delete 4 pixels of padding. Now it is not 640x480 but 644x484

        pass

    @staticmethod
    def get_func_value(
            _x: float,
            _a: float,
            _b: float,
            _c: float) -> Optional[float]:
        if _b + _x == 0 or _c - _x == 0:
            return None
        else:
            return (_a * _x) / ((_b + _x) * pow(_c - _x, 2))


if __name__ == "__main__":
    FuncDrawer().init_tkinter()

    mainloop()
