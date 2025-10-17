from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import subprocess
import json
import os
from typing import List

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all
    allow_credentials = False,  # Must be False with "*"
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# Serve video files
app.mount("/videos", StaticFiles(directory="public/videos"), name="videos")

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
    height: float

# ==================== ENDPOINTS ====================

@app.get("/")
def root():
    return {"message": "Engineering Solver Backend Running"}

@app.post("/api/transportation")
def solve_transportation(request: TransportationRequest):
    """Run transportation animation"""
    try:
        # Save data to JSON
        with open("backend/Transportation/transportation_problem.json", "w") as f:
            json.dump({
                "supply": request.supply,
                "demand": request.demand,
                "costs": request.costs
            }, f)
        
        # Run Python script
        result = subprocess.run(
            ["python", "backend/Transportation/animation.py"],
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.returncode != 0:
            return {"error": result.stderr}
        
        # Get video filename from output
        lines = result.stdout.strip().split('\n')
        video_file = lines[-1].strip()
        
        return {
            "status": "success",
            "video_url": f"/videos/{video_file}",
            "message": "Animation generated successfully"
        }
    
    except Exception as e:
        return {"error": str(e)}

@app.post("/api/assignment")
def solve_assignment(request: AssignmentRequest):
    """Run assignment problem animation"""
    try:
        with open("backend/Assignment/data.json", "w") as f:
            json.dump({
                "matrix": request.matrix,
                "type": request.problem_type
            }, f)
        
        result = subprocess.run(
            ["python", "backend/Assignment/animation.py"],
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.returncode != 0:
            return {"error": result.stderr}
        
        lines = result.stdout.strip().split('\n')
        video_file = lines[-1].strip()
        
        return {
            "status": "success",
            "video_url": f"/videos/{video_file}"
        }
    
    except Exception as e:
        return {"error": str(e)}

@app.post("/api/eot_crane")
def generate_eot(request: EOTRequest):
    """Run EOT Crane animation"""
    try:
        # Run Python script with arguments
        result = subprocess.run(
            [
                "python", "backend/EOT_Crane/animation.py",
                "--load", str(request.load),
                "--speed", str(request.speed),
                "--lift", str(request.height)
            ],
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.returncode != 0:
            return {"error": result.stderr}
        
        lines = result.stdout.strip().split('\n')
        video_file = lines[-1].strip()
        
        return {
            "status": "success",
            "video_url": f"/videos/{video_file}"
        }
    
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7000)