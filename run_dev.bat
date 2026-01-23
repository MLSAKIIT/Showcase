@echo off
echo ==========================================
echo 🚀 Showcase AI - Windows Development Start
echo ==========================================

echo [1/3] Starting Infrastructure (Docker)...
docker-compose up -d

echo Waiting 5 seconds for Database to initialize...
timeout /t 5 /nobreak >nul

echo [2/3] Running Database Migrations...
alembic upgrade head

echo [3/3] Launching Services in new windows...

:: Start Backend
start "Showcase Backend (Port 8000)" cmd /k "uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

:: Start Celery Worker (Pool: Solo for Windows compatibility)
:: Note: Windows often has issues with Celery prefork, using --pool=solo
start "Showcase Worker" cmd /k "celery -A app.tasks worker --loglevel=info --pool=solo"

:: Start Frontend
start "Showcase Frontend (Port 5173)" cmd /k "cd frontend && npm run dev"

echo.
echo ✅ All services launched!
echo ------------------------------------------
echo 🌍 Frontend: http://localhost:5173
echo 🔌 Backend:  http://localhost:8000/docs
echo ------------------------------------------
echo Press any key to exit this launcher (services will keep running)...
pause >nul
