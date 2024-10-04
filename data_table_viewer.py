import pandas as pd
import numpy as np
import datetime
from math import ceil

### For embedding in Qt
from PyQt6.QtWidgets import QWidget, QTableView, QLabel, QPushButton, QVBoxLayout, QFileDialog, QHBoxLayout
from PyQt6.QtGui import QWindow

from pandas_model import PandasModel
from page_model import PageModel

class DataTableViewer(QWidget):
    def __init__(self, data_frame):
        super().__init__()
        self.resize(700, 700)
        self.setWindowTitle("Data table")
        self.layout = QVBoxLayout()
        
        self._page_size = 50

        self._df = data_frame.copy(deep=True)

        self._number_of_pages = ceil(len(self._df)/self._page_size)
        self._current_page = 0

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

        self._page_model = PageModel(self._page_size, self)
        self._page_model.setSourceModel(model)
        self._page_model.setCurrentPage(self._current_page)

        view = QTableView()
        view.setModel(self._page_model)
        view.resize(800, 600)

        self._first_page_button = QPushButton("First")
        self._first_page_button.setFixedSize(100, 30)
        self._first_page_button.clicked.connect(self.go_to_first_page)

        self._last_page_button = QPushButton("Last")
        self._last_page_button.setFixedSize(100, 30)
        self._last_page_button.clicked.connect(self.go_to_last_page)

        self._next_page_button = QPushButton("Next")
        self._next_page_button.setFixedSize(100, 30)
        self._next_page_button.clicked.connect(self.go_to_next_page)

        self._previous_page_button = QPushButton("Previous")
        self._previous_page_button.setFixedSize(100, 30)
        self._previous_page_button.clicked.connect(self.go_to_previous_page)

        self._export_to_excel_button = QPushButton("Export to excel")
        self._export_to_excel_button.setFixedSize(100, 30)
        self._export_to_excel_button.clicked.connect(self.exportTableToExcel)

        self._pagination_label = QLabel(f"Page {self._current_page + 1} of {self._number_of_pages}")

        pagination_buttons_layout = QHBoxLayout()
        pagination_buttons_layout.addWidget(self._first_page_button)
        pagination_buttons_layout.addWidget(self._previous_page_button)
        pagination_buttons_layout.addWidget(self._pagination_label)
        pagination_buttons_layout.addWidget(self._next_page_button)
        pagination_buttons_layout.addWidget(self._last_page_button)

        self.layout.addWidget(view)
        self.layout.addLayout(pagination_buttons_layout)
        self.layout.addWidget(self._export_to_excel_button)

        self.setLayout(self.layout)

    def go_to_first_page(self):
        self._current_page = 0
        self.render()

    def go_to_last_page(self):
        self._current_page = self._number_of_pages - 1
        self.render()

    def go_to_next_page(self):
        self._current_page = min(self._current_page + 1, self._number_of_pages - 1)
        self.render()

    def go_to_previous_page(self):
        self._current_page = max(0, self._current_page - 1)
        self.render()

    def render(self):
        self._next_page_button.setEnabled(self._current_page < self._number_of_pages - 1)
        self._previous_page_button.setEnabled(self._current_page > 0)

        self._pagination_label.setText(f"Page {self._current_page + 1} of {self._number_of_pages}")

    def exportTableToExcel(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Export data frame", "", "Excel Files(*.xlsx)")
        if file_name:
            self._df.to_excel(file_name)
