#!/bin/bash
# Setup script for local development

set -e

echo "🚀 Setting up Resume Processing Pipeline..."

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -e .

# Install frontend generator dependencies
echo "📦 Installing frontend generator dependencies..."
cd frontend_generator
npm install
cd ..

# Create .env if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env from .env.example..."
    cp .env.example .env
    echo "⚠️  Please edit .env and add your API keys!"
fi

# Start Docker services
echo "🐳 Starting Docker services..."
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 5

# Run migrations
echo "🗄️  Running database migrations..."
alembic upgrade head

echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Edit .env and add your API keys"
echo "  2. Run: make run-backend (in one terminal)"
echo "  3. Run: make run-celery (in another terminal)"
echo "  4. Test: python agents/pipeline_agent.py <resume_file.pdf>"

