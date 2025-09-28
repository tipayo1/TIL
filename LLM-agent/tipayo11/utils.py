import os
import re
from typing import List, Dict, TypedDict
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

# =========================
# LLM 모델 호출
# =========================
def get_llm(role: str = "gen") -> ChatOpenAI:
    """
    노드별로 적합한 LLM 모델을 반환하는 팩토리 함수
    Args:
      role (str): 역할별 모델 선택
        - "gen": 본문 생성/분석
        - "router1": 1차 라우터
        - "router2": 2차 라우터
        - "planner": RPG 계획 합성
        - "judge": 검증/정책 판단
        - "reranker": LLM 점수화 재랭크
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY가 환경변수에 설정되지 않았습니다.")

    model_map = {
        "gen": os.getenv("GEN_LLM", "gpt-4.1"),
        "router1": os.getenv("ROUTER1_LLM", "gpt-4.1-nano"),
        "router2": os.getenv("ROUTER2_LLM", "gpt-4.1-nano"),
        "planner": os.getenv("PLANNER_LLM", "gpt-4.1"),
        "judge": os.getenv("JUDGE_LLM", "gpt-4.1-mini"),
        "reranker": os.getenv("RERANKER_LLM", "gpt-4.1-mini"),
    }
    model_name = model_map.get(role, model_map["gen"])
    try:
        return ChatOpenAI(model=model_name, temperature=0, api_key=api_key)
    except Exception as e:
        raise RuntimeError(f"LLM 초기화 실패 (role: {role}, model: {model_name}): {str(e)}")

# =========================
# RPG 보조 함수
# =========================
class TermsOut(TypedDict):
    terms: List[str]

def extract_query_terms_llm(question: str) -> List[str]:
    """LLM으로 핵심/동의어 용어를 구조화 추출"""
    llm = get_llm("planner")
    prompt = f"""
HR 규정/정책 질의의 핵심 검색어와 동의어를 3~8개로 선정하라.
한국어 위주로 간결히 단어만 추출하라.
질문: "{question}"
"""
    try:
        structured = llm.with_structured_output(TermsOut).invoke(prompt)
        out = [t.strip() for t in structured.get("terms", []) if t.strip()]
        return list(dict.fromkeys(out))[:8]
    except Exception:
        # 규칙 기반 폴백
        tokens = re.findall(r"[가-힣A-Za-z0-9]+", question)
        return list(dict.fromkeys([t for t in tokens if len(t) >= 2]))[:6]

def compute_retrieval_metrics(terms: List[str], docs: List) -> Dict[str, float]:
    """coverage/diversity/avgscore(의사값) 산출"""
    n = len(docs) or 0
    if n == 0:
        return {"n": 0, "coverage": 0.0, "diversity": 0.0, "avgscore": 0.0}
    terms_lower = [t.lower() for t in terms]
    hit = 0
    sources = set()
    scores = []
    for d in docs:
        text = (d.page_content or "").lower()
        src = (d.metadata or {}).get("source", "unknown")
        sources.add(src)
        matched = any(t in text for t in terms_lower) if terms_lower else False
        if matched:
            hit += 1
            scores.append(1.0)
        else:
            scores.append(0.5)  # 의사 점수(실제 재랭크 전 평균값 대용)
    coverage = hit / n
    diversity = len(sources) / n
    avgscore = sum(scores) / n if n else 0.0
    return {"n": n, "coverage": coverage, "diversity": diversity, "avgscore": avgscore}
