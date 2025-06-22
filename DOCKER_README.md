# Docker Setup for Load Website

This document explains how to dockerize and run the Load Website application.

## Architecture

The application consists of two main components:
- **Backend**: Flask API (Python) - serves data endpoints
- **Frontend**: PHP web interface - displays charts and statistics

## Prerequisites

- Docker
- Docker Compose

## Quick Start

1. **Build and run the application:**
   ```bash
   docker-compose up --build
   ```

2. **Access the application:**
   - Frontend: http://localhost
   - Backend API: http://localhost:5000

3. **Stop the application:**
   ```bash
   docker-compose down
   ```

## Docker Configuration

### Backend (Flask API)
- **Image**: `python:3.9-slim`
- **Port**: 5000
- **Dependencies**: See `backend/requirements.txt`
- **Database**: SQLite (persisted via Docker volume)

### Frontend (PHP/Apache)
- **Image**: `php:8.1-apache`
- **Port**: 80
- **Features**: Apache with PHP support

### Docker Compose Services

```yaml
services:
  backend:
    - Flask API on port 5000
    - Persistent database storage
    - Development mode enabled
    
  frontend:
    - PHP/Apache on port 80
    - Depends on backend service
    - Serves static files and PHP pages
```

## Development Workflow

User Docker Compose Bake for faster builds [^1]
```bash
# For faster builds (optional)
set COMPOSE_BAKE=true  # Windows
export COMPOSE_BAKE=true  # Linux/Mac
```

### Running in Development Mode
```bash
# Start services with volume mounts for live code changes
docker-compose up --build

# View logs
docker-compose logs -f

# Access backend container
docker-compose exec backend bash

# Access frontend container
docker-compose exec frontend bash
```

### Production Deployment
1. Update `docker-compose.yml` to set `FLASK_ENV=production`
2. Remove volume mounts for code directories
3. Use proper environment variables for secrets

## Database Management

The SQLite database is stored in a Docker volume (`backend_data`). To manage it:

```bash
# Access database from backend container
docker-compose exec backend sqlite3 database.db

# Backup database
docker-compose exec backend cp database.db database_backup.db

# Restore database
docker-compose exec backend cp database_backup.db database.db
```

## Troubleshooting

### Common Issues

1. **Port conflicts**: Ensure ports 80 and 5000 are available
2. **Permission issues**: Check file permissions in mounted volumes
3. **Database issues**: Verify database file exists and is accessible

### Debug Commands

```bash
# Check container status
docker-compose ps

# View detailed logs
docker-compose logs backend
docker-compose logs frontend

# Rebuild specific service
docker-compose build backend

# Clean up everything
docker-compose down -v
docker system prune -a
```

## Environment Variables

### Backend Environment Variables
- `FLASK_APP`: Application entry point
- `FLASK_ENV`: Environment (development/production)

### Frontend Environment Variables
- Apache configuration is handled via Dockerfile

## Network Configuration

Services communicate via Docker's internal network:
- Frontend → Backend: `http://backend:5000`
- External access: `http://localhost` (frontend) and `http://localhost:5000` (backend)

## Data Persistence

- Database files are stored in Docker volumes
- Code changes are reflected immediately in development mode
- Static assets are served from the frontend container

## Security Considerations

- Use environment variables for sensitive data
- Consider using secrets management in production
- Implement proper CORS policies
- Use HTTPS in production environments 




[^1] 🔥 What is Docker Compose Bake?
Bake is Docker's next-generation build system that provides:
Faster builds through advanced caching and parallelization
Better performance than traditional docker-compose build
Enhanced build features like buildx integration
Improved dependency management
🚀 Key Benefits:
1. Speed Improvements
Parallel builds - Multiple services build simultaneously
Advanced caching - Better layer caching strategies
Incremental builds - Only rebuilds what changed
2. Modern Features
Buildx integration - Multi-platform builds
Better dependency resolution
Enhanced build context handling
3. Performance
Up to 3x faster than traditional builds in some cases
Reduced resource usage
Better memory management