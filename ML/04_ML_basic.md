# 🎯 TIL `04_ML_basic.md`

# 1️⃣ RandomizedSearchCV

## 개념
- **GridSearchCV**: 모든 후보 하이퍼파라미터 조합 탐색 → 연산량 큼
- **RandomizedSearchCV**: 지정된 범위(distribution)에서 임의로 샘플링 → 빠르고 효율적

```python
from scipy.stats import uniform, randint

# 정수 범위 샘플링
randint(0, 10).rvs(10)

# 실수 범위 샘플링
uniform(0, 1).rvs(10)
```

## 활용 예시

```python
params = {
    'min_impurity_decrease': uniform(0.0001, 0.001),
    'max_depth': randint(10, 50),
    'min_samples_split': randint(2, 25),
    'min_samples_leaf': randint(1, 25)
}

from sklearn.model_selection import RandomizedSearchCV
gs = RandomizedSearchCV(
    DecisionTreeClassifier(random_state=42),
    param_distributions=params,
    n_iter=1000,
    n_jobs=-1,
    random_state=42
)

gs.fit(X_train, y_train)
print(gs.best_params_, gs.best_score_)
```

**best_score_**: 내부 교차검증(CV)에서 최적 파라미터 조합의 평균 성능

***

# 2️⃣ 앙상블 학습 (Ensemble Learning)

📌 **정형 데이터(표 구조 데이터)에서 가장 강력한 알고리즘 계열**
- 대부분 트리 기반 (Decision Tree → 여러 개 조합)

## 🔹 Random Forest (랜덤 포레스트)

- 여러 개의 결정트리를 복원추출(bootstrap) 데이터로 학습
- **예측 시**:
  - 분류: 다수결 투표
  - 회귀: 평균
- **장점**: 과적합 방지 + 안정적 성능
- 노드 분할 시 특성 일부만 고려 → 다양한 트리 생성

```python
rf = RandomForestClassifier(n_jobs=-1, random_state=42)
scores = cross_validate(rf, X_train, y_train, return_train_score=True, n_jobs=-1)
print(np.mean(scores['train_score']), np.mean(scores['test_score']))

rf.fit(X_train, y_train)
print(rf.feature_importances_)
```

### OOB (Out-Of-Bag) 평가
- 복원추출 시 선택되지 않은 데이터(OOB)를 검증에 활용

```python
rf = RandomForestClassifier(oob_score=True, n_jobs=-1, random_state=42)
rf.fit(X_train, y_train)
print(rf.oob_score_)
```

### 하이퍼파라미터 튜닝

```python
params = {
    'max_depth': randint(3, 50),
    'min_samples_split': randint(2, 20),
    'min_samples_leaf': randint(1, 20),
    'max_features': ['sqrt', 'log2', None],
    'n_estimators': randint(50, 300)
}

rs = RandomizedSearchCV(rf, params, n_iter=100, n_jobs=-1, random_state=42)
rs.fit(X_train, y_train)
print(rs.best_params_, rs.best_score_, rs.score(X_test, y_test))
```

## 🔹 Extra Trees (Extremely Randomized Trees)

- Random Forest와 거의 유사
- **차이점**:
  - 부트스트랩 샘플링 안함 → 전체 데이터 사용
  - 노드 분할 시 최적 분할 대신 무작위 분할
- **장점**: 더 무작위성 ↑ → 과적합 방지, 노이즈 데이터에서 유리

```python
et = ExtraTreesClassifier(n_jobs=-1, random_state=42)
scores = cross_validate(et, X_train, y_train, return_train_score=True, n_jobs=-1)
print(np.mean(scores['train_score']), np.mean(scores['test_score']))
```

## 🔹 Gradient Boosting (GB)

- **부스팅(Boosting)**: 약한 모델(얕은 트리)을 순차적으로 학습 → 이전 모델의 오차 보완
- **방식**:
  1. 첫 번째 트리 학습
  2. 오차(잔차) 계산
  3. 잔차를 예측하도록 다음 트리 학습
  4. 반복 → 오차 줄여감
- **장점**: 높은 예측 성능
- **단점**: 학습 속도 느림(순차적), 하이퍼파라미터 많음

```python
gb = GradientBoostingClassifier(random_state=42)
scores = cross_validate(gb, X_train, y_train, return_train_score=True, n_jobs=-1)
print(np.mean(scores['train_score']), np.mean(scores['test_score']))
```

## 🔹 HistGradientBoosting (HGB)

- Gradient Boosting 개선 버전 (속도 ↑)
- 입력 특성을 **256개 구간(bin)**으로 나눠서 분할 후보 줄임 → 빠른 학습
- **NaN(결측치) 자동 처리** 가능

```python
hgb = HistGradientBoostingClassifier(random_state=42)
scores = cross_validate(hgb, X_train, y_train, return_train_score=True, n_jobs=-1)
print(np.mean(scores['train_score']), np.mean(scores['test_score']))
```

### 결측치 처리 방법 비교

**사전 처리 (Imputation)**
- 평균/중앙값 대체, KNN, MICE 등
- 모델 독립적, 도메인 지식 반영 가능

**HGB 자동 처리**
- NaN 그대로 넣어도 학습 가능
- 단, 다른 모델에는 적용 불가

## 🔹 XGBoost, LightGBM

- Gradient Boosting 라이브러리 (속도·성능 최적화)
- 대회/실무에서 많이 사용됨

```python
from xgboost import XGBClassifier
xgb = XGBClassifier(tree_method='hist', random_state=42)
xgb.fit(X_train, y_train)

from lightgbm import LGBMClassifier
lgb = LGBMClassifier(random_state=42)
lgb.fit(X_train, y_train)
```

***

# 3️⃣ 오늘 핵심 정리

## RandomizedSearchCV
- 확률분포에서 샘플링해 빠른 탐색
- **best_score_** = 교차검증 평균 성능

## 앙상블 학습
- **Random Forest**: 안정적, 과적합 방지, OOB 활용 가능
- **Extra Trees**: 더 무작위, 노이즈 많은 데이터에 유리
- **Gradient Boosting**: 잔차 학습 → 성능 높음, 느림
- **HistGradientBoosting**: 빠름, NaN 자동 처리
- **XGBoost / LightGBM**: 대회/실무 최강

