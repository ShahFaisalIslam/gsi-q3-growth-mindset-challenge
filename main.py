# Replication of Data Sweeper streamlit app by Code with Josh
import streamlit as st
import pandas as pd
import os
from io import BytesIO

latest_file_id = 0

# Object containing file data including the following:
# * File object
# * File data
class FileData:
    def __init__(self,file):
        global latest_file_id
        latest_file_id += 1
        self.id = latest_file_id
        self.file = file
        self.file_ext = os.path.splitext(self.file.name)[-1].lower()
        if self.file_ext == ".csv":
            self.df = pd.read_csv(self.file)
        else: # Only csv or xlsx comes from file uploader
            self.df = pd.read_excel(self.file)

    # Print file statistics
    def print_stats(file_data):
        st.write(f"""
**Name:** {file_data.file.name}

**Size:** {file_data.file.size} B

""")

    # Remove duplicates from data
    def remove_duplicates(file_data):
        file_data.df.drop_duplicates(inplace=True)
        st.write("Duplicates Removed!")

    # Fill missing data (only numeric data is filled)
    def fill_missing_data(file_data):
        numeric_cols = file_data.df.select_dtypes(include='number').columns
        file_data.df[numeric_cols] = file_data.df[numeric_cols].fillna(round(file_data.df[numeric_cols].mean()))
        st.write("Missing Data Filled!")

    # Visualize Data as follows:
    # * First five rows
    # * Bar chart of name and age
    def visualize_data(file_data):
        st.subheader(f"Visualization of {file_data.file.name}:")
        # First five rows of data
        st.write(f"First five rows")
        st.dataframe(file_data.df.head())
        # Bar Chart
        st.bar_chart(file_data.df[file_data.df.columns[0:2]],x=file_data.df.columns[0],y_label=file_data.df.columns[1])


    # Download file
    def download_file(self,file_name=None):
        buffer = BytesIO()
        # Prepare download according to format
        if self.file_ext == ".csv":
            self.df.to_csv(buffer,index=False)
            mime_type = "text/csv"

        elif self.file_ext == ".xlsx":
            self.df.to_excel(buffer,index=False)
            mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

        if not file_name:
            file_name = file.name

        st.download_button(
            label=f"Download {file_name}",
            data=buffer,
            file_name=file_name,
            mime=mime_type,
            key=f"{self.id}-download")

    def convert_file(self):
        columns = st.multiselect("Select columns to keep for conversion:",
                                 self.df.columns,
                                 default=self.df.columns,
                                 key=f"{self.id}-column-sel")
        self.df = self.df[columns]
        buffer = BytesIO()
        # Ask the format for conversion
        format = st.radio("Convert file to",["CSV","Excel"],key=f"{self.id}-convert-choice")
        if format:
            if format == "CSV":
                file_name = file.name.replace(self.file_ext,".csv")

            elif format == "Excel":
                file_name = file.name.replace(self.file_ext,".xlsx")

            self.download_file(file_name)

# App Setup
title = "Data Sweeper"
st.set_page_config(page_title=title,layout="centered")

st.title(title)
st.write("Convert file between CSV and Excel formats, with built-in data visualization and cleaning options!")

uploaded_files = st.file_uploader("Upload CSV or Excel file:",type=["csv","xlsx"],accept_multiple_files=True)

if uploaded_files:
    for file in uploaded_files:

        # Load file into FileData object
        file_data = FileData(file)


        # Print file statistics from file data
        file_data.print_stats()        

        st.subheader("Tools")
        option = st.radio("Choose between",["Data Cleaning",
                                            "File Conversion"],
                                            key=f"{file_data.id}-tool-choice",
                                            horizontal=True)

        if option:
            if option == "Data Cleaning":
                st.write("_Note: Only one tool is effective on data at a time._")
                [col1,col2] = st.columns(2)

                # Remove Duplicates
                with col1:
                    if st.button("Remove Duplicates",key=f"{file_data.id}-remdup"):
                        file_data.remove_duplicates()
                        file_data.download_file()

                # Fill Missing Data
                with col2:
                    if st.button("Fill Missing Data",key=f"{file_data.id}-fillna"):
                        file_data.fill_missing_data()
                        file_data.download_file()
                            
            else:
                file_data.convert_file()

            # Visualization
            file_data.visualize_data()
