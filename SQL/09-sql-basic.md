# 🎯 오늘 학습한 핵심 내용 TIL



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




```sql
-- pg-08-window.sql
-- window 함수 -> OVER() 구문

-- 전체구매액 평균
SELECT AVG(amount) FROM orders;
-- 고객별 구매액 평균
SELECT
	customer_id,
	AVG(amount)
FROM orders
GROUP BY customer_id;

-- 각 데이터와 전체 평균을 동시에 확인
SELECT
	order_id,
	customer_id,
	amount,
	AVG(amount)	OVER() as 전체평균
FROM orders
LIMIT 10;

-- ROW_NUMBER() -> 줄세우기 [ROW_NUMBER() OVER(ORDER BY 정렬기준)]
-- 주문 금액이 높은 순서로
SELECT
	order_id,
	customer_id,
	amount,
	ROW_NUMBER() OVER (ORDER BY amount DESC) as 호구번호
FROM orders
ORDER BY 호구번호
LIMIT 20 OFFSET 40;

-- 주문 날짜가 최신인 순서대로 번호 매기기
SELECT
	order_id,
	customer_id,
	amount,
	order_date,
	ROW_NUMBER() OVER (ORDER BY order_date DESC) as 최신주문순서,
	RANK() OVER (ORDER BY order_date DESC) as 랭크,
	DENSE_RANK() OVER (ORDER BY order_date DESC) as 덴스랭크
FROM orders
ORDER BY 최신주문순서
LIMIT 20;

-- 7월 매출 TOP 3 고객 찾기
-- [이름, (해당고객)7월구매액, 순위]
-- CTE
-- 1. 고객별 7월의 총구매액 구하기 [고객id, 총구매액]
-- 2. 기존 컬럼에 번호 붙이기 [고객id, 구매액, 순위]
-- 3. 보여주기
WITH july_sales AS (
	SELECT
		customer_id,
		SUM(amount) AS 월구매액
	FROM orders
	WHERE order_date BETWEEN '2024-07-01' AND '2024-07-31'
	GROUP BY customer_id
),
ranking AS (
	SELECT
		customer_id,
		월구매액,
		ROW_NUMBER() OVER(ORDER BY 월구매액) AS 순위
	FROM july_sales
)
SELECT
	r.customer_id,
	c.customer_name,
	r.월구매액,
	r.순위
FROM ranking r
INNER JOIN customers c ON r.customer_id=c.customer_id
WHERE r.순위 <= 10;


-- 각 지역에서 총구매액 1위 고객 => ROW_NUMBER() 로 숫자를 매기고, 이 컬럼의 값이 1인 사람
-- [지역, 고객이름, 총구매액]
-- CTE
-- 1. 지역-사람별 "매출 데이터" 생성 [지역, 고객id, 이름, 해당 고객의 총 매출]
-- 2. "매출데이터" 에 새로운 열(ROW_NUMBER) 추가
-- 3. 최종 데이터 표시

WITH region_sales AS (
	SELECT
		c.region,
		c.customer_id,
		c.customer_name,
		SUM(o.amount) AS 고객별총매출
	FROM customers c
	INNER JOIN orders o ON c.customer_id=o.customer_id
	GROUP BY c.region, c.customer_id, c.customer_name
),
ranked_by_region AS (
	SELECT
		region AS 지역,
		customer_name AS 이름,
		고객별총매출,
		ROW_NUMBER() OVER(PARTITION BY region ORDER BY 고객별총매출 DESC) AS 지역순위
	FROM region_sales
)
SELECT
	지역,
	이름,
	고객별총매출,
	지역순위
FROM ranked_by_region
WHERE 지역순위 < 4;  -- 1~3위

```

```sql
-- pg-09-partition.sql

-- PARTITION BY -> 데이터를 특정 그룹으로 나누고, Window 함수로 결과를 확인
-- 동(1~4) | 층(15, 10, 20) | 호수 | 이름
-- 101 | 20 | 2001 |  <- 101동 에서는 1위
-- 102 | 15 | 2001 |  <- 102동 에서는 1위
-- 103 | 10 | 2001 |
-- 104 | 20 | 2001 |

-- 체육대회. 1, 2, 3 학년 -> 한번에 "학년 순위 | 전체 순위" 를 확인할 수 있다ㄴ

SELECT 
	region,
	customer_id,
	amount,
	ROW_NUMBER() OVER (ORDER BY amount DESC) AS 전체순위,
	ROW_NUMBER() OVER (PARTITION BY region ORDER BY amount DESC) AS 지역순위,
	RANK() OVER (ORDER BY amount DESC) AS 전체순위,
	RANK() OVER (PARTITION BY region ORDER BY amount DESC) AS 지역순위,
	DENSE_RANK() OVER (ORDER BY amount DESC) AS 전체순위,
	DENSE_RANK() OVER (PARTITION BY region ORDER BY amount DESC) AS 지역순위
FROM orders LIMIT 10;


-- SUM() OVER()
-- 일별 누적 매출액
WITH daily_sales AS (
	SELECT
		order_date,
		SUM(amount) AS 일매출
	FROM orders
	WHERE order_date BETWEEN '2024-06-01' AND '2024-08-31'
	GROUP BY order_date
	ORDER BY order_date
)
SELECT
	order_date,
	일매출,
	-- 범위 내에서 계속 누적
	SUM(일매출) OVER (ORDER BY order_date) as 누적매출,
	-- 범위 내에서, PARTITION 바뀔 때 초기화.
	SUM(일매출) OVER (
		PARTITION BY DATE_TRUNC('month', order_date)
		ORDER BY order_date
	) as 월누적매출
FROM daily_sales;

-- AVG() OVER()

WITH daily_sales AS (
	SELECT
		order_date,
		SUM(amount) AS 일매출
	FROM orders
	WHERE order_date BETWEEN '2024-06-01' AND '2024-08-31'
	GROUP BY order_date
	ORDER BY order_date
)
SELECT
	order_date,
	일매출,	
	ROUND(AVG(일매출) OVER(
		ORDER BY order_date
		ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
	)) AS 이동평균7일,
	ROUND(AVG(일매출) OVER(
		ORDER BY order_date
		ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
	)) AS 이동평균3일
FROM daily_sales;


-- 카테고리 별 인기 상품(매출순위) TOP 5
-- CTE
-- [상품 카테고리, 상품id, 상품이름, 상품가격, 해당상품의주문건수, 해당상품판매개수, 해당상품총매출]
-- 위에서 만든 테이블에 WINDOW함수 컬럼추가 + [매출순위, 판매량순위]
-- 총데이터 표시(매출순위 1 ~ 5위 기준으로 표시)
WITH product_sales AS (
	SELECT
		p.category,
		p.product_id,
		p.product_name,
		p.price,
		COUNT(o.order_id) AS 주문건수,
		SUM(o.quantity) AS 판매개수,
		SUM(o.amount) AS 총매출
	FROM products p
	LEFT JOIN orders o ON p.product_id = o.product_id
	GROUP BY p.category, p.product_id, p.product_name, p.price
),
ranked_products AS (
	SELECT
		*,
		DENSE_RANK() OVER (PARTITION BY category ORDER BY 총매출 DESC) AS 매출순위,
		DENSE_RANK() OVER (PARTITION BY category ORDER BY 판매개수 DESC) AS 판매량순위
	FROM product_sales
)
SELECT
	category, product_name, price, 주문건수, 판매개수, 총매출, 매출순위, 판매량순위
FROM ranked_products
WHERE 매출순위 <= 5
ORDER BY category, 매출순위;

	


















SELECT
	region,
	order_date,
	amount,
	AVG(amount) OVER (PARTITION BY region ORDER BY order_date) as 지역매출누적평균
FROM orders
WHERE order_date BETWEEN '2024-07-01' AND '2024-07-02';
```

```sql
-- pg-10-lag-lead.sql

-- LAG() - 이전 값을 가져온다.
-- 전월 대비 매출 분석
WITH monthly_sales AS (
	SELECT
		DATE_TRUNC('month', order_date) AS 월,
		SUM(amount) as 월매출
	FROM orders
	GROUP BY 월
),
compare_before AS (
	SELECT
		TO_CHAR(월, 'YYYY-MM') as 년월,
		월매출,
		LAG(월매출, 1) OVER (ORDER BY 월) AS 전월매출
	FROM monthly_sales
)
SELECT
	*,
	월매출 - 전월매출 AS 증감액,
	CASE
		WHEN 전월매출 IS NULL THEN NULL
		ELSE ROUND((월매출 - 전월매출) * 100 / 전월매출, 2)::TEXT || '%'
	END AS 증감률
FROM compare_before
ORDER BY 년월;


-- 고객별 다음 구매를 예측?
-- [고객id, 주문일, 구매액, 다음구매일, 다음구매액수]
-- 고객별로 PARTITION 필요
-- order by customer_id, order_date LIMIT 10;

SELECT
	customer_id,
	order_date,
	amount,
	LEAD(order_date, 1) OVER (PARTITION BY customer_id ORDER BY order_date) AS 다음구매일,
	LEAD(amount, 1) OVER (PARTITION BY customer_id ORDER BY order_date) AS 다음구매금액
FROM orders
WHERE customer_id='CUST-000001'
ORDER BY customer_id, order_date

-- [고객id, 주문일, 금액, 구매 순서(ROW_NUMBER),
-- 이전구매간격, 다음구매간격
-- 금액변화=(이번-저번), 금액변화율
-- 누적 구매 금액(SUM OVER)
-- [추가]누적 평균 구매 금액 (AVG OVER)
-- ]

WITH customer_orders AS (
	SELECT
		ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY order_date) AS 구매순서,
		customer_id,
		amount,
		LAG(amount, 1) OVER (PARTITION BY customer_id ORDER BY order_date) AS 이전구매금액,
		LAG(order_date, 1) OVER (PARTITION BY customer_id ORDER BY order_date) AS 이전구매일,
		order_date,
		LEAD(order_date, 1) OVER (PARTITION BY customer_id ORDER BY order_date) AS 다음구매일
	FROM orders
)
SELECT
	customer_id,
	order_date,
	amount,
	구매순서,
	-- 구매 간격
	order_date - 이전구매일 AS 이전구매간격,
	다음구매일 - order_date AS 다음구매간격,
	-- 구매금액변화
	amount - 이전구매금액 AS 금액변화,
	CASE
		WHEN 이전구매금액 IS NULL THEN NULL
		ELSE ROUND((amount - 이전구매금액) * 100 / 이전구매금액, 2)::TEXT || '%'
	END AS 금액변화율,
	--  누적 구매 통계
	SUM(amount) OVER (PARTITION BY customer_id ORDER BY order_date) AS 누적구매금액,
	AVG(amount) OVER (
		PARTITION BY customer_id
		ORDER BY order_date
		ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW  -- 현재 확인중인 ROW 부터 맨 앞까지
		-- ROWS BETWEEN 2 PRECEDING AND CURRENT ROW  -- 현재 확인중인 ROW 포함 총 3개
	) AS 평균구매금액,
	-- 고객 구매 단계 분류
	CASE
		WHEN 구매순서 = 1 THEN '첫구매'
		WHEN 구매순서 <= 3 THEN '초기고객'
		WHEN 구매순서 <= 10 THEN '일반고객'
		ELSE 'VIP고객'
	END AS 고객단계
FROM customer_orders
ORDER BY customer_id, order_date;
	
	




```


```sql
-- pg-11-ntile-percent.sql
-- NTILE 균등하게 나누기 NTILE(4) 4등분
-- NTILE(4) OVER (ORDER BY 총구매금액) AS 4분위  

WITH customer_totals AS (
	SELECT
		customer_id,
		SUM(amount) AS 총구매금액,
		COUNT(*) AS 구매횟수
	FROM orders
	GROUP BY customer_id
),
customer_grade AS (
	SELECT
		customer_id,
		총구매금액,
		구매횟수,
		NTILE(4) OVER (ORDER BY 총구매금액) AS 분위4,
		NTILE(10) OVER (ORDER BY 총구매금액) AS 분위10
	FROM customer_totals
	ORDER BY 총구매금액 DESC
)
SELECT
	c.customer_name,
	cg.총구매금액,
	cg.구매횟수,
	CASE
		WHEN 분위4=1 THEN 'Bronze'
		WHEN 분위4=2 THEN 'Silver'
		WHEN 분위4=3 THEN 'Gold'
		WHEN 분위4=4 THEN 'VIP'
	END AS 고객등급
FROM customer_grade cg
INNER JOIN customers c ON cg.customer_id=c.customer_id;

-- PERCNET_RANK()
SELECT
	product_name,
	category,
	price,
	RANK() OVER (ORDER BY price) AS 가격순위,
	PERCENT_RANK() OVER (ORDER BY price)AS 백분위순위,
	CASE
		WHEN PERCENT_RANK() OVER (ORDER BY price) >= 0.9 THEN '최고가(상위10%)'
		WHEN PERCENT_RANK() OVER (ORDER BY price) >= 0.7 THEN '고가(상위30%)'
		WHEN PERCENT_RANK() OVER (ORDER BY price) >= 0.3 THEN '중간가(상위70%)'
		ELSE '저가(하위30%)'
	END 가격등급
FROM products;

-- 카테고리별 처음등장/마지막등장 (파티션의 처음/마지막을 찾는 윈도우함수)
SELECT
	category,
	product_name,
	price,
	FIRST_VALUE(product_name) OVER (
		PARTITION BY category
		ORDER BY price DESC
		ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING  -- 파티션의 모든 행을 봐라
	) AS 최고가상품명,
	FIRST_VALUE(price) OVER (
		PARTITION BY category
		ORDER BY price DESC
		ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
	) AS 최고가격,
	LAST_VALUE(product_name) OVER (
		PARTITION BY category
		ORDER BY price DESC
		ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
	) AS 최저가상품명,
	LAST_VALUE(price) OVER (
		PARTITION BY category
		ORDER BY price DESC
		ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
	) AS 최저가격
FROM products;

```
