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
        
        data_frame["Time"] = data_frame["Time"].apply(lambda x: x.strftime('%H:%M:%S'))
        data_frame["Tot. Distance"] = round(data_frame["Tot. Distance"], 2)
        data_frame["Tot. Time"] = data_frame["Tot. Time"].apply(
                lambda x: f'{x.components.hours:02d}:{x.components.minutes:02d}:{x.components.seconds:02d}'
                                  if not pd.isnull(x) else ''
                                  )
        data_frame["Speed"] = round(data_frame["Speed"], 2)
        data_frame["Speed ma"] = round(data_frame["Speed ma"], 2)
        data_frame["Avg Speed"] = round(data_frame["Avg Speed"], 2)

        model = PandasModel(data_frame.drop(columns=["Elevation Gain", "Delta Time"], axis=1))

        view = QTableView()
        view.setModel(model)
        view.resize(800, 600)


        self._export_to_excel_button = QPushButton("Export to excel")
        self._export_to_excel_button.setFixedSize(100, 30)
        self._export_to_excel_button.clicked.connect(self.exportTableToExcel)

        self.layout.addWidget(view)
        self.layout.addWidget(self._export_to_excel_button)

        self.setLayout(self.layout)

    def exportTableToExcel(self):
        print("Export to excel")
