import streamlit as st
import tabula
import pandas as pd
import base64
import io
import os

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
if uploaded_file and uploaded_file.name == 'OYSTER_BAY_RS5.pdf':
    # Create a temporary directory to store PDF chunks
    temp_dir = st.beta_container()
    temp_dir.write("Processing... Please wait.")

    with NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
        temp_pdf.write(uploaded_file.read())

        # Extract the number of pages in the PDF
        pdf_reader = tabula.io.pdf.PDFFileReader(temp_pdf.name)
        num_pages = len(pdf_reader.pages)

        # Initialize an empty DataFrame to store all tables
        combined_df = pd.DataFrame()

        st.write("\nTables extracted from the PDF:")
        for page_num in range(num_pages):
            # Create a temporary PDF file for the current page
            page_pdf_path = os.path.join(temp_dir.name, f"page_{page_num + 1}.pdf")
            tabula.io.extract_pages(temp_pdf.name, page_pdf_path, area=(0, 0, 100, 100), pages=[page_num + 1])

            # Extract tables from the current page
            pdf_tables = extract_tables_from_pdf(page_pdf_path)

            for idx, table in enumerate(pdf_tables, start=1):
                df = pd.DataFrame(table)  # Convert the table to a DataFrame
                combined_df = pd.concat([combined_df, df], ignore_index=True)  # Combine the DataFrames
                # st.write(f"Page {page_num + 1}, Table {idx}:")
                # st.write(df)

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

    # Clean up temporary files and directory
    temp_dir.empty()
    os.unlink(temp_pdf.name)
else:
    st.write("Please upload your file.")
