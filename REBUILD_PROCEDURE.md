# Professional Rebuild Procedure

## Overview

This document describes the **single, unified rebuild process** for the Enhanced Savings Groups microfinance application. This is the **ONLY** rebuild method to use.

**CRITICAL**: This rebuild process is designed to be **100% reproducible** from a clean state. Every rebuild creates the exact same database schema and initial data, making it suitable for rigorous testing including 12-month stress tests with 3 saving groups.

## Prerequisites

- Docker and Docker Compose installed
- Git repository cloned
- No running containers from previous builds
- Ports 3001, 5001, 5432, 8080 available

## One-Command Rebuild

```bash
./scripts/rebuild-final.sh
```

This single command handles:

1. ✅ Complete cleanup (containers, volumes, images)
2. ✅ Docker image builds with cache optimization
3. ✅ Service startup with proper dependency ordering
4. ✅ Database initialization with PostgreSQL
5. ✅ SQL migrations (creates all tables)
6. ✅ Alembic migrations (tracks schema history)
7. ✅ Initial data seeding
8. ✅ Health verification for all services

## What Gets Created

### Database

- **82 tables** across all 7 phases (Phases 1-7)
- PostgreSQL 15 Alpine
- Automatic migrations on startup
- Persistent volume: `testdriven-appcopy_postgres_data`
- **Reproducible schema**: Same tables created every rebuild

### Backend

- Flask API on port 5001
- Alembic-based migrations
- Automatic schema initialization
- Health check: `http://localhost:5001/ping`

### Frontend

- React application on port 3001
- Nginx reverse proxy
- Health check: `http://localhost:3001`

### Database Admin

- Adminer on port 8080
- Access: `http://localhost:8080`

## Access Points

| Service | URL | Credentials |
|---------|-----|-------------|
| Frontend | http://localhost:3001 | admin@savingsgroup.com / admin123 |
| Backend API | http://localhost:5001 | N/A |
| Database Admin | http://localhost:8080 | postgres / postgres |
| Health Check | http://localhost:5001/ping | N/A |

## Verification

After rebuild completes, verify all systems:

```bash
# Check backend
curl http://localhost:5001/ping

# Check frontend
curl http://localhost:3001

# Check database table count
docker exec testdriven_db psql -U postgres -d users_dev -c \
  "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public';"
# Should return: 82
```

## Key Files

- **Rebuild Script**: `./scripts/rebuild-final.sh`
- **Docker Compose**: `./docker-compose.professional.yml`
- **Backend Startup**: `./services/users/startup.sh`
- **Migrations**: `./migrations/` (15 SQL files)
- **Alembic Config**: `./services/users/migrations/`

## Troubleshooting

### Containers won't start
```bash
docker-compose -f docker-compose.professional.yml down -v
./scripts/rebuild-final.sh
```

### Database connection issues
```bash
docker logs testdriven_db
docker logs testdriven_backend
```

### Port conflicts
Ensure ports 3001, 5001, 5432, 8080 are available:
```bash
lsof -i :3001
lsof -i :5001
lsof -i :5432
lsof -i :8080
```

## Environment Variables

Default values (can be overridden):
- `DB_USER=postgres`
- `DB_PASSWORD=postgres`
- `DB_NAME=users_dev`
- `DB_PORT=5432`
- `API_PORT=5001`
- `FRONTEND_PORT=3001`

## 12-Month Stress Testing

This rebuild process is designed to support rigorous 12-month stress tests with 3 saving groups:

### Reproducibility Guarantee

- **Same schema every rebuild**: 82 tables created identically
- **Same initial data every rebuild**: Seeding is deterministic
- **No random failures**: All migrations are SQL-based (no Alembic conflicts)
- **Clean state**: Complete volume cleanup ensures no leftover data

### Testing with 3 Saving Groups

The rebuild creates:
- 1 admin user: `admin@savingsgroup.com` / `admin123`
- 3 pre-seeded savings groups:
  - Kigali Women Savings Group (18 members)
  - Kampala Traders Association (17 members)
  - Nairobi Entrepreneurs Fund (18 members)
- 53 total members across all groups
- 60 monthly meetings (12 per group)
- Complete financial data (savings, loans, fines, transactions)
- Ready for immediate 12-month stress testing

To run 12-month stress tests:
1. Rebuild with `./scripts/rebuild-final.sh`
2. Login with `admin@savingsgroup.com` / `admin123`
3. Run your 12-month stress tests against the pre-seeded data

### Ensuring No Errors

**Before running tests:**
```bash
# Verify clean rebuild
./scripts/rebuild-final.sh

# Check database
curl http://localhost:5001/ping

# Verify table count
docker exec testdriven_db psql -U postgres -d users_dev -c \
  "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public';"
# Should return: 82
```

**If errors occur:**
1. Check Docker logs: `docker logs testdriven_backend`
2. Verify ports are free: `lsof -i :3001 :5001 :5432 :8080`
3. Clean rebuild: `./scripts/rebuild-final.sh`

## Notes

- This rebuild process is **production-ready**
- All migrations are **SQL-based** (deterministic, no conflicts)
- Database schema is **automatically initialized**
- No manual migration steps required
- All tests use this same rebuild process
- **Reproducible**: Same result every time from clean state

