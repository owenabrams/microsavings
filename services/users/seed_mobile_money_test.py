#!/usr/bin/env python
"""
Seed script for testing Mobile Money Remote Payments feature.
Creates clean test data with 3 groups, members, meetings, and mobile money transactions.
"""

import sys
import os
from decimal import Decimal
from datetime import datetime, timedelta, date

# Add the parent directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from project import create_app, db
from project.api.models import (
    User, SavingsGroup, GroupMember, Meeting, MeetingAttendance,
    MemberSaving, SavingTransaction, SavingType, MemberFine
)

app = create_app()

def clear_all_data():
    """Clear all existing data except admin user"""
    print("\n🗑️  Clearing existing data...")
    
    with app.app_context():
        try:
            # Delete in correct order to respect foreign keys
            SavingTransaction.query.delete()
            MemberSaving.query.delete()
            MeetingAttendance.query.delete()
            Meeting.query.delete()
            GroupMember.query.delete()
            SavingsGroup.query.delete()
            
            # Delete all users except admin
            User.query.filter(User.email != 'admin@savingsgroup.com').delete()
            
            db.session.commit()
            print("   ✅ All data cleared (admin user preserved)")
        except Exception as e:
            db.session.rollback()
            print(f"   ❌ Error clearing data: {str(e)}")
            raise

def create_groups_and_members():
    """Create 3 groups with members"""
    print("\n🏢 Creating 3 savings groups with members...")
    
    with app.app_context():
        admin = User.query.filter_by(email='admin@savingsgroup.com').first()
        if not admin:
            print("   ❌ Admin user not found!")
            return None, []

        # Make sure admin user has admin flag set
        if not admin.admin:
            admin.admin = True
            db.session.commit()
            print("   ✅ Admin flag set for admin user")

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
                    ('Alice Mukamana', 'alice.mukamana@example.com', 'F', 'chairperson'),
                    ('Betty Uwase', 'betty.uwase@example.com', 'F', 'secretary'),
                    ('Catherine Ingabire', 'catherine.ingabire@example.com', 'F', 'treasurer'),
                    ('Diana Mutesi', 'diana.mutesi@example.com', 'F', 'member'),
                    ('Emma Nyirahabimana', 'emma.nyira@example.com', 'F', 'member'),
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
                    ('Frank Okello', 'frank.okello@example.com', 'M', 'chairperson'),
                    ('Grace Nambi', 'grace.nambi@example.com', 'F', 'secretary'),
                    ('Henry Mugisha', 'henry.mugisha@example.com', 'M', 'treasurer'),
                    ('Irene Nakato', 'irene.nakato@example.com', 'F', 'member'),
                    ('John Ssemakula', 'john.ssemakula@example.com', 'M', 'member'),
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
                    ('Kevin Omondi', 'kevin.omondi@example.com', 'M', 'chairperson'),
                    ('Lucy Wanjiku', 'lucy.wanjiku@example.com', 'F', 'secretary'),
                    ('Michael Kamau', 'michael.kamau@example.com', 'M', 'treasurer'),
                    ('Nancy Akinyi', 'nancy.akinyi@example.com', 'F', 'member'),
                    ('Oscar Mwangi', 'oscar.mwangi@example.com', 'M', 'member'),
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
                formation_date=date.today() - timedelta(days=90),
                max_members=30,
                minimum_contribution=Decimal(str(gdata['share_value'] * 5))
            )
            db.session.add(group)
            db.session.flush()
            
            print(f"   ✅ Created group: {group.name} ({group.currency})")

            # Add admin as a member of this group with ADMIN role
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
                joined_date=date.today() - timedelta(days=90),
                share_balance=Decimal('0')
            )
            db.session.add(admin_member)
            db.session.flush()
            print(f"      • Added admin as ADMIN member")

            # Create members
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
                user.role = 'officer' if role in ['chairperson', 'secretary', 'treasurer'] else 'member'
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
                    role=role.upper(),  # Ensure role is uppercase
                    status='ACTIVE',
                    joined_date=date.today() - timedelta(days=80),
                    share_balance=Decimal(str((10 + idx * 2) * gdata['share_value']))
                )
                db.session.add(member)
                db.session.flush()
                
                group_members.append((member, user))
            
            print(f"      • Added {len(group_members)} members")
            all_members.append(group_members)
            groups.append(group)
        
        db.session.commit()
        return groups, all_members

def create_meetings_and_transactions(groups, all_members):
    """Create meetings with both physical and mobile money transactions"""
    print("\n📅 Creating meetings with transactions...")

    with app.app_context():
        admin = User.query.filter_by(email='admin@savingsgroup.com').first()

        # Requery groups to get fresh instances
        groups = SavingsGroup.query.all()

        for group_idx, group in enumerate(groups):
            # Requery members for this group
            members_query = GroupMember.query.filter_by(group_id=group.id).all()
            members = [(m, User.query.get(m.user_id)) for m in members_query]
            
            # Get or create Personal Savings type
            saving_type = SavingType.query.filter_by(code='PERSONAL').first()
            if not saving_type:
                saving_type = SavingType(
                    name='Personal Savings',
                    code='PERSONAL',
                    description='Regular personal savings contributions',
                    is_mandatory=True,
                    minimum_amount=Decimal(str(group.share_value * 5)),
                    is_active=True
                )
                db.session.add(saving_type)
                db.session.flush()
            
            # Create member_savings records for each member
            member_savings_map = {}
            for member, user in members:
                ms = MemberSaving(
                    member_id=member.id,
                    saving_type_id=saving_type.id,
                    current_balance=Decimal('0.00'),
                    total_deposits=Decimal('0.00'),
                    total_withdrawals=Decimal('0.00')
                )
                db.session.add(ms)
                db.session.flush()
                member_savings_map[member.id] = ms
            
            # Create 3 meetings for each group
            for meeting_num in range(1, 4):
                meeting_date = date.today() - timedelta(days=(4-meeting_num) * 7)

                # Meeting 1 & 2: COMPLETED, Meeting 3: IN_PROGRESS (not ACTIVE!)
                if meeting_num < 3:
                    status = 'COMPLETED'
                else:
                    status = 'IN_PROGRESS'

                meeting = Meeting(
                    group_id=group.id,
                    meeting_number=meeting_num,
                    meeting_date=meeting_date,
                    location=f"{group.village} Community Center",
                    status=status,
                    members_present=len(members) - 1,  # One member will be remote
                    total_members=len(members),
                    quorum_met=True
                )
                db.session.add(meeting)
                db.session.flush()
                
                # Create attendance and transactions
                transaction_count = 0
                for idx, (member, user) in enumerate(members):
                    # Last member submits remote payment, others are present
                    is_remote = (idx == len(members) - 1)
                    
                    if not is_remote:
                        # Mark as present
                        attendance = MeetingAttendance(
                            meeting_id=meeting.id,
                            group_id=group.id,
                            member_id=member.id,
                            meeting_date=meeting_date,
                            is_present=True,
                            arrival_time=datetime.min.time().replace(hour=14),
                            contributed_to_savings=True
                        )
                        db.session.add(attendance)
                        
                        # Create physical transaction (auto-verified)
                        amount = Decimal(str(group.share_value * 10))
                        transaction = SavingTransaction(
                            member_saving_id=member_savings_map[member.id].id,
                            amount=amount,
                            transaction_type='DEPOSIT',
                            transaction_date=meeting_date,
                            description=f'Physical savings contribution - Meeting {meeting_num}',
                            meeting_id=meeting.id,
                            is_mobile_money=False,
                            verification_status='VERIFIED',
                            verified_by=admin.id,
                            verified_date=datetime.combine(meeting_date, datetime.min.time().replace(hour=15)),
                            notes='Physical payment collected during meeting'
                        )
                        db.session.add(transaction)
                        
                        # Update member_saving balance
                        member_savings_map[member.id].current_balance += amount
                        member_savings_map[member.id].total_deposits += amount
                        transaction_count += 1
                    else:
                        # Create remote mobile money transaction
                        amount = Decimal(str(group.share_value * 10))
                        
                        # For meeting 1 & 2: VERIFIED, For meeting 3: PENDING
                        if meeting_num < 3:
                            status = 'VERIFIED'
                            verified_by = admin.id
                            verified_date = datetime.combine(meeting_date, datetime.min.time().replace(hour=16))
                            notes = f'Remote payment verified - MTN Mobile Money'
                            # Update balance for verified payments
                            member_savings_map[member.id].current_balance += amount
                            member_savings_map[member.id].total_deposits += amount
                        else:
                            status = 'PENDING'
                            verified_by = None
                            verified_date = None
                            notes = f'Remote payment submitted by {member.first_name} {member.last_name}'
                        
                        transaction = SavingTransaction(
                            member_saving_id=member_savings_map[member.id].id,
                            amount=amount,
                            transaction_type='DEPOSIT',
                            transaction_date=meeting_date,
                            description=f'Remote mobile money contribution - Meeting {meeting_num}',
                            meeting_id=meeting.id,
                            is_mobile_money=True,
                            mobile_money_reference=f'MTN-{group.group_code}-{meeting_num:03d}{idx:02d}',
                            mobile_money_phone=member.phone_number,
                            verification_status=status,
                            verified_by=verified_by,
                            verified_date=verified_date,
                            notes=notes
                        )
                        db.session.add(transaction)
                        transaction_count += 1
                
                print(f"   ✅ Meeting {meeting_num} for {group.name}: {transaction_count} transactions")

        db.session.commit()

def create_additional_meeting_data(groups, all_members):
    """Create fines for completed meetings"""
    print("\n📋 Creating additional meeting data (fines)...")

    with app.app_context():
        admin = User.query.filter_by(email='admin@savingsgroup.com').first()
        groups = SavingsGroup.query.all()

        for group_idx, group in enumerate(groups):
            members_query = GroupMember.query.filter_by(group_id=group.id).all()
            meetings = Meeting.query.filter_by(group_id=group.id).order_by(Meeting.meeting_number).all()

            for meeting_idx, meeting in enumerate(meetings):
                meeting_num = meeting.meeting_number

                # Add fines for late arrival (only for completed meetings)
                if meeting.status == 'COMPLETED' and len(members_query) > 2:
                    late_member = members_query[1]  # Second member was late
                    fine = MemberFine(
                        member_id=late_member.id,
                        amount=Decimal(str(group.standard_fine_amount)),
                        reason='Late arrival to meeting',
                        fine_type='LATE_ARRIVAL',
                        fine_date=meeting.meeting_date,
                        is_paid=True,
                        paid_amount=Decimal(str(group.standard_fine_amount)),
                        payment_date=meeting.meeting_date,
                        payment_method='CASH',
                        verification_status='VERIFIED',
                        verified_by=admin.id,
                        verified_date=datetime.combine(meeting.meeting_date, datetime.min.time().replace(hour=15)),
                        meeting_id=meeting.id
                    )
                    db.session.add(fine)

            print(f"   ✅ Added fines for {group.name}")

        db.session.commit()

def print_summary():
    """Print summary of created data"""
    print("\n" + "="*70)
    print("📊 SEED DATA SUMMARY")
    print("="*70)
    
    with app.app_context():
        groups = SavingsGroup.query.all()
        
        for group in groups:
            members = GroupMember.query.filter_by(group_id=group.id).all()
            meetings = Meeting.query.filter_by(group_id=group.id).all()
            
            # Count transactions and other data
            total_transactions = 0
            pending_remote = 0
            verified_remote = 0
            physical = 0
            total_fines = 0

            for meeting in meetings:
                transactions = SavingTransaction.query.filter_by(meeting_id=meeting.id).all()
                total_transactions += len(transactions)
                for t in transactions:
                    if t.is_mobile_money:
                        if t.verification_status == 'PENDING':
                            pending_remote += 1
                        elif t.verification_status == 'VERIFIED':
                            verified_remote += 1
                    else:
                        physical += 1

                # Count fines
                total_fines += MemberFine.query.filter_by(meeting_id=meeting.id).count()
            
            print(f"\n📍 {group.name}")
            print(f"   Currency: {group.currency}")
            print(f"   Location: {group.village}, {group.district}, {group.country}")
            print(f"   Members: {len(members)}")
            print(f"   Meetings: {len(meetings)} (2 COMPLETED, 1 IN_PROGRESS)")
            print(f"   Savings Transactions:")
            print(f"      • Physical (✅ Verified): {physical}")
            print(f"      • Remote (✅ Verified): {verified_remote}")
            print(f"      • Remote (⏳ Pending): {pending_remote}")
            print(f"   Fines: {total_fines}")
            print(f"   URL: http://localhost:3001/groups/{group.id}")
        
        print("\n" + "="*70)
        print("🔐 LOGIN CREDENTIALS")
        print("="*70)
        print("\n👤 Admin Account:")
        print("   Email: admin@savingsgroup.com")
        print("   Password: admin123")
        
        print("\n👥 Member Accounts (all groups):")
        print("   Password: password123")
        print("\n   Group 1 (Kigali Women Savings):")
        print("      alice.mukamana@example.com (Chairperson)")
        print("      betty.uwase@example.com (Secretary)")
        print("      catherine.ingabire@example.com (Treasurer)")
        print("      diana.mutesi@example.com (Member)")
        print("      emma.nyira@example.com (Member - has pending remote payment)")
        
        print("\n   Group 2 (Kampala Youth Savers):")
        print("      frank.okello@example.com (Chairperson)")
        print("      grace.nambi@example.com (Secretary)")
        print("      henry.mugisha@example.com (Treasurer)")
        print("      irene.nakato@example.com (Member)")
        print("      john.ssemakula@example.com (Member - has pending remote payment)")
        
        print("\n   Group 3 (Nairobi Community Fund):")
        print("      kevin.omondi@example.com (Chairperson)")
        print("      lucy.wanjiku@example.com (Secretary)")
        print("      michael.kamau@example.com (Treasurer)")
        print("      nancy.akinyi@example.com (Member)")
        print("      oscar.mwangi@example.com (Member - has pending remote payment)")
        
        print("\n" + "="*70)

def main():
    """Main seeding function"""
    print("\n" + "="*70)
    print("🌱 MOBILE MONEY TEST DATA SEEDING")
    print("="*70)
    
    try:
        clear_all_data()
        groups, all_members = create_groups_and_members()
        create_meetings_and_transactions(groups, all_members)
        create_additional_meeting_data(groups, all_members)
        print_summary()
        
        print("\n✅ SEEDING COMPLETE!")
        print("\n🚀 Ready to test at: http://localhost:3001")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error during seeding: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())

