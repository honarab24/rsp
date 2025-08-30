FROM python:3.10-slim

RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

# Create app user
RUN useradd -m appuser
WORKDIR /app

# Copy and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy code and give permissions
COPY . .
RUN chown -R appuser:appuser /app

# Switch to non-root
USER appuser

EXPOSE 10000
CMD ["gunicorn", "-b", "0.0.0.0:10000", "app:app"]
