import matplotlib.pyplot as plt
import numpy as np

from matplotlib.widgets import EllipseSelector, RectangleSelector

class ChartRangeSelector:
    def __init__(self, ax, select_callback):
        self._ax = ax
        self._select_callback = select_callback

        self._init_selector()

    def reset(self):
        self._selector = None
        self._init_selector()
    
    def _init_selector(self):
        self._selector = RectangleSelector(
            self._ax, self._select_callback,
            useblit=True,
            button=[1, 3],  # disable middle button
            minspanx=5, minspany=5,
            spancoords='pixels')
        