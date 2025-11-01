# Microfinance Savings Group Management Platform

A comprehensive web application for managing microfinance savings groups in Uganda, built with React, Flask, and PostgreSQL.

## Quick Start

### Prerequisites
- Docker Desktop
- Git

### Installation

1. **Clone and start:**
```bash
git clone https://github.com/owenabrams/microsavings.git
cd microsavings
docker compose -f docker-compose.professional.yml up -d --build
```

2. **Access the application:**
- Frontend: http://localhost:3001
- Backend API: http://localhost:5001
- Database Admin: http://localhost:8080

3. **Login:**
- Email: `admin@savingsgroup.com`
- Password: `admin123`

### Seed Sample Data

**Note:** Sample data is automatically seeded on first build. To manually re-seed:

```bash
# Option 1: Clear marker and restart (triggers auto-seeding)
docker compose -f docker-compose.professional.yml exec backend rm -f /usr/src/app/.data_seeded
docker compose -f docker-compose.professional.yml restart backend

# Option 2: Run seeding script directly
docker compose -f docker-compose.professional.yml exec backend python seed_comprehensive_data.py

# Option 3: Use CLI command
docker compose -f docker-compose.professional.yml exec backend python manage.py seed_demo_data
```

**Seeded Data Includes:**
- 3 diverse savings groups (Rwanda, Uganda, Kenya)
- 21 members with login credentials (password: `password123`)
- 24 weekly meetings per group (6 months of data)
- Complete transaction coverage: savings, fines, loans, training, voting

## Technology Stack

- **Frontend:** React 18, Material-UI v5, React Query v5
- **Backend:** Flask 2.3.3, SQLAlchemy 3.0.5
- **Database:** PostgreSQL 15
- **Infrastructure:** Docker, Nginx

## Project Structure

```
microsavings/
├── client/                          # React frontend
│   ├── src/components/             # UI components
│   │   └── Dashboard/              # Dashboard cards
│   └── src/services/api.js         # API client
├── services/users/                  # Flask backend
│   ├── project/api/                # API endpoints
│   │   ├── auth.py                 # Authentication
│   │   ├── members.py              # Member endpoints
│   │   └── savings_groups.py       # Group endpoints
│   └── scripts/                    # Seeding scripts
├── migrations/                      # Database schema
└── docker-compose.professional.yml  # Docker orchestration
```

## Implementation Status

### ✅ Phase 1: Member Financial Dashboard (COMPLETE)
- Member dashboard with 6 cards (savings, loans, performance, metrics, IGA)
- Savings tracking by fund type (Personal, ECD, Social)
- Loan eligibility display
- Performance comparison with group averages

### 🔄 Upcoming Phases
- Phase 1.5: IGA (Income Generating Activities)
- Phase 2: Loan Management
- Phase 3: Achievements & Gamification
- Phase 4: Analytics & Reporting
- Phase 5: Advanced Features (QR, GPS, Mobile Money)
- Phase 6: Intelligence & AI
- Phase 7: Social Engagement

## Development Commands

```bash
# Rebuild specific service
docker compose -f docker-compose.professional.yml up -d --build frontend
docker compose -f docker-compose.professional.yml up -d --build backend

# View logs
docker logs testdriven_frontend --tail 50
docker logs testdriven_backend --tail 50

# Database access
docker exec -it testdriven_db psql -U postgres -d users_dev

# Stop all services
docker compose -f docker-compose.professional.yml down
```

## Documentation

- **SYSTEM_SPECIFICATION_COMPLETE.md** - Complete feature specifications (all 7 phases)
- **ORM_DATABASE_ALIGNMENT_GUIDE.md** - Database schema and ORM alignment
- **CLEAN_SLATE_REBUILD_SUCCESS_REPORT.md** - Rebuild procedures

## License

Proprietary - All rights reserved
