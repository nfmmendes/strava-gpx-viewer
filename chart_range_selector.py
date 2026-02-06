import matplotlib.pyplot as plt
from typing import Callable

from matplotlib.widgets import RectangleSelector
from matplotlib.backend_bases import MouseEvent, MouseButton

class ChartRangeSelector:
    def __init__(self, ax: plt.Axes, select_callback: Callable[[MouseEvent, MouseButton], None]):
        """
        Class constructor.

        :param ax: The axis selected. 
        :type ax: Axes
        :param select_callback: The function to be called after the range selection. 
        :type select_callback: Function[MouseEvent, MouseEvent]
        """
        self._ax = ax
        self._select_callback = select_callback

        self._init_selector()

    def reset(self) -> None:
        """
        Reset the range selection

        :return: None
        :rtype: None
        """
        self._selector = None
        self._init_selector()
    
    def _init_selector(self):
        """
        Init range selection.
        
        :return: None
        :rtype: None
        """
        self._selector = RectangleSelector(
            self._ax, self._select_callback,
            useblit=True,
            button=[1, 3],  # disable middle button
            minspanx=5, minspany=5,
            spancoords='pixels')
        