<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

## **Chain-of-Agents (CoA)란 무엇인가?**

**Chain-of-Agents (CoA)**는 Google Cloud AI Research와 Penn State University 연구진이 2024년 NeurIPS에서 발표한 **다중 에이전트 협업 프레임워크**로, **장문 컨텍스트 처리를 위해 여러 AI 에이전트가 순차적으로 협력하는 새로운 접근법**입니다.[^1][^2]

### **CoA의 핵심 개념**

CoA는 **인간이 긴 텍스트를 단계적으로 처리하는 방식에서 영감**을 받아 설계되었으며, 하나의 대형 언어 모델에 의존하는 대신 **여러 전문화된 AI 에이전트들이 협력하여 무제한의 텍스트를 처리**할 수 있게 합니다.[^3][^4]

### **CoA의 2단계 작동 구조**

#### **1단계: 워커 에이전트(Worker Agents)의 순차적 협업**

- **텍스트 분할**: 긴 문서를 각 에이전트가 처리할 수 있는 작은 청크(chunk)로 분할[^1]
- **순차적 정보 전달**: 각 워커 에이전트가 자신의 청크를 처리한 후, **유용한 정보를 다음 에이전트에게 전달**하는 "커뮤니케이션 유닛(Communication Unit)" 방식[^4][^1]
- **정보 축적**: 이전 에이전트의 발견사항과 자신의 분석 결과를 결합하여 **점진적으로 완전한 이해를 구축**[^4]


#### **2단계: 매니저 에이전트(Manager Agent)의 통합**

- **최종 종합**: 마지막 워커 에이전트로부터 **모든 수집된 정보를 받아** 최종 응답을 생성[^1]
- **역할 분리**: 텍스트 분석과 답변 생성을 분리하여 **각 에이전트가 전문 업무에 집중**할 수 있게 함[^4]


### **CoA의 주요 특징**

#### **훈련 불필요(Training-Free)**

**기존 LLM을 그대로 활용**하여 별도의 훈련이나 파인튜닝 없이 바로 적용 가능합니다.[^2][^1]

#### **작업 독립적(Task-Agnostic)**

**질문 답변, 요약, 코드 완성** 등 다양한 장문 처리 작업에 범용적으로 적용할 수 있습니다.[^2][^1]

#### **해석 가능성(Interpretability)**

각 에이전트의 기여도를 추적할 수 있어 **전체 과정이 투명하고 해석 가능**합니다.[^2][^1]

#### **비용 효율성**

시간 복잡도를 **O(n²)에서 O(nk)로 크게 단축**시켜 계산 비용을 대폭 절감합니다.[^1]

### **기존 방식과의 차이점**

#### **RAG vs CoA**

- **RAG**: 관련 정보만 검색하여 중요한 정보를 놓칠 위험
- **CoA**: **전체 텍스트를 순차적으로 처리**하여 정보 손실 최소화[^4]


#### **Long Context LLM vs CoA**

- **Long Context LLM**: 긴 입력에서 "lost-in-the-middle" 현상으로 성능 저하
- **CoA**: **각 에이전트가 짧은 컨텍스트만 처리**하여 집중도 유지[^1]


#### **기존 Multi-Agent vs CoA**

- **기존 방식**: 에이전트들이 **병렬적으로 독립 작업** 후 결과 병합
- **CoA**: **순차적 커뮤니케이션**으로 정보를 점진적으로 축적[^5][^4]


### **성능 및 효과**

실험 결과 CoA는 **RAG와 Long Context LLM 대비 최대 10% 향상된 성능**을 보였으며, **긴 샘플일수록 더 뛰어난 성능**을 발휘했습니다. 특히 "lost-in-the-middle" 문제를 효과적으로 완화하여 **정보 통합과 컨텍스트 추론 능력**이 크게 향상되었습니다.[^2][^1]

### **실제 구현 및 활용**

#### **GitHub 구현체**

CoA는 **Python과 Swift로 구현된 오픈소스 버전**이 GitHub에서 제공되어 실무에서 바로 활용할 수 있습니다.[^6]

#### **응용 분야**

- **장문 문서 요약**: 긴 보고서나 연구 논문의 종합적 요약
- **복잡한 질문 답변**: 여러 문서에 걸친 정보를 종합한 답변
- **코드 완성**: 대규모 코드베이스에서의 맥락적 코드 생성
- **법률 문서 분석**: 긴 계약서나 법률 문서의 핵심 내용 추출


### **한계 및 향후 발전 방향**

#### **현재 한계**

- **에이전트 간 커뮤니케이션 최적화** 필요: 현재 LLM들이 인간 규범에 맞춰져 있어 LLM 간 소통에는 최적화되지 않음[^1]
- **다양한 커뮤니케이션 방식** 미탐구: 토론이나 복잡한 논의 형태는 아직 활용되지 않음[^1]


#### **발전 방향**

- **모델 라우팅**을 통한 비용과 지연시간 추가 단축
- **파인튜닝이나 인컨텍스트 학습**을 통한 커뮤니케이션 효율성 향상
- **더 복잡한 에이전트 간 상호작용** 메커니즘 개발

CoA는 **단일 모델의 한계를 뛰어넘어 협력적 AI의 새로운 패러다임**을 제시하며, 특히 **장문 처리가 중요한 실무 환경**에서 혁신적인 솔루션으로 자리잡고 있습니다.

<div style="text-align: center">⁂</div>

[^1]: https://arxiv.org/html/2406.02818v1

[^2]: https://research.google/blog/chain-of-agents-large-language-models-collaborating-on-long-context-tasks/

[^3]: https://turingpost.co.kr/p/topic-27-coa-corag

[^4]: https://huggingface.co/blog/Kseniase/coa-and-co-rag

[^5]: https://openreview.net/pdf?id=LuCLf4BJsr

[^6]: https://github.com/rudrankriyam/Chain-of-Agents

[^7]: https://www.themoonlight.io/ko/review/chain-of-agents-large-language-models-collaborating-on-long-context-tasks

[^8]: https://www.linkedin.com/pulse/chain-agents-llm-models-enhancing-ai-multi-agent-collaboration-m-hejlf

[^9]: https://promptengineering.org/distinguishing-between-chains-and-agents-in-ai/

[^10]: https://www.linkedin.com/pulse/artificial-intelligence-exploring-chain-agents-coa-ai-kumar-crtjc

