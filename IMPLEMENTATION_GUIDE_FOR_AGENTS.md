# IMPLEMENTATION GUIDE FOR AGENTS
## Step-by-Step Instructions to Rebuild the System

**Target Audience:** AI Agents or Developers  
**Estimated Time:** 4-5 hours (including testing)  
**Success Criteria:** All 7 phases working, 3 groups with 53 members, 60 meetings, full financial data

---

## PHASE 0: PREREQUISITES & VALIDATION

### 1. Environment Setup
```bash
# Verify Docker is installed
docker --version  # Should be 20.10+
docker-compose --version  # Should be 1.29+

# Verify available ports
lsof -i :3001  # Frontend
lsof -i :5001  # Backend
lsof -i :5432  # Database
lsof -i :8080  # Adminer

# Verify disk space
df -h  # Need 10GB minimum
```

### 2. Repository Structure Validation
```
testdriven-appcopy/
├── client/                          # React frontend
│   ├── Dockerfile
│   ├── package.json
│   ├── src/
│   └── build/                       # Pre-built React files
├── services/users/                  # Flask backend
│   ├── Dockerfile
│   ├── manage.py
│   ├── project/
│   │   ├── __init__.py
│   │   ├── api/
│   │   │   ├── models.py           # 63 ORM models
│   │   │   ├── auth.py
│   │   │   ├── savings_groups.py
│   │   │   ├── meeting_api.py
│   │   │   ├── loan_assessment_service.py
│   │   │   └── [other APIs]
│   │   └── config.py
│   ├── scripts/
│   │   └── seed_comprehensive_12month_journey.py
│   └── startup.sh
├── migrations/                      # SQL migrations
│   ├── 000_create_base_schema.sql
│   ├── 001_create_meeting_scheduler_tables.sql
│   ├── 002_enhance_existing_tables.sql
│   ├── 003_create_indexes_and_triggers.sql
│   ├── 004_seed_meeting_templates.sql
│   ├── 005_add_phase1_and_iga_tables.sql
│   ├── 006_fix_schema_mismatches.sql
│   ├── 006a_add_activity_documents_table.sql
│   ├── 006b_add_phase2_loan_eligibility_settings.sql
│   ├── 006c_harmonize_activity_types.sql
│   ├── 007_complete_schema_alignment.sql
│   ├── 007a_add_aggregation_triggers.sql
│   ├── 007b_add_phase3_achievements_tables.sql
│   ├── 008_add_mobile_money_activity_link.sql
│   ├── 008_add_phase4_analytics_tables.sql
│   ├── 009_add_phase5_advanced_features_tables.sql
│   ├── 009_align_all_tables_with_orm_models.sql
│   └── 010_add_phase7_social_engagement_tables.sql
├── scripts/
│   └── rebuild-final.sh             # Main rebuild script
├── docker-compose.professional.yml  # Docker Compose config
├── REBUILD_PROCEDURE.md
└── SYSTEM_SPECIFICATION_COMPLETE.md
```

---

## PHASE 1: CRITICAL VALIDATION BEFORE REBUILD

### 1. Verify ORM Models Match Database Schema

**Key Files to Check:**
- `services/users/project/api/models.py` - Contains all 63 ORM models
- `migrations/009_align_all_tables_with_orm_models.sql` - Alignment migration

**Critical Models to Verify:**
```python
# GroupMember model (lines 495-540)
- first_name, last_name (NOT name)
- phone_number (NOT phone)
- All audit fields: created_date, updated_date

# SavingType model (lines 839-880)
- is_active, requires_target, allows_withdrawal
- minimum_amount, maximum_amount
- created_by (required in __init__)

# MeetingAttendance model (lines 1042-1102)
- attendance_time (TIMESTAMP, NOT TIME)
- excuse_reason (TEXT)
- contributed_to_meeting, meeting_notes
- recorded_by, recorded_date

# Meeting model (lines 2008-2100)
- attendance_count, total_fines_collected, total_loan_repayments
- agenda, minutes
- created_by, recorded_by, scheduled_by

# All models must have:
- Proper __init__ methods with required parameters
- Relationships defined correctly
- Foreign key constraints
- Audit fields (created_date, updated_date)
```

### 2. Verify Seeding Script Matches ORM

**File:** `services/users/scripts/seed_comprehensive_12month_journey.py`

**Critical Sections:**
```python
# Line 176-196: seed_members() function
- Split names into first_name and last_name
- Use phone_number (NOT phone)
- Set role='FOUNDER' for first member

# Line 270-280: seed_financial_data() function
- SavingType requires created_by=1 (admin user)
- Do NOT pass is_active parameter

# Line 222-256: seed_meetings_and_attendance() function
- MeetingAttendance requires recorded_by parameter
- Set excuse_reason for absent members
- Set contributed_to_meeting for attended members
```

### 3. Verify Migration Files

**Critical Checks:**
```sql
-- 000_create_base_schema.sql
- group_members table uses first_name, last_name
- All tables have created_date, updated_date

-- 009_align_all_tables_with_orm_models.sql
- attendance_time is TIMESTAMP (not TIME)
- excuse_reason is TEXT
- All missing columns are added
- No duplicate column additions
```

---

## PHASE 2: EXECUTE REBUILD

### Step 1: Navigate to Project Directory
```bash
cd /path/to/testdriven-appcopy
```

### Step 2: Run Rebuild Script
```bash
bash scripts/rebuild-final.sh
```

**Expected Output:**
```
✅ REBUILD COMPLETE!
📍 Access your application:
   Frontend:  http://localhost:3001
   Backend:   http://localhost:5001
   Database:  http://localhost:8080 (Adminer)
🔐 Login credentials:
   Email:    admin@savingsgroup.com
   Password: admin123
```

### Step 3: Monitor Rebuild Progress
```bash
# In separate terminal, watch logs
docker logs -f testdriven_backend

# Expected log sequence:
# 1. "Creating users..."
# 2. "✅ Admin user ready (ID: 1)"
# 3. "Creating 3 savings groups..."
# 4. "✅ 3 groups created"
# 5. "Creating 53 members..."
# 6. "✅ 53 members created"
# 7. "Creating 60 meetings..."
# 8. "✅ Seeding complete!"
```

---

## PHASE 3: VALIDATION & TESTING

### Test 1: Database Verification
```bash
# Check table count
docker-compose -f docker-compose.professional.yml exec -T db psql -U postgres -d users_dev -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public';"
# Expected: 63

# Check specific tables
docker-compose -f docker-compose.professional.yml exec -T db psql -U postgres -d users_dev -c "\dt"
```

### Test 2: Backend API Verification
```bash
# Test login
curl -X POST http://localhost:5001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@savingsgroup.com","password":"admin123"}'
# Expected: auth_token in response

# Test groups endpoint
curl -X GET http://localhost:5001/api/savings-groups \
  -H "Authorization: Bearer <token>"
# Expected: 3 groups in response

# Test members endpoint
curl -X GET http://localhost:5001/api/savings-groups/1/members \
  -H "Authorization: Bearer <token>"
# Expected: 18 members for group 1
```

### Test 3: Frontend Verification
```bash
# Access frontend
curl http://localhost:3001
# Expected: HTML response (React app)

# Manual testing:
# 1. Open http://localhost:3001 in browser
# 2. Login with admin@savingsgroup.com / admin123
# 3. Verify dashboard loads
# 4. Check all 3 groups visible
# 5. Click on group to see 18 members
# 6. Verify financial data displays
```

### Test 4: Run E2E Tests
```bash
cd /path/to/testdriven-appcopy
python -m pytest tests/test_e2e_all_phases.py -v

# Expected: 25 tests passing
# Coverage: All 7 phases
```

---

## PHASE 4: TROUBLESHOOTING GUIDE

### Issue: Database has 0 tables
**Cause:** SQL migrations didn't run  
**Solution:**
```bash
# Check migration files exist
ls -la migrations/

# Check database logs
docker logs testdriven_db

# Manually run migrations
docker-compose -f docker-compose.professional.yml exec -T db psql -U postgres -d users_dev < migrations/000_create_base_schema.sql
```

### Issue: Seeding fails with "column X does not exist"
**Cause:** ORM model expects column that's not in database  
**Solution:**
1. Check migration file 009_align_all_tables_with_orm_models.sql
2. Verify column is added for that table
3. Rebuild database: `docker volume rm testdriven-appcopy_postgres_data`
4. Re-run rebuild script

### Issue: Login returns 401 Unauthorized
**Cause:** Admin user not created  
**Solution:**
```bash
# Check if admin user exists
docker-compose -f docker-compose.professional.yml exec -T db psql -U postgres -d users_dev -c "SELECT * FROM users WHERE email='admin@savingsgroup.com';"

# If empty, manually create
docker-compose -f docker-compose.professional.yml exec -T backend python manage.py create_super_admin
```

### Issue: Groups endpoint returns 0 groups
**Cause:** Seeding didn't complete  
**Solution:**
```bash
# Check backend logs for seeding errors
docker logs testdriven_backend | grep -E "(❌|Seeding failed)"

# Manually run seeding
docker-compose -f docker-compose.professional.yml exec -T backend python manage.py seed_demo_data

# Check groups in database
docker-compose -f docker-compose.professional.yml exec -T db psql -U postgres -d users_dev -c "SELECT COUNT(*) FROM savings_groups;"
```

### Issue: Frontend shows blank page
**Cause:** API URL misconfiguration  
**Solution:**
```bash
# Check frontend environment
docker exec testdriven_frontend env | grep REACT_APP_API_URL

# Should be: http://localhost:5001

# If wrong, rebuild frontend
docker-compose -f docker-compose.professional.yml build --no-cache frontend
docker-compose -f docker-compose.professional.yml up -d frontend
```

---

## PHASE 5: POST-REBUILD VERIFICATION CHECKLIST

- [ ] Database has 63 tables
- [ ] Admin user created (admin@savingsgroup.com)
- [ ] 3 groups created (Kigali, Muhanga, Gitarama)
- [ ] 53 total members across groups
- [ ] 60 meetings created
- [ ] All members have financial data
- [ ] Loan assessments completed
- [ ] Mobile money accounts linked
- [ ] Achievements system initialized
- [ ] Leaderboard populated
- [ ] Notifications system working
- [ ] Frontend loads without errors
- [ ] Backend API responding
- [ ] E2E tests passing (25/25)
- [ ] All 7 phases functional

---

## PHASE 6: PRODUCTION DEPLOYMENT

### AWS ECS Deployment
```bash
# Build production images
docker build -t microfinance-backend:latest -f services/users/Dockerfile .
docker build -t microfinance-frontend:latest -f client/Dockerfile .

# Push to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account>.dkr.ecr.us-east-1.amazonaws.com
docker tag microfinance-backend:latest <account>.dkr.ecr.us-east-1.amazonaws.com/microfinance-backend:latest
docker push <account>.dkr.ecr.us-east-1.amazonaws.com/microfinance-backend:latest

# Update ECS task definitions and services
# (Refer to AWS deployment documentation)
```

---

## CRITICAL SUCCESS FACTORS

1. **ORM-First Approach:** Database schema MUST match ORM models exactly
2. **Migration Order:** SQL migrations run in alphabetical order
3. **Seeding Sequence:** Users → Groups → Members → Meetings → Financial Data
4. **Parameter Matching:** All __init__ methods must receive correct parameters
5. **Audit Fields:** All tables must have created_date and updated_date
6. **Foreign Keys:** All relationships must be properly defined
7. **No Manual Edits:** Use migrations for schema changes, not manual SQL

---

## SUPPORT RESOURCES

- **Specification:** SYSTEM_SPECIFICATION_COMPLETE.md
- **Rebuild Procedure:** REBUILD_PROCEDURE.md
- **Tests:** tests/test_e2e_all_phases.py
- **API Documentation:** services/users/project/api/
- **Database Schema:** migrations/

---

**End of Implementation Guide**

