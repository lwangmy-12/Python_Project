FROM python:3.11-slim

WORKDIR /app

# Copy requirements from web_app directory
COPY web_app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the web_app directory contents
COPY web_app/ .
# Copy the data directory
COPY data/ /data

# Collect static files
RUN python manage.py collectstatic --noinput

# Expose port
EXPOSE 8000

# Run gunicorn
CMD ["sh", "-c", "python manage.py migrate && python manage.py import_bridges && gunicorn --bind 0.0.0.0:8000 pa_bridges_project.wsgi:application"]
