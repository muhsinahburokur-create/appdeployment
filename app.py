import streamlit as st
import tabula
import pandas as pd
import os

st.set_page_config(page_title="PDF to CSV Converter", page_icon="")

st.title("PDF to CSV Converter")
st.write("Upload a PDF file containing tables and convert it to CSV.")

# File upload
uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

if uploaded_file is not None:
    # Save temporary file
    temp_pdf = "temp.pdf"
    with open(temp_pdf, "wb") as f:
        f.write(uploaded_file.read())

    st.success("File uploaded successfully!")

    try:
        # Extract tables
        tables = tabula.read_pdf(temp_pdf, pages="all", multiple_tables=True)

        if tables:
            # Merge tables
            df = pd.concat(tables, ignore_index=True)

            # Drop completely empty rows
            df = df.dropna(how='all')

            # Reset index
            df = df.reset_index(drop=True)

            # Remove rows that contain header text (noise)
            keywords = ["MAURITIUS", "Weather", "Issued", "Forecast", "Region", "Station"]
            df = df[~df.apply(lambda row: row.astype(str).str.contains('|'.join(keywords), case=False).any(), axis=1)]

            # Rename columns manually (based on your PDF structure)
            df.columns = ["Region", "Station", "Rainfall", "Humidity", "Weather", "MaxTemp", "MinTemp", "Wind"]

            # Clean values
            df["Rainfall"] = pd.to_numeric(df["Rainfall"], errors='coerce')
            df["Humidity"] = pd.to_numeric(df["Humidity"], errors='coerce')
            df["MaxTemp"] = pd.to_numeric(df["MaxTemp"], errors='coerce')
            df["MinTemp"] = pd.to_numeric(df["MinTemp"], errors='coerce')

            # Drop rows where Region is missing (invalid rows)
            df = df[df["Region"].notna()]

            # Reset index again
            df = df.reset_index(drop=True)

            st.subheader("Extracted Data Preview")
            st.dataframe(df)

            # Convert to CSV
            csv = df.to_csv(index=False).encode('utf-8')

            st.download_button(
                label="⬇ Download CSV",
                data=csv,
                file_name="output.csv",
                mime="text/csv"
            )
        else:
            st.error("No tables found in this PDF.")

    except Exception as e:
        st.error(f"Error: {e}")

    # Clean up
    if os.path.exists(temp_pdf):
        os.remove(temp_pdf)