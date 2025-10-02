"""ReAct 스타일 헤드헌터 AI 에이전트 - 완전한 구현"""

import os
from typing import Dict, Any
from dotenv import load_dotenv

from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_upstage import ChatUpstage
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver

# 도구들 임포트
from ..tools.candidate_tools import (
    search_candidates_by_skills,
    search_candidates_by_location,
    search_candidates_by_salary_range,
    search_candidates_by_work_type,
    search_candidates_by_industry,
    search_candidates_by_availability,
    get_candidate_details,
    complex_candidate_search,
    get_candidate_statistics,
    search_companies_by_name,
    search_companies_by_category
)

from ..tools.market_tools import (
    search_tech_information,
    search_market_trends,
    search_industry_analysis,
    search_salary_information,
    general_knowledge_search,
    compare_technologies,
    get_knowledge_base_stats
)

from ..tools.web_search_tools import (
    web_search_latest_trends,
    search_job_postings,
    search_company_information,
    search_salary_benchmarks,
    search_tech_news,
    search_startup_funding_news
)

load_dotenv()

# 시스템 프롬프트 (최적화됨 - 토큰 절약)
HEADHUNTER_SYSTEM_PROMPT = """당신은 전문 헤드헌터 AI 어시스턴트입니다.

**역할**: 인재 검색, 시장 분석, 채용 정보 제공, 커리어 상담

**데이터 소스**:
- 정형 데이터(DB): 인재/회사 정보
- 비정형 데이터(RAG): 기술/시장 트렌드, 급여 정보
- 실시간(웹검색): 최신 채용/뉴스

**응답 원칙**:
1. 친절하고 전문적인 톤 사용
2. 도구를 활용한 구체적 데이터 제공
3. 복합 검색 시 여러 도구 조합 활용
4. 실행 가능한 조언 제공

항상 사용자 의도를 파악하고 적절한 도구로 최고의 답변을 제공하세요.
"""

class HeadhunterReactAgent:
    """ReAct 패턴 기반 헤드헌터 AI 에이전트"""

    def __init__(self):
        # LLM 초기화
        self.llm = ChatUpstage(
            model="solar-pro",
            temperature=0.1
        )

        # 모든 도구 수집
        self.tools = [
            # 후보자 검색 도구
            search_candidates_by_skills,
            search_candidates_by_location,
            search_candidates_by_salary_range,
            search_candidates_by_work_type,
            search_candidates_by_industry,
            search_candidates_by_availability,
            get_candidate_details,
            complex_candidate_search,
            get_candidate_statistics,

            # 회사 검색 도구
            search_companies_by_name,
            search_companies_by_category,

            # 시장 분석 도구 (RAG)
            search_tech_information,
            search_market_trends,
            search_industry_analysis,
            search_salary_information,
            general_knowledge_search,
            compare_technologies,
            get_knowledge_base_stats,

            # 웹 검색 도구
            web_search_latest_trends,
            search_job_postings,
            search_company_information,
            search_salary_benchmarks,
            search_tech_news,
            search_startup_funding_news
        ]

        # 메모리 체크포인터
        self.memory = MemorySaver()

        # ReAct 에이전트 생성 (state_modifier 제거)
        self.agent = create_react_agent(
            model=self.llm,
            tools=self.tools,
            checkpointer=self.memory
        )

        # 시스템 프롬프트는 invoke 시 추가
        self.system_message = SystemMessage(content=HEADHUNTER_SYSTEM_PROMPT)

    def invoke(self, message: str, thread_id: str = "default") -> Dict[str, Any]:
        """
        에이전트 실행

        Args:
            message: 사용자 메시지
            thread_id: 대화 스레드 ID (세션 관리용)

        Returns:
            에이전트 응답
        """
        config = {"configurable": {"thread_id": thread_id}}

        # 시스템 메시지 + 사용자 메시지
        messages = [self.system_message, HumanMessage(content=message)]

        response = self.agent.invoke(
            {"messages": messages},
            config=config
        )

        return response

    def stream(self, message: str, thread_id: str = "default"):
        """
        스트리밍 응답

        Args:
            message: 사용자 메시지
            thread_id: 대화 스레드 ID

        Yields:
            스트리밍 청크
        """
        config = {"configurable": {"thread_id": thread_id}}

        # 시스템 메시지 + 사용자 메시지
        messages = [self.system_message, HumanMessage(content=message)]

        for chunk in self.agent.stream(
            {"messages": messages},
            config=config,
            stream_mode="values"
        ):
            yield chunk

    def get_chat_history(self, thread_id: str = "default"):
        """
        대화 히스토리 조회

        Args:
            thread_id: 대화 스레드 ID

        Returns:
            대화 히스토리
        """
        config = {"configurable": {"thread_id": thread_id}}
        state = self.agent.get_state(config)
        return state.values.get("messages", [])


# 전역 인스턴스
_react_agent_instance = None

def get_react_agent() -> HeadhunterReactAgent:
    """ReAct 에이전트 싱글톤 인스턴스 반환"""
    global _react_agent_instance
    if _react_agent_instance is None:
        _react_agent_instance = HeadhunterReactAgent()
    return _react_agent_instance


# 간단한 사용 예시
if __name__ == "__main__":
    agent = get_react_agent()

    # 테스트 쿼리
    test_queries = [
        "Python 개발자를 찾고 있어요",
        "데이터 사이언티스트의 평균 연봉이 궁금합니다",
        "최근 AI 개발자 채용 트렌드는 어떤가요?"
    ]

    for query in test_queries:
        print(f"\n질문: {query}")
        print("-" * 50)

        response = agent.invoke(query, thread_id="test-session")

        # 마지막 메시지 출력
        if response["messages"]:
            last_message = response["messages"][-1]
            print(f"답변: {last_message.content}")
