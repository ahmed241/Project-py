# Use an official Python image as a base
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# Install Manim's system-level dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    texlive-full \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container
COPY requirements.txt requirements.txt

# Install Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy your entire project code into the container
COPY . .

# Tell Docker what command to run when the container starts
# This will run your FastAPI server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]