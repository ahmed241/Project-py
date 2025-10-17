from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import subprocess
import json
import os
import uuid
from typing import List, Dict

app = FastAPI()

# --- Global dictionary to store job statuses and results ---
# This acts as a simple in-memory database for our background jobs.
jobs: Dict[str, Dict] = {}

# --- Build Absolute Paths for Reliability ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PUBLIC_DIR = os.path.join(BASE_DIR, "public")
BACKEND_DIR = os.path.join(BASE_DIR, "backend")

# --- CORS Middleware to allow frontend access ---
origins = [
    # The URL of your deployed Streamlit application
    "https://project-py-3q8o.onrender.com",
    
    # The URL for local testing of your Streamlit app
    "http://localhost:8501",
]

# Enable CORS with the specific origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, # Use the specific list instead of the wildcard "*"
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Static File Serving for Videos ---
# This makes the public/videos folder accessible via URL.
videos_dir = os.path.join(PUBLIC_DIR, "videos")
os.makedirs(videos_dir, exist_ok=True)
app.mount("/videos", StaticFiles(directory=videos_dir), name="videos")

# ==================== Pydantic Input Models ====================
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
    height: float

# ==================== Generalized Background Task Function ====================

def run_manim_render(job_id: str, problem_data: dict, script_name: str, scene_name: str, problem_dir_name: str, data_filename: str = "data.json"):
    """
    A general-purpose function to run any Manim render command in the background.
    It updates the global 'jobs' dictionary with the final status.
    """
    problem_dir = os.path.join(BACKEND_DIR, problem_dir_name)
    script_path = os.path.join(problem_dir, script_name)
    # Each job gets a unique JSON file to avoid conflicts
    json_path = os.path.join(problem_dir, f"{job_id}_{data_filename}")

    # Save the problem-specific data to its unique JSON file
    with open(json_path, "w") as f:
        json.dump(problem_data, f)
    
    video_filename = f"{job_id}.mp4"
    
    # This robust Manim command saves the video directly to the public/videos directory
    command = [
        "manim", script_path, scene_name, "-ql",
        "--media_dir", videos_dir,
        "-o", video_filename,
        "--disable_caching",
        # Pass the unique job_id to the animation script so it knows which JSON file to read
        "--job_id", job_id
    ]

    try:
        # Run the command and wait for it to complete. check=True will raise an error if Manim fails.
        subprocess.run(command, capture_output=True, text=True, check=True)
        # If successful, update the job status to 'completed' with the video URL.
        jobs[job_id] = {"status": "completed", "video_url": f"/videos/{video_filename}"}
    except subprocess.CalledProcessError as e:
        # If Manim fails, update the job status to 'failed' and save the error log.
        jobs[job_id] = {"status": "failed", "error": e.stderr}
    finally:
        # Clean up the temporary JSON file after the process is finished.
        if os.path.exists(json_path):
            os.remove(json_path)


# ==================== API Endpoints ====================

@app.get("/")
def root():
    return {"message": "Engineering Solver Backend is Running"}

# --- JOB STATUS ENDPOINT (Used by all tasks) ---
@app.get("/api/status/{job_id}")
def get_status(job_id: str):
    """Checks the status of any running job."""
    job = jobs.get(job_id)
    if not job:
        return JSONResponse({"status": "error", "message": "Job not found"}, status_code=404)
    return job

# --- TRANSPORTATION PROBLEM ENDPOINT ---
@app.post("/api/start-transportation-animation")
def start_transportation_animation(request: TransportationRequest, background_tasks: BackgroundTasks):
    job_id = str(uuid.uuid4())
    jobs[job_id] = {"status": "running"}

    # Add the rendering task to run in the background with specific parameters
    background_tasks.add_task(
        run_manim_render,
        job_id=job_id,
        problem_data=request.dict(),
        script_name="animation.py",
        scene_name="TransportationScene",
        problem_dir_name="Transportation",
        data_filename="transportation_problem.json"
    )
    return {"job_id": job_id}

# --- ASSIGNMENT PROBLEM ENDPOINT ---
@app.post("/api/start-assignment-animation")
def start_assignment_animation(request: AssignmentRequest, background_tasks: BackgroundTasks):
    job_id = str(uuid.uuid4())
    jobs[job_id] = {"status": "running"}

    background_tasks.add_task(
        run_manim_render,
        job_id=job_id,
        problem_data=request.dict(),
        script_name="animation.py",
        scene_name="AssignmentScene", # Assuming this is the scene name in your script
        problem_dir_name="Assignment"
    )
    return {"job_id": job_id}

# --- EOT CRANE ENDPOINT ---
@app.post("/api/start-eot-crane-animation")
def start_eot_crane_animation(request: EOTRequest, background_tasks: BackgroundTasks):
    job_id = str(uuid.uuid4())
    jobs[job_id] = {"status": "running"}

    background_tasks.add_task(
        run_manim_render,
        job_id=job_id,
        problem_data=request.dict(),
        script_name="animation.py",
        scene_name="EOTCraneScene", # Assuming this is the scene name in your script
        problem_dir_name="EOT_Crane"
    )
    return {"job_id": job_id}
