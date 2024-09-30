import pandas as pd
import numpy as np
import datetime

### For embedding in Qt
from PyQt6.QtWidgets import QWidget, QTableView, QLabel, QPushButton, QVBoxLayout, QGridLayout
from PyQt6.QtGui import QWindow

from pandas_model import PandasModel

class DataTableViewer(QWidget):
    def __init__(self, data_frame):
        super().__init__()
        self.resize(700, 700)
        self.setWindowTitle("Data table")
        self.layout = QVBoxLayout()

        model = PandasModel(data_frame)

        view = QTableView()
        view.setModel(model)
        view.resize(800, 600)

        self.layout.addWidget(view)

        self.setLayout(self.layout)
