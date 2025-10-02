"""
Solar API를 이용한 회사명 추출 모듈
Structured Output을 사용하여 JD에서 회사명을 안정적으로 추출
Tavily 웹 검색을 통한 정확한 사명 검증 기능 포함
"""
import json
import os
import sys
from typing import Optional, Dict, Any

# 프로젝트 루트 경로 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))


class CompanyExtractor:
    """Solar API와 Tavily를 이용한 회사명 추출기"""
    
    def __init__(self):
        # 환경 변수에서 API 키들 가져오기
        from dotenv import load_dotenv
        load_dotenv()
        
        self.solar_api_key = os.getenv("UPSTAGE_API_KEY")
        self.tavily_api_key = os.getenv("TAVILY_API_KEY")
        
    def _get_company_extraction_schema(self) -> Dict[str, Any]:
        """회사명 추출을 위한 JSON 스키마 정의"""
        return {
            "type": "json_schema",
            "json_schema": {
                "name": "company_name_extraction",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "company_name": {
                            "type": "string",
                            "description": "JD에서 추출된 회사명"
                        },
                        "confidence": {
                            "type": "string",
                            "enum": ["high", "medium", "low"],
                            "description": "회사명 추출 신뢰도"
                        },
                        "extraction_method": {
                            "type": "string",
                            "enum": ["explicit", "inferred", "not_found"],
                            "description": "추출 방법: explicit(명시적), inferred(추론), not_found(찾을 수 없음)"
                        }
                    },
                    "required": ["company_name", "confidence", "extraction_method"]
                }
            }
        }
    
    def _create_extraction_prompt(self, jd_text: str) -> str:
        """회사명 추출을 위한 프롬프트 생성"""
        prompt = f"""
다음은 Job Description(JD)에서 텍스트 파싱한 결과입니다.

JD 내용:
{jd_text}

위 JD에서 어떤 회사의 채용공고인지 회사명을 추출해주세요.

추출 가이드라인:
1. 회사명은 정확하고 공식적인 이름을 사용하세요
2. "주식회사", "(주)", "Co., Ltd." 등의 법인 형태는 포함하지 마세요
3. 브랜드명이 회사명과 다른 경우 회사명을 우선하세요
4. 여러 회사가 언급된 경우 채용하는 회사(모집주체)를 찾아주세요
5. 회사명을 찾을 수 없는 경우 "알 수 없음"으로 표시하세요

예시:
- "네이버(주)에서 백엔드 개발자를 모집합니다" → "네이버"
- "카카오페이에서 프론트엔드 개발자를 찾습니다" → "카카오페이"
- "토스에서 풀스택 개발자를 채용합니다" → "토스"
"""
        return prompt.strip()
    
    def extract_company_name(self, jd_text: str) -> Dict[str, str]:
        """
        JD 텍스트에서 회사명 추출
        
        Args:
            jd_text: Job Description 텍스트
            
        Returns:
            Dict containing company_name, confidence, extraction_method
        """
        try:
            # Solar API 설정 확인
            if not self.solar_api_key:
                return {
                    "company_name": "알 수 없음",
                    "confidence": "low", 
                    "extraction_method": "not_found",
                    "error": "Solar API 키가 설정되지 않았습니다"
                }
            
            # 프롬프트 생성
            prompt = self._create_extraction_prompt(jd_text)
            
            # Solar API 호출을 위한 메시지 구성
            messages = [
                {
                    "role": "system",
                    "content": "당신은 Job Description에서 회사명을 정확하게 추출하는 전문가입니다. 주어진 JD를 분석하여 회사명을 찾아주세요."
                },
                {
                    "role": "user", 
                    "content": prompt
                }
            ]
            
            # Solar API 호출
            import requests
            
            headers = {
                "Authorization": f"Bearer {self.solar_api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "solar-1-mini-chat",
                "messages": messages,
                "response_format": self._get_company_extraction_schema(),
                "temperature": 0.1,  # 일관된 결과를 위해 낮은 temperature 사용
                "max_tokens": 200
            }
            
            response = requests.post(
                "https://api.upstage.ai/v1/solar/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if "choices" in result and len(result["choices"]) > 0:
                    content = result["choices"][0]["message"]["content"]
                    
                    try:
                        # JSON 파싱
                        extracted_data = json.loads(content)
                        return extracted_data
                    except json.JSONDecodeError as e:
                        return {
                            "company_name": "알 수 없음",
                            "confidence": "low",
                            "extraction_method": "not_found", 
                            "error": f"JSON 파싱 실패: {e}"
                        }
                else:
                    return {
                        "company_name": "알 수 없음",
                        "confidence": "low",
                        "extraction_method": "not_found",
                        "error": "API 응답에서 결과를 찾을 수 없습니다"
                    }
            else:
                return {
                    "company_name": "알 수 없음", 
                    "confidence": "low",
                    "extraction_method": "not_found",
                    "error": f"Solar API 호출 실패: {response.status_code} - {response.text}"
                }
                
        except Exception as e:
            return {
                "company_name": "알 수 없음",
                "confidence": "low", 
                "extraction_method": "not_found",
                "error": f"회사명 추출 중 오류 발생: {str(e)}"
            }
    
    def _search_company_official_name(self, company_name: str) -> Dict[str, Any]:
        """
        Tavily를 사용하여 회사명의 정확한 사명을 검색
        
        Args:
            company_name: 검색할 회사명
            
        Returns:
            검색 결과 딕셔너리
        """
        if not self.tavily_api_key:
            return {
                "official_name": company_name,
                "confidence": "low",
                "search_method": "not_available",
                "error": "Tavily API 키가 설정되지 않았습니다"
            }
        
        try:
            from tavily import TavilyClient
            
            client = TavilyClient(api_key=self.tavily_api_key)
            
            # 회사명 검색 쿼리 구성
            search_query = f"{company_name} 정확한 사명 공식명칭 회사명"
            
            # 웹 검색 실행
            search_response = client.search(
                query=search_query,
                search_depth="basic",
                max_results=3
            )
            
            # Solar API로 검색 결과 분석
            if search_response and "results" in search_response:
                results_text = "\n".join([
                    f"제목: {result.get('title', '')}\n내용: {result.get('content', '')}\n"
                    for result in search_response["results"][:3]
                ])
                
                # Solar API로 정확한 사명 추출
                analysis_result = self._analyze_search_results_with_solar(
                    company_name, results_text
                )
                
                return analysis_result
            else:
                return {
                    "official_name": company_name,
                    "confidence": "low",
                    "search_method": "search_failed",
                    "error": "웹 검색 결과를 찾을 수 없습니다"
                }
                
        except Exception as e:
            return {
                "official_name": company_name,
                "confidence": "low",
                "search_method": "error",
                "error": f"웹 검색 중 오류 발생: {str(e)}"
            }
    
    def _analyze_search_results_with_solar(self, company_name: str, search_results: str) -> Dict[str, Any]:
        """
        Solar API를 사용하여 검색 결과에서 정확한 사명 분석
        
        Args:
            company_name: 원본 회사명
            search_results: 웹 검색 결과 텍스트
            
        Returns:
            분석 결과 딕셔너리
        """
        try:
            if not self.solar_api_key:
                return {
                    "official_name": company_name,
                    "confidence": "low",
                    "search_method": "solar_unavailable",
                    "error": "Solar API 키가 설정되지 않았습니다"
                }
            
            # Solar API 분석 프롬프트
            prompt = f"""
다음은 "{company_name}" 회사에 대한 웹 검색 결과입니다.

검색 결과:
{search_results}

위 검색 결과를 분석하여 "{company_name}"의 정확한 공식 사명(법인명)을 찾아주세요.

분석 가이드라인:
1. 브랜드명이 아닌 정확한 법인명을 찾아주세요
2. "주식회사", "(주)", "Co., Ltd." 등의 법인 형태를 포함한 완전한 사명을 찾아주세요
3. 여러 사명이 있는 경우 가장 정확하고 공식적인 것을 선택해주세요
4. 확실하지 않은 경우 원본 회사명을 그대로 사용해주세요

예시:
- "토스" → "비바리퍼블리카(주)"
- "카카오페이" → "카카오페이(주)"
- "네이버" → "네이버(주)"
"""
            
            messages = [
                {
                    "role": "system",
                    "content": "당신은 웹 검색 결과를 분석하여 회사의 정확한 사명을 찾는 전문가입니다."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
            
            import requests
            
            headers = {
                "Authorization": f"Bearer {self.solar_api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "solar-1-mini-chat",
                "messages": messages,
                "temperature": 0.1,
                "max_tokens": 200
            }
            
            response = requests.post(
                "https://api.upstage.ai/v1/solar/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if "choices" in result and len(result["choices"]) > 0:
                    content = result["choices"][0]["message"]["content"]
                    
                    # 간단한 추출 로직 (정규식 사용)
                    import re
                    
                    # 괄호 안의 법인 형태 찾기
                    official_pattern = r'([가-힣A-Za-z0-9\s&]+(?:주식회사|\(주\)|Co\. Ltd\.|Corp|Inc|Ltd))'
                    match = re.search(official_pattern, content)
                    
                    if match:
                        official_name = match.group(1).strip()
                        return {
                            "official_name": official_name,
                            "confidence": "high",
                            "search_method": "web_search_verified",
                            "original_name": company_name,
                            "analysis": content
                        }
                    else:
                        # 괄호 없는 경우 원본 사용
                        return {
                            "official_name": company_name,
                            "confidence": "medium",
                            "search_method": "web_search_partial",
                            "original_name": company_name,
                            "analysis": content
                        }
                else:
                    return {
                        "official_name": company_name,
                        "confidence": "low",
                        "search_method": "solar_failed",
                        "error": "Solar API 응답을 처리할 수 없습니다"
                    }
            else:
                return {
                    "official_name": company_name,
                    "confidence": "low",
                    "search_method": "solar_error",
                    "error": f"Solar API 호출 실패: {response.status_code}"
                }
                
        except Exception as e:
            return {
                "official_name": company_name,
                "confidence": "low",
                "search_method": "error",
                "error": f"분석 중 오류 발생: {str(e)}"
            }

    def extract_company_name_with_verification(self, jd_text: str) -> Dict[str, Any]:
        """
        JD에서 회사명을 추출하고 웹 검색으로 정확한 사명을 검증
        
        Args:
            jd_text: Job Description 텍스트
            
        Returns:
            최종 회사명 검증 결과
        """
        # 1단계: Solar API로 기본 회사명 추출
        initial_result = self.extract_company_name(jd_text)
        
        if "error" in initial_result or not initial_result.get("company_name"):
            return initial_result
        
        company_name = initial_result["company_name"]
        
        # "알 수 없음"인 경우 웹 검색하지 않음
        if company_name == "알 수 없음":
            return initial_result
        
        # 2단계: Tavily로 정확한 사명 검색
        verification_result = self._search_company_official_name(company_name)
        
        # 결과 통합
        final_result = {
            "company_name": verification_result.get("official_name", company_name),
            "original_extraction": company_name,
            "confidence": verification_result.get("confidence", initial_result.get("confidence", "low")),
            "extraction_method": initial_result.get("extraction_method", "unknown"),
            "verification_method": verification_result.get("search_method", "not_verified"),
            "is_verified": verification_result.get("search_method") == "web_search_verified"
        }
        
        # 추가 정보
        if "analysis" in verification_result:
            final_result["analysis"] = verification_result["analysis"]
        
        if "error" in verification_result:
            final_result["verification_error"] = verification_result["error"]
        
        return final_result

    def extract_company_name_simple(self, jd_text: str) -> str:
        """
        간단한 회사명 추출 (문자열만 반환)
        
        Args:
            jd_text: Job Description 텍스트
            
        Returns:
            추출된 회사명 문자열
        """
        result = self.extract_company_name(jd_text)
        return result.get("company_name", "알 수 없음")


# 테스트용 함수
def test_company_extractor():
    """회사명 추출기 테스트"""
    extractor = CompanyExtractor()
    
    # 테스트 JD 텍스트들
    test_cases = [
        "네이버(주)에서 백엔드 개발자를 모집합니다. 5년 이상의 경험을 가진 개발자를 찾고 있습니다.",
        "카카오페이에서 프론트엔드 개발자를 채용합니다. React, Vue.js 경험이 필요합니다.",
        "토스에서 풀스택 개발자를 찾습니다. TypeScript와 Node.js를 다룰 수 있는 분을 원합니다.",
        "당근마켓에서 iOS 개발자를 모집합니다. Swift와 UIKit 경험이 필요합니다.",
        "컴퓨터 프로그래머를 모집합니다. Java와 Python 경험이 필요합니다."  # 회사명 없는 케이스
    ]
    
    print("=== 회사명 추출 테스트 ===")
    for i, jd_text in enumerate(test_cases, 1):
        print(f"\n테스트 케이스 {i}:")
        print(f"JD: {jd_text}")
        
        result = extractor.extract_company_name(jd_text)
        print(f"결과: {result}")
        
        simple_result = extractor.extract_company_name_simple(jd_text)
        print(f"간단 결과: {simple_result}")


if __name__ == "__main__":
    test_company_extractor()
