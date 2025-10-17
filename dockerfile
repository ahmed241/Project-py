# Use an official Python image as the base.
FROM python:3.10-slim

# Set the working directory inside the container to /app
WORKDIR /app

# Install system dependencies required by Manim: FFmpeg for video and a full LaTeX suite for math text.
# This is the step that makes Docker essential for Manim.
RUN apt-get update && apt-get install -y \
    ffmpeg \
    texlive-full \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container first.
# This is a Docker optimization: this layer is only re-built if requirements change.
COPY requirements.txt requirements.txt

# Install all the Python packages from your requirements file.
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your project's code into the container.
COPY . .

# Expose port 7000 so the web server can be accessed from outside the container.
EXPOSE 7000

# The command to run when the container starts.
# This starts your FastAPI server using Uvicorn.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7000"]