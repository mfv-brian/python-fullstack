# Full-Stack FastAPI - Multi-Tenant Application

A modern full-stack application with FastAPI backend and React frontend, featuring multi-tenant architecture and database optimization.

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Node.js 18+ (for local development)
- Python 3.8+ (for local development)

### 1. Clone and Setup
```bash
git clone <repository-url>
cd full-stack-fastapi
```

### 2. Environment Configuration
```bash
# Copy environment files
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env

# Edit backend environment
nano backend/.env
```

**Backend `.env` file:**
```env
DATABASE_URL=postgresql://postgres:changethis@localhost:5432/app
SECRET_KEY=changethis
FIRST_SUPERUSER=admin@example.com
FIRST_SUPERUSER_PASSWORD=changethis
```

**Frontend `.env` file:**
```env
VITE_API_URL=http://localhost:8000
```

## 🔧 Development Mode

### Option 1: Docker Compose (Recommended)
```bash
# Start all services
docker-compose up -d

# Watch for changes (auto-reload)
docker-compose watch

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Stop services
docker-compose down
```

### Option 2: Local Development
```bash
# Start PostgreSQL
docker-compose up -d postgres

# Backend setup
cd backend
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Frontend setup (new terminal)
cd frontend
npm install
npm run dev
```

### Development URLs
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Database**: localhost:5432

### Default Login
- **Email**: admin@example.com
- **Password**: changethis

## 🚀 Production Mode

### 1. Build Production Images
```bash
# Build all services
docker-compose build

# Build specific service
docker-compose build backend
docker-compose build frontend
```

### 2. Production Environment
```bash
# Copy production environment
cp .env.example .env.prod

# Edit production environment
nano .env.prod
```

**Production `.env.prod`:**
```env
# Database
DATABASE_URL=postgresql://user:password@db:5432/app
POSTGRES_PASSWORD=secure-password

# Security
SECRET_KEY=your-secure-secret-key
FIRST_SUPERUSER=admin@yourdomain.com
FIRST_SUPERUSER_PASSWORD=secure-password

# Frontend
VITE_API_URL=https://api.yourdomain.com
```

### 3. Deploy with Traefik
```bash
# Deploy with reverse proxy
docker-compose -f docker-compose.yml -f docker-compose.traefik.yml up -d

# Deploy without Traefik
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### 4. Database Setup
```bash
# Run migrations
docker-compose exec backend alembic upgrade head

# Initialize data
docker-compose exec backend python -m app.initial_data
```

## 🛠️ Common Commands

### Docker Operations
```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# Restart services
docker-compose restart

# View logs
docker-compose logs -f

# Execute commands in containers
docker-compose exec backend bash
docker-compose exec frontend bash
docker-compose exec postgres psql -U postgres -d app
```

### Database Operations
```bash
# Run migrations
docker-compose exec backend alembic upgrade head

# Create new migration
docker-compose exec backend alembic revision --autogenerate -m "description"

# Rollback migration
docker-compose exec backend alembic downgrade -1

# Reset database
docker-compose exec backend alembic downgrade base
docker-compose exec backend alembic upgrade head
```

### Development Workflow
```bash
# Backend development
docker-compose exec backend bash
# Inside container: uvicorn app.main:app --reload

# Frontend development
docker-compose exec frontend bash
# Inside container: npm run dev

# Database access
docker-compose exec postgres psql -U postgres -d app
```

### Testing
```bash
# Backend tests
docker-compose exec backend pytest

# Frontend tests
docker-compose exec frontend npm test

# E2E tests
docker-compose exec frontend npm run test:e2e
```

## 📁 Project Structure
```
full-stack-fastapi/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # API routes
│   │   │   ├── core/           # Configuration
│   │   │   ├── models.py       # Database models
│   │   │   └── main.py         # Application entry
│   │   ├── alembic/            # Database migrations
│   │   ├── .env                # Environment variables
│   │   └── requirements.txt    # Python dependencies
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── routes/         # Application routes
│   │   └── main.tsx        # Application entry
│   ├── .env                # Environment variables
│   └── package.json        # Node dependencies
├── docker-compose.yml      # Development services
├── docker-compose.traefik.yml  # Production with Traefik
└── README.md              # This file
```

## 🔧 Configuration

### Backend Configuration
```python
# backend/app/core/config.py
class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    FIRST_SUPERUSER: str
    FIRST_SUPERUSER_PASSWORD: str
```

### Frontend Configuration
```typescript
// frontend/src/config.ts
export const config = {
  apiUrl: import.meta.env.VITE_API_URL,
}
```

### Docker Configuration
```yaml
# docker-compose.yml
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:changethis@postgres:5432/app
    depends_on:
      - postgres

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - VITE_API_URL=http://localhost:8000
```

## 🚨 Troubleshooting

### Common Issues
```bash
# Port already in use
sudo lsof -i :8000
sudo lsof -i :3000

# Database connection issues
docker-compose exec postgres pg_isready -U postgres

# Container not starting
docker-compose logs backend
docker-compose logs frontend

# Permission issues
sudo chown -R $USER:$USER .
```

### Reset Everything
```bash
# Stop and remove everything
docker-compose down -v
docker system prune -a

# Rebuild from scratch
docker-compose build --no-cache
docker-compose up -d
```

## 📚 Documentation

- **API Documentation**: http://localhost:8000/docs
- **Backend README**: [backend/README.md](backend/README.md)
- **Frontend README**: [frontend/README.md](frontend/README.md)
- **Database Schema**: [backend/MULTI_TENANT_SCHEMA.md](backend/MULTI_TENANT_SCHEMA.md)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

---

**Built with FastAPI, React, and PostgreSQL.**
