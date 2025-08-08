# 🎯 오늘 학습한 핵심 내용 TIL

## **제목:** KPI 분석 실습 데이터 + 문제 세트 (간소화)

**섹션:** 📊 실습 데이터셋 (3개 파일)
- customer_transactions.csv — 고객 정보 및 거래 내역
- marketing_performance.csv — 채널별 마케팅 성과  
- customer_satisfaction.csv — 고객 서비스 및 만족도

**섹션:** 데이터셋 생성 코드
**코드블록 (언어: python)**
```python
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# 시드 설정
np.random.seed(42)

# 1. 고객 및 거래 통합 데이터 (customer_transactions.csv)
customers_data = []
for customer_id in range(1, 1001):  # 1000명의 고객
    # 고객 기본 정보 - 2023년~2024년에 걸쳐 가입
    reg_date = datetime(2023, 1, 1) + timedelta(days=np.random.randint(0, 730))
    channel = np.random.choice(['organic', 'paid_search', 'social_media', 'email', 'referral'], 
                              p=[0.3, 0.25, 0.2, 0.15, 0.1])
    segment = np.random.choice(['premium', 'standard', 'basic'], p=[0.2, 0.6, 0.2])
    
    # 세그먼트별 거래 패턴
    if segment == 'premium':
        num_transactions = np.random.poisson(6) + 2
        base_value = 120
    elif segment == 'standard':
        num_transactions = np.random.poisson(3) + 1
        base_value = 70
    else:
        num_transactions = np.random.poisson(2) + 1
        base_value = 35
    
    # 각 고객의 거래 생성
    for trans_num in range(num_transactions):
        if trans_num == 0:
            trans_date = reg_date + timedelta(days=np.random.randint(0, 30))
        else:
            trans_date = reg_date + timedelta(days=np.random.randint(trans_num * 30, trans_num * 60 + 200))
        
        if trans_date  0 else np.random.poisson(500),
            'conversions': new_customers
        })

marketing_df = pd.DataFrame(marketing_data)

# 3. 고객 서비스 및 만족도 데이터 (customer_satisfaction.csv)
satisfaction_data = []
service_customers = np.random.choice(range(1, 1001), size=400, replace=False)

for customer_id in service_customers:
    num_contacts = np.random.poisson(2) + 1
    for contact_num in range(num_contacts):
        contact_date = datetime(2023, 6, 1) + timedelta(days=np.random.randint(0, 500))
        satisfaction_data.append({
            'customer_id': customer_id,
            'contact_date': contact_date,
            'contact_reason': np.random.choice(['billing', 'technical', 'product', 'shipping'],
                                            p=[0.3, 0.35, 0.25, 0.1]),
            'satisfaction_score': round(np.random.normal(4.1, 0.9), 1),
            'resolution_time_hours': round(np.random.exponential(8) + 1, 1),
            'repeat_contact': np.random.choice([True, False], p=[0.2, 0.8])
        })

satisfaction_df = pd.DataFrame(satisfaction_data)
satisfaction_df['satisfaction_score'] = satisfaction_df['satisfaction_score'].clip(1, 5)

# 데이터 저장
customer_transactions_df.to_csv('customer_transactions.csv', index=False)
marketing_df.to_csv('marketing_performance.csv', index=False)
satisfaction_df.to_csv('customer_satisfaction.csv', index=False)

print("✅ 실습용 데이터셋 생성 완료!")
print(f"- 고객-거래 레코드: {len(customer_transactions_df):,}건")
print(f"- 마케팅 성과 레코드: {len(marketing_df):,}건")
print(f"- 고객 만족도 레코드: {len(satisfaction_df):,}건")
```

**섹션:** 📋 상세 지침이 있는 문제 (2개)

**블록:** 💎 문제 1: 채널별 고객 획득 비용(CAC) 및 생애 가치(LTV) 분석
- **목표:** 마케팅 채널의 진정한 ROI를 평가하기 위해 CAC와 LTV를 계산하고 최적 투자 전략 제안
- **상세 지침:**
  1. **데이터 로드 및 전처리 (15분)**
     ```python
     import pandas as pd
     import numpy as np
     import matplotlib.pyplot as plt
     import seaborn as sns
     
     transactions = pd.read_csv('customer_transactions.csv')
     marketing = pd.read_csv('marketing_performance.csv')
     
     transactions['registration_date'] = pd.to_datetime(transactions['registration_date'])
     transactions['transaction_date'] = pd.to_datetime(transactions['transaction_date'])
     marketing['month'] = pd.to_datetime(marketing['month'])
     ```
  2. **채널별 CAC 계산 (20분)**
     - 2024년 데이터만 사용
     - 각 채널별 총 마케팅 비용 집계
     - 각 채널별 신규 고객 수 집계 (2024년 첫 거래 기준)
     - CAC = 총 마케팅 비용 / 신규 고객 수
     - organic, referral은 CAC = 0 처리
  3. **고객별 LTV 계산 (25분)**
     ```python
     customer_metrics = transactions.groupby('customer_id').agg({
         'order_value': ['sum', 'count', 'mean'],
         'transaction_date': ['min', 'max']
     }).reset_index()
     # 활동기간 계산 후 LTV = 총 구매금액 * (365 / 활동기간) * 예상수명(2년)
     ```
  4. **채널별 LTV 및 ROI 분석 (25분)**
     - 채널별 평균 LTV 계산
     - ROI = LTV / CAC (organic, referral은 무한대)
     - Payback period = CAC / 월평균 구매금액
  5. **시각화 및 전략 제안 (15분)**
     - CAC vs LTV 산점도
     - 채널별 ROI 막대 차트
     - 마케팅 예산 재배분 제안
- **기대 결과물:**
  - 채널별 CAC, LTV, ROI 요약 테이블
  - 시각화 차트 2개
  - 마케팅 예산 최적화 제안서 (150자 이상)

**블록:** 📊 문제 2: 고객 코호트 분석 및 유지율 개선 전략
- **목표:** 월별 가입 코호트의 유지율과 매출 기여도를 분석하여 고객 유지 전략 수립
- **상세 지침:**
  1. **코호트 그룹 생성 (20분)**
     ```python
     first_purchase = transactions.groupby('customer_id')['transaction_date'].min()
     first_purchase_month = first_purchase.dt.to_period('M')
     
     transactions_with_cohort = transactions.merge(
         first_purchase_month.reset_index().rename(columns={'transaction_date': 'cohort_month'}),
         on='customer_id'
     )
     ```
  2. **월별 유지율 계산 (30분)**
     - 코호트 대비 경과 개월 수 계산
     - 코호트별 Month 0,1,2,...12 활성 고객 수
     - 유지율 테이블(코호트 × 경과월), 평균 유지율 곡선
  3. **코호트별 매출 기여도 분석 (25분)**
     - 월별 누적 매출, 1인당 누적 매출(ARPU)
     - 6개월/12개월 후 예상 LTV 추정
  4. **유지율 히트맵 시각화 (15분)**
     ```python
     import seaborn as sns
     plt.figure(figsize=(12, 8))
     sns.heatmap(cohort_retention_table, annot=True, fmt='.1%', cmap='Blues')
     plt.title('코호트별 고객 유지율')
     ```
  5. **개선 전략 수립 (10분)**
     - 유지율 급감 시점 식별
     - 고성과 vs 저성과 코호트 특성 비교
     - 개선 액션 3가지 제안
- **기대 결과물:**
  - 코호트 유지율 히트맵
  - 코호트별 누적 매출 곡선 차트
  - 유지율 개선 전략 리포트 (200자 이상)

**섹션:** 🚀 자유도가 높은 문제 (2개)

**블록:** 🎯 오픈 문제 1: "최고 가치 고객" 발굴 및 확대 전략
- **목표:** 가장 큰 가치를 제공하는 고객군 식별 및 확대 전략 제시
- **리소스:** 3개 데이터셋 전체
- **분석 방향 힌트:**
  - 고객 세그멘테이션: RFM, 구매 패턴, 만족도
  - 고가치 고객의 공통 특성: 채널, 카테고리, 서비스 이용
  - 유사 특성 잠재 고객 타겟팅
- **제약 조건:**
  - 최소 2가지 이상의 분석 기법
  - 정량적 근거 포함, 실행 가능성과 기대 효과 제시
- **평가 기준:**
  - 분석 깊이/논리성 40%, 전략 35%, 시각화 25%

**블록:** 📈 오픈 문제 2: "숨겨진 비즈니스 기회" 탐지 및 수익화 방안
- **목표:** 미활용 패턴 발견을 통한 신규 매출 기회 창출
- **리소스:** 3개 데이터셋 전체
- **탐색 영역 예시:**
  - 교차 판매, 이탈 방지, 저활용 채널, 계절성, 만족도-매출 관계
- **제약 조건:**
  - 잠재 매출 영향 정량 추정
  - 실행 액션 플랜
  - 리스크와 완화 방안
- **평가 기준:**
  - 창의성/실현 가능성 35%, 데이터 근거 30%, 수익 잠재력 25%, 실행 계획 10%

**섹션:** 📚 실습 진행 가이드

**블록:** ⏰ 권장 시간 배분
- 상세 문제 1: 100분
- 상세 문제 2: 100분
- 오픈 문제 1: 120분
- 오픈 문제 2: 120분
- 발표 준비: 40분
- **총 소요시간: 약 8시간**

**블록:** 🎯 문제별 학습 목표
- 문제 1: CAC, LTV 계산 및 마케팅 ROI 분석
- 문제 2: 코호트 분석 및 고객 유지 전략
- 오픈 문제 1: 고객 세그멘테이션 및 타겟팅 전략
- 오픈 문제 2: 패턴 발견 및 비즈니스 기회 창출

**블록:** 💡 성공을 위한 팁
- **데이터 탐색 우선:** 각 문제 시작 전 데이터 구조와 분포를 충분히 파악
- **가설 수립:** 분석 전에 명확한 가설을 세우고 검증하는 접근
- **비즈니스 관점:** 단순 계산이 아닌 비즈니스 의사결정에 도움이 되는 인사이트 도출
- **시각화 활용:** 복잡한 분석 결과를 직관적으로 전달할 수 있는 차트 활용
- **실행 가능성:** 이론적 분석을 넘어서 실제 실행할 수 있는 액션 아이템 제시

**텍스트:** 이 실습을 통해 학생들은 실무 중심의 KPI 분석 역량을 체계적으로 습득할 수 있습니다! 🎯

***
