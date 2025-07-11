-- 상 난이도

-- 1. 월별 매출 및 전월 대비 증감률
-- 각 연월(YYYY-MM)별 총 매출과, 전월 대비 매출 증감률을 구하세요.
-- 결과는 연월 오름차순 정렬하세요.
WITH monthly_sales AS (
    SELECT
        TO_CHAR(DATE_TRUNC('month', invoice_date), 'YYYY-MM') AS 연월,
        SUM(total) AS 총매출
    FROM invoices
    GROUP BY TO_CHAR(DATE_TRUNC('month', invoice_date), 'YYYY-MM')
)
SELECT
    연월,
    총매출,
    ROUND(
        (총매출 - LAG(총매출) OVER (ORDER BY 연월)) 
        / NULLIF(LAG(총매출) OVER (ORDER BY 연월), 0) * 100, 2
    ) AS 전월대비매출증감률
FROM monthly_sales
ORDER BY 연월 ASC;
-- 2. 장르별 상위 3개 아티스트 및 트랙 수
-- 각 장르별로 트랙 수가 가장 많은 상위 3명의 아티스트(artist_id, name, track_count)를 구하세요.
-- 동점일 경우 아티스트 이름 오름차순 정렬.
SELECT 
	r.artist_id,
	r.name,
	COUNT(t.track_id) AS 트랙수
FROM artists r
INNER JOIN albums a ON r.artist_id = a.artist_id
INNER JOIN tracks t ON a.album_id = t.album_id
INNER JOIN genres g ON t.genre_id = g.genre_id
GROUP BY 
	r.artist_id,
	r.name
ORDER BY 트랙수, r.name ASC 
LIMIT 3
;
-- 3. 고객별 누적 구매액 및 등급 산출
-- 각 고객의 누적 구매액을 구하고,
-- 상위 20%는 'VIP', 하위 20%는 'Low', 나머지는 'Normal' 등급을 부여하세요.
WITH purchase_ranking AS (
    SELECT
        customer_id,
        SUM(total) AS total_purchase
    FROM invoices
    GROUP BY customer_id
),
ranked AS (
    SELECT
        customer_id,
        total_purchase,
        NTILE(5) OVER (ORDER BY total_purchase DESC) AS quintile
    FROM purchase_ranking
)
SELECT
    customer_id,
    total_purchase,
    CASE
        WHEN quintile = 1 THEN 'VIP'
        WHEN quintile = 5 THEN 'Low'
        ELSE 'Normal'
    END AS 등급
FROM ranked
ORDER BY total_purchase DESC
;

-- 4. 국가별 재구매율(Repeat Rate)
-- 각 국가별로 전체 고객 수, 2회 이상 구매한 고객 수, 재구매율을 구하세요.
-- 결과는 재구매율 내림차순 정렬.
WITH customer_purchase_counts AS (
    SELECT
        c.country AS billing_country,
        c.customer_id,
        COUNT(i.invoice_id) AS purchase_count
    FROM customers c
    LEFT JOIN invoices i ON c.customer_id = i.customer_id
    GROUP BY c.country, c.customer_id
)
SELECT
    billing_country,
    COUNT(customer_id) AS 전체고객수,
    COUNT(CASE WHEN purchase_count >= 2 THEN 1 END) AS 재구매고객수,
    ROUND(COUNT(CASE WHEN purchase_count >= 2 THEN 1 END)::numeric / COUNT(customer_id) * 100, 2) AS 재구매율
FROM customer_purchase_counts
GROUP BY billing_country
ORDER BY 재구매율 DESC
;
-- 5. 최근 1년간 월별 신규 고객 및 잔존 고객
-- 최근 1년(마지막 인보이스 기준 12개월) 동안,
-- 각 월별 신규 고객 수와 해당 월에 구매한 기존 고객 수를 구하세요.

WITH customer_purchase_counts AS (
    SELECT
        c.country,
        c.customer_id,
        COUNT(i.invoice_id) AS purchase_count
    FROM customers c
    LEFT JOIN invoices i ON c.customer_id = i.customer_id
    GROUP BY c.country, c.customer_id
)
SELECT
    country,
    COUNT(customer_id) AS total_customers,
    COUNT(CASE WHEN purchase_count >= 2 THEN 1 END) AS repeat_customers,
    ROUND(COUNT(CASE WHEN purchase_count >= 2 THEN 1 END)::numeric / COUNT(customer_id) * 100, 2) AS repeat_rate_percent
FROM customer_purchase_counts
GROUP BY country
ORDER BY repeat_rate_percent DESC
;
