"""Import CSV data to PostgreSQL database"""

import csv
import json
import sys
from datetime import datetime
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database.connection import get_engine, Base
from src.database.models import Company, TalentProfile, ExpTag, CompanyExternalData
from sqlalchemy.orm import sessionmaker

def parse_datetime(date_str):
    """Parse datetime string to datetime object"""
    if not date_str:
        return datetime.now()
    try:
        return datetime.strptime(date_str.split('.')[0], '%Y-%m-%d %H:%M:%S')
    except Exception:
        return datetime.now()

def import_companies(db):
    """Import companies from CSV"""
    print("Importing companies...")
    with open('data/structured/company_info.csv', 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        count = 0
        for row in reader:
            company = Company(
                id=int(row['id']) if row['id'] else None,
                created_at=parse_datetime(row['created_at']),
                updated_at=parse_datetime(row['updated_at']),
                name=row['name'] or '',
                innoforest_company_code=row['innoforest_company_code'] or None,
                thevc_company_code=row['thevc_company_code'] or None,
                note=row['note'] or None,
                business_number=row['business_number'] or None,
                business_category=row['business_category'] or None
            )
            db.add(company)
            count += 1
            if count % 100 == 0:
                db.commit()
                print(f"  Progress: {count} companies...")
        db.commit()
        print(f"  Completed: {count} companies imported\n")

def import_talent_profiles(db):
    """Import talent profiles from CSV"""
    print("Importing talent profiles...")
    with open('data/structured/talent_profile.csv', 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        count = 0
        for row in reader:
            talent = TalentProfile(
                name=row['name'] or '',
                profile_url=row['profile_url'] or None,
                summary=row['summary'] or None,
                positions=row['positions'] or None
            )
            db.add(talent)
            count += 1
            if count % 100 == 0:
                db.commit()
                print(f"  Progress: {count} talent profiles...")
        db.commit()
        print(f"  Completed: {count} talent profiles imported\n")

def import_exp_tags(db):
    """Import experience tags from CSV"""
    print("Importing experience tags...")
    with open('data/structured/exp_tag.csv', 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        count = 0
        for row in reader:
            exp_tag = ExpTag(
                id=int(row['id']) if row['id'] else None,
                created_at=parse_datetime(row['created_at']),
                updated_at=parse_datetime(row['updated_at']),
                name=row['name'] or '',
                note=row['note'] or None
            )
            db.add(exp_tag)
            count += 1
            if count % 100 == 0:
                db.commit()
                print(f"  Progress: {count} exp tags...")
        db.commit()
        print(f"  Completed: {count} exp tags imported\n")

def import_company_external_data(db):
    """Import company external data from CSV"""
    print("Importing company external data (this may take a while)...")
    with open('data/structured/company_external_data.csv', 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        count = 0
        for row in reader:
            result_data = None
            if row['result_data']:
                try:
                    result_data = json.loads(row['result_data'])
                except json.JSONDecodeError:
                    result_data = {"raw": row['result_data']}

            external_data = CompanyExternalData(
                id=int(row['id']) if row['id'] else None,
                created_at=parse_datetime(row['created_at']),
                updated_at=parse_datetime(row['updated_at']),
                result_data=result_data,
                note=row['note'] or None,
                company_id=int(row['company_id']) if row['company_id'] else None,
                platform_id=int(row['platform_id']) if row['platform_id'] else None
            )
            db.add(external_data)
            count += 1
            if count % 100 == 0:
                db.commit()
                print(f"  Progress: {count} external data records...")
        db.commit()
        print(f"  Completed: {count} external data records imported\n")

def main():
    """Main import process"""
    print("=" * 60)
    print("Database Import Process")
    print("=" * 60 + "\n")

    # Get engine and create tables
    engine = get_engine()
    if not engine:
        print("ERROR: Could not connect to database")
        print("Check your .env file and ensure PostgreSQL is running")
        return

    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully\n")

    # Create session
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()

    try:
        # Import data in order (companies first due to foreign key)
        import_companies(db)
        import_talent_profiles(db)
        import_exp_tags(db)
        import_company_external_data(db)

        print("=" * 60)
        print("All data imported successfully!")
        print("=" * 60)

    except Exception as e:
        print(f"\nERROR: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    main()