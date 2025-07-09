# 🎯오늘 학습한 핵심 내용 TIL

# CTE(Common Table Expression) & 윈도우 함수들

## ✅ CTE vs Subquery vs View 비교표

| 항목        | CTE (WITH)                | 서브쿼리 (Inline View)         | VIEW (뷰)                    |
|-------------|--------------------------|-------------------------------|------------------------------|
| 정의 방식   | WITH name AS (...)       | 쿼리 안에 SELECT ... 바로 사용 | CREATE VIEW name AS ...      |
| 지속성      | ✖ 일회성 (한 쿼리 내)    | ✖ 일회성 (해당 구문 내)        | ✔ 영구 (DB에 저장됨)         |
| 재사용성    | ✖ (같은 쿼리 내에서만)   | ✖ (재사용 불가)                | ✔ 여러 쿼리에서 재사용       |
| 가독성      | ✔ 매우 좋음 (블록 이름)  | ✖ 복잡해지기 쉬움              | ✔ 깔끔함 (외부에서 보기 쉬움)|
| 계층/재귀   | ✔ 가능 (WITH RECURSIVE)  | ✖ 불가능                       | ✖ 불가능                    |
| 인덱스 사용 | ✔ 가능                   | ✔ 가능                         | ✔ 가능 (실행계획 주의)       |
| 파라미터    | ✖ 불가능                 | ✖ 불가능                       | ✖ 불가능 (함수 필요)         |
| 권한 제어   | ✖ 없음                   | ✖ 없음                         | ✔ 가능 (SELECT 권한 부여)    |
| 작성 목적   | 쿼리 구조 분리/가독성    | 즉석 사용                      | 공용 쿼리 저장/반복 사용     |

## ✅ 예제 비교

### 1. CTE (WITH절)
```sql
WITH high_salary AS (
  SELECT * FROM employees WHERE salary > 50000
)
SELECT name FROM high_salary WHERE department = 'Sales';
```

### 2. 서브쿼리 (Inline View)
```sql
SELECT name
FROM (
  SELECT * FROM employees WHERE salary > 50000
) AS high_salary
WHERE department = 'Sales';
```

### 3. VIEW
```sql
-- 미리 정의
CREATE VIEW high_salary AS
SELECT * FROM employees WHERE salary > 50000;

-- 나중에 재사용
SELECT name FROM high_salary WHERE department = 'Sales';
```

## ✅ 언제 무엇을 써야 할까?

| 상황                                 | 추천 도구         | 이유                                  |
|--------------------------------------|-------------------|---------------------------------------|
| 쿼리 복잡한데 쪼개고 싶을 때         | CTE               | 쿼리 블록 나눠서 가독성 향상          |
| 쿼리 한 번만 쓸 때                   | 서브쿼리          | 가장 단순한 방법                      |
| 반복해서 여러 쿼리에서 쓸 예정일 때  | VIEW              | 유지보수 편하고 권한 부여도 가능      |
| 재귀 구조 필요할 때 (조직도, 트리 등) | CTE (RECURSIVE)   | 유일하게 재귀 지원                    |
| 보안상 원본 테이블 숨기고 싶을 때     | VIEW              | SELECT 권한만 부여 가능               |

## ✨ 요약 한 줄

- **CTE:** 쿼리 내에서 구조를 정리, 가독성 향상
- **서브쿼리:** 가장 간단한 즉석용 쿼리
- **VIEW:** 자주 쓰는 쿼리를 영구적으로 저장, 재사용

## 🎯 CTE란 무엇인가?

### 📚 한 줄 정의
> CTE(Common Table Expression) = 복잡한 쿼리를 단계별로 나누어 해결하는 SQL의 임시 테이블

### 🏗️ 기본 구조
```sql
WITH 임시테이블명 AS (
    SELECT ... -- 단계별 쿼리
),
두번째테이블명 AS (
    SELECT ... -- 다음 단계 쿼리
)
SELECT ... -- 최종 결과
```

## 💡 CTE의 3가지 핵심 장점

1. **가독성 향상**
   - 복잡한 서브쿼리 대신 단계별로 명확하게 작성 가능

   ```sql
   -- 복잡한 서브쿼리
   SELECT * FROM orders WHERE amount > (
       SELECT AVG(amount) FROM orders WHERE region = (
           SELECT region FROM customers WHERE customer_id = 'CUST-001'
       )
   );

   -- CTE 사용
   WITH customer_region AS (
       SELECT region FROM customers WHERE customer_id = 'CUST-001'
   ),
   region_avg AS (
       SELECT AVG(amount) as avg_amount
       FROM orders o JOIN customer_region cr ON o.region = cr.region
   )
   SELECT * FROM orders o JOIN region_avg ra ON o.amount > ra.avg_amount;
   ```

2. **성능 향상**
   - 반복 계산을 한 번만 수행

   ```sql
   -- 중복 계산
   SELECT
       customer_id,
       (SELECT AVG(amount) FROM orders),
       amount - (SELECT AVG(amount) FROM orders)
   FROM orders;

   -- CTE 사용
   WITH avg_amount AS (
       SELECT AVG(amount) as avg_val FROM orders
   )
   SELECT customer_id, avg_val, amount - avg_val FROM orders, avg_amount;
   ```

3. **재사용성**
   - 동일한 CTE를 여러 번 활용 가능

   ```sql
   WITH monthly_sales AS (
       SELECT DATE_TRUNC('month', order_date) as month, SUM(amount) as sales
       FROM orders GROUP BY month
   )
   SELECT month, sales FROM monthly_sales WHERE sales > 1000000
   UNION ALL
   SELECT '평균' as month, AVG(sales) FROM monthly_sales;
   ```

## 🎯 CTE 활용 시나리오별 가이드

### 📈 시나리오 1: 단계별 계산이 필요한 경우

- **언제 사용?**
  - 전월 대비 증감률 계산
  - 누적 매출 분석
  - 복잡한 수식이 포함된 분석

- **실무 사례**
  ```sql
  WITH monthly_sales AS (
      SELECT DATE_TRUNC('month', order_date) as month, SUM(amount) as sales
      FROM orders GROUP BY month
  ),
  sales_with_prev AS (
      SELECT ms1.month, ms1.sales, ms2.sales as prev_sales
      FROM monthly_sales ms1
      LEFT JOIN monthly_sales ms2 ON ms1.month = ms2.month + INTERVAL '1 month'
  )
  SELECT month, sales,
         ROUND((sales - prev_sales) * 100.0 / prev_sales, 2) as growth_rate
  FROM sales_with_prev ORDER BY month;
  ```

### 🏆 시나리오 2: 복잡한 분류/등급화가 필요한 경우

- **언제 사용?**
  - 고객 등급 분류, ABC 분석, 성과 평가 시스템

- **실무 사례**
  ```sql
  WITH customer_stats AS (
      SELECT customer_id, 
      SUM(amount) as total_purchase, 
      COUNT(*) as order_count
      FROM orders GROUP BY customer_id
  ),
  purchase_thresholds AS (
      SELECT
          AVG(total_purchase) as avg_purchase,
          PERCENTILE_CONT(0.8) WITHIN GROUP (ORDER BY total_purchase) as vip_threshold
      FROM customer_stats
  ),
  customer_grades AS (
      SELECT cs.*,
             CASE
                 WHEN total_purchase >= pt.vip_threshold THEN 'VIP'
                 WHEN total_purchase >= pt.avg_purchase THEN '우수'
                 ELSE '일반'
             END as grade
      FROM customer_stats cs CROSS JOIN purchase_thresholds pt
  )
  SELECT grade, COUNT(*) as customers, AVG(total_purchase) as avg_sales
  FROM customer_grades GROUP BY grade;
  ```

### 🎯 시나리오 3: TOP N 분석 (윈도우 함수 대체)

- **언제 사용?**
  - 지역별 매출 상위 고객, 카테고리별 인기 상품, 부서별 성과 우수자

- **실무 사례**
  ```sql
  WITH regional_sales AS (
      SELECT c.region, c.customer_name, SUM(o.amount) as total_sales
      FROM customers c JOIN orders o ON c.customer_id = o.customer_id
      GROUP BY c.region, c.customer_name
  )
  SELECT region, customer_name, total_sales,
         (SELECT COUNT(*) + 1 FROM regional_sales rs2
          WHERE rs1.region = rs2.region AND rs2.total_sales > rs1.total_sales) as rank
  FROM regional_sales rs1
  WHERE (SELECT COUNT(*) FROM regional_sales rs2
         WHERE rs1.region = rs2.region AND rs2.total_sales > rs1.total_sales)  이 문서는 CTE와 서브쿼리, 뷰의 차이와 활용법을 실무 중심으로 정리한 Markdown 예시입니다.

         
```sql
-- pg-data-set.sql
-- 외래 키 제약 조건 때문에 순서대로 삭제
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS customers;
-- 고객 테이블 생성
CREATE TABLE customers (
    customer_id VARCHAR(20) PRIMARY KEY,
    customer_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE,
    phone VARCHAR(20),
    region VARCHAR(50),
    registration_date DATE,
    status VARCHAR(20) DEFAULT 'active'
);

-- 고객 데이터 삽입 (1,000명)
INSERT INTO customers (customer_id, customer_name, email, phone, region, registration_date, status)
SELECT 
    'CUST-' || LPAD(generate_series::text, 6, '0') as customer_id,
    '고객' || generate_series as customer_name,
    'customer' || generate_series || '@example.com' as email,
    '010-' || LPAD((random() * 9000 + 1000)::int::text, 4, '0') || '-' || LPAD((random() * 9000 + 1000)::int::text, 4, '0') as phone,
    (ARRAY['서울', '부산', '대구', '인천', '광주', '대전', '울산'])[floor(random() * 7) + 1] as region,
    '2023-01-01'::date + (random() * 365)::int as registration_date,
    CASE WHEN random() < 0.95 THEN 'active' ELSE 'inactive' END as status
FROM generate_series(1, 1000);

-- 상품 테이블 생성
CREATE TABLE products (
    product_id VARCHAR(20) PRIMARY KEY,
    product_name VARCHAR(200) NOT NULL,
    category VARCHAR(100),
    price DECIMAL(10, 2),
    stock_quantity INTEGER,
    supplier VARCHAR(100)
);

-- 상품 데이터 삽입 (500개)
INSERT INTO products (product_id, product_name, category, price, stock_quantity, supplier)
SELECT 
    'PROD-' || LPAD(generate_series::text, 5, '0') as product_id,
    (ARRAY['스마트폰', '노트북', '태블릿', '이어폰', '키보드', '마우스', '모니터', '스피커', '충전기', '케이블'])[floor(random() * 10) + 1] || ' ' || 
    (ARRAY['프리미엄', '스탠다드', '베이직', '프로', '울트라', '맥스'])[floor(random() * 6) + 1] || ' ' || generate_series as product_name,
    (ARRAY['전자제품', '컴퓨터', '액세서리', '모바일', '음향기기'])[floor(random() * 5) + 1] as category,
    (random() * 1900000 + 100000)::decimal(10,2) as price,
    (random() * 1000 + 10)::int as stock_quantity,
    '공급업체' || (floor(random() * 20) + 1)::text as supplier
FROM generate_series(1, 500);

-- 주문 테이블 생성
CREATE TABLE orders (
    order_id VARCHAR(20) PRIMARY KEY,
    customer_id VARCHAR(20) NOT NULL,
    product_id VARCHAR(20) NOT NULL,
    quantity INTEGER,
    unit_price DECIMAL(10, 2),
    amount DECIMAL(12, 2),
    order_date DATE,
    status VARCHAR(20),
    region VARCHAR(50),
    payment_method VARCHAR(20),
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

-- 스마트 주문 데이터 생성 (50,000건)
WITH customer_weights AS (
    -- 고객별 주문 가중치 설정 (현실적 분포)
    SELECT 
        customer_id,
        region,
        CASE 
            WHEN random() < 0.05 THEN 50    -- 5% 고객: VIP (많은 주문)
            WHEN random() < 0.15 THEN 20    -- 10% 고객: 우수 고객
            WHEN random() < 0.40 THEN 8     -- 25% 고객: 일반 고객
            WHEN random() < 0.70 THEN 3     -- 30% 고객: 가끔 구매
            WHEN random() < 0.90 THEN 1     -- 20% 고객: 가끔 구매
            ELSE 0                          -- 10% 고객: 미구매
        END as weight
    FROM customers
),
product_weights AS (
    -- 상품별 인기도 설정 (파레토 법칙 적용)
    SELECT 
        product_id,
        category,
        price,
        CASE 
            WHEN random() < 0.15 THEN 30    -- 15% 상품: 인기 상품
            WHEN random() < 0.35 THEN 15    -- 20% 상품: 보통 인기
            WHEN random() < 0.65 THEN 8     -- 30% 상품: 평균적 판매
            WHEN random() < 0.85 THEN 3     -- 20% 상품: 저조한 판매
            ELSE 1                          -- 15% 상품: 거의 안 팔림
        END as popularity
    FROM products
),
expanded_customers AS (
    -- 가중치에 따라 고객 확장
    SELECT 
        customer_id,
        region,
        row_number() OVER () as seq
    FROM customer_weights
    CROSS JOIN generate_series(1, weight)
    WHERE weight > 0
),
expanded_products AS (
    -- 가중치에 따라 상품 확장
    SELECT 
        product_id,
        category,
        price,
        row_number() OVER () as seq
    FROM product_weights
    CROSS JOIN generate_series(1, popularity)
),
random_combinations AS (
    -- 랜덤 조합 생성
    SELECT 
        ec.customer_id,
        ec.region,
        ep.product_id,
        ep.category,
        ep.price,
        row_number() OVER () as order_seq
    FROM (
        SELECT *, row_number() OVER (ORDER BY random()) as rn
        FROM expanded_customers
    ) ec
    JOIN (
        SELECT *, row_number() OVER (ORDER BY random()) as rn  
        FROM expanded_products
    ) ep ON ec.rn = ep.rn
    LIMIT 50000
)
INSERT INTO orders (order_id, customer_id, product_id, quantity, unit_price, amount, order_date, status, region, payment_method)
SELECT 
    'ORDER-' || LPAD(order_seq::text, 8, '0') as order_id,
    customer_id,
    product_id,
    (floor(random() * 5) + 1)::int as quantity,
    price * (0.8 + random() * 0.4) as unit_price, -- 상품 가격의 80~120%
    0 as amount, -- 나중에 계산
    '2024-01-01'::date + (random() * 210)::int as order_date,
    (ARRAY['pending', 'processing', 'shipped', 'delivered', 'cancelled'])[floor(random() * 5) + 1] as status,
    region,
    (ARRAY['card', 'cash', 'transfer', 'mobile'])[floor(random() * 4) + 1] as payment_method
FROM random_combinations;

-- 주문 금액 계산
UPDATE orders SET amount = quantity * unit_price;
```

```sql
-- pg-06-cte.sql


-- CTE (Common Table Expression) -> 쿼리 속의 '이름이 있는' 임시 테이블
-- 가독성: 복잡한 쿼리를 단계별로 나누어 이해하기 쉬움
-- 재사용: 한 번 정의한 결과를 여러 번 사용 가능
-- 유지보수: 각 단계별로 수정이 용이
-- 디버깅: 단계별로 결과를 확인할 수 있음

-- [평균 주문 금액] 보다 큰 주문들의 고객 정보

SELECT c.customer_name, o.amount
FROM customers c
INNER JOIN orders o ON c.customer_id=o.customer_id
WHERE o.amount > (SELECT AVG(amount) FROM orders)
LIMIT 10;

EXPLAIN ANALYSE  -- 1.58
WITH avg_order AS (
    SELECT AVG(amount) as avg_amount
    FROM orders
)
SELECT c.customer_name, o.amount, ao.avg_amount
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
JOIN avg_order ao ON o.amount > ao.avg_amount
LIMIT 10;


-- 서브쿼리가 여러 번 실행됨 (비효율적)
EXPLAIN ANALYSE  -- 4.75
SELECT 
    customer_id,
    (SELECT AVG(amount) FROM orders) as avg_amount,
    amount,
    amount - (SELECT AVG(amount) FROM orders) as diff
FROM orders
WHERE amount > (SELECT AVG(amount) FROM orders);


--
WITH region_summary AS (
	SELECT
		c.region AS 지역명,
		COUNT(DISTINCT c.customer_id) AS 고객수,
		COUNT(o.order_id) AS 주문수,
		COALESCE(AVG(o.amount), 0) AS 평균주문금액
	FROM customers c
	LEFT JOIN orders o ON c.customer_id=o.customer_id
	GROUP BY c.region
)
SELECT
	지역명,
	고객수,
	주문수,
	ROUND(평균주문금액) AS 평균주문금액
FROM region_summary rs
ORDER BY 고객수 DESC;


-- 1. 각 상품의 총 판매량과 총 매출액을 계산하세요
-- 2. 상품 카테고리별로 그룹화하여 표시하세요
-- 3. 각 카테고리 내에서 매출액이 높은 순서로 정렬하세요
-- 4. 각 상품의 평균 주문 금액도 함께 표시하세요

-- - 먼저 상품별 판매 통계를 CTE로 만들어보세요
-- - products 테이블과 orders 테이블을 JOIN하세요
-- - 카테고리별로 정렬하되, 각 카테고리 내에서는 매출액 순으로 정렬하세요

WITH product_sales AS (
	SELECT
		p.category AS 카테고리,
		p.product_name AS 제품명,
		p.price AS 상품가격,
		SUM(o.quantity) AS 총판매량,
		SUM(o.amount) AS 총매출액,
		COUNT(o.order_id) AS 주문건수,
		AVG(o.amount) AS 평균주문금액
	FROM products p
	LEFT JOIN orders o ON p.product_id=o.product_id
	GROUP BY p.category, p.product_name, p.price
)
SELECT
	카테고리,
	제품명,
	총판매량,
	총매출액,
	ROUND(평균주문금액) AS 평균주문금액,
	주문건수,
	상품가격
FROM product_sales
ORDER BY 카테고리, 총매출액 DESC;


-- 카테고리별 매출 비중 분석
WITH product_sales AS (
	SELECT
		p.category AS 카테고리,
		p.product_name AS 제품명,
		p.price AS 상품가격,
		SUM(o.quantity) AS 총판매량,
		SUM(o.amount) AS 제품총매출액,
		COUNT(o.order_id) AS 주문건수,
		AVG(o.amount) AS 평균주문금액
	FROM products p
	LEFT JOIN orders o ON p.product_id=o.product_id
	GROUP BY p.category, p.product_name, p.price
),
category_total AS (
	SELECT
		카테고리,
		SUM(제품총매출액) AS 카테고리총매출액
	FROM product_sales
	GROUP BY 카테고리
)
SELECT
	ps.카테고리,
	ps.제품명,
	ROUND(ps.제품총매출액 * 100 / ct.카테고리총매출액, 2) AS 카테고리매출비중
FROM product_sales ps
INNER JOIN category_total ct ON ps.카테고리=ct.카테고리
ORDER BY ps.카테고리, ps.제품총매출액 DESC;


-- 고객 구매금액에 따라 VIP(상위 20%) / 일반(전체평균보다 높음) / 신규(나머지) 로 나누어 등급통계를 보자.
-- [등급, 등급별 회원수, 등급별 구매액총합, 등급별 평균 주문수]

-- 1. 고객별 총 구매 금액 + 주문수
WITH customer_total AS (
	SELECT
		customer_id,
		SUM(amount) as 총구매액,
		COUNT(*) AS 총주문수
	FROM orders
	GROUP BY customer_id
),
-- 2. 구매 금액 기준 계산
purchase_threshold AS (
	SELECT
		AVG(총구매액) AS 일반기준,
		-- 상위 20% 기준값 구하기
		PERCENTILE_CONT(0.8) WITHIN GROUP (ORDER BY 총구매액) AS vip기준
	FROM customer_total
),
-- 3. 고객 등급 분류
customer_grade AS (
	SELECT
		ct.customer_id,
		ct.총구매액,
		ct.총주문수,
		CASE 
			WHEN ct.총구매액 >= pt.vip기준 THEN 'VIP'
			WHEN ct.총구매액 >= pt.일반기준 THEN '일반'
			ELSE '신규'
		END AS 등급
	FROM customer_total ct
	CROSS JOIN purchase_threshold pt
)
-- 4. 등급별 통계 출력
SELECT
	등급,
	COUNT(*) AS 등급별고객수,
	SUM(총구매액) AS 등급별총구매액,
	ROUND(AVG(총주문수), 2) AS 등급별평균주문수
FROM customer_grade
GROUP BY 등급

```

```sql
-- -- pg-07-recursive-cte.sql

-- CREATE TABLE employees (
--     employee_id INTEGER PRIMARY KEY,
--     employee_name VARCHAR(100) NOT NULL,
--     manager_id INTEGER REFERENCES employees(employee_id),
--     department VARCHAR(50),
--     position VARCHAR(50),
--     salary DECIMAL(10),
--     hire_date DATE,
--     level INTEGER
-- );

-- -- 조직도 데이터 삽입 (4단계 계층)
-- INSERT INTO employees VALUES
-- -- CEO (1단계)
-- (1, 'CEO 김대표', NULL, '경영진', 'CEO', 150000000, '2020-01-01', 1),
-- -- 이사급 (2단계)
-- (2, '이사 박영업', 1, '영업본부', '이사', 120000000, '2020-03-01', 2),
-- (3, '이사 최개발', 1, '개발본부', '이사', 120000000, '2020-03-01', 2),
-- (4, '이사 정마케팅', 1, '마케팅본부', '이사', 110000000, '2020-04-01', 2),
-- (5, '이사 한인사', 1, '인사본부', '이사', 110000000, '2020-04-01', 2),
-- -- 부장급 (3단계)
-- (6, '부장 김영업1', 2, '영업1팀', '부장', 90000000, '2020-06-01', 3),
-- (7, '부장 이영업2', 2, '영업2팀', '부장', 90000000, '2020-06-01', 3),
-- (8, '부장 박프론트', 3, '프론트엔드팀', '부장', 95000000, '2020-07-01', 3),
-- (9, '부장 최백엔드', 3, '백엔드팀', '부장', 95000000, '2020-07-01', 3),
-- (10, '부장 정마케팅', 4, '마케팅팀', '부장', 85000000, '2020-08-01', 3),
-- (11, '부장 한인사', 5, '인사팀', '부장', 85000000, '2020-08-01', 3),
-- -- 팀장급 (4단계)
-- (12, '팀장 김영업A', 6, '영업1팀', '팀장', 70000000, '2021-01-01', 4),
-- (13, '팀장 이영업B', 6, '영업1팀', '팀장', 70000000, '2021-01-01', 4),
-- (14, '팀장 박영업C', 7, '영업2팀', '팀장', 70000000, '2021-01-01', 4),
-- (15, '팀장 최영업D', 7, '영업2팀', '팀장', 70000000, '2021-01-01', 4),
-- (16, '팀장 정프론트', 8, '프론트엔드팀', '팀장', 75000000, '2021-02-01', 4),
-- (17, '팀장 한백엔드', 9, '백엔드팀', '팀장', 75000000, '2021-02-01', 4),
-- (18, '팀장 김마케팅', 10, '마케팅팀', '팀장', 65000000, '2021-03-01', 4),
-- (19, '팀장 이인사', 11, '인사팀', '팀장', 65000000, '2021-03-01', 4),
-- -- 사원급 (5단계)
-- (20, '사원 박영업1', 12, '영업1팀', '사원', 45000000, '2021-06-01', 5),
-- (21, '사원 최영업2', 12, '영업1팀', '사원', 45000000, '2021-06-01', 5),
-- (22, '사원 김영업3', 13, '영업1팀', '사원', 45000000, '2021-06-01', 5),
-- (23, '사원 이영업4', 14, '영업2팀', '사원', 45000000, '2021-07-01', 5),
-- (24, '사원 정영업5', 15, '영업2팀', '사원', 45000000, '2021-07-01', 5),
-- (25, '사원 한프론트1', 16, '프론트엔드팀', '사원', 50000000, '2021-08-01', 5),
-- (26, '사원 박프론트2', 16, '프론트엔드팀', '사원', 50000000, '2021-08-01', 5),
-- (27, '사원 최백엔드1', 17, '백엔드팀', '사원', 50000000, '2021-09-01', 5),
-- (28, '사원 김백엔드2', 17, '백엔드팀', '사원', 50000000, '2021-09-01', 5),
-- (29, '사원 이마케팅', 18, '마케팅팀', '사원', 40000000, '2021-10-01', 5),
-- (30, '사원 정인사', 19, '인사팀', '사원', 40000000, '2021-10-01', 5);

-- SELECT * FROM employees;


-- Recursive - 재귀

WITH RECURSIVE numbers AS (
	-- 초기값
	SELECT 1 as num
	--
	UNION ALL
	-- 재귀 부분
	SELECT num + 1
	FROM numbers
	WHERE num < 10
)
SELECT * FROM numbers;


WITH RECURSIVE calender AS (
	-- 1/1 은 제공
	SELECT '2024-01-01'::DATE as 날짜
	UNION ALL
	SELECT (날짜 + INTERVAL'1 day')::DATE
	FROM calender
	WHERE 날짜 < '2024-01-31'::DATE
)
SELECT
	날짜
FROM calender;

-- 대표부터 전체 조직도 확인
WITH RECURSIVE org_chart AS (
	SELECT
		employee_id,
		employee_name,
		manager_id,
		department,
		1 AS 레벨,
		employee_name::text AS 조직구조
	FROM employees
	WHERE manager_id is NULL  -- 대표 찾기
	UNION ALL
	SELECT
		e.employee_id,
		e.employee_name,
		e.manager_id,
		e.department,
		oc.레벨 + 1,  -- 2
		(oc.조직구조 || '>>' || e.employee_name)::text
	FROM employees e
	INNER JOIN org_chart oc ON e.manager_id=oc.employee_id  -- 박영업 내 상사인 사람들
)
SELECT 
  	*
FROM org_chart
ORDER BY 레벨;

-- 특정 인물을 첫줄에 배치 -> 해당 인물을 기준으로 부하 직원 확인하기
WITH RECURSIVE org_chart AS (
	SELECT
		employee_id,
		employee_name,
		manager_id,
		department,
		level,
		employee_name::text AS 조직구조
	FROM employees
	WHERE employee_name = '부장 김영업1'
	UNION ALL
	SELECT
		e.employee_id,
		e.employee_name,
		e.manager_id,
		e.department,
		e.level,
		(oc.조직구조 || '>>' || e.employee_name)::text
	FROM employees e
	INNER JOIN org_chart oc ON e.manager_id=oc.employee_id
)
SELECT 
  	*
FROM org_chart
ORDER BY level;

```

```sql
-- pg-08-window.sql

-- window 함수 -> OVER() 구문


-- 전체구매액 평균
SELECT AVG(amount) FROM orders;

-- 고객별 구매액 평균
SELECT
	AVG(amount)
FROM orders
GROUP BY customer_id;

-- 각 데이터와 전체 평균을 동시에 확인
SELECT
	order_id,
	customer_id,
	amount,
	AVG(amount) OVER() as 전체평균
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
	order_date,
	ROW_NUMBER() OVER (ORDER BY order_date DESC) as 최신주문순서,
	RANK() OVER (ORDER BY order_date DESC) as 랭크(올림픽),
	DENSE_RANK() OVER (ORDER BY order_date DESC) as 덴스랭크
FROM orders
ORDER BY 최신주문순서
LIMIT 20; --OFFSET 40;



-- 7월 매출 TOP 3 고객 찾기
-- [이름, 해당고객의 7월구입액, 순위]
SELECT
	order_id,
	customer_id,
	amount,
	ROW_NUMBER() OVER (ORDER BY amount DESC) as 월구입순위,
	RANK() OVER (ORDER BY amount DESC) as 월구입랭크,
	DENSE_RANK() OVER (ORDER BY amount DESC) as 월구입덴스랭크
FROM orders
ORDER BY 월구입순위
LIMIT 10;



-- 각 지역에서 매출 1위 고객 => ROW_NUMBER() 로 숫자를 매기고, 이 컬럼의 값이 1인 사람
-- [지역, 고객이름, 총판매액]
-- CTE
-- 1.
SELECT
	order_id,
	customer_id,
	amount,
	ROW_NUMBER() OVER (ORDER BY amount DESC) as 월구입순위,
	RANK() OVER (ORDER BY amount DESC) as 월구입랭크,
	DENSE_RANK() OVER (ORDER BY amount DESC) as 월구입덴스랭크
FROM orders
ORDER BY 월구입순위
LIMIT 10;



WITH customer_sales AS (
    SELECT
        c.region AS 지역,
        o.customer_id AS 고객ID,
        SUM(o.amount) AS 총판매액,
        ROW_NUMBER() OVER (
            PARTITION BY c.region
            ORDER BY SUM(o.amount) DESC
        ) AS 지역내_순위
    FROM orders o
    JOIN customers c ON o.customer_id = c.customer_id
    GROUP BY c.region, o.customer_id
)
SELECT 지역, 고객ID, 총판매액
FROM customer_sales
WHERE 지역내_순위 = 1
ORDER BY 지역;

```