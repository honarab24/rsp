FROM python:3.11-slim

# Install ffmpeg
RUN apt-get update \
    && apt-get install -y --no-install-recommends ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir --break-system-packages -r requirements.txt

# Install gunicorn for production
RUN pip install gunicorn

# Copy app
COPY . .

# Expose Flask port
EXPOSE 5000

# Use Gunicorn to serve Flask app on Render
CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]
