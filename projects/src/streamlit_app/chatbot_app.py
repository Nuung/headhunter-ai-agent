"""헤드헌터 AI 챗봇 - 완전한 한글 Streamlit UI"""

import streamlit as st
import sys
import os
from datetime import datetime
import uuid

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(project_root)

from src.agents.react_agent import get_react_agent
from langchain_core.messages import HumanMessage, AIMessage
from src.ui.pdf_parser import parse_pdf_jd, extract_company_name_with_details

# 페이지 설정
st.set_page_config(
    page_title="헤드헌터 AI 어시스턴트",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 커스텀 CSS
st.markdown("""
<style>
/* 메인 컨테이너 */
.main {
    background-color: #f8f9fa;
}

/* 헤더 스타일 */
.main-header {
    font-size: 2.5rem;
    font-weight: 700;
    color: #1e3a8a;
    margin-bottom: 0.5rem;
    text-align: center;
}

.sub-header {
    font-size: 1.1rem;
    color: #64748b;
    text-align: center;
    margin-bottom: 2rem;
}

/* 챗 메시지 스타일 */
.user-message {
    background-color: #3b82f6;
    color: white;
    padding: 1rem;
    border-radius: 1rem;
    margin: 0.5rem 0;
}

.assistant-message {
    background-color: white;
    color: #1e293b;
    padding: 1rem;
    border-radius: 1rem;
    margin: 0.5rem 0;
    border: 1px solid #e2e8f0;
}

/* 사이드바 스타일 */
.sidebar .sidebar-content {
    background-color: #ffffff;
}

/* 버튼 스타일 */
.stButton>button {
    background-color: #3b82f6;
    color: white;
    border-radius: 0.5rem;
    border: none;
    padding: 0.5rem 1rem;
    font-weight: 600;
}

.stButton>button:hover {
    background-color: #2563eb;
}

/* 입력 박스 */
.stTextInput>div>div>input {
    border-radius: 0.5rem;
}

/* 정보 박스 */
.info-box {
    background-color: #eff6ff;
    padding: 1rem;
    border-radius: 0.5rem;
    border-left: 4px solid #3b82f6;
    margin: 1rem 0;
}

/* 통계 카드 */
.stat-card {
    background-color: white;
    padding: 1.5rem;
    border-radius: 0.75rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    text-align: center;
}

.stat-value {
    font-size: 2rem;
    font-weight: 700;
    color: #3b82f6;
}

.stat-label {
    font-size: 0.875rem;
    color: #64748b;
    margin-top: 0.5rem;
}
</style>
""", unsafe_allow_html=True)

# 세션 상태 초기화
if 'thread_id' not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

if 'messages' not in st.session_state:
    st.session_state.messages = []

# JD 관련 세션 상태 추가
if 'jd_text' not in st.session_state:
    st.session_state.jd_text = ""

if 'company_name' not in st.session_state:
    st.session_state.company_name = ""

if 'agent' not in st.session_state:
    with st.spinner('AI 에이전트를 초기화하는 중...'):
        try:
            st.session_state.agent = get_react_agent()
            st.session_state.agent_ready = True
        except Exception as e:
            st.session_state.agent_ready = False
            st.session_state.agent_error = str(e)

# 사이드바
with st.sidebar:
    st.markdown("### 🤖 헤드헌터 AI")
    st.markdown("---")


    # JD 업로드 섹션
    st.markdown("#### 📄 Internal Materials Upload (Optional)")
    uploaded_file = st.file_uploader(
        "PDF 파일을 업로드하세요",
        type=['pdf'],
        help="JD가 포함된 PDF 파일을 업로드하면 회사 정보를 자동으로 추출합니다."
    )
    
    if uploaded_file is not None:
        # PDF 파싱
        with st.spinner("PDF를 분석 중..."):
            try:
                jd_text = parse_pdf_jd(uploaded_file)
                
                if jd_text:
                    st.session_state.jd_text = jd_text
                    
                    # 이미 처리된 파일인지 확인
                    file_hash = hash(uploaded_file.getvalue())
                    if hasattr(st.session_state, 'processed_file_hash') and st.session_state.processed_file_hash == file_hash:
                        st.info("이미 처리된 파일입니다. 회사 정보는 이미 수집되었습니다.")
                    else:
                        # 파일 해시 저장
                        st.session_state.processed_file_hash = file_hash
                    
                    # 회사 이름 추출 및 검증 시도 (Solar API + Tavily)
                    with st.spinner("🤖 Solar API로 회사명을 추출하고 웹 검색으로 검증하는 중..."):
                        company_details = extract_company_name_with_details(jd_text)
                        company_name = company_details.get("company_name")
                        original_name = company_details.get("original_extraction")
                        is_verified = company_details.get("is_verified", False)
                        
                        if company_name and company_name != "알 수 없음":
                            st.session_state.company_name = company_name
                            
                            # 이미 이 회사의 정보가 수집되었는지 확인
                            if hasattr(st.session_state, 'collected_companies') and company_name in st.session_state.collected_companies:
                                st.info(f"'{company_name}'의 회사 정보는 이미 수집되었습니다.")
                            else:
                                # 추출 결과 표시
                                confidence = company_details.get("confidence", "unknown")
                                method = company_details.get("extraction_method", "unknown")
                                verification_method = company_details.get("verification_method", "not_verified")
                                
                                # 신뢰도에 따른 아이콘과 색상
                                if is_verified and confidence == "high":
                                    st.success(f"✅ 회사명 검증 완료: **{company_name}** (웹 검색 검증됨)")
                                    if original_name and original_name != company_name:
                                        st.info(f"📝 원본 추출: {original_name} → 최종 확인: {company_name}")
                                elif confidence == "high":
                                    st.success(f"✅ 회사명 자동 추출: **{company_name}** (신뢰도: 높음)")
                                elif confidence == "medium":
                                    st.info(f"ℹ️ 회사명 자동 추출: **{company_name}** (신뢰도: 보통)")
                                else:
                                    st.warning(f"⚠️ 회사명 자동 추출: **{company_name}** (신뢰도: 낮음)")
                                
                                # 추출 및 검증 방법 표시
                                method_map = {
                                    "explicit": "명시적 추출",
                                    "inferred": "추론적 추출", 
                                    "not_found": "찾을 수 없음",
                                    "web_search_verified": "웹 검색 검증됨",
                                    "web_search_partial": "웹 검색 부분 확인",
                                    "not_verified": "검증되지 않음"
                                }
                                
                                st.caption(f"추출 방법: {method_map.get(method, method)}")
                                if verification_method != "not_verified":
                                    st.caption(f"검증 방법: {method_map.get(verification_method, verification_method)}")
                                
                                # 분석 결과 표시 (있는 경우)
                                if "analysis" in company_details:
                                    with st.expander("🔍 회사명 검증 분석 결과"):
                                        st.text(company_details["analysis"])
                            
                                # 회사 정보 수집 및 벡터화
                                with st.spinner(f"🔍 {company_name} 회사 정보를 수집하고 벡터 DB에 저장하는 중..."):
                                    try:
                                        from src.tools.web_search_tools import search_company_comprehensive_info
                                        from src.vector_store.faiss_store import get_vector_store
                                        
                                        # 검색 키워드 정의
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
                                        
                                        # 진행 상태 표시용 컨테이너
                                        progress_container = st.container()
                                        
                                        # 각 키워드별 검색 진행
                                        all_search_results = []
                                        total_count = 0
                                        
                                        for i, keyword in enumerate(search_keywords):
                                            # 검색 중 상태 표시
                                            with progress_container:
                                                st.info(f"🟢 {keyword}을 검색하는 중...")
                                            
                                            try:
                                                # 개별 키워드 검색
                                                search_params = {
                                                    "query": keyword,
                                                    "max_results": 30,
                                                    "search_depth": "advanced"
                                                }
                                                
                                                from src.tools.web_search_tools import _tavily_search_and_format
                                                search_result = _tavily_search_and_format(search_params)
                                                formatted_results = search_result.get("results", [])
                                                
                                                if formatted_results:
                                                    all_search_results.append({
                                                        "keyword": keyword,
                                                        "results": formatted_results
                                                    })
                                                    total_count += len(formatted_results)
                                                
                                                # 검색 완료 상태 표시
                                                with progress_container:
                                                    st.success(f"🔵 {keyword} 검색 완료 ({len(formatted_results)}건)")
                                                    
                                            except Exception as e:
                                                with progress_container:
                                                    st.error(f"❌ {keyword} 검색 실패: {str(e)}")
                                                continue
                                        
                                        if all_search_results:
                                            # 벡터 스토어에 추가
                                            vector_store = get_vector_store()
                                            vector_store.add_company_info(company_name, all_search_results)
                                            
                                            st.success(f"📚 {company_name} 회사 정보 {total_count}건을 벡터 DB에 저장했습니다.")
                                            
                                            # 수집된 회사 목록에 추가
                                            if not hasattr(st.session_state, 'collected_companies'):
                                                st.session_state.collected_companies = set()
                                            st.session_state.collected_companies.add(company_name)
                                            
                                            # 수집된 정보 미리보기
                                            with st.expander(f"📋 {company_name} 수집 정보 미리보기"):
                                                for result in all_search_results[:3]:  # 처음 3개만 표시
                                                    keyword = result.get('keyword', '')
                                                    results = result.get('results', [])
                                                    st.write(f"**{keyword}**: {len(results)}건")
                                                    for item in results[:1]:  # 각 키워드당 1개만 표시
                                                        st.caption(f"- {item.get('title', '')[:100]}...")
                                        else:
                                            st.warning(f"⚠️ {company_name}에 대한 검색 결과가 없습니다.")
                                        
                                        # 진행 상태 컨테이너 초기화 (모든 메시지 삭제)
                                        progress_container.empty()
                                            
                                    except Exception as e:
                                        st.error(f"❌ 회사 정보 수집 중 오류: {str(e)}")
                            
                        else:
                            st.warning("⚠️ 회사명을 자동으로 추출할 수 없습니다.")
                            if "error" in company_details:
                                st.caption(f"오류: {company_details['error']}")
                            if "verification_error" in company_details:
                                st.caption(f"검증 오류: {company_details['verification_error']}")
                    
                    # JD 미리보기
                    with st.expander("📋 JD 미리보기"):
                        st.text_area("JD 내용", jd_text, height=200, disabled=True)
                else:
                    st.error("❌ PDF 파싱에 실패했습니다.")
                    st.info("💡 **해결 방법:**\n"
                           "- PDF가 텍스트 기반인지 확인하세요\n"
                           "- 이미지로 스캔된 PDF는 OCR이 필요합니다\n"
                           "- 다른 PDF 파일로 시도해보세요\n"
                           "- JD 내용을 직접 입력해보세요")
            except Exception as e:
                st.error(f"❌ PDF 처리 중 오류가 발생했습니다: {str(e)}")
                st.info("💡 **해결 방법:**\n"
                       "- PDF 파일이 손상되지 않았는지 확인하세요\n"
                       "- 파일 크기가 200MB 이하인지 확인하세요\n"
                       "- JD 내용을 직접 입력해보세요")
    
    st.markdown("---")
    
    # JD 텍스트 직접 입력
    st.markdown("#### 📝 Internal Text Upload (Optional)")
    jd_input = st.text_area(
        "JD 내용",
        value=st.session_state.jd_text,
        height=150,
        placeholder="JD 내용을 직접 입력하세요...",
        help="PDF 업로드 대신 JD 내용을 직접 입력할 수 있습니다."
    )
    
    if jd_input != st.session_state.jd_text:
        st.session_state.jd_text = jd_input

    # JD 입력 처리 버튼
    if st.button("📝 입력", use_container_width=True, help="입력한 JD 내용에서 회사명을 추출하고 회사 정보를 수집합니다."):
        if jd_input and jd_input.strip():
            # 이미 처리된 텍스트인지 확인
            text_hash = hash(jd_input.strip())
            if hasattr(st.session_state, 'processed_text_hash') and st.session_state.processed_text_hash == text_hash:
                st.info("이미 처리된 JD 내용입니다. 회사 정보는 이미 수집되었습니다.")
            else:
                # 텍스트 해시 저장
                st.session_state.processed_text_hash = text_hash
                
                # 회사 이름 추출 및 검증 시도 (Solar API + Tavily)
                with st.spinner("🤖 Solar API로 회사명을 추출하고 웹 검색으로 검증하는 중..."):
                    company_details = extract_company_name_with_details(jd_input)
                    company_name = company_details.get("company_name")
                    original_name = company_details.get("original_extraction")
                    is_verified = company_details.get("is_verified", False)
                    
                    if company_name and company_name != "알 수 없음":
                        st.session_state.company_name = company_name
                        
                        # 이미 이 회사의 정보가 수집되었는지 확인
                        if hasattr(st.session_state, 'collected_companies') and company_name in st.session_state.collected_companies:
                            st.info(f"'{company_name}'의 회사 정보는 이미 수집되었습니다.")
                        else:
                            # 추출 결과 표시
                            confidence = company_details.get("confidence", "unknown")
                            method = company_details.get("extraction_method", "unknown")
                            verification_method = company_details.get("verification_method", "not_verified")
                            
                            # 신뢰도에 따른 아이콘과 색상
                            if is_verified and confidence == "high":
                                st.success(f"✅ 회사명 검증 완료: **{company_name}** (웹 검색 검증됨)")
                                if original_name and original_name != company_name:
                                    st.info(f"📝 원본 추출: {original_name} → 최종 확인: {company_name}")
                            elif confidence == "high":
                                st.success(f"✅ 회사명 자동 추출: **{company_name}** (신뢰도: 높음)")
                            elif confidence == "medium":
                                st.info(f"ℹ️ 회사명 자동 추출: **{company_name}** (신뢰도: 보통)")
                            else:
                                st.warning(f"⚠️ 회사명 자동 추출: **{company_name}** (신뢰도: 낮음)")
                            
                            # 추출 및 검증 방법 표시
                            method_map = {
                                "explicit": "명시적 추출",
                                "inferred": "추론적 추출", 
                                "not_found": "찾을 수 없음",
                                "web_search_verified": "웹 검색 검증됨",
                                "web_search_partial": "웹 검색 부분 확인",
                                "not_verified": "검증되지 않음"
                            }
                            
                            st.caption(f"추출 방법: {method_map.get(method, method)}")
                            if verification_method != "not_verified":
                                st.caption(f"검증 방법: {method_map.get(verification_method, verification_method)}")
                            
                            # 분석 결과 표시 (있는 경우)
                            if "analysis" in company_details:
                                with st.expander("🔍 회사명 검증 분석 결과"):
                                    st.text(company_details["analysis"])
                            
                            # 회사 정보 수집 및 벡터화
                            with st.spinner(f"🔍 {company_name} 회사 정보를 수집하고 벡터 DB에 저장하는 중..."):
                                try:
                                    from src.tools.web_search_tools import search_company_comprehensive_info
                                    from src.vector_store.faiss_store import get_vector_store
                                    
                                    # 검색 키워드 정의
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
                                    
                                    # 진행 상태 표시용 컨테이너
                                    progress_container = st.container()
                                    
                                    # 각 키워드별 검색 진행
                                    all_search_results = []
                                    total_count = 0
                                    
                                    for i, keyword in enumerate(search_keywords):
                                        # 검색 중 상태 표시
                                        with progress_container:
                                            st.info(f"🟢 {keyword}을 검색하는 중...")
                                        
                                        try:
                                            # 개별 키워드 검색
                                            search_params = {
                                                "query": keyword,
                                                "max_results": 30,
                                                "search_depth": "advanced"
                                            }
                                            
                                            from src.tools.web_search_tools import _tavily_search_and_format
                                            search_result = _tavily_search_and_format(search_params)
                                            formatted_results = search_result.get("results", [])
                                            
                                            if formatted_results:
                                                all_search_results.append({
                                                    "keyword": keyword,
                                                    "results": formatted_results
                                                })
                                                total_count += len(formatted_results)
                                            
                                            # 검색 완료 상태 표시
                                            with progress_container:
                                                st.success(f"🔵 {keyword} 검색 완료 ({len(formatted_results)}건)")
                                                
                                        except Exception as e:
                                            with progress_container:
                                                st.error(f"❌ {keyword} 검색 실패: {str(e)}")
                                            continue
                                    
                                    if all_search_results:
                                        # 벡터 스토어에 추가
                                        vector_store = get_vector_store()
                                        vector_store.add_company_info(company_name, all_search_results)
                                        
                                        st.success(f"📚 {company_name} 회사 정보 {total_count}건을 벡터 DB에 저장했습니다.")
                                        
                                        # 수집된 회사 목록에 추가
                                        if not hasattr(st.session_state, 'collected_companies'):
                                            st.session_state.collected_companies = set()
                                        st.session_state.collected_companies.add(company_name)
                                        
                                        # 수집된 정보 미리보기
                                        with st.expander(f"📋 {company_name} 수집 정보 미리보기"):
                                            for result in all_search_results[:3]:  # 처음 3개만 표시
                                                keyword = result.get('keyword', '')
                                                results = result.get('results', [])
                                                st.write(f"**{keyword}**: {len(results)}건")
                                                for item in results[:1]:  # 각 키워드당 1개만 표시
                                                    st.caption(f"- {item.get('title', '')[:100]}...")
                                    else:
                                        st.warning(f"⚠️ {company_name}에 대한 검색 결과가 없습니다.")
                                    
                                    # 진행 상태 컨테이너 초기화 (모든 메시지 삭제)
                                    progress_container.empty()
                                        
                                except Exception as e:
                                    st.error(f"❌ 회사 정보 수집 중 오류: {str(e)}")
                    else:
                        st.warning("⚠️ 회사명을 자동으로 추출할 수 없습니다.")
                        if "error" in company_details:
                            st.caption(f"오류: {company_details['error']}")
                        if "verification_error" in company_details:
                            st.caption(f"검증 오류: {company_details['verification_error']}")
        else:
            st.warning("⚠️ JD 내용을 입력해주세요.")

    st.markdown("---")

    # 새 대화 시작
    if st.button("🔄 새 대화 시작", use_container_width=True):
        st.session_state.thread_id = str(uuid.uuid4())
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")

    # 기능 안내
    st.markdown("#### 💡 가능한 질문")
    st.markdown("""
    **인재 검색**
    - Python 개발자 찾아줘
    - 서울 지역 백엔드 개발자
    - 연봉 5000~8000만원 개발자

    **시장 분석**
    - AI 개발자 시장 트렌드
    - 데이터 사이언티스트 평균 연봉
    - React vs Vue.js 비교

    **최신 정보**
    - 2024년 개발자 채용 동향
    - 네이버 채용 공고 찾아줘
    - 스타트업 투자 뉴스
    """)

    st.markdown("---")

    # 사용 가능한 도구
    with st.expander("🛠️ 사용 가능한 도구"):
        st.markdown("""
        **정형 데이터 (PostgreSQL)**
        - 인재 프로필 검색
        - 회사 정보 조회
        - 경험 태그 검색

        **비정형 데이터 (RAG)**
        - 기술 정보 분석
        - 시장 트렌드 연구
        - 급여 정보 조회

        **실시간 데이터 (웹 검색)**
        - 최신 채용 공고
        - 기술 뉴스
        - 회사 정보
        """)

    st.markdown("---")
    st.caption("Powered by LangGraph & Solar LLM")

# 메인 컨텐츠
st.markdown('<div class="main-header">🤖 헤드헌터 AI 어시스턴트</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">인재 검색부터 시장 분석까지, AI가 도와드립니다</div>', unsafe_allow_html=True)

# 에이전트 상태 확인
if not st.session_state.get('agent_ready', False):
    st.error(f"""
    ⚠️ AI 에이전트 초기화에 실패했습니다.

    **오류 내용:**
    {st.session_state.get('agent_error', '알 수 없는 오류')}

    **해결 방법:**
    1. .env 파일에 UPSTAGE_API_KEY가 설정되어 있는지 확인
    2. PostgreSQL 데이터베이스가 실행 중인지 확인
    3. 필요한 패키지가 모두 설치되어 있는지 확인
    """)
    st.stop()

# 환영 메시지 (첫 로드 시)
if len(st.session_state.messages) == 0:
    st.markdown("""
    <div class="info-box">
        <h4>👋 안녕하세요! 헤드헌터 AI 어시스턴트입니다.</h4>
        <p>인재 검색, 시장 분석, 채용 트렌드 등 무엇이든 물어보세요!</p>
        <p><strong>예시:</strong> "Python 개발자 5명 추천해줘" 또는 "AI 개발자 평균 연봉이 궁금해요"</p>
    </div>
    """, unsafe_allow_html=True)

# 채팅 메시지 표시
chat_container = st.container()
with chat_container:
    for message in st.session_state.messages:
        role = message["role"]
        content = message["content"]

        if role == "user":
            with st.chat_message("user", avatar="👤"):
                st.markdown(content)
        else:
            with st.chat_message("assistant", avatar="🤖"):
                st.markdown(content)

# 채팅 입력
if prompt := st.chat_input("메시지를 입력하세요...", key="chat_input"):
    # 사용자 메시지 추가
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 사용자 메시지 표시
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    # AI 응답 생성
    with st.chat_message("assistant", avatar="🤖"):
        message_placeholder = st.empty()
        full_response = ""

        try:
            # 스트리밍 응답
            with st.spinner("생각 중..."):
                for chunk in st.session_state.agent.stream(
                    prompt,
                    thread_id=st.session_state.thread_id
                ):
                    # 마지막 메시지 추출
                    if 'messages' in chunk and len(chunk['messages']) > 0:
                        last_msg = chunk['messages'][-1]

                        # AIMessage만 표시
                        if isinstance(last_msg, AIMessage):
                            full_response = last_msg.content
                            message_placeholder.markdown(full_response + "▌")

            # 최종 응답 표시
            message_placeholder.markdown(full_response)

            # 응답 저장
            st.session_state.messages.append({
                "role": "assistant",
                "content": full_response
            })

        except Exception as e:
            error_message = f"⚠️ 오류가 발생했습니다: {str(e)}"
            message_placeholder.error(error_message)
            st.session_state.messages.append({
                "role": "assistant",
                "content": error_message
            })

# 하단 정보
st.markdown("---")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="stat-card">
        <div class="stat-value">3</div>
        <div class="stat-label">데이터 소스</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="stat-card">
        <div class="stat-value">20+</div>
        <div class="stat-label">AI 도구</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="stat-card">
        <div class="stat-value">24/7</div>
        <div class="stat-label">실시간 지원</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")
st.caption("💡 Tip: 더 구체적인 질문을 하실수록 정확한 답변을 받으실 수 있습니다.")
