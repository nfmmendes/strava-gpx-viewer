import pandas as pd
import numpy as np
import datetime

### For embedding in Qt
from PyQt6.QtWidgets import QWidget, QTableView, QLabel, QPushButton, QVBoxLayout, QFileDialog
from PyQt6.QtGui import QWindow

from pandas_model import PandasModel

class DataTableViewer(QWidget):
    def __init__(self, data_frame):
        super().__init__()
        self.resize(700, 700)
        self.setWindowTitle("Data table")
        self.layout = QVBoxLayout()
        
        self._df = data_frame.copy(deep=True)

        self._df["Time"] = self._df["Time"].apply(lambda x: x.strftime('%H:%M:%S'))
        self._df["Tot. Distance"] = round(self._df["Tot. Distance"], 2)
        self._df["Tot. Time"] = self._df["Tot. Time"].apply(
                lambda x: f'{x.components.hours:02d}:{x.components.minutes:02d}:{x.components.seconds:02d}'
                                  if not pd.isnull(x) else ''
                                  )
        self._df["Speed"] = round(self._df["Speed"], 2)
        self._df["Speed ma"] = round(self._df["Speed ma"], 2)
        self._df["Avg Speed"] = round(self._df["Avg Speed"], 2)

        model = PandasModel(self._df.drop(columns=["Elevation Gain", "Delta Time"], axis=1))

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
        file_name, _ = QFileDialog.getSaveFileName(self, "Export data frame", "", "Excel Files(*.xlsx)")
        if file_name:
            self._df.to_excel(file_name)
