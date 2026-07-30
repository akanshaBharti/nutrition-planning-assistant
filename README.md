# Nutrition Planning Assistant

Knowledge-grounded wellness app with a React frontend and Django REST backend. It helps a user save basic nutrition preferences, extract meal items from text, review and correct nutrition estimates, compare daily intake against a calorie target, and generate a next-day meal plan from a documented starter knowledge base.

This app supports general wellness tracking only. It does not provide medical diagnosis, treatment, or guaranteed health outcomes.

## Setup

### Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 manage.py migrate
python3 manage.py seed_nutrition
python3 manage.py runserver 127.0.0.1:8000
```

If port `8000` is already in use, either stop the existing process or run Django on another valid port, for example:

```bash
python3 manage.py runserver 127.0.0.1:8001
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The frontend defaults to `http://127.0.0.1:8000/api`. To point it elsewhere, set `VITE_API_BASE`.

## Configuration

Copy `.env.example` into the environment mechanism used by your shell, host, or process manager. Do not commit real secrets.

Required and supported names:

- `DJANGO_SECRET_KEY`
- `DJANGO_DEBUG`
- `DJANGO_ALLOWED_HOSTS`
- `DJANGO_CORS_ALLOWED_ORIGINS`
- `WORKFLOW_LOG_LEVEL`
- `VITE_API_BASE`

The repository ignores `backend/.env`, `backend/.env.local`, `frontend/node_modules`, `frontend/dist`, and the local SQLite database.

## Architecture

- `backend/config`: Django settings and URL routing.
- `backend/profiles`: single-user profile with calorie target, dietary preferences, allergies, and foods to avoid.
- `backend/nutrition`: documented nutrition knowledge base and seed command.
- `backend/meals`: meal extraction, review/save API, daily intake, saved history, and user correction persistence.
- `backend/plans`: next-day meal-plan generation, approval, rejection, and persisted plan records.
- `frontend/src/main.jsx`: React single-page UI with Tracker and Saved History tabs.
- `frontend/src/styles.css`: application styling.

The backend uses SQLite for local persistence. The frontend talks to the Django REST API through JSON endpoints.

## Completed Scope

- Create and update a basic wellness profile.
- Record a meal in comma/newline/`and` separated text.
- Extract structured food items, quantities, units, preparation methods, calories, and macros.
- Ask clarification questions when quantity or preparation method is important but missing.
- Retrieve nutrition values from the seeded `NutritionItem` knowledge base.
- Avoid inventing values for unknown foods; unknown entries are marked uncertain and require manual correction.
- Show assumptions, uncertainty, and source information during review.
- Allow calorie, quantity, method, and macro corrections before saving a meal.
- Preserve meal history, user calorie corrections, and previously approved plans.
- Show daily intake against the saved calorie target.
- Generate a draft meal plan for the next day using saved preferences and restrictions.
- Approve or reject generated meal plans.
- Display dates in `DD-MM-YYYY` format in the UI.
- Emit structured JSON AI-workflow events for extraction, meal save/corrections, plan generation, and plan review.
- Provide visible loading, empty, validation, success, warning, and failure states for the main workflows.

## Intentionally Excluded Scope

- Medical advice, diagnosis, treatment recommendations, or clinical risk scoring.
- Authentication, multi-user accounts, and role-based authorization.
- External AI model calls or external nutrition APIs.
- Barcode scanning, image-based meal recognition, and grocery ordering.
- Production-grade diet planning optimization.
- Automatic correction learning beyond preserving user correction records.

## Tests And Verification

Run backend checks:

```bash
cd backend
python3 manage.py check
```

Run the frontend production build:

```bash
cd frontend
npm run build
```

Useful manual API checks:

```bash
cd backend
python3 manage.py shell -c "from meals.services import extract_meal; print(extract_meal('chicken and rice'))"
python3 manage.py shell -c "from rest_framework.test import APIClient; r=APIClient().get('/api/meals/history/'); print(r.status_code, r.json().keys())"
```

Focused backend tests cover important behavior:

- Structured extraction and clarification.
- Unknown foods marked uncertain instead of invented.
- User corrections persisted into history.
- Meal plan restrictions and approval.

Run them with:

```bash
cd backend
python3 manage.py test meals plans
```

The project has also been verified through Django system checks, Vite production builds, and direct service/API smoke checks.

## Structured Logs

AI-workflow events are emitted on the `wellness.workflow` logger as JSON payloads inside normal log lines. Representative events:

- `meal_extract_started`
- `meal_extract_completed`
- `meal_save_started`
- `meal_save_completed`
- `meal_plan_generation_started`
- `meal_plan_generation_completed`
- `meal_plan_reviewed`

Control verbosity with `WORKFLOW_LOG_LEVEL`.

## Known Limitations

- Preference handling is intentionally small: vegetarian and vegan are enforced explicitly; other preference tags are not fully optimized.
- The meal parser is rule-based and supports a limited set of quantity words, units, and preparation keywords.
- The nutrition knowledge base is intentionally small and must be seeded with `python3 manage.py seed_nutrition`.
- The app currently stores one shared profile using `pk=1`; it is not multi-user.
- `.env` files are not loaded automatically by Django in this project; provide environment variables through your shell or deployment platform.
- SQLite is suitable for local development and demos, not high-concurrency production use.

## Deployment Details

For production:

1. Set `DJANGO_SECRET_KEY` to a real secret through the deployment environment.
2. Set `DJANGO_DEBUG=false`.
3. Set `DJANGO_ALLOWED_HOSTS` to the backend hostnames.
4. Set `DJANGO_CORS_ALLOWED_ORIGINS` to the deployed frontend origins.
5. Run migrations and seed the nutrition KB if needed.
6. Serve Django with a production WSGI or ASGI server.
7. Build the frontend with `npm run build` and serve `frontend/dist` from a static host.
8. Set `VITE_API_BASE` at frontend build time if the API is not `http://127.0.0.1:8000/api`.

Deployment status for this workspace: the app is prepared and verified locally, but no live full-stack deployment URL is committed in the repository. A working deployment requires a Python-capable host for Django plus a static host for `frontend/dist`; static frontend-only hosting is insufficient unless `VITE_API_BASE` points to a live Django API.

Never commit API keys, passwords, tokens, production secrets, or real `.env` files.
