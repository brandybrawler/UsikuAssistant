# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements.txt file into the container
COPY cookbook/llms/ollama/rag/requirements.txt ./

# Install system dependencies and Python packages
RUN apt-get update && \
    apt-get install -y wget libgl1-mesa-glx poppler-utils libglib2.0-0 libxkbcommon-x11-0 libxrender1 libxcb1 libfontconfig1 libfreetype6 libxext6 libx11-xcb1 && \
    pip3 install pyqt5 pyqtwebengine && \
    pip install -r requirements.txt && \
    pip install websockets && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy the rest of the application code into the container
COPY . .

# Set environment variable to specify the display (necessary for GUI apps)
ENV DISPLAY=:0

# Run the application
CMD ["python3", "cookbook/llms/ollama/rag/app.py"]
