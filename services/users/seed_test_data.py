"""
Seed script to populate database with test data:
- 3 groups with different currencies
- Members for each group
- Meetings for each group
- Transactions (savings, fines, loan repayments, training, voting)
"""

from project import create_app, db
from project.api.models import (
    User, SavingsGroup, GroupMember, GroupSettings, SavingType, MemberSaving,
    Meeting, MeetingAttendance, SavingTransaction, MemberFine,
    MeetingActivity, MemberActivityParticipation
)
from datetime import datetime, date, timedelta
from decimal import Decimal
import random

app = create_app()

def clear_data():
    """Clear existing test data"""
    with app.app_context():
        print("🗑️  Clearing existing data...")
        # Clear in reverse order of dependencies
        try:
            # First, get admin user email to preserve it
            admin_email = 'admin@savingsgroup.com'

            MemberActivityParticipation.query.delete()
            MeetingActivity.query.delete()
            MemberFine.query.delete()
            SavingTransaction.query.delete()
            MeetingAttendance.query.delete()
            Meeting.query.delete()
            MemberSaving.query.delete()
            GroupSettings.query.delete()
            GroupMember.query.delete()
            SavingsGroup.query.delete()
            # Delete all users except admin
            User.query.filter(User.email != admin_email).delete()
            db.session.commit()
            print("✅ Data cleared")
        except Exception as e:
            db.session.rollback()
            print(f"⚠️  Error clearing data: {e}")
            print("Continuing anyway...")

def seed_data():
    """Seed test data"""
    with app.app_context():
        print("\n🌱 Seeding test data...")
        
        # Get admin user
        admin = User.query.filter_by(email='admin@savingsgroup.com').first()
        if not admin:
            print("❌ Admin user not found. Please create admin user first.")
            return
        
        # Create 3 groups with different currencies
        groups_data = [
            {
                'name': 'Kigali Women Savings Group',
                'currency': 'RWF',
                'country': 'Rwanda',
                'district': 'Kigali',
                'parish': 'Nyarugenge',
                'village': 'Muhima',
                'share_value': 1000,
                'member_count': 8
            },
            {
                'name': 'Kampala Business Collective',
                'currency': 'UGX',
                'country': 'Uganda',
                'district': 'Kampala',
                'parish': 'Central',
                'village': 'Nakasero',
                'share_value': 5000,
                'member_count': 6
            },
            {
                'name': 'Nairobi Community Fund',
                'currency': 'KES',
                'country': 'Kenya',
                'district': 'Nairobi',
                'parish': 'Westlands',
                'village': 'Parklands',
                'share_value': 500,
                'member_count': 7
            }
        ]
        
        groups = []
        for group_data in groups_data:
            print(f"\n📁 Creating group: {group_data['name']}")
            
            # Create group
            group = SavingsGroup(
                name=group_data['name'],
                description=f"A community savings group in {group_data['district']}, {group_data['country']}",
                group_code=f"GRP{random.randint(1000, 9999)}",
                country=group_data['country'],
                region=group_data['district'],  # Using district as region
                district=group_data['district'],
                parish=group_data['parish'],
                village=group_data['village'],
                currency=group_data['currency'],
                share_value=Decimal(group_data['share_value']),
                standard_fine_amount=Decimal(group_data['share_value'] * 0.5),
                loan_interest_rate=Decimal('0.10'),
                meeting_frequency='WEEKLY',
                meeting_day=1,  # Monday
                created_by=admin.id,
                state='ACTIVE',
                status='ACTIVE'
            )
            db.session.add(group)
            db.session.flush()

            # Create group settings
            settings = GroupSettings(
                group_id=group.id,
                personal_savings_enabled=True,
                loan_disbursement_enabled=True,
                loan_repayment_enabled=True,
                voting_session_enabled=True,
                training_session_enabled=True,
                fine_collection_enabled=True,
                attendance_tracking_enabled=True
            )
            db.session.add(settings)
            
            db.session.flush()
            groups.append(group)
            print(f"  ✅ Group created: {group.name} (ID: {group.id})")
        
        # Create members for each group with unique names
        member_names = [
            # Group 1 - Kigali
            ('Alice', 'Mukamana'), ('Betty', 'Uwase'), ('Catherine', 'Ingabire'),
            ('Diana', 'Mutesi'), ('Emma', 'Nyirahabimana'), ('Faith', 'Uwineza'),
            ('Grace', 'Mukandori'), ('Hannah', 'Uwimana'),
            # Group 2 - Kampala
            ('Irene', 'Mukeshimana'), ('Jane', 'Nyiramana'), ('Kate', 'Uwera'),
            ('Lucy', 'Mukamugema'), ('Mary', 'Uwamahoro'), ('Nancy', 'Mukasine'),
            # Group 3 - Nairobi
            ('Olive', 'Nyiransabimana'), ('Patricia', 'Mukamwezi'), ('Queen', 'Uwimbabazi'),
            ('Rose', 'Mukandayisenga'), ('Sarah', 'Nyirabahizi'), ('Therese', 'Mukamana'),
            ('Vestine', 'Uwase')
        ]
        
        all_members = []
        name_offset = 0  # Track which name to use
        for idx, group in enumerate(groups):
            print(f"\n👥 Creating members for {group.name}")
            member_count = groups_data[idx]['member_count']

            for i in range(member_count):
                first_name, last_name = member_names[name_offset + i]
                
                # Create user
                user = User(
                    username=f"{first_name.lower()}{last_name.lower()}",
                    email=f"{first_name.lower()}.{last_name.lower()}@example.com",
                    password='password123'
                )
                user.role = 'member'
                db.session.add(user)
                db.session.flush()
                
                # Create group member
                roles = ['CHAIRMAN', 'TREASURER', 'SECRETARY', 'MEMBER', 'MEMBER', 'MEMBER', 'MEMBER', 'MEMBER']
                member = GroupMember(
                    group_id=group.id,
                    user_id=user.id,
                    first_name=first_name,
                    last_name=last_name,
                    phone_number=f"+25078{random.randint(1000000, 9999999)}",
                    role=roles[i],
                    share_balance=Decimal(random.randint(5, 20) * group.share_value),
                    total_contributions=Decimal(0),
                    target_amount=Decimal(random.randint(100000, 500000)),
                    is_active=True,
                    joined_date=date.today() - timedelta(days=random.randint(30, 180))
                )
                db.session.add(member)
                db.session.flush()
                
                # Create member savings for existing saving types
                saving_types = SavingType.query.filter_by(is_active=True).limit(3).all()
                if saving_types:
                    for saving_type in saving_types:
                        member_saving = MemberSaving(
                            member_id=member.id,
                            saving_type_id=saving_type.id,
                            balance=Decimal(random.randint(10000, 50000)),
                            target_amount=Decimal(random.randint(100000, 500000))
                        )
                        db.session.add(member_saving)
                
                all_members.append(member)
                print(f"  ✅ Member: {first_name} {last_name} ({roles[i]})")

            name_offset += member_count  # Move to next set of names
            db.session.flush()
        
        # Create meetings and transactions for each group
        for group in groups:
            print(f"\n📅 Creating meetings for {group.name}")
            members = GroupMember.query.filter_by(group_id=group.id).all()
            saving_types = SavingType.query.filter_by(is_active=True).limit(3).all()
            
            # Create 3 meetings (2 completed, 1 in progress)
            for meeting_num in range(3):
                meeting_date = date.today() - timedelta(days=(3 - meeting_num) * 7)
                status = 'COMPLETED' if meeting_num < 2 else 'IN_PROGRESS'
                
                meeting = Meeting(
                    group_id=group.id,
                    meeting_date=meeting_date,
                    meeting_number=meeting_num + 1,
                    location=f"{group.district} Community Center",
                    agenda=f"Weekly meeting #{meeting_num + 1}",
                    status=status,
                    chairperson_id=members[0].id,
                    secretary_id=members[2].id if len(members) > 2 else None,
                    treasurer_id=members[1].id if len(members) > 1 else None
                )
                db.session.add(meeting)
                db.session.flush()
                
                # Record attendance (80-100% attendance)
                attending_count = random.randint(int(len(members) * 0.8), len(members))
                attending_members = random.sample(members, attending_count)
                
                for member in attending_members:
                    attendance = MeetingAttendance(
                        meeting_id=meeting.id,
                        member_id=member.id,
                        group_id=group.id,
                        meeting_date=meeting_date,
                        meeting_number=meeting_num + 1,
                        is_present=True,
                        arrival_time=datetime.min.time().replace(hour=14, minute=random.randint(0, 30))
                    )
                    db.session.add(attendance)
                
                # Add transactions only for completed meetings
                if status == 'COMPLETED':
                    # Savings transactions
                    if saving_types:
                        for member in attending_members[:random.randint(4, len(attending_members))]:
                            member_savings = MemberSaving.query.filter_by(
                                member_id=member.id,
                                saving_type_id=saving_types[0].id
                            ).first()

                            if member_savings:
                                transaction = SavingTransaction(
                                    member_saving_id=member_savings.id,
                                    amount=Decimal(random.choice([5000, 10000, 15000, 20000])),
                                    transaction_type='DEPOSIT',
                                    description=f"Meeting #{meeting_num + 1} contribution",
                                    notes=f"Regular contribution for week {meeting_num + 1}",
                                    meeting_id=meeting.id
                                )
                                db.session.add(transaction)
                    
                    # Fines (20% chance per member)
                    for member in attending_members:
                        if random.random() < 0.2:
                            fine = MemberFine(
                                member_id=member.id,
                                amount=Decimal(random.choice([1000, 2000, 3000])),
                                reason=random.choice(['Late arrival', 'Missed last meeting', 'Incomplete contribution']),
                                fine_type='ATTENDANCE',
                                is_paid=random.choice([True, False]),
                                paid_amount=Decimal(random.choice([0, 1000, 2000])),
                                notes='Issued during meeting',
                                meeting_id=meeting.id
                            )
                            db.session.add(fine)
                    
                    # Training activity
                    if meeting_num == 1:
                        training = MeetingActivity(
                            meeting_id=meeting.id,
                            activity_type='TRAINING',
                            activity_name='Financial Literacy Workshop',
                            description='Basic financial management and budgeting',
                            status='COMPLETED',
                            duration_minutes=45,
                            conducted_by=members[0].id,
                            notes='Well attended, members engaged actively'
                        )
                        db.session.add(training)
                        db.session.flush()
                        
                        # Training participation
                        for member in attending_members:
                            participation = MemberActivityParticipation(
                                activity_id=training.id,
                                member_id=member.id,
                                is_present=True,
                                contributed_to_discussions=True
                            )
                            db.session.add(participation)
                    
                    # Voting activity
                    if meeting_num == 0:
                        voting = MeetingActivity(
                            meeting_id=meeting.id,
                            activity_type='VOTING',
                            activity_name='Approve New Loan Policy',
                            description='Vote on updated loan interest rates',
                            status='COMPLETED',
                            conducted_by=members[1].id,
                            notes='Motion passed with majority vote'
                        )
                        db.session.add(voting)
                        db.session.flush()
                        
                        # Voting participation
                        for member in attending_members:
                            vote = random.choice(['YES', 'YES', 'YES', 'NO', 'ABSTAIN'])
                            participation = MemberActivityParticipation(
                                activity_id=voting.id,
                                member_id=member.id,
                                is_present=True,
                                voted_on_decisions=True,
                                notes=f"Voted: {vote}"
                            )
                            db.session.add(participation)
                
                print(f"  ✅ Meeting #{meeting_num + 1} ({status}) - {attending_count}/{len(members)} attended")
        
        # Commit all changes
        db.session.commit()
        print("\n✅ All test data seeded successfully!")
        
        # Print summary
        print("\n" + "="*60)
        print("📊 SUMMARY")
        print("="*60)
        for group in groups:
            members = GroupMember.query.filter_by(group_id=group.id).count()
            meetings = Meeting.query.filter_by(group_id=group.id).count()
            print(f"\n{group.name}")
            print(f"  Currency: {group.currency}")
            print(f"  Members: {members}")
            print(f"  Meetings: {meetings}")
            print(f"  URL: http://localhost:3001/groups/{group.id}")

if __name__ == '__main__':
    clear_data()
    seed_data()
    print("\n🎉 Database seeding complete!")
    print("\n🔐 Login credentials:")
    print("   Email: admin@savingsgroup.com")
    print("   Password: admin123")
    print("\n🌐 Access the app at: http://localhost:3001")

