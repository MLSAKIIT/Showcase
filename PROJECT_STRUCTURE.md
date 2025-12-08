# Project Structure

```
showcase/
├── app/                          # Main application package
│   ├── __init__.py
│   ├── main.py                   # FastAPI application entry point
│   ├── database.py               # Database configuration & session management
│   ├── models.py                 # SQLAlchemy models (Job, Artifact, Resume, ChatMessage)
│   ├── tasks.py                  # Celery background tasks
│   ├── ai_pipeline.py            # Main pipeline orchestration
│   ├── api/                      # API routes
│   │   ├── __init__.py
│   │   ├── routes.py             # FastAPI route handlers
│   │   └── dependencies.py       # API dependencies
│   ├── ai_providers/             # AI provider adapters
│   │   ├── __init__.py
│   │   └── gemini_adapter.py     # Gemini AI adapter (mock for testing)
│   ├── ocr/                      # OCR adapters
│   │   ├── __init__.py
│   │   └── ocr_adapter.py        # OCR adapter with pytesseract + cloud providers
│   └── frontend_generator/       # Frontend generation logic
│       ├── __init__.py
│       └── generator.py          # Python frontend bundle generator
│
├── agents/                       # Agent orchestration
│   ├── __init__.py
│   └── pipeline_agent.py        # Agno agent example for pipeline orchestration
│
├── frontend/                     # React + Vite frontend UI
│   ├── src/
│   │   ├── components/         # React components
│   │   │   ├── UploadForm.jsx  # Resume upload form
│   │   │   ├── JobList.jsx     # Job list sidebar
│   │   │   └── JobDetails.jsx  # Job details and preview
│   │   ├── api/
│   │   │   └── client.js       # API client (axios)
│   │   ├── App.jsx             # Main app component
│   │   └── main.jsx            # Entry point
│   ├── package.json
│   ├── vite.config.js          # Vite configuration
│   └── tailwind.config.js      # Tailwind CSS config
│
├── frontend_generator/           # Node.js frontend generator
│   ├── package.json
│   └── generate.js              # Maps UI JSON -> React/Next.js bundle
│
├── alembic/                      # Database migrations
│   ├── env.py
│   ├── script.py.mako
│   └── versions/                # Migration files
│
├── tests/                        # Test suite
│   ├── __init__.py
│   └── test_api.py              # Basic API tests
│
├── scripts/                      # Setup scripts
│   ├── setup.sh                 # Bash setup script
│   └── setup.ps1                # PowerShell setup script
│
├── docker-compose.yml           # Postgres + Redis services
├── Makefile                     # Development commands
├── pyproject.toml               # Python dependencies & project config
├── alembic.ini                  # Alembic configuration
├── .env.example                 # Environment variables template
├── .gitignore                   # Git ignore rules
└── README.md                    # Project documentation
```

## Key Files

### Backend Core
- `app/main.py`: FastAPI app with CORS, routes, static file serving
- `app/models.py`: Database models for Job, Artifact, Resume, ChatMessage
- `app/database.py`: SQLAlchemy engine and session management
- `app/tasks.py`: Celery tasks for async processing
- `app/ai_pipeline.py`: Main pipeline that orchestrates OCR → AI → Frontend

### API Routes
- `app/api/routes.py`: 
  - `POST /api/v1/resumes/upload` - Upload resume, returns job_id
  - `GET /api/v1/jobs/{job_id}` - Get job status, artifacts, logs
  - `GET /preview/{job_id}` - Preview page (static)
  - `POST /api/v1/jobs/{job_id}/deploy` - Trigger Vercel deploy

### AI & OCR
- `app/ai_providers/gemini_adapter.py`: Gemini adapter (returns mock data for testing)
- `app/ocr/ocr_adapter.py`: OCR adapter with pytesseract fallback + cloud provider interfaces

### Frontend Generation
- `app/frontend_generator/generator.py`: Python wrapper that calls Node.js generator
- `frontend_generator/generate.js`: Node.js script that generates React/Next.js bundle

### Agent Orchestration
- `agents/pipeline_agent.py`: Example agent that orchestrates upload → process → deploy

## Data Flow

1. **Upload** → `POST /api/v1/resumes/upload` → Creates Job → Queues Celery task
2. **Processing** → Celery worker → `process_resume_pipeline()`:
   - OCR extraction (`OCRAdapter`)
   - Structured JSON (`GeminiAdapter.generate_structured_resume()`)
   - Content enhancement (`GeminiAdapter.enhance_content()`)
   - Frontend JSON (`GeminiAdapter.generate_frontend_json()`)
   - Validation (`GeminiAdapter.validate_and_fix_ui()`)
   - Frontend generation (`generate_frontend_bundle()`)
   - Preview generation
3. **Status Check** → `GET /api/v1/jobs/{job_id}` → Returns status, artifacts, logs
4. **Preview** → `GET /preview/{job_id}` → Serves generated HTML
5. **Deploy** → `POST /api/v1/jobs/{job_id}/deploy` → Queues Vercel deployment task

## Environment Variables

See `.env.example` for all required variables:
- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string
- `GEMINI_API_KEY`: Google Gemini API key
- `VERCEL_TOKEN`: Vercel deployment token
- `VERCEL_ORG_ID`: Vercel organization ID
- `VERCEL_PROJECT_ID`: Vercel project ID

## Development Workflow

1. Start infrastructure: `make dev-up`
2. Run migrations: `make upgrade`
3. Start backend: `make run-backend`
4. Start Celery: `make run-celery`
5. Run agent: `make run-agent` or `python agents/pipeline_agent.py <resume.pdf>`

