FROM python:3.10-slim

# Prevent Python from writing .pyc files and force stdout/stderr to be unbuffered
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Create an unprivileged user
RUN useradd --create-home appuser
WORKDIR /home/appuser/app

# Copy and install requirements first to leverage Docker layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app.py .
COPY static/ ./static/
COPY templates/ ./templates/

# Enforce strict ownership
RUN chown -R appuser:appuser /home/appuser/app
USER appuser

EXPOSE 5000

# For a strict production deployment, swap this to a WSGI server like Gunicorn:
# CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]
CMD ["python", "app.py"]