import pandas as pd
import numpy as np
import datetime

### For embedding in Qt
from PyQt6.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout, QGridLayout
from PyQt6.QtGui import QWindow

class DataTableViewer(QWindow):
    def __init__(self):
        super().__init__()
        self._main = QWidget()
        self.resize(700, 700)
        self.setTitle("Gpx stats viewer")
        layout = QVBoxLayout(self._main)
