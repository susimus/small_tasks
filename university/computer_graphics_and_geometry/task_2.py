from typing import Dict, List, Tuple
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
from math import sin, cos, pi


class FuncDrawer:
    _VARS_NAMES: List[str] = ['r_max', 'a', 'b']

    _AXES_INDENT: int = 0
    _COORDINATE_GRID_INDENT: int = 40
    _DASH_HALF_DIAMETER: int = 5
    _VERTICAL_DASH_NUMBER_INDENT: int = 10
    _HORIZONTAL_DASH_NUMBER_INDENT: int = 17

    _GREY_COLOR: str = "#aaaaaa"
    _RED_COLOR: str = "#FF0000"
    _BLUE_COLOR: str = '#0000FF'

    # Coefficients are different to prevent bug when searching loop becomes
    # infinite
    _INCREASING_COEFFICIENT: float = 2
    _DECREASING_COEFFICIENT: float = 3
    _MIN_ANGLE_STEP: float = 10**-3

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
    _r_in_pixel: float

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
            bd=-2)

        self._root.grid_columnconfigure(1, weight=1)
        self._root.grid_rowconfigure(0, weight=1)

        self._canvas.grid(column=1, sticky=NSEW)

    def _init_setup_window(self):
        self._setup_window = Toplevel(master=self._root)

        self._setup_window.resizable(False, False)

        self._func_image = PhotoImage(file="task_2_func.png")
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
        self._canvas_center = (
            self._canvas.winfo_width() // 2, self._canvas.winfo_height() // 2)

        self._draw_horizontal_lines()
        self._draw_vertical_lines()

        self._calculate_scaling()

        self._draw_vertical_scale_divisions()
        self._draw_horizontal_scale_divisions()

    def _draw_horizontal_lines(self):
        self._draw_horizontal_line(
            self._AXES_INDENT,
            self._canvas.winfo_width() - self._AXES_INDENT,
            self._canvas_center[1],
            self._RED_COLOR)

        for i in range(
                1, self._canvas_center[1] // self._COORDINATE_GRID_INDENT + 1):
            self._draw_horizontal_line(
                self._AXES_INDENT,
                self._canvas.winfo_width() - self._AXES_INDENT,
                self._canvas_center[1] + i * self._COORDINATE_GRID_INDENT)
            self._draw_horizontal_line(
                self._AXES_INDENT,
                self._canvas.winfo_width() - self._AXES_INDENT,
                self._canvas_center[1] - i * self._COORDINATE_GRID_INDENT)

    def _draw_vertical_lines(self):
        self._draw_vertical_line(
            self._AXES_INDENT,
            self._canvas.winfo_height() - self._AXES_INDENT,
            self._canvas_center[0],
            self._RED_COLOR)

        for i in range(
                1, self._canvas_center[0] // self._COORDINATE_GRID_INDENT + 1):
            self._draw_vertical_line(
                self._AXES_INDENT,
                self._canvas.winfo_height() - self._AXES_INDENT,
                self._canvas_center[0] + i * self._COORDINATE_GRID_INDENT)
            self._draw_vertical_line(
                self._AXES_INDENT,
                self._canvas.winfo_height() - self._AXES_INDENT,
                self._canvas_center[0] - i * self._COORDINATE_GRID_INDENT)

    def _calculate_scaling(self):
        self._r_in_pixel = (
                self._current_vars_values['r_max']
                / (min(self._canvas.winfo_width(),
                       self._canvas.winfo_height()) // 2))

    def _draw_vertical_scale_divisions(self):
        for i in range(
                1, self._canvas_center[0] // self._COORDINATE_GRID_INDENT + 1):
            self._draw_vertical_line(
                self._canvas_center[1] - self._DASH_HALF_DIAMETER,
                self._canvas_center[1] + self._DASH_HALF_DIAMETER,
                self._canvas_center[0] + i * self._COORDINATE_GRID_INDENT,
                self._RED_COLOR)
            self._draw_vertical_line(
                self._canvas_center[1] - self._DASH_HALF_DIAMETER,
                self._canvas_center[1] + self._DASH_HALF_DIAMETER,
                self._canvas_center[0] - i * self._COORDINATE_GRID_INDENT,
                self._RED_COLOR)

            self._canvas.create_text(
                (self._canvas_center[0] + i * self._COORDINATE_GRID_INDENT,
                 self._canvas_center[1]
                 + self._DASH_HALF_DIAMETER
                 + self._VERTICAL_DASH_NUMBER_INDENT),
                text='{:.2f}'.format(float(self._COORDINATE_GRID_INDENT)
                                     * self._r_in_pixel
                                     * i),
                fill='red')
            self._canvas.create_text(
                (self._canvas_center[0] - i * self._COORDINATE_GRID_INDENT,
                 self._canvas_center[1]
                 + self._DASH_HALF_DIAMETER
                 + self._VERTICAL_DASH_NUMBER_INDENT),
                text='{:.2f}'.format(float(self._COORDINATE_GRID_INDENT)
                                     * self._r_in_pixel
                                     * i),
                fill='red')

    def _draw_horizontal_scale_divisions(self):
        for i in range(
                1, self._canvas_center[1] // self._COORDINATE_GRID_INDENT + 1):
            self._draw_horizontal_line(
                self._canvas_center[0] - self._DASH_HALF_DIAMETER,
                self._canvas_center[0] + self._DASH_HALF_DIAMETER,
                self._canvas_center[1] + i * self._COORDINATE_GRID_INDENT,
                self._RED_COLOR)
            self._draw_horizontal_line(
                self._canvas_center[0] - self._DASH_HALF_DIAMETER,
                self._canvas_center[0] + self._DASH_HALF_DIAMETER,
                self._canvas_center[1] - i * self._COORDINATE_GRID_INDENT,
                self._RED_COLOR)

            scale_division_number: float = (
                float(self._COORDINATE_GRID_INDENT) * self._r_in_pixel * i)

            self._canvas.create_text(
                (self._canvas_center[0]
                 + self._DASH_HALF_DIAMETER
                 + self._HORIZONTAL_DASH_NUMBER_INDENT
                 + ((len(str(int(scale_division_number))) - 1) * 3),
                 self._canvas_center[1] + i * self._COORDINATE_GRID_INDENT),
                text='{:.2f}'.format(scale_division_number),
                fill='red')
            self._canvas.create_text(
                (self._canvas_center[0]
                 + self._DASH_HALF_DIAMETER
                 + self._HORIZONTAL_DASH_NUMBER_INDENT
                 + ((len(str(int(scale_division_number))) - 1) * 3),
                 self._canvas_center[1] - i * self._COORDINATE_GRID_INDENT),
                text='{:.2f}'.format(scale_division_number),
                fill='red')

    def _draw_horizontal_line(
            self, x1: int, x2: int, y: int, color: str = _GREY_COLOR):
        for i in range(x1, x2 + 1):
            self._canvas_image.put(color, (i, y))

    def _draw_vertical_line(
            self, y1: int, y2: int, x: int, color: str = _GREY_COLOR):
        for i in range(y1, y2 + 1):
            self._canvas_image.put(color, (x, i))

    def _draw_func_pixels(self):
        angle: float = 0
        angle_step: float = 0

        # Border is set according with given func
        while angle + angle_step < 2 * pi:
            angle += angle_step
            radius: float = self.get_func_value(
                angle,
                self._current_vars_values['a'],
                self._current_vars_values['b'])
            pixel_position: Tuple[int, int] = (
                self._get_pixel_position_from_func_values(angle, radius))

            if pixel_position[0] < 0 or pixel_position[1] < 0:
                continue

            self._canvas_image.put(self._BLUE_COLOR, pixel_position)

            angle_step = self._get_new_angle_step(angle_step)

    # Improvement: Dynamic step when next pixel is near previous
    def _get_new_angle_step(self, prev_angle_step: float) -> float:
        return self._MIN_ANGLE_STEP

    def _get_pixel_position_from_func_values(
            self, angle: float, radius: float) -> Tuple[int, int]:
        return (self._canvas_center[0]
                + int(radius * cos(angle) / self._r_in_pixel),
                self._canvas_center[1]
                + int(radius * sin(angle) / self._r_in_pixel))

    @staticmethod
    def get_func_value(angle: float, a: float, b: float) -> float:
        return a + b * cos(angle)


if __name__ == "__main__":
    FuncDrawer().init_tkinter()

    mainloop()
