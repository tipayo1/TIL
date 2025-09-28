# usage_example.py - LangGraph RAG 시스템 사용 예제
# RPG 기반 경량화된 Agentic AI 시스템 데모

import asyncio
import os
from typing import Dict, Any

# 환경 변수 설정 예제
os.environ.setdefault("OPENAI_API_KEY", "your-openai-api-key")
os.environ.setdefault("PINECONE_API_KEY", "your-pinecone-api-key")  # 선택사항

from graph import GraphOrchestrator, GraphMode, run_rag_system
from db import create_database_manager_with_defaults
from utils import get_config, set_config

async def basic_usage_example():
    """기본 사용 예제"""
    print("=== 기본 RAG 시스템 사용 예제 ===")

    try:
        # 1. 간단한 질답
        result = await run_rag_system("안녕하세요, 반갑습니다!", mode="standard")
        print(f"답변: {result.get('answer', '')}")
        print(f"답변 타입: {result.get('answer_type', '')}")

        # 2. HR 관련 질문
        result = await run_rag_system("연차는 어떻게 사용하나요?", mode="standard")
        print(f"\nHR 질문 답변: {result.get('answer', '')}")

        # 3. 복잡한 분석 작업
        result = await run_rag_system("우리 회사의 인사 정책을 종합적으로 분석해주세요", mode="rpg")
        print(f"\nRPG 모드 답변: {result.get('answer', '')}")

    except Exception as e:
        print(f"기본 사용 예제 오류: {str(e)}")

async def advanced_usage_example():
    """고급 사용 예제 - 수동 구성"""
    print("\n=== 고급 사용 예제 - 수동 구성 ===")

    try:
        # 1. 오케스트레이터 생성 및 초기화
        orchestrator = GraphOrchestrator()

        if not orchestrator.initialize_components():
            print("구성요소 초기화 실패")
            return

        # 2. 데이터베이스 설정
        if orchestrator.database_manager:
            # FAISS 로컬 DB 사용 (Pinecone이 없는 경우)
            success = await orchestrator.database_manager.connect_database("faiss")
            if success:
                print("FAISS 데이터베이스 연결 성공")
            else:
                # 메모리 DB 폴백
                success = await orchestrator.database_manager.connect_database("memory")
                print(f"메모리 데이터베이스 연결: {success}")

        # 3. 다양한 모드로 그래프 빌드 및 실행
        modes_to_test = [
            ("standard", "표준 RAG 모드"),
            ("rpg", "RPG 강화 모드"),
            ("autonomous", "자율 에이전트 모드"),
            ("coordinator", "조정 에이전트 모드")
        ]

        for mode_key, mode_name in modes_to_test:
            print(f"\n--- {mode_name} 테스트 ---")

            try:
                # 그래프 빌드
                mode_enum = {
                    "standard": GraphMode.STANDARD,
                    "rpg": GraphMode.RPG_ENHANCED,
                    "autonomous": GraphMode.AUTONOMOUS,
                    "coordinator": GraphMode.COORDINATOR
                }[mode_key]

                orchestrator.build_graph(mode_enum)

                # 실행
                result = await orchestrator.run("LangGraph와 RPG를 활용한 시스템에 대해 설명해주세요")

                print(f"성공: {result.get('success', False)}")
                print(f"답변: {result.get('answer', '')[:100]}...")

            except Exception as e:
                print(f"{mode_name} 오류: {str(e)}")

    except Exception as e:
        print(f"고급 사용 예제 오류: {str(e)}")

async def document_loading_example():
    """문서 로딩 및 검색 예제"""
    print("\n=== 문서 로딩 및 검색 예제 ===")

    try:
        # 데이터베이스 매니저 생성
        db_manager = create_database_manager_with_defaults()

        # 로컬 메모리 DB 연결 (데모용)
        success = await db_manager.connect_database("memory")
        if not success:
            print("데이터베이스 연결 실패")
            return

        # 샘플 문서 데이터 생성
        from langchain_core.documents import Document
        sample_docs = [
            Document(
                page_content="LangGraph는 상태 기반 멀티 에이전트 워크플로우를 구축하는 라이브러리입니다.",
                metadata={"source": "langgraph_guide.md", "topic": "langgraph"}
            ),
            Document(
                page_content="Repository Planning Graph(RPG)는 코드 생성을 위한 계획 그래프 방법론입니다.",
                metadata={"source": "rpg_paper.md", "topic": "rpg"}
            ),
            Document(
                page_content="Agentic AI는 자율적이고 목표 지향적인 AI 시스템을 의미합니다.",
                metadata={"source": "agentic_ai.md", "topic": "agentic_ai"}
            )
        ]

        # 문서 추가
        success = await db_manager.add_documents_to_active_db(sample_docs)
        if success:
            print(f"샘플 문서 {len(sample_docs)}개 추가 완료")

        # 검색 테스트
        queries = [
            "LangGraph란 무엇인가요?",
            "RPG에 대해 설명해주세요",
            "Agentic AI의 특징은?"
        ]

        for query in queries:
            print(f"\n검색어: {query}")
            results = await db_manager.search_in_active_db(query, top_k=2)

            for i, doc in enumerate(results):
                print(f"  결과 {i+1}: {doc.page_content[:50]}...")
                print(f"  출처: {doc.metadata.get('source', 'unknown')}")

        # 데이터베이스 통계
        stats = await db_manager.get_database_stats()
        print(f"\n데이터베이스 통계: {stats}")

    except Exception as e:
        print(f"문서 로딩 예제 오류: {str(e)}")

async def configuration_example():
    """설정 관리 예제"""
    print("\n=== 설정 관리 예제 ===")

    try:
        from utils import get_config, set_config, save_config

        # 기본 설정 조회
        llm_config = get_config("llm")
        print(f"LLM 설정: {llm_config}")

        vector_db_config = get_config("vector_db")
        print(f"Vector DB 설정: {vector_db_config}")

        # 설정 변경
        set_config("llm.temperature", 0.2)
        set_config("vector_db.chunk_size", 800)

        # 도메인별 설정 조회
        hr_config = get_config("domains.hr", {})
        print(f"HR 도메인 설정: {hr_config}")

        # 설정 저장 (실제로는 파일에 저장됨)
        # save_success = save_config()
        # print(f"설정 저장 성공: {save_success}")

        print("설정 관리 예제 완료")

    except Exception as e:
        print(f"설정 관리 예제 오류: {str(e)}")

async def monitoring_example():
    """모니터링 및 성능 분석 예제"""
    print("\n=== 모니터링 예제 ===")

    try:
        from utils import record_execution, get_metrics, profile

        # 성능 프로파일링 사용
        with profile("test_operation"):
            await asyncio.sleep(0.1)  # 가상의 작업
            print("프로파일링된 작업 완료")

        # 수동 실행 기록
        record_execution("test_component", "test_operation", 0.15, True, 
                        test_param="example_value")

        # 메트릭 조회
        metrics = get_metrics()
        print(f"\n현재 메트릭:")
        print(f"  총 실행 수: {metrics.get('total_executions', 0)}")
        print(f"  업타임: {metrics.get('uptime', 0):.2f}초")

        component_metrics = metrics.get('component_metrics', {})
        for component, metric in component_metrics.items():
            print(f"  {component}: 평균 {metric.get('avg_duration', 0):.3f}초, "
                  f"성공률 {metric.get('success_rate', 0):.1%}")

    except Exception as e:
        print(f"모니터링 예제 오류: {str(e)}")

async def main():
    """메인 실행 함수"""
    print("🚀 LangGraph RPG RAG 시스템 사용 예제")
    print("=" * 50)

    try:
        # 각 예제 실행
        await basic_usage_example()
        await advanced_usage_example()
        await document_loading_example()
        await configuration_example()
        await monitoring_example()

        print("\n✅ 모든 예제 실행 완료!")
        print("\n📝 참고사항:")
        print("- 실제 사용시 OPENAI_API_KEY 환경변수를 설정하세요")
        print("- Pinecone 사용시 PINECONE_API_KEY도 설정하세요")
        print("- 문서 파일들을 data/ 폴더에 준비하세요")
        print("- 자세한 설정은 config.yaml 파일을 참조하세요")

    except Exception as e:
        print(f"\n❌ 메인 실행 오류: {str(e)}")

if __name__ == "__main__":
    # 비동기 메인 함수 실행
    asyncio.run(main())
