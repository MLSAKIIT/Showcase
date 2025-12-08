# PowerShell setup script for Windows

Write-Host "🚀 Setting up Resume Processing Pipeline..." -ForegroundColor Green

# Check Python version
$pythonVersion = python --version 2>&1
Write-Host "Python version: $pythonVersion"

# Install Python dependencies
Write-Host "📦 Installing Python dependencies..." -ForegroundColor Yellow
pip install -e .

# Install frontend generator dependencies
Write-Host "📦 Installing frontend generator dependencies..." -ForegroundColor Yellow
Set-Location frontend_generator
npm install
Set-Location ..

# Create .env if it doesn't exist
if (-not (Test-Path .env)) {
    Write-Host "📝 Creating .env from .env.example..." -ForegroundColor Yellow
    Copy-Item .env.example .env
    Write-Host "⚠️  Please edit .env and add your API keys!" -ForegroundColor Red
}

# Start Docker services
Write-Host "🐳 Starting Docker services..." -ForegroundColor Yellow
docker-compose up -d

# Wait for services to be ready
Write-Host "⏳ Waiting for services to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Run migrations
Write-Host "🗄️  Running database migrations..." -ForegroundColor Yellow
alembic upgrade head

Write-Host "✅ Setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:"
Write-Host "  1. Edit .env and add your API keys"
Write-Host "  2. Run: make run-backend (in one terminal)"
Write-Host "  3. Run: make run-celery (in another terminal)"
Write-Host "  4. Test: python agents/pipeline_agent.py <resume_file.pdf>"

