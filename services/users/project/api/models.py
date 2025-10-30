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
    minimum_contribution = Column(Numeric(10, 2))
    constitution_document_url = Column(String(255))
    registration_certificate_url = Column(String(255))
    is_registered = Column(Boolean, default=False)
    registration_number = Column(String(100))
    registration_date = Column(Date)
    created_by = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_date = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_date = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)

    # Relationships
    members = relationship('GroupMember', back_populates='group', lazy='dynamic', foreign_keys='[GroupMember.group_id]')
    meetings = relationship('Meeting', back_populates='group', lazy='dynamic')


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
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text)
    code = Column(String(20), nullable=False, unique=True)
    is_mandatory = Column(Boolean, default=False)
    minimum_amount = Column(Numeric(10, 2), default=0.00)
    maximum_amount = Column(Numeric(10, 2))
    allows_withdrawal = Column(Boolean, default=True)
    withdrawal_notice_days = Column(Integer, default=0)
    interest_rate = Column(Numeric(5, 4), default=0.0000)
    is_active = Column(Boolean, default=True)
    created_date = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)


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
    created_date = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    # Relationships
    member = relationship('GroupMember', back_populates='fines')


class GroupLoan(db.Model):
    """Group loan model."""

    __tablename__ = 'group_loans'

    id = Column(Integer, primary_key=True, autoincrement=True)
    group_id = Column(Integer, ForeignKey('savings_groups.id'), nullable=False)
    member_id = Column(Integer, ForeignKey('group_members.id'), nullable=False)
    loan_type = Column(String(100))
    amount = Column(Numeric(15, 2), nullable=False)
    interest_rate = Column(Numeric(5, 2), default=0)
    repayment_frequency = Column(String(50), default='MONTHLY')
    repayment_status = Column(String(50), default='PENDING')
    total_repaid = Column(Numeric(15, 2), default=0)
    outstanding_balance = Column(Numeric(15, 2), default=0)
    approved_by = Column(Integer, ForeignKey('users.id'))
    approved_date = Column(Date)
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

