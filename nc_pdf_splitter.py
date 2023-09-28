import streamlit as st
import tabula
import pandas as pd
from tempfile import NamedTemporaryFile
import base64

# Function to extract tables from PDF using tabula and return as a list of DataFrames
def extract_tables_from_pdf(pdf_path):
    tables = tabula.read_pdf(pdf_path, pages='all', multiple_tables=True)
    return tables

# Function to create a downloadable link for a DataFrame
def get_table_download_link(df, filename, text):
    csv = df.to_excel(index=False, engine="openpyxl")
    b64 = base64.b64encode(csv.encode()).decode()  # Encode as base64
    href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="{filename}">{text}</a>'
    return href

# Streamlit UI
st.title("PDF Table Extractor")

# File Upload
uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])
if uploaded_file and uploaded_file.name == 'OYSTER_BAY_RS5.pdf':
    with NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
        temp_pdf.write(uploaded_file.read())

    # Extract tables from the uploaded PDF
    pdf_tables = extract_tables_from_pdf(temp_pdf.name)

    if pdf_tables:
        combined_df = pd.DataFrame()  # Initialize an empty DataFrame to store all tables

        st.write("\nTables extracted from the PDF:")
        for idx, table in enumerate(pdf_tables, start=1):
            df = pd.DataFrame(table)  # Convert the table to a DataFrame
            combined_df = pd.concat([combined_df, df], ignore_index=True)  # Combine the DataFrames
            # st.write(f"Table {idx}:")
            # st.write(df)

        # st.write("\nCombined DataFrame:")
        # st.write(combined_df)

        # Provide a download button for the Excel file
        st.markdown(get_table_download_link(combined_df, "combined_data.xlsx", "Download Excel"), unsafe_allow_html=True)
    else:
        st.write("\nNo tables found in the PDF.")
else:
    st.write("Please upload the file named 'OYSTER_BAY_RS5.pdf'.")
