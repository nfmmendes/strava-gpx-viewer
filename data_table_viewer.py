import pandas as pd
from math import ceil

from PyQt6.QtWidgets import (
    QWidget,
    QTableView,
    QLabel, 
    QPushButton, 
    QFileDialog, 
    QComboBox, 
    QVBoxLayout, 
    QHBoxLayout,
    QAbstractItemView
)

from map_viewer import MapViewer
from pandas_model import PandasModel
from page_model import PageModel

class DataTableViewer(QWidget):
    def __init__(self, data_frame):
        super().__init__()
        self.resize(1024, 720)
        self.setWindowTitle("Data table")
        self.layout = QVBoxLayout()
        
        self._page_size = 50

        self._df = data_frame.copy(deep=True)

        self._number_of_pages = ceil(len(self._df)/self._page_size)
        self._current_page = 0

        ## Clean the data, create a filter/page model and use it to fill the table. 
        self._format_data()
        model = PandasModel(self._df.drop(columns=["Elevation Gain", "Delta Time"], axis=1))
        
        self._page_model = PageModel(self._page_size, self)
        self._page_model.setSourceModel(model)
        self._page_model.setCurrentPage(self._current_page)

        self._view = QTableView()
        self._view.setModel(self._page_model)
        self._view.doubleClicked.connect(self._table_clicked)
        self._view.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self._view.resize(1024, 600)

        self._page_size_combobox = QComboBox()
        self._page_size_combobox.setFixedSize(100, 30)
        self._page_size_combobox.addItems(["50", "100", "200", "500", "1000"])
        self._page_size_combobox.currentIndexChanged.connect(self.page_size_changed)

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

        self._show_on_map_button = QPushButton("Show on map")
        self._show_on_map_button.setFixedSize(100, 30)
        self._show_on_map_button.clicked.connect(self._show_on_map_button_clicked)

        pagination_buttons_layout = QHBoxLayout()
        pagination_buttons_layout.addWidget(self._first_page_button)
        pagination_buttons_layout.addWidget(self._previous_page_button)
        pagination_buttons_layout.addWidget(self._pagination_label, 0)
        pagination_buttons_layout.addWidget(self._next_page_button)
        pagination_buttons_layout.addWidget(self._last_page_button)
        pagination_buttons_layout.addStretch()
        pagination_buttons_layout.addWidget(self._show_on_map_button)

        self.layout.addWidget(QLabel("Rows by page:"))
        self.layout.addWidget(self._page_size_combobox, 0)
        self.layout.addWidget(self._view)
        self.layout.addLayout(pagination_buttons_layout)
        self.layout.addWidget(self._export_to_excel_button)

        self.setLayout(self.layout)

    def _table_clicked(self, index):
        
        model = self._view.model()
        
        latitude = model.data_by_column_name(index.row(), 'Latitude')
        longitude = model.data_by_column_name(index.row(), 'Longitude')

        self._map_viewer = MapViewer()
        self._map_viewer.show_marker(latitude, longitude)

    def _format_data(self):
        self._df["Time"] = self._df["Time"].apply(lambda x: x.strftime('%H:%M:%S'))
        self._df["Tot. Distance"] = round(self._df["Tot. Distance"], 2)
        self._df["Tot. Time"] = self._df["Tot. Time"].apply(
                lambda x: f'{x.components.hours:02d}:{x.components.minutes:02d}:{x.components.seconds:02d}'
                                  if not pd.isnull(x) else ''
                                  )
        self._df["Speed"] = round(self._df["Speed"], 2)
        self._df["Speed rollmean"] = round(self._df["Speed rollmean"], 2)
        self._df["Avg Speed"] = round(self._df["Avg Speed"], 2)

    def go_to_first_page(self):
        self._current_page = 0
        self.updateModel()
        self.render()

    def go_to_last_page(self):
        self._current_page = self._number_of_pages - 1
        self.updateModel()
        self.render()

    def go_to_next_page(self):
        self._current_page = min(self._current_page + 1, self._number_of_pages - 1)
        self.updateModel()
        self.render()

    def go_to_previous_page(self):
        self._current_page = max(0, self._current_page - 1)
        self.updateModel()
        self.render()

    def page_size_changed(self, index):
        value = self._page_size_combobox.currentText()
        self._page_size = int(value) 
        self._number_of_pages = ceil(len(self._df)/self._page_size)
        self.updateModel()
        self.render()

    def render(self):
        self._next_page_button.setEnabled(self._current_page < self._number_of_pages - 1)
        self._previous_page_button.setEnabled(self._current_page > 0)

        self._pagination_label.setText(f"Page {self._current_page + 1} of {self._number_of_pages}")

    def updateModel(self):
        self._page_model.setMaxRows(self._page_size)
        self._page_model.setCurrentPage(self._current_page)

    def exportTableToExcel(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Export data frame", "", "Excel Files(*.xlsx)")
        if file_name:
            self._df.to_excel(file_name)

    def _show_on_map_button_clicked(self):
        points = []
        model = self._view.model()
        if model.rowCount() == 0:
            return
        
        for i in range(model.rowCount()):
            latitude = float(model.data_by_column_name(i, 'Latitude'))
            longitude = float(model.data_by_column_name(i, 'Longitude'))
            points.append([latitude, longitude])

        half = int(len(points)/2)
        self._map_viewer = MapViewer()
        self._map_viewer.show_poly_line(points, 10)
        