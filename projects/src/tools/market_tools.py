"""비정형 데이터 기반 시장 정보 및 기술 트렌드 도구들 (FAISS Vector DB)"""

from typing import List, Dict, Any, Optional
from langchain_core.tools import tool
from ..vector_store.faiss_store import get_vector_store

# 벡터 스토어 인스턴스
vector_store = get_vector_store()

@tool
def search_tech_information(technology: str, top_k: int = 3) -> List[Dict[str, Any]]:
    """기술 정보 검색 (예: Python, React, AWS)"""
    try:
        results = vector_store.search_by_category(
            query=f"{technology} 기술 특징 사용법 트렌드",
            category="tech_info",
            top_k=top_k
        )

        if not results:
            return {
                "success": False,
                "message": f"'{technology}' 기술에 대한 정보를 찾을 수 없습니다."
            }

        return {
            "success": True,
            "technology": technology,
            "count": len(results),
            "information": results,
            "message": f"'{technology}' 기술에 대한 정보 {len(results)}건을 찾았습니다."
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "기술 정보 검색 중 오류가 발생했습니다."
        }

@tool
def search_market_trends(query: str, top_k: int = 3) -> List[Dict[str, Any]]:
    """시장 트렌드 검색 (예: AI 엔지니어 수요, 원격근무 트렌드)"""
    try:
        results = vector_store.search_by_category(
            query=query,
            category="market_trends",
            top_k=top_k
        )

        if not results:
            return {
                "success": False,
                "message": f"'{query}'에 대한 시장 트렌드 정보를 찾을 수 없습니다."
            }

        return {
            "success": True,
            "query": query,
            "count": len(results),
            "trends": results,
            "message": f"'{query}'에 대한 시장 트렌드 {len(results)}건을 찾았습니다."
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "시장 트렌드 검색 중 오류가 발생했습니다."
        }

@tool
def search_industry_analysis(industry: str, top_k: int = 3) -> List[Dict[str, Any]]:
    """산업 분석 정보 검색 (예: 핀테크, 이커머스, AI)"""
    try:
        results = vector_store.search_by_category(
            query=f"{industry} 산업 전망 동향 분석",
            category="industry_analysis",
            top_k=top_k
        )

        if not results:
            return {
                "success": False,
                "message": f"'{industry}' 산업에 대한 분석 정보를 찾을 수 없습니다."
            }

        return {
            "success": True,
            "industry": industry,
            "count": len(results),
            "analysis": results,
            "message": f"'{industry}' 산업 분석 {len(results)}건을 찾았습니다."
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "산업 분석 검색 중 오류가 발생했습니다."
        }

@tool
def search_salary_information(position: str, top_k: int = 3) -> List[Dict[str, Any]]:
    """급여 정보 검색 (예: AI 엔지니어, 데이터 사이언티스트)"""
    try:
        results = vector_store.search_by_category(
            query=f"{position} 연봉 급여 수준",
            category="salary_info",
            top_k=top_k
        )

        if not results:
            return {
                "success": False,
                "message": f"'{position}' 포지션의 급여 정보를 찾을 수 없습니다."
            }

        return {
            "success": True,
            "position": position,
            "count": len(results),
            "salary_info": results,
            "message": f"'{position}' 포지션의 급여 정보 {len(results)}건을 찾았습니다."
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "급여 정보 검색 중 오류가 발생했습니다."
        }

@tool
def general_knowledge_search(query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """일반 지식 검색 (자연어 질문 가능)"""
    try:
        results = vector_store.search(query=query, top_k=top_k)

        if not results:
            return {
                "success": False,
                "message": f"'{query}'에 대한 정보를 찾을 수 없습니다."
            }

        return {
            "success": True,
            "query": query,
            "count": len(results),
            "results": results,
            "message": f"'{query}'에 대한 정보 {len(results)}건을 찾았습니다."
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "지식 검색 중 오류가 발생했습니다."
        }

@tool
def compare_technologies(tech1: str, tech2: str) -> Dict[str, Any]:
    """두 기술 비교 (예: React vs Vue)"""
    try:
        tech1_info = vector_store.search_by_category(
            query=f"{tech1} 기술 특징",
            category="tech_info",
            top_k=2
        )

        tech2_info = vector_store.search_by_category(
            query=f"{tech2} 기술 특징",
            category="tech_info",
            top_k=2
        )

        return {
            "success": True,
            "comparison": {
                "technology_1": {
                    "name": tech1,
                    "information": tech1_info
                },
                "technology_2": {
                    "name": tech2,
                    "information": tech2_info
                }
            },
            "message": f"{tech1}와 {tech2} 기술 비교 정보입니다."
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "기술 비교 중 오류가 발생했습니다."
        }

@tool
def search_company_information(company_name: str, top_k: int = 5) -> Dict[str, Any]:
    """
    벡터 스토어에서 특정 회사의 정보를 검색하는 도구

    Args:
        company_name: 검색할 회사명
        top_k: 반환할 최대 결과 수

    Returns:
        해당 회사의 정보
    """
    try:
        # 회사명으로 검색
        results = vector_store.search_by_category(
            query=f"{company_name} 회사 정보",
            category="company_info",
            top_k=top_k
        )

        if not results:
            return {
                "success": False,
                "message": f"'{company_name}'에 대한 정보를 찾을 수 없습니다."
            }

        return {
            "success": True,
            "company": company_name,
            "count": len(results),
            "information": results,
            "message": f"'{company_name}'에 대한 정보 {len(results)}건을 찾았습니다."
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "회사 정보 검색 중 오류가 발생했습니다."
        }

@tool
def get_knowledge_base_stats() -> Dict[str, Any]:
    """지식 베이스 통계 정보 조회"""
    try:
        stats = vector_store.get_stats()

        return {
            "success": True,
            "statistics": stats,
            "message": f"지식 베이스에 총 {stats['total_documents']}개의 문서가 있습니다."
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "지식 베이스 통계 조회 중 오류가 발생했습니다."
        }
