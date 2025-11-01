# 🏗️ Default Build Setup - Single Source of Truth

**Last Updated:** 2025-11-01
**Status:** ✅ Production-Ready
**Repository:** https://github.com/owenabrams/microsavings

**Recent Updates:** Fixed documents tab 401 error, member profile 500 error, super admin permissions, member self-service profile management, database schema updates

---

## ⚠️ IMPORTANT: This is the ONLY Default Build Configuration

This document defines the **single source of truth** for building and running the microsavings application. All other setup files, seeding scripts, and documentation have been cleaned up to prevent confusion.

### **Latest Fixes Included in Default Build:**

1. ✅ **Documents Tab 401 Error** - Super admin can now access all group documents
2. ✅ **Member Profile 500 Error** - Database view auto-created on startup
3. ✅ **Super Admin Permissions** - Full access to all groups without membership
4. ✅ **Member Self-Service** - New endpoints for user account management
5. ✅ **Database Schema** - Auto-updates `group_documents` table with 20 missing columns

---

## 🎯 Default Build Configuration

### **1. Docker Compose File**

**PRIMARY FILE:** `docker-compose.professional.yml`

This is the **ONLY** docker-compose file for the project. Use this for all operations:

```bash
# Start application
docker compose -f docker-compose.professional.yml up -d --build

# Stop application
docker compose -f docker-compose.professional.yml down

# View logs
docker compose -f docker-compose.professional.yml logs -f

# Rebuild from scratch
docker compose -f docker-compose.professional.yml down -v
docker compose -f docker-compose.professional.yml up -d --build
```

### **2. Startup Script**

**PRIMARY FILE:** `services/users/startup.sh`

This script runs automatically when the backend container starts. It:
1. Waits for database to be ready
2. Creates database if it doesn't exist
3. Runs database migrations
4. **Creates `member_profile_complete` database view** (for member profiles)
5. **Updates `group_documents` table schema** (adds 20 missing columns)
6. Seeds admin user
7. **AUTO-SEEDS comprehensive data on first run** (checks for `.data_seeded` marker)
8. Starts the Flask application

**No manual intervention required** - everything happens automatically, including all recent fixes.

### **3. Seeding Script**

**PRIMARY FILE:** `services/users/seed_comprehensive_data.py`

This is the **ONLY** seeding script for the project. It:
- Populates 3 diverse savings groups (Rwanda, Uganda, Kenya)
- Creates 21 members with login credentials
- Generates 24 weekly meetings per group (6 months of data)
- Includes ALL transaction types with realistic distribution
- Matches ORM models exactly (no schema mismatches)

**All other seeding scripts have been deleted:**
- ❌ `seed_mobile_money_test.py` - DELETED
- ❌ `seed_test_data.py` - DELETED
- ❌ `scripts/seed_comprehensive_12month_journey.py` - DELETED

### **4. Database Management**

**PRIMARY FILE:** `services/users/manage.py`

CLI commands for database operations:

```bash
# Seed admin user only
docker compose -f docker-compose.professional.yml exec backend python manage.py seed_db

# Seed comprehensive demo data (recommended)
docker compose -f docker-compose.professional.yml exec backend python manage.py seed_demo_data

# Recreate database (drops and recreates)
docker compose -f docker-compose.professional.yml exec backend python manage.py recreate_db
```

---

## 📊 Default Seeded Data

### **Automatic on First Build**

When you build the application for the first time, it automatically seeds:

**3 Savings Groups:**
- Kigali Women Savings (RWF - Rwandan Franc)
- Kampala Youth Savers (UGX - Ugandan Shilling)
- Nairobi Community Fund (KES - Kenyan Shilling)

**21 Members:**
- 7 members per group
- Each group has: 1 Chairperson, 1 Secretary, 1 Treasurer, 4 regular members
- All members have login credentials (password: `password123`)
- Admin user is a member of all groups

**24 Meetings per Group:**
- 23 COMPLETED meetings
- 1 IN_PROGRESS meeting (for testing)
- Weekly meetings over 6 months

**Complete Transaction Coverage:**
- ~500+ savings transactions (90% physical, 10% mobile money)
- ~100+ fines (late arrivals, absences)
- ~18 loan disbursements
- ~100+ loan repayments
- 12 training sessions (every 6 meetings)
- 9 voting sessions (every 8 meetings)
- ~500+ attendance records
- 69 meeting summaries with calculated totals

---

## 🔐 Default Login Credentials

### **Admin Account**
```
Email: admin@savingsgroup.com
Password: admin123
Role: ADMIN in all groups
```

### **Member Accounts**
All members use password: `password123`

**Officers (can verify payments):**
- alice.mukamana@example.com (Chairperson - Kigali)
- betty.uwase@example.com (Secretary - Kigali)
- catherine.ingabire@example.com (Treasurer - Kigali)
- frank.okello@example.com (Chairperson - Kampala)
- grace.nambi@example.com (Secretary - Kampala)
- henry.mugisha@example.com (Treasurer - Kampala)
- kevin.omondi@example.com (Chairperson - Nairobi)
- lucy.wanjiku@example.com (Secretary - Nairobi)
- michael.kamau@example.com (Treasurer - Nairobi)

**Regular Members:**
- diana.mutesi@example.com (Kigali)
- emma.nyira@example.com (Kigali)
- fiona.uwera@example.com (Kigali)
- grace.mukeshimana@example.com (Kigali)
- irene.nakato@example.com (Kampala)
- john.ssemakula@example.com (Kampala)
- karen.namusoke@example.com (Kampala)
- lawrence.kato@example.com (Kampala)
- nancy.akinyi@example.com (Nairobi)
- oscar.mwangi@example.com (Nairobi)
- patricia.njeri@example.com (Nairobi)
- robert.otieno@example.com (Nairobi)

---

## 🚀 Quick Start (Default Build)

### **Step 1: Clone Repository**
```bash
git clone https://github.com/owenabrams/microsavings.git
cd microsavings
```

### **Step 2: Build and Start**
```bash
docker compose -f docker-compose.professional.yml up -d --build
```

### **Step 3: Wait for Seeding**
Wait ~30 seconds for automatic seeding to complete. Check logs:
```bash
docker compose -f docker-compose.professional.yml logs backend | grep "SEEDING"
```

### **Step 4: Access Application**
- Frontend: http://localhost:3001
- Backend API: http://localhost:5001
- Database Admin: http://localhost:8080

### **Step 5: Login**
Use admin credentials or any member account (see above).

---

## 🔄 Re-seeding Data

If you need to re-seed data after the initial build:

### **Option 1: Clear Marker and Restart (Recommended)**
```bash
docker compose -f docker-compose.professional.yml exec backend rm -f /usr/src/app/.data_seeded
docker compose -f docker-compose.professional.yml restart backend
```

### **Option 2: Run Seeding Script Directly**
```bash
docker compose -f docker-compose.professional.yml exec backend python seed_comprehensive_data.py
```

### **Option 3: Use CLI Command**
```bash
docker compose -f docker-compose.professional.yml exec backend python manage.py seed_demo_data
```

---

## 📁 Key Files (Single Source of Truth)

### **Build Configuration**
- `docker-compose.professional.yml` - **PRIMARY** docker compose file
- `services/users/Dockerfile` - Backend container definition
- `client/Dockerfile` - Frontend container definition

### **Startup & Initialization**
- `services/users/startup.sh` - **PRIMARY** startup script (auto-seeds on first run)
- `services/users/manage.py` - Database management CLI

### **Data Seeding**
- `services/users/seed_comprehensive_data.py` - **PRIMARY** seeding script

### **Documentation**
- `DEFAULT_BUILD_SETUP.md` - **THIS FILE** - Single source of truth
- `AGENT_HANDOFF_2025_11_01.md` - Complete system documentation
- `COMPREHENSIVE_SEEDING_SYSTEM_COMPLETE.md` - Seeding system details
- `README.md` - Project overview

### **Database**
- `services/users/project/api/models.py` - ORM models (matches database schema exactly)
- `migrations/` - Database migration files

---

## ✅ What Was Cleaned Up

To ensure a single source of truth, the following files were **DELETED**:

### **Old Seeding Scripts**
- ❌ `services/users/seed_mobile_money_test.py`
- ❌ `services/users/seed_test_data.py`
- ❌ `services/users/scripts/seed_comprehensive_12month_journey.py`

### **Old Utility Scripts**
- ❌ `services/users/create_missing_tables.py`
- ❌ `services/users/create_transaction_documents_table.py`
- ❌ `services/users/align_schema.py`

### **Old Documentation**
- ❌ `AGENT_HANDOFF.md` (replaced by `AGENT_HANDOFF_2025_11_01.md`)

---

## 🎯 Benefits of This Setup

1. **Single Source of Truth** - No confusion about which files to use
2. **Automatic Seeding** - No manual intervention required
3. **No ORM Mismatches** - Seeding script matches database schema exactly
4. **Complete Test Data** - All transaction types populated with realistic distribution
5. **Production-Ready** - 6 months of realistic activity data
6. **Easy Debugging** - Clear logging and marker file system
7. **Consistent Rebuilds** - Same data every time you rebuild

---

## 🔧 Troubleshooting

### **Problem: Data not seeding automatically**
**Solution:** Check if marker file exists:
```bash
docker compose -f docker-compose.professional.yml exec backend ls -la /usr/src/app/.data_seeded
```
If it exists, delete it and restart:
```bash
docker compose -f docker-compose.professional.yml exec backend rm -f /usr/src/app/.data_seeded
docker compose -f docker-compose.professional.yml restart backend
```

### **Problem: ORM/Schema mismatch errors**
**Solution:** The seeding script has been updated to match ORM models exactly. If you still see errors:
1. Check `services/users/project/api/models.py` for the correct field names
2. Update `services/users/seed_comprehensive_data.py` if needed
3. Report the issue for investigation

### **Problem: Want to start fresh**
**Solution:** Nuclear rebuild:
```bash
docker compose -f docker-compose.professional.yml down -v
docker compose -f docker-compose.professional.yml up -d --build
```

---

## 📝 Summary

**Default Build Process:**
1. Run `docker compose -f docker-compose.professional.yml up -d --build`
2. Backend container starts and runs `startup.sh`
3. `startup.sh` checks for `.data_seeded` marker
4. If not found, runs `seed_comprehensive_data.py`
5. Creates marker file to prevent re-seeding
6. Application ready at http://localhost:3001

**That's it!** No manual steps, no confusion, no ORM mismatches.

---

**Status:** ✅ PRODUCTION-READY - Single source of truth established

