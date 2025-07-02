-- 14-group-by.sql

USE lecture;

-- 카테고리별 매출 (피벗테이블 행=카테고리, 값=매출액)
SELECT
	category AS 카테고리,
    count(*) AS 주문건수,
    sum(total_amount) AS 총매출,
    sum(total_amount) AS 평균매출
FROM sales
GROUP BY category
ORDER BY 총매출 DESC;


-- 지역별 매출 분석
SELECT
	region AS 지역,
    count(*) AS 주문건수,
    sum(total_amount) AS 매출액,
    -- 지역별 고객 수
    count(DISTINCT customer_id) AS 고객수, -- DISTINCT 중복제거
    count(*) / count(DISTINCT customer_id) AS 고객당주문수,
    round(
		sum(total_amount) / count(DISTINCT customer_id)
	) AS 고객당평균매출
FROM sales
GROUP BY region;

-- 다중 GROUPing
SELECT
	region AS 지역,
    category AS 카테고리,
	count(*) AS 주문건수,
    sum(total_amount) AS 총매출액,
    round(AVG(total_amount)) AS 평균매출액
FROM sales
GROUP BY region, category
ORDER BY 지역, 총매출액 DESC;

-- 영업사원(sales_rep) 월별 성과 
SELECT
	sales_rep,
    date_format(order_date, '%Y-%m') AS 월,
    count(*) AS 주문건수,
    sum(total_amount) AS 월매출액,
    format(sum(total_amount), 0) AS easy,
    round(AVG(total_amount)) AS 평균매출액
FROM sales
GROUP BY sales_rep, 월
ORDER BY 월, 월매출액 DESC;

-- MAU(Monthly Active User) 측정
SELECT
	date_format(order_date, '%Y-%m') AS 월,
    count(*) AS 주문건수,
    sum(total_amount) AS 월매출액,
    count(DISTINCT customer_id) AS 월활성고객수
FROM sales
GROUP BY 월;

-- 요일별 매출 패턴
SELECT
	dayname(order_date) AS 요일,
    dayofweek(order_date) AS 요일번호,
    count(total_amount) AS 주문건수,
	sum(total_amount) AS 총매출액,
	round(AVG(total_amount)) AS 평균매출액
FROM sales
GROUP BY dayname(order_date), dayofweek(order_date)
ORDER BY 총매출액 DESC;