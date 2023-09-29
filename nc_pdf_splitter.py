import streamlit as st
import tabula
import pandas as pd
import os
import PyPDF2
import tempfile
import io

# Function to extract tables from PDF using tabula and return as a list of DataFrames
def extract_tables_from_pdf(pdf_path):
    tables = tabula.read_pdf(pdf_path, pages='all', multiple_tables=True)
    return tables

# Function to split a PDF into individual pages
def split_pdf(pdf_path, output_dir):
    with open(pdf_path, 'rb') as pdf_file:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        num_pages = len(pdf_reader.pages)

        # Create a temporary directory to store PDF pages
        os.makedirs(output_dir, exist_ok=True)

        for page_num in range(num_pages):
            pdf_writer = PyPDF2.PdfWriter()
            pdf_writer.append_pages([pdf_reader.pages[page_num]])
            
            page_filename = os.path.join(output_dir, f"page_{page_num + 1}.pdf")
            with open(page_filename, 'wb') as page_file:
                pdf_writer.write(page_file)

    return num_pages

# Streamlit UI
st.title("PDF Table Extractor")

# File Upload
uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])
if uploaded_file:
    # Create a unique temporary directory to store PDF pages
    temp_dir = tempfile.mkdtemp()

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
        temp_pdf.write(uploaded_file.read())

        # Extract the number of pages in the PDF
        pdf_reader = PyPDF2.PdfReader(temp_pdf.name)
        num_pages = len(pdf_reader.pages)

        # Initialize an empty DataFrame to store all tables
        combined_df = pd.DataFrame()

        st.write("Tables extracted from the PDF:")
        for page_num in range(num_pages):
            # Create a temporary PDF file for the current page
            page_pdf_path = os.path.join(temp_dir, f"page_{page_num + 1}.pdf")
            pdf_writer = PyPDF2.PdfWriter()
            pdf_writer.append_pages([pdf_reader.pages[page_num]])
            pdf_writer.write(page_pdf_path)

            # Extract tables from the current page
            pdf_tables = extract_tables_from_pdf(page_pdf_path)

            for idx, table in enumerate(pdf_tables, start=1):
                df = pd.DataFrame(table)  # Convert the table to a DataFrame
                combined_df = pd.concat([combined_df, df], ignore_index=True)  # Combine the DataFrames
                st.write(f"Page {page_num + 1}, Table {idx}")
                # st.write(df)

        # st.write("Combined DataFrame:")
        # st.write(combined_df)

        # Create a binary Excel file and provide a download link
        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
            combined_df.to_excel(writer, index=False)

        # Generate the output Excel filename based on the original PDF filename
        pdf_filename = os.path.splitext(uploaded_file.name)[0]
        excel_filename = f"{pdf_filename}.xlsx"

        st.write(f"Download Excel: [Click Here]({get_binary_download_link(excel_buffer.getvalue(), excel_filename)})")

        # Clean up temporary files and directory
        for page_num in range(num_pages):
            page_pdf_path = os.path.join(temp_dir, f"page_{page_num + 1}.pdf")
            os.unlink(page_pdf_path)
        os.rmdir(temp_dir)
else:
    st.write("Please upload a PDF file.")
