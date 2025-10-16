from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import subprocess
import os
import json
import time
import uuid

app = FastAPI(title="Engineering Solver Suite API")

# Enable CORS for your Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://your-vercel-app.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store job status in memory (use Redis for production)
jobs = {}

# ==================== DATA MODELS ====================

class EOTCraneRequest(BaseModel):
    load_tonnes: float
    speed_mps: float
    lift_height: float

class AssignmentRequest(BaseModel):
    cost_matrix: List[List[float]]
    problem_type: Optional[str] = "minimization"
    restrictions: Optional[List[List[bool]]] = None

class TransportationRequest(BaseModel):
    supply: List[float]
    demand: List[float]
    cost: List[List[float]]

class JobResponse(BaseModel):
    job_id: str
    status: str
    message: str

class JobStatusResponse(BaseModel):
    job_id: str
    status: str  # "pending", "processing", "completed", "failed"
    video_url: Optional[str] = None
    error: Optional[str] = None

# ==================== HELPER FUNCTIONS ====================

def run_python_script(script_path: str, args: List[str], job_id: str):
    """Run Python script in background"""
    try:
        jobs[job_id]["status"] = "processing"
        
        # Execute Python script
        result = subprocess.run(
            ["python", script_path] + args,
            capture_output=True,
            text=True,
            timeout=900  # 15 minute timeout
        )
        
        if result.returncode != 0:
            jobs[job_id]["status"] = "failed"
            jobs[job_id]["error"] = result.stderr
            return
        
        # Extract filename from output
        output_lines = result.stdout.strip().split('\n')
        filename = output_lines[-1].strip()
        
        if not filename.endswith('.mp4'):
            jobs[job_id]["status"] = "failed"
            jobs[job_id]["error"] = "Invalid output from Python script"
            return
        
        jobs[job_id]["status"] = "completed"
        jobs[job_id]["video_url"] = f"/videos/{filename}"
        
    except subprocess.TimeoutExpired:
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["error"] = "Script execution timed out"
    except Exception as e:
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["error"] = str(e)

# ==================== API ENDPOINTS ====================

@app.get("/")
def read_root():
    return {
        "message": "Engineering Solver Suite API",
        "version": "1.0",
        "endpoints": ["/eot-crane", "/assignment", "/transportation"]
    }

@app.post("/api/eot-crane", response_model=JobResponse)
async def generate_eot_crane(request: EOTCraneRequest, background_tasks: BackgroundTasks):
    """Generate EOT Crane design video"""
    
    # Generate unique job ID
    job_id = str(uuid.uuid4())
    
    # Initialize job status
    jobs[job_id] = {
        "status": "pending",
        "created_at": time.time()
    }
    
    # Prepare script arguments
    load_kn = request.load_tonnes * 10  # Convert to kN
    script_path = os.path.join("EOT_Crane", "animation.py")
    args = [
        "--load", str(load_kn),
        "--speed", str(request.speed_mps),
        "--lift", str(request.lift_height)
    ]
    
    # Run in background
    background_tasks.add_task(run_python_script, script_path, args, job_id)
    
    return JobResponse(
        job_id=job_id,
        status="pending",
        message="Video generation started"
    )

@app.post("/api/assignment", response_model=JobResponse)
async def solve_assignment(request: AssignmentRequest, background_tasks: BackgroundTasks):
    """Solve Assignment Problem and generate video"""
    
    job_id = str(uuid.uuid4())
    
    jobs[job_id] = {
        "status": "pending",
        "created_at": time.time()
    }
    
    # Create temporary data file
    data_file = f"temp_data_{job_id}.json"
    with open(data_file, "w") as f:
        json.dump({
            "matrix": request.cost_matrix,
            "type": request.problem_type,
            "restrictions": request.restrictions or []
        }, f)
    
    script_path = os.path.join("Assignment", "animation.py")
    args = [
        "--data_file", data_file,
        "--output_name", f"assignment_{job_id}.mp4"
    ]
    
    background_tasks.add_task(run_python_script, script_path, args, job_id)
    
    return JobResponse(
        job_id=job_id,
        status="pending",
        message="Solving assignment problem"
    )

@app.post("/api/transportation", response_model=JobResponse)
async def solve_transportation(request: TransportationRequest, background_tasks: BackgroundTasks):
    """Solve Transportation Problem and generate video"""
    
    job_id = str(uuid.uuid4())
    
    jobs[job_id] = {
        "status": "pending",
        "created_at": time.time()
    }
    
    # Create temporary data file
    data_file = f"temp_data_{job_id}.json"
    with open(data_file, "w") as f:
        json.dump({
            "supply": request.supply,
            "demand": request.demand,
            "cost": request.cost
        }, f)
    
    script_path = os.path.join("Transportation", "animation.py")
    args = [
        "--data_file", data_file,
        "--output_name", f"transportation_{job_id}.mp4"
    ]
    
    background_tasks.add_task(run_python_script, script_path, args, job_id)
    
    return JobResponse(
        job_id=job_id,
        status="pending",
        message="Solving transportation problem"
    )

@app.get("/api/job/{job_id}", response_model=JobStatusResponse)
async def get_job_status(job_id: str):
    """Check the status of a job"""
    
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = jobs[job_id]
    
    return JobStatusResponse(
        job_id=job_id,
        status=job["status"],
        video_url=job.get("video_url"),
        error=job.get("error")
    )

@app.delete("/api/job/{job_id}")
async def cancel_job(job_id: str):
    """Cancel a job (if still pending)"""
    
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if jobs[job_id]["status"] == "pending":
        jobs[job_id]["status"] = "cancelled"
        return {"message": "Job cancelled"}
    
    return {"message": "Job cannot be cancelled"}

# ==================== HEALTH CHECK ====================

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "active_jobs": len([j for j in jobs.values() if j["status"] == "processing"]),
        "total_jobs": len(jobs)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)