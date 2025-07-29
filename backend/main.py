from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from downloader import get_video_info

app = FastAPI(
    title="TIKTOKMASTER API",
    description="A simple API to fetch TikTok video download links.",
    version="1.0.0"
)

# Configure CORS
origins = [
    "http://localhost:5173", # Vite dev server
    "http://127.0.0.1:5173",
    "https://tiktokmaster-frontend.onrender.com", # Your frontend URL on Render
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For simplicity, allow all. Restrict in production.
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

class VideoRequest(BaseModel):
    url: str

@app.get("/health")
def health_check():
    """Health check endpoint for Render."""
    return {"status": "ok"}

@app.post("/api/download")
async def download_video(request: VideoRequest):
    """
    API endpoint to get video information and download links.
    """
    try:
        video_info = await get_video_info(request.url)
        if not video_info or not video_info.get("formats"):
            raise HTTPException(status_code=404, detail="Could not find any downloadable formats for the given URL.")
        return video_info
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="An internal server error occurred.")

# Optional: Add root endpoint for basic info
@app.get("/")
def read_root():
    return {"message": "Welcome to the TIKTOKMASTER API. Use the /api/download endpoint to fetch videos."}