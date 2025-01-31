FROM python:3.11

# Install PortAudio system dependencies
RUN apt-get update && apt-get install -y portaudio19-dev build-essential

# Set up a working directory
WORKDIR /app

# Copy project files into the container
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Command to run the app
CMD ["python", "app.py"]
