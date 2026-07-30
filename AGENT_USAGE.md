# Agent Usage

## Tools Used

- Shell commands for repository inspection, Django checks, Vite builds, and API smoke checks.
- `apply_patch` for source edits and documentation changes.
- Django shell and DRF `APIClient` for representative backend behavior checks.
- Browser screenshot evidence provided by the user for diagnosing the CORS origin mismatch.

## Representative Prompts

- "Build a wellness application where a user can create a basic profile..."
- "Check whether all the points are present in the UI or not"
- "cors error"
- "The AI workflow should..."
- "The application should preserve meal history, user corrections, previously approved plans to show these add another tab."
- "Date format should be DD-MM-YYYY"
- "Please include README.md, AGENT_USAGE.md, .env.example..."

## Work Delegated To Agents

No work was delegated to separate sub-agents. All repository inspection, implementation, verification, and documentation updates were performed in this session.

## Important Agent Mistakes Or Rejected Suggestions

- An early search over the repository included `frontend/node_modules`, producing noisy output. The follow-up inspection narrowed to project files.
- A broad React patch for adding the saved-history tab failed to apply cleanly. The file was then replaced with a complete, reviewed `main.jsx` using `apply_patch`.
- No external AI nutrition service was added. The app intentionally uses the documented local knowledge base so it does not invent nutrition values.

## Verification Of Generated Output

Verification commands used during the build:

```bash
cd backend
python3 manage.py check
python3 manage.py shell -c "from meals.services import extract_meal; print(extract_meal('chicken and rice'))"
python3 manage.py shell -c "from rest_framework.test import APIClient; response=APIClient().get('/api/meals/history/'); print(response.status_code); print(response.json().keys())"
```

```bash
cd frontend
npm run build
```

The output was checked for:

- Django settings and URL configuration loading without system-check errors.
- Meal extraction returning structured items, clarification questions, assumptions, uncertainty, and documented nutrition sources.
- The history API returning `meals` and `corrections`.
- The React app compiling successfully after UI changes.
- CORS settings allowing the observed Vite dev origin.
- Focused tests passing for meal extraction, corrections, history, meal-plan restrictions, and plan approval.
- Workflow log output showing JSON events for extraction, save, generation, and approval actions.

## Secret Handling

No API keys, passwords, tokens, or production secrets were added. Django settings now read `DJANGO_SECRET_KEY` from the environment with a development-only fallback, and `.env.example` documents required variable names without real credentials.
