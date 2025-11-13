Absolutely — here is your **updated README in the SAME format**, but rewritten to match your **current system**:

* **Replaced Streamlit with Next.js**
* Updated architecture
* Added **SFD/BMD solver**
* Added **Laplace solver**
* Mentioned animation pipeline status
* Updated tech stack badges
* Streamlined for competition submission

---

# 🎓 Engineering Solver Suite

A comprehensive web-based platform for solving complex engineering and mathematical problems using symbolic computation and animated explanations.

Frontend now uses **Next.js**, backend uses **FastAPI**, and all solvers + animations are powered by Python.

![Next.js](https://img.shields.io/badge/Next.js-14-black)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110-teal)
![Python](https://img.shields.io/badge/Python-3.10+-green)
![Manim](https://img.shields.io/badge/Manim-0.18-blueviolet)
![Docker](https://img.shields.io/badge/Docker-20-blue)

---

## 🌟 Overview

Engineering Solver Suite is an educational platform that generates **step-by-step solutions** and **Manim-powered animated explanations** for complex engineering subjects.

The platform aims to make engineering concepts interactive, visual, and easy to understand—automatically.

---

## 🏗️ Architecture

Our system uses a **modern decoupled architecture**:

1. **Frontend (Next.js)**
   Users enter equations, view step-by-step solutions, and watch generated animations.

2. **API Request**
   Next.js sends data to FastAPI endpoints such as `/solve-laplace`, `/solve-sfd-bmd`, etc.

3. **Backend (FastAPI)**
   Receives request → calls Python solver → generates step-by-step result and animation-ready LaTeX.

4. **Solver Engine (Python + SymPy)**
   Modular solvers designed for symbolic math, engineering formulas, structural analysis, and animations.

5. **Animation Engine (Manim)**
   Converts solver steps into smooth, high-quality math animations (work in progress).

6. **Storage & Delivery**
   Future support: Task queue for rendering, CDN for video output.

---

## 📚 Available Solvers

### ✅ Implemented Solutions

---

### 1. 📐 **Structural Analysis — SFD/BMD Solver**

* Compute reactions, shear forces, bending moments
* Supports distributed loads, point loads, supports
* Step-by-step JSON output
* **Animations in progress** (beam + diagrams)

---

### 2. 🔁 **Laplace Transform Solver (Beta)**

* Parses LaTeX → SymPy
* Supports base rules:

  * ( e^{at} ), ( t^n ), ( \sin(bt) ), ( \cos(bt) )
* Applies properties:

  * Linearity
  * Exponential shift
* Step-by-step rule application
* Produces LaTeX equations for Manim animations
* **Limited variety** but functional for common engineering problems

---

### 3. 🏗️ **Mechanical Design — EOT Crane**

* Wire rope selection
* Pulley calculations
* Load handling design
* Manim animations for explanation steps

---

### 4. 🎯 **Operations Research — Assignment Problem**

* Hungarian Algorithm
* Step-by-step matrix reduction
* Visual explanation

---

### 5. 🚚 **Operations Research — Transportation Problem**

* Vogel’s Approximation Method
* Balanced/unbalanced problems
* Stepwise visual reasoning

---

## ✨ Key Features

* 🎬 Step-by-step animations (Manim-based)
* 🔍 Transparent reasoning engine (JSON output)
* 💻 Modern web interface (Next.js)
* 🧠 Symbolic math engine (SymPy + custom rules)
* 📊 Engineering-grade accuracy
* 🧩 Modular solver architecture

---

## 🚀 Quick Start (Local Development)

### Prerequisites

* Node.js 18+
* Python 3.10+
* Docker (for backend environment)
* Git

---

### **1. Clone the repository**

```bash
git clone https://github.com/ahmed241/Project-py
cd engineering-solver-suite
```

---

### **2. Install & Run the Backend (FastAPI)**

```bash
cd backend
docker-compose up --build
```

Backend runs at:

```
http://localhost:7000
```

---

### **3. Install & Run the Frontend (Next.js)**

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at:

```
http://localhost:3000
```

---

# 🏗️ Project Structure

```
engineering-solver-suite/
│
├── frontend/                # Next.js UI
│   ├── components/
│   ├── pages/
│   └── public/
│
├── backend/                 # FastAPI service
│   ├── main.py
│   ├── Dockerfile
│   ├── docker-compose.yml
│   ├── requirements.txt
│   └── solvers/
│       ├── laplace/
│       │   ├── laplace_solver.py
│       │   └── laplace_rules.py
│       ├── sfd_bmd/
│       │   └── solver.py
│       ├── assignment/
│       └── transportation/
│
└── animation_engine/        # Manim animation modules
    ├── scenes/
    └── utils/
```

---

# 🎯 Technology Stack

### **Frontend**

* Next.js
* React
* TailwindCSS
* MathLive (LaTeX input)

### **Backend**

* FastAPI
* Pydantic
* SymPy (symbolic math)
* NumPy, SciPy
* Manim (animation)

### **Infrastructure**

* Docker
* (Planned) Celery Workers
* (Planned) S3 Storage / CDN

---

# 🐛 Troubleshooting

### ❌ 404/500 Errors (Frontend → Backend)

Ensure backend is running at `http://localhost:7000`
And the frontend `.env.local` has:

```
NEXT_PUBLIC_BACKEND_URL=http://localhost:7000
```

### ❌ Animation not generating

Check backend logs:

```
docker logs <container-name>
```

### ❌ LaTeX parse failures

Ensure expressions are passed as raw strings:

```
r"e^{2t} + \sin(3t)"
```

---

# 🚀 Deployment

### Backend (FastAPI)

Deploy using:

* Render
* Railway
* Docker-based VPS

### Frontend (Next.js)

Deploy using:

* Vercel (recommended)
* Netlify

Set environment variable:

```
NEXT_PUBLIC_BACKEND_URL = <your backend URL>
```

---

# 🤝 Contributing

Pull requests welcome!
Feel free to submit improvements to solvers, animations, UI, or documentation.

---

<div align="center">

⭐ If this project inspires you, please give it a star!
Built with ❤️ for the engineering community.

</div>

