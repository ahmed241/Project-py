import uvicorn
from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import json
import uuid
import subprocess
import sys
from typing import List, Dict, Any # Added for new model

# --- App Setup ---
app = FastAPI()

# --- CORS ---
origins = [
    "http://localhost:3000",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Pydantic Models (Data Validation) ---
class TransportRequest(BaseModel):
    costMatrix: list
    supply: list
    demand: list
    problemType: str
    outputType: str
    solutionType: str

class EOTRequest(BaseModel):
    load: float
    loadUnit: str
    speed: float
    speedUnit: str
    liftHeight: float
    outputType: str

class LaplaceRequest(BaseModel):
    latex: str
    operation: str
    outputType: str

class AssignmentRequest(BaseModel):
    isSquare: bool
    rows: int
    cols: int
    problemType: str
    tableData: list
    outputType: str

# --- NEW SFD_BMD MODEL ---
class SFD_BMD_Request(BaseModel):
    beamLength: float
    supports: List[Dict[str, Any]] # List of support objects
    loads: List[Dict[str, Any]]    # List of load objects
    outputType: str
# --- END NEW MODEL ---


# --- Background Task Worker ---
def run_script_in_background(job_id: str, command: list, output_file_json: str):
    """
    Runs a script in the background and writes its final status to a
    '..._status.json' file that the get_status endpoint can read.
    """
    
    # --- THIS IS THE NEW STATUS FILE ---
    # We will write the final result to this file
    status_file_path = output_file_json.replace(".json", "_status.json")
    final_payload = {}

    try:
        print(f"Starting job {job_id}: {' '.join(command)}")
        command.insert(0, sys.executable) 
        command.insert(1, "-X")
        command.insert(2, "utf8")

        result = subprocess.run(command, capture_output=True, text=True, encoding='utf-8')
        
        if result.returncode != 0:
            print(f"Job {job_id} FAILED. Stderr: {result.stderr}")
            if os.path.exists(output_file_json):
                with open(output_file_json, 'r', encoding='utf-8') as f:
                    final_payload = json.load(f)
            else:
                final_payload = {"status": "error", "message": result.stderr or "Script failed and no error file was created."}
        else:
            print(f"Job {job_id} COMPLETED. Stdout: {result.stdout}")
            
            public_path_json = output_file_json.replace(os.path.join(os.getcwd(), '..', 'algo-viz', 'public'), '')
            public_path_base = public_path_json.replace('.json', '')
            public_path_base_url = public_path_base.replace(os.sep, '/')
            
            output_file_mp4 = output_file_json.replace('.json', '.mp4')
            output_file_pdf = output_file_json.replace('.json', '.pdf')

            if os.path.exists(output_file_mp4):
                final_payload = {"status": "complete", "videoUrl": public_path_base_url + ".mp4"}
            elif os.path.exists(output_file_pdf):
                final_payload = {"status": "complete", "pdfUrl": public_path_base_url + ".pdf"}
            elif os.path.exists(output_file_json):
                with open(output_file_json, 'r', encoding='utf-8') as f:
                    final_payload = json.load(f)
            else:
                final_payload = {"status": "error", "message": "Script ran but no output file was found."}
            
    except Exception as e:
        print(f"CRITICAL: Job {job_id} failed in worker: {str(e)}")
        final_payload = {"status": "error", "message": str(e)}
    
    finally:
        # Write the final payload to the status file
        try:
            with open(status_file_path, 'w', encoding='utf-8') as f:
                json.dump(final_payload, f)
            print(f"Wrote final status for job {job_id} to {status_file_path}")
        except Exception as e:
            print(f"CRITICAL: Failed to write status file for job {job_id}: {str(e)}")

# --- Function to get file paths ---
def get_job_paths(job_id: str, output_type: str):
    """Generates all file paths based on a job_id."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    algo_viz_dir = os.path.join(base_dir, '..', 'algo-viz')
    
    ext = ".mp4" if output_type == "video" else ".pdf" if output_type == "pdf" else ".json"
    
    base_file_name = job_id # Use the job_id as the unique file name
    input_file = os.path.join(algo_viz_dir, 'temp', f"{base_file_name}.json")
    output_file = os.path.join(algo_viz_dir, 'public', 'outputs', f"{base_file_name}{ext}")
    output_file_json = os.path.join(algo_viz_dir, 'public', 'outputs', f"{base_file_name}.json") 
    status_file = os.path.join(algo_viz_dir, 'public', 'outputs', f"{base_file_name}_status.json")

    return input_file, output_file, output_file_json, status_file

# --- API Endpoints (UPDATED) ---

@app.post("/api/transportation/solve")
async def solve_transportation(req: TransportRequest, tasks: BackgroundTasks):
    job_id = f"transport_{uuid.uuid4()}" # Add a prefix for clarity
    
    input_file, output_file, output_file_json, status_file = get_job_paths(job_id, req.outputType)
    script_path = os.path.join(os.path.dirname(__file__), 'Transportation', 'transportation_main.py')
    
    os.makedirs(os.path.dirname(input_file), exist_ok=True)
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(input_file, 'w', encoding='utf-8') as f:
        json.dump(req.dict(), f)
    
    command = [script_path, '--input', input_file, '--output', output_file, '--type', req.outputType]
    
    tasks.add_task(run_script_in_background, job_id, command, output_file_json)
    return {"job_id": job_id}


@app.post("/api/eot-crane/solve")
async def solve_eot(req: EOTRequest, tasks: BackgroundTasks):
    job_id = f"eot_{uuid.uuid4()}"
    
    input_file, output_file, output_file_json, status_file = get_job_paths(job_id, req.outputType)
    script_path = os.path.join(os.path.dirname(__file__), 'EOT_Crane', 'eot_main.py')
    
    os.makedirs(os.path.dirname(input_file), exist_ok=True)
    with open(input_file, 'w', encoding='utf-8') as f:
        json.dump(req.dict(), f)
    
    command = [script_path, '--input', input_file, '--output', output_file, '--type', req.outputType]
    
    tasks.add_task(run_script_in_background, job_id, command, output_file_json)
    return {"job_id": job_id}


@app.post("/api/laplace/solve")
async def solve_laplace(req: LaplaceRequest, tasks: BackgroundTasks):
    job_id = f"laplace_{uuid.uuid4()}"

    input_file, output_file, output_file_json, status_file = get_job_paths(job_id, req.outputType)
    script_path = os.path.join(os.path.dirname(__file__), 'Laplace', 'laplace_main.py')
    
    os.makedirs(os.path.dirname(input_file), exist_ok=True)
    with open(input_file, 'w', encoding='utf-8') as f:
        json.dump(req.dict(), f)
    
    command = [script_path, '--input', input_file, '--output', output_file, '--type', req.outputType]
    
    tasks.add_task(run_script_in_background, job_id, command, output_file_json)
    return {"job_id": job_id}


@app.post("/api/assignment/solve")
async def solve_assignment(req: AssignmentRequest, tasks: BackgroundTasks):
    job_id = f"assignment_{uuid.uuid4()}"

    input_file, output_file, output_file_json, status_file = get_job_paths(job_id, req.outputType)
    script_path = os.path.join(os.path.dirname(__file__), 'Assignment', 'assignment_main.py')
    
    os.makedirs(os.path.dirname(input_file), exist_ok=True)
    with open(input_file, 'w', encoding='utf-8') as f:
        json.dump(req.dict(), f)
    
    command = [script_path, '--input', input_file, '--output', output_file, '--type', req.outputType]
    
    tasks.add_task(run_script_in_background, job_id, command, output_file_json)
    return {"job_id": job_id}


@app.post("/api/sfd-bmd/solve")
async def solve_sfd_bmd(req: SFD_BMD_Request, tasks: BackgroundTasks):
    job_id = f"sfd_bmd_{uuid.uuid4()}"

    input_file, output_file, output_file_json, status_file = get_job_paths(job_id, req.outputType)
    # Assuming your script is in 'SFD_BMD/sfd_bmd_main.py'
    script_path = os.path.join(os.path.dirname(__file__), 'SFD_BMD', 'sfd_bmd_main.py')
    
    os.makedirs(os.path.dirname(input_file), exist_ok=True)
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(input_file, 'w', encoding='utf-8') as f:
        json.dump(req.dict(), f)
    
    command = [
        script_path,
        '--input', input_file,
        '--output', output_file,
        '--type', req.outputType
    ]
    
    tasks.add_task(run_script_in_background, job_id, command, output_file_json)
    return {"job_id": job_id}
# --- END NEW ENDPOINT ---


@app.get("/api/status/{job_id}")
async def get_status(job_id: str):
    """
    Client polls this endpoint. We check for a status file
    created by the background task.
    """
    
    # --- THIS IS THE FIX ---
    # We find the status file based on the job_id
    base_dir = os.path.dirname(os.path.abspath(__file__))
    algo_viz_dir = os.path.join(base_dir, '..', 'algo-viz')
    status_file = os.path.join(algo_viz_dir, 'public', 'outputs', f"{job_id}_status.json")

    if os.path.exists(status_file):
        # File exists! The job is done.
        try:
            with open(status_file, 'r', encoding='utf-8') as f:
                result = json.load(f)
            
            # Clean up the status file
            os.remove(status_file)
            
            # Also clean up the main .json file if it exists
            # (which it should, for direct/error)
            main_json = status_file.replace("_status.json", ".json")
            if os.path.exists(main_json):
                os.remove(main_json)
            
            # Clean up the temp input file
            input_file = os.path.join(algo_viz_dir, 'temp', f"{job_id}.json")
            if os.path.exists(input_file):
                os.remove(input_file)

            return result
        except Exception as e:
            return {"status": "error", "message": f"Failed to read status file: {str(e)}"}
    else:
        # File doesn't exist yet, job is still pending
        return {"status": "pending"}

# --- Run the Server ---
if __name__ == "__main__":
    print("Starting FastAPI server on http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)