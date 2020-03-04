from typing import Optional
from tkinter import Tk, Canvas, PhotoImage, Label, mainloop
from math import sin


def input_func(_x: float, _a: float, _b: float, _c: float) -> Optional[float]:
    if _b + _x == 0 or _c - _x == 0:
        return None
    else:
        return (_a * _x) / ((_b + _x) * pow(_c - _x, 2))


WIDTH, HEIGHT = 640, 480
window = Tk()

canvas = Canvas(window, width=WIDTH, height=HEIGHT, bg='grey80')
img = PhotoImage(width=WIDTH, height=HEIGHT)

canvas.grid(column=0)
canvas.create_image((WIDTH/2, HEIGHT/2), image=img, state="normal")

for x in range(4 * WIDTH):
    y = int(HEIGHT/2 + HEIGHT/4 * sin(x/80.0))
    img.put("#000000", (x//4, y))

mainloop()
