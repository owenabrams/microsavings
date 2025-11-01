"""
Migration script to create transaction_documents table.
This is a NON-BREAKING change - creates new table without modifying existing ones.

Phase 1: Foundation - Polymorphic Document System
"""

import os
import sys
from sqlalchemy import create_engine, text

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from project import create_app, db

def create_transaction_documents_table():
    """Create the transaction_documents table for polymorphic document attachments."""
    
    app = create_app()
    
    with app.app_context():
        print("\n" + "="*70)
        print("PHASE 1: Creating transaction_documents table")
        print("="*70 + "\n")
        
        # Check if table already exists
        check_sql = """
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name = 'transaction_documents';
        """
        result = db.session.execute(text(check_sql))
        if result.fetchone():
            print("⚠️  Table 'transaction_documents' already exists!")
            print("   Skipping creation to avoid conflicts.\n")
            return True
        
        print("Step 1: Creating transaction_documents table...")
        
        # SQL to create table
        create_table_sql = """
        CREATE TABLE transaction_documents (
            -- Primary key
            id SERIAL PRIMARY KEY,
            
            -- Polymorphic relationship
            entity_type VARCHAR(50) NOT NULL,
            entity_id INTEGER NOT NULL,
            
            -- Document metadata
            document_name VARCHAR(255) NOT NULL,
            original_filename VARCHAR(255) NOT NULL,
            document_type VARCHAR(50) NOT NULL,
            description TEXT,
            document_category VARCHAR(50),
            
            -- File information
            file_path VARCHAR(500) NOT NULL,
            file_size INTEGER NOT NULL,
            mime_type VARCHAR(100),
            file_hash VARCHAR(64),
            
            -- Compression features
            is_compressed BOOLEAN DEFAULT FALSE,
            compressed_size INTEGER,
            compression_ratio NUMERIC(5, 2),
            
            -- Preview features
            thumbnail_path VARCHAR(500),
            preview_path VARCHAR(500),
            has_preview BOOLEAN DEFAULT FALSE,
            
            -- Access control
            is_public BOOLEAN DEFAULT FALSE,
            access_level VARCHAR(50) DEFAULT 'GROUP',
            is_proof_document BOOLEAN DEFAULT FALSE,
            
            -- Audit fields
            uploaded_by INTEGER REFERENCES users(id),
            upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
            updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
            
            -- Soft delete
            is_deleted BOOLEAN DEFAULT FALSE,
            deleted_at TIMESTAMP,
            deleted_by INTEGER REFERENCES users(id)
        );
        """
        
        # Execute table creation
        db.session.execute(text(create_table_sql))
        db.session.commit()
        print("   ✓ Table created successfully\n")
        
        # Create indexes
        print("Step 2: Creating indexes for performance...")
        
        indexes = [
            ("idx_transaction_docs_entity", 
             "CREATE INDEX idx_transaction_docs_entity ON transaction_documents(entity_type, entity_id);"),
            ("idx_transaction_docs_uploaded_by", 
             "CREATE INDEX idx_transaction_docs_uploaded_by ON transaction_documents(uploaded_by);"),
            ("idx_transaction_docs_upload_date", 
             "CREATE INDEX idx_transaction_docs_upload_date ON transaction_documents(upload_date);"),
            ("idx_transaction_docs_file_hash", 
             "CREATE INDEX idx_transaction_docs_file_hash ON transaction_documents(file_hash);"),
            ("idx_transaction_docs_not_deleted", 
             "CREATE INDEX idx_transaction_docs_not_deleted ON transaction_documents(is_deleted) WHERE is_deleted = FALSE;")
        ]
        
        for index_name, index_sql in indexes:
            db.session.execute(text(index_sql))
            print(f"   ✓ Created index: {index_name}")
        
        db.session.commit()
        print()
        
        # Add table comment
        print("Step 3: Adding table documentation...")
        comment_sql = """
        COMMENT ON TABLE transaction_documents IS 
        'Polymorphic document storage for all transaction types. Supports: training, voting, loan_repayment, fine, savings, meeting, member, group';
        """
        db.session.execute(text(comment_sql))
        
        # Add column comments
        column_comments = [
            ("entity_type", "Type of entity: training, voting, loan_repayment, fine, savings, meeting, member, group"),
            ("entity_id", "ID of the entity in its respective table"),
            ("document_type", "Type of document: RECEIPT, INVOICE, PHOTO, REPORT, CERTIFICATE, OTHER"),
            ("document_category", "Category: FINANCIAL, TRAINING, VOTING, LEGAL, GENERAL"),
            ("access_level", "Access level: GROUP, ADMIN, PUBLIC")
        ]
        
        for col_name, col_desc in column_comments:
            comment_col_sql = f"""
            COMMENT ON COLUMN transaction_documents.{col_name} IS '{col_desc}';
            """
            db.session.execute(text(comment_col_sql))
        
        db.session.commit()
        print("   ✓ Documentation added\n")
        
        # Verify table exists
        print("Step 4: Verifying table creation...")
        verify_sql = """
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name = 'transaction_documents';
        """
        result = db.session.execute(text(verify_sql))
        if result.fetchone():
            print("   ✓ Table verified successfully\n")
            
            # Show table structure
            print("Step 5: Table structure:")
            print("-" * 70)
            structure_sql = """
            SELECT 
                column_name, 
                data_type, 
                is_nullable,
                column_default
            FROM information_schema.columns
            WHERE table_name = 'transaction_documents'
            ORDER BY ordinal_position;
            """
            columns = db.session.execute(text(structure_sql))
            
            print(f"{'Column Name':<25} {'Type':<20} {'Nullable':<10} {'Default':<15}")
            print("-" * 70)
            for col in columns:
                col_name = col[0]
                col_type = col[1]
                col_nullable = col[2]
                col_default = str(col[3])[:15] if col[3] else ''
                print(f"{col_name:<25} {col_type:<20} {col_nullable:<10} {col_default:<15}")
            
            print("\n" + "="*70)
            print("✅ SUCCESS: Phase 1 Foundation Complete!")
            print("="*70)
            print("\nWhat was created:")
            print("  ✓ transaction_documents table (polymorphic document storage)")
            print("  ✓ 5 performance indexes")
            print("  ✓ Foreign key constraints to users table")
            print("  ✓ Soft delete support")
            print("  ✓ Comprehensive documentation")
            print("\nImpact on existing system:")
            print("  ✓ ZERO - This is a completely non-breaking change")
            print("  ✓ Old system continues to work unchanged")
            print("  ✓ New table is ready but not yet used")
            print("\nNext steps:")
            print("  → Add TransactionDocument ORM model to models.py")
            print("  → Test the model")
            print("  → Proceed to Phase 2 (API endpoints)")
            print()
        else:
            print("\n❌ ERROR: Table creation verification failed!")
            return False
        
        return True

if __name__ == '__main__':
    try:
        success = create_transaction_documents_table()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

