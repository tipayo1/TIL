<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" class="logo" width="120"/>

# 🗂️ 윈도우 함수 (Window Functions) 핵심 정리

## 🎯 윈도우 함수란?

> **윈도우 함수**란, *창문을 통해 주변을 보며 내 위치를 파악하는 함수*입니다.
> 즉, 전체 데이터 중 특정 "창(윈도우)"을 지정해 그 범위 내에서 각 행에 대해 연산을 수행합니다.

## 🏗️ 기본 구조

```sql
윈도우함수() OVER (
    PARTITION BY 그룹컬럼    -- 방 나누기 (선택사항)
    ORDER BY 정렬컬럼       -- 순서 정하기
    ROWS/RANGE BETWEEN ...  -- 범위 지정 (선택사항)
)
```


## 💡 일반 집계 함수와의 차이

| 구분 | 일반 집계 함수 | 윈도우 함수 |
| :-- | :-- | :-- |
| 결과 | 하나의 값 | 각 행마다 값 |
| 정보 유지 | ❌ 개별 행 정보 사라짐 | ✅ 개별 행 정보 유지 |
| 활용도 | 단순 집계 | 순위, 비교, 분석 |

## 🏆 1. 순위 함수들

### 📊 ROW_NUMBER() - 고유한 순번

```sql
ROW_NUMBER() OVER (ORDER BY amount DESC)
```

- **특징:** 동점자도 다른 번호
- **용도:** 페이징, 고유 식별번호
- **결과:** 1, 2, 3, 4, 5...


### 🥇 RANK() - 진짜 순위

```sql
RANK() OVER (ORDER BY amount DESC)
```

- **특징:** 동점자 같은 순위, 다음 순위 건너뛰기
- **용도:** 성적 순위, 매출 순위
- **결과:** 1, 2, 2, 4, 5...


### 🏅 DENSE_RANK() - 촘촘한 순위

```sql
DENSE_RANK() OVER (ORDER BY amount DESC)
```

- **특징:** 동점자 같은 순위, 연속 순위
- **용도:** 등급 분류, 레벨 시스템
- **결과:** 1, 2, 2, 3, 4...


#### 🎯 언제 어떤 순위 함수를 쓸까?

| 상황 | 함수 | 이유 |
| :-- | :-- | :-- |
| 게시판 페이징 | ROW_NUMBER | 고유 번호 필요 |
| 시험 성적 순위 | RANK | 동점자 처리 + 현실적 순위 |
| 상품 등급 분류 | DENSE_RANK | 연속된 등급 번호 |

## 🏠 2. PARTITION BY - 그룹별 분석

### 🎯 핵심 개념

- 전체 아파트 → 동별로 나누기 → 각 동에서 순위 매기기
- 전체 데이터 → 그룹별로 나누기 → 각 그룹에서 윈도우 함수 적용


### 💪 실무 활용 패턴

- **지역별 TOP N**

```sql
RANK() OVER (PARTITION BY region ORDER BY 총매출 DESC) = 1
```

- **카테고리별 인기 상품**

```sql
ROW_NUMBER() OVER (PARTITION BY category ORDER BY 총판매량 DESC) <= 3
```

- **월별 성과 분석**

```sql
RANK() OVER (PARTITION BY DATE_TRUNC('month', order_date) ORDER BY daily_sales DESC)
```


## 📊 3. 집계 윈도우 함수

### 💰 SUM() OVER() - 누적 합계

- **기본 누적**

```sql
SUM(amount) OVER (ORDER BY order_date)
```

→ 처음부터 현재까지 누적
- **그룹별 누적**

```sql
SUM(amount) OVER (PARTITION BY customer_id ORDER BY order_date)
```

→ 각 고객별로 누적 구매금액
- **월별 리셋 누적**

```sql
SUM(daily_sales) OVER (
    PARTITION BY DATE_TRUNC('month', order_date)
    ORDER BY order_date
)
```

→ 매월 1일부터 다시 누적


### 📈 AVG() OVER() - 이동 평균

- **최근 7일 이동 평균**

```sql
AVG(daily_sales) OVER (
    ORDER BY order_date
    ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
)
```

- **앞뒤 3일 평균 (총 7일)**

```sql
AVG(daily_sales) OVER (
    ORDER BY order_date
    ROWS BETWEEN 3 PRECEDING AND 3 FOLLOWING
)
```

- **전체 기간 평균**

```sql
AVG(daily_sales) OVER (
    ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
)
```


### 📅 ROWS vs RANGE 차이

| 구분 | ROWS | RANGE |
| :-- | :-- | :-- |
| 기준 | 행 개수 | 값의 범위 |
| 사용례 | "최근 7일" | "같은 날짜들" |
| 동점 처리 | 개별 처리 | 함께 처리 |

## 🔄 4. 이동 함수 (LAG, LEAD)

### ⬅️ LAG() - 과거 데이터 참조

- **기본 문법**

```sql
LAG(컬럼명, 단계수, 기본값) OVER (PARTITION BY 그룹 ORDER BY 정렬)
```

- **실무 활용**
    - 전월 대비:
`LAG(monthly_sales, 1) OVER (ORDER BY month) as 전월매출`
    - 전년 동월 대비:
`LAG(monthly_sales, 12) OVER (ORDER BY month) as 전년동월매출`
    - 고객별 이전 구매일:
`LAG(order_date, 1) OVER (PARTITION BY customer_id ORDER BY order_date)`


### ➡️ LEAD() - 미래 데이터 참조

- **실무 활용**
    - 다음 구매 예측:
`LEAD(order_date, 1) OVER (PARTITION BY customer_id ORDER BY order_date)`
    - 구매 간격 분석:
`LEAD(order_date) - order_date as 다음구매까지_간격`


## 📊 5. 분위수 함수들

### 🎯 NTILE() - 균등 분할

```sql
NTILE(4) OVER (ORDER BY 총구매금액)
```

- 4등급으로 균등하게 나누기
- **실무 활용**
    - 고객 등급: VIP(4), 골드(3), 실버(2), 브론즈(1)
    - 상품 분류: A급, B급, C급, D급
    - 성과 평가: 상위 25%, 중위 50%, 하위 25%


### 📈 PERCENT_RANK() - 백분위 순위

```sql
PERCENT_RANK() OVER (ORDER BY price)
```

- 0.85 → 상위 15%에 해당
- **실무 활용**
    - 가격 포지셔닝: "상위 10% 프리미엄 상품"
    - 성과 평가: "상위 5% 우수 사원"
    - 리스크 관리: "하위 20% 주의 고객"


## 🎯 6. FIRST_VALUE, LAST_VALUE

### 🥇 그룹별 최고/최저값 찾기

- **올바른 사용법**

```sql
FIRST_VALUE(product_name) OVER (
    PARTITION BY category
    ORDER BY price DESC
    ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
) as 최고가상품
```

- **주의사항:**
ROWS BETWEEN 구문 필수!
    - 잘못된 예시:

```sql
LAST_VALUE(price) OVER (PARTITION BY category ORDER BY price)
```

→ 현재 행까지만 보므로 잘못된 결과
    - 올바른 예시:

```sql
LAST_VALUE(price) OVER (
    PARTITION BY category ORDER BY price
    ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
)
```

→ 전체 그룹을 다 보고 판단


## ⚡ 7. 성능 최적화 팁

### 🔧 인덱스 전략

```sql
CREATE INDEX idx_orders_customer_date ON orders(customer_id, order_date);
CREATE INDEX idx_orders_date_amount ON orders(order_date, amount);
CREATE INDEX idx_orders_region_date ON orders(region, order_date);
```


### 📊 성능 고려사항

| 요소 | 좋은 성능 | 나쁜 성능 |
| :-- | :-- | :-- |
| ORDER BY | 인덱스 있음 | 인덱스 없음 |
| PARTITION BY | 카디널리티 적당 | 카디널리티 너무 높음 |
| 데이터량 | 필요한 만큼만 | 전체 테이블 스캔 |

## 🎯 8. 실무 활용 시나리오별 가이드

### 📈 매출 분석

```sql
WITH monthly_sales AS (...)
SELECT
    월,
    월매출,
    LAG(월매출, 1) OVER (ORDER BY 월) as 전월매출,
    AVG(월매출) OVER (ORDER BY 월 ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) as 3개월이동평균
FROM monthly_sales;
```


### 👥 고객 분석

```sql
SELECT
    customer_id,
    ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY order_date) as 구매순서,
    SUM(amount) OVER (PARTITION BY customer_id ORDER BY order_date) as 누적구매금액,
    LAG(order_date, 1) OVER (PARTITION BY customer_id ORDER BY order_date) as 이전구매일
FROM orders;
```


### 🏆 순위 분석

```sql
SELECT
    product_name,
    RANK() OVER (ORDER BY 총매출 DESC) as 매출순위,
    RANK() OVER (PARTITION BY category ORDER BY 총매출 DESC) as 카테고리내순위,
    NTILE(4) OVER (ORDER BY 총매출) as 매출등급
FROM product_sales;
```


## 💡 9. 자주 하는 실수들

- **PARTITION BY 빼먹기**
    - ❌ `RANK() OVER (ORDER BY amount)` (전체에서 순위)
    - ✅ `RANK() OVER (PARTITION BY region ORDER BY amount)` (지역별 순위)
- **ORDER BY 빼먹기**
    - ❌ `LAG(amount) OVER (PARTITION BY customer_id)` (순서 없음)
    - ✅ `LAG(amount) OVER (PARTITION BY customer_id ORDER BY order_date)`
- **LAST_VALUE에서 ROWS BETWEEN 안 쓰기**
    - ❌ `LAST_VALUE(price) OVER (ORDER BY price)`
    - ✅ `LAST_VALUE(price) OVER (ORDER BY price ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING)`
- **NULL 처리 안 하기**
    - ❌ `amount - LAG(amount) OVER (...)` (첫 행에서 NULL)
    - ✅ `COALESCE(amount - LAG(amount) OVER (...), 0)` (NULL 처리)

> 이 문서는 윈도우 함수의 핵심 개념과 실무 활용법, 자주 하는 실수까지 한눈에 볼 수 있도록 정리한 마크다운 예시입니다.
> 각 함수별 예제와 실전 패턴을 참고하여 SQL 분석 실력을 높여보세요!

