#!/usr/bin/env python
"""
Create missing tables that are defined in ORM models but don't exist in database.
This script creates:
- loan_repayments
- training_records
- voting_records
- training_attendance
- member_votes
"""

import sys
from project import create_app, db
from sqlalchemy import text

app = create_app()

def create_missing_tables():
    """Create all missing tables."""
    with app.app_context():
        try:
            print("Creating missing tables...")
            
            # Create loan_repayments table
            print("\n1. Creating loan_repayments table...")
            db.session.execute(text("""
                CREATE TABLE IF NOT EXISTS loan_repayments (
                    id SERIAL PRIMARY KEY,
                    loan_id INTEGER NOT NULL REFERENCES group_loans(id) ON DELETE CASCADE,
                    meeting_id INTEGER REFERENCES meetings(id) ON DELETE SET NULL,
                    member_id INTEGER NOT NULL REFERENCES group_members(id) ON DELETE CASCADE,
                    repayment_amount NUMERIC(12, 2) NOT NULL,
                    principal_amount NUMERIC(12, 2) NOT NULL,
                    interest_amount NUMERIC(12, 2) NOT NULL,
                    outstanding_balance NUMERIC(12, 2) NOT NULL,
                    repayment_date DATE NOT NULL,
                    payment_method VARCHAR(50) DEFAULT 'CASH',
                    mobile_money_reference VARCHAR(100),
                    mobile_money_phone VARCHAR(20),
                    recorded_by INTEGER REFERENCES users(id),
                    notes TEXT,
                    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
                    updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
                );
            """))
            print("✓ loan_repayments table created")
            
            # Create training_records table
            print("\n2. Creating training_records table...")
            db.session.execute(text("""
                CREATE TABLE IF NOT EXISTS training_records (
                    id SERIAL PRIMARY KEY,
                    meeting_id INTEGER NOT NULL REFERENCES meetings(id) ON DELETE CASCADE,
                    training_topic VARCHAR(255) NOT NULL,
                    training_description TEXT,
                    trainer_name VARCHAR(255),
                    trainer_type VARCHAR(50),
                    duration_minutes INTEGER,
                    materials_provided TEXT,
                    total_attendees INTEGER DEFAULT 0,
                    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
                    updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
                );
            """))
            print("✓ training_records table created")
            
            # Create voting_records table
            print("\n3. Creating voting_records table...")
            db.session.execute(text("""
                CREATE TABLE IF NOT EXISTS voting_records (
                    id SERIAL PRIMARY KEY,
                    meeting_id INTEGER NOT NULL REFERENCES meetings(id) ON DELETE CASCADE,
                    vote_topic VARCHAR(255) NOT NULL,
                    vote_description TEXT,
                    vote_type VARCHAR(50) DEFAULT 'SIMPLE_MAJORITY',
                    result VARCHAR(50),
                    yes_count INTEGER DEFAULT 0,
                    no_count INTEGER DEFAULT 0,
                    abstain_count INTEGER DEFAULT 0,
                    absent_count INTEGER DEFAULT 0,
                    proposed_by INTEGER REFERENCES group_members(id),
                    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
                    updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
                );
            """))
            print("✓ voting_records table created")
            
            # Create training_attendance table
            print("\n4. Creating training_attendance table...")
            db.session.execute(text("""
                CREATE TABLE IF NOT EXISTS training_attendance (
                    id SERIAL PRIMARY KEY,
                    training_id INTEGER NOT NULL REFERENCES training_records(id) ON DELETE CASCADE,
                    member_id INTEGER NOT NULL REFERENCES group_members(id) ON DELETE CASCADE,
                    attended BOOLEAN DEFAULT FALSE,
                    participation_score NUMERIC(3, 1),
                    notes TEXT,
                    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
                    UNIQUE(training_id, member_id)
                );
            """))
            print("✓ training_attendance table created")
            
            # Create member_votes table
            print("\n5. Creating member_votes table...")
            db.session.execute(text("""
                CREATE TABLE IF NOT EXISTS member_votes (
                    id SERIAL PRIMARY KEY,
                    voting_record_id INTEGER NOT NULL REFERENCES voting_records(id) ON DELETE CASCADE,
                    member_id INTEGER NOT NULL REFERENCES group_members(id) ON DELETE CASCADE,
                    vote_cast VARCHAR(20) NOT NULL,
                    notes TEXT,
                    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
                    UNIQUE(voting_record_id, member_id)
                );
            """))
            print("✓ member_votes table created")

            # Create meeting_summaries table
            print("\n6. Creating meeting_summaries table...")
            db.session.execute(text("""
                CREATE TABLE IF NOT EXISTS meeting_summaries (
                    id SERIAL PRIMARY KEY,
                    meeting_id INTEGER NOT NULL REFERENCES meetings(id) ON DELETE CASCADE UNIQUE,
                    total_members INTEGER DEFAULT 0,
                    members_present INTEGER DEFAULT 0,
                    members_absent INTEGER DEFAULT 0,
                    attendance_rate NUMERIC(5, 2) DEFAULT 0.00,
                    total_deposits NUMERIC(12, 2) DEFAULT 0.00,
                    total_withdrawals NUMERIC(12, 2) DEFAULT 0.00,
                    net_savings NUMERIC(12, 2) DEFAULT 0.00,
                    total_fines_issued NUMERIC(12, 2) DEFAULT 0.00,
                    total_fines_paid NUMERIC(12, 2) DEFAULT 0.00,
                    outstanding_fines NUMERIC(12, 2) DEFAULT 0.00,
                    total_loans_disbursed NUMERIC(12, 2) DEFAULT 0.00,
                    loans_disbursed_count INTEGER DEFAULT 0,
                    total_loan_repayments NUMERIC(12, 2) DEFAULT 0.00,
                    loan_repayments_count INTEGER DEFAULT 0,
                    trainings_held INTEGER DEFAULT 0,
                    training_attendance_count INTEGER DEFAULT 0,
                    training_participation_rate NUMERIC(5, 2) DEFAULT 0.00,
                    voting_sessions_held INTEGER DEFAULT 0,
                    votes_cast_count INTEGER DEFAULT 0,
                    voting_participation_rate NUMERIC(5, 2) DEFAULT 0.00,
                    net_cash_flow NUMERIC(12, 2) DEFAULT 0.00,
                    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
                    updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
                );
            """))
            print("✓ meeting_summaries table created")

            db.session.commit()
            
            print("\n" + "="*60)
            print("✅ All missing tables created successfully!")
            print("="*60)
            
            # Verify tables exist
            print("\nVerifying tables...")
            result = db.session.execute(text("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_name IN ('loan_repayments', 'training_records', 'voting_records', 'training_attendance', 'member_votes', 'meeting_summaries')
                ORDER BY table_name;
            """))

            tables = [row[0] for row in result]
            print(f"Found {len(tables)} tables:")
            for table in tables:
                print(f"  ✓ {table}")
            
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Migration failed: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    success = create_missing_tables()
    sys.exit(0 if success else 1)

