# D3 SQL 함수 & 실전 쿼리 패턴 정리

---

## 🗓️ 1️⃣ 날짜/시간 함수

| 함수                | 용도               | 예시                                      |
|---------------------|--------------------|-------------------------------------------|
| NOW()               | 현재 날짜+시간     | `SELECT NOW();`                           |
| CURDATE()           | 현재 날짜만        | `SELECT CURDATE();`                       |
| DATE_FORMAT()       | 날짜 형식 변환     | `DATE_FORMAT(birth, '%Y년 %m월')`         |
| DATEDIFF()          | 날짜 간 일수 차이  | `DATEDIFF(CURDATE(), birth)`              |
| TIMESTAMPDIFF()     | 기간 단위별 차이   | `TIMESTAMPDIFF(YEAR, birth, CURDATE())`   |
| DATE_ADD()          | 날짜 더하기        | `DATE_ADD(birth, INTERVAL 1 YEAR)`        |
| YEAR(), MONTH(), DAY() | 날짜 요소 추출 | `YEAR(birth), MONTH(birth)`               |

> **FORMAT 기호:**  
> `%Y`(년도), `%m`(월), `%d`(일), `%H`(시간), `%i`(분)

---

## 🔢 2️⃣ 숫자 함수

| 함수      | 용도     | 예시                  |
|-----------|----------|-----------------------|
| ROUND()   | 반올림   | `ROUND(score, 1)`     |
| CEIL()    | 올림     | `CEIL(score)`         |
| FLOOR()   | 내림     | `FLOOR(score)`        |
| ABS()     | 절댓값   | `ABS(score - 80)`     |
| MOD()     | 나머지   | `MOD(id, 2)`          |
| POWER()   | 거듭제곱 | `POWER(score, 2)`     |
| SQRT()    | 제곱근   | `SQRT(score)`         |

---

## 🧩 3️⃣ 조건부 함수

| 함수/구문      | 용도           | 예시                                         |
|----------------|----------------|----------------------------------------------|
| IF()           | 단순 조건      | `IF(score >= 80, '우수', '보통')`            |
| CASE WHEN      | 다중 조건      | `CASE WHEN score >= 90 THEN 'A' ELSE 'B' END`|
| IFNULL()       | NULL 처리      | `IFNULL(nickname, '미설정')`                 |
| COALESCE()     | 첫 번째 NULL이 아닌 값 | `COALESCE(nickname, name, 'Unknown')` |

---

## 📊 4️⃣ 집계 함수 (=스프레드시트 함수)

| SQL 집계함수 | 스프레드시트 | 용도        |
|--------------|--------------|-------------|
| COUNT(*)     | =COUNT()     | 행 개수 세기|
| SUM()        | =SUM()       | 합계        |
| AVG()        | =AVERAGE()   | 평균        |
| MIN()        | =MIN()       | 최솟값      |
| MAX()        | =MAX()       | 최댓값      |

---

## 📑 5️⃣ GROUP BY (=피벗테이블)

**카테고리별 매출 (피벗테이블의 행=카테고리, 값=매출합계)**







```sql
-- 11-datetime-func.sql

USE lecture;
SELECT * FROM dt_demo;

-- 현재 날짜/시간
-- 날짜 + 시간
SELECT NOW() AS 지금시간;
SELECT CURRENT_TIMESTAMP;

-- 날짜
SELECT CURDATE();
SELECT CURRENT_DATE;

-- 시간
SELECT CURTIME();
SELECT CURRENT_TIME;

SELECT 
	name,
    birth AS 원본,
    DATE_FORMAT(birth, '%y년 %m월 %d일') AS 한국식,
    DATE_FORMAT(birth, '%Y-%M') AS 년월,
    DATE_FORMAT(birth, '%M %d, %Y') AS 영문식,
    DATE_FORMAT(birth, '%w') AS 요일번호,
    DATE_FORMAT(birth, '%W') AS 요일이름  
FROM dt_demo;

SELECT 
	created_at AS 원본시간,
    DATE_FORMAT(created_at, '%Y-%m-%d %H:%i') AS 분까지만,
    DATE_FORMAT(created_at, '%p %h:%i') AS 12시간
FROM dt_demo;

-- 날짜 계산 함수
SELECT
	name,
    birth,
    DATEDIFF(CURDATE(), birth) AS 살아온날들,
    -- TIMESTAMPDIFF(결과 단위, 날짜1, 날짜2)
    TIMESTAMPDIFF(YEAR, birth, CURDATE()) AS 나이
FROM dt_demo;

-- 더하기/빼기
SELECT
	name, birth,
    DATE_ADD(birth, INTERVAL 100 DAY) AS 백일후,
    DATE_ADD(birth, INTERVAL 1 YEAR) AS 돌,
    DATE_SUB(birth, INTERVAL 10 MONTH) AS 등장
FROM dt_demo;

-- 계정 생성 후 경과 시간
SELECT
	name, created_at,
    TIMESTAMPDIFF(HOUR, created_at, NOW()) AS 가입후시간,
    TIMESTAMPDIFF(DAY, created_at, NOW()) AS 가입후일수
FROM dt_demo;

-- 날짜 추출
SELECT
	name, birth,
    -- birth -> DATE정보
    YEAR(birth),
    MONTH(birth),
    DAY(birth),
    DAYOFWEEK(birth) AS 요일번호,
    DAYNAME(birth) AS 요일,
    QUARTER(birth) AS 분기
FROM dt_demo;

-- 월별, 연도별
SELECT
	YEAR(birth) AS 출생년도,
    COUNT(*) AS 인원수
FROM dt_demo
GROUP BY YEAR(birth)
ORDER BY 출생년도;

SELECT
    (YEAR(birth) DIV 10) * 10 AS 출생연도_10년단위,
    COUNT(*) AS 인원수
FROM dt_demo
GROUP BY 출생연도_10년단위
ORDER BY 출생연도_10년단위;
```

```sql
-- 12-number-func.sql
USE lecture;

-- 실수(소수점) 함수들
SELECT
	name,
    score AS 원점수,
    ROUND(score) AS 반올림,
    ROUND(score, 1) AS 소수1반올림,
    CEIL(score) AS 올림,
    FLOOR(score) AS 내림,
	TRUNCATE(score, 1) AS 소수1버림
FROM dt_demo;

-- 사칙연산
SELECT
	10 + 5 AS plus,
    10 - 5 AS minus,
    10 * 5 AS multiply,
    10 / 5 AS divide,
    10 DIV 3 AS 몫,
    10 % 3 AS 나머지,
    MOD(10, 3) AS 나머지2,  -- modulo 나머지
    POWER(10, 3) AS 거듭제곱,  -- 거듭제곱 
    SQRT(16) AS 루트,
    ABS(-10) AS 절댓값;

SELECT
	id, name,
    id % 2 AS 나머지,
    CASE
		WHEN id % 2 = 0 THEN '짝수'
        ELSE '홀수'
	END AS 홀짝,
    IF(id % 2 = 1, '홀수', '짝수') AS 홀_짝
FROM dt_demo;


-- 조건문 IF, CASE
SELECT
	name, score,
    IF(score >= 80, '우수', '보통') AS 평가
FROM dt_demo;


SELECT
	name, 
    IFNULL(score, 0) AS 점수,
    CASE
		WHEN score >= 90 THEN 'A'
        WHEN score >= 80 THEN 'B'
        WHEN score >= 70 THEN 'C'
        ELSE 'D'
	END AS 학점
FROM dt_demo;

SELECT * FROM dt_demo;

-- INSERT INTO dt_demo(name) VALUES ('이상한');
	
    
    
    
    
    
    
    
	
-- 메모
-- case쓸 시 위일수록 좁은 조건


```

```sql
-- p07.sql
USE practice;

CREATE TABLE dt_demo2 AS SELECT * FROM lecture.dt_demo;

SELECT * FROM dt_demo2;

-- FROM dt_demo; -> Error. FROM dt_demo2;

-- 종합 정보 표시
SELECT
	id, -- id
	name, -- name
    -- 닉네임 (NULL -> '미설정')
	IFNULL(nickname, '미설정') AS 닉네임,
	-- 출생년도 (19xx년생)
    DATE_FORMAT(birth, '%Y년생') AS 출생년도,
	-- 나이 (TIMESTAMPDIFF 로 나이만 표시)
    TIMESTAMPDIFF(YEAR, birth, CURDATE()) AS 나이,
	-- 점수 (소수 1자리 반올림, Null -> 0)
    ROUND(score, 1) AS 점수,
	-- 등급 (A >= 90 / B >= 80 / C >= 70 / D)
    CASE
		WHEN score >= 90 THEN 'A'
        WHEN score >= 80 THEN 'B'
        WHEN score >= 70 THEN 'C'
        ELSE 'D'
	END AS 등급,
	-- 상태 (is_active 가 1 이면 '활성' / 0 '비활성')
	IF(is_active=1, '활성', '비활성') AS 상태,
	-- 연령대 (청년 < 30 < 청장년 < 50 < 장년)
	CASE
		WHEN TIMESTAMPDIFF(YEAR, birth, CURDATE()) < 30 THEN '청년'
        WHEN TIMESTAMPDIFF(YEAR, birth, CURDATE()) < 50 THEN '청장년'
		ELSE '장년'
    END AS 연령대
FROM dt_demo2;  
```

```sql
-- insert-data-01.sql
USE lecture;

-- 1. 고객 테이블 생성
DROP TABLE IF EXISTS customers;
CREATE TABLE customers (
    customer_id VARCHAR(10) PRIMARY KEY,
    customer_name VARCHAR(50) NOT NULL,
    customer_type VARCHAR(20) NOT NULL,
    join_date DATE NOT NULL
);

-- 2. 매출 테이블 생성  
DROP TABLE IF EXISTS sales;
CREATE TABLE sales (
    id INT PRIMARY KEY,
    order_date DATE NOT NULL,
    customer_id VARCHAR(10) NOT NULL,
    product_id VARCHAR(10) NOT NULL,
    product_name VARCHAR(100) NOT NULL,
    category VARCHAR(50) NOT NULL,
    quantity INT NOT NULL,
    unit_price INT NOT NULL,
    total_amount INT NOT NULL,
    sales_rep VARCHAR(50) NOT NULL,
    region VARCHAR(50) NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

DESC customers;
DESC sales;

-- 4. 데이터 확인
SELECT * FROM customers;
SELECT * FROM sales;
SELECT COUNT(*) AS 매출건수 FROM sales;
```

```sql
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
```

```sql
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
```

```sql
-- 15-having.sql
USE lecture;

SELECT
	category,
    count(*) AS 주문건수,
    sum(total_amount) AS 월매출액
FROM sales
WHERE total_amount >= 1000000 -- 원본 데이터에 필터링을 걸고, GROUPing
GROUP BY category;


SELECT
	category,
    count(*) AS 주문건수,
    sum(total_amount) AS 총매출액
FROM sales
GROUP BY category
HAVING 총매출액 >= power(10, 6); -- 피벗테이블에 필터 추가


-- 활성 지역 찾기(주문건수 >= 20, 고객수 >= 15)
SELECT 
	region AS 지역,
    count(*) AS 주문건수,
    count(DISTINCT customer_id) AS 고객수,
    sum(total_amount) AS 총매출액,
    round(AVG(total_amount)) AS 평균주문액
FROM sales
GROUP BY region
HAVING 주문건수 >= 20 AND 고객수 >= 15;

-- 활성 지역 찾기(주문건수 >= 20, 고객수 >= 15)
SELECT
	region AS 지역,
    COUNT(*) AS 주문건수,
    COUNT(DISTINCT customer_id) AS 고객수,
    SUM(total_amount) AS 총매출액,
    ROUND(AVG(total_amount)) AS 평균주문액
FROM sales
GROUP BY region
HAVING 주문건수 >= 20 AND 고객수 >= 15;

-- 우수 영업사원 => 달 평균 매출액이 50만원이상
SELECT
	sales_rep AS 영업사원,
    COUNT(*) AS 사원별판매건수,
	COUNT(DISTINCT customer_id) AS 사원별고객수,
    SUM(total_amount) AS 사원별총매출,
    COUNT(DISTINCT DATE_FORMAT(order_date, '%Y-%m')) AS 활동개월수,
    ROUND(
		SUM(total_amount) / COUNT(DISTINCT DATE_FORMAT(order_date, '%Y-%m'))
	) AS 월평균매출
FROM sales
GROUP BY sales_rep
HAVING 월평균매출 >= 5 * power(10, 5)
ORDER BY 월평균매출 DESC;
-- ORDER BY ??;
```

```md
# TIL+

# CSV, XML, JSON 파일의 차이

## CSV 파일
- **엑셀, 스프레드시트 등에서 바로 열 수 있어 사람이 선호하는 형식**
- 표(테이블) 형태로 단순하고 직관적
- 데이터가 단순할 때 읽고 쓰기 매우 편리
- 비전문가도 쉽게 다룰 수 있음

---

## XML, JSON 파일
- **기계(컴퓨터)가 선호하는 형식**
- 복잡한 데이터 구조(중첩, 계층 등) 표현이 가능
- 시스템 간 데이터 교환, 웹/앱 개발, API 등에 널리 사용

---

## ai엔지니어링에서의 활용: MCP(Model Context Protocol)
- **MCP는 JSON 형식으로 이루어져 있음**
- JSON은 구조가 명확하고, 다양한 데이터 타입 및 계층 구조를 지원
- AI 엔지니어링, 데이터 교환, 자동화 등에서 효율적으로 사용

---

> **요약:**  
> - **CSV**: 사람이 보기 쉽고, 엑셀 등에서 바로 활용 가능  
> - **XML/JSON**: 기계가 복잡한 데이터 구조를 다루기에 적합  
> - **MCP** 등 AI 엔지니어링 분야에서는 **JSON**이 표준적으로 사용됨
```