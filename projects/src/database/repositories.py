"""Data Access Layer - PostgreSQL Query Interface"""

from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func
from .models import Company, TalentProfile, ExpTag, CompanyExternalData
from .connection import get_db_session, is_db_available

class TalentRepository:
    """Talent and company data repository"""

    def __init__(self):
        self.db: Optional[Session] = get_db_session()
        self.is_available: bool = is_db_available()

    def get_all_talents(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Get all talent profiles"""
        if not self.is_available or not self.db:
            return []

        try:
            talents = self.db.query(TalentProfile)\
                .limit(limit)\
                .offset(offset)\
                .all()

            return [talent.to_dict() for talent in talents]
        except Exception as e:
            print(f"Error fetching talents: {e}")
            return []

    def get_talent_by_id(self, talent_id: int) -> Optional[Dict[str, Any]]:
        """Get talent by ID"""
        if not self.is_available or not self.db:
            return None

        try:
            talent = self.db.query(TalentProfile)\
                .filter(TalentProfile.id == talent_id)\
                .first()

            return talent.to_dict() if talent else None
        except Exception as e:
            print(f"Error fetching talent: {e}")
            return None

    def search_talents_by_name(self, name: str) -> List[Dict[str, Any]]:
        """Search talents by name"""
        if not self.is_available or not self.db:
            return []

        try:
            talents = self.db.query(TalentProfile)\
                .filter(TalentProfile.name.ilike(f'%{name}%'))\
                .all()

            return [talent.to_dict() for talent in talents]
        except Exception as e:
            print(f"Error searching talents: {e}")
            return []

    def search_talents_by_position(self, position: str) -> List[Dict[str, Any]]:
        """Search talents by position"""
        if not self.is_available or not self.db:
            return []

        try:
            talents = self.db.query(TalentProfile)\
                .filter(TalentProfile.positions.ilike(f'%{position}%'))\
                .all()

            return [talent.to_dict() for talent in talents]
        except Exception as e:
            print(f"Error searching talents: {e}")
            return []

    def get_all_companies(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Get all companies"""
        if not self.is_available or not self.db:
            return []

        try:
            companies = self.db.query(Company)\
                .limit(limit)\
                .offset(offset)\
                .all()

            return [company.to_dict() for company in companies]
        except Exception as e:
            print(f"Error fetching companies: {e}")
            return []

    def get_company_by_id(self, company_id: int) -> Optional[Dict[str, Any]]:
        """Get company by ID with external data"""
        if not self.is_available or not self.db:
            return None

        try:
            company = self.db.query(Company)\
                .options(joinedload(Company.external_data))\
                .filter(Company.id == company_id)\
                .first()

            if not company:
                return None

            result = company.to_dict()
            result['external_data'] = [data.to_dict() for data in company.external_data]
            return result
        except Exception as e:
            print(f"Error fetching company: {e}")
            return None

    def search_companies_by_name(self, name: str) -> List[Dict[str, Any]]:
        """Search companies by name"""
        if not self.is_available or not self.db:
            return []

        try:
            companies = self.db.query(Company)\
                .filter(Company.name.ilike(f'%{name}%'))\
                .all()

            return [company.to_dict() for company in companies]
        except Exception as e:
            print(f"Error searching companies: {e}")
            return []

    def search_companies_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Search companies by business category"""
        if not self.is_available or not self.db:
            return []

        try:
            companies = self.db.query(Company)\
                .filter(Company.business_category.ilike(f'%{category}%'))\
                .all()

            return [company.to_dict() for company in companies]
        except Exception as e:
            print(f"Error searching companies: {e}")
            return []

    def get_all_exp_tags(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Get all experience tags"""
        if not self.is_available or not self.db:
            return []

        try:
            tags = self.db.query(ExpTag)\
                .limit(limit)\
                .offset(offset)\
                .all()

            return [tag.to_dict() for tag in tags]
        except Exception as e:
            print(f"Error fetching exp tags: {e}")
            return []

    def search_exp_tags(self, keyword: str) -> List[Dict[str, Any]]:
        """Search experience tags by keyword"""
        if not self.is_available or not self.db:
            return []

        try:
            tags = self.db.query(ExpTag)\
                .filter(ExpTag.name.ilike(f'%{keyword}%'))\
                .all()

            return [tag.to_dict() for tag in tags]
        except Exception as e:
            print(f"Error searching exp tags: {e}")
            return []

    def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics"""
        if not self.is_available or not self.db:
            return {
                'total_talents': 0,
                'total_companies': 0,
                'total_exp_tags': 0,
                'total_external_data': 0,
                'error': 'Database not available'
            }

        try:
            total_talents = self.db.query(TalentProfile).count()
            total_companies = self.db.query(Company).count()
            total_exp_tags = self.db.query(ExpTag).count()
            total_external_data = self.db.query(CompanyExternalData).count()

            return {
                'total_talents': total_talents,
                'total_companies': total_companies,
                'total_exp_tags': total_exp_tags,
                'total_external_data': total_external_data
            }
        except Exception as e:
            print(f"Error fetching statistics: {e}")
            return {
                'total_talents': 0,
                'total_companies': 0,
                'total_exp_tags': 0,
                'total_external_data': 0,
                'error': str(e)
            }

    def close(self):
        """Close database session"""
        if self.db:
            self.db.close()

# Global repository instance
_repository_instance = None

def get_talent_repository() -> TalentRepository:
    """Get global repository instance"""
    global _repository_instance
    if _repository_instance is None:
        _repository_instance = TalentRepository()
    return _repository_instance