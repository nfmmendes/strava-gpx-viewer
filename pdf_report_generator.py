import pandas as pd
import datetime
from xhtml2pdf import pisa
import matplotlib.pyplot as plt

class PdfReportGenerator: 

    def __init__(self, df): 
        self._df = df

    def _generate_html_from_data_frame(self, df):
        p_df = df.drop(["Distance", "Elevation Gain", "Delta Time"], axis = 1)
        p_df["Time"] = p_df["Time"].apply(lambda x: x.strftime('%H:%M:%S'))
        p_df["Tot. Distance"] = round(p_df["Tot. Distance"], 2)
        p_df["Tot. Time"] = p_df["Tot. Time"].apply(
                lambda x: f'{x.components.hours:02d}:{x.components.minutes:02d}:{x.components.seconds:02d}'
                                  if not pd.isnull(x) else ''
                                  )
        p_df["Speed"] = round(p_df["Speed"], 2)
        p_df["Speed rollmean"] = round(p_df["Speed rollmean"], 2)
        p_df["Avg Speed"] = round(p_df["Avg Speed"], 2)

        return p_df.groupby(["KM"], as_index=False).last().to_html()

    def _generate_html_report(self):
        return """<html><head><style>  
        table.dataframe { font-weight: medium; } 
        table.dataframe tr { padding-top: 4px; height: 18px; } 
        table.dataframe td { text-align: center; }  
        </style></head> 
        <body> 
        <div>
        <h2> Speed and grade over distance </h2>
        <img src='speed_chart.png'></div>
        <div> 
        <h2> Elevation over distance </h2>
        <img src='elevation_distance_chart.png'></div>
        <div> 
        <h2> Distance and elevation gain over time </h2>
        <img src='time_stats_chart.png'></div>
        <pdf:nextpage>
        <h2> Summarized data </h2>
        <b>Last measurements before each 100 meters </b>""" \
                +  self._generate_html_from_data_frame(self._df) +  "</body> </html>"


    def generate(self, file_name):

        try:
            with open(file_name, "w+b") as file:        
                try:
                    # convert HTML to PDF
                    pisa_status = pisa.CreatePDF(self._generate_html_report(), dest=file)
                    file.close()
                    return pisa_status.err
                except (IOError, OSError):
                    print("Error writing to file")
                    return "Error writing to file"
        except (FileNotFoundError, PermissionError, OSError):
            print("Error opening file")
            return "Error opening file"

        return ""

