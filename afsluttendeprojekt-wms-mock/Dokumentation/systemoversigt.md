# Systemoversigt – WMS API Mock

## Flow

1. Bruger logger ind via Flask-dashboard.
2. Flask sender `POST` til mock-API for at hente token.
3. Flask anvender token til at hente data om enheder via mock-API.
4. Dashboard viser status, opdateringer og mulighed for brugerstyring.

## Komponenter

- `app.py`: Flask backend
- `templates/`: HTML-views
- `models.py`: SQLAlchemy-database
- `postman/`: Mock-data og testkald
