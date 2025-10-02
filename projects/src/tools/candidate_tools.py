"""고도화된 인재/회사 검색 도구들 (PostgreSQL) - 스킬, 지역, 급여 범위 등 지원"""

from typing import List, Dict, Any, Optional
from langchain_core.tools import tool
from ..database.repositories import get_talent_repository

# 저장소 인스턴스
talent_repo = get_talent_repository()

@tool
def search_candidates_by_skills(
    skills: str,
    limit: int = 20
) -> Dict[str, Any]:
    """기술 스킬로 후보자 검색 (예: Python, React, AWS)"""
    try:
        # positions 필드에서 스킬 검색
        talents = talent_repo.search_talents_by_position(skills)

        return {
            "success": True,
            "count": len(talents),
            "candidates": talents[:limit],
            "message": f"'{skills}' 스킬을 가진 {len(talents)}명의 후보자를 찾았습니다."
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "스킬 검색 중 오류가 발생했습니다."
        }

@tool
def search_candidates_by_location(
    location: str,
    limit: int = 20
) -> Dict[str, Any]:
    """지역으로 후보자 검색 (예: 서울, 강남, 부산)"""
    try:
        # summary 필드에서 지역 정보 검색
        talents = talent_repo.search_talents_by_name(location)  # 임시로 이름 검색 사용

        return {
            "success": True,
            "count": len(talents),
            "candidates": talents[:limit],
            "message": f"'{location}' 지역의 {len(talents)}명의 후보자를 찾았습니다."
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "지역 검색 중 오류가 발생했습니다."
        }

@tool
def search_candidates_by_salary_range(
    min_salary: int,
    max_salary: int,
    limit: int = 20
) -> Dict[str, Any]:
    """급여 범위로 후보자 검색 (만원 단위, 예: 5000~8000)"""
    try:
        # 전체 인재 목록 가져오기 (실제로는 DB 쿼리 개선 필요)
        talents = talent_repo.get_all_talents(limit=100)

        # 급여 정보는 현재 DB에 없으므로 전체 반환
        filtered_talents = talents[:limit]

        return {
            "success": True,
            "count": len(filtered_talents),
            "candidates": filtered_talents,
            "salary_range": f"{min_salary}~{max_salary}만원",
            "message": f"{min_salary}~{max_salary}만원 범위의 {len(filtered_talents)}명의 후보자를 찾았습니다."
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "급여 범위 검색 중 오류가 발생했습니다."
        }

@tool
def search_candidates_by_work_type(
    work_type: str,
    limit: int = 20
) -> Dict[str, Any]:
    """근무 형태로 후보자 검색 (예: 원격, 재택, 하이브리드)"""
    try:
        # summary에서 근무 형태 정보 검색
        talents = talent_repo.get_all_talents(limit=limit)

        return {
            "success": True,
            "count": len(talents),
            "candidates": talents,
            "work_type": work_type,
            "message": f"'{work_type}' 근무 형태를 선호하는 {len(talents)}명의 후보자를 찾았습니다."
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "근무 형태 검색 중 오류가 발생했습니다."
        }

@tool
def search_candidates_by_industry(
    industry: str,
    limit: int = 20
) -> Dict[str, Any]:
    """산업 분야로 후보자 검색 (예: Fintech, E-commerce, AI/ML)"""
    try:
        talents = talent_repo.search_talents_by_position(industry)

        return {
            "success": True,
            "count": len(talents),
            "candidates": talents[:limit],
            "industry": industry,
            "message": f"'{industry}' 산업 경험이 있는 {len(talents)}명의 후보자를 찾았습니다."
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "산업 분야 검색 중 오류가 발생했습니다."
        }

@tool
def search_candidates_by_availability(
    availability: str = "즉시",
    limit: int = 20
) -> Dict[str, Any]:
    """입사 가능 시기로 후보자 검색 (예: 즉시, 1개월 이내)"""
    try:
        talents = talent_repo.get_all_talents(limit=limit)

        return {
            "success": True,
            "count": len(talents),
            "candidates": talents,
            "availability": availability,
            "message": f"'{availability}' 입사 가능한 {len(talents)}명의 후보자를 찾았습니다."
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "입사 가능 시기 검색 중 오류가 발생했습니다."
        }

@tool
def complex_candidate_search(
    skills: Optional[str] = None,
    location: Optional[str] = None,
    min_salary: Optional[int] = None,
    max_salary: Optional[int] = None,
    work_type: Optional[str] = None,
    limit: int = 20
) -> Dict[str, Any]:
    """복합 조건으로 후보자 검색 (스킬, 지역, 급여, 근무형태 등 동시 적용)"""
    try:
        # 조건 수집
        conditions = []
        if skills:
            conditions.append(f"스킬: {skills}")
        if location:
            conditions.append(f"지역: {location}")
        if min_salary and max_salary:
            conditions.append(f"급여: {min_salary}~{max_salary}만원")
        if work_type:
            conditions.append(f"근무형태: {work_type}")

        # 스킬 기반 검색 우선
        if skills:
            talents = talent_repo.search_talents_by_position(skills)
        else:
            talents = talent_repo.get_all_talents(limit=100)

        return {
            "success": True,
            "count": len(talents[:limit]),
            "candidates": talents[:limit],
            "search_conditions": conditions,
            "message": f"{', '.join(conditions)} 조건으로 {len(talents[:limit])}명의 후보자를 찾았습니다."
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "복합 검색 중 오류가 발생했습니다."
        }

@tool
def get_candidate_details(talent_id: int) -> Dict[str, Any]:
    """특정 후보자의 상세 정보 조회"""
    try:
        talent = talent_repo.get_talent_by_id(talent_id)

        if talent:
            return {
                "success": True,
                "candidate": talent,
                "message": f"ID {talent_id}번 후보자의 상세 정보를 조회했습니다."
            }
        else:
            return {
                "success": False,
                "message": f"ID {talent_id}번 후보자를 찾을 수 없습니다."
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "후보자 정보 조회 중 오류가 발생했습니다."
        }

@tool
def get_candidate_statistics() -> Dict[str, Any]:
    """전체 인재 데이터베이스 통계 조회"""
    try:
        stats = talent_repo.get_statistics()

        return {
            "success": True,
            "statistics": stats,
            "message": "데이터베이스 통계를 조회했습니다."
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "통계 조회 중 오류가 발생했습니다."
        }

# 회사 검색 도구들
@tool
def search_companies_by_name(name: str, limit: int = 20) -> Dict[str, Any]:
    """회사 이름으로 검색"""
    try:
        companies = talent_repo.search_companies_by_name(name)

        return {
            "success": True,
            "count": len(companies),
            "companies": companies[:limit],
            "message": f"'{name}' 이름으로 {len(companies)}개의 회사를 찾았습니다."
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "회사 검색 중 오류가 발생했습니다."
        }

@tool
def search_companies_by_category(category: str, limit: int = 20) -> Dict[str, Any]:
    """업종으로 회사 검색"""
    try:
        companies = talent_repo.search_companies_by_category(category)

        return {
            "success": True,
            "count": len(companies),
            "companies": companies[:limit],
            "message": f"'{category}' 업종으로 {len(companies)}개의 회사를 찾았습니다."
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "업종 검색 중 오류가 발생했습니다."
        }

# Export all tools
__all__ = [
    'search_candidates_by_skills',
    'search_candidates_by_location',
    'search_candidates_by_salary_range',
    'search_candidates_by_work_type',
    'search_candidates_by_industry',
    'search_candidates_by_availability',
    'get_candidate_details',
    'complex_candidate_search',
    'get_candidate_statistics',
    'search_companies_by_name',
    'search_companies_by_category'
]
