# Preparation for Project Sharing (Git & Docker)

The goal is to prepare the chatbot project so that the team can easily integrate it into their platform. This involves version management setup (Git) and environment containerization (Docker) to ensure everyone has the same setup.

## Proposed Changes

### Configuration Files
- **[NEW] `.gitignore`**: Will suppress tracked files that shouldn't be shared: `venv/`, [.env](file:///home/nourhene/chatbot_moliere/.env), `__pycache__/`, `db/`, `.DS_Store`, etc.
- **[NEW] `requirements.txt`**: Will define all Python packages required to run the Backend API (`fastapi`, `uvicorn`, `langchain`, `langchain-community`, `langchain-ollama`, `langchain-groq`, `python-dotenv`, `chromadb`, `pypdf`, `pydantic`). We will base this on the actual virtual environment's pip freeze.
- **[NEW] `.env.example`**: A safe template file so the team knows what environment variables are needed (`GROQ_API_KEY=`).

### Docker & Documentation
- **[NEW] `Dockerfile`**: Uses `python:3.10-slim`. Copies requirements, installs them, copies the app code, and runs `uvicorn main:app --host 0.0.0.0 --port 8001`.
- **[NEW] `README.md`**: Provides clear instructions on how to install dependencies, set up the [.env](file:///home/nourhene/chatbot_moliere/.env) file, and run the app either locally or via Docker. It will also highlight the Swagger UI available at `/docs` which is critical for integration.

## Verification Plan
### Manual Verification
- Review the content of `requirements.txt` to ensure no internal dependencies are missing.
- Review the `Dockerfile` for build correctness.
- Review `.gitignore` to ensure [.env](file:///home/nourhene/chatbot_moliere/.env) and `db/` are properly ignored.
