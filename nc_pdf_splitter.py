import streamlit as st
import tabula
import pandas as pd
from tempfile import NamedTemporaryFile

# Function to extract tables from PDF using tabula and return as a list of DataFrames
def extract_tables_from_pdf(pdf_path):
    tables = tabula.read_pdf(pdf_path, pages='all', multiple_tables=True)
    return tables

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
            combined_df = pd.concat([combined_df, df], ignore_index=True)
            # st.write(f"Table {idx}:")
            # st.write(df)

        # st.write("\nCombined DataFrame:")
        # st.write(combined_df)

        # Create a temporary Excel file and save the combined DataFrame to it
        excel_file = NamedTemporaryFile(delete=False, suffix=".xlsx")
        combined_df.to_excel(excel_file.name, index=False)

        # Download the Excel file
        st.download_button("Download Excel", data=open(excel_file.name, "rb").read(), file_name="combined_data.xlsx", key="excel-download")
        
    else:
        st.write("\nNo tables found in the PDF.")
else:
    st.write("Please upload the file named 'OYSTER_BAY_RS5.pdf'.")

