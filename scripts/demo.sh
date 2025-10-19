#!/bin/bash

# TypeFlow Demo Script
# This script demonstrates the full TypeFlow setup and functionality

set -e

echo "🚀 TypeFlow Demo Script Starting..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    print_error "docker-compose is not installed. Please install Docker and docker-compose first."
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    print_warning ".env file not found. Creating from .env.example..."
    cp .env.example .env
fi

print_status "Starting TypeFlow services..."

# Start services
docker-compose up -d

print_status "Waiting for services to be ready..."
sleep 10

# Wait for PostgreSQL to be ready
print_status "Waiting for PostgreSQL to be ready..."
for i in {1..30}; do
    if docker-compose exec -T db pg_isready -U typeflow > /dev/null 2>&1; then
        print_success "PostgreSQL is ready!"
        break
    fi
    if [ $i -eq 30 ]; then
        print_error "PostgreSQL failed to start within 30 seconds"
        exit 1
    fi
    sleep 1
done

# Wait for Redis to be ready
print_status "Waiting for Redis to be ready..."
for i in {1..30}; do
    if docker-compose exec -T redis redis-cli ping > /dev/null 2>&1; then
        print_success "Redis is ready!"
        break
    fi
    if [ $i -eq 30 ]; then
        print_error "Redis failed to start within 30 seconds"
        exit 1
    fi
    sleep 1
done

# Run database migrations
print_status "Running database migrations..."
docker-compose exec -T backend alembic upgrade head

# Create admin user
print_status "Creating admin user..."
docker-compose exec -T backend python -c "
import asyncio
from app.core.database import AsyncSessionLocal
from app.models.users import User, AuthProvider, UserRole
from app.core.security import get_password_hash

async def create_admin():
    async with AsyncSessionLocal() as session:
        # Check if admin already exists
        from sqlalchemy import select
        result = await session.execute(
            select(User).where(User.email == 'admin@typeflow.local')
        )
        if result.scalar_one_or_none():
            print('Admin user already exists')
            return
        
        admin = User(
            display_name='Administrator',
            email='admin@typeflow.local',
            auth_provider=AuthProvider.GOOGLE,
            role=UserRole.SUPER_ADMIN,
            password_hash=get_password_hash('mabuchi_0315')
        )
        session.add(admin)
        await session.commit()
        print('Admin user created successfully')

asyncio.run(create_admin())
"

# Load sample articles
print_status "Loading sample articles..."
docker-compose exec -T backend python -c "
import asyncio
import os
from pathlib import Path
from app.core.database import AsyncSessionLocal
from app.models.articles import Article, Language, ArticleStatus
from app.models.users import User, UserRole
from sqlalchemy import select

async def load_articles():
    async with AsyncSessionLocal() as session:
        # Get admin user
        result = await session.execute(
            select(User).where(User.role == UserRole.SUPER_ADMIN)
        )
        admin = result.scalar_one_or_none()
        if not admin:
            print('No admin user found')
            return
        
        # Sample articles
        articles = [
            {
                'title': 'The Art of Touch Typing',
                'language': Language.EN,
                'content': 'Touch typing is the practice of typing without looking at the keyboard...',
                'status': ArticleStatus.PUBLISHED
            },
            {
                'title': 'JavaScript Array Methods',
                'language': Language.CODE,
                'content': '// JavaScript - Array Methods Practice\nconst numbers = [1, 2, 3, 4, 5];',
                'status': ArticleStatus.PUBLISHED
            },
            {
                'title': '打字技能的重要性',
                'language': Language.ZH_TW,
                'content': '在數位時代，打字技能已成為一項基本能力。無論是學生撰寫報告...',
                'status': ArticleStatus.PUBLISHED
            }
        ]
        
        for article_data in articles:
            # Check if article already exists
            result = await session.execute(
                select(Article).where(Article.title == article_data['title'])
            )
            if result.scalar_one_or_none():
                continue
                
            article = Article(
                title=article_data['title'],
                language=article_data['language'],
                content=article_data['content'],
                status=article_data['status'],
                submitted_by=admin.id,
                reviewed_by=admin.id
            )
            session.add(article)
        
        await session.commit()
        print('Sample articles loaded successfully')

asyncio.run(load_articles())
"

# Check service status
print_status "Checking service status..."

# Frontend
FRONTEND_PORT=${FRONTEND_PORT:-12012}
if curl -s -o /dev/null -w "%{http_code}" "http://localhost:$FRONTEND_PORT" | grep -q "200"; then
    print_success "Frontend is running on http://localhost:$FRONTEND_PORT"
else
    print_warning "Frontend may not be fully ready yet on port $FRONTEND_PORT"
fi

# Backend
BACKEND_PORT=${BACKEND_PORT:-12014}
if curl -s -o /dev/null -w "%{http_code}" "http://localhost:$BACKEND_PORT/healthz" | grep -q "200"; then
    print_success "Backend is running on http://localhost:$BACKEND_PORT"
else
    print_warning "Backend may not be fully ready yet on port $BACKEND_PORT"
fi

# Display service information
echo ""
echo "🎉 TypeFlow Demo Setup Complete!"
echo ""
echo "📊 Service URLs:"
echo "   Frontend: http://localhost:$FRONTEND_PORT"
echo "   Backend API: http://localhost:$BACKEND_PORT"
echo "   API Docs: http://localhost:$BACKEND_PORT/docs"
echo ""
echo "👤 Admin Login:"
echo "   Email: admin@typeflow.local"
echo "   Password: admin123"
echo ""
echo "🐳 Docker Services:"
docker-compose ps
echo ""
echo "📝 To stop services:"
echo "   docker-compose down"
echo ""
echo "📚 To view logs:"
echo "   docker-compose logs -f"
echo ""

# Optional: Open browser
if command -v xdg-open &> /dev/null; then
    read -p "Open frontend in browser? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        xdg-open "http://localhost:$FRONTEND_PORT"
    fi
elif command -v open &> /dev/null; then
    read -p "Open frontend in browser? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        open "http://localhost:$FRONTEND_PORT"
    fi
fi

print_success "Demo script completed! Happy typing! 🎯"