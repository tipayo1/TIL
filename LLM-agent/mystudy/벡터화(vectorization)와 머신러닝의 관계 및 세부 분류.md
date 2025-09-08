<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

# 벡터화(vectorization)와 머신러닝의 관계 및 세부 분류

벡터화는 **머신러닝 모델 학습 전(preprocessing)** 단계에 속하는 **특징 공학(feature engineering)** 기법으로, 원시 데이터를 수치 벡터 형태로 변환하여 모델이 처리할 수 있도록 준비하는 작업이다. 즉, 벡터화는 머신러닝 알고리즘 그 자체가 아니라, **데이터 전처리(Data Preprocessing)** → **특징 공학(Feature Engineering)** → **모델 학습(Model Training)** → **평가(Evaluation)** 등으로 구성된 전체 파이프라인의 일부이다.[^1][^2][^3]

***

## 1. 데이터 전처리 단계에서의 분류 체계

1. **데이터 수집(Data Collection)**
원시 데이터(raw data)를 확보하는 단계.
2. **데이터 전처리(Data Preprocessing)**
    - 결측치 처리, 이상치 제거, 중복 제거 등
    - 데이터 정제(Data Cleaning)
    - 데이터 통합·축소·균형(Integration, Reduction, Balancing)
3. **특징 공학(Feature Engineering)**
    - **특징 생성(Feature Creation)**: 새로운 변수(피처)를 도출(예: 파생 변수 생성, 원-핫 인코딩)
    - **특징 변환(Feature Transformation)**: 스케일링, 로그 변환, 비닝(bin) 등
    - **특징 추출(Feature Extraction)**: 차원 축소(PCA, LDA 등)
    - **특징 선택(Feature Selection)**: 중요도 기반 변수 선택

– 벡터화(Vectorization)는 **특징 생성** 또는 **변환**에 해당하는 기법으로, 범주형·문자·이미지 데이터를 수치 벡터로 변환한다.[^2][^1]
4. **모델 학습 및 튜닝(Model Training \& Tuning)**
알고리즘에 따라 하이퍼파라미터 최적화(hyperparameter optimization) 수행.
5. **평가 및 배포(Evaluation \& Deployment)**
테스트 성능 평가, 실제 환경 배포.

***

## 2. 벡터화(Vectorization)의 세부 기법

### 2.1 범주형 데이터 벡터화

- **레이블 인코딩(Label Encoding)**: 각 카테고리를 정수로 매핑
- **원-핫 인코딩(One-Hot Encoding)**: 카테고리별 이진 벡터 생성[^2]


### 2.2 텍스트 데이터 벡터화

- **Bag-of-Words / Count-Vectorizer**: 단어 등장 횟수를 특징으로 변환
- **TF-IDF(Term Frequency–Inverse Document Frequency)**: 빈도 정보에 역문서 빈도 가중치 적용
- **단어 임베딩(Word Embeddings)**: Word2Vec, GloVe, FastText 등으로 분산 표현
- **문장·문맥 임베딩(Contextual Embeddings)**: BERT, GPT 계열 모델을 통해 문맥 기반 벡터 생성[^3]


### 2.3 이미지·기타 데이터

- **픽셀 값 정규화**: 픽셀을 0~1 또는 –1~1 범위로 스케일링
- **특징 맵 추출**: CNN 레이어를 통해 고수준 특징 벡터화

***

## 3. 벡터화의 역할과 중요성

- 머신러닝 모델은 **수치 입력만** 처리할 수 있으므로, 벡터화 없이는 범주형·텍스트·이미지 데이터를 활용할 수 없다.
- **데이터 품질과 표현력**이 모델 성능을 좌우하므로, 적절한 벡터화 기법 선택이 필수적이다.
- **자동화 도구**(예: 딥러닝의 임베딩 레이어, `tf.keras.layers.TextVectorization`)를 통해 모델 내부에서 전처리를 통합할 수도 있다.[^2]

***

## 4. 결론

벡터화는 머신러닝 알고리즘 그 자체가 아니라, **특징 공학(feature engineering)** 단계에 속하는 데이터 전처리 기법이다. 전체 머신러닝 파이프라인의 핵심 전 단계로, 데이터를 모델이 이해할 수 있는 **수치 벡터**로 변환하는 역할을 담당하며, 용도에 따라 다양한 구체적 기법으로 세분화된다.
<span style="display:none">[^10][^11][^12][^4][^5][^6][^7][^8][^9]</span>

<div style="text-align: center">⁂</div>

[^1]: https://docs.aws.amazon.com/ko_kr/wellarchitected/latest/machine-learning-lens/feature-engineering.html

[^2]: https://east-hyun.tistory.com/33

[^3]: https://neptune.ai/blog/vectorization-techniques-in-nlp-guide

[^4]: https://milvus.io/ai-quick-reference/what-preprocessing-steps-are-required-before-vectorization

[^5]: https://www.geeksforgeeks.org/machine-learning/what-is-feature-engineering/

[^6]: https://yu1moo.tistory.com/entry/데이터-전처리와-최적화-데이터-실수화-Data-Vectorization

[^7]: https://h2o.ai/wiki/feature-engineering/

[^8]: https://www.ibm.com/think/topics/feature-engineering

[^9]: https://builtin.com/articles/feature-engineering

[^10]: https://dodonam.tistory.com/188

[^11]: https://en.wikipedia.org/wiki/Feature_engineering

[^12]: https://dacon.io/competitions/official/235658/codeshare/1839

