"""SQLAlchemy Models - Real Data Schema"""

from datetime import datetime
from sqlalchemy import JSON, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from .connection import Base

class Company(Base):
    """Company information model"""
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    name = Column(String(255), nullable=False, index=True)
    innoforest_company_code = Column(String(100))
    thevc_company_code = Column(String(100))
    note = Column(Text)
    business_number = Column(String(50))
    business_category = Column(Text)

    # Relationship
    external_data = relationship("CompanyExternalData", back_populates="company")

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'innoforest_company_code': self.innoforest_company_code,
            'thevc_company_code': self.thevc_company_code,
            'business_number': self.business_number,
            'business_category': self.business_category,
            'note': self.note,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class TalentProfile(Base):
    """Talent profile model"""
    __tablename__ = "talent_profiles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    profile_url = Column(String(500))
    summary = Column(Text)
    positions = Column(Text)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'profile_url': self.profile_url,
            'summary': self.summary,
            'positions': self.positions
        }

class ExpTag(Base):
    """Experience and skill tag model"""
    __tablename__ = "exp_tags"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    name = Column(String(255), nullable=False, index=True)
    note = Column(Text)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'note': self.note,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class CompanyExternalData(Base):
    """Company external platform data model"""
    __tablename__ = "company_external_data"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    result_data = Column(JSON)
    note = Column(Text)
    company_id = Column(Integer, ForeignKey("companies.id"), index=True)
    platform_id = Column(Integer, index=True)

    # Relationship
    company = relationship("Company", back_populates="external_data")

    def to_dict(self):
        return {
            'id': self.id,
            'company_id': self.company_id,
            'platform_id': self.platform_id,
            'result_data': self.result_data,
            'note': self.note,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }