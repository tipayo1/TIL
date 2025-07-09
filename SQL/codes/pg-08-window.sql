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
