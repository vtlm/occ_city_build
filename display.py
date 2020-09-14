import random
from OCC.Quantity import Quantity_Color, Quantity_TOC_RGB

__author__ = 'nezx'

OCC_FrontEnd=False
# OCC_FrontEnd = True

if OCC_FrontEnd:
    from OCC.Display.SimpleGui import init_display
    display, start_display, add_menu, add_function_to_menu = init_display()
# display=None


def Display(shapes, material=None, texture=None, color=None, transparency=None, update=False):
    if OCC_FrontEnd:
        display.DisplayShape(shapes, material, texture,
                             color, transparency, update)


def DisplayColored(shapes, color='YELLOW', update=False):
    if OCC_FrontEnd:
        display.DisplayColoredShape(shapes, color, update)


def QuantColor(r, g, b):
    return Quantity_Color(r, g, b, Quantity_TOC_RGB)


def randomColor():
    return Quantity_Color(random.random(), random.random(), random.random(), Quantity_TOC_RGB)
