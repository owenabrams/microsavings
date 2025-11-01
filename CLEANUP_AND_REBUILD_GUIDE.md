# 🧹 Cleanup and Rebuild Guide

**Last Updated:** 2025-11-01  
**Status:** ✅ Production-Ready  
**Repository:** https://github.com/owenabrams/microsavings

---

## 🎯 Overview

This guide provides all the commands you need to clean up and rebuild the microsavings application. Use these when you want to start fresh, reset data, or troubleshoot issues.

---

## 🔥 Quick Cleanup Options

### **Option 1: Nuclear Rebuild (Complete Fresh Start)** ⚠️ DESTRUCTIVE

This removes **EVERYTHING** - containers, volumes, images, and data. Use when you want a completely fresh start.

```bash
# Stop and remove containers, volumes, and networks
docker compose -f docker-compose.professional.yml down -v

# Remove images (optional - saves rebuild time if skipped)
docker rmi microsavings-backend microsavings-frontend 2>/dev/null || true

# Rebuild and start fresh
docker compose -f docker-compose.professional.yml up -d --build
```

**What This Does:**
- ✅ Stops all containers
- ✅ Removes all containers
- ✅ **DELETES ALL DATABASE DATA** (volumes removed)
- ✅ Removes networks
- ✅ Optionally removes Docker images
- ✅ Rebuilds from scratch
- ✅ Auto-seeds fresh data on startup

**Use When:**
- You want to start completely fresh
- Database is corrupted
- Testing the default build
- Major schema changes

---

### **Option 2: Re-seed Data (Keep Containers)** 🔄 SAFE

This keeps containers running but re-seeds the database with fresh data.

```bash
# Clear the seeding marker
docker compose -f docker-compose.professional.yml exec backend rm -f /usr/src/app/.data_seeded

# Restart backend to trigger auto-seeding
docker compose -f docker-compose.professional.yml restart backend

# Wait 30 seconds for seeding to complete
sleep 30

# Check logs
docker compose -f docker-compose.professional.yml logs backend | grep "SEEDING"
```

**What This Does:**
- ✅ Removes seeding marker file
- ✅ Restarts backend container
- ✅ Triggers automatic data seeding
- ✅ Keeps existing containers and images
- ✅ Preserves database schema

**Use When:**
- You want fresh data but keep the same build
- Testing with different data
- Data got corrupted but schema is fine

---

### **Option 3: Manual Seeding (Direct Script)** 🎯 TARGETED

Run the seeding script directly without restarting containers.

```bash
# Run comprehensive seeding script
docker compose -f docker-compose.professional.yml exec backend python seed_comprehensive_data.py

# OR use CLI command
docker compose -f docker-compose.professional.yml exec backend python manage.py seed_demo_data
```

**What This Does:**
- ✅ Runs seeding script immediately
- ✅ No container restart needed
- ✅ Adds data to existing database
- ✅ Can be run multiple times

**Use When:**
- You want to add more test data
- Quick data refresh
- Testing seeding script changes

---

### **Option 4: Recreate Database Only** 🗄️ DATABASE ONLY

Drops and recreates the database schema without rebuilding containers.

```bash
# Recreate database (drops all tables and data)
docker compose -f docker-compose.professional.yml exec backend python manage.py recreate_db

# Seed fresh data
docker compose -f docker-compose.professional.yml exec backend python manage.py seed_demo_data
```

**What This Does:**
- ✅ Drops all database tables
- ✅ Recreates schema from ORM models
- ✅ **DELETES ALL DATA**
- ✅ Keeps containers running
- ✅ Requires manual seeding after

**Use When:**
- Schema changes in ORM models
- Database corruption
- Testing migrations

---

### **Option 5: Restart Containers Only** 🔄 MINIMAL

Simple restart without any data changes.

```bash
# Restart all containers
docker compose -f docker-compose.professional.yml restart

# OR restart specific container
docker compose -f docker-compose.professional.yml restart backend
docker compose -f docker-compose.professional.yml restart frontend
docker compose -f docker-compose.professional.yml restart db
```

**What This Does:**
- ✅ Restarts containers
- ✅ Keeps all data
- ✅ Keeps all images
- ✅ No rebuild

**Use When:**
- Code changes in mounted volumes
- Container is unresponsive
- Quick refresh

---

## 📋 Cleanup Checklist

Before running cleanup commands, consider:

- [ ] Do you need to backup data?
- [ ] Are there any important documents uploaded?
- [ ] Do you want to keep the Docker images (faster rebuild)?
- [ ] Do you need to test the default build?

---

## 💾 Backup Before Cleanup

### **Backup Database**

```bash
# Backup entire database
docker compose -f docker-compose.professional.yml exec db pg_dump -U postgres users_dev > backup_$(date +%Y%m%d_%H%M%S).sql

# Backup specific table
docker compose -f docker-compose.professional.yml exec db pg_dump -U postgres -t savings_groups users_dev > groups_backup.sql
```

### **Restore Database**

```bash
# Restore from backup
docker compose -f docker-compose.professional.yml exec -T db psql -U postgres users_dev < backup_20251101_120000.sql
```

---

## 🔍 Verification Commands

After cleanup/rebuild, verify everything is working:

```bash
# Check container status
docker compose -f docker-compose.professional.yml ps

# Check backend logs
docker compose -f docker-compose.professional.yml logs backend --tail 50

# Check if seeding completed
docker compose -f docker-compose.professional.yml logs backend | grep "SEEDING COMPLETE"

# Check database tables
docker compose -f docker-compose.professional.yml exec db psql -U postgres -d users_dev -c "\dt"

# Check seeded groups
docker compose -f docker-compose.professional.yml exec db psql -U postgres -d users_dev -c "SELECT id, name FROM savings_groups;"

# Test API
curl http://localhost:5001/ping
curl http://localhost:5001/api/savings-groups

# Test frontend
curl http://localhost:3001
```

---

## 🚨 Troubleshooting

### **Problem: Containers won't start**

```bash
# Check logs
docker compose -f docker-compose.professional.yml logs

# Check specific container
docker compose -f docker-compose.professional.yml logs backend
docker compose -f docker-compose.professional.yml logs db

# Check ports
lsof -i :3001  # Frontend
lsof -i :5001  # Backend
lsof -i :5432  # Database
```

### **Problem: Database connection errors**

```bash
# Check database is ready
docker compose -f docker-compose.professional.yml exec db pg_isready -U postgres

# Check database exists
docker compose -f docker-compose.professional.yml exec db psql -U postgres -l

# Recreate database
docker compose -f docker-compose.professional.yml exec backend python manage.py recreate_db
```

### **Problem: Seeding fails**

```bash
# Check seeding logs
docker compose -f docker-compose.professional.yml logs backend | grep -i "seed"

# Remove marker and try again
docker compose -f docker-compose.professional.yml exec backend rm -f /usr/src/app/.data_seeded
docker compose -f docker-compose.professional.yml restart backend

# Run seeding manually with verbose output
docker compose -f docker-compose.professional.yml exec backend python seed_comprehensive_data.py
```

---

## 📊 What Gets Cleaned Up

| Command | Containers | Volumes | Images | Data | Networks |
|---------|-----------|---------|--------|------|----------|
| `down` | ✅ | ❌ | ❌ | ✅ | ✅ |
| `down -v` | ✅ | ✅ | ❌ | ❌ | ✅ |
| `down -v --rmi all` | ✅ | ✅ | ✅ | ❌ | ✅ |
| `restart` | ❌ | ❌ | ❌ | ✅ | ❌ |
| `recreate_db` | ❌ | ❌ | ❌ | ❌ | ❌ |

---

## 🎯 Recommended Cleanup Workflows

### **For Development:**
```bash
# Quick data refresh
docker compose -f docker-compose.professional.yml exec backend rm -f /usr/src/app/.data_seeded
docker compose -f docker-compose.professional.yml restart backend
```

### **For Testing Default Build:**
```bash
# Complete fresh start
docker compose -f docker-compose.professional.yml down -v
docker compose -f docker-compose.professional.yml up -d --build
```

### **For Production Deployment:**
```bash
# Backup first!
docker compose -f docker-compose.professional.yml exec db pg_dump -U postgres users_dev > backup.sql

# Then rebuild
docker compose -f docker-compose.professional.yml down
docker compose -f docker-compose.professional.yml up -d --build
```

---

## 🧹 Docker Space Cleanup (Free Up Disk Space)

### **Check Docker Disk Usage**

```bash
# See how much space Docker is using
docker system df

# Detailed view
docker system df -v
```

**Example Output:**
```
TYPE            TOTAL     ACTIVE    SIZE      RECLAIMABLE
Images          15        3         4.5GB     3.2GB (71%)
Containers      8         2         1.2GB     800MB (66%)
Local Volumes   5         2         2.1GB     1.5GB (71%)
Build Cache     45        0         1.8GB     1.8GB (100%)
```

---

### **Option 1: Remove ALL Unused Docker Resources** ⚠️ NUCLEAR

This removes **EVERYTHING** not currently in use - stopped containers, unused networks, dangling images, and build cache.

```bash
# Remove everything unused (CAREFUL!)
docker system prune -a --volumes

# With confirmation prompt
docker system prune -a --volumes --force
```

**What This Removes:**
- ✅ All stopped containers
- ✅ All networks not used by at least one container
- ✅ All volumes not used by at least one container
- ✅ All images without at least one container associated
- ✅ All build cache

**⚠️ WARNING:** This will remove your microsavings database volume if containers are stopped!

---

### **Option 2: Remove Unused Images Only** 🖼️ SAFE

Remove dangling and unused images to free up space.

```bash
# Remove dangling images (untagged)
docker image prune

# Remove ALL unused images (not just dangling)
docker image prune -a

# Force without confirmation
docker image prune -a --force
```

**What This Removes:**
- ✅ Dangling images (intermediate layers)
- ✅ Images not used by any container (with -a flag)
- ✅ Old image versions

**Space Saved:** Usually 1-5 GB

---

### **Option 3: Remove Unused Containers** 📦 SAFE

Remove stopped containers that are no longer needed.

```bash
# Remove all stopped containers
docker container prune

# Force without confirmation
docker container prune --force

# Remove specific stopped container
docker rm <container_id>
```

**What This Removes:**
- ✅ All stopped containers
- ✅ Container logs
- ✅ Container metadata

**Space Saved:** Usually 100 MB - 1 GB

---

### **Option 4: Remove Unused Volumes** 💾 CAREFUL

Remove volumes not attached to any container.

```bash
# Remove all unused volumes
docker volume prune

# Force without confirmation
docker volume prune --force

# List all volumes first
docker volume ls

# Remove specific volume
docker volume rm <volume_name>
```

**What This Removes:**
- ✅ Volumes not attached to containers
- ✅ **DATABASE DATA** if volume is not in use

**⚠️ WARNING:** This can delete your database data! Check first:

```bash
# Check which volumes are in use
docker compose -f docker-compose.professional.yml ps -q | xargs docker inspect -f '{{ .Name }}: {{ range .Mounts }}{{ .Name }} {{ end }}'
```

**Space Saved:** Usually 500 MB - 5 GB

---

### **Option 5: Remove Build Cache** 🏗️ VERY SAFE

Remove Docker build cache to free up space without affecting running containers.

```bash
# Remove build cache
docker builder prune

# Remove ALL build cache (including used)
docker builder prune -a

# Force without confirmation
docker builder prune -a --force
```

**What This Removes:**
- ✅ Cached build layers
- ✅ Intermediate build images
- ✅ Unused build cache

**Space Saved:** Usually 1-3 GB

**Note:** Next build will be slower but will work fine.

---

### **Option 6: Remove Unused Networks** 🌐 SAFE

Remove networks not used by any container.

```bash
# Remove all unused networks
docker network prune

# Force without confirmation
docker network prune --force
```

**What This Removes:**
- ✅ Networks not used by containers
- ✅ Old network configurations

**Space Saved:** Usually < 10 MB (minimal)

---

## 🎯 Recommended Space Cleanup Workflow

### **Safe Cleanup (Recommended):**

```bash
# 1. Check current usage
docker system df

# 2. Remove build cache (safest, biggest impact)
docker builder prune -a --force

# 3. Remove unused images
docker image prune -a --force

# 4. Remove stopped containers
docker container prune --force

# 5. Remove unused networks
docker network prune --force

# 6. Check space saved
docker system df
```

**Expected Space Saved:** 2-8 GB

---

### **Aggressive Cleanup (When Desperate for Space):**

```bash
# 1. Backup database first!
docker compose -f docker-compose.professional.yml exec db pg_dump -U postgres users_dev > backup.sql

# 2. Stop your app
docker compose -f docker-compose.professional.yml down

# 3. Nuclear cleanup
docker system prune -a --volumes --force

# 4. Rebuild your app
docker compose -f docker-compose.professional.yml up -d --build

# 5. Restore data if needed
docker compose -f docker-compose.professional.yml exec -T db psql -U postgres users_dev < backup.sql
```

**Expected Space Saved:** 5-20 GB

---

### **Surgical Cleanup (Keep Your App Running):**

```bash
# Remove only what's safe while app is running
docker image prune -a --force
docker builder prune -a --force
docker container prune --force
docker network prune --force

# Skip volume prune to keep database data
```

**Expected Space Saved:** 2-5 GB

---

## 📊 Space Cleanup Comparison

| Command | Safety | Space Saved | Affects Running App |
|---------|--------|-------------|---------------------|
| `builder prune -a` | ✅ Very Safe | 1-3 GB | ❌ No |
| `image prune -a` | ✅ Safe | 1-5 GB | ❌ No |
| `container prune` | ✅ Safe | 100 MB - 1 GB | ❌ No |
| `network prune` | ✅ Safe | < 10 MB | ❌ No |
| `volume prune` | ⚠️ Careful | 500 MB - 5 GB | ⚠️ Can delete data |
| `system prune -a --volumes` | ⚠️ Dangerous | 5-20 GB | ⚠️ Deletes everything |

---

## 🔍 Before/After Verification

### **Before Cleanup:**

```bash
# Check disk usage
docker system df

# List all images
docker images

# List all containers
docker ps -a

# List all volumes
docker volume ls

# Check system disk space
df -h
```

### **After Cleanup:**

```bash
# Verify space freed
docker system df

# Verify app still works
docker compose -f docker-compose.professional.yml ps
curl http://localhost:5001/ping
curl http://localhost:3001
```

---

## 💡 Pro Tips

### **Prevent Space Issues:**

1. **Regular Cleanup Schedule:**
   ```bash
   # Add to cron (weekly cleanup)
   0 2 * * 0 docker builder prune -a --force && docker image prune -a --force
   ```

2. **Monitor Docker Space:**
   ```bash
   # Create alias for quick check
   alias docker-space='docker system df'
   ```

3. **Limit Log Size:**
   Add to `docker-compose.professional.yml`:
   ```yaml
   services:
     backend:
       logging:
         driver: "json-file"
         options:
           max-size: "10m"
           max-file: "3"
   ```

4. **Use .dockerignore:**
   Prevent unnecessary files from being copied into images.

---

## ✅ Summary

**Quick Reference:**

| Goal | Command |
|------|---------|
| Complete fresh start | `docker compose -f docker-compose.professional.yml down -v && docker compose -f docker-compose.professional.yml up -d --build` |
| Re-seed data | `docker compose -f docker-compose.professional.yml exec backend rm -f /usr/src/app/.data_seeded && docker compose -f docker-compose.professional.yml restart backend` |
| Manual seed | `docker compose -f docker-compose.professional.yml exec backend python manage.py seed_demo_data` |
| Recreate DB | `docker compose -f docker-compose.professional.yml exec backend python manage.py recreate_db` |
| Simple restart | `docker compose -f docker-compose.professional.yml restart` |
| **Free up space (safe)** | `docker builder prune -a --force && docker image prune -a --force && docker container prune --force` |
| **Free up space (aggressive)** | `docker system prune -a --volumes --force` |
| **Check space usage** | `docker system df` |

---

**Status:** ✅ COMPLETE - All cleanup and space management options documented

