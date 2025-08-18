# 🎯 오늘 학습한 핵심 내용 TIL

***

# EDA 상관관계 분석 요약노트 📚

## 🎯 핵심 개념 요약

### 상관관계 분석이란?
두 변수 간의 선형/비선형 관계를 정량적으로 측정하여 비즈니스 인사이트를 도출하는 과정

**🔑 핵심 원칙:**
- 상관관계 ≠ 인과관계
- 데이터 타입에 따른 적절한 측정 방법 선택
- 혼란변수 통제의 중요성
- 비즈니스 액션으로 연결되는 실무 인사이트

***

## 📊 1교시: 기본 상관관계 분석

### 핵심 학습 내용
- Online Retail 데이터 전처리 및 고객별 집계
- RFM 분석 기반 고객 특성 변수 생성
- 피어슨 vs 스피어만 상관계수 비교

### 주요 발견사항
- **총매출 vs 구매빈도**: 0.89 (매우 강한 양의 상관)
- **구매빈도 vs 상품다양성**: 0.73 (강한 양의 상관)
- **평균단가 vs 구매빈도**: -0.32 (중간 음의 상관)

### 실무 적용
- **매출 전략**: 구매빈도 ↑ = 직접적 매출 증대
- **상품 전략**: 다양성 확대로 크로스셀링 효과
- **가격 전략**: 가격 상승 시 구매빈도 감소 고려

### 핵심 코드
```python
# 기본 상관관계 분석
correlation_matrix = df.corr()
sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm')

# 스피어만 상관계수
spearman_corr = df.corr(method='spearman')
```

***

## 🌀 2교시: 비선형 상관관계와 고급 측정

### 핵심 학습 내용
- 켄달 타우 (이상값에 강건한 순위 상관)
- 상호정보량 (Mutual Information)
- 조건부 상관관계 (고객 세그먼트별)
- U자형/포화점 관계 탐지

### 고급 측정 기법

| 기법 | 특징 | 활용 상황 |
|------|------|-----------|
| Distance Correlation | 0이면 완전독립 | 일반적 비선형 관계 |
| MIC (MINE) | 형태에 공평한 측정 | 다양한 패턴 탐색 |
| Kendall τ | 이상값에 강건 | 로버스트 분석 |
| Mutual Information | 정보이론 기반 | 특성 선택 |

### 비선형 패턴 발견
- **U자형**: 중간 가격대에서 최적 구매빈도
- **포화점**: 상품 다양성 증가 → 매출 증가 → 포화
- **지수적**: 구매주기와 Recency 관계

### 핵심 코드
```python
from scipy.stats import kendalltau
from sklearn.feature_selection import mutual_info_regression
import dcor

# 켄달 타우
tau, p_value = kendalltau(x, y)

# 상호정보량
mi_score = mutual_info_regression(X.reshape(-1, 1), y)

# Distance Correlation
dcor_value = dcor.distance_correlation(x, y)
```

***

## 🏷️ 3교시: 범주형 변수와 혼합형 연관성

### 핵심 학습 내용
- 국가별/시간대별 구매 패턴 차이 분석
- 카이제곱 검정과 Cramér's V
- 상관비(η²)로 범주형→수치형 영향 측정
- ANOVA를 통한 그룹 간 차이 검정

### 범주형 연관성 측정

| 측정 방법 | 데이터 타입 | 해석 |
|-----------|-------------|------|
| Cramér's V | 범주형-범주형 | 0-1, 1에 가까울수록 강한 연관 |
| Theil's U | 범주형-범주형 | 비대칭 연관성 (정보흐름) |
| η² (상관비) | 범주형-수치형 | 범주형이 수치형에 미치는 영향 |
| φk (Phi_k) | 혼합형 | 모든 타입에서 일관된 측정 |

### 주요 발견사항
- **국가별 차이**: 영국 vs 기타국가 구매패턴 상이
- **시간대별 패턴**: 10-15시 거래량 집중
- **요일별 차이**: 주중 vs 주말 구매액 차이

### 핵심 코드
```python
from scipy.stats import chi2_contingency
import scipy.stats as stats

# Cramér's V 계산
def cramers_v(x, y):
    confusion_matrix = pd.crosstab(x, y)
    chi2 = chi2_contingency(confusion_matrix)[0]
    n = confusion_matrix.sum().sum()
    return np.sqrt(chi2 / (n * (min(confusion_matrix.shape) - 1)))

# 상관비 (eta-squared)
def eta_squared(categorical, continuous):
    groups = [continuous[categorical == cat] for cat in categorical.unique()]
    return stats.f_oneway(*groups)
```

***

## 🎯 4교시: 편상관, 조건부 독립성, 인과관계

### 핵심 학습 내용
- 편상관으로 혼란변수 통제 효과 측정
- Fisher's Z 검정으로 편상관 유의성 검증
- 조건부 독립성 테스트
- 인과관계 추론 가이드라인

### 편상관과 부분상관
편상관(Partial Correlation): 제3변수의 영향을 제거한 후 두 변수 간 순수한 관계 측정

```
r_xy.z = (r_xy - r_xz × r_yz) / √((1-r_xz²)(1-r_yz²))
```

### 조건부 독립성
- **X ⊥ Y | Z**: Z가 주어졌을 때 X와 Y가 독립
- Fisher's Z 검정으로 유의성 확인
- p-value > 0.05면 조건부 독립

### 인과관계 추론 조건
✅ **시간적 선후관계**: 원인이 결과보다 앞선다  
✅ **통계적 연관성**: 상관관계 존재  
✅ **혼란변수 통제**: 제3변수 영향 제거  
✅ **도메인 지식**: 비즈니스 논리적 타당성  

### 매개변수 분석
**직접효과 vs 간접효과**: 매개변수를 통한 영향 경로 분석
- 총효과 = 직접효과 + 간접효과
- 매개효과 = a × b (경로계수의 곱)

***

## 📋 실무 활용 체크리스트

### 🔍 분석 전 준비
- [ ] 비즈니스 문제와 분석 목적 명확화
- [ ] 데이터 타입별 적절한 측정방법 선택
- [ ] 혼란변수(confounding variables) 사전 식별
- [ ] 도메인 지식 기반 가설 설정

### 📊 분석 단계별 체크
- [ ] **1단계**: 기본 상관관계로 전체 패턴 파악
- [ ] **2단계**: 비선형 관계 탐지 (산점도 + 고급기법)
- [ ] **3단계**: 범주형 변수 연관성 분석
- [ ] **4단계**: 편상관으로 혼란변수 통제
- [ ] **5단계**: 조건부 독립성으로 진짜 관계 식별

### 💼 결과 해석 및 적용
- [ ] 상관관계와 인과관계 구분하여 해석
- [ ] 통계적 유의성과 실무적 의미 동시 고려
- [ ] 비즈니스 액션 아이템 도출
- [ ] ROI 관점에서 우선순위 설정

***

## 🚀 실무 적용 베스트 프랙티스

### 📈 매출 증대 전략 우선순위
1. **구매빈도 증대** (상관계수: 0.8+)
   - 리타겟팅 캠페인, 구매 알림
2. **상품 다양성 확대** (상관계수: 0.6+)
   - 크로스셀링, 번들 상품
3. **장바구니 크기 증대** (상관계수: 0.4+)
   - 무료배송 임계값, 묶음할인
4. **적정 가격 정책** (음의 상관 고려)
   - 가격 탄력성 기반 최적화

### 🎯 고객 세그멘테이션 전략
- **VIP 고객**: 높은 단가-빈도 동시 만족
- **가격민감 고객**: 할인 중심 마케팅
- **다양성 추구 고객**: 신상품 우선 노출
- **충성 고객**: 정기구매 프로그램

### 🌍 글로벌 전략
- **국가별 차별화**: Cramér's V > 0.3인 변수 기준
- **시간대 최적화**: 피크타임 마케팅 집중
- **문화적 차이 반영**: 범주형 연관성 패턴 활용

***

## 🛠️ 핵심 코드 스니펫

### 종합 상관관계 분석 함수
```python
def comprehensive_correlation_analysis(df):
    """종합적인 상관관계 분석 수행"""
    results = {}
    
    # 피어슨 상관계수
    results['pearson'] = df.corr()
    
    # 스피어만 상관계수
    results['spearman'] = df.corr(method='spearman')
    
    # 켄달 타우
    results['kendall'] = df.corr(method='kendall')
    
    return results

# 사용 예시
corr_results = comprehensive_correlation_analysis(customer_df)
```

### 범주형 연관성 분석
```python
def categorical_association_analysis(cat1, cat2):
    """범주형 변수 간 연관성 분석"""
    # 교차표 생성
    crosstab = pd.crosstab(cat1, cat2)
    
    # 카이제곱 검정
    chi2, p_value, dof, expected = chi2_contingency(crosstab)
    
    # Cramér's V 계산
    n = crosstab.sum().sum()
    cramers_v = np.sqrt(chi2 / (n * (min(crosstab.shape) - 1)))
    
    return {
        'chi2': chi2,
        'p_value': p_value,
        'cramers_v': cramers_v,
        'crosstab': crosstab
    }
```

***

## 💡 핵심 인사이트 정리

### 🎯 Online Retail 데이터 주요 발견
- **매출 공식**: 총매출 = 구매횟수 × 평균구매액
- **최적 전략**: 빈도 ↑ > 단가 ↑ (상관계수 크기 기준)
- **세그먼트 효과**: VIP vs 일반고객 다른 상관 패턴
- **지역 차이**: 국가별 구매패턴 η² > 0.4 (강한 연관)

### ⚠️ 주의사항 (Common Pitfalls)
- 상관관계 ≠ 인과관계 (Simpson's Paradox 주의)
- 이상값이 상관계수에 미치는 왜곡 효과
- 다중비교 시 1종 오류 증가 (FDR 교정 필요)
- 비선형 관계를 선형 측정으로 놓치는 경우

***
