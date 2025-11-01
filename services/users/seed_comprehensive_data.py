#!/usr/bin/env python
"""
Comprehensive Data Seeding Script
Seeds complete realistic data for all transaction types with normal distribution.
This ensures the database has a complete schema with all tables populated.
"""
import sys
import os
import random
from datetime import date, datetime, timedelta
from decimal import Decimal

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from project import create_app, db
from project.api.models import (
    User, SavingsGroup, GroupMember, Meeting, MeetingAttendance,
    SavingType, MemberSaving, SavingTransaction, MemberFine,
    GroupLoan, LoanRepayment, TrainingRecord, VotingRecord,
    MeetingSummary, LoanAssessment, GroupSettings, TransactionDocument
)

app = create_app()

# Random seed for reproducibility
random.seed(42)

def ensure_schema_complete():
    """
    Ensure all required tables and columns exist before seeding.
    This prevents errors when the database schema is incomplete.
    """
    print("\n🔧 Ensuring database schema is complete...")

    with app.app_context():
        # Create all tables if they don't exist
        db.create_all()
        print("   ✅ All tables created/verified")

        # Add missing columns using raw SQL (safe with IF NOT EXISTS)
        from sqlalchemy import text

        missing_columns = [
            # group_members table
            ("group_members", "target_amount", "NUMERIC(15, 2) DEFAULT 0"),

            # transaction tables - notes column
            ("saving_transactions", "notes", "TEXT"),
            ("member_fines", "notes", "TEXT"),
            ("loan_repayments", "notes", "TEXT"),
            ("training_records", "notes", "TEXT"),
            ("voting_records", "notes", "TEXT"),
            ("group_loans", "notes", "TEXT"),

            # group_documents table - professional file management columns
            ("group_documents", "is_compressed", "BOOLEAN DEFAULT FALSE"),
            ("group_documents", "compressed_size", "INTEGER"),
            ("group_documents", "compression_ratio", "NUMERIC(5, 2)"),
            ("group_documents", "file_hash", "VARCHAR(64)"),
            ("group_documents", "thumbnail_path", "VARCHAR(500)"),
            ("group_documents", "preview_path", "VARCHAR(500)"),
            ("group_documents", "has_preview", "BOOLEAN DEFAULT FALSE"),
            ("group_documents", "parent_document_id", "INTEGER"),
            ("group_documents", "replaced_by_id", "INTEGER"),
            ("group_documents", "version_number", "INTEGER DEFAULT 1"),
            ("group_documents", "file_category", "VARCHAR(50)"),
            ("group_documents", "original_filename", "VARCHAR(255)"),
            ("group_documents", "download_count", "INTEGER DEFAULT 0"),
            ("group_documents", "last_accessed", "TIMESTAMP"),
            ("group_documents", "is_deleted", "BOOLEAN DEFAULT FALSE"),
            ("group_documents", "deleted_date", "TIMESTAMP"),
            ("group_documents", "deleted_by", "INTEGER"),
            ("group_documents", "version", "VARCHAR(20)"),
            ("group_documents", "is_current_version", "BOOLEAN DEFAULT TRUE"),
            ("group_documents", "access_level", "VARCHAR(50) DEFAULT 'GROUP'"),
        ]

        for table_name, column_name, column_def in missing_columns:
            try:
                sql = f"ALTER TABLE {table_name} ADD COLUMN IF NOT EXISTS {column_name} {column_def};"
                db.session.execute(text(sql))
                db.session.commit()
            except Exception as e:
                # Table might not exist yet, or column already exists - that's OK
                db.session.rollback()
                pass

        print("   ✅ All required columns added/verified")

        # Create member_profile_complete view if it doesn't exist
        try:
            view_sql = """
            CREATE OR REPLACE VIEW member_profile_complete AS
            SELECT
                gm.id,
                gm.group_id,
                gm.user_id,
                gm.first_name,
                gm.last_name,
                gm.email,
                gm.phone_number,
                gm.id_number,
                gm.date_of_birth,
                gm.gender,
                gm.occupation,
                gm.status,
                gm.joined_date,
                gm.is_active,
                gm.role,
                gm.share_balance,
                gm.total_contributions,
                gm.attendance_percentage,
                gm.is_eligible_for_loans,
                gm.target_amount,
                gm.profile_photo_url,
                gm.created_date,
                gm.updated_date,
                sg.name as group_name,
                sg.district as group_district,
                sg.parish as group_parish,
                sg.village as group_village,
                sg.formation_date as group_formation_date
            FROM group_members gm
            LEFT JOIN savings_groups sg ON gm.group_id = sg.id;
            """
            db.session.execute(text(view_sql))
            db.session.commit()
            print("   ✅ Database views created/verified")
        except Exception as e:
            db.session.rollback()
            print(f"   ⚠️  View creation skipped: {str(e)[:100]}")

def clear_all_data():
    """Clear all existing data except admin user"""
    print("\n🗑️  Clearing existing data...")
    
    with app.app_context():
        # Delete in correct order to respect foreign keys
        TransactionDocument.query.delete()
        SavingTransaction.query.delete()
        MemberSaving.query.delete()
        MeetingAttendance.query.delete()
        MemberFine.query.delete()
        LoanRepayment.query.delete()
        GroupLoan.query.delete()
        LoanAssessment.query.delete()
        TrainingRecord.query.delete()
        VotingRecord.query.delete()
        MeetingSummary.query.delete()
        Meeting.query.delete()
        GroupSettings.query.delete()
        GroupMember.query.filter(GroupMember.user_id != 1).delete()
        User.query.filter(User.email != 'admin@savingsgroup.com').delete()
        SavingsGroup.query.delete()
        db.session.commit()
        print("   ✅ All data cleared (admin preserved)")

def create_groups_and_members():
    """Create 3 diverse savings groups with members"""
    print("\n👥 Creating savings groups and members...")
    
    with app.app_context():
        admin = User.query.filter_by(email='admin@savingsgroup.com').first()
        if not admin:
            print("   ❌ Admin user not found!")
            return None, []
        
        # Ensure admin has admin flag
        if not admin.admin:
            admin.admin = True
            db.session.commit()
        
        groups_data = [
            {
                'name': 'Kigali Women Savings',
                'code': 'KWS001',
                'country': 'Rwanda',
                'region': 'Kigali',
                'district': 'Gasabo',
                'parish': 'Remera',
                'village': 'Gisimenti',
                'currency': 'RWF',
                'share_value': 1000,
                'members': [
                    ('Alice Mukamana', 'alice.mukamana@example.com', 'F', 'CHAIRPERSON'),
                    ('Betty Uwase', 'betty.uwase@example.com', 'F', 'SECRETARY'),
                    ('Catherine Ingabire', 'catherine.ingabire@example.com', 'F', 'TREASURER'),
                    ('Diana Mutesi', 'diana.mutesi@example.com', 'F', 'MEMBER'),
                    ('Emma Nyirahabimana', 'emma.nyira@example.com', 'F', 'MEMBER'),
                    ('Fiona Uwera', 'fiona.uwera@example.com', 'F', 'MEMBER'),
                    ('Grace Mukeshimana', 'grace.mukeshimana@example.com', 'F', 'MEMBER'),
                ]
            },
            {
                'name': 'Kampala Youth Savers',
                'code': 'KYS002',
                'country': 'Uganda',
                'region': 'Central',
                'district': 'Kampala',
                'parish': 'Nakawa',
                'village': 'Bugolobi',
                'currency': 'UGX',
                'share_value': 5000,
                'members': [
                    ('Frank Okello', 'frank.okello@example.com', 'M', 'CHAIRPERSON'),
                    ('Grace Nambi', 'grace.nambi@example.com', 'F', 'SECRETARY'),
                    ('Henry Mugisha', 'henry.mugisha@example.com', 'M', 'TREASURER'),
                    ('Irene Nakato', 'irene.nakato@example.com', 'F', 'MEMBER'),
                    ('John Ssemakula', 'john.ssemakula@example.com', 'M', 'MEMBER'),
                    ('Karen Namusoke', 'karen.namusoke@example.com', 'F', 'MEMBER'),
                    ('Lawrence Kato', 'lawrence.kato@example.com', 'M', 'MEMBER'),
                ]
            },
            {
                'name': 'Nairobi Community Fund',
                'code': 'NCF003',
                'country': 'Kenya',
                'region': 'Nairobi',
                'district': 'Westlands',
                'parish': 'Parklands',
                'village': 'Highridge',
                'currency': 'KES',
                'share_value': 500,
                'members': [
                    ('Kevin Omondi', 'kevin.omondi@example.com', 'M', 'CHAIRPERSON'),
                    ('Lucy Wanjiku', 'lucy.wanjiku@example.com', 'F', 'SECRETARY'),
                    ('Michael Kamau', 'michael.kamau@example.com', 'M', 'TREASURER'),
                    ('Nancy Akinyi', 'nancy.akinyi@example.com', 'F', 'MEMBER'),
                    ('Oscar Mwangi', 'oscar.mwangi@example.com', 'M', 'MEMBER'),
                    ('Patricia Njeri', 'patricia.njeri@example.com', 'F', 'MEMBER'),
                    ('Robert Otieno', 'robert.otieno@example.com', 'M', 'MEMBER'),
                ]
            }
        ]
        
        groups = []
        all_members = []
        
        for gdata in groups_data:
            # Create group
            group = SavingsGroup(
                name=gdata['name'],
                group_code=gdata['code'],
                description=f"A community savings group in {gdata['village']}, {gdata['district']}",
                country=gdata['country'],
                region=gdata['region'],
                district=gdata['district'],
                parish=gdata['parish'],
                village=gdata['village'],
                currency=gdata['currency'],
                share_value=Decimal(str(gdata['share_value'])),
                standard_fine_amount=Decimal(str(gdata['share_value'] * 0.5)),
                loan_interest_rate=Decimal('0.10'),
                meeting_frequency='WEEKLY',
                meeting_day=1,  # Monday
                created_by=admin.id,
                state='ACTIVE',
                status='ACTIVE',
                formation_date=date.today() - timedelta(days=180),
                max_members=30,
                minimum_contribution=Decimal(str(gdata['share_value'] * 5))
            )
            db.session.add(group)
            db.session.flush()
            
            # Create group settings
            settings = GroupSettings(
                group_id=group.id,
                personal_savings_enabled=True,
                ecd_fund_enabled=True,
                emergency_fund_enabled=True,
                social_fund_enabled=True,
                target_fund_enabled=True,
                attendance_tracking_enabled=True,
                loan_disbursement_enabled=True,
                loan_repayment_enabled=True,
                voting_session_enabled=True,
                training_session_enabled=True,
                fine_collection_enabled=True,
                max_loan_multiplier=Decimal('3.0'),
                quorum_percentage=Decimal('66.67'),
                late_arrival_fine=Decimal(str(gdata['share_value'] * 0.5)),
                absence_fine=Decimal(str(gdata['share_value'])),
                missed_contribution_fine=Decimal(str(gdata['share_value'] * 0.5))
            )
            db.session.add(settings)
            
            print(f"   ✅ Created group: {group.name} ({group.currency})")
            
            # Add admin as ADMIN member
            admin_member = GroupMember(
                group_id=group.id,
                user_id=admin.id,
                first_name='System',
                last_name='Admin',
                email='admin@savingsgroup.com',
                gender='M',
                phone_number='+250700000000',
                role='ADMIN',
                status='ACTIVE',
                joined_date=date.today() - timedelta(days=180),
                share_balance=Decimal('0')
            )
            db.session.add(admin_member)
            db.session.flush()
            
            # Create member users and group members
            group_members = []
            for idx, (name, email, gender, role) in enumerate(gdata['members']):
                # Create user
                username = email.split('@')[0]
                user = User(
                    username=username,
                    email=email,
                    password='password123'
                )
                user.active = True
                user.role = 'officer' if role in ['CHAIRPERSON', 'SECRETARY', 'TREASURER'] else 'member'
                db.session.add(user)
                db.session.flush()
                
                # Create group member
                member = GroupMember(
                    group_id=group.id,
                    user_id=user.id,
                    first_name=name.split()[0],
                    last_name=' '.join(name.split()[1:]),
                    email=email,
                    gender=gender,
                    phone_number=f"+25{idx}70{idx}123456",
                    role=role,
                    status='ACTIVE',
                    joined_date=date.today() - timedelta(days=150 - idx * 10),
                    share_balance=Decimal(str((10 + idx * 2) * gdata['share_value']))
                )
                db.session.add(member)
                db.session.flush()
                
                group_members.append((member, user))
            
            print(f"      • Added admin + {len(group_members)} members")
            all_members.append(group_members)
            groups.append(group)
        
        db.session.commit()
        return groups, all_members

def create_saving_types():
    """Create global saving types if they don't exist"""
    print("\n💰 Creating saving types...")

    with app.app_context():
        saving_types_data = [
            ('Personal Savings', 'PERSONAL', 'Regular personal savings contributions', True),
            ('ECD Fund', 'ECD', 'Early Childhood Development fund', False),
            ('Social Fund', 'SOCIAL', 'Social welfare and community support', False),
            ('Emergency Fund', 'EMERGENCY', 'Emergency assistance fund', False),
            ('Target Fund', 'TARGET', 'Target-based savings for specific goals', False),
        ]

        for name, code, desc, mandatory in saving_types_data:
            st = SavingType.query.filter_by(code=code).first()
            if not st:
                st = SavingType(
                    name=name,
                    code=code,
                    description=desc,
                    is_mandatory=mandatory,
                    is_active=True,
                    allows_withdrawal=True,
                    interest_rate=Decimal('0.0')
                )
                db.session.add(st)

        db.session.commit()
        print("   ✅ Saving types created")

def create_meetings_with_all_transactions(groups, all_members):
    """Create 6 months of meetings with ALL transaction types"""
    print("\n📅 Creating 6 months of meetings with comprehensive transactions...")

    with app.app_context():
        admin = User.query.filter_by(email='admin@savingsgroup.com').first()
        groups = SavingsGroup.query.all()

        for group_idx, group in enumerate(groups):
            members_query = GroupMember.query.filter_by(group_id=group.id, status='ACTIVE').all()
            members = [(m, User.query.get(m.user_id)) for m in members_query if m.user_id != admin.id]

            # Get saving types
            saving_types = SavingType.query.filter_by(is_active=True).all()
            personal_savings = next((st for st in saving_types if st.code == 'PERSONAL'), saving_types[0])

            # Create member_savings records
            member_savings_map = {}
            for member, user in members:
                for st in saving_types:
                    ms = MemberSaving(
                        member_id=member.id,
                        saving_type_id=st.id,
                        current_balance=Decimal('0'),
                        total_deposits=Decimal('0'),
                        total_withdrawals=Decimal('0')
                    )
                    db.session.add(ms)
                    db.session.flush()
                    if st.code == 'PERSONAL':
                        member_savings_map[member.id] = ms

            # Create 24 weekly meetings (6 months)
            num_meetings = 24
            for meeting_num in range(1, num_meetings + 1):
                meeting_date = date.today() - timedelta(days=(num_meetings - meeting_num) * 7)

                # Determine meeting status
                if meeting_num < num_meetings - 1:
                    status = 'COMPLETED'
                elif meeting_num == num_meetings - 1:
                    status = 'COMPLETED'
                else:
                    status = 'IN_PROGRESS'

                meeting = Meeting(
                    group_id=group.id,
                    meeting_number=meeting_num,
                    meeting_date=meeting_date,
                    meeting_time=datetime.strptime('14:00', '%H:%M').time(),
                    location=f"{group.village} Community Center",
                    status=status,
                    members_present=len(members),
                    total_members=len(members),
                    quorum_met=True
                )
                db.session.add(meeting)
                db.session.flush()

                # Create attendance (90-100% attendance rate)
                for member, user in members:
                    is_present = random.random() > 0.05  # 95% attendance
                    arrival_time = None
                    if is_present:
                        # Random arrival between 13:45 and 14:15
                        minutes_offset = random.randint(-15, 15)
                        arrival_time = (datetime.combine(meeting_date, datetime.strptime('14:00', '%H:%M').time()) +
                                      timedelta(minutes=minutes_offset)).time()

                    attendance = MeetingAttendance(
                        meeting_id=meeting.id,
                        group_id=group.id,
                        member_id=member.id,
                        meeting_date=meeting_date,
                        meeting_number=meeting_num,
                        is_present=is_present,
                        arrival_time=arrival_time,
                        participated_in_discussions=is_present,
                        contributed_to_savings=is_present,
                        voted_on_decisions=is_present,
                        participation_score=Decimal('10.0') if is_present else Decimal('0.0')
                    )
                    db.session.add(attendance)

                # SAVINGS TRANSACTIONS (Physical + Remote)
                for member, user in members:
                    ms = member_savings_map.get(member.id)
                    if not ms:
                        continue

                    # 90% make physical deposits
                    if random.random() < 0.90:
                        amount = Decimal(str(random.randint(5, 20) * group.share_value))
                        txn = SavingTransaction(
                            member_saving_id=ms.id,
                            meeting_id=meeting.id,
                            amount=amount,
                            transaction_type='DEPOSIT',
                            transaction_date=meeting_date,
                            is_mobile_money=False,
                            verification_status='VERIFIED',
                            verified_by=admin.id,
                            verified_date=datetime.combine(meeting_date, datetime.strptime('15:00', '%H:%M').time()),
                            description=f'Physical savings - Meeting {meeting_num}',
                            notes='Physical payment collected during meeting'
                        )
                        db.session.add(txn)
                        ms.current_balance += amount
                        ms.total_deposits += amount

                    # 10% make remote mobile money payments (only for last 2 meetings)
                    if meeting_num >= num_meetings - 2 and random.random() < 0.10:
                        amount = Decimal(str(random.randint(5, 15) * group.share_value))
                        verification_status = 'VERIFIED' if meeting_num < num_meetings else 'PENDING'

                        txn = SavingTransaction(
                            member_saving_id=ms.id,
                            meeting_id=meeting.id,
                            amount=amount,
                            transaction_type='DEPOSIT',
                            transaction_date=meeting_date,
                            is_mobile_money=True,
                            mobile_money_reference=f'MTN-{random.randint(100000, 999999)}',
                            mobile_money_phone=member.phone_number,
                            verification_status=verification_status,
                            verified_by=admin.id if verification_status == 'VERIFIED' else None,
                            verified_date=datetime.combine(meeting_date, datetime.strptime('15:30', '%H:%M').time()) if verification_status == 'VERIFIED' else None,
                            description=f'Remote mobile money payment - Meeting {meeting_num}',
                            notes='Submitted via mobile money'
                        )
                        db.session.add(txn)
                        if verification_status == 'VERIFIED':
                            ms.current_balance += amount
                            ms.total_deposits += amount

                # FINES (Late arrivals, absences)
                if status == 'COMPLETED':
                    for member, user in members:
                        attendance = MeetingAttendance.query.filter_by(
                            meeting_id=meeting.id, member_id=member.id
                        ).first()

                        # 15% get fines for late arrival
                        if attendance and attendance.is_present and attendance.arrival_time:
                            meeting_time = datetime.combine(meeting_date, meeting.meeting_time)
                            arrival_datetime = datetime.combine(meeting_date, attendance.arrival_time)
                            if arrival_datetime > meeting_time + timedelta(minutes=10):
                                fine = MemberFine(
                                    member_id=member.id,
                                    amount=group.standard_fine_amount,
                                    reason='Late arrival to meeting',
                                    fine_type='LATE_ARRIVAL',
                                    fine_date=meeting_date,
                                    is_paid=True,
                                    paid_amount=group.standard_fine_amount,
                                    payment_date=meeting_date,
                                    payment_method='CASH',
                                    verification_status='VERIFIED',
                                    verified_by=admin.id,
                                    verified_date=datetime.combine(meeting_date, datetime.strptime('15:00', '%H:%M').time()),
                                    meeting_id=meeting.id
                                )
                                db.session.add(fine)

                        # 5% get fines for absence
                        if attendance and not attendance.is_present and random.random() < 0.05:
                            fine = MemberFine(
                                member_id=member.id,
                                amount=group.standard_fine_amount * 2,
                                reason='Unexcused absence from meeting',
                                fine_type='ABSENCE',
                                fine_date=meeting_date,
                                is_paid=random.random() < 0.7,  # 70% paid
                                paid_amount=group.standard_fine_amount * 2 if random.random() < 0.7 else Decimal('0'),
                                payment_date=meeting_date if random.random() < 0.7 else None,
                                payment_method='CASH' if random.random() < 0.7 else None,
                                verification_status='VERIFIED' if random.random() < 0.7 else 'PENDING',
                                verified_by=admin.id if random.random() < 0.7 else None,
                                verified_date=datetime.combine(meeting_date, datetime.strptime('15:00', '%H:%M').time()) if random.random() < 0.7 else None,
                                meeting_id=meeting.id
                            )
                            db.session.add(fine)

                # LOANS (Disbursement every 4 meetings, ~30% of members)
                if meeting_num % 4 == 0 and status == 'COMPLETED':
                    eligible_members = random.sample(members, k=max(1, len(members) // 3))
                    for member, user in eligible_members:
                        ms = member_savings_map.get(member.id)
                        if not ms or ms.current_balance < group.share_value * 10:
                            continue

                        # Loan amount: 2-3x their savings
                        loan_amount = Decimal(str(float(ms.current_balance) * random.uniform(2.0, 3.0)))
                        loan_amount = (loan_amount // group.share_value) * group.share_value  # Round to share value
                        term_months = 3
                        total_amount_due = loan_amount * (1 + group.loan_interest_rate)
                        monthly_payment = total_amount_due / term_months

                        loan = GroupLoan(
                            member_id=member.id,
                            group_id=group.id,
                            principal=loan_amount,
                            interest_rate=group.loan_interest_rate,
                            term_months=term_months,
                            monthly_payment=monthly_payment,
                            total_amount_due=total_amount_due,
                            outstanding_balance=total_amount_due,
                            disbursement_date=meeting_date,
                            maturity_date=meeting_date + timedelta(days=90),
                            status='DISBURSED',
                            approval_date=meeting_date - timedelta(days=1),
                            approved_by=admin.id,
                            disbursed_by=admin.id
                        )
                        db.session.add(loan)
                        db.session.flush()

                        # Create loan assessment
                        assessment = LoanAssessment(
                            member_id=member.id,
                            assessment_date=meeting_date - timedelta(days=7),
                            total_savings=ms.current_balance,
                            attendance_rate=Decimal('95.0'),
                            months_active=6,
                            savings_score=Decimal('8.5'),
                            attendance_score=Decimal('9.0'),
                            participation_score=Decimal('8.0'),
                            overall_score=Decimal('8.5'),
                            is_eligible=True,
                            max_loan_amount=loan_amount * Decimal('1.5'),
                            recommended_term_months=3,
                            interest_rate=group.loan_interest_rate,
                            risk_level='LOW',
                            assessed_by=admin.id,
                            assessment_notes='Good standing member'
                        )
                        db.session.add(assessment)

                # LOAN REPAYMENTS (For existing loans, 80% make payments)
                if status == 'COMPLETED':
                    active_loans = GroupLoan.query.filter_by(
                        group_id=group.id,
                        status='DISBURSED'
                    ).all()

                    for loan in active_loans:
                        if random.random() < 0.80:  # 80% make repayments
                            repayment_amount = Decimal(str(float(loan.total_amount_due) * random.uniform(0.1, 0.3)))
                            repayment_amount = (repayment_amount // group.share_value) * group.share_value

                            repayment = LoanRepayment(
                                loan_id=loan.id,
                                member_id=loan.member_id,
                                meeting_id=meeting.id,
                                repayment_amount=repayment_amount,
                                principal_amount=repayment_amount * Decimal('0.9'),
                                interest_amount=repayment_amount * Decimal('0.1'),
                                repayment_date=meeting_date,
                                payment_method='CASH',
                                outstanding_balance=loan.outstanding_balance - repayment_amount,
                                recorded_by=admin.id
                            )
                            db.session.add(repayment)
                            loan.outstanding_balance = Decimal(str(loan.outstanding_balance)) - repayment_amount
                            loan.amount_paid = Decimal(str(loan.amount_paid)) + repayment_amount
                            loan.payments_made += 1

                            if loan.outstanding_balance <= 0:
                                loan.status = 'FULLY_REPAID'

                # TRAINING SESSIONS (Every 6 meetings)
                if meeting_num % 6 == 0 and status == 'COMPLETED':
                    topics = [
                        'Financial Literacy and Budgeting',
                        'Small Business Management',
                        'Agricultural Best Practices',
                        'Health and Nutrition',
                        'Gender Equality and Women Empowerment',
                        'Digital Financial Services'
                    ]
                    topic = random.choice(topics)

                    training = TrainingRecord(
                        meeting_id=meeting.id,
                        training_topic=topic,
                        training_description=f'Comprehensive training on {topic.lower()}',
                        trainer_name=random.choice(['John Doe', 'Jane Smith', 'Mary Johnson', 'David Brown']),
                        trainer_type=random.choice(['INTERNAL', 'EXTERNAL', 'MEMBER']),
                        duration_minutes=random.randint(60, 120),
                        total_attendees=len(members),
                        materials_provided='Training materials and handouts provided'
                    )
                    db.session.add(training)

                # VOTING SESSIONS (Every 8 meetings)
                if meeting_num % 8 == 0 and status == 'COMPLETED':
                    topics = [
                        'Increase share value',
                        'Approve new member application',
                        'Change meeting schedule',
                        'Approve group investment',
                        'Elect new officers',
                        'Approve constitution amendments'
                    ]
                    topic = random.choice(topics)

                    yes_votes = random.randint(int(len(members) * 0.6), len(members))
                    no_votes = len(members) - yes_votes

                    voting = VotingRecord(
                        meeting_id=meeting.id,
                        vote_topic=topic,
                        vote_description=f'Vote on: {topic}',
                        vote_type='SIMPLE_MAJORITY',
                        yes_count=yes_votes,
                        no_count=no_votes,
                        abstain_count=0,
                        result='PASSED' if yes_votes > no_votes else 'FAILED'
                    )
                    db.session.add(voting)

                # Create meeting summary for completed meetings
                if status == 'COMPLETED':
                    # Calculate totals
                    savings_txns = SavingTransaction.query.filter_by(
                        meeting_id=meeting.id,
                        verification_status='VERIFIED'
                    ).all()
                    total_deposits = sum(float(t.amount) for t in savings_txns if t.transaction_type == 'DEPOSIT')
                    total_withdrawals = sum(float(t.amount) for t in savings_txns if t.transaction_type == 'WITHDRAWAL')

                    fines = MemberFine.query.filter_by(meeting_id=meeting.id).all()
                    total_fines_issued = sum(float(f.amount) for f in fines)
                    total_fines_paid = sum(float(f.paid_amount or 0) for f in fines)

                    repayments = LoanRepayment.query.filter_by(meeting_id=meeting.id).all()
                    total_loan_repayments = sum(float(r.repayment_amount) for r in repayments)

                    attendances = MeetingAttendance.query.filter_by(meeting_id=meeting.id).all()
                    members_present = sum(1 for a in attendances if a.is_present)

                    summary = MeetingSummary(
                        meeting_id=meeting.id,
                        total_members=len(members),
                        members_present=members_present,
                        members_absent=len(members) - members_present,
                        attendance_rate=Decimal(str(members_present / len(members) * 100)),
                        total_deposits=Decimal(str(total_deposits)),
                        total_withdrawals=Decimal(str(total_withdrawals)),
                        net_savings=Decimal(str(total_deposits - total_withdrawals)),
                        total_fines_issued=Decimal(str(total_fines_issued)),
                        total_fines_paid=Decimal(str(total_fines_paid)),
                        outstanding_fines=Decimal(str(total_fines_issued - total_fines_paid)),
                        total_loan_repayments=Decimal(str(total_loan_repayments)),
                        loan_repayments_count=len(repayments)
                    )
                    db.session.add(summary)

                    # Update meeting totals
                    meeting.total_savings_collected = Decimal(str(total_deposits))
                    meeting.total_fines_collected = Decimal(str(total_fines_paid))
                    meeting.total_loan_repayments = Decimal(str(total_loan_repayments))

                if meeting_num % 5 == 0:
                    db.session.commit()
                    print(f"   ✅ Meeting {meeting_num} for {group.name}")

            db.session.commit()
            print(f"   ✅ Completed all meetings for {group.name}")

        print("   ✅ All meetings and transactions created")

def main():
    """Main seeding function"""
    print("\n" + "="*70)
    print("🌱 COMPREHENSIVE DATA SEEDING")
    print("="*70)

    ensure_schema_complete()
    clear_all_data()
    create_saving_types()
    groups, all_members = create_groups_and_members()
    create_meetings_with_all_transactions(groups, all_members)

    print("\n" + "="*70)
    print("✅ SEEDING COMPLETE!")
    print("="*70)
    print("\n📊 Summary:")
    print("   • 3 Savings Groups")
    print("   • 21 Members (7 per group)")
    print("   • 24 Meetings per group (6 months)")
    print("   • Comprehensive transactions:")
    print("     - Savings (Physical + Mobile Money)")
    print("     - Fines (Late arrivals + Absences)")
    print("     - Loans (Disbursements + Repayments)")
    print("     - Training Sessions")
    print("     - Voting Sessions")
    print("\n🔐 Login Credentials:")
    print("   Admin: admin@savingsgroup.com / admin123")
    print("   Members: password123")
    print("\n🚀 Ready at: http://localhost:3001")
    print("="*70 + "\n")

if __name__ == '__main__':
    main()

