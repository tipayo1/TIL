# 🎯 TIL `03_ML_basic.md`

# Decision Tree & 교차검증

## 1️⃣ 데이터 준비

**데이터셋**: wine.csv
- **특징(feature)**: alcohol, sugar, pH
- **타깃(target)**: class

```python
X = wine[['alcohol', 'sugar', 'pH']]
y = wine['class']

# Train / Test 분리 (80:20)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
```

**선택**: StandardScaler로 데이터 스케일링
```python
ss = StandardScaler()
X_train_scaled = ss.fit_transform(X_train)
X_test_scaled = ss.transform(X_test)
```

***

## 2️⃣ One-Hot Encoding (OHE)

### 개념
- 범주형 데이터를 숫자 벡터로 변환
- 순서/크기 의미 없이 각 범주를 독립적으로 표현

**예시**:
| 색상(Color) | Label Encoding | One-Hot Encoding |
|-------------|----------------|------------------|
| Red         | 0              | 1 0 0           |
| Blue        | 1              | 0 1 0           |
| Green       | 2              | 0 0 1           |
| Red         | 0              | 1 0 0           |

```python
df_ohe = pd.get_dummies(df, columns=['Color'])
```

- ✅ **장점**: 순서 왜곡 방지
- ⚠️ **단점**: 범주 많으면 차원 폭발

***

## 3️⃣ 모델 학습

### 3-1. Logistic Regression

```python
lr = LogisticRegression()
lr.fit(X_train_scaled, y_train)
lr.score(X_train_scaled, y_train)  # 훈련 점수
lr.score(X_test_scaled, y_test)    # 테스트 점수
```

- `.predict_proba()`: 클래스별 확률
- `.coef_`, `.intercept_`: 선형 계수 확인

### 3-2. Decision Tree

```python
dt = DecisionTreeClassifier(random_state=42)
dt.fit(X_train_scaled, y_train)
dt.score(X_train_scaled, y_train)
dt.score(X_test_scaled, y_test)
```

### 트리 시각화

```python
plt.figure(figsize=(12,10))
plot_tree(dt, max_depth=2, filled=True, feature_names=['alcohol','sugar','pH'])
plt.show()
```

### 하이퍼파라미터

| 파라미터 | 설명 |
|----------|------|
| `max_depth` | 트리 최대 깊이 |
| `min_samples_split` | 노드를 분할하기 위한 최소 샘플 수 |
| `min_impurity_decrease` | 노드 분할 최소 불순도 감소 |

***

## 4️⃣ 교차검증 (Cross Validation)

- 훈련 데이터만 이용, 모델 일반화 성능 평가
- **K-Fold 기본값**: 5

```python
from sklearn.model_selection import cross_validate
scores = cross_validate(dt, X_train, y_train)
np.mean(scores['test_score'])
```

**폴드 수 변경 & 계층화**:
```python
from sklearn.model_selection import StratifiedKFold
splitter = StratifiedKFold(n_splits=10, shuffle=True, random_state=42)
scores = cross_validate(dt, X_train, y_train, cv=splitter)
```

⚠️ **Test set은 마지막 1회만 사용**

***

## 5️⃣ GridSearchCV: 하이퍼파라미터 튜닝

### 단계
1. 탐색할 하이퍼파라미터 정의
2. GridSearchCV 실행 (cv = 교차검증)
3. 최적 조합 확인: `gs.best_params_`
4. 최적 조합 모델로 전체 훈련 데이터 학습: `gs.best_estimator_`
5. 마지막 테스트 점수 확인

```python
params = {
    'min_impurity_decrease': np.arange(0.0001, 0.001, 0.0001),
    'max_depth': range(5, 20),
    'min_samples_split': range(2, 100, 10)
}

gs = GridSearchCV(
    DecisionTreeClassifier(random_state=42),
    param_grid=params,
    n_jobs=-1,
    cv=5
)

gs.fit(X_train, y_train)
print(gs.best_params_)   # 최적 하이퍼파라미터
print(gs.best_score_)    # 최적 파라미터의 평균 CV 점수
```

### 🔹 best_score_ 계산 방식

1. 후보 파라미터 조합별로 K-Fold CV 수행
2. 각 fold에서 검증 점수(test_score) 계산
3. fold별 점수 평균 → mean_test_score
4. 모든 후보 조합 중 최고 평균 점수 → best_score_

```python
# 내부 계산 개념
scores_fold = []
for train_idx, val_idx in KFold.split(X_train, y_train):
    model.fit(X_train[train_idx], y_train[train_idx])
    scores_fold.append(model.score(X_train[val_idx], y_train[val_idx]))
mean_score = np.mean(scores_fold)  # 후보 파라미터 평균 점수
```

⚠️ **Test set은 GridSearchCV 내부 계산에 절대 사용하지 않음**

***

## 6️⃣ 최종 모델 평가

```python
dt_best = gs.best_estimator_
dt_best.score(X_test, y_test)  # Test set 1회 평가
```

***

## 7️⃣ 시각화

- **Decision Tree 구조 확인**: `plot_tree(dt_best, filled=True, feature_names=[...])`
- 트리 깊이/불순도 제한 → 과적합 방지
- OHE 후 범주형 특성 시각화 → 모델 입력 확인

***

## 8️⃣ 핵심 포인트

### Train / Validation / Test
- **Validation** → Cross Validation으로 대체 가능
- **Test** → 최종 평가용, 1회만

### Decision Tree 과적합 주의
- `max_depth`, `min_samples_split`, `min_impurity_decrease` 조절

### GridSearchCV
- 하이퍼파라미터 튜닝 + 교차검증 동시 수행
- **best_score_** = 내부 CV에서 최적 파라미터 평균 검증 점수

### One-Hot Encoding
- 순서 왜곡 없이 범주형 데이터를 숫자로 변환

### 시각화
- 트리 구조 및 특징 중요도 이해에 도움
