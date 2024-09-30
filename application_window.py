import pandas as pd
import numpy as np
import datetime
from xhtml2pdf import pisa
import matplotlib.pyplot as plt
from pdf_report_generator  import PdfReportGenerator
from gpx_processor import getDataFrameFromGpxFile
from gpx_processor import calculateSpeedDataFrame

### For embedding in Qt
from matplotlib.backends.qt_compat import QtWidgets
from PyQt6.QtWidgets import QApplication, QLabel, QPushButton, QFileDialog, QGridLayout
from chart_dashboard import ChartDashboard
from data_table_viewer import DataTableViewer

class ApplicationWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self._main = QtWidgets.QWidget()
        self.setWindowTitle("Gpx stats viewer")
        self.setCentralWidget(self._main)
        layout = QtWidgets.QVBoxLayout(self._main)

        self.setStyleSheet(".stats-title { font-weight: bold; }") 

        self._export_to_pdf_button = QPushButton("Export to pdf")
        self._export_to_pdf_button.setFixedSize(100, 32)
        self._export_to_pdf_button.setVisible(False)
        self._export_to_pdf_button.clicked.connect(self.exportReportToPdf)

        self._show_data_table_button = QPushButton("Show data table")
        self._show_data_table_button.setFixedSize(100, 32)
        self._show_data_table_button.setVisible(False)
        self._show_data_table_button.clicked.connect(self.showDataTable)

        self._open_file_button = QPushButton("Open gpx file")
        self._open_file_button.setFixedSize(100, 32)
        self._open_file_button.clicked.connect(self.openFileDialog)

        self._start_time_value_label = QLabel("")
        self._total_distance_value_label = QLabel("")
        self._total_time_value_label = QLabel("")
        self._average_speed_value_label = QLabel("")
        self._total_elevation_value_label = QLabel("")
      
        start_time_title_label = QLabel("Start time:")
        start_time_title_label.setProperty("class", "stats-title")

        total_distance_title_label = QLabel("Total distance: ")
        total_distance_title_label.setProperty("class", "stats-title")

        total_time_title_label = QLabel("Total time:")
        total_time_title_label.setProperty("class", "stats-title")

        average_speed_title_label = QLabel("Average speed:")
        average_speed_title_label.setProperty("class", "stats-title")

        total_elevation_title_label = QLabel("Elevation:")
        total_elevation_title_label.setProperty("class", "stats-title")

        stats_grid_layout = QGridLayout()
        stats_grid_layout.addWidget(start_time_title_label, 0, 0)
        stats_grid_layout.addWidget(self._start_time_value_label, 0, 1)
        stats_grid_layout.addWidget(total_distance_title_label, 1, 0)
        stats_grid_layout.addWidget(self._total_distance_value_label, 1, 1)
        stats_grid_layout.addWidget(total_time_title_label, 2, 0)
        stats_grid_layout.addWidget(self._total_time_value_label, 2, 1)
        stats_grid_layout.addWidget(average_speed_title_label, 3, 0)
        stats_grid_layout.addWidget(self._average_speed_value_label, 3, 1)
        stats_grid_layout.addWidget(total_elevation_title_label, 4, 0)
        stats_grid_layout.addWidget(self._total_elevation_value_label, 4, 1)
        stats_grid_layout.addWidget(self._show_data_table_button, 0, 2, 4, 2)  
        stats_grid_layout.addWidget(self._export_to_pdf_button, 2, 2, 4, 3)

        self._dashboard = ChartDashboard()

        layout.addWidget(self._open_file_button)
        layout.addLayout(stats_grid_layout, 0) 
        layout.addWidget(self._dashboard, 1) 
        self.showMaximized()


    def showDataTable(self):
        print("Show data table clicked")
        self.data_table_viewer = DataTableViewer(self._df)
        self.data_table_viewer.show()

    def exportReportToPdf(self):
        file_name, _ = QtWidgets.QFileDialog.getSaveFileName(self, 
                                                            "Save File", "", "PDF Files(*.pdf)")
        if file_name:
            pdf_generator = PdfReportGenerator(self._df)
            pdf_generator.generate(file_name)

    def openFileDialog(self):
        fname = QFileDialog.getOpenFileName(self,"Open File", "","GPX Files (*.gpx)",)

        if len(fname) > 1: 
            self._df = getDataFrameFromGpxFile(fname[0])
            calculateSpeedDataFrame(self._df)
            self.initializeStats(self._df)
            self._dashboard.initializeCharts(self._df)

        self._show_data_table_button.setVisible(True)
        self._export_to_pdf_button.setVisible(True)

    def initializeStats(self, df):
        start_time = df.iloc[0]["Time"].to_pydatetime()
        format_total_time = lambda x : f'{x.components.hours:02d}:{x.components.minutes:02d}:{x.components.seconds:02d}'
        self._start_time_value_label.setText(start_time.strftime("%Y-%m-%d %H:%M:%S"))
        self._total_distance_value_label.setText(str(round(df.iloc[-1]["Tot. Distance"]/1000,2)))
        self._total_time_value_label.setText(format_total_time(df.iloc[-1]["Tot. Time"]))
        self._average_speed_value_label.setText(str(round(df.iloc[-1]["Avg Speed"], 2)))
        self._total_elevation_value_label.setText(str(round(df[df["Elevation Gain"] > 0]["Elevation Gain"].sum(),2)))
        QApplication.processEvents()
