# Nutrition Planning Assistant

Knowledge-grounded wellness app with a React frontend and Django REST backend.

## Backend

```bash
cd backend
python3 manage.py migrate
python3 manage.py seed_nutrition
python3 manage.py runserver
```

## Frontend

```bash
cd frontend
npm install
npm run dev
```

The frontend expects the backend at `http://127.0.0.1:8000/api`.

## Safety

This app supports general wellness tracking only. It does not provide medical diagnosis, treatment, or guaranteed health outcomes.
