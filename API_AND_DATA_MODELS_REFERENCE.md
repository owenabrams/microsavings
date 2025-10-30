# API AND DATA MODELS REFERENCE
## Complete Technical Reference for All Endpoints and Models

---

## AUTHENTICATION API

### POST /api/auth/login
**Purpose:** Authenticate user and receive JWT token

**Request:**
```json
{
  "email": "admin@savingsgroup.com",
  "password": "admin123"
}
```

**Response (200):**
```json
{
  "status": "success",
  "auth_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@savingsgroup.com",
    "role": "super_admin",
    "is_super_admin": true
  }
}
```

**Response (401):**
```json
{
  "status": "error",
  "message": "Invalid credentials"
}
```

### GET /api/auth/status
**Purpose:** Check authentication status

**Headers:** `Authorization: Bearer <token>`

**Response (200):**
```json
{
  "status": "success",
  "authenticated": true,
  "user_id": 1
}
```

---

## SAVINGS GROUPS API

### GET /api/savings-groups
**Purpose:** List all savings groups

**Headers:** `Authorization: Bearer <token>`

**Query Parameters:**
- `limit` (optional): Number of results (default: 50)
- `offset` (optional): Pagination offset (default: 0)

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "groups": [
      {
        "id": 1,
        "name": "Kigali Savings Group",
        "description": "Main savings group in Kigali",
        "status": "ACTIVE",
        "country": "Rwanda",
        "district": "Kigali",
        "parish": "Kigali Central",
        "village": "Downtown",
        "total_members": 18,
        "total_savings": "2500000.00",
        "created_date": "2024-01-01T00:00:00"
      }
    ],
    "count": 3,
    "total": 3
  }
}
```

### GET /api/savings-groups/{id}
**Purpose:** Get specific group details

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "id": 1,
    "name": "Kigali Savings Group",
    "members": [
      {
        "id": 1,
        "first_name": "John",
        "last_name": "Doe",
        "email": "john@example.com",
        "phone_number": "+250788000001",
        "role": "FOUNDER",
        "status": "ACTIVE",
        "share_balance": "150000.00",
        "total_contributions": "450000.00",
        "attendance_percentage": 95.5,
        "is_eligible_for_loans": true
      }
    ],
    "financial_summary": {
      "total_savings": "2500000.00",
      "total_loans": "1200000.00",
      "total_fines": "50000.00",
      "average_attendance": 87.3
    }
  }
}
```

### POST /api/savings-groups
**Purpose:** Create new savings group

**Request:**
```json
{
  "name": "New Savings Group",
  "description": "Description",
  "country": "Rwanda",
  "district": "Kigali",
  "parish": "Kigali Central",
  "village": "Downtown"
}
```

**Response (201):**
```json
{
  "status": "success",
  "data": {
    "id": 4,
    "name": "New Savings Group",
    "status": "ACTIVE"
  }
}
```

---

## MEMBERS API

### GET /api/savings-groups/{group_id}/members
**Purpose:** List group members

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "members": [
      {
        "id": 1,
        "group_id": 1,
        "first_name": "John",
        "last_name": "Doe",
        "email": "john@example.com",
        "phone_number": "+250788000001",
        "gender": "M",
        "occupation": "Farmer",
        "id_number": "1234567890",
        "date_of_birth": "1985-05-15",
        "role": "FOUNDER",
        "status": "ACTIVE",
        "joined_date": "2024-01-01",
        "share_balance": "150000.00",
        "total_contributions": "450000.00",
        "attendance_percentage": 95.5,
        "is_eligible_for_loans": true,
        "created_date": "2024-01-01T00:00:00"
      }
    ],
    "count": 18
  }
}
```

### POST /api/savings-groups/{group_id}/members
**Purpose:** Add member to group

**Request:**
```json
{
  "first_name": "Jane",
  "last_name": "Smith",
  "email": "jane@example.com",
  "phone_number": "+250788000002",
  "gender": "F",
  "occupation": "Teacher",
  "id_number": "0987654321",
  "date_of_birth": "1990-03-20"
}
```

**Response (201):**
```json
{
  "status": "success",
  "data": {
    "id": 54,
    "group_id": 1,
    "first_name": "Jane",
    "last_name": "Smith",
    "status": "ACTIVE"
  }
}
```

### GET /api/members/{id}
**Purpose:** Get member details with financial summary

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "id": 1,
    "first_name": "John",
    "last_name": "Doe",
    "group_id": 1,
    "financial_summary": {
      "total_savings": "450000.00",
      "personal_savings": "150000.00",
      "ecd_fund": "200000.00",
      "social_fund": "100000.00",
      "total_loans": "300000.00",
      "outstanding_balance": "150000.00",
      "total_fines": "10000.00",
      "paid_fines": "5000.00"
    },
    "attendance": {
      "total_meetings": 60,
      "attended": 57,
      "percentage": 95.0
    },
    "achievements": {
      "total_achievements": 12,
      "total_points": 450,
      "total_badges": 5,
      "rank_in_group": 2,
      "rank_in_system": 15
    }
  }
}
```

---

## MEETINGS API

### GET /api/meetings
**Purpose:** List all meetings

**Query Parameters:**
- `group_id` (optional): Filter by group
- `status` (optional): SCHEDULED, COMPLETED, CANCELLED
- `limit` (optional): Number of results

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "meetings": [
      {
        "id": 1,
        "group_id": 1,
        "meeting_number": 1,
        "meeting_date": "2024-01-01",
        "meeting_time": "14:00:00",
        "meeting_type": "REGULAR",
        "location": "Community Center",
        "status": "COMPLETED",
        "total_members": 18,
        "members_present": 17,
        "attendance_count": 17,
        "quorum_met": true,
        "total_savings_collected": "50000.00",
        "total_fines_collected": "5000.00",
        "total_loan_repayments": "100000.00",
        "agenda": "Monthly savings review",
        "minutes": "Meeting minutes here"
      }
    ],
    "count": 60
  }
}
```

### POST /api/meetings
**Purpose:** Create new meeting

**Request:**
```json
{
  "group_id": 1,
  "meeting_date": "2024-11-15",
  "meeting_time": "14:00:00",
  "meeting_type": "REGULAR",
  "location": "Community Center",
  "agenda": "Monthly savings review"
}
```

**Response (201):**
```json
{
  "status": "success",
  "data": {
    "id": 61,
    "group_id": 1,
    "meeting_number": 61,
    "status": "SCHEDULED"
  }
}
```

### POST /api/meetings/{id}/attendance
**Purpose:** Record member attendance

**Request:**
```json
{
  "member_id": 1,
  "attended": true,
  "contributed_to_meeting": true,
  "meeting_notes": "Regular attendance"
}
```

**Response (201):**
```json
{
  "status": "success",
  "data": {
    "id": 1,
    "meeting_id": 1,
    "member_id": 1,
    "attended": true
  }
}
```

---

## LOANS API

### GET /api/loans
**Purpose:** List all loans

**Query Parameters:**
- `group_id` (optional): Filter by group
- `status` (optional): PENDING, APPROVED, DISBURSED, REPAYING, COMPLETED, DEFAULTED

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "loans": [
      {
        "id": 1,
        "group_id": 1,
        "member_id": 1,
        "loan_type": "PERSONAL",
        "amount": "300000.00",
        "interest_rate": 15.0,
        "repayment_frequency": "MONTHLY",
        "repayment_status": "ACTIVE",
        "total_repaid": "150000.00",
        "outstanding_balance": "150000.00",
        "approved_date": "2024-02-01",
        "created_date": "2024-01-15"
      }
    ],
    "count": 15
  }
}
```

### GET /api/loans/{id}/assessment
**Purpose:** Get loan eligibility assessment

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "member_id": 1,
    "is_eligible": true,
    "score": 85,
    "assessment_date": "2024-10-29",
    "reasons": [
      "Attendance above 80%",
      "Savings balance sufficient",
      "No outstanding fines"
    ],
    "recommendations": [
      "Eligible for up to 500,000 RWF",
      "Recommended interest rate: 15%",
      "Suggested repayment period: 12 months"
    ]
  }
}
```

### POST /api/loans
**Purpose:** Create new loan

**Request:**
```json
{
  "group_id": 1,
  "member_id": 1,
  "loan_type": "PERSONAL",
  "amount": "400000.00",
  "interest_rate": 15.0,
  "repayment_frequency": "MONTHLY",
  "repayment_period_months": 12
}
```

**Response (201):**
```json
{
  "status": "success",
  "data": {
    "id": 16,
    "group_id": 1,
    "member_id": 1,
    "amount": "400000.00",
    "status": "PENDING"
  }
}
```

---

## ACHIEVEMENTS API

### GET /api/achievements
**Purpose:** List all achievements

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "achievements": [
      {
        "id": 1,
        "name": "First Savings",
        "description": "Save your first 10,000 RWF",
        "category": "FINANCIAL",
        "criteria_type": "THRESHOLD",
        "criteria_value": "10000.00",
        "points": 10,
        "icon_url": "/icons/first-savings.png"
      }
    ],
    "count": 25
  }
}
```

### GET /api/achievements/leaderboard
**Purpose:** Get achievement leaderboard

**Query Parameters:**
- `limit` (optional): Number of results (default: 50)

**Response (200):**
```json
{
  "status": "success",
  "data": [
    {
      "member_id": 1,
      "member_name": "John Doe",
      "group_id": 1,
      "total_achievements": 12,
      "total_points": 450,
      "total_badges": 5,
      "rank_in_group": 1,
      "rank_in_system": 15
    }
  ],
  "count": 50
}
```

### GET /api/members/{id}/achievements
**Purpose:** Get member's achievements

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "member_id": 1,
    "achievements": [
      {
        "id": 1,
        "achievement_id": 1,
        "name": "First Savings",
        "earned_date": "2024-01-15",
        "points_earned": 10
      }
    ],
    "badges": [
      {
        "id": 1,
        "badge_id": 1,
        "name": "Gold Member",
        "earned_date": "2024-06-01"
      }
    ],
    "total_points": 450
  }
}
```

---

## ANALYTICS API

### GET /api/analytics/groups/{id}
**Purpose:** Get group analytics

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "group_id": 1,
    "total_members": 18,
    "active_members": 17,
    "total_savings": "2500000.00",
    "average_savings_per_member": "138888.89",
    "total_loans": "1200000.00",
    "total_loan_repayments": "600000.00",
    "average_attendance": 87.3,
    "total_meetings": 60,
    "completed_meetings": 60,
    "total_fines": "50000.00",
    "collected_fines": "45000.00"
  }
}
```

### GET /api/analytics/members/{id}
**Purpose:** Get member analytics

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "member_id": 1,
    "savings_trend": [
      {"month": "2024-01", "balance": "50000.00"},
      {"month": "2024-02", "balance": "100000.00"}
    ],
    "attendance_trend": [
      {"month": "2024-01", "attended": 1, "total": 1, "percentage": 100}
    ],
    "loan_performance": {
      "total_loans": 2,
      "active_loans": 1,
      "completed_loans": 1,
      "default_rate": 0
    }
  }
}
```

---

## MOBILE MONEY API

### POST /api/mobile-money/accounts
**Purpose:** Link mobile money account

**Request:**
```json
{
  "member_id": 1,
  "provider": "MTN",
  "phone_number": "+250788000001"
}
```

**Response (201):**
```json
{
  "status": "success",
  "data": {
    "id": 1,
    "member_id": 1,
    "provider": "MTN",
    "phone_number": "+250788000001",
    "account_status": "ACTIVE"
  }
}
```

### POST /api/mobile-money/transactions
**Purpose:** Record mobile money transaction

**Request:**
```json
{
  "account_id": 1,
  "transaction_id": "MTN123456",
  "amount": "50000.00",
  "transaction_type": "DEPOSIT"
}
```

**Response (201):**
```json
{
  "status": "success",
  "data": {
    "id": 1,
    "account_id": 1,
    "transaction_id": "MTN123456",
    "amount": "50000.00",
    "status": "PENDING"
  }
}
```

---

## NOTIFICATIONS API

### GET /api/notifications
**Purpose:** Get user notifications

**Query Parameters:**
- `read` (optional): true/false to filter by read status
- `limit` (optional): Number of results

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "notifications": [
      {
        "id": 1,
        "notification_type": "LOAN_APPROVED",
        "content": "Your loan has been approved",
        "read": false,
        "created_date": "2024-10-29T10:00:00"
      }
    ],
    "count": 5,
    "unread_count": 2
  }
}
```

### PUT /api/notifications/{id}
**Purpose:** Mark notification as read

**Request:**
```json
{
  "read": true
}
```

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "id": 1,
    "read": true
  }
}
```

---

## ERROR RESPONSES

### Standard Error Format
```json
{
  "status": "error",
  "message": "Error description",
  "code": "ERROR_CODE"
}
```

### Common HTTP Status Codes
- `200 OK` - Successful request
- `201 Created` - Resource created
- `400 Bad Request` - Invalid input
- `401 Unauthorized` - Authentication required
- `403 Forbidden` - Permission denied
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

---

**End of API Reference**

