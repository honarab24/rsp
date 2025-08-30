FROM python:3.11-slim

# Install ffmpeg
RUN apt-get update \
    && apt-get install -y --no-install-recommends ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user
RUN useradd -ms /bin/bash appuser

# Set workdir
WORKDIR /app

# Copy requirements and install as non-root
COPY requirements.txt .
RUN pip install --no-cache-dir --break-system-packages -r requirements.txt

# Copy app
COPY . .

# Change ownership
RUN chown -R appuser:appuser /app

# Switch to non-root
USER appuser

EXPOSE 5000
CMD ["python", "app.py"]
