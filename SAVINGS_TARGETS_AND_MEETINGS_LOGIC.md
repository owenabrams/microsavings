# Savings Targets and Meeting Activities - Business Logic

**Date:** 2025-10-30  
**Status:** Documented and Ready for Implementation

---

## 📊 **Savings Targets System**

### **1. Individual Member Targets**

**How They're Set:** **Manual Entry**
- Admins/Group leaders manually set savings targets for each member
- Targets are stored in `group_members.target_amount` (or similar field)
- Each member can have a different target based on their capacity/agreement

**Relationship to Shares:** **Unrelated**
- Savings goals are **independent** of share purchases
- `share_balance` represents shares owned, NOT savings target
- Members can save any amount regardless of shares held

**Example:**
```
Member A: 10 shares, Target: 50,000 UGX
Member B: 5 shares, Target: 100,000 UGX
Member C: 15 shares, Target: 30,000 UGX
```

---

### **2. Group-Level Target**

**Calculation:** **Sum of All Member Targets**
- `savings_groups.target_amount` = Σ(all member targets)
- Automatically calculated/updated when member targets change
- Represents the collective savings goal for the entire group

**Example:**
```
Group Target = Member A (50,000) + Member B (100,000) + Member C (30,000)
            = 180,000 UGX
```

---

## 🏦 **Active Saving Types and Settings**

### **Filtering Logic**

Only **active and operational** saving types and settings should appear for members:

#### **1. Saving Types (Custom Financial Activities)**
- Filter: `saving_types.is_active = true`
- Only show saving types that are currently operational
- Examples: Emergency Fund, Social Fund, Development Fund

#### **2. Group Settings Flags**
Check these boolean flags in `savings_groups` table:
- ✅ **Fines** - `enable_fines = true`
- ✅ **Voting** - `enable_voting = true` (if exists)
- ✅ **Attendance** - `enable_attendance = true` (if exists)
- ✅ **Training** - `enable_training = true` (if exists)

#### **3. Loan Settings**
Check loan-related flags:
- ✅ **Loan Disbursement** - `enable_loans = true` or `loan_enabled = true`
- ✅ **Loan Repayment** - Same flag as disbursement

**Important:** Only show loan-related activities if loans are enabled for the group.

---

## 📅 **Meeting Activities - Transaction Recording**

### **Core Principle**

> **"During the meeting, each activity is recorded for each individual member, then aggregated for the whole group."**

---

### **Meeting Flow**

```
1. Create Meeting
   ↓
2. Record Attendance (for each member)
   ↓
3. Record Individual Transactions:
   - Deposits (per saving type)
   - Withdrawals (per saving type)
   - Fines (if enabled)
   - Loan Disbursements (if enabled)
   - Loan Repayments (if enabled)
   - Training Fees (if enabled)
   - Voting Fees (if enabled)
   ↓
4. Aggregate for Group
   - Total deposits by saving type
   - Total withdrawals by saving type
   - Total fines collected
   - Total loans disbursed
   - Total loan repayments
   - Attendance rate
   ↓
5. Close Meeting & Generate Summary
```

---

### **1. Meeting Creation**

**Table:** `group_meetings` (or create if doesn't exist)

**Fields:**
```sql
- id (PK)
- group_id (FK → savings_groups)
- meeting_date (DATE)
- meeting_number (INT) -- Sequential meeting number
- location (VARCHAR)
- agenda (TEXT)
- status (ENUM: 'scheduled', 'in_progress', 'completed', 'cancelled')
- created_by (FK → users)
- created_at (TIMESTAMP)
- completed_at (TIMESTAMP)
```

---

### **2. Attendance Recording**

**Table:** `meeting_attendance`

**Process:**
1. For each member in the group
2. Mark as Present/Absent/Excused
3. Record time of arrival (if present)
4. Apply attendance fine if absent (if `enable_fines = true`)

**Fields:**
```sql
- id (PK)
- meeting_id (FK → group_meetings)
- member_id (FK → group_members)
- status (ENUM: 'present', 'absent', 'excused')
- arrival_time (TIME)
- fine_applied (BOOLEAN)
- fine_amount (DECIMAL)
- notes (TEXT)
```

**Aggregation:**
```
Attendance Rate = (Present Members / Total Members) × 100%
Total Attendance Fines = Σ(fine_amount where fine_applied = true)
```

---

### **3. Savings Transactions (Deposits & Withdrawals)**

**Table:** `member_savings` (existing) or `meeting_transactions`

**Process:**
1. For each member present
2. For each **active** saving type
3. Record deposit or withdrawal amount
4. Update member's balance for that saving type

**Fields:**
```sql
- id (PK)
- meeting_id (FK → group_meetings)
- member_id (FK → group_members)
- saving_type_id (FK → saving_types)
- transaction_type (ENUM: 'deposit', 'withdrawal')
- amount (DECIMAL)
- balance_after (DECIMAL) -- Running balance
- recorded_by (FK → users)
- recorded_at (TIMESTAMP)
- notes (TEXT)
```

**Aggregation (per saving type):**
```
Total Deposits = Σ(amount where transaction_type = 'deposit')
Total Withdrawals = Σ(amount where transaction_type = 'withdrawal')
Net Change = Total Deposits - Total Withdrawals
```

---

### **4. Fines Recording**

**Table:** `member_fines` (existing)

**Process:**
1. Record fines for each member (if `enable_fines = true`)
2. Types: Attendance fine, Late arrival fine, Other fines
3. Track payment status

**Fields:**
```sql
- id (PK)
- meeting_id (FK → group_meetings)
- member_id (FK → group_members)
- fine_type (ENUM: 'attendance', 'late_arrival', 'other')
- amount (DECIMAL)
- reason (TEXT)
- paid (BOOLEAN)
- paid_at (TIMESTAMP)
```

**Aggregation:**
```
Total Fines Issued = Σ(amount)
Total Fines Paid = Σ(amount where paid = true)
Outstanding Fines = Total Fines Issued - Total Fines Paid
```

---

### **5. Loan Transactions**

**Only if `enable_loans = true`**

#### **A. Loan Disbursements**

**Table:** `group_loans` (existing)

**Process:**
1. Disburse approved loans during meeting
2. Record disbursement amount and date
3. Update loan status to 'active'

**Fields:**
```sql
- id (PK)
- meeting_id (FK → group_meetings) -- Meeting where disbursed
- member_id (FK → group_members)
- loan_amount (DECIMAL)
- disbursement_date (DATE)
- status (ENUM: 'approved', 'active', 'repaid', 'defaulted')
```

**Aggregation:**
```
Total Loans Disbursed = Σ(loan_amount where disbursement_date = meeting_date)
```

#### **B. Loan Repayments**

**Table:** `loan_repayments` (create if doesn't exist)

**Process:**
1. Record repayment amount from each member with active loan
2. Update outstanding balance
3. Mark loan as 'repaid' if fully paid

**Fields:**
```sql
- id (PK)
- meeting_id (FK → group_meetings)
- loan_id (FK → group_loans)
- member_id (FK → group_members)
- repayment_amount (DECIMAL)
- principal_amount (DECIMAL)
- interest_amount (DECIMAL)
- outstanding_balance (DECIMAL) -- After this payment
- repayment_date (DATE)
```

**Aggregation:**
```
Total Repayments = Σ(repayment_amount)
Total Principal Repaid = Σ(principal_amount)
Total Interest Collected = Σ(interest_amount)
```

---

### **6. Training Records**

**Only if `training_session_enabled = true`**

**Table:** `training_records` (create if doesn't exist)

**Process:**
1. Record training sessions conducted during meetings
2. Track which members attended each training
3. Calculate participation rates

**Fields:**
```sql
- id (PK)
- meeting_id (FK → group_meetings)
- training_topic VARCHAR(255) NOT NULL
- training_description TEXT
- trainer_name VARCHAR(255)
- duration_minutes INTEGER
- created_at TIMESTAMP
```

**Member Participation Table:** `training_attendance`
```sql
- id (PK)
- training_id (FK → training_records)
- member_id (FK → group_members)
- attended BOOLEAN DEFAULT FALSE
- notes TEXT
```

**Aggregation:**
```
Total Trainings Held = COUNT(training_records)
Member Training Attendance = COUNT(training_attendance where attended = true)
Member Training Participation Rate = (Attended / Total Trainings) × 100%
```

---

### **7. Voting Records**

**Only if `voting_session_enabled = true`**

**Table:** `voting_records` (create if doesn't exist)

**Process:**
1. Record voting sessions/decisions made during meetings
2. Track how each member voted
3. Calculate participation rates

**Fields:**
```sql
- id (PK)
- meeting_id (FK → group_meetings)
- vote_topic VARCHAR(255) NOT NULL
- vote_description TEXT
- vote_type VARCHAR(50) -- 'SIMPLE_MAJORITY', 'TWO_THIRDS', 'UNANIMOUS'
- result VARCHAR(50) -- 'PASSED', 'FAILED', 'DEFERRED'
- yes_count INTEGER DEFAULT 0
- no_count INTEGER DEFAULT 0
- abstain_count INTEGER DEFAULT 0
- created_at TIMESTAMP
```

**Member Votes Table:** `member_votes`
```sql
- id (PK)
- voting_record_id (FK → voting_records)
- member_id (FK → group_members)
- vote_cast VARCHAR(20) -- 'YES', 'NO', 'ABSTAIN', 'ABSENT'
- notes TEXT
```

**Aggregation:**
```
Total Voting Sessions = COUNT(voting_records)
Member Votes Cast = COUNT(member_votes where vote_cast IN ('YES', 'NO', 'ABSTAIN'))
Member Voting Participation Rate = (Votes Cast / Total Voting Sessions) × 100%
```

---

## 📊 **Dual Dashboard System**

### **Member Dashboard (Individual View)**

Each member sees their **own** data:
- Personal savings balance (by fund type)
- Personal attendance record (attended X out of Y meetings)
- Personal voting participation (voted X out of Y voting sessions)
- Personal training participation (attended X out of Y trainings)
- Personal fines (issued vs paid)
- Personal loans (active, repayments)
- Personal targets and progress

**Key Metrics:**
```
Attendance Rate = (Meetings Attended / Total Meetings) × 100%
Voting Participation = (Votes Cast / Total Voting Sessions) × 100%
Training Participation = (Trainings Attended / Total Trainings) × 100%
Savings Progress = (Current Savings / Target) × 100%
```

---

### **Group Dashboard (Aggregated View)**

Group leaders/admins see **aggregated** data for the entire group:
- Total group savings (by fund type)
- Group attendance rate (average across all members)
- Group voting participation rate
- Group training participation rate
- Total fines collected
- Total loans disbursed/repaid
- Group targets and progress

**Key Metrics:**
```
Group Attendance Rate = (Total Attendances / (Total Members × Total Meetings)) × 100%
Group Voting Participation = (Total Votes Cast / (Total Members × Total Voting Sessions)) × 100%
Group Training Participation = (Total Training Attendances / (Total Members × Total Trainings)) × 100%
Group Savings Progress = (Total Group Savings / Group Target) × 100%
```

---

## 📈 **Meeting Summary (Aggregated Data)**

After all individual transactions are recorded, generate a meeting summary:

**Table:** `meeting_summaries` (create)

**Fields:**
```sql
- id (PK)
- meeting_id (FK → group_meetings)
- total_members (INT)
- members_present (INT)
- attendance_rate (DECIMAL)
- total_deposits (DECIMAL)
- total_withdrawals (DECIMAL)
- total_fines_issued (DECIMAL)
- total_fines_paid (DECIMAL)
- total_loans_disbursed (DECIMAL)
- total_loan_repayments (DECIMAL)
- trainings_held (INT)
- training_attendance_count (INT)
- voting_sessions_held (INT)
- votes_cast_count (INT)
- net_cash_flow (DECIMAL) -- Deposits + Repayments + Fines - Withdrawals - Disbursements
- created_at (TIMESTAMP)
```

---

## 🎯 **Implementation Priority**

### **Phase 1: Core Meeting System**
1. ✅ Create `group_meetings` table
2. ✅ Create Meeting Management API (Create, List, Get, Update, Close)
3. ✅ Create Meeting UI (Create Meeting Dialog, Meeting List, Meeting Detail)

### **Phase 2: Attendance & Basic Transactions**
4. ✅ Implement Attendance Recording (with fines if enabled)
5. ✅ Implement Savings Transactions (Deposits/Withdrawals for active saving types)
6. ✅ Implement Fines Recording

### **Phase 3: Loan Transactions**
7. ✅ Implement Loan Disbursement Recording
8. ✅ Implement Loan Repayment Recording

### **Phase 4: Additional Activities**
9. ✅ Implement Training Fees (if enabled)
10. ✅ Implement Voting Fees (if enabled)

### **Phase 5: Aggregation & Reporting**
11. ✅ Calculate and store meeting summaries
12. ✅ Update group-level statistics
13. ✅ Update member-level statistics
14. ✅ Generate meeting reports

---

## 🔄 **Data Flow Example**

**Scenario:** Savings Group "Tumaini" holds Meeting #12 on 2025-10-30

### **Step 1: Create Meeting**
```json
{
  "group_id": 1,
  "meeting_date": "2025-10-30",
  "meeting_number": 12,
  "location": "Community Center",
  "status": "in_progress"
}
```

### **Step 2: Record Attendance**
```json
[
  {"member_id": 1, "status": "present", "arrival_time": "14:00"},
  {"member_id": 2, "status": "absent", "fine_applied": true, "fine_amount": 5000},
  {"member_id": 3, "status": "present", "arrival_time": "14:05"}
]
```

### **Step 3: Record Transactions (Member 1)**
```json
{
  "deposits": [
    {"saving_type_id": 1, "amount": 10000}, // Emergency Fund
    {"saving_type_id": 2, "amount": 5000}   // Social Fund
  ],
  "fines": [
    {"fine_type": "late_arrival", "amount": 1000}
  ],
  "loan_repayment": {
    "loan_id": 5,
    "amount": 20000,
    "principal": 18000,
    "interest": 2000
  }
}
```

### **Step 4: Aggregate for Group**
```json
{
  "total_members": 30,
  "members_present": 28,
  "attendance_rate": 93.33,
  "total_deposits": 420000,
  "total_withdrawals": 50000,
  "total_fines_issued": 15000,
  "total_fines_paid": 12000,
  "total_loan_repayments": 180000,
  "net_cash_flow": 562000
}
```

---

## ✅ **Next Steps**

1. **Review this document** - Confirm business logic is correct
2. **Create database migrations** - Add missing tables
3. **Implement backend APIs** - Meeting management and transaction recording
4. **Create frontend components** - Meeting UI and transaction forms
5. **Test end-to-end** - Create meeting, record transactions, verify aggregations

---

**Ready to proceed with implementation?** 🚀

