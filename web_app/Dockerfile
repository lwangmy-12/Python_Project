FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput

# Expose port
EXPOSE 8000

# Run gunicorn
CMD ["sh", "-c", "python manage.py migrate && python manage.py import_bridges && gunicorn --bind 0.0.0.0:8000 pa_bridges_project.wsgi:application"]
