-- 13-aggr-func.sql

USE lecture;
SELECT * FROM sales;

SELECT count(*) AS 매출건수
FROM sales;

SELECT COUNT(customer_id)
FROM sales; -- 위와 결과는 같다 

SELECT
	count(*) AS 총주문건수,
    count(DISTINCT customer_id) AS 고객수, -- DISTINCT는 중복제거의 뜻
    count(DISTINCT product_name) AS 제품수
FROM sales;

-- SUM (총합)
SELECT
	sum(total_amount) AS 총매출액,
	format(sum(total_amount), 0) AS 총매출, -- 기본 천단위, 0은 소수점 표기 자리수
	sum(quantity) AS 총판매수량
FROM sales;

-- 적당한 데이터량
SELECT
	sum(if(region='서울', total_amount, 0)) AS 서울매출,
    sum(if(category='전자제품', total_amount, 0)) AS 전자매출
FROM sales;

-- 서울 매출만 다 더하기
SELECT
	sum(total_amount) AS 서울매출
FROM sales
WHERE region='서울';


-- AVG (평균)
SELECT
	avg(total_amount) AS 평균매출액,
    avg(quantity) AS 평균판매수량,
    round(avg(unit_price)) AS 평균단가
FROM sales;

-- MIN / MAX
SELECT
	min(total_amount) AS 최소매출액,
    max(total_amount) AS 최대매출액,
    min(order_date) AS 첫주문일,
    max(order_date) AS 마지막주문일   
FROM sales;

-- 종합
SELECT
	count(*) AS 주문건수,
    sum(total_amount) AS 총매출액,
    avg(total_amount) AS 평균매출액,
	min(total_amount) AS 최소매출액,
    max(total_amount) AS 최대매출액,
    round(avg(quantity), 1) AS 평균수량
FROM sales;