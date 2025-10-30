# Microservices with Docker, Flask, and React

<!-- AURORA INTEGRATION: Professional PostgreSQL with Aurora Serverless v2 -->
<!-- CI/CD: Fixed frontend paths for proper deployment -->

[![Build Status](https://github.com/owenabrams/testdriven-app/workflows/Continuous%20Integration%20and%20Delivery/badge.svg?branch=main)](https://github.com/owenabrams/testdriven-app/actions)

## 🎉 Production Setup Complete!

This application features a modern 3-service microservices architecture with automated deployment:

### ✅ **Architecture**
- **Frontend Service**: React application with nginx
- **Backend Service**: Flask API with PostgreSQL
- **Database Service**: PostgreSQL (Local for testing, RDS for production)

### ✅ **Deployment & CI/CD**
- **GitHub Actions**: Automated testing and deployment
- **ECS Production Automation**: Zero-downtime deployments
- **Branch-based Deployment**: Push to `production` branch triggers deployment
- **Modern Secrets Management**: GitHub repository secrets

### ✅ **Cost Optimization**
- **Local PostgreSQL**: $0/month for testing and development
- **Easy RDS Migration**: Switch to managed database when needed
- **Efficient Resource Usage**: Optimized container configurations

### 🚀 **Quick Start - Professional Rebuild**

#### **Complete System Rebuild (Recommended)**
```bash
# Execute the professional rebuild script
./scripts/rebuild-clean.sh
```

This single command will:
- ✅ Stop and clean all containers
- ✅ Build fresh Docker images
- ✅ Start all services
- ✅ Run database migrations
- ✅ Seed comprehensive 12-month member journey data
- ✅ Verify all services are healthy

**Total time:** ~3 minutes

#### **Access After Rebuild**
- **Frontend:** http://localhost:3001
- **Backend:** http://localhost:5000
- **Database:** localhost:5432

**Default Credentials:**
- Email: `admin@savingsgroup.com`
- Password: `admin123`

#### **For Detailed Instructions**
See [REBUILD_PROCEDURE.md](REBUILD_PROCEDURE.md) for:
- Step-by-step procedure
- Database configuration
- Troubleshooting guide
- Manual rebuild alternative
- Testing procedures

#### **Verify Installation**
```bash
# Check containers are running
docker ps

# Test backend API
curl http://localhost:5000/api/ping

# Run E2E tests
python E2E_TEST_SUITE.py
```

#### **Production Deployment**
```bash
# Automated deployment (triggers on push to production branch)
git push origin production

# Manual deployment
./scripts/deploy-production-complete.sh DB_PASSWORD SECRET_KEY

# Local production testing
./scripts/test-local-production.sh
```

### 📋 **Key Adaptations from TestDriven Tutorial**
- ✅ **GitHub Actions** instead of Travis CI
- ✅ **3-service architecture** instead of 4-service
- ✅ **us-east-1** region instead of us-west-1
- ✅ **Local PostgreSQL** option for cost-effective testing
- ✅ **Modern container orchestration** with ECS

### 🔧 **Production Services**
- **Frontend**: `testdriven-client-prod-service` (React + nginx)
- **Backend**: `testdriven-users-prod-service` (Flask API)
- **Database**: Local PostgreSQL or AWS RDS
- **Load Balancer**: Application Load Balancer with path-based routing

### 📊 **Monitoring & Testing**
- **CloudWatch Logs**: Centralized logging for all services
- **Health Checks**: Automated service health monitoring
- **End-to-End Testing**: Comprehensive test suite with Cypress
- **Database Connectivity**: Automated connection testing

---

**Built following the TestDriven.io tutorial with modern adaptations for GitHub Actions and cost optimization.**
