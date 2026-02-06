import pandas as pd
from pandas import DataFrame
from xhtml2pdf import pisa

class PdfReportGenerator: 

    def __init__(self, df: DataFrame): 
        """
        Class constructor

        :param df: The data frame to be used for the report generation.
        :type df: pandas.DataFrame
        """
        self._df = df

    def _generate_html_from_data_frame(self, df: DataFrame) -> str:
        """
        Generate an HTML table from a pandas DataFrame.

        :param df: The pandas DataFrame to be converted to HTML.
        :type df: pandas.DataFrame
        """
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

    def _generate_html_report(self) -> str:
        """
        Generate the HTML report to be converted to PDF.

        :return: The generated HTML report as a string.
        :rtype: str
        """


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


    def generate(self, file_name: str) -> str:
        """
        Generate a PDF report from the data frame and save it to the specified file.
        
        :param self: Description
        :param file_name: Description
        :return: Report generation status. An empty string indicates success, while any other string indicates an error message.
        :rtype: str
        """
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

