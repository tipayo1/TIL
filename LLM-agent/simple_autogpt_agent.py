
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LangChain Auto-GPT 에이전트 구현
간단한 Python 스크립트 버전

이 스크립트는 LangChain을 사용하여 Auto-GPT 스타일의 자율 에이전트를 구현합니다.
"""

import os
import faiss
from typing import List

# LangChain 라이브러리
try:
    from langchain_openai import ChatOpenAI, OpenAIEmbeddings
    from langchain_experimental.autonomous_agents.autogpt.agent import AutoGPT
    from langchain.agents import Tool
    from langchain.tools.file_management.write import WriteFileTool
    from langchain.tools.file_management.read import ReadFileTool
    from langchain_community.utilities import SerpAPIWrapper
    from langchain_community.vectorstores import FAISS
    from langchain.docstore import InMemoryDocstore
except ImportError as e:
    print(f"❌ 필요한 라이브러리를 설치해주세요: {e}")
    print("다음 명령어를 실행하세요:")
    print("pip install langchain-experimental langchain-openai langchain-community faiss-cpu google-search-results")
    exit(1)


class SimpleAutoGPT:
    """간단한 Auto-GPT 에이전트 클래스"""

    def __init__(self, openai_api_key: str, serpapi_key: str = None):
        """
        Auto-GPT 에이전트 초기화

        Args:
            openai_api_key: OpenAI API 키
            serpapi_key: SerpAPI 키 (선택사항)
        """
        self.openai_api_key = openai_api_key
        self.serpapi_key = serpapi_key

        # 환경 변수 설정
        os.environ["OPENAI_API_KEY"] = openai_api_key
        if serpapi_key:
            os.environ["SERPAPI_API_KEY"] = serpapi_key

        # 컴포넌트 초기화
        self.llm = self._setup_llm()
        self.tools = self._setup_tools()
        self.vectorstore = self._setup_memory()
        self.agent = self._create_agent()

        print("✅ Auto-GPT 에이전트가 성공적으로 초기화되었습니다!")

    def _setup_llm(self):
        """LLM 모델 설정"""
        return ChatOpenAI(
            model_name="gpt-4o-mini",
            temperature=0.1,
            max_tokens=2000
        )

    def _setup_tools(self):
        """도구들 설정"""
        tools = []

        # 웹 검색 도구
        if self.serpapi_key:
            search = SerpAPIWrapper()
            search_tool = Tool(
                name="search",
                func=search.run,
                description="웹에서 최신 정보를 검색합니다. 구체적인 키워드를 사용하세요."
            )
            tools.append(search_tool)

        # 파일 관리 도구
        tools.extend([
            WriteFileTool(),
            ReadFileTool()
        ])

        # 계산기 도구
        def calculator(expression: str) -> str:
            """간단한 수학 계산"""
            try:
                allowed_chars = set('0123456789+-*/(). ')
                if all(c in allowed_chars for c in expression):
                    result = eval(expression)
                    return f"계산 결과: {expression} = {result}"
                else:
                    return "잘못된 수식입니다."
            except Exception as e:
                return f"계산 오류: {str(e)}"

        calculator_tool = Tool(
            name="calculator",
            func=calculator,
            description="수학 계산을 수행합니다. 예: '2+2' 또는 '10*5'"
        )
        tools.append(calculator_tool)

        # 시간 확인 도구
        def get_time() -> str:
            from datetime import datetime
            return f"현재 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

        time_tool = Tool(
            name="current_time",
            func=get_time,
            description="현재 날짜와 시간을 확인합니다."
        )
        tools.append(time_tool)

        return tools

    def _setup_memory(self):
        """메모리 시스템 설정"""
        embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        embedding_size = 1536
        index = faiss.IndexFlatL2(embedding_size)

        vectorstore = FAISS(
            embedding_function=embeddings.embed_query,
            index=index,
            docstore=InMemoryDocstore({}),
            index_to_docstore_id={}
        )

        return vectorstore

    def _create_agent(self):
        """Auto-GPT 에이전트 생성"""
        return AutoGPT.from_llm_and_tools(
            ai_name="ResearchGPT",
            ai_role="연구 및 분석 전문 AI 어시스턴트",
            tools=self.tools,
            llm=self.llm,
            memory=self.vectorstore.as_retriever(search_kwargs={"k": 5})
        )

    def run_task(self, goals: List[str], max_iterations: int = 15) -> str:
        """
        작업 실행

        Args:
            goals: 목표 리스트
            max_iterations: 최대 반복 횟수

        Returns:
            실행 결과
        """
        print("🚀 작업을 시작합니다...")
        print(f"📋 목표: {goals}")
        print("=" * 50)

        try:
            result = self.agent.run(goals)
            print("
✅ 작업이 완료되었습니다!")
            return result
        except Exception as e:
            error_msg = f"❌ 작업 실행 중 오류 발생: {str(e)}"
            print(error_msg)
            return error_msg

    def get_system_info(self):
        """시스템 정보 출력"""
        print("🤖 Auto-GPT 시스템 정보")
        print("=" * 30)
        print(f"LLM 모델: {self.llm.model_name}")
        print(f"등록된 도구 수: {len(self.tools)}")
        print("도구 목록:")
        for tool in self.tools:
            print(f"  - {tool.name}: {tool.description}")


def main():
    """메인 함수"""
    print("🤖 LangChain Auto-GPT 에이전트")
    print("=" * 40)

    # API 키 입력
    openai_key = input("OpenAI API 키를 입력하세요: ").strip()
    if not openai_key:
        print("❌ OpenAI API 키가 필요합니다.")
        return

    serpapi_key = input("SerpAPI 키를 입력하세요 (선택사항, Enter로 건너뛰기): ").strip()
    if not serpapi_key:
        serpapi_key = None
        print("ℹ️ SerpAPI 키가 없어 웹 검색 기능이 제한됩니다.")

    try:
        # 에이전트 생성
        agent = SimpleAutoGPT(openai_key, serpapi_key)
        agent.get_system_info()

        print("
" + "=" * 40)
        print("사용 예제:")

        # 예제 1: 간단한 계산 및 파일 저장
        example_goals_1 = [
            "현재 시간을 확인하기",
            "100 + 200을 계산하기",
            "현재 시간과 계산 결과를 'example_result.txt' 파일에 저장하기"
        ]

        print("
📝 예제 1: 계산 및 파일 저장")
        result1 = agent.run_task(example_goals_1)
        print(f"결과: {result1}")

        # 예제 2: 연구 작업
        example_goals_2 = [
            "Python 프로그래밍 언어의 주요 특징 3가지를 정리하기",
            "정리한 내용을 'python_features.txt' 파일로 저장하기",
            "저장된 파일을 읽어서 내용이 올바른지 확인하기"
        ]

        print("
🔍 예제 2: 연구 및 검증")
        result2 = agent.run_task(example_goals_2)
        print(f"결과: {result2}")

        # 사용자 정의 작업
        print("
" + "=" * 40)
        while True:
            custom = input("
사용자 정의 작업을 실행하시겠습니까? (y/n): ").lower()
            if custom == 'y':
                print("목표를 입력하세요 (각 목표를 한 줄씩, 완료 시 빈 줄 입력):")
                goals = []
                while True:
                    goal = input(f"목표 {len(goals)+1}: ").strip()
                    if not goal:
                        break
                    goals.append(goal)

                if goals:
                    custom_result = agent.run_task(goals)
                    print(f"결과: {custom_result}")
                else:
                    print("목표가 입력되지 않았습니다.")
            else:
                break

        print("
🎉 Auto-GPT 에이전트 데모가 완료되었습니다!")

    except Exception as e:
        print(f"❌ 에이전트 초기화 실패: {str(e)}")
        print("필요한 라이브러리가 모두 설치되었는지 확인해주세요.")


if __name__ == "__main__":
    main()
