"""
Migration script to align database schema with ORM models.
This ensures the database matches what the application code expects.
"""

from project import create_app, db
from sqlalchemy import text

app = create_app()

def run_migration():
    """Run schema alignment migration"""
    with app.app_context():
        print("🔧 Aligning database schema with ORM models...")
        
        try:
            # Fix group_members table
            print("\n📋 Fixing group_members table...")
            
            # 1. Make user_id nullable (some members might not have user accounts)
            db.session.execute(text("""
                ALTER TABLE group_members 
                ALTER COLUMN user_id DROP NOT NULL;
            """))
            print("  ✅ Made user_id nullable")
            
            # 2. Make gender nullable
            db.session.execute(text("""
                ALTER TABLE group_members 
                ALTER COLUMN gender DROP NOT NULL;
            """))
            print("  ✅ Made gender nullable")
            
            # 3. Add target_amount column if it doesn't exist
            db.session.execute(text("""
                ALTER TABLE group_members 
                ADD COLUMN IF NOT EXISTS target_amount NUMERIC(12, 2) DEFAULT 0.00;
            """))
            print("  ✅ Added target_amount column")
            
            # 4. Change share_balance precision from (12,2) to (15,2)
            db.session.execute(text("""
                ALTER TABLE group_members 
                ALTER COLUMN share_balance TYPE NUMERIC(15, 2);
            """))
            print("  ✅ Updated share_balance precision to (15,2)")
            
            # 5. Change total_contributions precision from (12,2) to (15,2)
            db.session.execute(text("""
                ALTER TABLE group_members 
                ALTER COLUMN total_contributions TYPE NUMERIC(15, 2);
            """))
            print("  ✅ Updated total_contributions precision to (15,2)")
            
            db.session.commit()
            print("\n✅ Schema alignment complete!")
            
            # Verify the changes
            print("\n🔍 Verifying changes...")
            result = db.session.execute(text("""
                SELECT column_name, data_type, is_nullable, numeric_precision, numeric_scale
                FROM information_schema.columns
                WHERE table_name = 'group_members'
                AND column_name IN ('user_id', 'gender', 'target_amount', 'share_balance', 'total_contributions')
                ORDER BY column_name;
            """))
            
            print("\n📊 Current schema:")
            print(f"{'Column':<25} {'Type':<20} {'Nullable':<10} {'Precision':<10}")
            print("-" * 70)
            for row in result:
                col_name, data_type, is_nullable, precision, scale = row
                type_str = f"{data_type}"
                if precision and scale:
                    type_str = f"numeric({precision},{scale})"
                print(f"{col_name:<25} {type_str:<20} {is_nullable:<10} {precision or 'N/A':<10}")
            
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Migration failed: {str(e)}")
            raise

if __name__ == '__main__':
    run_migration()
    print("\n🎉 Database is now aligned with ORM models!")

