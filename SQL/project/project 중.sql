-- 중 난이도

-- 1. 직원별 담당 고객 수 집계
-- 각 직원(employee_id, first_name, last_name)이 담당하는 고객 수를 집계하세요.
-- 고객이 한 명도 없는 직원도 모두 포함하고, 고객 수 내림차순으로 정렬하세요.
SELECT 
	e.employee_id,
	e.first_name,
	e.last_name,
	COUNT(c.customer_id) AS 고객수
FROM employees e
INNER JOIN customers c ON e.employee_id = c.support_rep_id
GROUP BY e.employee_id
ORDER BY 고객수 DESC
;
-- 2. 가장 많이 팔린 트랙 TOP 5
-- 판매량(구매된 수량)이 가장 많은 트랙 5개(track_id, name, 총 판매수량)를 출력하세요.
-- 동일 판매수량일 경우 트랙 이름 오름차순 정렬하세요.
SELECT 
	t.track_id,
	t.name AS 트랙명,
	COUNT(ii.track_id) AS 트랙판매수
FROM tracks t
INNER JOIN invoice_items ii ON t.track_id = ii.track_id
GROUP BY t.track_id, t.name
ORDER BY 트랙판매수 DESC, 트랙명 ASC
LIMIT 5
;
-- 3. 2020년 이전에 가입한 고객 목록
-- 2020년 1월 1일 이전에 첫 인보이스를 발행한 고객의 customer_id, first_name, last_name, 첫구매일을 조회하세요.
SELECT 
	c.customer_id,
	c.first_name,
	c.last_name,
	MIN(i.invoice_date) AS 첫구매일
FROM customers c
INNER JOIN invoices i ON c.customer_id = i.customer_id
WHERE i.invoice_date < '2020-01-01'
GROUP BY 
	c.customer_id,
	c.first_name,
	c.last_name
ORDER BY 첫구매일 ASC
;
-- 4. 국가별 총 매출 집계 (상위 10개 국가)
-- 국가(billing_country)별 총 매출을 집계해, 매출이 많은 상위 10개 국가의 국가명과 총 매출을 출력하세요.
SELECT 
	billing_country,
	SUM(total) AS 국가별총매출
FROM invoices
GROUP BY 
	billing_country
ORDER BY 국가별총매출 DESC
LIMIT 10
;
-- 5. 각 고객의 최근 구매 내역
-- 각 고객별로 가장 최근 인보이스(invoice_id, invoice_date, total) 정보를 출력하세요.
SELECT 
	customer_id, 
	invoice_id, 
	invoice_date, 
	total
FROM (
    SELECT
        customer_id,
        invoice_id,
        invoice_date,
        total,
        ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY invoice_date DESC) AS rn
    FROM invoices
) t
WHERE rn = 1
;