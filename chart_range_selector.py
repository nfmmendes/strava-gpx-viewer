import matplotlib.pyplot as plt
import numpy as np

from matplotlib.widgets import EllipseSelector, RectangleSelector

class ChartRangeSelector:
    def __init__(self, ax, select_callback):
        self._ax = ax

        self._selector = RectangleSelector(
            self._ax, select_callback,
            useblit=True,
            button=[1, 3],  # disable middle button
            minspanx=5, minspany=5,
            spancoords='pixels',
            interactive=True)

        self._selector.set_active(True)