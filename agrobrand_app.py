# --------------------------------------------------------------------------
# AgroBrand Fusion AI - Phase 1: MVP Prototype Structure
# Focus: AI Assistant for Agribusiness (Option A)
# Scope: Nigeria-wide / Global Agribusiness Insights
# Origin Context: Akure, Ondo State, Nigeria
# Date: May 12, 2025
# --------------------------------------------------------------------------

# Import necessary libraries
import streamlit as st
import pandas as pd # For handling data files later
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

# --- ADDED LOGIC: Display Uploaded Image ---
if uploaded_image is not None:
    # Check if an image has been uploaded
    try:
        # Open the uploaded image file using Pillow
        image = Image.open(uploaded_image)

        # Display the image
        st.image(
            image,
            caption=f"Uploaded: {uploaded_image.name}", # Show filename in caption
            use_column_width=True # Adjust image width to column width
        )
        st.markdown("---") # Separator after image
    except Exception as e:
        st.error(f"Error displaying image: {e}")
        st.markdown("---")
else:
    # Show a placeholder message if no image is uploaded yet
    st.info("A preview of your uploaded product image will appear here.")
    st.markdown("---")


# --- Placeholder for Data Preview and Analysis ---
st.subheader("Data Preview & Analysis (Coming Soon...)")

if uploaded_file is not None:
    # Logic to read and display data will go here
    st.success(f"Data file '{uploaded_file.name}' uploaded. Preview coming next!")
else:
    st.info("Upload a CSV or Excel file to see a data preview and analysis.")


# --- 5. Footer (Optional) ---
st.markdown("---")
st.caption("Developed in Akure | Providing Nationwide Insights | © 2025")

