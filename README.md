# 🎓 Engineering Solver Suite

A comprehensive web-based platform for solving complex engineering problems, built entirely in Python with a Streamlit frontend and a FastAPI backend for heavy computation and video rendering.

![Streamlit](https://img.shields.io/badge/Streamlit-1.33-ff69b4)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110-teal)
![Python](https://img.shields.io/badge/Python-3.10+-green)
![Manim](https://img.shields.io/badge/Manim-0.18-blueviolet)
![Docker](https://img.shields.io/badge/Docker-20-blue)

## 🌟 Overview

Engineering Solver Suite is an all-in-one educational platform designed to help students and engineers tackle complex problems. Each solver provides not just answers but **visual explanations** and **step-by-step animated breakdowns** of the solution process, powered by a robust Python backend.

---

## 🏗️ Architecture

This project uses a modern decoupled architecture to handle long-running tasks like video rendering without timeouts, using a pure Python stack.

1.  **Frontend (Streamlit)**: The user interacts with the Streamlit app, enters their data, and clicks "Render Video."
2.  **API Request**: The frontend sends a request to a `/api/start-...` endpoint on the FastAPI backend.
3.  **Backend (FastAPI)**: The backend immediately accepts the request, creates a unique **Job ID**, and starts the Manim rendering process as a **background task**. It instantly returns the Job ID to the frontend.
4.  **Polling**: The Streamlit app then repeatedly calls a `/api/status/{job_id}` endpoint every few seconds to check the job's status.
5.  **Result**: Once the backend finishes rendering, it updates the job's status. The frontend sees the "completed" status, gets the final video URL, and displays it to the user.



---

## 📚 Available Solvers

### ✅ Implemented Solutions

#### 1. 🏗️ **Mechanical Design - EOT Crane**
- **Problem**: Design the hoisting mechanism for an Electric Overhead Traveling (EOT) crane.
- **Features**: Wire rope selection, pulley optimization, and animated design process using Manim.
- **Input**: Load (tonnes/kN), Speed (m/min or m/s), Lift height.
- **Output**: Complete design specifications or an animated explanation.

#### 2. 🎯 **Operations Research - Assignment Problem**
- **Problem**: Find the optimal minimum-cost assignment using the Hungarian Algorithm.
- **Features**: Step-by-step matrix reduction and a visual representation of the final assignments.
- **Input**: N×N cost matrix.
- **Output**: Optimal assignment pairs with minimum total cost.

#### 3. 🚚 **Operations Research - Transportation Problem**
- **Problem**: Find the optimal distribution plan from sources to destinations.
- **Features**: Vogel's Approximation Method, supply-demand balancing, and route visualization.
- **Input**: Supply array, Demand array, Cost matrix.
- **Output**: Optimal transportation plan with minimum cost.

---

## ✨ Key Features

- 🎬 **Asynchronous Video Rendering** - No more timeouts! Jobs run in the background.
- 📊 **Interactive Inputs** - User-friendly Streamlit widgets with real-time updates.
- 📱 **Mobile Friendly** - Responsive design that works on all devices.
- 📈 **Real Engineering Data** - Uses standard reference tables from the PSG Design Data Book.
- 🧮 **Accurate Calculations** - Implements industry-standard algorithms and methods.

---

## 🚀 Quick Start (Local Development)

### Prerequisites

- **Python** 3.10+ and pip
- **Docker** and Docker Compose
- **Git**

### Installation & Running


# 1. Clone the repository
git clone [https://github.com/ahmed241/Project-py](https://github.com/ahmed241/Project-py.git)
cd engineering-solver-suite

# 2. Run the Python Backend (using Docker)
# This builds the container with Manim, LaTeX, and all dependencies.
# This command might take a while the first time.
cd backend
docker-compose up --build
# The backend will now be running on http://localhost:7000

# 3. In a NEW terminal, install frontend dependencies and run the Streamlit app
cd .. # Go back to the root directory
pip install -r requirements.txt
streamlit run Home.py
# The frontend will now be running on http://localhost:8501
🏗️ Project Structure
engineering-solver-suite/
├── Home.py                       # Main Streamlit homepage
├── requirements.txt              # Frontend (Streamlit) Python dependencies
├── pages/
│   ├── 1_Transportation.py       # Transportation solver page
│   ├── 2_Assignment.py           # Assignment solver page
│   └── 3_EOT_Crane.py            # EOT Crane solver page
└── backend/
    ├── main.py                   # FastAPI app with all API endpoints
    ├── requirements.txt          # Backend Python dependencies
    ├── Dockerfile                # Docker instructions for backend server
    ├── docker-compose.yml        # Easy local startup for the backend
    ├── public/
    │   └── videos/               # Stores generated videos
    └── backend/
        ├── Transportation/
        │   ├── animation.py
        │   └── VAM_solver.py
        ├── Assignment/
        │   └── ...
        └── EOT_Crane/
            ├── animation.py
            └── EOT_solver.py
🎯 Technology Stack
Frontend
Framework: Streamlit

Language: Python

Backend
Framework: FastAPI

Language: Python

Animation: Manim

Computation: NumPy, SciPy

Deployment: Docker

🐛 Troubleshooting
Connection Refused Error in Streamlit:

Make sure your backend Docker container is running. Use docker ps to check.

Verify the BACKEND_URL variable in your Streamlit .py files is correct (e.g., http://localhost:7000 for local development).

403 Forbidden Error on Deployed App:

This is a CORS error. Go to backend/main.py, find the origins list, and add the exact URL of your deployed Streamlit app (e.g., https://your-app-name.streamlit.app).

Videos Not Generating:

Check the logs from your Docker container for any Manim errors.

Ensure the public/videos directory exists within your backend structure.

🚀 Deployment
This project requires deploying the frontend and backend separately.

1. Backend (Python/FastAPI)
Recommended Service: Render.

Method: Connect your GitHub repository. Render will automatically detect the Dockerfile and build your containerized backend.

Result: You will get a public URL like https://your-backend.onrender.com.

2. Frontend (Python/Streamlit)
Recommended Service: Streamlit Community Cloud.

Method: Connect your GitHub repository and point it to your app's main file (Home.py).

Crucial Step: You must set a Secret in your Streamlit app's settings. The secret key should be BACKEND_URL and its value should be the public URL of your deployed backend (e.g., https://your-backend.onrender.com). Your Streamlit code should read this secret to communicate with the backend.

🤝 Contributing
We welcome contributions! Please fork the repository, create a feature branch, and open a pull request.

<div align="center">

🌟 If this project helped you, please give it a star! ⭐
Made with ❤️ for the engineering community

</div>