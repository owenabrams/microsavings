# 📊 Dashboard Calculations & Data Flow Guide

## Overview

This document explains how the Member Dashboard performs its calculations, what data it's based on, and how to manage the underlying data. The dashboard provides a comprehensive view of a member's financial and participation status within their savings group.

---

## 🎯 Dashboard Architecture

### **Data Flow:**
```
Database Tables → Backend API (calculations) → Frontend Components (display)
```

### **Key Endpoint:**
- **`GET /api/members/{member_id}/dashboard`** - Returns all dashboard data
- **Location:** `services/users/project/api/members.py` (lines 90-256)

---

## 📈 Dashboard Cards & Calculations

### **1. Savings Progress Card** 💰

**What it shows:**
- Total savings across all fund types
- Progress toward savings target
- Current vs. Target comparison

**Calculation Logic:**

```python
# Backend: services/users/project/api/members.py (lines 104-123)

# Step 1: Get all member_savings records for this member
member_savings = MemberSaving.query.filter_by(member_id=member_id).all()

# Step 2: For each saving type, calculate balance
for ms in member_savings:
    balance = total_deposits - total_withdrawals
    
# Step 3: Sum all balances
total_savings = sum([fund['balance'] for fund in funds])

# Step 4: Calculate progress percentage
target = member.share_balance  # From group_members table
progress_percentage = (total_savings / target * 100) if target > 0 else 0
```

**Data Sources:**
- **`member_savings`** table - Stores balances per saving type
  - `total_deposits` - Sum of all deposits
  - `total_withdrawals` - Sum of all withdrawals
  - `current_balance` - Net balance (deposits - withdrawals)
- **`group_members`** table - Stores member's target
  - `share_balance` - Used as savings target

**How to Update:**
- ✅ **Record deposits** → Increases `total_deposits` in `member_savings`
- ✅ **Record withdrawals** → Increases `total_withdrawals` in `member_savings`
- ✅ **Set target** → Update `share_balance` in `group_members`

**Status:** ⚠️ **Transaction recording endpoints NOT YET IMPLEMENTED**

---

### **2. Savings by Fund Card** 📊

**What it shows:**
- Breakdown of savings by fund type (Personal, ECD, Social, etc.)
- Balance and percentage for each fund
- Visual progress bars

**Calculation Logic:**

```python
# Backend: services/users/project/api/members.py (lines 108-122)

# For each saving type the member has:
savings_by_fund_dict = {}
for ms in member_savings:
    saving_type = SavingType.query.filter_by(id=ms.saving_type_id).first()
    balance = float(ms.total_deposits or 0) - float(ms.total_withdrawals or 0)
    
    savings_by_fund_dict[saving_type.name] = {
        'name': saving_type.name,
        'description': saving_type.description,
        'total_deposits': float(ms.total_deposits or 0),
        'total_withdrawals': float(ms.total_withdrawals or 0),
        'balance': balance
    }

# Frontend calculates percentage:
percentage = (fund.balance / total_savings) * 100
```

**Data Sources:**
- **`member_savings`** table - Balance per fund type
- **`saving_types`** table - Fund metadata (name, description)
- **`group_saving_type_settings`** table - Group-specific fund rules

**How to Manage:**
- ✅ **Add new fund types** → Use "Manage Saving Types" in Group Settings
- ✅ **View fund types** → `GET /api/groups/{group_id}/saving-types`
- ✅ **Delete fund types** → `DELETE /api/groups/{group_id}/saving-types/{type_id}`

**Status:** ✅ **Fund management fully implemented**

---

### **3. Loan Status Card** 💳

**What it shows:**
- Loan eligibility status
- Maximum loan amount
- Overall credit score
- Risk level (LOW, MEDIUM, HIGH)
- Active loans count and outstanding balance

**Calculation Logic:**

```python
# Backend: services/users/project/api/members.py (lines 125-153)

# Step 1: Get latest loan assessment
loan_assessment = LoanAssessment.query.filter_by(
    member_id=member_id
).order_by(LoanAssessment.assessment_date.desc()).first()

# Step 2: Get active loans
active_loans = db.session.execute(text("""
    SELECT principal, outstanding_balance
    FROM group_loans
    WHERE member_id = :member_id
    AND status IN ('PENDING', 'APPROVED', 'DISBURSED', 'REPAYING')
"""), {'member_id': member_id}).fetchall()

# Step 3: Calculate totals
total_loan_amount = sum([loan.principal for loan in active_loans])
total_outstanding = sum([loan.outstanding_balance for loan in active_loans])

# Step 4: Return loan status
loan_status = {
    'is_eligible': loan_assessment.is_eligible,
    'max_loan_amount': loan_assessment.max_loan_amount,
    'overall_score': loan_assessment.overall_score,
    'risk_level': loan_assessment.risk_level,
    'active_loans_count': len(active_loans),
    'total_loan_amount': total_loan_amount,
    'total_outstanding': total_outstanding
}
```

**Data Sources:**
- **`loan_assessments`** table - Eligibility and scoring
  - `total_savings` - Member's total savings at assessment
  - `attendance_rate` - Attendance % at assessment
  - `months_active` - How long member has been active
  - `savings_score` - Score based on savings (0-100)
  - `attendance_score` - Score based on attendance (0-100)
  - `participation_score` - Score based on participation (0-100)
  - `overall_score` - Weighted average of all scores
  - `is_eligible` - Boolean eligibility flag
  - `max_loan_amount` - Maximum loan they can take
  - `risk_level` - LOW, MEDIUM, HIGH
- **`group_loans`** table - Active loan records
  - `principal` - Original loan amount
  - `outstanding_balance` - Amount still owed
  - `status` - PENDING, APPROVED, DISBURSED, REPAYING, COMPLETED, DEFAULTED

**How Loan Eligibility is Calculated:**

The loan assessment algorithm (not yet implemented in API) should calculate:

```python
# Pseudo-code for loan assessment calculation:

# 1. Savings Score (40% weight)
savings_score = min(100, (total_savings / (share_value * 12)) * 100)

# 2. Attendance Score (30% weight)
attendance_score = attendance_rate  # Already a percentage

# 3. Participation Score (30% weight)
participation_score = (
    (participated_in_discussions * 0.4) +
    (contributed_to_savings * 0.4) +
    (voted_on_decisions * 0.2)
) * 100

# 4. Overall Score
overall_score = (
    savings_score * 0.40 +
    attendance_score * 0.30 +
    participation_score * 0.30
)

# 5. Eligibility Rules (from group_settings)
is_eligible = (
    months_active >= min_months_for_loan AND
    attendance_rate >= min_attendance_for_loan AND
    overall_score >= 60 AND
    no_outstanding_fines
)

# 6. Max Loan Amount
max_loan_amount = total_savings * max_loan_multiplier
```

**How to Update:**
- ⚠️ **Run loan assessment** → Endpoint NOT YET IMPLEMENTED
- ⚠️ **Apply for loan** → Endpoint NOT YET IMPLEMENTED
- ⚠️ **Record repayment** → Endpoint NOT YET IMPLEMENTED

**Status:** ⚠️ **Loan management endpoints NOT YET IMPLEMENTED**

---

### **4. Performance Comparison Card** 📊

**What it shows:**
- Member's savings vs. group average
- Member's attendance vs. group average
- Performance indicators (above/below average)

**Calculation Logic:**

```python
# Backend: services/users/project/api/members.py (lines 183-196)

# Step 1: Calculate group average savings
group_avg_savings = db.session.query(
    func.avg(GroupMember.total_contributions)
).filter(
    GroupMember.group_id == member.group_id,
    GroupMember.is_active == True
).scalar() or 0

# Step 2: Calculate group average attendance
group_avg_attendance = db.session.query(
    func.avg(GroupMember.attendance_percentage)
).filter(
    GroupMember.group_id == member.group_id,
    GroupMember.is_active == True
).scalar() or 0

# Frontend calculates differences:
savings_diff = member_savings - group_avg_savings
savings_percent_diff = ((savings_diff / group_avg_savings) * 100)
is_above_average = savings_diff >= 0
```

**Data Sources:**
- **`group_members`** table - All members in the group
  - `total_contributions` - Used for savings average
  - `attendance_percentage` - Used for attendance average
  - `is_active` - Only active members included in averages

**How to Update:**
- ✅ **Automatic** - Recalculated on every dashboard load
- Updates when member savings or attendance changes

**Status:** ✅ **Fully functional**

---

### **5. Financial Metrics Card** 💵

**What it shows:**
- Attendance rate and status (Excellent, Good, Fair, Poor)
- Total meetings and attended meetings
- Fines status (total, paid, outstanding)

**Calculation Logic:**

```python
# Backend: services/users/project/api/members.py (lines 155-181)

# ATTENDANCE CALCULATION
total_meetings = db.session.query(func.count(MeetingAttendance.id)).filter(
    MeetingAttendance.member_id == member_id
).scalar() or 0

attended_meetings = db.session.query(func.count(MeetingAttendance.id)).filter(
    MeetingAttendance.member_id == member_id,
    MeetingAttendance.is_present == True
).scalar() or 0

attendance_rate = (attended_meetings / total_meetings * 100) if total_meetings > 0 else 0

# FINES CALCULATION
total_fines = db.session.query(
    func.coalesce(func.sum(MemberFine.amount), 0)
).filter(
    MemberFine.member_id == member_id
).scalar() or 0

paid_fines = db.session.query(
    func.coalesce(func.sum(MemberFine.paid_amount), 0)
).filter(
    MemberFine.member_id == member_id,
    MemberFine.is_paid == True
).scalar() or 0

outstanding_fines = total_fines - paid_fines
```

**Data Sources:**
- **`meeting_attendance`** table - Attendance records
  - `is_present` - Boolean flag for attendance
  - `meeting_date` - Date of meeting
  - `participation_score` - Quality of participation (0-10)
- **`member_fines`** table - Fine records
  - `amount` - Total fine amount
  - `paid_amount` - Amount paid so far
  - `is_paid` - Boolean flag for full payment
  - `fine_type` - LATE_ARRIVAL, ABSENCE, MISCONDUCT, LATE_PAYMENT

**How to Update:**
- ⚠️ **Record attendance** → Endpoint NOT YET IMPLEMENTED
- ⚠️ **Issue fine** → Endpoint NOT YET IMPLEMENTED
- ⚠️ **Record fine payment** → Endpoint NOT YET IMPLEMENTED

**Status:** ⚠️ **Transaction recording endpoints NOT YET IMPLEMENTED**

---

### **6. IGA Dashboard Card** 🌱

**What it shows:**
- Income Generating Activities participation
- Active campaigns
- Total invested and returns
- ROI percentage

**Calculation Logic:**

```python
# Backend: services/users/project/api/members.py (lines 198-204)

# Currently a placeholder - returns zeros
iga_participation = {
    'active_campaigns': 0,
    'total_invested': 0,
    'total_returns': 0,
    'roi_percentage': 0
}
```

**Status:** ⚠️ **NOT YET IMPLEMENTED - Placeholder for Phase 1.5**

---

## 🗄️ Database Tables Reference

### **Core Tables:**

1. **`group_members`** - Member master data
   - Personal info, role, status
   - `share_balance` - Savings target
   - `total_contributions` - Total contributed
   - `attendance_percentage` - Cached attendance %

2. **`member_savings`** - Savings balances by fund type
   - `member_id` + `saving_type_id` (unique combination)
   - `current_balance` - Current balance
   - `total_deposits` - Lifetime deposits
   - `total_withdrawals` - Lifetime withdrawals

3. **`saving_transactions`** - Individual transactions
   - `member_saving_id` - Links to member_savings
   - `amount` - Transaction amount
   - `transaction_type` - DEPOSIT or WITHDRAWAL
   - `transaction_date` - When it occurred

4. **`meeting_attendance`** - Attendance records
   - `member_id` + `meeting_date`
   - `is_present` - Boolean attendance flag
   - `participation_score` - Quality score (0-10)

5. **`member_fines`** - Fine records
   - `member_id` - Who was fined
   - `amount` - Fine amount
   - `paid_amount` - Amount paid
   - `is_paid` - Full payment flag

6. **`group_loans`** - Loan records
   - `member_id` - Borrower
   - `principal` - Original amount
   - `outstanding_balance` - Amount owed
   - `status` - Loan status

7. **`loan_assessments`** - Eligibility assessments
   - `member_id` - Who was assessed
   - `overall_score` - Credit score
   - `is_eligible` - Eligibility flag
   - `max_loan_amount` - Max they can borrow

---

## 🔧 How to Manage Dashboard Data

### **✅ Currently Implemented:**

1. **Manage Saving Types (Fund Types)**
   - **View:** `GET /api/groups/{group_id}/saving-types`
   - **Create:** `POST /api/groups/{group_id}/saving-types`
   - **Update:** `PUT /api/groups/{group_id}/saving-types/{type_id}`
   - **Delete:** `DELETE /api/groups/{group_id}/saving-types/{type_id}`
   - **UI:** Group Settings → Activities Tab → "Manage Saving Types"

2. **View Dashboard**
   - **Endpoint:** `GET /api/members/{member_id}/dashboard`
   - **UI:** Click member name → "View Dashboard"

3. **View Member Profile**
   - **Endpoint:** `GET /api/groups/{group_id}/members/{member_id}/profile`
   - **UI:** Click member name → "View Profile"

### **⚠️ NOT YET IMPLEMENTED (Need to Create):**

#### **A. Savings Transaction Management**
```
POST /api/members/{member_id}/savings/deposit
POST /api/members/{member_id}/savings/withdraw
GET /api/members/{member_id}/savings/transactions
```

#### **B. Meeting & Attendance Management**
```
POST /api/groups/{group_id}/meetings
GET /api/groups/{group_id}/meetings
POST /api/meetings/{meeting_id}/attendance
PUT /api/meetings/{meeting_id}/attendance/{member_id}
```

#### **C. Fine Management**
```
POST /api/members/{member_id}/fines
GET /api/members/{member_id}/fines
POST /api/fines/{fine_id}/payment
```

#### **D. Loan Management**
```
POST /api/members/{member_id}/loan-assessment
POST /api/loans/apply
GET /api/loans/{loan_id}
POST /api/loans/{loan_id}/repayment
PUT /api/loans/{loan_id}/status
```

#### **E. IGA Management**
```
POST /api/iga/campaigns
POST /api/members/{member_id}/iga/invest
GET /api/members/{member_id}/iga/participation
```

---

## 📝 Summary

### **What's Working:**
✅ Dashboard displays all 6 cards correctly  
✅ Calculations are accurate based on database data  
✅ Saving types (fund types) can be managed  
✅ Group settings control fund rules  

### **What's Missing:**
⚠️ No way to record savings deposits/withdrawals  
⚠️ No way to record meeting attendance  
⚠️ No way to issue or pay fines  
⚠️ No way to apply for or manage loans  
⚠️ No loan assessment calculation endpoint  
⚠️ No IGA functionality  

### **Next Steps:**
1. Implement transaction recording endpoints (savings, fines, loans)
2. Implement meeting and attendance management
3. Implement loan assessment algorithm
4. Implement IGA functionality (Phase 1.5)
5. Create UI components for data entry

---

**Questions? Need clarification on any calculation?** Let me know which area you'd like to explore further!

