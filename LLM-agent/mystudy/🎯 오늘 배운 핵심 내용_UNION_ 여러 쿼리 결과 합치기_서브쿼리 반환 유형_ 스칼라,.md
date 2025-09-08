<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" class="logo" width="120"/>

# 🎯 오늘 배운 핵심 내용

UNION: 여러 쿼리 결과 합치기
서브쿼리 반환 유형: 스칼라, 벡터, 매트릭스
Inline View \& View: 쿼리 재사용과 가상 테이블
SQL 작성 주의사항: JOIN, GROUP BY 등 실수 방지
🔗 1. UNION - 여러 쿼리 결과 합치기
💡 UNION의 개념
여러 SELECT 쿼리의 결과를 세로로(행 방향) 합치는 기능
Copy-- 기본 UNION 사용법
SELECT '고객 테이블' AS 구분, COUNT(*) AS 데이터수 FROM customers
UNION ALL
SELECT '매출 테이블' AS 구분, COUNT(*) AS 데이터수 FROM sales;

-- UNION vs UNION ALL
SELECT customer_type FROM customers  -- 중복 제거
UNION
SELECT customer_type FROM customers;

SELECT customer_type FROM customers  -- 중복 포함
UNION ALL
SELECT customer_type FROM customers;
🎯 UNION 실전 활용
통합 리포트 만들기
Copy-- 카테고리별 + 고객유형별 통합 분석
SELECT
'카테고리별' AS 분석유형,
category AS 구분,
COUNT(*) AS 건수,
SUM(total_amount) AS 총액
FROM sales s
JOIN products p ON s.product_id = p.product_id
GROUP BY category

UNION ALL

SELECT
'고객유형별' AS 분석유형,
customer_type AS 구분,
COUNT(*) AS 건수,
SUM(total_amount) AS 총액
FROM sales s
JOIN customers c ON s.customer_id = c.customer_id
GROUP BY customer_type

ORDER BY 분석유형, 총액 DESC;
⚠️ UNION 주의사항
컬럼 수 일치: 모든 SELECT문의 컬럼 개수가 같아야 함
데이터 타입 호환: 같은 위치 컬럼의 데이터 타입이 호환되어야 함
컬럼명: 첫 번째 SELECT문의 컬럼명 사용
📊 2. 서브쿼리 반환 유형
🔢 스칼라 서브쿼리 (Scalar Subquery)
단일 값(1행 1열) 반환
Copy-- 각 주문과 전체 평균 비교
SELECT
product_name,
total_amount,
(SELECT AVG(total_amount) FROM sales) AS 전체평균,  -- 스칼라
total_amount - (SELECT AVG(total_amount) FROM sales) AS 평균차이
FROM sales
WHERE total_amount > (SELECT AVG(total_amount) FROM sales);
📋 복수행(Vector) 서브쿼리
여러 행, 단일 컬럼 반환
Copy-- VIP 고객들의 주문 내역
SELECT * FROM sales
WHERE customer_id IN (  -- 벡터: 여러 customer_id 값들
SELECT customer_id FROM customers WHERE customer_type = 'VIP'
);

-- 전자제품 구매 경험 고객들의 모든 주문
SELECT * FROM sales
WHERE customer_id IN (  -- 벡터: 여러 customer_id 값들
SELECT DISTINCT customer_id FROM sales WHERE category = '전자제품'
);
📋 Inline View(Matrix)
여러 행, 여러 컬럼 반환 (주로 EXISTS나 FROM절에서 사용)
Copy-- EXISTS로 매트릭스 서브쿼리 활용
SELECT c.customer_name
FROM customers c
WHERE EXISTS (  -- 매트릭스: 여러 행, 여러 컬럼 반환 가능
SELECT s.customer_id, s.product_name, s.total_amount
FROM sales s
WHERE s.customer_id = c.customer_id
AND s.total_amount >= 1000000
);
🎯 서브쿼리 유형별 사용법
유형
반환값
사용 위치
연산자
예시
스칼라
1행 1열
SELECT, WHERE
=, >, <
WHERE amount > (SELECT AVG...)
벡터
여러행 1열
WHERE, HAVING
IN, ANY, ALL
WHERE id IN (SELECT...)
매트릭스
여러행 여러열
FROM, EXISTS
EXISTS
WHERE EXISTS (SELECT...)
📋 3. Inline View \& View
💡 Inline View (인라인 뷰)
FROM 절에 사용되는 서브쿼리 = 임시 테이블
Copy-- 카테고리별 평균 매출을 구한 후, 50만원 이상만 필터링
SELECT *
FROM (
SELECT
category,
AVG(total_amount) AS 평균매출,
COUNT(*) AS 주문건수
FROM sales s
JOIN products p ON s.product_id = p.product_id
GROUP BY category
) AS category_stats  -- 인라인 뷰
WHERE 평균매출 >= 500000;

-- 복잡한 고객 분석
SELECT
고객상태,
COUNT(*) AS 고객수,
AVG(총매출액) AS 평균매출액
FROM (
SELECT
c.customer_name,
SUM(s.total_amount) AS 총매출액,
CASE
WHEN MAX(s.order_date) IS NULL THEN '미구매'
WHEN DATEDIFF(CURDATE(), MAX(s.order_date)) <= 30 THEN '활성'
ELSE '휴면'
END AS 고객상태
FROM customers c
LEFT JOIN sales s ON c.customer_id = s.customer_id
GROUP BY c.customer_id, c.customer_name
) AS customer_analysis
GROUP BY 고객상태;
📋 View (뷰)
복잡한 쿼리를 재사용 가능한 가상 테이블로 저장
Copy-- View 생성
CREATE VIEW customer_summary AS
SELECT
c.customer_id,
c.customer_name,
c.customer_type,
COUNT(s.id) AS 주문횟수,
COALESCE(SUM(s.total_amount), 0) AS 총구매액,
COALESCE(AVG(s.total_amount), 0) AS 평균주문액
FROM customers c
LEFT JOIN sales s ON c.customer_id = s.customer_id
GROUP BY c.customer_id, c.customer_name, c.customer_type;

-- View 사용
SELECT * FROM customer_summary WHERE 주문횟수 >= 5;
SELECT * FROM customer_summary WHERE customer_type = 'VIP';

-- View 삭제
DROP VIEW customer_summary;
🔄 Inline View vs View 비교
구분
Inline View
View
저장 여부
일회용
데이터베이스에 저장
재사용
불가능
가능
성능
매번 실행
한 번 정의 후 재사용
용도
복잡한 일회성 분석
자주 사용하는 쿼리
⚠️ 4. SQL 작성 주의사항
🔗 JOIN 관련 주의사항

1. 별명(Alias) 필수 사용
Copy-- ❌ 잘못된 예
SELECT customer_name, product_name
FROM customers
JOIN sales ON customer_id = customer_id;  -- 어느 customer_id?

-- ✅ 올바른 예
SELECT c.customer_name, s.product_name
FROM customers c
JOIN sales s ON c.customer_id = s.customer_id;
2. JOIN 조건 누락 방지
Copy-- ❌ 카르테시안 곱 발생
SELECT c.customer_name, s.product_name
FROM customers c, sales s;  -- 조건 없음!

-- ✅ 명시적 JOIN 조건
SELECT c.customer_name, s.product_name
FROM customers c
JOIN sales s ON c.customer_id = s.customer_id;
3. LEFT JOIN에서 COUNT 주의
Copy-- ❌ 잘못된 COUNT
SELECT c.customer_name, COUNT(*) AS 주문횟수
FROM customers c
LEFT JOIN sales s ON c.customer_id = s.customer_id
GROUP BY c.customer_name;  -- 주문 없어도 1로 카운트

-- ✅ 올바른 COUNT
SELECT c.customer_name, COUNT(s.id) AS 주문횟수
FROM customers c
LEFT JOIN sales s ON c.customer_id = s.customer_id
GROUP BY c.customer_name;  -- 주문 없으면 0으로 카운트
📊 GROUP BY 관련 주의사항

1. SELECT 컬럼은 모두 GROUP BY에 포함
Copy-- ❌ 오류 발생
SELECT customer_name, customer_type, COUNT(*)
FROM customers
GROUP BY customer_name;  -- customer_type 누락

-- ✅ 올바른 방법
SELECT customer_name, customer_type, COUNT(*)
FROM customers
GROUP BY customer_name, customer_type;
2. HAVING vs WHERE 구분
Copy-- WHERE: 그룹핑 전 개별 행 조건
SELECT customer_type, COUNT(*)
FROM customers
WHERE join_date >= '2024-01-01'  -- 개별 행 조건
GROUP BY customer_type;

-- HAVING: 그룹핑 후 그룹 조건
SELECT customer_type, COUNT(*)
FROM customers
GROUP BY customer_type
HAVING COUNT(*) >= 10;  -- 그룹 조건
🔄 서브쿼리 관련 주의사항

1. 스칼라 서브쿼리는 단일 값만
Copy-- ❌ 오류: 여러 값 반환
SELECT product_name, (SELECT customer_id FROM sales)
FROM products;

-- ✅ 올바름: 단일 값 반환
SELECT product_name, (SELECT COUNT(*) FROM sales WHERE product_name = p.product_name)
FROM products p;
2. NULL 처리
Copy-- LEFT JOIN에서 NULL 처리
SELECT
c.customer_name,
COALESCE(SUM(s.total_amount), 0) AS 총구매액,  -- NULL → 0
COALESCE(MAX(s.order_date), '주문없음') AS 최근주문일  -- NULL → '주문없음'
FROM customers c
LEFT JOIN sales s ON c.customer_id = s.customer_id
GROUP BY c.customer_name;
💡 핵심 패턴 정리
🎯 문제 해결 접근법
단계별 분해: 복잡한 문제를 작은 단위로 나누기
인라인 뷰 활용: 집계 후 추가 조건이 필요할 때
적절한 JOIN 선택: INNER vs LEFT 상황에 맞게
NULL 처리: LEFT JOIN시 항상 고려
📝 SQL 작성 체크리스트
테이블 별명 사용했나?
JOIN 조건 정확한가?
GROUP BY에 필요한 컬럼 모두 포함했나?
LEFT JOIN에서 COUNT(특정컬럼) 사용했나?
NULL 값 처리했나?
서브쿼리 반환 유형 맞나?

---

위 내용을 md파일로 TIL에 올릴꺼야 깔끔하고 예쁘게 잘 다듬어줘

```markdown
# 🎯 오늘 배운 SQL 핵심 내용 정리

## 1. UNION: 여러 쿼리 결과 합치기

**UNION**  
- 여러 SELECT 쿼리의 결과를 **세로(행 방향)**로 합치는 SQL 연산자  
- **중복 행을 자동으로 제거**하며, 컬럼 개수와 데이터 타입이 모두 일치해야 함  
- 성능상 **UNION ALL**보다 느릴 수 있음 (중복 제거 작업 때문)[^1][^5][^6]

**UNION ALL**  
- 여러 SELECT 쿼리 결과를 **중복까지 모두 포함**하여 합침  
- 중복 제거 과정이 없어 **더 빠름**[^2][^5][^7]

| 구분      | 중복 제거 | 속도       | 사용 예시                                 |
|-----------|-----------|------------|-------------------------------------------|
| UNION     | O         | 느림       | SELECT ... UNION SELECT ...               |
| UNION ALL | X         | 빠름       | SELECT ... UNION ALL SELECT ...           |

> **주의:**  
> - 모든 SELECT문의 **컬럼 수와 타입이 일치**해야 함  
> - 컬럼명은 **첫 번째 SELECT문의 컬럼명**을 따름  
> - `ORDER BY`는 전체 UNION 쿼리의 마지막에만 사용 가능[^6]

**실전 예시**
```

SELECT '고객 테이블' AS 구분, COUNT(*) AS 데이터수 FROM customers
UNION ALL
SELECT '매출 테이블' AS 구분, COUNT(*) AS 데이터수 FROM sales;

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

```

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

```

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
```

<div style="text-align: center">⁂</div>

[^1]: https://mystyle70024.tistory.com/23

[^2]: https://jmkim.tistory.com/50

[^3]: https://mimah.tistory.com/entry/Oracle-SQL-UNION-과-UNION-ALL-차이

[^4]: https://chlengk.tistory.com/18

[^5]: https://datasciencebeehive.tistory.com/181

[^6]: https://itrh.tistory.com/entry/UNION-vs-UNION-ALL-사용법-차이

[^7]: https://anotherhound.tistory.com/59

[^8]: https://silverji.tistory.com/49

[^9]: https://whitepro.tistory.com/580

