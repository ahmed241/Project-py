from fastapi import FastAPI
import json
import subprocess
import os

app = FastAPI()

# Enable CORS (so frontend can talk to backend)
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all for now
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/assignment")
def solve_assignment(matrix: list):
    """
    This is EXACTLY like your Streamlit button click!
    """
    # 1. Save to JSON (SAME AS STREAMLIT)
    with open("backend/Assignment/data.json", "w") as f:
        json.dump({"matrix": matrix}, f)
    
    # 2. Run Python script (SAME AS STREAMLIT)
    result = subprocess.run(
        ["python", "Assignment/animation.py"],
        capture_output=True,
        text=True
    )
    
    # 3. Get video filename from output
    video_name = result.stdout.strip().split('\n')[-1]
    
    # 4. Return video URL
    return {"video_url": f"/videos/{video_name}"}

# Serve videos (so browser can access them)
from fastapi.staticfiles import StaticFiles
app.mount("/videos", StaticFiles(directory="E:/manimations/Project/algo-viz/public/videos/videos"), name="videos")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)