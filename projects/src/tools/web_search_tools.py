"""외부 웹 검색 도구들 (Tavily)

이 모듈은 Tavily API를 활용한 채용/개발자 트렌드 검색 도구를 제공합니다.
LangChain의 @tool 데코레이터를 사용하여 LLM 에이전트가 활용할 수 있는
구조화된 도구로 구현되었습니다.
"""

import os
from typing import List, Dict, Any, Optional
from langchain_core.tools import tool
from tavily import TavilyClient
from dotenv import load_dotenv

load_dotenv()

# Tavily 클라이언트 초기화
tavily_client = TavilyClient(api_key=os.getenv('TAVILY_API_KEY'))

def _tavily_search_and_format(search_params: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Tavily 검색을 수행하고 결과를 공통 형식으로 포맷합니다."""
    results = tavily_client.search(**search_params)
    
    formatted_results = []
    for result in results.get("results", []):
        item = {
            "title": result.get('title', ''),
            "content": result.get('content', ''),
            "url": result.get('url', ''),
            "score": result.get('score', 0)
        }
        # published_date가 있는 경우에만 추가
        if published_date := result.get('published_date'):
            item['published_date'] = published_date
        formatted_results.append(item)

    # 'answer' 키가 있는 경우 결과에 포함
    if 'answer' in results and results['answer']:
        return {"answer": results['answer'], "results": formatted_results}
        
    return {"results": formatted_results}

@tool(parse_docstring=True)
def web_search_latest_trends(
    query: str, 
    max_results: int = 3, 
    include_domains: Optional[List[str]] = None
) -> Dict[str, Any]:
    """최신 채용 및 개발자 트렌드를 웹에서 검색합니다.

    이 도구는 Tavily의 고급 검색 기능을 사용하여 최신 기술 트렌드, 
    채용 동향, 개발자 시장 정보를 찾습니다. 검색 결과는 관련성 점수와 
    함께 제공되며, AI가 생성한 요약 답변도 포함됩니다.
    
    사용 시점: 최신 기술 트렌드나 개발자 채용 시장 동향을 파악할 때, 
    특정 기술 스택이나 직무의 최신 정보가 필요할 때, 
    산업 전반의 개발자 관련 뉴스를 검색할 때 사용합니다.

    Args:
        query: 검색할 키워드 또는 질문. 예: "2024 AI 개발자 트렌드"
        max_results: 반환할 최대 검색 결과 수. 기본값 3, 권장 범위 1-5
        include_domains: 검색을 특정 도메인으로 제한. None이면 모든 도메인 검색

    Returns:
        검색 결과 딕셔너리. success(bool), query(str), count(int), 
        results(List[Dict]), answer(str), message(str) 키를 포함.
        각 result는 title, content, url, score, published_date 포함.

    Raises:
        Exception: Tavily API 호출 실패 시

    Examples:
        >>> result = web_search_latest_trends("AI 개발자 연봉 트렌드 2024")
        >>> print(result['answer'])
        >>> for item in result['results']:
        ...     print(f"{item['title']}: {item['url']}")
    """
    try:
        search_params = {
            "query": query,
            "max_results": max_results,
            "search_depth": "advanced",
            "include_answer": True
        }

        if include_domains:
            search_params["include_domains"] = include_domains

        search_result = _tavily_search_and_format(search_params)
        formatted_results = search_result.get("results", [])
        answer = search_result.get("answer", "")

        return {
            "success": True,
            "query": query,
            "count": len(formatted_results),
            "results": formatted_results,
            "answer": answer,
            "message": f"'{query}'에 대한 최신 웹 검색 결과 {len(formatted_results)}건을 찾았습니다."
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "웹 검색 중 오류가 발생했습니다."
        }

@tool(parse_docstring=True)
def search_job_postings(
    position: str, 
    location: str = "한국", 
    max_results: int = 5
) -> Dict[str, Any]:
    """특정 포지션의 채용공고를 검색합니다.

    한국 주요 채용 플랫폼(사람인, 잡코리아, 원티드, 프로그래머스)에서
    개발자 채용공고를 검색합니다. 포지션명과 지역을 기반으로 최신 
    채용 정보를 수집합니다.
    
    사용 시점: 특정 개발 포지션의 채용 공고를 찾을 때, 
    지역별 채용 시장 현황을 파악할 때, 
    실제 채용 중인 회사 정보를 확인할 때 사용합니다.

    Args:
        position: 검색할 직무. 예: "백엔드 개발자", "프론트엔드 개발자"
        location: 검색할 지역. 기본값 "한국"
        max_results: 반환할 최대 채용공고 수. 기본값 5, 권장 범위 3-10

    Returns:
        채용공고 검색 결과 딕셔너리. success(bool), position(str), 
        location(str), count(int), job_postings(List[Dict]), message(str) 포함.
        각 job_posting은 title, content, url, score 포함.

    Raises:
        Exception: 채용공고 검색 실패 시

    Examples:
        >>> postings = search_job_postings("풀스택 개발자", "서울")
        >>> for job in postings['job_postings']:
        ...     print(f"{job['title']}: {job['url']}")
    """
    try:
        query = f"{position} 채용 {location} 개발자 채용공고"

        search_params = {
            "query": query,
            "max_results": max_results,
            "search_depth": "advanced",
            "include_domains": ["saramin.co.kr", "jobkorea.co.kr", "wanted.co.kr", "programmers.co.kr"]
        }
        search_result = _tavily_search_and_format(search_params)
        formatted_results = search_result.get("results", [])

        return {
            "success": True,
            "position": position,
            "location": location,
            "count": len(formatted_results),
            "job_postings": formatted_results,
            "message": f"{location}의 '{position}' 채용공고 {len(formatted_results)}건을 찾았습니다."
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "채용공고 검색 중 오류가 발생했습니다."
        }

@tool(parse_docstring=True)
def search_company_information(
    company_name: str, 
    max_results: int = 3
) -> Dict[str, Any]:
    """특정 회사의 정보를 검색합니다.

    회사의 일반 정보, 채용 현황, 복리후생, 개발 문화 등을 검색합니다.
    스타트업부터 대기업까지 다양한 회사의 정보를 수집할 수 있습니다.
    
    사용 시점: 입사를 고려하는 회사에 대한 정보가 필요할 때, 
    회사의 개발 문화나 기술 스택을 파악할 때, 
    복리후생이나 근무 환경 정보를 찾을 때, 
    회사의 최근 소식이나 투자 현황을 알아볼 때 사용합니다.

    Args:
        company_name: 검색할 회사명. 예: "카카오", "네이버", "토스"
        max_results: 반환할 최대 검색 결과 수. 기본값 3, 권장 범위 2-5

    Returns:
        회사 정보 검색 결과 딕셔너리. success(bool), company(str), 
        count(int), company_info(List[Dict]), message(str) 포함.
        각 company_info는 title, content, url, score 포함.

    Raises:
        Exception: 회사 정보 검색 실패 시

    Examples:
        >>> info = search_company_information("토스")
        >>> for item in info['company_info']:
        ...     print(f"{item['title']}: {item['url']}")
    """
    try:
        query = f"{company_name} 회사 정보 채용 개발자 복리후생"

        search_params = {
            "query": query,
            "max_results": max_results,
            "search_depth": "advanced"
        }
        search_result = _tavily_search_and_format(search_params)
        formatted_results = search_result.get("results", [])

        return {
            "success": True,
            "company": company_name,
            "count": len(formatted_results),
            "company_info": formatted_results,
            "message": f"'{company_name}' 회사 정보 {len(formatted_results)}건을 찾았습니다."
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "회사 정보 검색 중 오류가 발생했습니다."
        }

@tool(parse_docstring=True)
def search_salary_benchmarks(
    position: str, 
    location: str = "한국", 
    max_results: int = 3
) -> Dict[str, Any]:
    """특정 포지션의 급여 벤치마크 정보를 검색합니다.

    개발자 포지션의 평균 연봉, 경력별 급여 수준, 연봉 협상 팁 등을 
    검색합니다. 최신 연봉 데이터를 기반으로 현실적인 급여 정보를 제공합니다.
    
    사용 시점: 특정 포지션의 시장 급여 수준을 파악할 때, 
    연봉 협상을 준비할 때, 
    경력별 급여 성장 곡선을 이해할 때, 
    다른 지역과의 급여 차이를 비교할 때 사용합니다.

    Args:
        position: 급여 정보를 검색할 직무. 예: "시니어 백엔드 개발자"
        location: 검색할 지역. 기본값 "한국"
        max_results: 반환할 최대 검색 결과 수. 기본값 3, 권장 범위 2-5

    Returns:
        급여 정보 검색 결과 딕셔너리. success(bool), position(str), 
        location(str), count(int), salary_benchmarks(List[Dict]), message(str) 포함.
        각 salary_benchmark는 title, content, url, score 포함.

    Raises:
        Exception: 급여 정보 검색 실패 시

    Examples:
        >>> salary = search_salary_benchmarks("백엔드 개발자 5년차")
        >>> for info in salary['salary_benchmarks']:
        ...     print(f"{info['title']}: {info['content']}")
    """
    try:
        query = f"{position} 연봉 급여 {location} 2024"

        search_params = {
            "query": query,
            "max_results": max_results,
            "search_depth": "advanced"
        }
        search_result = _tavily_search_and_format(search_params)
        formatted_results = search_result.get("results", [])

        return {
            "success": True,
            "position": position,
            "location": location,
            "count": len(formatted_results),
            "salary_benchmarks": formatted_results,
            "message": f"{location}의 '{position}' 급여 정보 {len(formatted_results)}건을 찾았습니다."
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "급여 벤치마크 검색 중 오류가 발생했습니다."
        }

@tool(parse_docstring=True)
def search_tech_news(
    technology: str, 
    max_results: int = 3
) -> Dict[str, Any]:
    """특정 기술에 관한 최신 뉴스와 트렌드를 검색합니다.

    기술 관련 뉴스, 업데이트, 트렌드, 커뮤니티 반응 등을 주요 IT 미디어에서
    검색합니다. 기술 선택이나 학습 방향 결정에 도움이 되는 정보를 제공합니다.
    
    사용 시점: 새로운 기술을 학습하기 전에 최신 동향을 파악할 때, 
    기술 스택 선택을 위한 정보가 필요할 때, 
    특정 기술의 산업 채택 현황을 알아볼 때, 
    최신 버전이나 중요 업데이트 정보를 확인할 때 사용합니다.

    Args:
        technology: 검색할 기술명. 예: "React", "Python 3.12", "Kubernetes"
        max_results: 반환할 최대 뉴스 수. 기본값 3, 권장 범위 2-5

    Returns:
        기술 뉴스 검색 결과 딕셔너리. success(bool), technology(str), 
        count(int), tech_news(List[Dict]), message(str) 포함.
        각 tech_news는 title, content, url, score, published_date 포함.

    Raises:
        Exception: 기술 뉴스 검색 실패 시

    Examples:
        >>> news = search_tech_news("React 19")
        >>> for article in news['tech_news']:
        ...     print(f"{article['title']}: {article['url']}")
    """
    try:
        query = f"{technology} 기술 뉴스 트렌드 2024"

        search_params = {
            "query": query,
            "max_results": max_results,
            "search_depth": "advanced",
            "include_domains": ["techcrunch.com", "zdnet.co.kr", "bloter.net", "itworld.co.kr"]
        }
        search_result = _tavily_search_and_format(search_params)
        formatted_results = search_result.get("results", [])

        return {
            "success": True,
            "technology": technology,
            "count": len(formatted_results),
            "tech_news": formatted_results,
            "message": f"'{technology}' 관련 최신 뉴스 {len(formatted_results)}건을 찾았습니다."
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "기술 뉴스 검색 중 오류가 발생했습니다."
        }

@tool(parse_docstring=True)
def search_company_comprehensive_info(
    company_name: str,
    max_results_per_keyword: int = 3
) -> Dict[str, Any]:
    """특정 회사에 대한 포괄적인 정보를 다양한 키워드로 검색합니다.

    회사의 역사, 채용 후기, 기술 스택, 복리후생, 뉴스 등 다양한 관점에서
    정보를 수집하여 벡터 스토어에 저장할 수 있는 형태로 제공합니다.
    
    사용 시점: JD에서 회사명을 추출한 후 해당 회사의 상세 정보를 수집할 때,
    회사별 맞춤형 정보를 벡터 DB에 저장할 때,
    채용 상담 시 회사에 대한 종합적인 정보가 필요할 때 사용합니다.

    Args:
        company_name: 검색할 회사명. 예: "비바리퍼블리카", "토스", "카카오"
        max_results_per_keyword: 키워드당 최대 검색 결과 수. 기본값 3

    Returns:
        회사 정보 검색 결과 딕셔너리. success(bool), company(str), 
        total_count(int), search_results(List[Dict]), message(str) 포함.
        각 search_result는 keyword, results(List[Dict]) 포함.

    Raises:
        Exception: 회사 정보 검색 실패 시

    Examples:
        >>> info = search_company_comprehensive_info("비바리퍼블리카")
        >>> for result in info['search_results']:
        ...     print(f"{result['keyword']}: {len(result['results'])}건")
    """
    try:
        # 회사별 검색 키워드 정의
        search_keywords = [
            f"{company_name} 회사 역사",
            f"{company_name} 회사 소개", 
            f"{company_name} 채용 후기",
            f"{company_name} 직원 인터뷰",
            f"{company_name} 기술 스택",
            f"{company_name} 개발 환경",
            f"{company_name} 복리후생",
            f"{company_name} 연봉",
            f"{company_name} 뉴스",
            f"{company_name} 보도자료"
        ]
        
        all_search_results = []
        total_count = 0
        
        for keyword in search_keywords:
            try:
                search_params = {
                    "query": keyword,
                    "max_results": max_results_per_keyword,
                    "search_depth": "advanced"
                }
                
                search_result = _tavily_search_and_format(search_params)
                formatted_results = search_result.get("results", [])
                
                if formatted_results:
                    all_search_results.append({
                        "keyword": keyword,
                        "results": formatted_results
                    })
                    total_count += len(formatted_results)
                    
            except Exception as e:
                print(f"키워드 '{keyword}' 검색 실패: {e}")
                continue
        
        return {
            "success": True,
            "company": company_name,
            "total_count": total_count,
            "search_results": all_search_results,
            "message": f"'{company_name}'에 대한 포괄적인 정보 {total_count}건을 수집했습니다."
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "회사 포괄 정보 검색 중 오류가 발생했습니다."
        }

@tool(parse_docstring=True)
def search_startup_funding_news(
    max_results: int = 3
) -> Dict[str, Any]:
    """스타트업의 투자 및 채용 관련 최신 뉴스를 검색합니다.

    스타트업 투자 유치 소식, 신규 채용 공고, 조직 확장 계획 등을 검색합니다.
    성장하는 스타트업에서 기회를 찾거나 산업 트렌드를 파악하는데 유용합니다.
    
    사용 시점: 투자를 받은 유망 스타트업을 찾을 때, 
    빠르게 성장하는 회사의 채용 기회를 발견할 때, 
    스타트업 생태계의 전반적인 동향을 파악할 때, 
    새로운 비즈니스 모델이나 기술을 가진 회사를 알아볼 때 사용합니다.

    Args:
        max_results: 반환할 최대 뉴스 수. 기본값 3, 권장 범위 3-7

    Returns:
        스타트업 뉴스 검색 결과 딕셔너리. success(bool), count(int), 
        startup_news(List[Dict]), message(str) 포함.
        각 startup_news는 title, content, url, score, published_date 포함.

    Raises:
        Exception: 스타트업 뉴스 검색 실패 시

    Examples:
        >>> news = search_startup_funding_news()
        >>> for article in news['startup_news']:
        ...     print(f"{article['title']}: {article['url']}")
    """
    try:
        query = "스타트업 투자 채용 개발자 2024"

        search_params = {
            "query": query,
            "max_results": max_results,
            "search_depth": "advanced"
        }
        search_result = _tavily_search_and_format(search_params)
        formatted_results = search_result.get("results", [])

        return {
            "success": True,
            "count": len(formatted_results),
            "startup_news": formatted_results,
            "message": f"스타트업 투자/채용 뉴스 {len(formatted_results)}건을 찾았습니다."
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "스타트업 뉴스 검색 중 오류가 발생했습니다."
        }