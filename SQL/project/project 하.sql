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