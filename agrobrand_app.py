# --------------------------------------------------------------------------
# AgroBrand Fusion AI - Phase 1: MVP Prototype Structure
# Focus: AI Assistant for Agribusiness (Option A)
# Scope: Nigeria-wide / Global Agribusiness Insights
# Origin Context: Akure, Ondo State, Nigeria
# Date: May 12, 2025
# --------------------------------------------------------------------------

# Import necessary libraries
import streamlit as st
import pandas as pd # For handling data files
from PIL import Image # Pillow library for image handling
import io # For handling file streams

# --- 1. Page Configuration ---
st.set_page_config(
    page_title="AgroBrand Fusion AI",
    layout="wide",
)

# --- 2. Main Application Interface ---
st.title("🌾 AgroBrand Fusion AI")
st.markdown("Your AI Assistant for Agribusiness Marketing & Pricing Insights across Nigeria and beyond.")
st.markdown("---")

# --- 3. Sidebar for User Inputs ---
st.sidebar.header("Upload Your Assets Here")

uploaded_image = st.sidebar.file_uploader(
    "1. Upload Product Image",
    type=["png", "jpg", "jpeg"],
    help="Upload a clear picture of your farm product."
)

uploaded_file = st.sidebar.file_uploader(
    "2. Upload Sales/Cost Sheet",
    type=["csv", "xlsx"],
    help="Upload your data file (CSV or Excel)."
)

# --- 4. Main Content Area ---
st.subheader("Uploaded Asset Preview")

# --- Display Uploaded Image ---
if uploaded_image is not None:
    try:
        image = Image.open(uploaded_image)
        st.image(
            image,
            caption=f"Uploaded: {uploaded_image.name}",
            use_column_width=True
        )
        st.markdown("---")
    except Exception as e:
        st.error(f"Error displaying image: {e}")
        st.markdown("---")
else:
    st.info("A preview of your uploaded product image will appear here.")
    st.markdown("---")


# --- ADDED LOGIC: Read and Preview Uploaded Data File ---
st.subheader("Data Preview & Analysis")

# Initialize dataframe variable
df = None

if uploaded_file is not None:
    try:
        # Check file type and read using pandas
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith(('.xlsx', '.xls')):
            # Requires openpyxl (pip install openpyxl) for .xlsx
            # Might require xlrd (pip install xlrd) for older .xls
            df = pd.read_excel(uploaded_file)

        # Check if dataframe was loaded successfully
        if df is not None:
            st.success(f"Successfully loaded data from '{uploaded_file.name}'.")
            st.write("Preview of the first 5 rows:")
            # Display the first 5 rows of the dataframe
            st.dataframe(df.head())
        else:
            # This case might be redundant if exceptions catch failures, but good practice
             st.warning("Could not process the uploaded file.")

    except Exception as e:
        st.error(f"Error reading data file: {e}")
        st.info("Please ensure the file is a valid CSV or Excel file and is not corrupted or password protected.")
        df = None # Ensure df is None if reading failed

else:
    st.info("Upload a CSV or Excel file using the sidebar to see a data preview and analysis.")

# --- Placeholder for Analysis Results ---
# We will use the 'df' dataframe and image info later for analysis
st.markdown("---")
st.subheader("Generated Insights (Coming Soon...)")
if df is not None or uploaded_image is not None:
     st.write("Next steps will involve analyzing the uploaded assets...")
else:
    st.write("Upload an image and/or data file to enable analysis.")


# --- 5. Footer (Optional) ---
st.markdown("---")
st.caption("Developed in Akure | Providing Nationwide Insights | © 2025")

