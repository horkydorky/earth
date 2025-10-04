# app.py
import streamlit as st
from services import ndvi_analysis # <-- SEE? We import your existing work!
import os

# --- Page Configuration ---
st.set_page_config(
    page_title="EarthPulse",
    layout="wide"
)

# --- Sidebar for User Inputs ---
st.sidebar.title("Control Panel")
region = st.sidebar.selectbox("Select a Region", ["kathmandu", "amazon"])
year = st.sidebar.slider("Select a Year", 2000, 2025, 2023)

# --- Main Page ---
st.title("EarthPulse NDVI Heatmaps")
st.write(f"Displaying data for **{region.capitalize()}** in the year **{year}**.")

# Process Button
if st.sidebar.button("Generate Heatmap"):
    try:
        # Check if the raw data files exist first
        red_file = f"data/ndvi/raw/{region}_{year}_red.tif"
        nir_file = f"data/ndvi/raw/{region}_{year}_nir.tif"
        
        if not os.path.exists(red_file) or not os.path.exists(nir_file):
            st.error(f"Data for {region} {year} not found. Please add the required .tif files.")
        else:
            with st.spinner(f"Processing NDVI for {region} {year}... this may take a moment."):
                # This calls your powerful data processing function!
                result_path = ndvi_analysis.process_vegetation_data_for_region(region, year)
                
                # The result_path from your service is slightly different than what we need
                # Service returns: /static/data/ndvi/processed/heatmap_...
                # We need the local path: data/ndvi/processed/heatmap_...
                local_image_path = result_path.replace("/static/", "")

                st.success("Processing Complete!")
                st.image(local_image_path, caption=f"NDVI Heatmap for {region.capitalize()} {year}")

    except Exception as e:
        st.error(f"An error occurred during processing: {e}")