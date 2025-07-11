# 🎯 오늘 학습한 핵심 내용 TIL

## 🗂️하, 중, 상, 난이도 문제 풀기 
```sql
-- 하 난이도

-- 1. 모든 고객 목록 조회
-- 고객의 customer_id, first_name, last_name, country를 조회하고, customer_id 오름차순으로 정렬하세요.
SELECT 
	customer_id,
	first_name,
	last_name,
	country
FROM customers
ORDER BY customer_id ASC
;
-- 2. 모든 앨범과 해당 아티스트 이름 출력
-- 각 앨범의 title과 해당 아티스트의 name을 출력하고, 앨범 제목 기준 오름차순 정렬하세요.
SELECT 
	a.title,
	r.name
FROM albums a
INNER JOIN artists r ON a.artist_id = r.artist_id
ORDER BY title ASC
;
-- 3. 트랙(곡)별 단가와 재생 시간 조회
-- tracks 테이블에서 각 곡의 name, unit_price, milliseconds를 조회하세요.
-- 5분(300,000 milliseconds) 이상인 곡만 출력하세요.
SELECT 
	name,
	unit_price,	
	milliseconds
FROM tracks
WHERE milliseconds > 300000
;
-- 4. 국가별 고객 수 집계
-- 각 국가(country)별로 고객 수를 집계하고, 고객 수가 많은 순서대로 정렬하세요.
SELECT 
	COUNT(customer_id) AS 고객수,
	country AS 국가
FROM customers
GROUP BY country
ORDER BY 고객수 DESC
;
-- 5. 각 장르별 트랙 수 집계
-- 각 장르(genres.name)별로 트랙 수를 집계하고, 트랙 수 내림차순으로 정렬하세요.
SELECT 
	g.name AS 장르,
	COUNT(t.track_id) AS 트랙수
FROM genres g
INNER JOIN tracks t ON g.genre_id = t.genre_id
GROUP BY g.name
ORDER BY 트랙수 DESC
;
```

```sql
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
```

```sql
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

```

## 🗂️개인 자율 프로젝트 만들어보기 
```sql
-- ## 자율 분석
-- 현재 파악한 ERD를 바탕으로 추출할 수 있는 데이터나 정보를 확인할 수 있는 대시보드를 제작

SELECT * FROM albums;
SELECT * FROM artists;
SELECT * FROM customers;
SELECT * FROM employees;
SELECT * FROM genres;
SELECT * FROM invoices;
SELECT * FROM playlists;
SELECT * FROM tracks;

1. 국가들(북반구/남반구) 내에서 계절별 유행 장르 찾기

SELECT count(*) FROM invoices;
--> 판매목록수 확인 412

SELECT 
	billing_country,
	count(billing_country)
FROM invoices
GROUP BY billing_country
;
--> 국가별 판매량 확인, 24개 국가

아르헨티나 칠레 브라질 호주를 제외한 모든 국가 : 북반구
--> 북반구와 남반구 국가 분리(view 활용)

-->북반구의 계절별 장르 선호순위와 남반구의 것을 확인할 수 있는 쿼리 작성

2. 연도별 장르 성장변화

3. 가장 매출이 


-- ### 예시

-- 1. 음악/고객/매출 관련 창의적 분석
-- 가장 충성도 높은 고객 Top 10 분석

-- 구매 횟수, 총 매출, 평균 구매 간격 등 기준별로 상위 고객을 선정하고 특징 분석

-- 특정 장르 또는 아티스트의 성장 추이

-- 월별/연도별로 특정 장르나 아티스트의 트랙 판매량, 매출 변화 분석

-- 고객의 음악 취향 클러스터링

-- 고객별로 가장 많이 구매한 장르를 파악하고, 유사 고객 그룹(취향별 세그먼트) 도출

-- 직원(지원 담당자)별 고객 만족도 예측

-- 담당 직원별 고객의 재구매율, 평균 구매 금액, 이탈률 등 비교

-- 특정 국가/도시별 인기 음악 스타일

-- 국가·도시별로 가장 많이 팔린 장르, 아티스트, 트랙 순위 분석

-- 2. 추천·마케팅 시나리오
-- 고객별 맞춤 트랙/앨범 추천

-- 최근 구매 이력과 유사 고객의 구매 패턴을 바탕으로 추천 리스트 도출

-- 휴면 고객 재활성화 대상 선정

-- 일정 기간(예: 6개월) 동안 구매 이력이 없는 고객을 찾아, 재구매 가능성이 높은 타겟 추출

-- 장르/아티스트별 프로모션 효과 분석

-- 특정 기간 동안 프로모션이 있었던 장르/아티스트의 매출 증감 효과 측정

-- 3. 데이터 품질 및 이상 탐지
-- 이상 거래 탐지

-- 비정상적으로 높은/낮은 단가, 짧은 시간 내 반복 구매 등 이상 패턴 탐색

-- 데이터 누락/오류 사례 분석

-- 주소, 이메일, 가격 등 주요 필드의 NULL/이상값 빈도 및 원인 파악

-- 4. 서비스·운영 인사이트
-- 플레이리스트 활용 분석

-- 가장 많이 사용된 플레이리스트, 플레이리스트별 트랙 수, 인기 트랙 등 분석

-- 고객 여정 분석

-- 신규 고객이 첫 구매 후 재구매까지 걸리는 평균 기간, 구매 패턴 변화 등 시각화

-- 음원 길이·가격과 판매량의 상관관계

-- 트랙의 재생시간, 단가와 실제 판매량 간의 통계적 상관관계 분석

-- 5. 자유 주제형 탐구
-- 음악 시장 트렌드 예측

-- 최근 1~2년간 데이터로 장르/아티스트별 성장률을 분석하고 향후 트렌드 예측

-- 가상의 신규 상품/서비스 제안

-- 데이터 기반으로 새로운 번들 상품, 추천 시스템, 고객 혜택 프로그램 등 기획안 작성
```