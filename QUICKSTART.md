# Quick Start Guide

Get the pipeline running locally in 5 minutes.

## Prerequisites Check

```bash
# Check Python version (need 3.11+)
python --version

# Check Node.js version (need 18+)
node --version

# Check Docker is running
docker ps
```

## Step-by-Step Setup

### 1. Install Dependencies

```bash
# Python dependencies
pip install -e .

# Frontend generator dependencies
cd frontend_generator
npm install
cd ..

# Frontend dependencies
cd frontend
npm install
cd ..
```

### 2. Install Tesseract OCR

**Windows:**
```powershell
# Using Chocolatey
choco install tesseract

# Or download from: https://github.com/UB-Mannheim/tesseract/wiki
```

**macOS:**
```bash
brew install tesseract
```

**Linux:**
```bash
sudo apt-get install tesseract-ocr
```

### 3. Configure Environment

```bash
# Copy example env file
cp .env.example .env

# Edit .env and add at minimum:
# - GEMINI_API_KEY (get from https://makersuite.google.com/app/apikey)
# - VERCEL_TOKEN (optional, for deployment)
```

### 4. Start Infrastructure

```bash
# Start PostgreSQL and Redis
make dev-up

# Or manually:
docker-compose up -d
```

### 5. Run Database Migrations

```bash
make upgrade
```

### 6. Start Services

**Terminal 1 - Backend:**
```bash
make run-backend
```

**Terminal 2 - Celery Worker:**
```bash
make run-celery
```

**Terminal 3 - Frontend (Optional):**
```bash
make run-frontend
# Open http://localhost:3001 in your browser
```

### 7. Test the Pipeline

**Option A: Using the Agent (Recommended)**
```bash
# In Terminal 3
python agents/pipeline_agent.py path/to/your/resume.pdf
```

**Option B: Using cURL**
```bash
# Upload resume
curl -X POST http://localhost:8000/api/v1/resumes/upload \
  -F "file=@path/to/your/resume.pdf"

# Get job status (replace 1 with your job_id)
curl http://localhost:8000/api/v1/jobs/1

# View preview in browser
# Open: http://localhost:8000/preview/1
```

## Expected Output

When you upload a resume, you should see:

1. **Upload Response:**
   ```json
   {
     "job_id": 1,
     "status": "pending",
     "message": "Resume uploaded and processing started"
   }
   ```

2. **Job Status (after processing):**
   ```json
   {
     "job_id": 1,
     "status": "completed",
     "artifacts": {
       "resume_json": "/api/v1/artifacts/1/resume.json",
       "frontend_bundle": "/api/v1/bundles/1_bundle.zip",
       "preview": "/preview/1/index.html"
     }
   }
   ```

3. **Preview Page:** Open `http://localhost:8000/preview/1` to see the generated resume

## Troubleshooting

### "Tesseract not found"
- Ensure Tesseract is installed and in your PATH
- Windows: Add Tesseract installation directory to PATH
- Test: `tesseract --version`

### "Database connection error"
- Check Docker containers: `docker-compose ps`
- Verify DATABASE_URL in `.env`
- Restart: `docker-compose restart postgres`

### "Celery worker not processing"
- Check Redis: `docker-compose ps`
- Verify REDIS_URL in `.env`
- Check Celery logs for errors

### "GEMINI_API_KEY not set"
- The pipeline will use mock responses
- For real AI features, add your Gemini API key to `.env`

## Next Steps

- Read [README.md](README.md) for full documentation
- Check [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) for architecture details
- Review TODO comments in code for production integration points

