# COMPREHENSIVE SYSTEM SPECIFICATION
## Microfinance Savings Group Management Platform

**Version:** 1.0
**Last Updated:** October 29, 2025
**Status:** Production Ready
**Overall Progress:** 100% Complete (All 7 Phases)
**Database Tables:** 63 (All 7 Phases)

---

## EXECUTIVE SUMMARY

This document provides complete technical specifications for rebuilding the Microfinance Savings Group Management Platform from scratch. The system is a full-stack web application with React frontend, Flask backend, and PostgreSQL database, deployed via Docker Compose.

**Key Characteristics:**
- **7 Complete Phases** of microfinance functionality
- **63 Database Tables** created from ORM models
- **3 Savings Groups** with 53 total members
- **60 Monthly Meetings** with complete financial tracking
- **Mobile Money Integration** (MTN, Airtel)
- **Loan Assessment & Management** with automated scoring
- **Achievement System** with badges and leaderboards
- **Professional Attendance Tracking** with QR codes and GPS
- **Real-time Notifications** system
- **Social Engagement** features

---

## ARCHITECTURE OVERVIEW

### Technology Stack

**Frontend:**
- React 18 with functional components and hooks
- Material-UI v5 for professional UI components
- React Query v5 (@tanstack/react-query) for data fetching
- React Router v6 for navigation
- Axios with JWT interceptor for API calls
- Nginx reverse proxy in Docker

**Backend:**
- Flask (Python) with Blueprint architecture
- SQLAlchemy ORM for database abstraction
- Flask-CORS for cross-origin requests
- Flask-SQLAlchemy for database integration
- Alembic for migration tracking
- JWT authentication with token-based access

**Database:**
- PostgreSQL 15 Alpine
- 63 tables across 7 phases
- Automatic SQL migrations on startup
- Persistent volume for data durability

**Deployment:**
- Docker Compose for local development
- Docker containers for all services
- Professional networking and health checks
- Adminer for database management

---

## PHASE DEFINITIONS

### Phase 1: Member Financial Dashboard (100% Complete)
**Core Features:**
- Group management with location fields (District, Parish, Village)
- Member profiles with financial tracking
- Multiple saving types (Personal, ECD Fund, Social Fund)
- Member savings tracking by type
- Saving transactions with mobile money support
- Group cashbook with running balances
- Meeting attendance tracking
- Member fines management
- **Document upload for meeting activities** (PDF, Word, PowerPoint, images)
- Real-time financial aggregation
- **Professional UI/UX with 6 detailed financial cards**
- **Fully functional navigation and error handling**

**UI Components (Complete):**
- `SavingsProgressCard` - Total savings with progress bar and trend indicators
- `SavingsByFundCard` - Fund breakdown visualization
- `LoanStatusCard` - Loan eligibility status with working navigation
- `PerformanceComparisonCard` - Member vs group comparison
- `FinancialMetricsCard` - Attendance, training, fines tracking
- `IGADashboardCard` - IGA participation summary with navigation

**Key Tables:**
- `savings_groups`, `group_members`, `saving_types`, `member_savings`
- `saving_transactions`, `group_cashbook`, `meeting_attendance`, `member_fines`
- `activity_documents`, `activity_document_audit_log` (document management)

### Phase 1.5: IGA (Income Generating Activities) (100% Complete)
**Core Features:**
- Complete IGA tracking system with 4 database tables
- Member-centric IGA participation and returns tracking
- IGA cashflow management (income, expenses, profit distribution)
- Group-level and individual member IGA summaries
- Integration with member financial dashboard and group reporting

**Database Tables:**
- `savings_group_iga` - IGA activity definitions and tracking
- `iga_member_participation` - Individual member participation in IGAs
- `iga_cashflow` - Complete cashflow tracking (income, expenses, distributions)
- `iga_member_returns` - Member profit/loss distributions from IGAs

**API Endpoints (10+):**
- Group IGA activities, member participation, cashflow tracking
- Member IGA summaries, group IGA summaries, returns distribution
- Complete CRUD operations for IGA management

### Phase 2: Loan Eligibility & Management (100% Complete)
**Core Features:**
- **Real-time loan eligibility checking** with instant feedback
- **Comprehensive assessment system** from eligibility to application submission
- **Professional loans dashboard** with view, search, and filter capabilities
- **4 major components** with 1,442 lines of production-ready code
- Automated loan eligibility assessment with industry-standard scoring
- Risk-based loan terms calculation
- Loan request workflow with 3-step guided process
- Loan approval and disbursement tracking
- Loan repayment schedules and overdue tracking
- Loan performance analytics

**UI Components (Complete):**
- `LoanAssessmentPage` (429 lines) - Group/member selection, real-time eligibility
- `LoansDashboard` (363 lines) - Summary stats, tabbed interface, search
- `LoanEligibilityChecker` (200 lines) - Reusable eligibility display component
- `LoanApplicationWorkflow` (300 lines) - 3-step guided application process

**Key Tables:**
- `group_loans`, `loan_assessments`, `loan_repayment_schedule`

### Phase 3: Achievements & Gamification (100% Complete)
**Core Features:**
- **Professional achievements hub** with 4-tab interface
- **Achievement browsing** with search and filter capabilities
- **Personal achievements tracking** with progress visualization
- **Leaderboard rankings** (global and group-level competition)
- **Certificate management** for earned achievements
- Achievement definitions and criteria with detailed requirements
- Badge system with visual rewards and color-coded categories
- Points-based scoring system with member tracking

**UI Components (Complete):**
- `AchievementsPage` (200 lines) - Main hub with 4 tabs (All, My, Leaderboard, Certificates)
- `AchievementDetailsPage` (280 lines) - Detailed view with member tracking
- `AchievementsList` - Browse all available achievements
- `MemberAchievements` - Personal achievements and progress
- `AchievementLeaderboard` - Global and group rankings
- `CertificateViewer` - View and manage earned certificates

**Key Tables:**
- `achievements`, `member_achievements`, `achievement_badges`, `member_badges`
- `achievement_leaderboard`

### Phase 4: Analytics & Reporting (100% Complete)
**Core Features:**
- **Professional analytics dashboard** with 4-tab interface
- **Financial analytics** with savings trends and member performance
- **Loan analytics** with portfolio and repayment tracking
- **Achievement analytics** with engagement metrics and progress
- **Group analytics** with health scores and performance metrics
- **Date range filtering** (7, 30, 90, 365 day views)
- **Export functionality** for report generation and download
- Real-time analytics snapshots with automatic updates
- Comprehensive reporting system with 12 API endpoints

**UI Components (Complete):**
- `AnalyticsPage` (75 lines) - Main page with automatic group detection
- `AnalyticsDashboard` (200 lines) - 4-tab dashboard container
- `FinancialAnalytics` - Savings trends and top savers tracking
- `LoanAnalytics` - Loan portfolio and repayment analysis
- `AchievementAnalytics` - Member engagement and points tracking
- `GroupAnalytics` - Group health and member growth analysis

**Key Tables:**
- `analytics_snapshots`, `analytics_reports`, `member_analytics`

### Phase 5: Advanced Features (100% Complete)
**Core Features:**
- **Professional advanced features dashboard** with 3-tab interface
- **Document management system** with template creation and management
- **Mobile money integration** with multi-provider support (MTN, Airtel, Vodafone)
- **Advanced reporting** with custom report builder and scheduling
- Document templates and versioning with approval workflows
- Professional attendance sessions with QR code-based check-in
- GPS location verification and photo verification for attendance
- Biometric support and comprehensive tracking

**UI Components (Complete):**
- `AdvancedFeaturesPage` (70 lines) - Main page with automatic group detection
- `MobileMoneyPage` (70 lines) - Dedicated mobile money dashboard
- `AdvancedFeaturesDashboard` - 3-tab dashboard (Documents, Mobile Money, Reporting)
- `MobileMoneyDashboard` - 4-tab dashboard (Record, Verify, Settings, Reports)
- Document management components with template creation
- Mobile money components with provider configuration

**API Integration (14 Endpoints):**
- Document Management (5 endpoints) - Templates, versions, approvals
- Mobile Money (5 endpoints) - Providers, transactions, reconciliation
- Advanced Reporting (4 endpoints) - Schedules, custom reports

**Key Tables:**
- `document_templates`, `document_versions`, `document_approvals`
- `attendance_sessions`, `attendance_records`

### Phase 6: Intelligence & AI (100% Complete)
**Core Features:**
- **Professional intelligence dashboard** with 4-tab interface
- **Loan default risk predictions** with risk scores and confidence metrics
- **Savings growth forecasts** with 12-month projections
- **Personalized recommendation engine** with priority-based filtering
- **Automatic anomaly detection** with severity classification
- **AI-generated insights** with group risk assessment
- Rule-based algorithms with no external API dependencies
- Member risk assessment and loan default prediction

**UI Components (Complete):**
- `IntelligencePage` (70 lines) - Main page with automatic group detection
- `IntelligenceDashboard` (100 lines) - 4-tab dashboard container
- `PredictionDashboard` (200 lines) - Loan and savings predictions
- `RecommendationEngine` (220 lines) - Personalized member recommendations
- `AnomalyDetector` (240 lines) - Automatic anomaly detection
- `InsightViewer` (260 lines) - AI-generated insights display

**API Integration (10 Endpoints):**
- Predictions (2 endpoints) - Loan default risk, savings growth
- Recommendations (1 endpoint) - Personalized recommendations
- Anomalies (1 endpoint) - Anomaly detection
- Insights (1 endpoint) - AI insights generation
- Risk Assessment (1 endpoint) - Risk evaluation
- Models (2 endpoints) - Model status, feedback
- Health Check (1 endpoint) - System health

### Phase 7: Social Engagement (100% Complete)
**Core Features:**
- **Automatic posting for all CRUD activities** (CREATE, UPDATE, DELETE operations)
- **@ mention system** with autocomplete and real-time notifications
- **Database-stored notifications** retrieved on login with unread counts
- Activity feed with manual and automatic posts
- Comment system with threaded conversations and replies
- Reaction system (like, celebrate, inspire, motivate)
- **Privacy levels** (real_name, pseudonym, anonymous, spoofed)
- **Admin controls** for content moderation and approval workflows
- Hashtag support for post categorization
- Cross-group sharing capabilities
- Member blocking and content moderation
- Leaderboard integration for engagement metrics
- Complete audit trail for all social activities

**Key Tables:**
- `social_posts`, `social_comments`, `social_reactions`, `social_mentions`
- `social_hashtags`, `social_post_hashtags`, `social_attachments`
- `social_admin_settings`, `social_member_settings`, `social_moderation_logs`
- `social_blocked_members`, `social_post_views`

---

## DATABASE SCHEMA

### Core Tables (Phase 1)

**users** - System users and authentication
- id, username, email, password, active, admin, role, is_super_admin, created_date

**savings_groups** - Savings group definitions
- id, name, description, status, country, district, parish, village
- constitution_file, registration_certificate, created_date, updated_date

**group_members** - Group membership
- id, group_id, user_id, first_name, last_name, email, phone_number
- id_number, date_of_birth, gender, occupation, status, joined_date
- is_active, role, share_balance, total_contributions, attendance_percentage
- is_eligible_for_loans, created_date, updated_date

**saving_types** - Configurable saving categories
- id, name, code, description, is_active, requires_target, allows_withdrawal
- minimum_amount, maximum_amount, created_by, created_date, updated_date

**member_savings** - Individual member savings by type
- id, member_id, saving_type_id, current_balance, target_amount, target_date
- target_description, is_target_achieved, target_achieved_date
- created_date, updated_date

**saving_transactions** - All savings transactions
- id, member_id, saving_type_id, transaction_type, amount, balance_after
- mobile_money_provider, mobile_money_phone, status, processed_date
- created_date, updated_date

**group_cashbook** - Financial ledger
- id, group_id, entry_type, amount, reference_number, status
- approved_by, approved_date, created_date, updated_date

**meeting_attendance** - Meeting participation tracking
- id, group_id, member_id, meeting_date, meeting_type, attended
- attendance_time, excuse_reason, contributed_to_meeting, meeting_notes
- recorded_by, recorded_date

**member_fines** - Disciplinary fines
- id, member_id, fine_type, reason, amount, status, paid_date
- created_by, created_date

### Loan Management Tables (Phase 2)

**group_loans** - Loan records
- id, group_id, member_id, loan_type, amount, interest_rate
- repayment_frequency, repayment_status, total_repaid, outstanding_balance
- approved_by, approved_date, created_date, updated_date

**loan_assessments** - Eligibility assessments
- id, member_id, assessment_date, is_eligible, score, reasons
- recommendations, created_date, updated_date

**loan_repayment_schedule** - Payment schedules
- id, loan_id, due_date, amount_due, amount_paid, status
- created_date, updated_date

### Achievement Tables (Phase 3)

**achievements** - Achievement definitions
- id, name, description, category, criteria_type, criteria_value
- criteria_duration_days, points, icon_url, created_date

**member_achievements** - Member achievement records
- id, member_id, achievement_id, earned_date, points_earned

**achievement_badges** - Badge definitions
- id, name, description, icon_url, color, created_date

**member_badges** - Member badge assignments
- id, member_id, badge_id, earned_date

**achievement_leaderboard** - Materialized leaderboard
- id, member_id, group_id, total_achievements, total_points
- total_badges, rank_in_group, rank_in_system

### Analytics Tables (Phase 4)

**analytics_snapshots** - Point-in-time analytics
- id, group_id, snapshot_date, total_members, total_savings
- total_loans, average_attendance, created_date

**analytics_reports** - Generated reports
- id, group_id, report_type, report_data, generated_date

**member_analytics** - Individual member metrics
- id, member_id, metric_name, metric_value, calculated_date

### Advanced Features Tables (Phase 5)

**attendance_sessions** - Professional attendance management
- id, meeting_id, session_code, qr_code_data, meeting_latitude
- meeting_longitude, geofence_radius_meters, check_in_opens, check_in_closes
- late_threshold_minutes, is_active, total_expected_attendees, total_checked_in
- requires_photo_verification, requires_location_verification, allows_remote_attendance
- created_by, created_date

**attendance_records** - Individual attendance records
- id, session_id, member_id, check_in_method, attendance_status, check_in_time
- location_latitude, location_longitude, location_accuracy_meters
- photo_verification_url, device_info, participation_score
- participated_in_discussions, contributed_to_savings, voted_on_decisions
- excuse_reason, excuse_approved_by, excuse_approved_date
- recorded_by, recorded_date

**document_templates** - Document templates
- id, name, description, template_content, created_by, created_date

**document_versions** - Document versioning
- id, template_id, version_number, content, created_by, created_date

**document_approvals** - Approval workflows
- id, document_id, approver_id, status, approved_date

### Mobile Money Tables (Phase 1 Extension)

**mobile_money_accounts** - Mobile money account linking
- id, member_id, provider, phone_number, account_status, created_date

**mobile_money_payments** - Mobile money transactions
- id, account_id, transaction_id, amount, status, created_date

**mobile_money_verification** - Transaction verification
- id, payment_id, verification_status, verified_by, verified_date

### Social Engagement Tables (Phase 7)

**social_posts** - Main social posts with automatic CRUD activity posting
- id, group_id, member_id, post_type, activity_type, activity_id
- title, content, privacy_level, visibility, status, attachment_ids
- created_date, updated_date, published_date, created_by, updated_by

**social_comments** - Threaded comments with replies
- id, post_id, member_id, parent_comment_id, content, privacy_level
- status, created_date, updated_date, created_by, updated_by

**social_reactions** - Emoji reactions (like, celebrate, inspire, motivate)
- id, post_id, comment_id, member_id, reaction_type, created_date

**social_mentions** - @ mention system with notifications
- id, post_id, comment_id, mentioned_member_id, mentioned_by_member_id
- mention_text, created_date

**social_hashtags** - Hashtag definitions
- id, hashtag, description, created_date

**social_post_hashtags** - Post-hashtag mapping
- id, post_id, hashtag_id

**social_attachments** - File attachments for posts
- id, post_id, file_name, file_path, file_type, file_size, created_date

**social_admin_settings** - Group admin controls
- id, group_id, auto_post_savings, auto_post_loans, auto_post_achievements
- auto_post_meetings, auto_post_iga, default_privacy_level, require_approval
- enable_moderation, allow_cross_group_posts, allow_public_posts

**social_member_settings** - Member privacy preferences
- id, member_id, default_privacy_level, allow_mentions, allow_notifications
- block_anonymous_posts, created_date, updated_date

**social_moderation_logs** - Content moderation audit trail
- id, post_id, comment_id, moderator_id, action, reason, created_date

**social_blocked_members** - Member blocking system
- id, blocker_member_id, blocked_member_id, reason, created_date

**social_post_views** - Post view analytics
- id, post_id, member_id, view_date, view_duration

### Meeting & Activity Tables

**meetings** - Meeting instances
- id, group_id, meeting_number, meeting_date, meeting_time, meeting_type
- location, status, agenda, minutes, total_members, members_present
- attendance_count, quorum_met, total_savings_collected, total_fines_collected
- total_loan_repayments, loans_disbursed_count, recorded_by, scheduled_by
- created_by, created_date, updated_date

**meeting_activities** - Activities during meetings
- id, meeting_id, activity_type, description, created_date

**member_activity_participation** - Member participation in activities
- id, activity_id, member_id, participation_status, created_date

**activity_documents** - Document attachments for meeting activities
- id, meeting_activity_id, member_participation_id, meeting_id, document_type
- file_name, original_file_name, file_path, file_size, file_type, mime_type
- title, description, access_level, is_verified, verified_by, verified_date
- verification_notes, uploaded_by, upload_date, created_date, updated_date

**activity_document_audit_log** - Audit trail for document operations
- id, document_id, action, action_by, action_date, details

**activity_documents** - Document attachments for activities
- id, activity_id, document_url, document_type, created_date

### IGA (Income Generating Activities) Tables

**savings_group_iga** - IGA definitions
- id, group_id, name, description, status, created_date

**iga_member_participation** - Member participation
- id, iga_id, member_id, participation_status, created_date

**iga_cashflow** - IGA financial tracking
- id, iga_id, transaction_type, amount, created_date

**iga_member_returns** - Member returns from IGA
- id, iga_id, member_id, return_amount, created_date

---

## GROUP FORMATION & MEMBER REGISTRATION

### Group Formation Process

**Group Creation Workflow:**
1. **Permission Check** - Only admins or existing group officers can create groups
2. **Location Setup** - Country, Region, District, Parish, Village (required)
3. **Group Configuration** - Name, description, target amount, max members (30)
4. **Founder Assignment** - Creator becomes first officer (Secretary, Chair, or Treasurer)
5. **Group Code Generation** - Unique code format: `SG-YYYYMMDD-XXXX`

**Group Attributes:**
- **Location:** Country, Region, District, Parish, Village
- **Details:** Name, description, group_code, formation_date
- **Financial:** Target amount, minimum contribution, meeting frequency
- **Governance:** Constitution document, registration certificate
- **Leadership:** Chair, Secretary, Treasurer (officer assignments)
- **Lifecycle:** FORMING → ACTIVE → MATURE → ELIGIBLE_FOR_LOAN → LOAN_ACTIVE → CLOSED

### Member Registration Process

**Member Registration Workflow:**
1. **Permission Check** - Only group officers or admins can add members
2. **Group Capacity Check** - Ensure group not full (max 30 members)
3. **User Creation/Assignment** - Create new user or assign existing user
4. **Member Profile Creation** - Complete member attributes and information
5. **Role Assignment** - MEMBER, OFFICER, or FOUNDER role
6. **Notification** - Member notified of group addition

**Member Attributes:**
- **Personal:** First name, last name, email, phone, ID number, date of birth, gender, occupation
- **Membership:** Status (ACTIVE/INACTIVE/SUSPENDED), joined date, role (MEMBER/OFFICER/FOUNDER)
- **Financial:** Share balance, total contributions, attendance percentage, loan eligibility
- **Performance:** Auto-calculated attendance %, participation score, loan eligibility status

### Officer Management System

**Officer Roles:**
- **Chairperson** - Meeting leadership, decision making
- **Secretary** - Record keeping, documentation
- **Treasurer** - Financial management, cashbook

**Officer Permissions:**
- Add/remove members, create meetings, financial management, role assignments
- Only officers can add new members to groups
- Officers receive notifications of role assignments

## PROFESSIONAL FILTERING SYSTEM

### Multi-Dimensional Filtering

**Filtering Capabilities Across All Phases:**
- **Group-Based:** Filter by groups, group state, location, size
- **Member-Based:** Filter by gender, role, membership duration, performance
- **Meeting-Based:** Filter by status, type, date range, leadership
- **Activity-Based:** Filter by type, fund type, amount range, verification status
- **Financial:** Filter by transaction amounts, fund types, payment methods

**Filter Integration:**
- All phases support comprehensive filtering by relevant attributes
- Real-time aggregation with filtering applied
- Professional FilterProcessor class handles complex filter combinations
- Standardized filter parameters across all API endpoints

## SEEDING DATA

### Initial Data Created on Rebuild

**Admin User:**
- Email: admin@savingsgroup.com
- Password: admin123
- Role: super_admin

**3 Savings Groups:**
1. **Kigali Savings Group** - Kigali, Rwanda
   - 18 members with complete officer assignments
   - 20 meetings with leadership roles
   - Complete financial data and IGA activities

2. **Muhanga Savings Group** - Muhanga, Rwanda
   - 18 members
   - 20 meetings
   - Complete financial data

3. **Gitarama Savings Group** - Gitarama, Rwanda
   - 17 members
   - 20 meetings
   - Complete financial data

**Total Members:** 53 across all groups

**Meeting Data:**
- 60 total meetings (20 per group)
- Monthly meetings from January to December 2024
- Attendance records for all members
- Financial transactions for each meeting

**Financial Data:**
- Saving types: Personal, ECD Fund, Social Fund
- Member savings with balances
- Saving transactions with mobile money support
- Group cashbook entries
- Member fines and penalties

**Loan Data:**
- Loan assessments for eligible members
- Loan records with repayment schedules
- Loan repayment tracking

**Mobile Money Accounts:**
- MTN and Airtel accounts for members
- Transaction history
- Verification records

---

## DEPLOYMENT INSTRUCTIONS

### Prerequisites
- Docker and Docker Compose installed
- 4GB RAM minimum
- 10GB disk space
- Ports 3001, 5001, 5432, 8080 available

### One-Command Rebuild

```bash
cd /path/to/testdriven-appcopy
bash scripts/rebuild-final.sh
```

This single command:
1. Stops and removes all containers
2. Removes volumes and images
3. Builds fresh Docker images
4. Starts all services
5. Waits for database readiness
6. Runs SQL migrations (creates 63 tables)
7. Seeds initial data (3 groups, 53 members, 60 meetings)
8. Verifies all services are running

### Access Points

**Frontend:** http://localhost:3001  
**Backend API:** http://localhost:5001  
**Database Admin:** http://localhost:8080 (Adminer)

**Login Credentials:**
- Email: admin@savingsgroup.com
- Password: admin123

**Database Credentials (Adminer):**
- System: PostgreSQL
- Server: db
- Username: postgres
- Password: postgres
- Database: users_dev

---

## KEY API ENDPOINTS

### Authentication
- `POST /api/auth/login` - User login
- `POST /api/auth/logout` - User logout
- `GET /api/auth/status` - Check authentication status

### Savings Groups
- `GET /api/savings-groups` - List all groups
- `GET /api/savings-groups/{id}` - Get group details
- `POST /api/savings-groups` - Create new group
- `PUT /api/savings-groups/{id}` - Update group

### Members
- `GET /api/savings-groups/{id}/members` - List group members
- `POST /api/savings-groups/{id}/members` - Add member
- `GET /api/members/{id}` - Get member details
- `PUT /api/members/{id}` - Update member

### Meetings
- `GET /api/meetings` - List meetings
- `POST /api/meetings` - Create meeting
- `GET /api/meetings/{id}` - Get meeting details
- `POST /api/meetings/{id}/attendance` - Record attendance

### Loans
- `GET /api/loans` - List loans
- `POST /api/loans` - Create loan
- `GET /api/loans/{id}/assessment` - Get loan assessment
- `POST /api/loans/{id}/repayment` - Record repayment

### Achievements
- `GET /api/achievements` - List achievements
- `GET /api/achievements/leaderboard` - Get leaderboard
- `GET /api/members/{id}/achievements` - Get member achievements

### Analytics
- `GET /api/analytics/groups/{id}` - Group analytics
- `GET /api/analytics/members/{id}` - Member analytics
- `GET /api/analytics/reports` - Generate reports

### Mobile Money
- `POST /api/mobile-money/accounts` - Link mobile money account
- `POST /api/mobile-money/transactions` - Record transaction
- `GET /api/mobile-money/verification/{id}` - Verify transaction

### Document Management
- `POST /api/meeting-activities/activities/{id}/documents/upload` - Upload document
- `GET /api/meeting-activities/activities/{id}/documents` - List documents
- `GET /api/meeting-activities/activities/{id}/documents/{doc_id}/download` - Download document
- `DELETE /api/meeting-activities/activities/{id}/documents/{doc_id}` - Delete document
- `PUT /api/meeting-activities/activities/{id}/documents/{doc_id}/verify` - Verify document
- `GET /api/meeting-activities/activities/{id}/documents/{doc_id}/audit-log` - View audit trail

### Social Engagement (Phase 7)
- `GET /api/social/posts` - Get social feed posts with filtering
- `POST /api/social/posts` - Create manual post
- `GET /api/social/posts/{id}` - Get specific post details
- `PUT /api/social/posts/{id}` - Update post
- `DELETE /api/social/posts/{id}` - Delete post
- `GET /api/social/posts/{id}/comments` - Get post comments
- `POST /api/social/comments` - Create comment or reply
- `PUT /api/social/comments/{id}` - Update comment
- `DELETE /api/social/comments/{id}` - Delete comment
- `POST /api/social/reactions` - Add reaction to post/comment
- `DELETE /api/social/reactions/{id}` - Remove reaction
- `GET /api/social/leaderboard/engagement` - Get engagement leaderboard
- `GET /api/social/admin/settings` - Get admin settings
- `PUT /api/social/admin/settings` - Update admin settings
- `GET /api/social/admin/analytics` - Get social analytics

### Notifications
- `GET /api/notifications` - List notifications (includes social notifications)
- `PUT /api/notifications/{id}` - Mark as read
- `DELETE /api/notifications/{id}` - Delete notification

---

## TESTING & VALIDATION

### E2E Tests
Located in `tests/test_e2e_all_phases.py`
- 25 comprehensive tests
- 100% pass rate
- All 7 phases validated
- Real data testing

### Running Tests
```bash
cd /path/to/testdriven-appcopy
python -m pytest tests/test_e2e_all_phases.py -v
```

### Manual Testing Checklist
1. ✅ Login with admin credentials
2. ✅ View all 3 groups
3. ✅ View all 53 members
4. ✅ View 60 meetings
5. ✅ Check member financial summaries
6. ✅ Verify loan assessments
7. ✅ Check achievement leaderboard
8. ✅ Test mobile money integration
9. ✅ Verify notifications system
10. ✅ Check analytics reports

---

## TROUBLESHOOTING

### Database Connection Issues
```bash
# Check database status
docker-compose -f docker-compose.professional.yml exec db pg_isready

# View database logs
docker logs testdriven_db
```

### Backend API Issues
```bash
# Check backend logs
docker logs testdriven_backend

# Test API endpoint
curl http://localhost:5001/api/auth/status
```

### Frontend Issues
```bash
# Check frontend logs
docker logs testdriven_frontend

# Verify frontend is serving
curl http://localhost:3001
```

### Complete Reset
```bash
# Full cleanup and rebuild
docker-compose -f docker-compose.professional.yml down -v
bash scripts/rebuild-final.sh
```

---

## MAINTENANCE & UPDATES

### Database Backups
```bash
# Backup database
docker-compose -f docker-compose.professional.yml exec db pg_dump -U postgres users_dev > backup.sql

# Restore database
docker-compose -f docker-compose.professional.yml exec -T db psql -U postgres users_dev < backup.sql
```

### Logs Location
- Backend logs: `services/users/logs/`
- Docker logs: `docker logs <container_name>`

### Performance Monitoring
- Database: Adminer at http://localhost:8080
- Backend: Check logs for errors
- Frontend: Browser developer tools

---

## SUPPORT & DOCUMENTATION

For detailed information, refer to:
- `REBUILD_PROCEDURE.md` - Rebuild process
- `README.md` - Project overview
- `docs/` - Additional documentation
- `tests/` - Test examples

---

**End of Specification Document**

