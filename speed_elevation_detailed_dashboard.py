import numpy as np
import pandas as pd
from PyQt6.QtWidgets import QWidget, QTableView, QLabel, QPushButton, QFileDialog, QComboBox, QVBoxLayout, QHBoxLayout

class SpeedElevationDetailedDashboard(QWidget):
    def __init__(self, data_frame):
        super().__init__()

        print(data_frame.columns)
        intervals = np.arange(-10, 10.00001, 2)
        intervals = np.append(np.array([-np.inf]), intervals)
        intervals = np.append(intervals, np.array([np.inf]))
        cuts = pd.cut(100*data_frame["Elevation Gain"]/data_frame["Distance"], intervals)
        new_chart = data_frame[["Elevation Gain", "Distance", "Delta Time"]].groupby(cuts).sum()
        new_chart["Speed 2"] = np.where(new_chart["Delta Time"] > 0, 3.6*new_chart["Distance"]/new_chart["Delta Time"], 0)
        print(new_chart)


