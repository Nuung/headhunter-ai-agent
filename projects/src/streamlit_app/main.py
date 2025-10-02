"""Headhunter AI Agent - Streamlit App"""

import streamlit as st
import pandas as pd
import sys
import os

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(project_root)

from src.database.repositories import get_talent_repository

# Page config
st.set_page_config(
    page_title="Headhunter AI Agent",
    page_icon="briefcase",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Minimal CSS
st.markdown("""
<style>
.main-header {
    font-size: 2.5rem;
    font-weight: 600;
    color: #1a1a1a;
    margin-bottom: 1rem;
}
.metric-card {
    background-color: #f8f9fa;
    padding: 1.5rem;
    border-radius: 8px;
    border: 1px solid #e9ecef;
}
.search-result {
    padding: 1rem;
    margin: 0.5rem 0;
    border-radius: 6px;
    border-left: 3px solid #0066cc;
    background-color: #f8f9fa;
}
</style>
""", unsafe_allow_html=True)

# Initialize repository
@st.cache_resource
def get_repository():
    return get_talent_repository()

repo = get_repository()

# Header
st.markdown('<div class="main-header">Headhunter AI Agent</div>', unsafe_allow_html=True)
st.markdown("---")

# Sidebar
with st.sidebar:
    st.header("Navigation")
    page = st.radio(
        "Select Page",
        ["🤖 AI 챗봇", "Dashboard", "Talent Search", "Company Search", "Statistics"],
        label_visibility="collapsed"
    )

    st.markdown("---")
    st.caption("Powered by LangGraph & PostgreSQL")

# AI Chat Page - Redirect to chatbot_app.py
if page == "🤖 AI 챗봇":
    st.info("💡 완전한 AI 챗봇 경험을 위해 별도 페이지를 사용하세요!")
    st.markdown("""
    ## 🚀 AI 챗봇 실행 방법

    터미널에서 다음 명령어를 실행하세요:

    ```bash
    streamlit run src/streamlit_app/chatbot_app.py
    ```

    또는 Python으로:

    ```bash
    python -m streamlit run src/streamlit_app/chatbot_app.py
    ```

    ### ✨ AI 챗봇 기능
    - ✅ ReAct 에이전트 (추론 + 행동)
    - ✅ 3가지 데이터 소스 통합 (PostgreSQL + RAG + 웹검색)
    - ✅ 스트리밍 응답
    - ✅ 대화 히스토리 & 메모리
    - ✅ 20+ AI 도구
    - ✅ 한글 최적화 UI
    """)

    st.warning("⚠️ 현재 페이지는 기본 UI입니다. 완전한 AI 기능을 위해 chatbot_app.py를 사용하세요.")

# Dashboard Page
elif page == "Dashboard":
    st.header("Dashboard")

    # Get statistics
    stats = repo.get_statistics()

    if 'error' not in stats:
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Talents", f"{stats['total_talents']:,}")
        with col2:
            st.metric("Total Companies", f"{stats['total_companies']:,}")
        with col3:
            st.metric("Experience Tags", f"{stats['total_exp_tags']:,}")
        with col4:
            st.metric("External Data", f"{stats['total_external_data']:,}")
    else:
        st.error(f"Database connection error: {stats.get('error')}")
        st.info("Please check your PostgreSQL connection and ensure data is imported")

# Talent Search Page
elif page == "Talent Search":
    st.header("Talent Search")

    col1, col2 = st.columns([2, 1])

    with col1:
        search_type = st.radio("Search By", ["Name", "Position"], horizontal=True)

    with col2:
        limit = st.selectbox("Results Limit", [10, 20, 50, 100], index=1)

    search_query = st.text_input("Search Query", placeholder=f"Enter {search_type.lower()} to search...")

    if st.button("Search", type="primary"):
        if search_query:
            with st.spinner("Searching..."):
                if search_type == "Name":
                    results = repo.search_talents_by_name(search_query)
                else:
                    results = repo.search_talents_by_position(search_query)

                if results:
                    st.success(f"Found {len(results)} results")

                    for talent in results[:limit]:
                        with st.container():
                            st.markdown(f"""
                            <div class="search-result">
                                <h4>{talent['name']}</h4>
                                <p><strong>Position:</strong> {talent['positions'] or 'N/A'}</p>
                                <p><strong>Summary:</strong> {talent['summary'][:200] if talent['summary'] else 'No summary available'}...</p>
                                <p><small>ID: {talent['id']}</small></p>
                            </div>
                            """, unsafe_allow_html=True)
                else:
                    st.warning("No results found")
        else:
            st.warning("Please enter a search query")

# Company Search Page
elif page == "Company Search":
    st.header("Company Search")

    col1, col2 = st.columns([2, 1])

    with col1:
        search_type = st.radio("Search By", ["Name", "Category"], horizontal=True)

    with col2:
        limit = st.selectbox("Results Limit", [10, 20, 50, 100], index=1)

    search_query = st.text_input("Search Query", placeholder=f"Enter {search_type.lower()} to search...")

    if st.button("Search", type="primary"):
        if search_query:
            with st.spinner("Searching..."):
                if search_type == "Name":
                    results = repo.search_companies_by_name(search_query)
                else:
                    results = repo.search_companies_by_category(search_query)

                if results:
                    st.success(f"Found {len(results)} results")

                    for company in results[:limit]:
                        with st.container():
                            st.markdown(f"""
                            <div class="search-result">
                                <h4>{company['name']}</h4>
                                <p><strong>Business Number:</strong> {company['business_number'] or 'N/A'}</p>
                                <p><strong>Category:</strong> {company['business_category'] or 'N/A'}</p>
                                <p><small>ID: {company['id']}</small></p>
                            </div>
                            """, unsafe_allow_html=True)
                else:
                    st.warning("No results found")
        else:
            st.warning("Please enter a search query")

# Statistics Page
elif page == "Statistics":
    st.header("Database Statistics")

    stats = repo.get_statistics()

    if 'error' not in stats:
        st.subheader("Overview")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <h3>Talent Profiles</h3>
                <p style="font-size: 2rem; font-weight: 600;">{stats['total_talents']:,}</p>
            </div>
            """, unsafe_allow_html=True)

            st.markdown(f"""
            <div class="metric-card">
                <h3>Experience Tags</h3>
                <p style="font-size: 2rem; font-weight: 600;">{stats['total_exp_tags']:,}</p>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <h3>Companies</h3>
                <p style="font-size: 2rem; font-weight: 600;">{stats['total_companies']:,}</p>
            </div>
            """, unsafe_allow_html=True)

            st.markdown(f"""
            <div class="metric-card">
                <h3>External Data Records</h3>
                <p style="font-size: 2rem; font-weight: 600;">{stats['total_external_data']:,}</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.error("Unable to fetch statistics")
        st.info("Check database connection")

# Footer
st.markdown("---")
st.caption("Headhunter AI Agent | Professional Talent Management System")