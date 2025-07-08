# 🎯 오늘 학습한 핵심 내용 TIL

# D4 SQL 기초: 서브쿼리, JOIN, GROUP BY 실전 정리

---

## 🎯 오늘 배운 핵심 내용

- **서브쿼리 기초**: 쿼리 안의 쿼리로 조건 만들기
- **JOIN 기초**: 여러 테이블 연결하여 정보 합치기
- **GROUP BY + JOIN**: 연결된 데이터를 그룹별로 집계하기

---

## 🔍 1. 서브쿼리 (Subquery) - 쿼리 안의 쿼리

### 💡 서브쿼리란?
> 다른 쿼리의 결과를 조건이나 값으로 사용하는 쿼리  
> 예시: "평균보다 높은 매출의 주문들을 보여줘"

#### 단계별 예시

1. **평균 구하기**
    ```
    SELECT AVG(total_amount) FROM sales;  -- 결과: 612,862
    ```

2. **평균보다 높은 주문 찾기**
    ```
    SELECT * FROM sales WHERE total_amount > 612862;
    ```

3. **서브쿼리로 한 번에!**
    ```
    SELECT * FROM sales
    WHERE total_amount > (SELECT AVG(total_amount) FROM sales);
    ```

### 🎯 서브쿼리 기본 패턴

1. **평균과 비교**
    ```
    SELECT
        product_name,
        total_amount,
        total_amount - (SELECT AVG(total_amount) FROM sales) AS 평균차이
    FROM sales
    WHERE total_amount > (SELECT AVG(total_amount) FROM sales);
    ```

2. **최대/최소값 찾기**
    ```
    -- 가장 비싼 주문
    SELECT * FROM sales
    WHERE total_amount = (SELECT MAX(total_amount) FROM sales);

    -- 가장 최근 주문
    SELECT * FROM sales
    WHERE order_date = (SELECT MAX(order_date) FROM sales);
    ```

3. **목록에 포함된 것들 (IN)**
    ```
    -- VIP 고객들의 모든 주문
    SELECT * FROM sales
    WHERE customer_id IN (
        SELECT customer_id FROM customers
        WHERE customer_type = 'VIP'
    )
    ORDER BY total_amount DESC;

    -- 전자제품을 구매한 적 있는 고객들의 모든 주문
    SELECT * FROM sales
    WHERE customer_id IN (
        SELECT DISTINCT customer_id
        FROM sales
        WHERE category = '전자제품'
    );
    ```

### 💡 서브쿼리 핵심 포인트

- 괄호 필수: `(SELECT ...)`
- 단일 값 vs 여러 값: `=`는 단일 값, `IN`은 여러 값
- **실행 순서**: 서브쿼리 먼저 → 외부 쿼리 나중

---

## 🔗 2. JOIN - 테이블 연결하기

### 💡 JOIN이 왜 필요한가?

#### 문제 상황
- 고객 이름과 주문 정보를 함께 보고 싶을 때  
- **서브쿼리 방식** (비효율적, 성능 저하)
    ```
    SELECT
        customer_id,
        product_name,
        total_amount,
        (SELECT customer_name FROM customers WHERE customer_id = s.customer_id) AS customer_name,
        (SELECT customer_type FROM customers WHERE customer_id = s.customer_id) AS customer_type
    FROM sales s;
    ```
- **JOIN 방식** (간단, 효율적)
    ```
    SELECT
        c.customer_name,
        c.customer_type,
        s.product_name,
        s.total_amount
    FROM customers c
    INNER JOIN sales s ON c.customer_id = s.customer_id;
    ```

### 🎯 INNER JOIN vs LEFT JOIN

- **INNER JOIN** = 교집합 (양쪽에 데이터 있는 것만)
    ```
    SELECT c.customer_name, s.product_name
    FROM customers c
    INNER JOIN sales s ON c.customer_id = s.customer_id;
    ```
    > 주문 없는 고객은 결과에서 제외

- **LEFT JOIN** = 왼쪽 기준 (왼쪽은 다 보여줌)
    ```
    SELECT c.customer_name, s.product_name
    FROM customers c
    LEFT JOIN sales s ON c.customer_id = s.customer_id;
    ```
    > 주문 없는 고객도 나타남 (주문 정보는 NULL)

### 🔧 JOIN 기본 문법




```sql
-- 16-subquery1.sql
USE lecture;

-- 매출 평균보다 더 높은 금액을 주문한 판매데이터(*) 보여줘
SELECT AVG(total_amount) FROM sales;
SELECT * FROM sales WHERE total_amount > 612862;

-- 서브쿼리
SELECT * FROM sales 
WHERE total_amount > (SELECT AVG(total_amount) FROM sales);


SELECT
  product_name AS 이름,
  total_amount AS 판매액,
  total_amount - (SELECT AVG(total_amount) FROM sales) AS 평균차이
FROM sales
-- 평균보다 더 주문한 
WHERE total_amount > (SELECT AVG(total_amount) FROM sales);


-- 데이터가 하나 나오는 경우
SELECT AVG(quantity) FROM sales;

-- sales 에서 | 가장 비싼 주문을 한사람 -> total_amount
-- SELECT * FROM sales ORDER BY total_amount DESC LIMIT 1;

SELECT * FROM sales WHERE total_amount=(SELECT MAX(total_amount) FROM sales);

-- 가장 최근 주문일 | 의 주문데이터
SELECT * FROM sales
WHERE order_date=(SELECT MAX(order_date) FROM sales);

-- 가장 [주문액수 평균]과 실제 주문액수의 차이가 적은 데이터 5개

SELECT AVG(total_amount) FROM sales;

SELECT
  customer_id,
  product_name,
  order_date,
  total_amount,
  -- 평균과 주문사이의 차액
  ABS(
    (SELECT AVG(total_amount) FROM sales)
    -
    total_amount
  ) AS 평균과의차이
FROM sales
ORDER BY 평균과의차이
LIMIT 5
```

```sql
-- 17-subquery2.sql
USE lecture;
-- Scala -> 한개의 데이터
-- Vector -> 한줄로 이루어진 데이터
-- Matirx -> 행과 열로 이루어진 데이터
SELECT * FROM customers;

-- 모든 VIP의 id  (C001, C005, C010, C013, ... )
SELECT customer_id FROM customers WHERE customer_type = 'VIP';

-- 모든 VIP의 주문 내역
SELECT *
FROM sales
WHERE customer_id IN (
  SELECT customer_id FROM customers 
  WHERE customer_type = 'VIP'
)
ORDER BY total_amount DESC;

-- 전자 제품을 구매한 고객들 | 의 모든 주문
SELECT DISTINCT customer_id FROM sales WHERE category = '전자제품';

SELECT * FROM sales
WHERE customer_id IN (
  SELECT DISTINCT customer_id 
  FROM sales WHERE category = '전자제품'
);  -- 구매했던적이 있는 사람들을 넣기
```

```sql
-- p08.sql

-- practice DB에
USE practice;
-- lecture - sales, products 복사해오기
CREATE TABLE sales AS SELECT * FROM lecture.sales;
CREATE TABLE products AS SELECT * FROM lecture.products;
CREATE TABLE products AS SELECT * FROM lecture.customer;
SELECT * FROM sales;
SELECT * FROM products;
-- 단일값 서브쿼리
-- 1-1. 평균 이상 매출 주문들(성과가 좋은 주문들)
-- 평균
SELECT AVG(total_amount) FROM sales;
-- 평균 이상 주문들
SELECT
  *,
  ROUND((SELECT AVG(total_amount) FROM sales), 0) AS 전체평균,
  ROUND(total_amount - (SELECT AVG(total_amount) FROM sales), 0) AS 평균초과금액
FROM sales
WHERE total_amount >= (SELECT AVG(total_amount) FROM sales);


-- 1-2. 최고 매출 지역의 모든 주문들
-- 최고 매출 지역?
SELECT region
FROM sales
GROUP BY region
ORDER BY SUM(total_amount) DESC
LIMIT 1;

SELECT * FROM sales
WHERE region=(
  -- 최고 매출 지역
  SELECT region
  FROM sales
  GROUP BY region
  ORDER BY SUM(total_amount) DESC
  LIMIT 1
);

-- 여러데이터(벡터) 서브쿼리
-- 2-2. 재고 부족(50개 미만) 제품의 매출 내역
SELECT product_name FROM products
WHERE stock_quantity < 50;

SELECT * FROM sales
WHERE product_name IN (
  SELECT product_name FROM products
  WHERE stock_quantity < 50
);

-- 2-3. 상위 3개 매출 지역의 주문들
-- 매출 상위 3개 지역(벡터)
SELECT region
FROM sales
GROUP BY region
ORDER BY SUM(total_amount) DESC
LIMIT 3;

SELECT *
FROM sales
WHERE region IN (SELECT region
FROM sales
GROUP BY region
ORDER BY SUM(total_amount) DESC
LIMIT 3);


-- 2-4. 상반기(24-01-01 ~ 24-06-30) 에 주문한 고객들의 하반기(0701~1231) 주문 내역 (BETWEEN)
SELECT
    *,
    '하반기주문' AS 구분
FROM sales
WHERE customer_id IN (
    SELECT DISTINCT customer_id
    FROM sales
    WHERE order_date BETWEEN '2024-01-01' AND '2024-06-30'
)
AND order_date BETWEEN '2024-07-01' AND '2024-12-31'
ORDER BY customer_id, order_date;
```

```sql
-- 18-JOIN.sql
-- 고객정보 + 주문정보
USE lecture;

SELECT
  *,
  -- 지루하고 현학적임
  (
    SELECT customer_name FROM customers c
    WHERE c.customer_id=s.customer_id
  ) AS 주문고객이름,
  (
    SELECT customer_type FROM customers c
    WHERE c.customer_id=s.customer_id
  ) AS 고객등급
FROM sales s;

-- JOIN
SELECT
  COUNT(*)
FROM customers c
INNER JOIN sales s ON c.customer_id = s.customer_id;

-- LEFT JOIN -> 왼쪽 테이블(c) 의 모든 데이터와 + 매칭되는 오른쪽 데이터 | 매칭되는 오른쪽 데이터 (없어도 등장)
SELECT *
FROM customers c
LEFT JOIN sales s ON c.customer_id = s.customer_id;  
-- WHERE s.id IS NULL;  -> 한번도 주문한적 없는 사람들이 나온다;
```

```sql
-- 19-join-group.sql

USE lecture;
-- VIP 고객들의 구매 내역 조회 (고객명, 고객유형, 상품명, 카테고리, 주문금액)
SELECT *
FROM customers c
INNER JOIN sales s ON c.customer_id = s.customer_id
WHERE c.customer_type = 'VIP';


-- 각 등급별 구매액 평균
SELECT
  c.customer_type,
  AVG(s.total_amount)
FROM customers c
INNER JOIN sales s ON c.customer_id = s.customer_id
GROUP BY c.customer_type;

-- 18-JOIN.sql
-- 고객정보 + 주문정보
USE lecture;

SELECT
  *,
  -- 지루하고 현학적임
  (
    SELECT customer_name FROM customers c
    WHERE c.customer_id=s.customer_id
  ) AS 주문고객이름,
  (
    SELECT customer_type FROM customers c
    WHERE c.customer_id=s.customer_id
  ) AS 고객등급
FROM sales s;


-- INNER JOIN (교집합)
SELECT
  COUNT(*)
FROM customers c
INNER JOIN sales s ON c.customer_id = s.customer_id;


-- LEFT JOIN -> 왼쪽 테이블(c) 의 모든 데이터와 + 매칭되는 오른쪽 데이터 | 매칭되는 오른쪽 데이터 (없어도 등장)
SELECT *
FROM customers c
LEFT JOIN sales s ON c.customer_id = s.customer_id
WHERE s.id IS NULL;  -- -> 한번도 주문한적 없는 사람들이 나온다;
  

-- LEFT JOIN을 통한 [모든 고객]의 구매 현황 분석(구매를 하지 않았어도 분석)
SELECT
    c.customer_id,
    c.customer_name,
    c.customer_type,
    c.join_date,
    COUNT(s.id) AS 주문횟수,
    COALESCE(SUM(s.total_amount), 0) AS 총구매액,
    COALESCE(AVG(s.total_amount), 0) AS 평균주문액,
    COALESCE(MAX(s.order_date), '주문없음') AS 최근주문일,
    CASE
        WHEN COUNT(s.id) = 0 THEN '잠재고객'
        WHEN COUNT(s.id) >= 5 THEN '충성고객'
        WHEN COUNT(s.id) >= 4 THEN '일반고객'
        ELSE '신규고객'
    END AS 고객분류
FROM customers c
LEFT JOIN sales s ON c.customer_id = s.customer_id
GROUP BY c.customer_id, c.customer_name, c.customer_type, c.join_date
ORDER BY 총구매액 DESC;
```

```md
# TIL+

## DB는 대개 메모리보다 느린 디스크를 사용
- 디스크 접근 횟수를 줄이는게 매우 중요

## B+Tree
- B+Tree의 B는 Balance
- 모든 노드가 항상 정렬된 상태유지
범위 검색에 효율적 
- 리프노드가 연결리스트로 연결되어있어
연속적인 범위 검색에 매우 빠른 성능을 보인다
-내부 노드에 데이터가 없으므로 한 노드에 더 많은 인덱스를 저장할 수 있음
트리의 높이가 낮아짐

## 정렬 / 탐색
- 정렬은 탐색의 효율성을 높이기 위한 전처리 과정
```

