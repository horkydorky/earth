# backend/services/ndvi_analysis.py

import numpy as np
import rasterio
from PIL import Image
import matplotlib.cm as cm
import os

# Define our data directories for clarity
RAW_DATA_DIR = "backend/data/ndvi/raw"
PROCESSED_DATA_DIR = "backend/data/ndvi/processed"

# Crucial step: Ensure the output directory exists.
os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)


def process_vegetation_data_for_region(region: str, year: int) -> str:
    """
    Main function to process satellite data for a given region and year.
    1. Finds the correct satellite image files.
    2. Calculates the NDVI array.
    3. Converts NDVI values to a color heatmap image.
    4. Saves the heatmap as a PNG.
    5. Returns the path to the final image for the API.
    """
    print(f"Starting NDVI processing for {region} {year}...")
    # Construct the filenames dynamically using the function's parameters
    red_filename = f"{region}_{year}_red.tif"
    nir_filename = f"{region}_{year}_nir.tif"

    red_band_path = os.path.join(RAW_DATA_DIR, red_filename)
    nir_band_path = os.path.join(RAW_DATA_DIR, nir_filename)

    # Check if the files actually exist before we proceed
    if not os.path.exists(red_band_path) or not os.path.exists(nir_band_path):
        raise FileNotFoundError("Required TIF files not found in the raw data directory.")

    # Step 2: Calculate the NDVI data using our helper function
    print("Calculating NDVI...")
    ndvi_data = _calculate_ndvi(red_band_path, nir_band_path)

    # Step 3: Create the heatmap image
    print("Creating heatmap image...")
    # We will name the output file based on the region and year
    output_filename = f"heatmap_{region}_{year}.png"
    output_image_path = os.path.join(PROCESSED_DATA_DIR, output_filename)

    _create_heatmap_image(ndvi_data, output_image_path)

    # Step 4: Return the public-facing URL path for the API
    # This path assumes static files will be served from the 'processed' folder.
    api_path = f"/static/data/ndvi/processed/{output_filename}"
    print(f"Processing complete. Heatmap available at: {api_path}")
    return api_path


def _calculate_ndvi(red_path: str, nir_path: str) -> np.ndarray:
    """Uses rasterio to open the two TIF files and calculate NDVI."""
    with rasterio.open(red_path) as red_src, rasterio.open(nir_path) as nir_src:
        # Read the image data into numpy arrays
        red = red_src.read(1).astype('float64')
        nir = nir_src.read(1).astype('float64')

    # Allow division by zero errors (we will handle them)
    np.seterr(divide='ignore', invalid='ignore')

    # The NDVI formula
    ndvi = (nir - red) / (nir + red)

    # Handle the 'nan' (not a number) values that result from 0/0 division
    # We'll set them to 0, which will be transparent in our final image.
    ndvi[np.isnan(ndvi)] = 0
    return ndvi


def _create_heatmap_image(ndvi_data: np.ndarray, output_path: str):
    """Normalizes NDVI data and saves it as a colormapped PNG."""
    # Normalize data from the NDVI range [-1, 1] to [0, 1] for coloring
    normalized_data = (ndvi_data + 1) / 2

    # Use a matplotlib colormap. 'YlGn' (Yellow-Green) is great for vegetation.
    # It will color low values yellow and high values green.
    colored_data = cm.YlGn(normalized_data)

    # Matplotlib gives us values between 0 and 1. We need 0-255 for an image.
    # Also, we set an "alpha" (transparency) channel.
    # We make pixels with 0 NDVI value (normalized to 0.5) fully transparent.
    alpha = np.where(normalized_data == 0.5, 0, 255) # 0 = transparent, 255 = opaque
    image_data_rgba = (colored_data * 255).astype(np.uint8)
    image_data_rgba[:, :, 3] = alpha # Apply the transparency

    # Create image using the Pillow library and save it as a PNG
    img = Image.fromarray(image_data_rgba, 'RGBA')
    img.save(output_path)
    print(f"Heatmap successfully saved to: {output_path}")