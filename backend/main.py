from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import subprocess
import json
import os
from typing import List
import uuid

app = FastAPI()

# --- Build Absolute Paths ---
# This makes sure that no matter where you run the server from,
# it can always find the 'public' and 'backend' directories.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PUBLIC_DIR = os.path.join(BASE_DIR, "public")
BACKEND_DIR = os.path.join(BASE_DIR)


# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve video files from an absolute path
app.mount("/videos", StaticFiles(directory=os.path.join(PUBLIC_DIR, "videos")), name="videos")

# ==================== DATA MODELS ====================

class TransportationRequest(BaseModel):
    supply: List[float]
    demand: List[float]
    costs: List[List[float]]

class AssignmentRequest(BaseModel):
    matrix: List[List[float]]
    problem_type: str = "minimization"

class EOTRequest(BaseModel):
    load: float
    speed: float
    lift: float

# ==================== ENDPOINTS ====================

@app.get("/")
def root():
    return {"message": "Engineering Solver Backend Running"}

@app.post("/api/transportation")
def solve_transportation(request: TransportationRequest):
    """Run transportation animation"""
    try:
        # Define reliable, absolute paths
        problem_dir = os.path.join(BACKEND_DIR, "Transportation")
        json_path = os.path.join(problem_dir, "transportation_problem.json")
        script_path = os.path.join(problem_dir, "animation.py")

        # Ensure the target directory exists before writing to it
        os.makedirs(problem_dir, exist_ok=True)

        # Save data to JSON using the reliable path
        with open(json_path, "w") as f:
            json.dump({
                "supply": request.supply,
                "demand": request.demand,
                "costs": request.costs
            }, f)

        # --- THIS IS THE UPDATED SECTION ---

        # 1. Generate a unique filename to prevent conflicts
        video_filename = f"{uuid.uuid4()}.mp4"
        
        # 2. Build a robust command that tells Manim exactly where to save the video
        command = [
            "manim",
            script_path,           # Your script to run
            "-ql",                 # Render in low quality (faster)
            "--media_dir", os.path.join(PUBLIC_DIR), # Tell Manim to use /public as the root media folder
            "-o", video_filename,
            "--disable_caching"  # The final name for the video file
        ]

        # 3. Run the updated command
        result = subprocess.run(
            command,
            capture_output=True,
            text=True
        )
        
        # 4. Check for errors
        if result.returncode != 0:
            # Manim often outputs useful errors to stderr
            return {"error": result.stderr}

        # 5. Return the predictable URL
        return {
        "status": "success",
        "video_url": f"/videos/animation/480p15/{video_filename}",
        "message": "Animation generated successfully"
    }

    except Exception as e:
        return {"error": str(e)}

@app.post("/api/assignment")
def solve_assignment(request: AssignmentRequest):
    """Run assignment problem animation"""
    try:
        # Define reliable, absolute paths
        problem_dir = os.path.join(BACKEND_DIR, "Assignment")
        json_path = os.path.join(problem_dir, "data.json")
        script_path = os.path.join(problem_dir, "animation.py")

        # Ensure the target directory exists
        os.makedirs(problem_dir, exist_ok=True)

        with open(json_path, "w") as f:
            json.dump({
                "matrix": request.matrix,
                "type": request.problem_type
            }, f)
            
        # 1. Generate a unique filename to prevent conflicts
        video_filename = f"{uuid.uuid4()}.mp4"
        # 2. Build a robust command that tells Manim exactly where to save the video
        command = [
            "manim",
            script_path,           # Your script to run
            "-ql",                 # Render in low quality (faster)
            "--media_dir", os.path.join(PUBLIC_DIR), # Tell Manim to use /public as the root media folder
            "-o", video_filename, # The final name for the video file
            "--disable_caching"  
        ]

        # 3. Run the updated command
        result = subprocess.run(
            command,
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            return {"error": result.stderr}
        return {
            "status": "success",
            "video_url": f"/videos/animation/480p15/{video_filename}", # We already know the URL!
            "message": "Animation generated successfully"
        }

    except Exception as e:
        return {"error": str(e)}

@app.post("/api/eot-crane")
def generate_eot(request: EOTRequest):
    """Run EOT Crane animation"""
    try:
        # Define reliable, absolute paths
        problem_dir = os.path.join(BACKEND_DIR, "EOT_Crane")
        json_path = os.path.join(problem_dir, "data.json")
        script_path = os.path.join(problem_dir, "animation.py")

        # Ensure the target directory exists
        os.makedirs(problem_dir, exist_ok=True)

        with open(json_path, "w") as f:
            json.dump({
                "load": request.load,
                "speed": request.speed,
                "lift": request.lift
            }, f)
            
        # 1. Generate a unique filename to prevent conflicts
        video_filename = f"{uuid.uuid4()}.mp4"
        # 2. Build a robust command that tells Manim exactly where to save the video
        command = [
            "manim",
            script_path,           # Your script to run
            "-ql",                 # Render in low quality (faster)
            "--media_dir", os.path.join(PUBLIC_DIR), # Tell Manim to use /public as the root media folder
            "-o", video_filename, # The final name for the video file
            "--disable_caching"  
        ]

        # 3. Run the updated command
        result = subprocess.run(
            command,
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            return {"error": result.stderr}
        return {
            "status": "success",
            "video_url": f"/videos/animation/480p15/{video_filename}", # We already know the URL!
            "message": "Animation generated successfully"
        }

    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7000)