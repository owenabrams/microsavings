"""Database models for the microfinance application."""
import datetime
import jwt
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date, Time, Numeric, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
from project import db, bcrypt
from flask import current_app


class User(db.Model):
    """User model for authentication."""
    
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(128), unique=True, nullable=False)
    email = Column(String(128), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    active = Column(Boolean, default=True, nullable=False)
    admin = Column(Boolean, default=False, nullable=False)
    role = Column(String(50), default='user')
    is_super_admin = Column(Boolean, default=False)
    created_date = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    
    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')
    
    def encode_token(self, user_id):
        """Generate auth token."""
        try:
            payload = {
                'exp': datetime.datetime.utcnow() + datetime.timedelta(
                    days=current_app.config.get('TOKEN_EXPIRATION_DAYS'),
                    seconds=current_app.config.get('TOKEN_EXPIRATION_SECONDS')
                ),
                'iat': datetime.datetime.utcnow(),
                'sub': user_id
            }
            return jwt.encode(
                payload,
                current_app.config.get('SECRET_KEY'),
                algorithm='HS256'
            )
        except Exception as e:
            return e
    
    @staticmethod
    def decode_token(auth_token):
        """Decode auth token."""
        try:
            payload = jwt.decode(
                auth_token,
                current_app.config.get('SECRET_KEY'),
                algorithms=['HS256']
            )
            return payload['sub']
        except jwt.ExpiredSignatureError:
            return 'Token expired. Please log in again.'
        except jwt.InvalidTokenError:
            return 'Invalid token. Please log in again.'


class SavingsGroup(db.Model):
    """Savings group model."""

    __tablename__ = 'savings_groups'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    group_code = Column(String(50), nullable=False, unique=True)
    formation_date = Column(Date)
    state = Column(String(50), default='ACTIVE')
    status = Column(String(50), default='ACTIVE')
    country = Column(String(100))
    region = Column(String(100))
    district = Column(String(100), nullable=False)
    parish = Column(String(100), nullable=False)
    village = Column(String(100), nullable=False)
    target_amount = Column(Numeric(15, 2), default=0)
    savings_balance = Column(Numeric(15, 2), default=0)
    loan_balance = Column(Numeric(15, 2), default=0)
    loan_fund_balance = Column(Numeric(15, 2), default=0)
    members_count = Column(Integer, default=0)
    max_members = Column(Integer, default=30)
    chair_member_id = Column(Integer, ForeignKey('group_members.id'))
    treasurer_member_id = Column(Integer, ForeignKey('group_members.id'))
    secretary_member_id = Column(Integer, ForeignKey('group_members.id'))
    meeting_frequency = Column(String(50), default='WEEKLY')
    meeting_day = Column(Integer)
    meeting_time = Column(Time)
    meeting_location = Column(String(255))
    latitude = Column(Numeric(10, 8))
    longitude = Column(Numeric(11, 8))
    minimum_contribution = Column(Numeric(10, 2))
    constitution_document_url = Column(String(255))
    constitution_version = Column(String(50))
    constitution_description = Column(Text)
    registration_certificate_url = Column(String(255))
    is_registered = Column(Boolean, default=False)
    registration_number = Column(String(100))
    registration_date = Column(Date)
    registration_authority = Column(String(255))
    certificate_number = Column(String(100))
    currency = Column(String(10), default='UGX')
    share_value = Column(Numeric(10, 2), default=5000.00)
    standard_fine_amount = Column(Numeric(10, 2), default=1000.00)
    loan_interest_rate = Column(Numeric(5, 4), default=0.0500)
    negotiated_interest_rate = Column(Numeric(5, 4))
    saving_cycle_months = Column(Integer, default=12)
    created_by = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_date = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_date = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)

    # Relationships
    members = relationship('GroupMember', back_populates='group', lazy='dynamic', foreign_keys='[GroupMember.group_id]')
    meetings = relationship('Meeting', back_populates='group', lazy='dynamic')
    settings = relationship('GroupSettings', back_populates='group', uselist=False)
    documents = relationship('GroupDocument', back_populates='group', lazy='dynamic')


class GroupMember(db.Model):
    """Group member model."""
    
    __tablename__ = 'group_members'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    group_id = Column(Integer, ForeignKey('savings_groups.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'))
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(128))
    phone_number = Column(String(20))
    id_number = Column(String(50))
    date_of_birth = Column(Date)
    gender = Column(String(10))
    occupation = Column(String(100))
    status = Column(String(50), default='ACTIVE')
    joined_date = Column(Date, default=datetime.date.today)
    is_active = Column(Boolean, default=True)
    role = Column(String(50), default='MEMBER')
    share_balance = Column(Numeric(15, 2), default=0)
    total_contributions = Column(Numeric(15, 2), default=0)
    target_amount = Column(Numeric(12, 2), default=0.00)
    attendance_percentage = Column(Numeric(5, 2), default=0)
    is_eligible_for_loans = Column(Boolean, default=False)
    created_date = Column(DateTime, default=datetime.datetime.utcnow)
    updated_date = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # Relationships
    group = relationship('SavingsGroup', back_populates='members', foreign_keys=[group_id])
    user = relationship('User', foreign_keys=[user_id])
    savings = relationship('MemberSaving', back_populates='member', lazy='dynamic')
    fines = relationship('MemberFine', back_populates='member', lazy='dynamic')
    loans = relationship('GroupLoan', back_populates='member', lazy='dynamic')
    attendance_records = relationship('MeetingAttendance', back_populates='member', lazy='dynamic')


class SavingType(db.Model):
    """Saving type model."""

    __tablename__ = 'saving_types'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    code = Column(String(20), nullable=False)
    is_mandatory = Column(Boolean, default=False)
    is_system = Column(Boolean, default=False)
    group_id = Column(Integer, ForeignKey('savings_groups.id'))
    minimum_amount = Column(Numeric(10, 2), default=0.00)
    maximum_amount = Column(Numeric(10, 2))
    allows_withdrawal = Column(Boolean, default=True)
    withdrawal_notice_days = Column(Integer, default=0)
    interest_rate = Column(Numeric(5, 4), default=0.0000)
    is_active = Column(Boolean, default=True)
    created_date = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)


class GroupSavingTypeSettings(db.Model):
    """Group-specific settings for saving types."""

    __tablename__ = 'group_saving_type_settings'

    id = Column(Integer, primary_key=True, autoincrement=True)
    group_id = Column(Integer, ForeignKey('savings_groups.id'), nullable=False)
    saving_type_id = Column(Integer, ForeignKey('saving_types.id'), nullable=False)
    is_enabled = Column(Boolean, default=True)
    minimum_amount = Column(Numeric(10, 2))
    maximum_amount = Column(Numeric(10, 2))
    allows_withdrawal = Column(Boolean)
    withdrawal_notice_days = Column(Integer)
    interest_rate = Column(Numeric(5, 4))
    display_order = Column(Integer, default=0)
    created_date = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_date = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)


class MemberSaving(db.Model):
    """Member savings model."""

    __tablename__ = 'member_savings'

    id = Column(Integer, primary_key=True, autoincrement=True)
    member_id = Column(Integer, ForeignKey('group_members.id'), nullable=False)
    saving_type_id = Column(Integer, ForeignKey('saving_types.id'), nullable=False)
    current_balance = Column(Numeric(12, 2), default=0.00, nullable=False)
    target_amount = Column(Numeric(12, 2))
    total_deposits = Column(Numeric(12, 2), default=0.00)
    total_withdrawals = Column(Numeric(12, 2), default=0.00)
    last_transaction_date = Column(Date)
    is_active = Column(Boolean, default=True)
    created_date = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_date = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)

    # Relationships
    member = relationship('GroupMember', back_populates='savings')
    saving_type = relationship('SavingType')
    transactions = relationship('SavingTransaction', back_populates='member_saving', cascade='all, delete-orphan')


class SavingTransaction(db.Model):
    """Saving transaction model."""

    __tablename__ = 'saving_transactions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    member_saving_id = Column(Integer, ForeignKey('member_savings.id', ondelete='CASCADE'), nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)
    transaction_type = Column(String(50), nullable=False)  # 'DEPOSIT' or 'WITHDRAWAL'
    transaction_date = Column(Date, default=datetime.date.today)
    description = Column(Text)
    reference_number = Column(String(100))
    is_mobile_money = Column(Boolean, default=False)
    mobile_money_reference = Column(String(100))
    mobile_money_phone = Column(String(20))
    verification_status = Column(String(50), default='PENDING')
    verified_by = Column(Integer, ForeignKey('users.id'))
    verified_date = Column(DateTime)
    meeting_id = Column(Integer, ForeignKey('meetings.id'))
    activity_id = Column(Integer)
    notes = Column(Text)
    created_date = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    # Relationships
    member_saving = relationship('MemberSaving', back_populates='transactions')
    meeting = relationship('Meeting')
    verifier = relationship('User', foreign_keys=[verified_by])


class Meeting(db.Model):
    """Meeting model."""

    __tablename__ = 'meetings'

    id = Column(Integer, primary_key=True, autoincrement=True)
    group_id = Column(Integer, ForeignKey('savings_groups.id'), nullable=False)
    meeting_number = Column(Integer, nullable=False)
    meeting_date = Column(Date, nullable=False)
    meeting_time = Column(Time)
    meeting_type = Column(String(50), default='REGULAR')
    status = Column(String(50), default='SCHEDULED')
    chairperson_id = Column(Integer, ForeignKey('group_members.id'))
    secretary_id = Column(Integer, ForeignKey('group_members.id'))
    treasurer_id = Column(Integer, ForeignKey('group_members.id'))
    total_members = Column(Integer, default=0)
    members_present = Column(Integer, default=0)
    attendance_count = Column(Integer, default=0)
    quorum_met = Column(Boolean, default=False)
    total_savings_collected = Column(Numeric(12, 2), default=0)
    total_fines_collected = Column(Numeric(12, 2), default=0)
    total_loan_repayments = Column(Numeric(12, 2), default=0)
    loans_disbursed_count = Column(Integer, default=0)
    agenda = Column(Text)
    minutes = Column(Text)
    decisions_made = Column(Text)
    action_items = Column(Text)
    location = Column(String(255))
    latitude = Column(Numeric(10, 8))
    longitude = Column(Numeric(11, 8))
    created_date = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_date = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)

    # Relationships
    group = relationship('SavingsGroup', back_populates='meetings')
    chairperson = relationship('GroupMember', foreign_keys=[chairperson_id])
    secretary = relationship('GroupMember', foreign_keys=[secretary_id])
    treasurer = relationship('GroupMember', foreign_keys=[treasurer_id])
    attendance_records = relationship('MeetingAttendance', back_populates='meeting', lazy='dynamic')


class MeetingAttendance(db.Model):
    """Meeting attendance model."""

    __tablename__ = 'meeting_attendance'

    id = Column(Integer, primary_key=True, autoincrement=True)
    group_id = Column(Integer, ForeignKey('savings_groups.id'), nullable=False)
    member_id = Column(Integer, ForeignKey('group_members.id'), nullable=False)
    meeting_date = Column(Date, nullable=False)
    meeting_number = Column(Integer)
    is_present = Column(Boolean, default=False)
    arrival_time = Column(Time)
    excuse_reason = Column(Text)
    participated_in_discussions = Column(Boolean, default=False)
    contributed_to_savings = Column(Boolean, default=False)
    voted_on_decisions = Column(Boolean, default=False)
    participation_score = Column(Numeric(3, 1), default=0.0)
    meeting_id = Column(Integer, ForeignKey('meetings.id'))
    created_date = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    # Relationships
    member = relationship('GroupMember', back_populates='attendance_records')
    meeting = relationship('Meeting', back_populates='attendance_records')


class MemberFine(db.Model):
    """Member fines model."""

    __tablename__ = 'member_fines'

    id = Column(Integer, primary_key=True, autoincrement=True)
    member_id = Column(Integer, ForeignKey('group_members.id'), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    reason = Column(Text, nullable=False)
    fine_type = Column(String(50), nullable=False)
    fine_date = Column(Date, default=datetime.date.today)
    due_date = Column(Date)
    is_paid = Column(Boolean, default=False)
    paid_amount = Column(Numeric(10, 2), default=0.00)
    payment_date = Column(Date)
    payment_method = Column(String(50))
    mobile_money_reference = Column(String(100))
    verification_status = Column(String(50), default='PENDING')
    verified_by = Column(Integer, ForeignKey('users.id'))
    verified_date = Column(DateTime)
    meeting_id = Column(Integer)
    imposed_by = Column(Integer, ForeignKey('users.id'))
    notes = Column(Text)
    created_date = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    # Relationships
    member = relationship('GroupMember', back_populates='fines')


class GroupLoan(db.Model):
    """Group loan model."""

    __tablename__ = 'group_loans'

    id = Column(Integer, primary_key=True, autoincrement=True)
    group_id = Column(Integer, ForeignKey('savings_groups.id'), nullable=False)
    member_id = Column(Integer, ForeignKey('group_members.id'), nullable=False)
    principal = Column(Numeric(15, 2), nullable=False)
    interest_rate = Column(Numeric(5, 4), nullable=False)
    term_months = Column(Integer, nullable=False)
    monthly_payment = Column(Numeric(12, 2), nullable=False)
    status = Column(String(50), default='PENDING')
    application_date = Column(Date, default=datetime.date.today)
    approval_date = Column(Date)
    disbursement_date = Column(Date)
    maturity_date = Column(Date)
    total_amount_due = Column(Numeric(15, 2), nullable=False)
    amount_paid = Column(Numeric(15, 2), default=0.00)
    outstanding_balance = Column(Numeric(15, 2), nullable=False)
    payments_made = Column(Integer, default=0)
    payments_missed = Column(Integer, default=0)
    days_overdue = Column(Integer, default=0)
    approved_by = Column(Integer, ForeignKey('users.id'))
    disbursed_by = Column(Integer, ForeignKey('users.id'))
    created_date = Column(DateTime, default=datetime.datetime.utcnow)
    updated_date = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relationships
    member = relationship('GroupMember', back_populates='loans')


class LoanAssessment(db.Model):
    """Loan assessment model."""

    __tablename__ = 'loan_assessments'

    id = Column(Integer, primary_key=True, autoincrement=True)
    member_id = Column(Integer, ForeignKey('group_members.id'), nullable=False)
    assessment_date = Column(Date, default=datetime.date.today)
    total_savings = Column(Numeric(12, 2), nullable=False)
    attendance_rate = Column(Numeric(5, 2), nullable=False)
    months_active = Column(Integer, nullable=False)
    savings_score = Column(Numeric(5, 2), default=0.00)
    attendance_score = Column(Numeric(5, 2), default=0.00)
    participation_score = Column(Numeric(5, 2), default=0.00)
    overall_score = Column(Numeric(5, 2), default=0.00)
    is_eligible = Column(Boolean, default=False)
    max_loan_amount = Column(Numeric(12, 2), default=0.00)
    recommended_term_months = Column(Integer, default=0)
    interest_rate = Column(Numeric(5, 4), default=0.0000)
    risk_level = Column(String(20), default='MEDIUM')
    risk_factors = Column(Text)
    assessed_by = Column(Integer, ForeignKey('users.id'))
    assessment_notes = Column(Text)
    created_date = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)


class GroupTransaction(db.Model):
    """Group transaction model."""

    __tablename__ = 'group_transactions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    group_id = Column(Integer, ForeignKey('savings_groups.id'), nullable=False)
    transaction_type = Column(String(50), nullable=False)
    amount = Column(Numeric(15, 2), nullable=False)
    description = Column(Text)
    reference_number = Column(String(100))
    status = Column(String(50), default='PENDING')
    created_by = Column(Integer, ForeignKey('users.id'))
    created_date = Column(DateTime, default=datetime.datetime.utcnow)


class GroupCashbook(db.Model):
    """Group cashbook model."""

    __tablename__ = 'group_cashbook'

    id = Column(Integer, primary_key=True, autoincrement=True)
    group_id = Column(Integer, ForeignKey('savings_groups.id'), nullable=False)
    entry_type = Column(String(50), nullable=False)
    amount = Column(Numeric(15, 2), nullable=False)
    balance_after = Column(Numeric(15, 2), default=0)
    description = Column(Text)
    reference_number = Column(String(100))
    status = Column(String(50), default='APPROVED')
    approved_by = Column(Integer, ForeignKey('users.id'))
    approved_date = Column(Date)
    created_date = Column(DateTime, default=datetime.datetime.utcnow)
    updated_date = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)


class MobileMoneyAccount(db.Model):
    """Mobile money account model for groups."""

    __tablename__ = 'group_mobile_money_accounts'

    id = Column(Integer, primary_key=True, autoincrement=True)
    group_id = Column(Integer, ForeignKey('savings_groups.id'), nullable=False)
    provider = Column(String(100), nullable=False)
    account_number = Column(String(50), nullable=False)
    account_holder = Column(String(255), nullable=False)
    is_primary = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    daily_limit = Column(Numeric(12, 2))
    monthly_limit = Column(Numeric(12, 2))
    created_date = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)


class SavingsGroupIGA(db.Model):
    """Income Generating Activity model."""

    __tablename__ = 'savings_group_iga'

    id = Column(Integer, primary_key=True, autoincrement=True)
    group_id = Column(Integer, ForeignKey('savings_groups.id'), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    start_date = Column(Date)
    end_date = Column(Date)
    initial_capital = Column(Numeric(15, 2), default=0)
    current_value = Column(Numeric(15, 2), default=0)
    status = Column(String(50), default='ACTIVE')
    created_by = Column(Integer, ForeignKey('users.id'))
    created_date = Column(DateTime, default=datetime.datetime.utcnow)
    updated_date = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)


class Achievement(db.Model):
    """Achievement model."""

    __tablename__ = 'achievements'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    category = Column(String(100))
    points = Column(Integer, default=0)
    badge_icon = Column(String(255))
    criteria = Column(Text)
    is_active = Column(Boolean, default=True)
    created_date = Column(DateTime, default=datetime.datetime.utcnow)


class MemberAchievement(db.Model):
    """Member achievement model."""

    __tablename__ = 'member_achievements'

    id = Column(Integer, primary_key=True, autoincrement=True)
    member_id = Column(Integer, ForeignKey('group_members.id'), nullable=False)
    achievement_id = Column(Integer, ForeignKey('achievements.id'), nullable=False)
    earned_date = Column(Date, nullable=False)
    points_earned = Column(Integer, default=0)
    created_date = Column(DateTime, default=datetime.datetime.utcnow)


class SocialPost(db.Model):
    """Social post model."""

    __tablename__ = 'social_posts'

    id = Column(Integer, primary_key=True, autoincrement=True)
    group_id = Column(Integer, ForeignKey('savings_groups.id'), nullable=False)
    author_id = Column(Integer, ForeignKey('group_members.id'), nullable=False)
    content = Column(Text, nullable=False)
    post_type = Column(String(50), default='TEXT')
    privacy_level = Column(String(50), default='GROUP')
    is_pinned = Column(Boolean, default=False)
    created_date = Column(DateTime, default=datetime.datetime.utcnow)
    updated_date = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)


class SocialComment(db.Model):
    """Social comment model."""

    __tablename__ = 'social_comments'

    id = Column(Integer, primary_key=True, autoincrement=True)
    post_id = Column(Integer, ForeignKey('social_posts.id'), nullable=False)
    author_id = Column(Integer, ForeignKey('group_members.id'), nullable=False)
    content = Column(Text, nullable=False)
    created_date = Column(DateTime, default=datetime.datetime.utcnow)
    updated_date = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)


class SocialReaction(db.Model):
    """Social reaction model."""

    __tablename__ = 'social_reactions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    post_id = Column(Integer, ForeignKey('social_posts.id'))
    comment_id = Column(Integer, ForeignKey('social_comments.id'))
    member_id = Column(Integer, ForeignKey('group_members.id'), nullable=False)
    reaction_type = Column(String(50), nullable=False)
    created_date = Column(DateTime, default=datetime.datetime.utcnow)


class GroupSettings(db.Model):
    """Group settings model for activity configurations."""

    __tablename__ = 'group_settings'

    id = Column(Integer, primary_key=True, autoincrement=True)
    group_id = Column(Integer, ForeignKey('savings_groups.id'), nullable=False, unique=True)

    # Financial Activities (enabled/disabled)
    personal_savings_enabled = Column(Boolean, default=True)
    ecd_fund_enabled = Column(Boolean, default=True)
    emergency_fund_enabled = Column(Boolean, default=False)
    social_fund_enabled = Column(Boolean, default=True)
    target_fund_enabled = Column(Boolean, default=False)

    # Attendance Tracking Activities
    attendance_tracking_enabled = Column(Boolean, default=True)

    # Loan Activities
    loan_disbursement_enabled = Column(Boolean, default=True)
    loan_repayment_enabled = Column(Boolean, default=True)

    # Other Activities
    voting_session_enabled = Column(Boolean, default=True)
    training_session_enabled = Column(Boolean, default=True)
    fine_collection_enabled = Column(Boolean, default=True)

    # Activity-specific settings
    personal_savings_minimum = Column(Numeric(10, 2))
    personal_savings_maximum = Column(Numeric(10, 2))
    ecd_fund_minimum = Column(Numeric(10, 2))
    ecd_fund_maximum = Column(Numeric(10, 2))
    social_fund_minimum = Column(Numeric(10, 2))
    social_fund_maximum = Column(Numeric(10, 2))

    # Loan settings
    max_loan_multiplier = Column(Numeric(5, 2), default=3.00)
    min_months_for_loan = Column(Integer, default=3)
    min_attendance_for_loan = Column(Numeric(5, 2), default=75.00)

    # Fine settings
    late_arrival_fine = Column(Numeric(10, 2))
    absence_fine = Column(Numeric(10, 2))
    missed_contribution_fine = Column(Numeric(10, 2))

    # Meeting settings
    quorum_percentage = Column(Numeric(5, 2), default=66.67)
    allow_proxy_voting = Column(Boolean, default=False)

    created_date = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_date = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)

    # Relationships
    group = relationship('SavingsGroup', back_populates='settings')


class GroupDocument(db.Model):
    """Group document model for attachments."""

    __tablename__ = 'group_documents'

    id = Column(Integer, primary_key=True, autoincrement=True)
    group_id = Column(Integer, ForeignKey('savings_groups.id'), nullable=False)

    # Document details
    document_title = Column(String(255), nullable=False)
    document_type = Column(String(50), nullable=False)  # CONSTITUTION, TRAINING, FINANCIAL_RECORD, REGISTRATION, OTHER
    document_category = Column(String(50))
    version = Column(String(50))
    description = Column(Text)

    # File information
    file_path = Column(String(500), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_size = Column(Integer)
    mime_type = Column(String(100))

    # Document status
    is_active = Column(Boolean, default=True)
    is_current_version = Column(Boolean, default=True)

    # Upload tracking
    uploaded_by = Column(Integer, ForeignKey('users.id'))
    upload_date = Column(DateTime, default=datetime.datetime.utcnow)

    # Approval tracking
    approved_by = Column(Integer, ForeignKey('users.id'))
    approval_date = Column(DateTime)
    approval_status = Column(String(20), default='PENDING')  # PENDING, APPROVED, REJECTED

    created_date = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_date = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)

    # Compression and storage fields
    is_compressed = Column(Boolean, default=False)
    compressed_size = Column(Integer)
    compression_ratio = Column(Numeric(5, 2))
    file_hash = Column(String(64))

    # Preview and thumbnail fields
    thumbnail_path = Column(String(500))
    preview_path = Column(String(500))
    has_preview = Column(Boolean, default=False)

    # Versioning fields
    parent_document_id = Column(Integer, ForeignKey('group_documents.id'))
    replaced_by_id = Column(Integer, ForeignKey('group_documents.id'))
    version_number = Column(Integer, default=1)

    # Metadata fields
    file_category = Column(String(50))
    original_filename = Column(String(255))
    download_count = Column(Integer, default=0)
    last_accessed = Column(DateTime)

    # Soft delete
    is_deleted = Column(Boolean, default=False)
    deleted_date = Column(DateTime)
    deleted_by = Column(Integer, ForeignKey('users.id'))

    # Relationships
    group = relationship('SavingsGroup', back_populates='documents')
    uploader = relationship('User', foreign_keys=[uploaded_by])
    approver = relationship('User', foreign_keys=[approved_by])
    deleter = relationship('User', foreign_keys=[deleted_by])
    parent_document = relationship('GroupDocument', remote_side=[id], foreign_keys=[parent_document_id])
    replaced_by = relationship('GroupDocument', remote_side=[id], foreign_keys=[replaced_by_id])


class DocumentTemplate(db.Model):
    """Document template model."""

    __tablename__ = 'document_templates'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    template_type = Column(String(100))
    content = Column(Text)
    is_active = Column(Boolean, default=True)
    created_by = Column(Integer, ForeignKey('users.id'))
    created_date = Column(DateTime, default=datetime.datetime.utcnow)
    updated_date = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)


class TrainingRecord(db.Model):
    """Training session record model."""

    __tablename__ = 'training_records'

    id = Column(Integer, primary_key=True, autoincrement=True)
    meeting_id = Column(Integer, ForeignKey('meetings.id'), nullable=False)
    training_topic = Column(String(255), nullable=False)
    training_description = Column(Text)
    trainer_name = Column(String(255))
    trainer_type = Column(String(50))  # INTERNAL, EXTERNAL, MEMBER
    duration_minutes = Column(Integer)
    materials_provided = Column(Text)
    total_attendees = Column(Integer, default=0)
    created_date = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_date = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)

    # Relationships
    meeting = relationship('Meeting')
    attendance = relationship('TrainingAttendance', back_populates='training', lazy='dynamic')


class TrainingAttendance(db.Model):
    """Training attendance model."""

    __tablename__ = 'training_attendance'

    id = Column(Integer, primary_key=True, autoincrement=True)
    training_id = Column(Integer, ForeignKey('training_records.id'), nullable=False)
    member_id = Column(Integer, ForeignKey('group_members.id'), nullable=False)
    attended = Column(Boolean, default=False)
    notes = Column(Text)
    created_date = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    # Relationships
    training = relationship('TrainingRecord', back_populates='attendance')
    member = relationship('GroupMember')


class VotingRecord(db.Model):
    """Voting session record model."""

    __tablename__ = 'voting_records'

    id = Column(Integer, primary_key=True, autoincrement=True)
    meeting_id = Column(Integer, ForeignKey('meetings.id'), nullable=False)
    vote_topic = Column(String(255), nullable=False)
    vote_description = Column(Text)
    vote_type = Column(String(50), default='SIMPLE_MAJORITY')  # SIMPLE_MAJORITY, TWO_THIRDS, UNANIMOUS
    result = Column(String(50))  # PASSED, FAILED, DEFERRED
    yes_count = Column(Integer, default=0)
    no_count = Column(Integer, default=0)
    abstain_count = Column(Integer, default=0)
    absent_count = Column(Integer, default=0)
    proposed_by = Column(Integer, ForeignKey('group_members.id'))
    created_date = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_date = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)

    # Relationships
    meeting = relationship('Meeting')
    proposer = relationship('GroupMember', foreign_keys=[proposed_by])
    votes = relationship('MemberVote', back_populates='voting_record', lazy='dynamic')


class MemberVote(db.Model):
    """Member vote model."""

    __tablename__ = 'member_votes'

    id = Column(Integer, primary_key=True, autoincrement=True)
    voting_record_id = Column(Integer, ForeignKey('voting_records.id'), nullable=False)
    member_id = Column(Integer, ForeignKey('group_members.id'), nullable=False)
    vote_cast = Column(String(20), nullable=False)  # YES, NO, ABSTAIN, ABSENT
    notes = Column(Text)
    created_date = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    # Relationships
    voting_record = relationship('VotingRecord', back_populates='votes')
    member = relationship('GroupMember')


class LoanRepayment(db.Model):
    """Loan repayment transaction model."""

    __tablename__ = 'loan_repayments'

    id = Column(Integer, primary_key=True, autoincrement=True)
    loan_id = Column(Integer, ForeignKey('group_loans.id'), nullable=False)
    meeting_id = Column(Integer, ForeignKey('meetings.id'))
    member_id = Column(Integer, ForeignKey('group_members.id'), nullable=False)
    repayment_amount = Column(Numeric(12, 2), nullable=False)
    principal_amount = Column(Numeric(12, 2), nullable=False)
    interest_amount = Column(Numeric(12, 2), nullable=False)
    outstanding_balance = Column(Numeric(12, 2), nullable=False)
    repayment_date = Column(Date, nullable=False)
    payment_method = Column(String(50), default='CASH')  # CASH, MOBILE_MONEY
    mobile_money_reference = Column(String(100))
    mobile_money_phone = Column(String(20))
    recorded_by = Column(Integer, ForeignKey('users.id'))
    notes = Column(Text)
    created_date = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_date = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)

    # Relationships
    loan = relationship('GroupLoan')
    meeting = relationship('Meeting')
    member = relationship('GroupMember')


class MeetingSummary(db.Model):
    """Meeting summary model."""

    __tablename__ = 'meeting_summaries'

    id = Column(Integer, primary_key=True, autoincrement=True)
    meeting_id = Column(Integer, ForeignKey('meetings.id'), nullable=False, unique=True)

    # Attendance summary
    total_members = Column(Integer, default=0)
    members_present = Column(Integer, default=0)
    members_absent = Column(Integer, default=0)
    attendance_rate = Column(Numeric(5, 2), default=0.00)

    # Savings summary
    total_deposits = Column(Numeric(12, 2), default=0.00)
    total_withdrawals = Column(Numeric(12, 2), default=0.00)
    net_savings = Column(Numeric(12, 2), default=0.00)

    # Fines summary
    total_fines_issued = Column(Numeric(12, 2), default=0.00)
    total_fines_paid = Column(Numeric(12, 2), default=0.00)
    outstanding_fines = Column(Numeric(12, 2), default=0.00)

    # Loan summary
    total_loans_disbursed = Column(Numeric(12, 2), default=0.00)
    loans_disbursed_count = Column(Integer, default=0)
    total_loan_repayments = Column(Numeric(12, 2), default=0.00)
    loan_repayments_count = Column(Integer, default=0)

    # Training summary
    trainings_held = Column(Integer, default=0)
    training_attendance_count = Column(Integer, default=0)
    training_participation_rate = Column(Numeric(5, 2), default=0.00)

    # Voting summary
    voting_sessions_held = Column(Integer, default=0)
    votes_cast_count = Column(Integer, default=0)
    voting_participation_rate = Column(Numeric(5, 2), default=0.00)

    # Financial summary
    net_cash_flow = Column(Numeric(12, 2), default=0.00)

    created_date = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_date = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)

    # Relationships
    meeting = relationship('Meeting')


class MeetingActivity(db.Model):
    """Meeting activity model for tracking activities during meetings."""

    __tablename__ = 'meeting_activities'

    id = Column(Integer, primary_key=True, autoincrement=True)
    meeting_id = Column(Integer, ForeignKey('meetings.id', ondelete='CASCADE'), nullable=False)
    activity_type = Column(String(50), nullable=False)  # SAVINGS, FINE, LOAN_REPAYMENT, TRAINING, VOTING, etc.
    activity_name = Column(String(255), nullable=False)
    description = Column(Text)
    status = Column(String(50), default='PENDING')  # PENDING, IN_PROGRESS, COMPLETED, CANCELLED
    start_time = Column(Time)
    end_time = Column(Time)
    duration_minutes = Column(Integer)
    total_amount = Column(Numeric(12, 2), default=0.00)
    participants_count = Column(Integer, default=0)
    conducted_by = Column(Integer, ForeignKey('group_members.id'))
    notes = Column(Text)
    created_date = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_date = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)

    # Relationships
    meeting = relationship('Meeting')
    conductor = relationship('GroupMember', foreign_keys=[conducted_by])
    documents = relationship('ActivityDocument', back_populates='activity', lazy='dynamic', cascade='all, delete-orphan')
    participations = relationship('MemberActivityParticipation', back_populates='activity', lazy='dynamic', cascade='all, delete-orphan')


class ActivityDocument(db.Model):
    """Activity document model for file attachments to meeting activities."""

    __tablename__ = 'activity_documents'

    id = Column(Integer, primary_key=True, autoincrement=True)
    activity_id = Column(Integer, ForeignKey('meeting_activities.id', ondelete='CASCADE'), nullable=False)
    document_name = Column(String(255), nullable=False)
    document_type = Column(String(50), nullable=False)  # RECEIPT, INVOICE, PHOTO, REPORT, OTHER
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=False)
    mime_type = Column(String(100))
    description = Column(Text)
    is_proof_document = Column(Boolean, default=False)
    document_category = Column(String(50))  # FINANCIAL, TRAINING, VOTING, GENERAL
    uploaded_by = Column(Integer, ForeignKey('users.id'))
    upload_date = Column(DateTime, default=datetime.datetime.utcnow)
    is_public = Column(Boolean, default=False)
    access_level = Column(String(50), default='GROUP')  # GROUP, ADMIN, PUBLIC
    created_date = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    # Compression and storage fields
    is_compressed = Column(Boolean, default=False)
    compressed_size = Column(Integer)
    compression_ratio = Column(Numeric(5, 2))  # Percentage
    file_hash = Column(String(64))  # SHA256 hash for duplicate detection

    # Preview and thumbnail fields
    thumbnail_path = Column(String(500))
    preview_path = Column(String(500))
    has_preview = Column(Boolean, default=False)

    # Versioning fields
    version = Column(Integer, default=1)
    parent_document_id = Column(Integer, ForeignKey('activity_documents.id'))
    is_current_version = Column(Boolean, default=True)
    replaced_by_id = Column(Integer, ForeignKey('activity_documents.id'))

    # Metadata fields
    file_category = Column(String(50))  # documents, images, videos, archives, audio
    original_filename = Column(String(255))
    download_count = Column(Integer, default=0)
    last_accessed = Column(DateTime)

    # Soft delete
    is_deleted = Column(Boolean, default=False)
    deleted_date = Column(DateTime)
    deleted_by = Column(Integer, ForeignKey('users.id'))

    # Relationships
    activity = relationship('MeetingActivity', back_populates='documents')
    uploader = relationship('User', foreign_keys=[uploaded_by])
    deleter = relationship('User', foreign_keys=[deleted_by])
    parent_document = relationship('ActivityDocument', remote_side=[id], foreign_keys=[parent_document_id])
    replaced_by = relationship('ActivityDocument', remote_side=[id], foreign_keys=[replaced_by_id])


class MemberActivityParticipation(db.Model):
    """Member activity participation model for tracking member participation in activities."""

    __tablename__ = 'member_activity_participation'

    id = Column(Integer, primary_key=True, autoincrement=True)
    activity_id = Column(Integer, ForeignKey('meeting_activities.id', ondelete='CASCADE'), nullable=False)
    member_id = Column(Integer, ForeignKey('group_members.id'), nullable=False)
    is_present = Column(Boolean, default=False)
    participation_type = Column(String(50))
    amount_contributed = Column(Numeric(12, 2), default=0.00)
    fund_type = Column(String(50))
    payment_method = Column(String(50), default='CASH')
    mobile_money_reference = Column(String(100))
    mobile_money_phone = Column(String(20))
    verification_status = Column(String(50), default='PENDING')
    verified_by = Column(Integer, ForeignKey('users.id'))
    verified_date = Column(DateTime)
    participation_score = Column(Numeric(3, 1), default=0.0)
    contributed_to_discussions = Column(Boolean, default=False)
    voted_on_decisions = Column(Boolean, default=False)
    notes = Column(Text)
    excuse_reason = Column(Text)
    created_date = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    # Relationships
    activity = relationship('MeetingActivity', back_populates='participations')
    member = relationship('GroupMember')
    verifier = relationship('User', foreign_keys=[verified_by])


class TransactionDocument(db.Model):
    """
    Polymorphic document model for attaching files to any transaction type.

    This model uses a polymorphic association pattern to support document attachments
    for multiple entity types through a single table. The entity_type and entity_id
    fields work together to reference any transaction type.

    Supported entity types:
    - 'training': Training sessions (training_records table)
    - 'voting': Voting sessions (voting_records table)
    - 'loan_repayment': Loan repayment transactions (loan_repayments table)
    - 'fine': Member fines (member_fines table)
    - 'savings': Savings transactions (saving_transactions table)
    - 'meeting': Meeting-level documents (meetings table)
    - 'member': Member documents (group_members table)
    - 'group': Group documents (savings_groups table)

    Features:
    - File compression for large files
    - Thumbnail and preview generation
    - File hash for deduplication
    - Soft delete support
    - Access control levels
    - Audit trail (uploaded_by, upload_date)

    Usage Example:
        # Attach document to training
        doc = TransactionDocument(
            entity_type='training',
            entity_id=training.id,
            document_name='certificate.pdf',
            original_filename='certificate.pdf',
            document_type='CERTIFICATE',
            file_path='/path/to/file',
            file_size=12345,
            uploaded_by=user_id
        )
        db.session.add(doc)
        db.session.commit()

        # Get all documents for a training
        docs = TransactionDocument.get_for_entity('training', training_id)

        # Count documents
        count = TransactionDocument.count_for_entity('training', training_id)
    """

    __tablename__ = 'transaction_documents'

    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Polymorphic relationship fields
    entity_type = Column(String(50), nullable=False, index=True)
    entity_id = Column(Integer, nullable=False, index=True)

    # Document metadata
    document_name = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    document_type = Column(String(50), nullable=False)  # RECEIPT, INVOICE, PHOTO, REPORT, CERTIFICATE, OTHER
    description = Column(Text)
    document_category = Column(String(50))  # FINANCIAL, TRAINING, VOTING, LEGAL, GENERAL

    # File information
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=False)
    mime_type = Column(String(100))
    file_hash = Column(String(64))  # SHA-256 hash for deduplication

    # Compression features
    is_compressed = Column(Boolean, default=False)
    compressed_size = Column(Integer)
    compression_ratio = Column(Numeric(5, 2))

    # Preview features
    thumbnail_path = Column(String(500))
    preview_path = Column(String(500))
    has_preview = Column(Boolean, default=False)

    # Access control
    is_public = Column(Boolean, default=False)
    access_level = Column(String(50), default='GROUP')  # GROUP, ADMIN, PUBLIC
    is_proof_document = Column(Boolean, default=False)

    # Audit fields
    uploaded_by = Column(Integer, ForeignKey('users.id'))
    upload_date = Column(DateTime, default=datetime.datetime.utcnow)
    created_date = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_date = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)

    # Soft delete
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime)
    deleted_by = Column(Integer, ForeignKey('users.id'))

    # Relationships
    uploader = relationship('User', foreign_keys=[uploaded_by])
    deleter = relationship('User', foreign_keys=[deleted_by])

    def to_dict(self):
        """
        Convert to dictionary for API responses.

        Returns:
            dict: Dictionary representation of the document
        """
        return {
            'id': self.id,
            'entity_type': self.entity_type,
            'entity_id': self.entity_id,
            'document_name': self.document_name,
            'original_filename': self.original_filename,
            'document_type': self.document_type,
            'description': self.description,
            'document_category': self.document_category,
            'file_size': self.file_size,
            'compressed_size': self.compressed_size,
            'is_compressed': self.is_compressed,
            'compression_ratio': float(self.compression_ratio) if self.compression_ratio else 0,
            'mime_type': self.mime_type,
            'has_preview': self.has_preview,
            'thumbnail_path': self.thumbnail_path,
            'preview_path': self.preview_path,
            'is_public': self.is_public,
            'access_level': self.access_level,
            'is_proof_document': self.is_proof_document,
            'uploaded_by': self.uploaded_by,
            'upload_date': self.upload_date.isoformat() if self.upload_date else None,
            'created_date': self.created_date.isoformat() if self.created_date else None,
            'is_deleted': self.is_deleted
        }

    @staticmethod
    def get_for_entity(entity_type, entity_id):
        """
        Get all non-deleted documents for a specific entity.

        Args:
            entity_type (str): Type of entity ('training', 'voting', etc.)
            entity_id (int): ID of the entity

        Returns:
            list: List of TransactionDocument objects ordered by upload date (newest first)
        """
        return TransactionDocument.query.filter_by(
            entity_type=entity_type,
            entity_id=entity_id,
            is_deleted=False
        ).order_by(TransactionDocument.upload_date.desc()).all()

    @staticmethod
    def get_entity_types():
        """
        Get list of supported entity types.

        Returns:
            list: List of valid entity type strings
        """
        return [
            'training',
            'voting',
            'loan_repayment',
            'fine',
            'savings',
            'meeting',
            'member',
            'group'
        ]

    @staticmethod
    def count_for_entity(entity_type, entity_id):
        """
        Get count of non-deleted documents for an entity.

        Args:
            entity_type (str): Type of entity
            entity_id (int): ID of the entity

        Returns:
            int: Number of documents
        """
        return TransactionDocument.query.filter_by(
            entity_type=entity_type,
            entity_id=entity_id,
            is_deleted=False
        ).count()

    @staticmethod
    def validate_entity_type(entity_type):
        """
        Validate if entity type is supported.

        Args:
            entity_type (str): Entity type to validate

        Returns:
            bool: True if valid, False otherwise
        """
        return entity_type in TransactionDocument.get_entity_types()

    def soft_delete(self, deleted_by_user_id):
        """
        Soft delete the document.

        Args:
            deleted_by_user_id (int): ID of user performing the deletion
        """
        self.is_deleted = True
        self.deleted_at = datetime.datetime.utcnow()
        self.deleted_by = deleted_by_user_id

    def __repr__(self):
        return f'<TransactionDocument {self.id}: {self.document_name} for {self.entity_type}#{self.entity_id}>'

