#!/usr/bin/env python
"""Management script for Flask application."""
import sys
import os
from flask.cli import FlaskGroup
from flask_migrate import Migrate
from project import create_app, db
from project.api.models import User, SavingsGroup, GroupMember


# Create Flask app
app = create_app()
migrate = Migrate(app, db)
cli = FlaskGroup(create_app=create_app)


@cli.command('recreate_db')
def recreate_db():
    """Recreate the database."""
    db.drop_all()
    db.create_all()
    db.session.commit()
    print('✅ Database recreated!')


@cli.command('seed_db')
def seed_db():
    """Seed the database with initial data."""
    # Create admin user
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
        print('✅ Admin user created')
    else:
        print('ℹ️  Admin user already exists')


@cli.command('seed_demo_data')
def seed_demo_data():
    """Seed comprehensive demo data with all transaction types."""
    print('🌱 Seeding comprehensive demo data...')

    # Import and run the comprehensive seeding script
    sys.path.insert(0, os.path.dirname(__file__))

    try:
        from seed_comprehensive_data import main as seed_main
        seed_main()
        print('✅ Demo data seeded successfully!')
    except Exception as e:
        print(f'❌ Error seeding demo data: {str(e)}')
        import traceback
        traceback.print_exc()


@cli.command('seed_comprehensive')
def seed_comprehensive():
    """Seed comprehensive data (alias for seed_demo_data)."""
    seed_demo_data()


@cli.command('create_super_admin')
def create_super_admin():
    """Create a super admin user."""
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
        print('✅ Super admin created: admin@savingsgroup.com / admin123')
    else:
        print('ℹ️  Super admin already exists')


if __name__ == '__main__':
    cli()

