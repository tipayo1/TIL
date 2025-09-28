# 리팩터링된 모듈 구조 설계
refactored_structure = {
    "modules": {
        "1_state.py": {
            "purpose": "통합 상태 관리",
            "enhancements": [
                "RPG 그래프 상태 추가",
                "Dynamic memory management",
                "Composable state components"
            ]
        },
        "2_rpg.py": {
            "purpose": "Repository Planning Graph 관리 - 새로 추가",
            "components": [
                "RPGNode (기능, 파일, 의존성 노드)",
                "RPGGraph (그래프 구조 관리)",
                "RPGPlanner (계획 수립)",
                "RPGExecutor (실행 관리)"
            ]
        },
        "3_memory.py": {
            "purpose": "Agentic AI Memory 시스템 - nodes.py에서 분리",
            "components": [
                "ShortTermMemory (컨텍스트 메모리)",
                "LongTermMemory (벡터 저장소 연동)",
                "MemoryRetriever (메모리 검색)",
                "MemoryManager (메모리 통합 관리)"
            ]
        },
        "4_tools.py": {
            "purpose": "Tool 인터페이스 관리 - 새로 추가",
            "components": [
                "ToolRegistry (도구 등록소)",
                "ToolExecutor (도구 실행기)",
                "ToolValidator (도구 검증기)"
            ]
        },
        "5_agents.py": {
            "purpose": "Agentic 구성 요소 - nodes.py 리팩터링",
            "components": [
                "LLMAgent (언어 모델 에이전트)",
                "AutonomousAgent (자율 에이전트)",
                "CoordinatorAgent (조정 에이전트)"
            ]
        },
        "6_db.py": {
            "purpose": "데이터베이스 추상화 - create_pinecone_index.py 개선",
            "enhancements": [
                "벤더 독립적 인터페이스",
                "다중 벡터 DB 지원",
                "동적 설정 관리"
            ]
        },
        "7_router.py": {
            "purpose": "지능형 라우팅 - 기존 router.py 확장",
            "enhancements": [
                "RPG 기반 동적 라우팅",
                "의도 분석 고도화",
                "멀티 패스 라우팅"
            ]
        },
        "8_graph.py": {
            "purpose": "통합 그래프 오케스트레이션",
            "enhancements": [
                "RPG와 LangGraph 통합",
                "동적 워크플로우 생성",
                "실시간 그래프 수정"
            ]
        },
        "9_utils.py": {
            "purpose": "공통 유틸리티",
            "enhancements": [
                "프롬프트 템플릿 엔진",
                "설정 관리자",
                "로깅 및 모니터링"
            ]
        }
    },
    
    "architecture_principles": {
        "separation_of_concerns": "각 모듈은 단일 책임을 가짐",
        "dependency_injection": "런타임에 의존성 주입",
        "interface_based_design": "추상 인터페이스를 통한 느슨한 결합",
        "event_driven": "이벤트 기반 비동기 처리",
        "plugin_architecture": "플러그인 방식의 확장성"
    }
}

print("=== 리팩터링된 모듈 구조 ===")
print(json.dumps(refactored_structure, indent=2, ensure_ascii=False))

# 각 모듈별 핵심 개선사항 요약
print("\n=== 주요 개선사항 요약 ===")
improvements = [
    "1. RPG 모듈 신규 추가: 논문의 Repository Planning Graph 로직 구현",
    "2. Memory 시스템 분리: Agentic AI의 메모리 관리 전담",
    "3. Tools 추상화: 외부 도구와의 인터페이스 표준화",
    "4. Agents 리팩터링: LLM, Autonomy 요소 모듈화",
    "5. 벤더 독립적 DB: 다양한 벡터 DB 지원",
    "6. 동적 라우팅: RPG 기반 지능형 워크플로우 제어",
    "7. Composable 아키텍처: 모듈의 독립성과 재사용성 극대화"
]

for improvement in improvements:
    print(improvement)