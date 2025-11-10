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

from .LaplaceTransform import laplace_solver

app = FastAPI()

# --- Global dictionary to store job statuses and results ---
# This is simple for demonstration. For a more robust app, you might use Redis.
jobs: Dict[str, Dict] = {}

# --- Build Absolute Paths ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PUBLIC_DIR = os.path.join(BASE_DIR, "public")

# --- CORS Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)

# --- Static File Serving ---
# This ensures the /videos directory inside /public is served.
videos_dir = os.path.join(PUBLIC_DIR, "videos")
os.makedirs(videos_dir, exist_ok=True)
app.mount("/videos", StaticFiles(directory=videos_dir), name="videos")

# ==================== DATA MODELS ======================

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

class LaplaceRequest(BaseModel):
    inputLatex: str
    format: str = "latex"
    output: str = "instant"
    options: Dict = {}


# ==================== ENDPOINTS ====================

@app.get("/")
def root():
    return {"message": "Engineering Solver Backend Running"}

@app.post("/api/transportation")
def solve_transportation_VAM(request: TransportationRequest):
    """Run transportation animation"""
    try:
        # Define reliable, absolute paths
        problem_dir = os.path.join(BASE_DIR, "Transportation", "VAM")
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
        problem_dir = os.path.join(BASE_DIR, "Assignment")
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
        problem_dir = os.path.join(BASE_DIR, "EOT_Crane")
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

@app.post("/api/laplace")
def solve_laplace(request: LaplaceRequest):
    """
    Solve Laplace or Inverse Laplace Transform and optionally generate Manim animation.
    """
    try:
        problem_dir = os.path.join(BASE_DIR, "LaplaceTransform")
        json_path = os.path.join(problem_dir, "data.json")
        animation_script_path = os.path.join(problem_dir, "animation.py")

        os.makedirs(problem_dir, exist_ok=True)

        if request.output == "instant":
            result = laplace_solver.solve_laplace_transform(
                request.inputLatex,
                request.options.get("showSteps", False)
            )
            return {"result": result}
        elif request.output == "inverse":
            result = laplace_solver.solve_inverse_laplace_transform(
                request.inputLatex,
                request.options.get("showSteps", False)
            )
            return {"result": result}
        elif request.output == "video":
            # First, get the result from the solver to pass to Manim
            solver_result = laplace_solver.solve_laplace_transform(
                request.inputLatex,
                request.options.get("showSteps", False)
            )
            if not solver_result["ok"]:
                return {"error": solver_result["error"]}

            # Save data for Manim animation
            with open(json_path, "w") as f:
                json.dump({
                    "inputLatex": request.inputLatex,
                    "outputLatex": solver_result["latex"],
                    "showSteps": request.options.get("showSteps", False),
                    "steps": solver_result.get("steps", [])
                }, f)

            video_filename = f"laplace_{uuid.uuid4()}.mp4"
            command = [
                "manim",
                animation_script_path,
                "-ql",
                "--media_dir", os.path.join(PUBLIC_DIR),
                "-o", video_filename,
                "--disable_caching"
            ]

            result = subprocess.run(
                command,
                capture_output=True,
                text=True
            )

            if result.returncode != 0:
                print("Manim Error (stdout):", result.stdout)
                print("Manim Error (stderr):", result.stderr)
                return {"error": result.stderr}
            
            # Manim saves videos in a subdirectory like 480p15
            # We need to find the actual path.
            # A more robust solution would parse Manim's output for the exact path.
            # For now, we'll assume the default 480p15.
            return {
                "status": "success",
                "videoUrl": f"/videos/LaplaceTransformScene/480p15/{video_filename}",
                "message": "Laplace Transform animation generated successfully"
            }
        elif request.output == "pdf":
            # PDF generation logic (placeholder for now)
            return {"error": "PDF generation not implemented yet."}
        else:
            return {"error": "Invalid output type specified."}

    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7000)