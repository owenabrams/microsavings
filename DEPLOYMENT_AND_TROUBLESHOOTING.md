# DEPLOYMENT AND TROUBLESHOOTING GUIDE
## Production Deployment and Issue Resolution

---

## LOCAL DEVELOPMENT DEPLOYMENT

### Quick Start (5 minutes)
```bash
cd /path/to/testdriven-appcopy
bash scripts/rebuild-final.sh
```

### Manual Step-by-Step Deployment
```bash
# 1. Stop existing containers
docker-compose -f docker-compose.professional.yml down

# 2. Remove volumes for fresh database
docker volume rm testdriven-appcopy_postgres_data

# 3. Remove old images
docker rmi testdriven-appcopy-backend testdriven-appcopy-frontend

# 4. Build images
docker-compose -f docker-compose.professional.yml build --no-cache backend frontend

# 5. Start services
docker-compose -f docker-compose.professional.yml up -d

# 6. Wait for database
sleep 30

# 7. Seed data
docker-compose -f docker-compose.professional.yml exec -T backend python manage.py seed_demo_data

# 8. Verify
curl http://localhost:5001/api/auth/status
```

---

## DOCKER COMPOSE CONFIGURATION

### Service Dependencies
```
db (PostgreSQL)
  ↓
backend (Flask API) - depends on db
  ↓
frontend (React) - depends on backend
```

### Environment Variables
```bash
# Database
DB_USER=postgres
DB_PASSWORD=postgres
DB_NAME=users_dev
DB_PORT=5432

# Backend
FLASK_ENV=development
APP_SETTINGS=project.config.DevelopmentConfig
SECRET_KEY=dev-secret-key-change-in-production
API_PORT=5001
API_HOST=0.0.0.0

# Frontend
REACT_APP_API_URL=http://localhost:5001
REACT_APP_ENV=development
FRONTEND_PORT=3001
```

### Port Mappings
- Frontend: 3001 → 80 (Nginx)
- Backend: 5001 → 5001 (Flask)
- Database: 5432 → 5432 (PostgreSQL)
- Adminer: 8080 → 8080 (Database UI)

---

## AWS ECS DEPLOYMENT

### Prerequisites
- AWS Account with ECR, ECS, RDS, ALB access
- Docker images pushed to ECR
- RDS PostgreSQL instance created
- ALB configured with target groups

### Step 1: Create ECR Repositories
```bash
aws ecr create-repository --repository-name microfinance-backend --region us-east-1
aws ecr create-repository --repository-name microfinance-frontend --region us-east-1
```

### Step 2: Build and Push Images
```bash
# Login to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account>.dkr.ecr.us-east-1.amazonaws.com

# Build backend
docker build -t microfinance-backend:latest \
  --platform linux/amd64 \
  -f services/users/Dockerfile .

# Tag and push backend
docker tag microfinance-backend:latest <account>.dkr.ecr.us-east-1.amazonaws.com/microfinance-backend:latest
docker push <account>.dkr.ecr.us-east-1.amazonaws.com/microfinance-backend:latest

# Build frontend
docker build -t microfinance-frontend:latest \
  --platform linux/amd64 \
  -f client/Dockerfile .

# Tag and push frontend
docker tag microfinance-frontend:latest <account>.dkr.ecr.us-east-1.amazonaws.com/microfinance-frontend:latest
docker push <account>.dkr.ecr.us-east-1.amazonaws.com/microfinance-frontend:latest
```

### Step 3: Create ECS Task Definitions

**Backend Task Definition:**
```json
{
  "family": "microfinance-backend",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "containerDefinitions": [
    {
      "name": "backend",
      "image": "<account>.dkr.ecr.us-east-1.amazonaws.com/microfinance-backend:latest",
      "portMappings": [
        {
          "containerPort": 5001,
          "hostPort": 5001,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "DATABASE_URL",
          "value": "postgresql://user:password@rds-endpoint:5432/users_prod"
        },
        {
          "name": "FLASK_ENV",
          "value": "production"
        },
        {
          "name": "SECRET_KEY",
          "value": "your-production-secret-key"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/microfinance-backend",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

**Frontend Task Definition:**
```json
{
  "family": "microfinance-frontend",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "256",
  "memory": "512",
  "containerDefinitions": [
    {
      "name": "frontend",
      "image": "<account>.dkr.ecr.us-east-1.amazonaws.com/microfinance-frontend:latest",
      "portMappings": [
        {
          "containerPort": 80,
          "hostPort": 80,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "REACT_APP_API_URL",
          "value": "https://api.yourdomain.com"
        },
        {
          "name": "REACT_APP_ENV",
          "value": "production"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/microfinance-frontend",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

### Step 4: Create ECS Services
```bash
# Create backend service
aws ecs create-service \
  --cluster microfinance-cluster \
  --service-name microfinance-backend \
  --task-definition microfinance-backend:1 \
  --desired-count 2 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx],securityGroups=[sg-xxx],assignPublicIp=ENABLED}" \
  --load-balancers targetGroupArn=arn:aws:elasticloadbalancing:...,containerName=backend,containerPort=5001

# Create frontend service
aws ecs create-service \
  --cluster microfinance-cluster \
  --service-name microfinance-frontend \
  --task-definition microfinance-frontend:1 \
  --desired-count 2 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx],securityGroups=[sg-xxx],assignPublicIp=ENABLED}" \
  --load-balancers targetGroupArn=arn:aws:elasticloadbalancing:...,containerName=frontend,containerPort=80
```

### Step 5: Configure RDS Database
```bash
# Create RDS PostgreSQL instance
aws rds create-db-instance \
  --db-instance-identifier microfinance-db \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --engine-version 15.3 \
  --master-username postgres \
  --master-user-password <strong-password> \
  --allocated-storage 20 \
  --storage-type gp2 \
  --publicly-accessible false \
  --vpc-security-group-ids sg-xxx

# Run migrations on RDS
docker run --rm \
  -e DATABASE_URL="postgresql://postgres:password@rds-endpoint:5432/users_prod" \
  <account>.dkr.ecr.us-east-1.amazonaws.com/microfinance-backend:latest \
  python manage.py seed_demo_data
```

---

## TROUBLESHOOTING GUIDE

### Issue 1: Database Connection Failed
**Error:** `psycopg2.OperationalError: could not connect to server`

**Diagnosis:**
```bash
# Check if database is running
docker-compose -f docker-compose.professional.yml ps db

# Check database logs
docker logs testdriven_db

# Test connection
docker-compose -f docker-compose.professional.yml exec db pg_isready
```

**Solutions:**
```bash
# Restart database
docker-compose -f docker-compose.professional.yml restart db

# Check database credentials
docker-compose -f docker-compose.professional.yml exec db psql -U postgres -c "SELECT 1"

# Rebuild database
docker volume rm testdriven-appcopy_postgres_data
docker-compose -f docker-compose.professional.yml up -d db
```

### Issue 2: Backend API Not Responding
**Error:** `curl: (7) Failed to connect to localhost port 5001`

**Diagnosis:**
```bash
# Check backend status
docker-compose -f docker-compose.professional.yml ps backend

# Check backend logs
docker logs testdriven_backend

# Check if port is in use
lsof -i :5001
```

**Solutions:**
```bash
# Restart backend
docker-compose -f docker-compose.professional.yml restart backend

# Check for errors in logs
docker logs testdriven_backend | grep -E "(Error|Exception|Traceback)"

# Rebuild backend
docker-compose -f docker-compose.professional.yml build --no-cache backend
docker-compose -f docker-compose.professional.yml up -d backend
```

### Issue 3: Frontend Blank Page
**Error:** Frontend loads but shows blank page

**Diagnosis:**
```bash
# Check frontend logs
docker logs testdriven_frontend

# Check browser console for errors
# Open http://localhost:3001 and check browser DevTools

# Check if API URL is correct
docker exec testdriven_frontend env | grep REACT_APP_API_URL
```

**Solutions:**
```bash
# Verify API URL
# Should be: http://localhost:5001

# Rebuild frontend with correct URL
docker-compose -f docker-compose.professional.yml build --no-cache frontend
docker-compose -f docker-compose.professional.yml up -d frontend

# Clear browser cache
# Ctrl+Shift+Delete (Chrome) or Cmd+Shift+Delete (Safari)
```

### Issue 4: Login Returns 401 Unauthorized
**Error:** `{"status": "error", "message": "Invalid credentials"}`

**Diagnosis:**
```bash
# Check if admin user exists
docker-compose -f docker-compose.professional.yml exec -T db psql -U postgres -d users_dev -c "SELECT * FROM users WHERE email='admin@savingsgroup.com';"

# Check user password
docker-compose -f docker-compose.professional.yml exec -T db psql -U postgres -d users_dev -c "SELECT id, email, password FROM users LIMIT 5;"
```

**Solutions:**
```bash
# Create admin user manually
docker-compose -f docker-compose.professional.yml exec -T backend python manage.py create_super_admin

# Or run seeding
docker-compose -f docker-compose.professional.yml exec -T backend python manage.py seed_demo_data
```

### Issue 5: Groups Endpoint Returns Empty
**Error:** `GET /api/savings-groups` returns 0 groups

**Diagnosis:**
```bash
# Check if groups exist in database
docker-compose -f docker-compose.professional.yml exec -T db psql -U postgres -d users_dev -c "SELECT COUNT(*) FROM savings_groups;"

# Check seeding logs
docker logs testdriven_backend | grep -E "(groups|Seeding)"
```

**Solutions:**
```bash
# Run seeding
docker-compose -f docker-compose.professional.yml exec -T backend python manage.py seed_demo_data

# Check for seeding errors
docker logs testdriven_backend | grep -E "(❌|Error|Traceback)"

# Manually verify data
docker-compose -f docker-compose.professional.yml exec -T db psql -U postgres -d users_dev -c "SELECT * FROM savings_groups;"
```

### Issue 6: Database Has Wrong Number of Tables
**Error:** Database has 30 tables instead of 63

**Diagnosis:**
```bash
# Count tables
docker-compose -f docker-compose.professional.yml exec -T db psql -U postgres -d users_dev -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public';"

# List all tables
docker-compose -f docker-compose.professional.yml exec -T db psql -U postgres -d users_dev -c "\dt"
```

**Solutions:**
```bash
# Check migration files
ls -la migrations/

# Verify migrations ran
docker logs testdriven_db | grep -E "(CREATE TABLE|migration)"

# Manually run migrations
docker-compose -f docker-compose.professional.yml exec -T db psql -U postgres -d users_dev < migrations/000_create_base_schema.sql

# Full rebuild
docker volume rm testdriven-appcopy_postgres_data
bash scripts/rebuild-final.sh
```

### Issue 7: Seeding Fails with Column Error
**Error:** `column "X" of relation "Y" does not exist`

**Diagnosis:**
```bash
# Check which column is missing
docker logs testdriven_backend | grep "does not exist"

# Check table schema
docker-compose -f docker-compose.professional.yml exec -T db psql -U postgres -d users_dev -c "\d table_name"
```

**Solutions:**
```bash
# Add missing column
docker-compose -f docker-compose.professional.yml exec -T db psql -U postgres -d users_dev -c "ALTER TABLE table_name ADD COLUMN column_name TYPE;"

# Or rebuild with updated migrations
docker volume rm testdriven-appcopy_postgres_data
bash scripts/rebuild-final.sh
```

### Issue 8: Port Already in Use
**Error:** `Error response from daemon: Ports are not available`

**Diagnosis:**
```bash
# Check which process is using the port
lsof -i :3001  # Frontend
lsof -i :5001  # Backend
lsof -i :5432  # Database
```

**Solutions:**
```bash
# Kill process using port
kill -9 <PID>

# Or use different ports
# Edit docker-compose.professional.yml and change port mappings

# Or stop all Docker containers
docker-compose -f docker-compose.professional.yml down
```

---

## PERFORMANCE OPTIMIZATION

### Database Optimization
```sql
-- Create indexes for common queries
CREATE INDEX idx_members_group ON group_members(group_id);
CREATE INDEX idx_transactions_member ON saving_transactions(member_id);
CREATE INDEX idx_meetings_group ON meetings(group_id);
CREATE INDEX idx_loans_member ON group_loans(member_id);
```

### Backend Optimization
```python
# Enable query caching
SQLALCHEMY_ECHO = False
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Use connection pooling
SQLALCHEMY_ENGINE_OPTIONS = {
    'pool_size': 10,
    'pool_recycle': 3600,
    'pool_pre_ping': True,
}
```

### Frontend Optimization
```javascript
// Enable React Query caching
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5, // 5 minutes
      cacheTime: 1000 * 60 * 10, // 10 minutes
    },
  },
});
```

---

## MONITORING & LOGGING

### View Logs
```bash
# Backend logs
docker logs -f testdriven_backend

# Database logs
docker logs -f testdriven_db

# Frontend logs
docker logs -f testdriven_frontend

# All logs
docker-compose -f docker-compose.professional.yml logs -f
```

### Health Checks
```bash
# Backend health
curl http://localhost:5001/api/auth/status

# Database health
docker-compose -f docker-compose.professional.yml exec db pg_isready

# Frontend health
curl http://localhost:3001/health
```

---

## BACKUP AND RECOVERY

### Backup Database
```bash
docker-compose -f docker-compose.professional.yml exec -T db pg_dump -U postgres users_dev > backup_$(date +%Y%m%d_%H%M%S).sql
```

### Restore Database
```bash
docker-compose -f docker-compose.professional.yml exec -T db psql -U postgres users_dev < backup_20251029_120000.sql
```

### Backup Docker Volumes
```bash
docker run --rm -v testdriven-appcopy_postgres_data:/data -v $(pwd):/backup alpine tar czf /backup/postgres_backup.tar.gz /data
```

---

**End of Deployment and Troubleshooting Guide**

