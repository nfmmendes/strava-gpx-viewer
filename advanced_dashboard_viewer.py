import numpy as np
import pandas as pd

from PyQt6.QtWidgets import QWidget, QLabel, QTabWidget, QVBoxLayout
from grade_detailed_dashboard import GradeDetailedDashboard
from speed_detailed_dashboard import SpeedDetailedDashboard


class AdvancedDashboardViewer(QWidget):
    def __init__(self, data_frame):
        super().__init__()
        layout = QVBoxLayout(self)
        self._redraw = False

        tab_widget = QTabWidget()
        tab_widget.addTab(GradeDetailedDashboard(data_frame), "Grade")
        tab_widget.addTab(SpeedDetailedDashboard(data_frame), "Speed")

        layout.addWidget(tab_widget)
        
