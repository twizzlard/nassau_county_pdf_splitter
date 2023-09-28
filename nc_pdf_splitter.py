import streamlit as st
import tabula
import pandas as pd
from tempfile import NamedTemporaryFile
import base64
import io

# Function to extract tables from PDF using tabula and return as a list of DataFrames
def extract_tables_from_pdf(pdf_path):
    tables = tabula.read_pdf(pdf_path, pages='all', multiple_tables=True)
    return tables

# Function to create a downloadable link for a binary file
def get_binary_download_link(binary_data, filename, text):
    b64 = base64.b64encode(binary_data).decode()  # Encode as base64
    href = f'<a href="data:application/octet-stream;base64,{b64}" download="{filename}">{text}</a>'
    return href

# Streamlit UI
st.title("PDF Table Extractor")

# File Upload
uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])
if uploaded_file:
    with NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
        temp_pdf.write(uploaded_file.read())

    # Extract tables from the uploaded PDF
    pdf_tables = extract_tables_from_pdf(temp_pdf.name)

    if pdf_tables:
        combined_df = pd.DataFrame()  # Initialize an empty DataFrame to store all tables

        st.write("\nTables extracted from the PDF.")
        for idx, table in enumerate(pdf_tables, start=1):
            df = pd.DataFrame(table)  # Convert the table to a DataFrame
            
            combined_df = pd.concat([combined_df, df], ignore_index=True)  # Combine the DataFrames
        #     st.write(f"Table {idx}:")
        #     st.write(df)

        # st.write("\nCombined DataFrame:")
        # st.write(combined_df)

        # Create a binary Excel file and provide a download link
        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
            combined_df.to_excel(writer, index=False)
        
        # Generate the output Excel filename based on the original PDF filename
        pdf_filename = os.path.splitext(uploaded_file.name)[0]
        excel_filename = f"{pdf_filename}.xlsx"

        st.markdown(get_binary_download_link(excel_buffer.getvalue(), excel_filename, "Download Excel"), unsafe_allow_html=True)
    else:
        st.write("\nNo tables found in the PDF.")
else:
    st.write("Please upload a file.")
