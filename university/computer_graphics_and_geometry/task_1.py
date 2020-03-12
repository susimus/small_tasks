from typing import Optional, Dict, List, Tuple
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


class FuncDrawer:
    _VARS_NAMES: List[str] = ['y_abs_max', 'alpha', 'beta', 'a', 'b', 'c']
    _AXES_INDENT: int = 5

    _root: Tk
    _canvas: Canvas
    _canvas_image: PhotoImage

    _setup_window: Toplevel
    _func_image: PhotoImage
    _func_image_label: Label
    _input_labels: Dict[str, Label]
    _input_entries: Dict[str, Entry]
    _draw_button: Button

    _current_vars_values: Dict[str, float]

    _canvas_center: Tuple[int, int]

    def __init__(self):
        self._root = Tk()

        self._current_vars_values = {name: 0 for name in self._VARS_NAMES}

    def init_tkinter(self):
        self._root.minsize(100, 100)

        self._init_setup_window()

        self._init_canvas()

        # self._root.bind(
        #     "<Configure>", lambda event: self._redraw_func(event))

    def _init_canvas(self):
        self._canvas = Canvas(
            self._root,
            width=640,
            height=480,
            bg='grey80',
            bd=-2)

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

        self._input_entries = dict()
        self._input_labels = dict()
        for name in self._VARS_NAMES:
            self._input_labels[name] = (
                Label(master=self._setup_window, text="Ввод " + name))
            self._input_entries[name] = Entry(master=self._setup_window)

            self._input_entries[name].insert(0, "1")

        self._draw_button = Button(
            master=self._setup_window,
            text="Построить график",
            command=self._draw_new_func)

        self._func_image_label.grid(row=0)
        for i, name in enumerate(self._VARS_NAMES):
            self._input_labels[name].grid(row=2 * i + 1)
            self._input_entries[name].grid(row=2 * i + 2)
        self._draw_button.grid(row=len(self._VARS_NAMES) * 2 + 1)

    # def _redraw_func(self, event):
    #     """Draws func if new width or height was given"""
    #     if (event.width != self._canvas_width
    #             or event.height != self._canvas_height):
    #         self._draw_func()

    def _draw_new_func(self):
        """Changes consts and invokes [_draw_func] if consts were changed"""
        consts_were_changed: bool = self._change_consts()

        if consts_were_changed:
            self._draw_func()
        else:
            print("Something is wrong with some entry value")

    def _change_consts(self) -> bool:
        """Changes consts if correct ones were given

        Returns [True] if consts were changed and [False] otherwise
        """
        try:
            for name in self._VARS_NAMES:
                float(self._input_entries[name].get())
        except ValueError:
            return False

        for name in self._VARS_NAMES:
            self._current_vars_values[name] = (
                float(self._input_entries[name].get()))

        return True

    def _draw_func(self):
        self._create_canvas_image()

        self._draw_coordinate_plane()

        self._draw_func_pixels()

    def _create_canvas_image(self):
        self._canvas.delete('all')

        self._canvas_image = PhotoImage(
            width=self._canvas.winfo_width(),
            height=self._canvas.winfo_height())

        # Magical fix of PhotoImage garbage collection
        self._canvas.image = self._canvas_image

        self._canvas.create_image(
            (int(self._canvas.winfo_width()) / 2,
             int(self._canvas.winfo_height()) / 2),
            image=self._canvas.image,
            state="normal")

    def _draw_coordinate_plane(self):
        self.canvas_center = (
            self._canvas.winfo_width() // 2, self._canvas.winfo_height() // 2)

        self._draw_horizontal_lines()

        self._draw_vertical_lines()

    # TODO: _draw_horizontal_lines
    def _draw_horizontal_lines(self):
        for i in range(
                self._AXES_INDENT,
                self._canvas.winfo_width() - self._AXES_INDENT):
            self._canvas_image.put("#000000", (i, self.canvas_center[1]))

        for i in range(1, 10):
            self._canvas_image.put(
                "#000000",
                (self._canvas.winfo_width() - self._AXES_INDENT - i,
                 self.canvas_center[1] - i // 2))
            self._canvas_image.put(
                "#000000",
                (self._canvas.winfo_width() - self._AXES_INDENT - i,
                 self.canvas_center[1] + i // 2))

    # TODO: _draw_vertical_lines
    def _draw_vertical_lines(self):
        pass

    # TODO: _draw_func_pixels
    def _draw_func_pixels(self):
        # for x in range(4 * int(self._canvas.winfo_width())):
        #     y = int(
        #         float(self._canvas.winfo_height()) / 2
        #         + float(self._canvas.winfo_height()) / 4 * sin(x / 80.0))
        #
        #     self._canvas_image.put("#000000", (x // 4, y))
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
