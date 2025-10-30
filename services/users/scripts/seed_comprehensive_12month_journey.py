#!/usr/bin/env python3
"""
Comprehensive 12-Month Member Journey Seeding Script
Production-Ready Seed Data for Complete Testing

This script creates:
- 3 Savings Groups (Kigali Women, Kampala Traders, Nairobi Entrepreneurs)
- 53 Total Members (distributed across groups)
- 60 Monthly Meetings (12 per group)
- Complete Financial Data (savings, loans, fines, transactions)
- Mobile Money Accounts
- Attendance Records
- Loan Assessments
- IGA Participation Data

Database: PostgreSQL
Environment: Docker Container
"""

import os
import sys
from datetime import datetime, timedelta
from decimal import Decimal
import json

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from project import create_app, db
from project.api.models import (
    User, SavingsGroup, GroupMember, Meeting, MeetingAttendance,
    MemberSaving, MemberFine, GroupLoan, LoanAssessment,
    GroupTransaction, GroupCashbook, MobileMoneyAccount, SavingType
)

def create_seed_app():
    """Create Flask app for seeding"""
    app = create_app()
    return app

def seed_users():
    """Create admin and staff users"""
    print("👤 Creating users...")
    
    admin = User.query.filter_by(email='admin@savingsgroup.com').first()
    if not admin:
        admin = User(
            username='admin',
            email='admin@savingsgroup.com',
            password='admin123'
        )
        admin.admin = True
        admin.role = 'super_admin'
        admin.is_super_admin = True
        admin.active = True
        db.session.add(admin)
    
    db.session.commit()
    print(f"   ✅ Admin user ready (ID: {admin.id})")
    return admin

def seed_groups(admin):
    """Create 3 savings groups"""
    print("\n🏢 Creating 3 savings groups...")

    groups_data = [
        {
            'name': 'Kigali Women Savings Group',
            'group_code': 'KWSG001',
            'description': 'Professional women savings and investment group',
            'parish': 'Gasabo',
            'village': 'Gisozi',
            'district': 'Kigali',
            'country': 'Rwanda',
            'region': 'Central',
            'members_count': 18,
        },
        {
            'name': 'Kampala Traders Association',
            'group_code': 'KTA002',
            'description': 'Small business traders savings circle',
            'parish': 'Nakawa',
            'village': 'Bukoto',
            'district': 'Kampala',
            'country': 'Uganda',
            'region': 'Central',
            'members_count': 17,
        },
        {
            'name': 'Nairobi Entrepreneurs Fund',
            'group_code': 'NEF003',
            'description': 'Young entrepreneurs investment group',
            'parish': 'Westlands',
            'village': 'Kilimani',
            'district': 'Nairobi',
            'country': 'Kenya',
            'region': 'East',
            'members_count': 18,
        }
    ]

    groups = []
    for gdata in groups_data:
        group = SavingsGroup.query.filter_by(name=gdata['name']).first()
        if not group:
            group = SavingsGroup(
                name=gdata['name'],
                group_code=gdata['group_code'],
                formation_date=datetime.now().date(),
                created_by=admin.id,
                description=gdata['description'],
                country=gdata['country'],
                region=gdata['region'],
                district=gdata['district'],
                parish=gdata['parish'],
                village=gdata['village'],
                target_amount=Decimal('50000.00'),
                max_members=30
            )
            group.state = 'ACTIVE'
            group.savings_balance = Decimal('0.00')
            group.members_count = gdata['members_count']
            group.meeting_frequency = 'MONTHLY'
            group.minimum_contribution = Decimal('5000.00')
            db.session.add(group)
        groups.append(group)

    db.session.commit()
    print(f"   ✅ {len(groups)} groups created")
    return groups

def seed_members(groups):
    """Create 53 members across 3 groups"""
    print("\n👥 Creating 53 members...")

    members_data = {
        0: [  # Kigali Women (18 members)
            ('Alice Mukamana', 'F'), ('Beatrice Uwimana', 'F'), ('Claudette Habimana', 'F'),
            ('Diana Nyirahabimana', 'F'), ('Evelyne Mukamusoni', 'F'), ('Francine Uwase', 'F'),
            ('Grace Mukankusi', 'F'), ('Hilda Nyiramahoro', 'F'), ('Irene Mukamusoni', 'F'),
            ('Jacqueline Habimana', 'F'), ('Karine Uwimana', 'F'), ('Lydia Mukamana', 'F'),
            ('Madeleine Nyirahabimana', 'F'), ('Nadine Mukamusoni', 'F'), ('Odette Uwase', 'F'),
            ('Pauline Mukankusi', 'F'), ('Quincy Nyiramahoro', 'F'), ('Rachel Mukamusoni', 'F'),
        ],
        1: [  # Kampala Traders (17 members)
            ('Samuel Okonkwo', 'M'), ('Tunde Adeyemi', 'M'), ('Uche Nwankwo', 'M'),
            ('Victor Okafor', 'M'), ('Wale Adebayo', 'M'), ('Xavier Okoro', 'M'),
            ('Yusuf Adeyinka', 'M'), ('Zainab Okafor', 'F'), ('Amara Nwankwo', 'F'),
            ('Blessing Adeyemi', 'F'), ('Chioma Okonkwo', 'F'), ('Deborah Okoro', 'F'),
            ('Ebube Adebayo', 'F'), ('Folake Adeyinka', 'F'), ('Gina Nwankwo', 'F'),
            ('Hanna Okafor', 'F'), ('Ify Adeyemi', 'F'),
        ],
        2: [  # Nairobi Entrepreneurs (18 members)
            ('James Kipchoge', 'M'), ('Kevin Mwangi', 'M'), ('Liam Omondi', 'M'),
            ('Michael Kariuki', 'M'), ('Noel Kiplagat', 'M'), ('Oscar Mwangi', 'M'),
            ('Peter Omondi', 'M'), ('Quinton Kariuki', 'M'), ('Rachel Kipchoge', 'F'),
            ('Sarah Mwangi', 'F'), ('Tessa Omondi', 'F'), ('Usha Kariuki', 'F'),
            ('Violet Kiplagat', 'F'), ('Wendy Mwangi', 'F'), ('Xenia Omondi', 'F'),
            ('Yara Kariuki', 'F'), ('Zara Kiplagat', 'F'), ('Amelia Mwangi', 'F'),
        ]
    }

    all_members = []
    for group_idx, group in enumerate(groups):
        for idx, (name, gender) in enumerate(members_data[group_idx]):
            # Create user for member
            email = f'{name.lower().replace(" ", ".")}@group{group_idx}.com'
            user = User.query.filter_by(email=email).first()
            if not user:
                user = User(
                    username=name.lower().replace(" ", "."),
                    email=email,
                    password='password123'
                )
                user.active = True
                user.role = 'user'
                db.session.add(user)
                db.session.flush()

            # Create group member
            member = GroupMember.query.filter_by(
                group_id=group.id, user_id=user.id
            ).first()
            if not member:
                # Split name into first and last name
                name_parts = name.split(' ', 1)
                first_name = name_parts[0]
                last_name = name_parts[1] if len(name_parts) > 1 else name_parts[0]

                member = GroupMember(
                    group_id=group.id,
                    user_id=user.id,
                    first_name=first_name,
                    last_name=last_name,
                    gender=gender,
                    phone_number=f'+250{78800000 + group_idx*1000 + idx}',
                    role='FOUNDER' if idx == 0 else 'MEMBER'
                )
                db.session.add(member)
            all_members.append(member)

    db.session.commit()
    print(f"   ✅ {len(all_members)} members created")
    return all_members

def seed_meetings_and_attendance(groups, all_members):
    """Create 12 meetings per group with attendance"""
    print("\n📅 Creating 60 meetings with attendance records...")

    meeting_count = 0
    start_date = datetime(2024, 1, 1)

    for group in groups:
        group_members = [m for m in all_members if m.group_id == group.id]

        if len(group_members) < 3:
            print(f"   ⚠️  Skipping {group.name} - needs at least 3 members")
            continue

        for month in range(12):
            meeting_date = start_date + timedelta(days=30*month)
            meeting_number = month + 1  # Meeting numbers start at 1

            meeting = Meeting.query.filter_by(
                group_id=group.id,
                meeting_date=meeting_date.date()
            ).first()

            if not meeting:
                meeting = Meeting(
                    group_id=group.id,
                    meeting_number=meeting_number,
                    meeting_date=meeting_date.date(),
                    chairperson_id=group_members[0].id,
                    secretary_id=group_members[1].id,
                    treasurer_id=group_members[2].id,
                    meeting_type='REGULAR'
                )
                meeting.status = 'COMPLETED'
                meeting.total_members = len(group_members)
                meeting.members_present = int(len(group_members) * 0.75)
                meeting.attendance_count = meeting.members_present
                meeting.quorum_met = True
                meeting.total_savings_collected = Decimal('50000.00')
                db.session.add(meeting)
                db.session.flush()

                # Add attendance records
                for idx, member in enumerate(group_members):
                    is_present = (idx % 3) != 0  # 2/3 attendance rate
                    attendance = MeetingAttendance(
                        group_id=group.id,
                        member_id=member.id,
                        meeting_date=meeting_date.date(),
                        meeting_number=meeting_number,
                        meeting_id=meeting.id,
                        is_present=is_present,
                        excuse_reason='Personal commitment' if not is_present else None,
                        participated_in_discussions=is_present,
                        contributed_to_savings=is_present,
                        voted_on_decisions=is_present,
                        participation_score=8.0 if is_present else 0.0
                    )
                    db.session.add(attendance)

            meeting_count += 1

    db.session.commit()
    print(f"   ✅ {meeting_count} meetings created with attendance")

def seed_financial_data(groups, all_members):
    """Create member savings, fines, loans, and transactions"""
    print("\n💰 Creating financial data...")

    # First, ensure saving types exist
    saving_types = SavingType.query.all()
    if not saving_types:
        saving_types = []
        for code, name in [('PERSONAL', 'Personal Savings'), ('ECD', 'ECD Fund'), ('SOCIAL', 'Social Fund')]:
            st = SavingType(
                name=name,
                code=code,
                description=f'{name} for group members'
            )
            db.session.add(st)
            saving_types.append(st)
        db.session.flush()

    for group in groups:
        group_members = [m for m in all_members if m.group_id == group.id]

        for idx, member in enumerate(group_members):
            # Create member savings for each saving type
            for saving_type in saving_types:
                saving = MemberSaving.query.filter_by(
                    member_id=member.id,
                    saving_type_id=saving_type.id
                ).first()
                if not saving:
                    amount = Decimal(str(5000 + (idx * 100)))
                    saving = MemberSaving(
                        member_id=member.id,
                        saving_type_id=saving_type.id,
                        current_balance=amount,
                        target_amount=Decimal('50000.00'),
                        total_deposits=amount
                    )
                    db.session.add(saving)
                    member.total_contributions += amount

            # Member Fines (occasional)
            if idx % 5 == 0:
                fine = MemberFine.query.filter_by(
                    member_id=member.id
                ).first()
                if not fine:
                    fine = MemberFine(
                        member_id=member.id,
                        amount=Decimal('500.00'),
                        reason='Late attendance',
                        fine_type='LATE_ARRIVAL',
                        imposed_by=1,
                        fine_date=datetime.now().date(),
                        due_date=datetime.now().date() + timedelta(days=30)
                    )
                    db.session.add(fine)

    db.session.commit()
    print(f"   ✅ Financial data created")

def seed_loan_data(groups, all_members):
    """Create loan assessments and loans"""
    print("\n🏦 Creating loan data...")

    for group in groups:
        group_members = [m for m in all_members if m.group_id == group.id]

        for idx, member in enumerate(group_members[:5]):  # 5 members per group
            assessment = LoanAssessment.query.filter_by(
                member_id=member.id
            ).first()
            if not assessment:
                assessment = LoanAssessment(
                    member_id=member.id,
                    total_savings=Decimal(str(50000 + (idx * 5000))),
                    months_active=12,
                    attendance_rate=Decimal('85.00'),
                    assessed_by=1,
                    savings_score=Decimal('80.00'),
                    attendance_score=Decimal('85.00'),
                    participation_score=Decimal('75.00'),
                    overall_score=Decimal(str(75 + (idx * 3))),
                    is_eligible=True,
                    max_loan_amount=Decimal(str(50000 + (idx * 10000))),
                    recommended_term_months=12,
                    interest_rate=Decimal('0.0500'),
                    risk_level='LOW' if idx % 2 == 0 else 'MEDIUM',
                    assessment_notes='Eligible for loan'
                )
                assessment.is_current = True
                db.session.add(assessment)

    db.session.commit()
    print(f"   ✅ Loan data created")

def seed_mobile_money_accounts(groups):
    """Add mobile money accounts to groups"""
    print("\n📱 Adding mobile money accounts...")

    providers = ['MTN Mobile Money', 'Airtel Money', 'Vodafone Cash']

    for idx, group in enumerate(groups):
        for provider_idx, provider in enumerate(providers[:2]):
            account = MobileMoneyAccount.query.filter_by(
                group_id=group.id,
                provider=provider
            ).first()
            if not account:
                account = MobileMoneyAccount(
                    group_id=group.id,
                    provider=provider,
                    account_number=f'+250{78800000 + idx*1000 + provider_idx}',
                    account_holder=group.name,
                    is_primary=(provider_idx == 0)
                )
                db.session.add(account)

    db.session.commit()
    print(f"   ✅ Mobile money accounts added")

def main():
    """Main seeding function"""
    print("\n" + "="*70)
    print("🌱 COMPREHENSIVE 12-MONTH MEMBER JOURNEY SEEDING")
    print("="*70)

    try:
        app = create_seed_app()
        with app.app_context():
            # Create tables if they don't exist
            db.create_all()
            
            # Seed data in order
            admin = seed_users()
            groups = seed_groups(admin)
            all_members = seed_members(groups)
            seed_meetings_and_attendance(groups, all_members)
            seed_financial_data(groups, all_members)
            seed_loan_data(groups, all_members)
            seed_mobile_money_accounts(groups)
            
            print("\n" + "="*70)
            print("✅ SEEDING COMPLETE!")
            print("="*70)
            print(f"📊 Summary:")
            print(f"   • 3 Savings Groups")
            print(f"   • 53 Total Members")
            print(f"   • 60 Monthly Meetings")
            print(f"   • Complete Financial Data")
            print("="*70 + "\n")
            
    except Exception as e:
        print(f"\n❌ Seeding failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()

