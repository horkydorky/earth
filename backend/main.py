# backend/main.py
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from .routers import vegetation
import os

app = FastAPI(title="EarthPulse-3D Backend")

# --- Static File Serving ---
# Create the directory if it doesn't exist, to prevent errors on first run
os.makedirs("backend/data/ndvi/processed", exist_ok=True)

# This is the crucial line:
# It tells FastAPI to serve any file in the 'backend/data' directory
# if the URL starts with '/static/data'.
app.mount("/static/data", StaticFiles(directory="backend/data"), name="static-data")


# --- API Routers ---
# Include the router for our vegetation endpoint
app.include_router(vegetation.router, prefix="/api/v1")


# --- Root Endpoint ---
@app.get("/")
def read_root():
    return {"status": "ok", "message": "EarthPulse-3D Backend is running!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)