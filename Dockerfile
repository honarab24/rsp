FROM python:3.11-slim

# Install ffmpeg (needed for decryption + HLS)
RUN apt-get update \
    && apt-get install -y --no-install-recommends ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Set workdir
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app source
COPY app.py .

# Expose Flask port
EXPOSE 5000

# Run Flask app
CMD ["python", "app.py"]
