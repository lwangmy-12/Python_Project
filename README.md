# PA Bridge Information Dashboard

## Overview
This project is a Django-based web application for analyzing and visualizing Pennsylvania bridge data. It provides an interactive dashboard with maps and charts, detailed bridge information, a feedback submission system, and data export capabilities.

## Requirements Met
- **Django Web Application**: Built using Django 5.0+.
- **Form/Data Submission**: Users can submit feedback/reviews for individual bridges.
- **Dashboard**: Interactive Leaflet map and Chart.js visualization of bridge conditions.
- **Admin Interface**: Standard Django admin enabled.
- **Models**: Two models: `Bridge` (bridge data) and `Feedback` (user reviews).
- **Data Export**: Export filtered bridge data to XLSX format.
- **Documentation**: This README explains all features.
- **Git Repository**: Project is version controlled.
- **Release**: Tagged as a release.
- **ERD**: See Database Schema section below.
- **Portable**: Dockerized application.
- **CI/CD**: GitHub Actions workflow for building and testing.
- **Testing**: Tests implemented using `pytest-django`.

## Database Schema (ERD)
The application uses two main entities:

1. **Bridge**: Stores NBI bridge data (Structure Number, Location, Condition, Year, etc.).
2. **Feedback**: Stores user reviews linked to a specific Bridge.

```mermaid
erDiagram
    BRIDGE ||--o{ FEEDBACK : has
    BRIDGE {
        string structure_number
        int data_year
        string location
        float latitude
        float longitude
        string deck_cond
        ...
    }
    FEEDBACK {
        string name
        string email
        int rating
        string comment
        datetime created_at
    }
```

## Setup & Installation

### Using Docker (Recommended)
1. Ensure Docker and Docker Compose are installed.
2. Build and run the container:
   ```bash
   cd web_app
   docker-compose up --build
   ```
3. Access the application at `http://localhost:8000`.

### Manual Setup
1. Create a virtual environment and install dependencies:
   ```bash
   cd web_app
   pip install -r requirements.txt
   ```
2. Run migrations:
   ```bash
   python manage.py migrate
   ```
3. Import data (ensure `data/pa_bridges_clean.db` exists):
   ```bash
   python manage.py import_bridges
   ```
4. Run the server:
   ```bash
   python manage.py runserver
   ```

## Features
- **Dashboard**: Filter bridges by year, view on map, see condition statistics.
- **Bridge Details**: Click on a map marker or use the search to view details.
- **Feedback**: Submit ratings and comments on bridge detail pages.
- **Export**: Download the currently filtered dataset as an Excel file.
- **Admin**: Manage bridges and feedback via `/admin`.

## Testing
Run tests using pytest:
```bash
cd web_app
pytest
```
