"""
PDF JD 파싱 유틸리티
Solar API를 이용한 회사명 추출 기능 포함
"""
import PyPDF2
import io
import os
import sys
from typing import Optional, Dict, Any

# 프로젝트 루트 경로 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

def parse_pdf_jd(pdf_file) -> Optional[str]:
    """
    PDF 파일에서 JD 텍스트를 추출합니다.
    
    Args:
        pdf_file: Streamlit file uploader로 받은 PDF 파일
        
    Returns:
        추출된 텍스트 또는 None
    """
    try:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_file.read()))
        text = ""
        
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        
        return text.strip()
    except Exception as e:
        print(f"PDF 파싱 오류: {e}")
        return None

def extract_company_name_from_jd(jd_text: str, use_solar_api: bool = True) -> Optional[str]:
    """
    JD 텍스트에서 회사 이름을 추출합니다.
    
    Args:
        jd_text: JD 텍스트
        use_solar_api: Solar API 사용 여부 (기본값: True)
        
    Returns:
        추출된 회사 이름 또는 None
    """
    if use_solar_api:
        try:
            from ..services.company_extractor import CompanyExtractor
            extractor = CompanyExtractor()
            result = extractor.extract_company_name_simple(jd_text)
            
            # "알 수 없음"이 아닌 경우에만 반환
            if result and result != "알 수 없음":
                return result
        except Exception as e:
            print(f"Solar API 회사명 추출 실패, 정규식으로 대체: {e}")
    
    # Solar API 실패 시 정규식 패턴으로 대체
    import re
    
    # 일반적인 회사 이름 패턴들
    patterns = [
        r'회사[:\s]*([가-힣A-Za-z0-9\s&]+)',
        r'Company[:\s]*([가-힣A-Za-z0-9\s&]+)',
        r'([가-힣A-Za-z]+(?:주식회사|㈜|\(주\)|Corp|Inc|Ltd))',
        r'([A-Za-z]+(?:Corporation|Corp|Inc|Ltd|Company))'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, jd_text, re.IGNORECASE)
        if match:
            company_name = match.group(1).strip()
            # 너무 긴 경우 제한
            if len(company_name) <= 50:
                return company_name
    
    return None


def extract_company_name_with_details(jd_text: str) -> Dict[str, Any]:
    """
    JD 텍스트에서 회사명과 추가 정보를 추출합니다.
    
    Args:
        jd_text: JD 텍스트
        
    Returns:
        회사명 추출 결과 딕셔너리
    """
    try:
        from ..services.company_extractor import CompanyExtractor
        extractor = CompanyExtractor()
        result = extractor.extract_company_name_with_verification(jd_text)
        return result
    except Exception as e:
        return {
            "company_name": None,
            "confidence": "low",
            "extraction_method": "not_found",
            "error": f"회사명 추출 실패: {e}"
        }