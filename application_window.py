import pandas as pd
import numpy as np
from xhtml2pdf import pisa
import matplotlib.pyplot as plt
from gpx_processor import getDataFrameFromGpxFile
from gpx_processor import calculateSpeedDataFrame

### For embedding in Qt
from matplotlib.backends.qt_compat import QtWidgets
from PyQt6.QtWidgets import QApplication, QLabel, QPushButton, QFileDialog, QGridLayout
from chart_dashboard import ChartDashboard

class ApplicationWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self._main = QtWidgets.QWidget()
        self.setCentralWidget(self._main)
        layout = QtWidgets.QVBoxLayout(self._main)

        self._export_to_pdf_button = QPushButton("Export to pdf")
        self._export_to_pdf_button.setFixedSize(100, 32)
        self._export_to_pdf_button.setVisible(False)
        self._export_to_pdf_button.clicked.connect(self.exportReportToPdf)

        self._open_file_button = QPushButton("Open gpx file")
        self._open_file_button.setFixedSize(100, 32)
        self._open_file_button.clicked.connect(self.openFileDialog)

        self._total_distance_label = QLabel("")
        self._total_time_label = QLabel("")
        self._average_speed_label = QLabel("")
        self._total_elevation_label = QLabel("")
       
        stats_grid_layout = QGridLayout()
        stats_grid_layout.addWidget(QLabel("Total distance: "), 0, 0)
        stats_grid_layout.addWidget(self._total_distance_label, 0, 1)
        stats_grid_layout.addWidget(QLabel("Total time: "), 1, 0)
        stats_grid_layout.addWidget(self._total_time_label, 1, 1)
        stats_grid_layout.addWidget(QLabel("Average speed: "), 2, 0)
        stats_grid_layout.addWidget(self._average_speed_label, 2, 1)
        stats_grid_layout.addWidget(QLabel("Elevation: "), 3, 0)
        stats_grid_layout.addWidget(self._total_elevation_label, 3, 1)

        self._dashboard = ChartDashboard()

        layout.addWidget(self._open_file_button)
        layout.addLayout(stats_grid_layout) 
        layout.addWidget(self._export_to_pdf_button)
        layout.addWidget(self._dashboard) 
        self.showMaximized()

    def generateHtmlFromDataFrame(self, df):
        p_df = df.drop(["Distance", "Elevation Gain", "Delta Time"], axis = 1)
        p_df["Time"] = p_df["Time"].apply(lambda x: x.strftime('%H:%M:%S'))
        p_df["Tot. Distance"] = round(p_df["Tot. Distance"], 2)
        p_df["Tot. Time"] = p_df["Tot. Time"].apply(
                lambda x: f'{x.components.hours:02d}:{x.components.minutes:02d}:{x.components.seconds:02d}'
                                  if not pd.isnull(x) else ''
                                  )
        p_df["Speed"] = round(p_df["Speed"], 2)
        p_df["Speed ma"] = round(p_df["Speed ma"], 2)
        p_df["Avg Speed"] = round(p_df["Avg Speed"], 2)

        return p_df.groupby(["KM"], as_index=False).last().to_html()

    def exportReportToPdf(self):

        try:
            with open("out.pdf", "w+b") as file:        
                try:
                    # convert HTML to PDF
                    pisa_status = pisa.CreatePDF("<html> <body><head><style> table.dataframe { font-weight: medium; }" + 
                                                 "table.dataframe tr { padding-top: 4px; height: 18px; }" + 
                                                 "table.dataframe td { text-align: center; }" +
                                                 "</style></head>" +  
                                                 self.generateHtmlFromDataFrame(self._df) + 
                                                 "</body> </html>", dest=file)
                    file.close()
                    return pisa_status.err
                except (IOError, OSError):
                    print("Error writing to file")
                    return "Error writing to file"
        except (FileNotFoundError, PermissionError, OSError):
            print("Error opening file")
            return "Error opening file"

        return ""

    def openFileDialog(self):
        fname = QFileDialog.getOpenFileName(self,"Open File", "",
                                            "GPX Files (*.gpx)",)

        if len(fname) > 1: 
            self._df = getDataFrameFromGpxFile(fname[0])
            calculateSpeedDataFrame(self._df)
            self.initializeStats(self._df)
            self._dashboard.initializeCharts(self._df)

        self._export_to_pdf_button.setVisible(True)

    def initializeStats(self, df):
        self._total_distance_label.setText(str(round(df.iloc[-1]["Tot. Distance"]/1000,2)))
        self._total_time_label.setText(str(df.iloc[-1]["Tot. Time"]))
        self._average_speed_label.setText(str(round(df.iloc[-1]["Avg Speed"], 2)))
        self._total_elevation_label.setText(str(round(df[df["Elevation Gain"] > 0]["Elevation Gain"].sum(),2)))
        QApplication.processEvents()
