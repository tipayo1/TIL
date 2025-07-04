# 🎯 오늘 배운 SQL 핵심 내용 정리

## 1. UNION: 여러 쿼리 결과 합치기

**UNION**  
- 여러 SELECT 쿼리의 결과를 **세로(행 방향)**로 합치는 SQL 연산자  
- **중복 행을 자동으로 제거**하며, 컬럼 개수와 데이터 타입이 모두 일치해야 함  
- 성능상 **UNION ALL**보다 느릴 수 있음 (중복 제거 작업 때문)[1][5][6]

**UNION ALL**  
- 여러 SELECT 쿼리 결과를 **중복까지 모두 포함**하여 합침  
- 중복 제거 과정이 없어 **더 빠름**[2][5][7]

| 구분      | 중복 제거 | 속도       | 사용 예시                                 |
|-----------|-----------|------------|-------------------------------------------|
| UNION     | O         | 느림       | SELECT ... UNION SELECT ...               |
| UNION ALL | X         | 빠름       | SELECT ... UNION ALL SELECT ...           |

> **주의:**  
> - 모든 SELECT문의 **컬럼 수와 타입이 일치**해야 함  
> - 컬럼명은 **첫 번째 SELECT문의 컬럼명**을 따름  
> - `ORDER BY`는 전체 UNION 쿼리의 마지막에만 사용 가능[6]

**실전 예시**
```sql
SELECT '고객 테이블' AS 구분, COUNT() AS 데이터수 FROM customers
UNION ALL
SELECT '매출 테이블' AS 구분, COUNT() AS 데이터수 FROM sales;
```

---

## 2. 서브쿼리 반환 유형

| 유형      | 반환값        | 사용 위치         | 연산자             | 예시                                 |
|-----------|---------------|-------------------|--------------------|--------------------------------------|
| 스칼라    | 1행 1열       | SELECT, WHERE     | =, >, <            | WHERE amount > (SELECT AVG(...))     |
| 벡터      | 여러 행 1열   | WHERE, HAVING     | IN, ANY, ALL       | WHERE id IN (SELECT ...)             |
| 매트릭스  | 여러 행 여러열| FROM, EXISTS      | EXISTS             | WHERE EXISTS (SELECT ...)            |

**예시**
- **스칼라:**  
    ```
    SELECT product_name, total_amount,
           (SELECT AVG(total_amount) FROM sales) AS 전체평균
    FROM sales
    WHERE total_amount > (SELECT AVG(total_amount) FROM sales);
    ```
- **벡터:**  
    ```
    SELECT * FROM sales
    WHERE customer_id IN (
        SELECT customer_id FROM customers WHERE customer_type = 'VIP'
    );
    ```
- **매트릭스(Inline View):**  
    ```
    SELECT c.customer_name
    FROM customers c
    WHERE EXISTS (
        SELECT s.customer_id
        FROM sales s
        WHERE s.customer_id = c.customer_id
        AND s.total_amount >= 1000000
    );
    ```

---

## 3. Inline View & View (가상 테이블)

### Inline View (인라인 뷰)
- **FROM 절에 사용하는 서브쿼리**
- 실행 시점에만 존재하는 **임시 테이블**
- 복잡한 집계, 추가 조건이 필요한 분석에 활용
```sql
SELECT *
FROM (
SELECT category, AVG(total_amount) AS 평균매출
FROM sales s
JOIN products p ON s.product_id = p.product_id
GROUP BY category
) AS category_stats
WHERE 평균매출 >= 500000;
```

### View (뷰)
- 복잡한 쿼리를 **재사용 가능한 가상 테이블**로 저장
- 데이터베이스에 **영구적으로 저장**되며, 반복 사용 가능

```sql
CREATE VIEW customer_summary AS
SELECT c.customer_id, c.customer_name, c.customer_type,
COUNT(s.id) AS 주문횟수,
COALESCE(SUM(s.total_amount), 0) AS 총구매액
FROM customers c
LEFT JOIN sales s ON c.customer_id = s.customer_id
GROUP BY c.customer_id, c.customer_name, c.customer_type;
``` 


| 구분        | Inline View      | View                |
|-------------|------------------|---------------------|
| 저장 여부   | 일회용           | 데이터베이스에 저장 |
| 재사용      | 불가능           | 가능                |
| 성능        | 매번 실행        | 한 번 정의 후 재사용|
| 용도        | 복잡한 일회성 분석| 자주 사용하는 쿼리 |

---

## 4. SQL 작성 주의사항

### JOIN 관련
- **테이블 별명(Alias) 필수**  
    ```
    SELECT c.customer_name, s.product_name
    FROM customers c
    JOIN sales s ON c.customer_id = s.customer_id;
    ```
- **JOIN 조건 누락 주의** (카르테시안 곱 방지)
- **LEFT JOIN에서 COUNT(*) 대신 특정 컬럼 사용** (주문 없을 때 0 처리)

### GROUP BY 관련
- SELECT 컬럼은 **GROUP BY에 모두 포함**
- **WHERE**: 그룹핑 전 조건 / **HAVING**: 그룹핑 후 조건

### 서브쿼리 관련
- **스칼라 서브쿼리는 단일 값만 반환**
- **LEFT JOIN 시 NULL 처리**  
    ```
    COALESCE(SUM(s.total_amount), 0) AS 총구매액
    ```

---

## 💡 핵심 패턴 & 체크리스트

- **단계별 분해:** 복잡한 문제는 작은 단위로 쪼개기
- **인라인 뷰:** 집계 후 추가 조건 필터링에 활용
- **JOIN:** 상황에 맞는 JOIN 유형 선택 (INNER vs LEFT)
- **NULL 처리:** LEFT JOIN 시 항상 고려

**SQL 작성 체크리스트**
- 테이블 별명 사용했나?
- JOIN 조건 정확한가?
- GROUP BY에 필요한 컬럼 모두 포함했나?
- LEFT JOIN에서 COUNT(특정컬럼) 사용했나?
- NULL 값 처리했나?
- 서브쿼리 반환 유형 맞나?


```sql
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

```sql
-- p09.sql
USE practice;

DROP TABLE sales;
DROP TABLE products;
DROP TABLE customers;

CREATE TABLE sales AS SELECT * FROM lecture.sales;
CREATE TABLE products AS SELECT * FROM lecture.products;
CREATE TABLE customers AS SELECT * FROM lecture.customers;

SELECT COUNT(*) FROM sales
UNION
SELECT COUNT(*) FROM customers;

-- 주문 거래액이 가장 높은 10건을 높은순으로 [고객명, 상품명, 주문금액]을 보여주자.
SELECT
  c.customer_name AS 고객명,
  s.product_name AS 상품명,
  s.total_amount AS 주문금액
FROM customers c
INNER JOIN sales s ON c.customer_id = s.customer_id
ORDER BY s.total_amount DESC
LIMIT 10;
-- 고객 유형별 [고객유형, 주문건수, 평균주문금액] 을 평균주문금액 높은순으로 정렬해서 보여주자.
SELECT
  c.customer_type AS 고객유형,
  COUNT(*) AS 주문건수,
  AVG(s.total_amount) AS 평균주문금액
FROM customers c
-- INNER JOIN 은 구매자들끼리 평균 / customers LEFT JOIN 는 모든 고객을 분석
INNER JOIN sales s ON c.customer_id = s.customer_id
GROUP BY c.customer_type;

-- 문제 1: 모든 고객의 이름과 구매한 상품명 조회
SELECT
  c.customer_name AS 고객명,
  coalesce(s.product_name, '🙀') AS 상품명
FROM customers c
LEFT JOIN sales s ON c.customer_id = s.customer_id
ORDER BY c.customer_name;

-- 문제 2: 고객 정보와 주문 정보를 모두 포함한 상세 조회
SELECT
  c.customer_name AS 고객명,
  c.customer_type AS 고객유형,
  c.join_date AS 가입일,
  s.product_name AS 상품명,
  s.category AS 카테고리,
  s.total_amount AS 주문금액,
  s.order_date AS 주문일
FROM customers c
INNER JOIN sales s ON c.customer_id = s.customer_id
ORDER BY 주문일 DESC;

-- 문제 3: VIP 고객들의 구매 내역만 조회
SELECT
  c.customer_name AS 고객명,
  c.customer_type AS 고객유형,
  s.product_name AS 상품명,
  s.total_amount AS 주문금액,
  s.order_date AS 주문일
FROM customers c
INNER JOIN sales s ON c.customer_id = s.customer_id
WHERE c.customer_type = 'VIP'
ORDER BY s.total_amount DESC;

-- 문제 4: 건당 50만원 이상 주문한 기업 고객들과 주문내역
SELECT 
  c.customer_name AS 고객명,
  c.customer_type AS 고객유형,
  s.product_name AS 상품명,
  s.total_amount AS 주문금액,
  s.order_date AS 주문일
FROM customers c
INNER JOIN sales s ON c.customer_id = s.customer_id
WHERE c.customer_type = '기업' AND s.total_amount >= 500000;
-- 고객 별 분석 GROUP BY


-- 문제 5: 2024년 하반기(7월~12월) AND 전자제품 구매 내역
SELECT
  *
FROM customers c
INNER JOIN sales s ON c.customer_id = s.customer_id
WHERE s.category = '전자제품' AND (
  YEAR(s.order_date) = 2024
  AND 
  MONTH(s.order_date) BETWEEN 7 AND 12
);

-- 문제 6: 고객별 주문 통계 (INNER JOIN) [고객명, 유형, 주문횟수, 총구매, 평균구매, 최근주문일]
SELECT
  c.customer_id,
  c.customer_name,
  c.customer_type,
  COUNT(*) AS 주문횟수,
  SUM(s.total_amount) AS 총구매금액,
  AVG(s.total_amount) AS 평균구매금액,
  MAX(s.order_date) AS 최근주문일
FROM customers c
INNER JOIN sales s ON c.customer_id = s.customer_id
GROUP BY c.customer_id, c.customer_name, c.customer_type
ORDER BY 평균구매금액 DESC;


-- 문제 7: 모든 고객의 주문 통계 (LEFT JOIN) - 주문 없는 고객도 포함
SELECT
  c.customer_id,
  c.customer_name,
  c.customer_type,
  c.join_date,
  COUNT(s.id) AS 주문횟수,  -- COUNT 주의
  COALESCE(SUM(s.total_amount), 0) AS 총구매금액,  -- NULL 값 주의
  COALESCE(AVG(s.total_amount), 0) AS 평균구매금액,
  COALESCE(MAX(s.total_amount), 0) AS 최대구매금액
FROM customers c
LEFT JOIN sales s ON c.customer_id = s.customer_id
GROUP BY c.customer_id, c.customer_name, c.customer_type, c.join_date
ORDER BY 총구매금액 DESC;

-- 문제 8: 상품 카테고리별로 구매한 고객 유형 분석
SELECT
  c.customer_type AS 유형,
  s.category AS 카테고리,
  COUNT(*) AS 주문건수,
  SUM(s.total_amount) AS 총매출액
FROM customers c
INNER JOIN sales s ON c.customer_id = s.customer_id
GROUP BY s.category, c.customer_type;

-- 문제 9: 고객별 등급 분류 
-- 활동등급(구매횟수) : [0(잠재고객) < 브론즈 < 3 <= 실버 < 5 <= 골드 < 10 <= 플래티넘]
-- 구매등급(구매총액) : [0(신규) < 일반 <= 10만 < 우수 <= 20만 < 최우수 < 50만 <= 로얄]
SELECT
  c.customer_id, c.customer_name, c.customer_type,
  COUNT(s.id) AS 구매횟수,
  coalesce(SUM(s.total_amount), 0) AS 총구매액,
  CASE
    WHEN COUNT(s.id) = 0 THEN '잠재고객'
    WHEN COUNT(s.id) >= 10 THEN '플래티넘'
    WHEN COUNT(s.id) >= 5 THEN '골드'
    WHEN COUNT(s.id) >= 3 THEN '실버'
    ELSE '브론즈'
  END AS 활동등급,
  CASE
    WHEN COALESCE(SUM(s.total_amount), 0) >= 5000000 THEN 'VIP+'
    WHEN COALESCE(SUM(s.total_amount), 0) >= 2000000 THEN 'VIP'
    WHEN COALESCE(SUM(s.total_amount), 0) >= 1000000 THEN '우수'
    WHEN COALESCE(SUM(s.total_amount), 0) > 0 THEN '일반'
    ELSE '신규'
  END AS 구매등급
FROM customers c
LEFT JOIN sales s ON c.customer_id = s.customer_id
GROUP BY c.customer_id, c.customer_name, c.customer_type;



-- 문제 10: 활성 고객 분석
-- 고객상태('24-12-31' - 최종구매일) [NULL(구매없음) | 활성고객 <= 30 < 관심고객 <= 90 관심고객 < 휴면고객]별로 
-- 고객수, 총주문건수, 총매출액, 평균주문금액 분석
SELECT
  고객상태,
  COUNT(*) AS 고객수,
  SUM(총주문건수) AS 상태별총주문건수,
  SUM(총매출액) AS 상태별총매출액,
  ROUND(AVG(평균주문금액)) AS 상태별평균주문금액
FROM (
  SELECT
    c.customer_id,
    c.customer_name,
    COUNT(s.id) AS 총주문건수,
    coalesce(SUM(total_amount), 0)AS 총매출액,
    coalesce(ROUND(AVG(total_amount)), 0) AS 평균주문금액,
    CASE
      WHEN MAX(order_date) IS NULL THEN '구매없음'
      WHEN DATEDIFF('2024-12-31', MAX(s.order_date)) <= 30 THEN '활성고객'
      WHEN DATEDIFF('2024-12-31', MAX(s.order_date)) <= 90 THEN '관심고객'
      ELSE '휴면고객'
    END AS 고객상태
    FROM customers c
    LEFT JOIN sales s ON c.customer_id = s.customer_id
    GROUP BY c.customer_id, c.customer_name
) AS customer_anlysis
GROUP BY 고객상태
;
```

```sql
-- 20-subquery3.sql

USE lecture;

-- 각 카테고리 별 평균매출중에서 50만원 이상만 구하기
SELECT 
  category,
  AVG(total_amount) AS 평균매출액
FROM sales GROUP BY category
HAVING 평균매출액 > 500000;

-- 인라인 뷰(View) => 내가 만든 테이블
SELECT *
FROM (
  SELECT 
    category,
  AVG(total_amount) AS 평균매출액
  FROM sales GROUP BY category
) AS cateogry_summary
WHERE 평균매출액 >= 500000;

--  category_summary
-- ┌─────────────┬─────────────┐
-- │  category   │   평균매출액   │
-- ├─────────────┼─────────────┤
-- │  전자제품     │   890,000   │
-- │  의류        │   420,000   │
-- │  생활용품     │   650,000   │
-- │  식품        │   180,000   │
-- └─────────────┴─────────────┘
-- SELECT * FROM category_summary WHERE 평균매출액 > 500000

-- 1. 카테고리별 매출 분석 후 필터링
-- 카테고리명, 주문건수, 총매출, 평균매출, 평균매출 [0 <= 저단가 < 400000 <= 중단가 < 800000 < 고단가]

SELECT
  category,
  판매건수,
  총매출,
  평균매출,
  CASE
    WHEN 평균매출 >= 800000 THEN '고단가'
    WHEN 평균매출 >= 400000 THEN '중단가'
    ELSE '저단가'
  END AS 단가구분
FROM (
  SELECT
    category,
    COUNT(*) AS 판매건수,
    SUM(total_amount) AS 총매출,
    ROUND(AVG(total_amount)) AS 평균매출
  FROM sales
  GROUP BY category
) AS c_a 
WHERE 평균매출 >= 300000;

-- 영업사원별 성과 등급 분류 [영업사원, 총매출액, 주문건수, 평균주문액, 매출등급, 주문등급]
-- 매출등급 - 총매출[0< C <= 백만 < B < 3백만 <= A < 5백만 <= S]
-- 주문등급 - 주문건수  [0 <= C < 15 <= B < 30 <= A]
-- ORDER BY 총매출액 DESC

SELECT
  영업사원, 총매출액, 주문건수, 평균주문액,
  CASE
    WHEN 총매출액 >= 15000000 THEN 'S'
    WHEN 총매출액 >= 3000000 THEN 'A'
    WHEN 총매출액 >= 1000000 THEN 'B'
    ELSE 'C'
  END AS 매출등급,
  CASE
    WHEN 주문건수 >= 20 THEN 'A'
    WHEN 주문건수 >= 10 THEN 'B'
    ELSE 'C'
  END AS 주문등급
FROM (
  SELECT
    coalesce(sales_rep, '확인불가') AS 영업사원,
    SUM(total_amount) AS 총매출액,
    COUNT(*) AS 주문건수,
    AVG(total_amount) AS 평균주문액
  FROM sales
  GROUP BY sales_rep
) AS rep_analyze
ORDER BY 총매출액 DESC;
```

```sql
-- 21-view.sql
USE lecture;

CREATE VIEW customer_summary AS
SELECT
    c.customer_id,
    c.customer_name,
    c.customer_type,
    COUNT(s.id) AS 주문횟수,
    COALESCE(SUM(s.total_amount), 0) AS 총구매액,
    COALESCE(AVG(s.total_amount), 0) AS 평균주문액,
    COALESCE(MAX(s.order_date), '주문없음') AS 최근주문일
FROM customers c
LEFT JOIN sales s ON c.customer_id = s.customer_id
GROUP BY c.customer_id, c.customer_name, c.customer_type;

-- 등급별 구매 평균
SELECT 
  customer_type,
  AVG(총구매액)
FROM customer_summary
GROUP BY customer_type;

SELECT * FROM customer_summary;

-- 충성고객 -> 주문횟수 5이상
SELECT * FROM customer_summary
WHERE 주문횟수 >= 5;

-- 잠재고객 -> 최근주문 빠른 10명
SELECT * FROM customer_summary
WHERE 최근주문일 != '주문없음'
ORDER BY 최근주문일 DESC
LIMIT 10;



-- View 2: 카테고리별 성과 요약 View (category_performance)
-- 카테고리 별로, 총 주문건수, 총매출액, 평균주문금액, 구매고객수, 판매상품수, 매출비중(전체매출에서 해당 카테고리가 차지하는비율)

CREATE VIEW category_performance AS
SELECT
    s.category,
    COUNT(*) AS 총주문건수,
    SUM(s.total_amount) AS 총매출액,
    AVG(s.total_amount) AS 평균주문금액,
    COUNT(DISTINCT s.customer_id) AS 구매고객수,
    COUNT(DISTINCT s.product_name) AS 판매상품수,
    ROUND(SUM(s.total_amount) * 100.0 / (SELECT SUM(total_amount) FROM sales), 2) AS 매출비중
FROM sales s
GROUP BY s.category;

SELECT * FROM category_performance;


-- View 3: 월별 매출 요약 (monthly_sales )
-- 년월(24-07), 월주문건수, 월평균매출액, 월활성고객수, 월신규고객수

CREATE VIEW monthly_sales AS
SELECT
    DATE_FORMAT(s.order_date, '%Y-%m') AS 년월,
    COUNT(*) AS 월주문건수,
    SUM(s.total_amount) AS 월매출액,
    AVG(s.total_amount) AS 월평균주문액,
    COUNT(DISTINCT s.customer_id) AS 월활성고객수,
    COUNT(DISTINCT c.customer_id) AS 월신규고객수
FROM sales s
LEFT JOIN customers c
    ON s.customer_id = c.customer_id
    AND DATE_FORMAT(s.order_date, '%Y-%m') = DATE_FORMAT(c.join_date, '%Y-%m')
GROUP BY
    DATE_FORMAT(s.order_date, '%Y-%m');

SELECT * FROM monthly_sales;
```

```sql
-- TIL+
-- 서브쿼리를 이용한 가상테이블(인라인 뷰)은 가장 기초가 되는 FROM절에 붙기 떄문에 가장 기본이 되는 테이블이 된다.
-- 그러므로 alies를 사용할 수 있는게 쿼리논리순서상으로 order by 밖에 쓸 수 없던 것을 모든 곳에 쓸 수 있게 된다. 
-- 가상테이블을 AS로 만들면 스키마의 Views에 저장해서 마음껏 쓸 수 있다.
```

