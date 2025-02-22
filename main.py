# Replication of Data Sweeper streamlit app by Code with Josh
import streamlit as st
import pandas as pd
import os
from io import BytesIO

# Downloader
def downloader(df,file):
    columns = st.multiselect("Select columns to keep for conversion:",df.columns,default=df.columns)
    df = df[columns]
    buffer = BytesIO()
    # Ask the format for conversion
    format = st.radio("Convert file to",["CSV","Excel"])
    if format:
        if format == "CSV":
            df.to_csv(buffer,index=False)
            file_name = file.name.replace(file_ext,".csv")
            mime_type = "text/csv"

        elif format == "Excel":
            df.to_excel(buffer,index=False)
            file_name = file.name.replace(file_ext,".xlsx")
            mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

        st.download_button(
            label=f"Download {file_name}",
            data=buffer,
            file_name=file_name,
            mime=mime_type)


# App Setup
title = "Data Sweeper"
st.set_page_config(page_title=title,layout="centered")

st.title(title)
st.write("Convert file between CSV and Excel formats, with built-in data visualization and cleaning options!")

uploaded_files = st.file_uploader("Upload CSV or Excel file:",type=["csv","xlsx"],accept_multiple_files=True)

if uploaded_files:
    for file in uploaded_files:
        # Load data frame
        file_ext = os.path.splitext(file.name)[-1].lower()
        if file_ext == ".csv":
            df = pd.read_csv(file)
        elif file_ext == ".xlsx":
            df = pd.read_excel(file)
        else:
            st.error("Incorrect file format")
        
        # File statistics
        print(f"""
**Name:** {file.name}
**Size:** {file.size} B
""")
        [col1,col2] = st.columns(2)

        # Remove Duplicates
        with col1:
            if st.button("Remove Duplicates"):
                df.drop_duplicates(inplace=True)
                st.write("Duplicates Removed!")
                downloader(df,file)

        with col2:
            if st.button("Fill Missing Data"):
                numeric_cols = df.select_dtypes(include='number').columns
                df[numeric_cols] = df[numeric_cols].fillna(round(df[numeric_cols].mean()))
                st.write("Missing Data Filled!")
                downloader(df,file)
                    
                
        # Visualization
        st.subheader(f"Visualization of {file.name}:")
        # First five rows of data
        st.write(f"First five rows")
        st.dataframe(df.head())
        # Bar Chart
        st.bar_chart(df[["name","age"]],x="name")
