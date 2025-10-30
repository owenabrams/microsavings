# Contributing Guidelines

## For AI Agents Working on This Codebase

### 🚫 DO NOT Create These Files

**Never create AI-generated documentation files with these patterns:**
- `*_SUMMARY.md`
- `*_GUIDE.md`
- `*_COMPLETE.md`
- `*_REPORT.md`
- `*_PLAN.md`
- `*_ANALYSIS.md`
- `*_LESSONS*.md`
- `*_HANDOFF*.md`
- `*_TESTING*.md`
- `*_REFERENCE.md`
- Any other AI conversation artifacts

**These patterns are blocked in `.gitignore`**

### ✅ Essential Documentation Only

**Only these documentation files should exist:**
1. `README.md` - Main project documentation (keep concise)
2. `SYSTEM_SPECIFICATION_COMPLETE.md` - Feature specifications for all 7 phases
3. `ORM_DATABASE_ALIGNMENT_GUIDE.md` - Database schema and ORM alignment reference
4. `CLEAN_SLATE_REBUILD_SUCCESS_REPORT.md` - Rebuild procedures and troubleshooting
5. `CONTRIBUTING.md` - This file

### 📁 Essential Files Structure

```
microsavings/
├── README.md                        # Main documentation
├── SYSTEM_SPECIFICATION_COMPLETE.md # Feature specs
├── ORM_DATABASE_ALIGNMENT_GUIDE.md  # Database reference
├── CLEAN_SLATE_REBUILD_SUCCESS_REPORT.md # Rebuild guide
├── CONTRIBUTING.md                  # This file
├── .gitignore                       # Git ignore patterns
├── docker-compose.professional.yml  # Docker orchestration
├── client/                          # React frontend
│   ├── src/
│   │   ├── components/             # UI components
│   │   └── services/api.js         # API client
│   ├── Dockerfile
│   ├── nginx.conf
│   └── package.json
├── services/users/                  # Flask backend
│   ├── project/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   └── api/                    # API endpoints
│   ├── scripts/                    # Utility scripts
│   ├── Dockerfile
│   ├── requirements.txt
│   └── manage.py
├── migrations/                      # Database schema
│   └── 000_unified_schema.sql
└── scripts/                         # Build scripts
    └── rebuild-final.sh
```

### 🔧 Development Workflow

**When implementing new features:**

1. **Read specifications** from `SYSTEM_SPECIFICATION_COMPLETE.md`
2. **Check database schema** in `ORM_DATABASE_ALIGNMENT_GUIDE.md`
3. **Write code** in appropriate directories:
   - Frontend components: `client/src/components/`
   - Backend APIs: `services/users/project/api/`
4. **Test locally** using Docker Compose
5. **Commit with clear messages** describing what was implemented
6. **Push to GitHub** to create recovery points

**DO NOT:**
- Create summary files of your work
- Create handoff documents
- Create analysis documents
- Create backup folders (use git instead)
- Create test files unless explicitly requested

### 🗑️ Cleanup Strategy

**If you find junk files:**
1. Remove them immediately
2. Update `.gitignore` if needed
3. Commit the cleanup with clear message
4. Push to GitHub

**Example cleanup:**
```bash
# Remove junk files
rm -f *_SUMMARY.md *_GUIDE.md *_COMPLETE.md

# Commit cleanup
git add -A
git commit -m "Cleanup: Remove AI-generated documentation junk"
git push origin main
```

### 📝 Code Quality Standards

**Backend (Flask):**
- Use blueprints for API organization
- Use `@authenticate` decorator for protected endpoints
- Handle ORM mismatches with raw SQL when needed
- Return consistent JSON responses

**Frontend (React):**
- Use functional components with hooks
- Use Material-UI components consistently
- Handle loading and error states
- Format currency with K/M notation
- Make components responsive (mobile + desktop)

**Database:**
- SQL migrations are source of truth
- Use `migrations/000_unified_schema.sql` as reference
- Check `ORM_DATABASE_ALIGNMENT_GUIDE.md` for known mismatches
- Use raw SQL when ORM doesn't match schema

### 🚀 Deployment

**Local development:**
```bash
docker compose -f docker-compose.professional.yml up -d --build
```

**Rebuild specific service:**
```bash
docker compose -f docker-compose.professional.yml up -d --build frontend
docker compose -f docker-compose.professional.yml up -d --build backend
```

**View logs:**
```bash
docker logs testdriven_frontend --tail 50
docker logs testdriven_backend --tail 50
```

### 🎯 Implementation Phases

**Current Status:** Phase 1 Complete

**Next Steps:**
- Phase 1.5: IGA (Income Generating Activities)
- Phase 2: Loan Management
- Phase 3: Achievements & Gamification
- Phase 4: Analytics & Reporting
- Phase 5: Advanced Features
- Phase 6: Intelligence & AI
- Phase 7: Social Engagement

See `SYSTEM_SPECIFICATION_COMPLETE.md` for detailed specifications of each phase.

### 💾 Git Workflow

**Commit frequently:**
- After completing each feature
- After fixing bugs
- After cleanup
- Before major refactoring

**Commit message format:**
```
<Type>: <Short description>

<Detailed description>
- Bullet point 1
- Bullet point 2
```

**Types:**
- `Feature:` - New feature implementation
- `Fix:` - Bug fix
- `Cleanup:` - Code cleanup or refactoring
- `Docs:` - Documentation updates
- `Config:` - Configuration changes

### 🔒 Security

- Never commit secrets or passwords
- Use environment variables for sensitive data
- Keep `.env` files in `.gitignore`
- Use JWT tokens for authentication

### 📊 Testing

**Manual testing:**
1. Login with `admin@savingsgroup.com` / `admin123`
2. Navigate through all implemented features
3. Check browser console for errors
4. Test responsive design
5. Verify data loads correctly

**When to write tests:**
- Only when explicitly requested by user
- Never create test files proactively
- Remove incomplete test files during cleanup

---

**Remember:** Keep the codebase clean, focused, and maintainable. Only essential files should exist in the repository.

