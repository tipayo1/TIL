# 🎯 TIL `02_ML_basic.md`

# 📘 Logistic Regression

## 1. 데이터 준비
- **데이터**: fish_data.csv on slack
- **입력 변수**: Weight, Length, Diagonal, Height, Width
- **출력 변수**: Species (생선 종류)
- 훈련/테스트 분리 후 스케일링(StandardScaler) 적용

***

## 2. KNN 복습
- `KNeighborsClassifier(n_neighbors=3)`
- 특정 데이터 주위 3개의 이웃으로 확률 계산
- `predict_proba()` → 각 클래스일 확률 반환
- `classes_` 속성: 분류 가능한 클래스 목록

***

## 3. 로지스틱 회귀 개념
- 이름은 회귀(Regression) 이지만 실제로는 **분류(Classification)** 모델
- 선형 방정식 `z` 를 계산 후,
  - **이진분류** → 시그모이드 함수(sigmoid)
  - **다중분류** → 소프트맥스 함수(softmax)

### 시그모이드 함수
$$ \phi(z) = \frac{1}{1+e^{-z}} $$

### 소프트맥스 함수
$$ \sigma(z_i) = \frac{e^{z_i}}{\sum_j e^{z_j}} $$

- 출력은 확률 (0~1), 확률이 가장 큰 클래스로 예측

***

## 4. 이진 분류 (빙어 vs 도미)
- `LogisticRegression()` 학습
- **결과**: 계수(`coef_`), 절편(`intercept_`) → 방정식
- `decision_function()` : z값 반환
- `scipy.special.expit(z)` : 직접 시그모이드 적용 가능
- `predict_proba()` : 각 클래스 확률 반환
- ⚠️ **클래스는 알파벳 순으로 정렬됨** → 기준 클래스 확인 필요

***

## 5. 다중 분류 (7종 생선)
- `LogisticRegression(C=20, max_iter=1000)`
- **One-vs-Rest(OVR)** 방식으로 각 클래스에 대해 분류 수행
- `decision_function()` : 각 클래스별 z값 반환
- `predict_proba()` : softmax 적용된 확률 반환
- 클래스별 계수(`coef_`) → 어떤 피처가 어떤 생선 분류에 영향을 주는지 해석 가능

***

## 6. 하이퍼파라미터

### C : 규제 강도 (Inverse of Regularization Strength)
- 값 ↑ → 규제 약화 → 과적합 위험↑
- 값 ↓ → 규제 강화 → 일반화↑ (과소적합 위험↑)

### max_iter : 최적화 반복 횟수
- 데이터가 크면 크게 설정 필요

***

## 7. 실무 적용 팁

### 스케일링 필수
- 변수 크기 차이에 민감

### 계수(coef_) 해석
- **양수** → 해당 피처 값이 증가하면 특정 클래스 확률↑
- **음수** → 해당 피처 값이 증가하면 특정 클래스 확률↓

### 규제 활용
- **L2 규제**(Ridge, 기본)
- **L1 규제**(Lasso) → 중요 변수 선택(Feature Selection) 효과

***

## ✅ 핵심 정리
- 로지스틱 회귀는 **분류 모델**
- **이진분류** → 시그모이드 / **다중분류** → 소프트맥스
- `decision_function()` → z값, `predict_proba()` → 확률
- **C 파라미터**로 규제 조정 → 과적합/과소적합 제어
- 단순 정확도보다 **AUC, F1** 등 지표 활용이 중요
- `coef_` 해석으로 어떤 피처가 분류에 중요한지 확인 가능

[1](https://learn.dailyalgo.kr/courses/ai-%EA%B8%B0%EB%B0%98-%EB%8D%B0%EC%9D%B4%ED%84%B0-%EB%B6%84%EC%84%9D%EA%B0%80-%EC%96%91%EC%84%B1-%EA%B3%BC%EC%A0%95/25c611ac-3a00-8028-9101-f2abf21a0bac)