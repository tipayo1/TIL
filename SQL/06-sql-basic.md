# 🎯 오늘 학습한 핵심 내용 TIL
## 오전: MySQL 고급 기능 완성


## 1. 테이블 관계 설계 완전 정리


### 1.1 관계 유형별 특징
#### 1:1 관계 (One-to-One)
사용 사례: 직원 ↔ 직원상세정보 (보안상 분리)

테이블 예시:

sql
CREATE TABLE employees (
    emp_id INT PRIMARY KEY,
    emp_name VARCHAR(50),
    department VARCHAR(30)
);

CREATE TABLE employee_details (
    emp_id INT PRIMARY KEY,  -- 같은 키 사용
    social_number VARCHAR(20),
    salary DECIMAL(10,2),
    FOREIGN KEY (emp_id) REFERENCES employees(emp_id) ON DELETE CASCADE
);
특징

보안/성능상 테이블 분리

같은 Primary Key 사용

CASCADE 옵션으로 데이터 일관성 유지

#### 1:N 관계 (One-to-Many)
사용 사례: 고객 ↔ 주문 (가장 흔한 관계)

customers (1) ↔ sales (N)

특징

외래키는 항상 'N'쪽에 위치

부모 삭제시 자식 데이터 처리 방법 고려

실무에서 가장 자주 사용

#### N:M 관계 (Many-to-Many)
사용 사례: 학생 ↔ 수업

테이블 예시:

sql
CREATE TABLE students (
    student_id INT PRIMARY KEY,
    student_name VARCHAR(50)
);
CREATE TABLE courses (
    course_id INT PRIMARY KEY,
    course_name VARCHAR(100)
);
CREATE TABLE student_courses (
    student_id INT,
    course_id INT,
    enrollment_date DATE,    -- 추가 정보 저장 가능
    grade VARCHAR(5),
    PRIMARY KEY (student_id, course_id),  -- 복합 기본키
    FOREIGN KEY (student_id) REFERENCES students(student_id),
    FOREIGN KEY (course_id) REFERENCES courses(course_id)
);
특징

반드시 중간 테이블 필요

중간 테이블에 추가 속성 저장 가능

복합 기본키 사용

## 2. 고급 JOIN 패턴
### FULL OUTER JOIN (MySQL에서 구현)
MySQL은 FULL OUTER JOIN 미지원 → UNION으로 구현

sql
SELECT c.customer_name, s.product_name, 'LEFT에서' AS 출처
FROM customers c LEFT JOIN sales s ON c.customer_id = s.customer_id
UNION
SELECT c.customer_name, s.product_name, 'RIGHT에서' AS 출처
FROM customers c RIGHT JOIN sales s ON c.customer_id = s.customer_id
WHERE c.customer_id IS NULL;
실무 사용: 데이터 무결성 검사, 마스터 데이터 통합

### CROSS JOIN (카르테시안 곱)
모든 조합 생성 (주의: 결과 많음)

sql
SELECT c.customer_name, p.product_name, p.selling_price
FROM customers c
CROSS JOIN products p
WHERE c.customer_type = 'VIP'
ORDER BY c.customer_name, p.selling_price DESC;
실무 활용

추천 시스템 (구매하지 않은 상품 찾기)

날짜별 기준 테이블 생성

시나리오 분석

### Self JOIN (같은 테이블끼리)
직원-상사 관계, 고객 유사성 분석 등

sql
SELECT
    직원.emp_name AS 직원명,
    상사.emp_name AS 상사명
FROM employees 직원
LEFT JOIN employees 상사 ON 직원.manager_id = 상사.emp_id;
실무 활용

조직도 구성

연속 주문 분석

고객 구매 패턴 유사성

## 3. 고급 서브쿼리 연산자
### ANY 연산자 - "하나라도 만족하면"
예시: VIP 고객들의 최소 주문액보다 높은 모든 주문

sql
SELECT product_name, total_amount
FROM sales
WHERE total_amount > ANY (
    SELECT s.total_amount
    FROM sales s
    JOIN customers c ON s.customer_id = c.customer_id
    WHERE c.customer_type = 'VIP'
);
동일한 의미: WHERE total_amount > (SELECT MIN(total_amount) FROM vip_orders);

대표 사례

어떤 기준보다 높은/낮은 값 찾기

다중 조건 중 일부만 만족해도 되는 경우

### ALL 연산자 - "모든 조건을 만족"
예시: 모든 VIP 고객 주문액보다 높은 주문

sql
SELECT product_name, total_amount
FROM sales
WHERE total_amount > ALL (
    SELECT s.total_amount
    FROM sales s
    JOIN customers c ON s.customer_id = c.customer_id
    WHERE c.customer_type = 'VIP'
);
동일한 의미: WHERE total_amount > (SELECT MAX(total_amount) FROM vip_orders);

대표 사례

모든 기준을 넘어서는 값 찾기

절대적 우위 조건

### EXISTS vs IN 성능 비교
동일한 결과, 다른 성능

sql
-- IN 방식
SELECT customer_name FROM customers
WHERE customer_id IN (SELECT customer_id FROM sales WHERE category = '전자제품');

-- EXISTS 방식 (일반적으로 더 빠름)
SELECT customer_name FROM customers c
WHERE EXISTS (SELECT 1 FROM sales s WHERE s.customer_id = c.customer_id AND s.category = '전자제품');
선택 기준

EXISTS: 큰 테이블, 복잡한 조건, 존재 여부만 확인

IN: 작은 값 목록, 간단한 조건

오후: PostgreSQL 기초 & 성능 체감
## 4. PostgreSQL vs MySQL 핵심 차이점
측면	MySQL	PostgreSQL
철학	빠르고 간단	표준 준수, 고급 기능
대상	웹 애플리케이션	엔터프라이즈, 분석
강점	단순 읽기 성능	복잡한 쿼리 최적화
### 4.2 데이터 타입 차이
MySQL 기본 타입

INT, VARCHAR, TEXT, DATE, DATETIME, JSON(5.7+)

PostgreSQL 고급 타입

배열 타입: tags TEXT[], scores INTEGER[]

JSONB (검색 최적화): metadata JSONB

네트워크 타입: ip_address INET, mac_address MACADDR

범위 타입: salary_range INT4RANGE, date_range DATERANGE

기하학적 타입: location POINT, area POLYGON

### 4.3 성능 특성
단순 읽기 성능

MySQL: 10,000 QPS (우수)

PostgreSQL: 8,000 QPS

→ 웹 애플리케이션에서는 MySQL이 유리

복잡한 분석 쿼리

MySQL: 15초 (제한적)

PostgreSQL: 8초 (우수)

→ 데이터 분석에서는 PostgreSQL이 유리

## 5. PostgreSQL 특화 기능
### 5.1 강력한 데이터 생성
generate_series 함수 (MySQL에는 없음)

sql
SELECT generate_series(1, 1000000) AS id;
SELECT generate_series('2024-01-01'::date, '2024-12-31'::date, '1 day') AS dates;
100만 건 대용량 데이터 한 번에 생성

sql
CREATE TABLE large_orders AS
SELECT
    generate_series(1, 1000000) AS order_id,
    'CUST-' || LPAD((random() * 50000)::text, 6, '0') AS customer_id,
    (random() * 1000000)::NUMERIC(12,2) AS amount,
    ARRAY['전자제품', '의류', '생활용품'][CEIL(random() * 3)::int] AS categories,
    jsonb_build_object('payment', 'card', 'express', random() < 0.3) AS details
FROM generate_series(1, 1000000);
### 5.2 고급 검색 기능
배열 검색

sql
SELECT * FROM orders WHERE '전자제품' = ANY(categories);
JSONB 검색 (인덱스 지원)

sql
SELECT * FROM orders WHERE details @> '{"express": true}';
범위 검색

sql
SELECT * FROM products WHERE price_range @> 50000;
## 6. EXPLAIN 분석 비교
### 6.1 MySQL EXPLAIN
테이블 형태 출력

sql
EXPLAIN SELECT * FROM sales WHERE customer_id = 'C001';
주요 컬럼

type: const > eq_ref > ref > range > index > ALL

Extra: Using index (좋음), Using filesort (주의)

### 6.2 PostgreSQL EXPLAIN
트리 형태 출력, 더 상세함

sql
EXPLAIN ANALYZE SELECT * FROM large_orders WHERE customer_id = 'CUST-025000';
정보

cost=0.42..8.45 (시작비용..총비용)

actual time=0.123..0.125 (실제 시간)

rows=1 (예상 행 수)

Buffers: shared hit=3 (메모리 사용량)

💡 실무 선택 가이드
MySQL을 선택해야 하는 경우
웹 애플리케이션 (블로그, 전자상거래)

단순한 CRUD 작업이 주된 경우

빠른 개발과 배포 필요

공유 호스팅 환경

제한된 메모리 환경

PostgreSQL을 선택해야 하는 경우
복잡한 비즈니스 로직 (ERP, CRM)

데이터 분석 및 리포팅

JSON 데이터 처리 중요

고급 SQL 기능 필요

데이터 무결성이 중요한 금융/회계 시스템

```sql
-- 22-one-to-one.sql
USE lecture;

CREATE TABLE employees(
  id INT PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(50) NOT NULL,
  hire_date DATE NOT NULL
);

CREATE TABLE employee_details(
  emp_id INT PRIMARY KEY,
  social_number VARCHAR(20) UNIQUE,
  address TEXT,
  salary DECIMAL(20),
  FOREIGN KEY (emp_id) REFERENCES employees(id) ON DELETE CASCADE
);

INSERT INTO employees VALUES
(1, '김철수', '2023-01-01'),
(2, '이영희', '2023-02-01'),
(3, '박민수', '2023-03-01');

INSERT INTO employee_details VALUES
(1, '123456-1234567', '서울시 강남구', 5000000),
(2, '234567-2345678', '서울시 서초구', 4500000),
(3, '345678-3456789', '부산시 해운대', 4000000);

SELECT * FROM employee_details;

-- '김철수'의 주소?
SELECT name, address 
FROM employees e
INNER JOIN employee_details ed ON e.id = ed.emp_id
WHERE e.name = '김철수';
```

```sql
-- 23-one-to-many.sql
USE lecture;

SELECT 
	c.customer_id, 
    c.customer_name,
    count(s.id) AS 주문횟수,
    GROUP_CONCAT(s.product_name) AS 주문제품들
    
FROM customers c
LEFT JOIN sales s ON c.customer_id = s.customer_id	
GROUP BY c.customer_id, c.customer_name;
```

```sql
-- 24-many-to-many.sql
USE lecture;

DROP TABLE IF EXISTS students_courses;
DROP TABLE IF EXISTS students;
DROP TABLE IF EXISTS courses;

CREATE TABLE students (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(20)
);

CREATE TABLE courses (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50),
    classroom VARCHAR(20)
);

-- 중간테이블 (Junction Table)  students:courses = M : N
CREATE TABLE students_courses (
  student_id INT,
  course_id INT,
  grade VARCHAR(5),
  PRIMARY KEY (student_id, course_id),  -- 복합 PK
  FOREIGN KEY(student_id) REFERENCES students(id),
  FOREIGN KEY(course_id) REFERENCES courses(id)
);

-- 데이터 삽입
INSERT INTO students VALUES
(1, '김학생'),
(2, '이학생' ),
(3, '박학생');

INSERT INTO courses VALUES
(1, 'MySQL 데이터베이스', 'A관 101호'),
(2, 'PostgreSQL 고급', 'B관 203호'),
(3, '데이터 분석', 'A관 704호');

INSERT INTO students_courses VALUES
(1, 1, 'A'),  -- 김학생이 MySQL 수강
(1, 2,'B+'), -- 김학생이 PostgreSQL 수강
(2, 1, 'A-'), -- 이학생이 MySQL 수강
(2, 3, 'B'),  -- 이학생이 데이터분석 수강
(3, 2, 'A+'), -- 박학생이 PostgreSQL 수강
(3, 3, 'A');  -- 박학생이 데이터분석 수강

-- 학생별 수강 과목
SELECT
	s.id,
    s.name,
    GROUP_CONCAT(c.name)
    
FROM students s
INNER JOIN students_courses sc ON s.id = sc.student_id
INNER JOIN courses c ON sc.student_id = c.id
GROUP BY s.id, s.name;

-- 과목별 정리
-- [과목명, 강의실, 수강인원, 수강 학생들(,), 학점 평균(A+ 4.3/A 4.0/A- 3.7/B+ 3.3/ b 3.0)]
SELECT
	c.id,
    c.name,
    c.classroom,
    count(sc.student_id) AS 수강인원,
    GROUP_CONCAT(s.name) AS 학생들,
    AVG(CASE
        WHEN sc.grade = 'A+' THEN 4.3
        WHEN sc.grade = 'A' THEN 4.0
        WHEN sc.grade = 'A-' THEN 3.7 
        WHEN sc.grade = 'B+' THEN 3.3 
        WHEN >= 'B' 3.0 THEN 
        ELSE 'C'
    ) AS 평균학점
    
FROM courses c
INNER JOIN students_courses sc ON c.id = sc.student_id
INNER JOIN students s ON sc.student_id = s.id
GROUP BY c.id, s.name, c.classroom;
```

```sql
-- 25-full-outer-join.sql

-- 데이터 무결성 검사(양쪽에 비어있는 데이터 찾기) 
-- MySQL에는 FULL OUTER JOIN이 없다 그래서 UNION을 이용해 흉내
USE lecture;

SELECT
	'LEFT에서' AS 출처,
    c.customer_name,
    s.product_name
FROM customers c
LEFT JOIN sales s ON c.customer_id = s.customer_id

UNION

SELECT
	'RIGHT에서' AS 출처,
    c.customer_name,
    s.product_name
FROM customers c
RIGHT JOIN sales s ON c.customer_id = s.customer_id
```

```sql
-- 26-cross-join.sql

USE lecture;

DROP TABLE IF EXISTS products;

CREATE TABLE products (
    product_id VARCHAR(10) PRIMARY KEY,
    product_name VARCHAR(100) NOT NULL,
    category VARCHAR(50) NOT NULL,
    cost_price DECIMAL(10, 2) NOT NULL,
    selling_price DECIMAL(10, 2) NOT NULL,
    stock_quantity INT NOT NULL,
    supplier VARCHAR(50) NOT NULL
);

INSERT INTO products VALUES
-- 전자제품 (P1xxx)
('P1001', '스마트폰', '전자제품', 600000, 900000, 50, 'Samsung'),
('P1002', '노트북', '전자제품', 800000, 1500000, 30, 'LG'),
('P1003', '태블릿', '전자제품', 300000, 500000, 25, 'Apple'),
('P1004', '이어폰', '전자제품', 20000, 50000, 150, 'Sony'),
('P1005', '스마트워치', '전자제품', 150000, 300000, 80, 'Apple'),

-- 의류 (P2xxx)
('P2001', '티셔츠', '의류', 15000, 35000, 100, '유니클로'),
('P2002', '청바지', '의류', 40000, 80000, 60, 'Levi\'s'),
('P2003', '운동화', '의류', 60000, 120000, 40, 'Nike'),
('P2004', '원피스', '의류', 30000, 70000, 90, 'ZARA'),
('P2005', '코트', '의류', 80000, 180000, 50, 'Uniqlo'),

-- 생활용품 (P3xxx)
('P3001', '세제', '생활용품', 3000, 8000, 200, 'P&G'),
('P3002', '샴푸', '생활용품', 5000, 15000, 150, 'L\'Oreal'),
('P3003', '청소기', '생활용품', 120000, 250000, 20, 'Dyson'),
('P3004', '수건', '생활용품', 8000, 20000, 200, 'Towel Master'),
('P3005', '베개', '생활용품', 15000, 40000, 120, 'Sleep Well'),

-- 식품 (P4xxx)
('P4001', '쌀', '식품', 25000, 45000, 80, '농협'),
('P4002', '라면', '식품', 2000, 4000, 300, '농심'),
('P4003', '과자', '식품', 1500, 3500, 250, '오리온'),
('P4004', '음료수', '식품', 800, 2000, 500, 'Coca-Cola'),
('P4005', '과일', '식품', 5000, 12000, 300, 'Fresh Farm');

-- 데이터 확인
SELECT * FROM products ORDER BY product_id;

-- 🚀 완전한 product_id 동기화 코드

-- product_name을 기준으로 새로운 product_id 체계로 업데이트
UPDATE sales s
INNER JOIN products p ON s.product_name = p.product_name
SET s.product_id = p.product_id;

-- 업데이트 결과 즉시 확인
SELECT 
    '업데이트 완료' AS 상태,
    s.product_id,
    s.product_name,
    COUNT(*) AS 주문수
FROM sales s
GROUP BY s.product_id, s.product_name
ORDER BY s.product_id;

SELECT count(*) FROM sales s
INNER JOIN products p ON s.product_id = p.product_id;


-- 카르테시안 곱(모든 경우의 수 조합)

SELECT
	c.customer_name,
    p.product_name,
    p.category,
    p.selling_price
FROM customers c
CROSS JOIN products p
WHERE c.customer_type = 'VIP'
ORDER BY c.customer_name, p.product_name;

-- 구매하지 않은 상품 추천


SELECT
	c.customer_name AS 고객명,
    p.product_name AS 미구매상품
FROM customers c
CROSS JOIN products p
-- VIP 고객이며, 구매하지 않은 상품만
WHERE c.customer_type = 'VIP' 
	AND NOT EXISTS (
	SELECT 1 FROM sales s
    WHERE s.customer_id = c.customer_id
    AND s.product_id = p.product_id
    )
ORDER BY c.customer_name, p.product_name;

SELECT 1 FROM sales s
    WHERE id = 1;
```

```sql
-- 27-self-join.sql

SELECT * FROM employees;
-- id 가 1 차이나면 적은사람이 상사, 많은사람이 직원
SELECT
  상사.name AS 상사명,
  직원.name AS 직원명
FROM employees 상사
LEFT JOIN employees 직원 ON 직원.id = 상사.id + 1;

-- 고객 간 구매 패턴 유사성
-- [손님1, 손님2, 공통구매카테고리수, 공통카테고리이름(GROUP_CONCAT)]

SELECT 
  c1.customer_id,
  c1.customer_name,
  c2.customer_id,
  c2.customer_name,
  COUNT(DISTINCT s1.category) AS 공통구매카테고리수,
  GROUP_CONCAT(DISTINCT s1.category) AS 공통카테고리
-- 1번 손님의 구매 데이터
FROM customers c1
INNER JOIN sales s1 ON c1.customer_id = s1.customer_id  -- 1번 손님의 구매 데이터
-- 2번 손님의 구매 데이터
INNER JOIN customers c2 ON c1.customer_id < c2.customer_id  -- 1번 손님과 다른 사람(2번)을 고르는 중
INNER JOIN sales s2 ON c2.customer_id = s2.customer_id -- 2번 손님의 구매 데이터
  AND s1.category = s2.category  -- s1, s2 의 카테고리가 같은것만 JOIN
GROUP BY c1.customer_id, c1.customer_name, c2.customer_id, c2.customer_name
ORDER BY 공통구매카테고리수 DESC;
```

```sql
-- 28-any-all.sql
-- ANY - 여러 값들 중에 하나라도 조건을 만족하면 TRUE (OR)

-- 1. VIP 고객들의 최소 주문액 보다 높은 모든 주문

SELECT s.total_amount
  FROM sales s
  INNER JOIN customers c on s.customer_id = c.customer_id
  WHERE c.customer_type = 'VIP';


SELECT
  customer_id,
  product_name,
  total_amount,
  '일반 고객이지만 VIP 최소보다 높음' AS 구분
FROM sales
WHERE total_amount > ANY(
 -- VIP 들의 모든 주문 금액들 (Vector)
  SELECT s.total_amount
  FROM sales s
  INNER JOIN customers c on s.customer_id = c.customer_id
  WHERE c.customer_type = 'VIP'
) AND
customer_id NOT IN (SELECT customer_id FROM customers WHERE customer_type = 'VIP')
ORDER BY total_amount DESC;
-- 위의 코드는 아래와 같음
SELECT
  customer_id,
  product_name,
  total_amount,
  '일반 고객이지만 VIP 최소보다 높음' AS 구분
FROM sales
WHERE total_amount > (
  SELECT MIN(s.total_amount) FROM sales s
  INNER JOIN customers c on s.customer_id = c.customer_id
  WHERE c.customer_type = 'VIP'
) AND
customer_id NOT IN (SELECT customer_id FROM customers WHERE customer_type = 'VIP')
ORDER BY total_amount DESC;

-- 어떤 지역 평균 매출액보다라도 높은 주문들.
SELECT
  region,
  product_name,
  total_amount
FROM sales s
WHERE total_amount > ANY(  -- 2. 보다 하나라도 더 크면 만족
  -- 1. 각 지역별 평균 매출액들  
  SELECT AVG(total_amount)
  FROM sales
  GROUP BY region
)
ORDER BY total_amount DESC;

-- ALL 벡터의 모든 값들이 조건을 만족해야 통과
-- 모든 부서의 평균연봉보다 더 높은 연봉을 받는 사람 (예시 - 실행 안됨)
SELECT * 
FROM employees
-- 서브쿼리 벡터의 모든 값보다 커야함.
WHERE salary > ALL(
    -- 각 부서의 평균 연봉 Vector
    SELECT AVG(salary)
    FROM employees
    GROUP BY department_id
);


```

```sql
-- 29-exists.sql

-- 전자제품을 구매(sales)한 고객 정보(customers)
SELECT
  customer_id, customer_name, customer_type
FROM customers
WHERE customer_id IN (
  SELECT customer_id FROM sales WHERE category='전자제품' -- 1, 2, 3, 4, 5, 6
);

SELECT
  customer_id, customer_name, customer_type
FROM customers c
WHERE EXISTS (
  SELECT 1 FROM sales s WHERE s.customer_id=c.customer_id AND s.category='전자제품'
);


-- EXISTS(~~한 적이 있는)
-- 전자제품과 의류를 모두 구매해 본적이 있고 동시에 50만원 이상 구매 이력도 가진 고객을 찾자.
SELECT
  c.customer_name,
  c.customer_type
FROM customers c
WHERE 
  -- 전자제품 구매
  EXISTS(SELECT 1 FROM sales s1 WHERE s1.customer_id = c.customer_id AND s1.category = '전자제품')
  AND
  -- 의류 구매
  EXISTS(SELECT 1 FROM sales s2 WHERE s2.customer_id = c.customer_id AND s2.category = '의류')
  AND
  -- 50만원 이상
  EXISTS(SELECT 1 FROM sales s3 WHERE s3.customer_id = c.customer_id AND s3.total_amount >= 500000);
  
  -- 3. NOT EXISTS
  
```

```md

```
# TIL+
```
```
<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" class="logo" width="120"/>

# ML Papers Explained - IT 용어를 모르는 사람을 위한 쉬운 설명

## 📚 이 문서가 무엇인가요?

**ML Papers Explained**는 인공지능(AI) 분야의 가장 중요한 연구 논문 549개를 정리한 종합 가이드북입니다. 마치 "AI 발전사 백과사전"이라고 생각하시면 됩니다.

## 🎯 왜 이런 문서가 필요할까요?

인공지능은 매년 수천 개의 새로운 연구가 발표되는 빠르게 발전하는 분야입니다. 하지만 그중에서 정말 중요한 것들만 골라서 이해하기 쉽게 정리한 자료는 드물었습니다. 이 문서는 바로 그 역할을 합니다.

## 🗂️ 문서 구성 - 10개 주요 분야

### 1. **언어 모델 (Language Models)** - 172개 논문

- **쉬운 설명**: 컴퓨터가 사람처럼 글을 읽고 쓸 수 있게 만드는 기술
- **실생활 예시**: ChatGPT, 번역기, 음성인식기
- **중요한 발전**:
    - 2017년 Transformer → AI가 문맥을 이해하게 됨
    - 2018년 BERT, GPT → 더 자연스러운 대화 가능
    - 2023년 ChatGPT → 일반인도 쉽게 사용할 수 있게 됨


### 2. **수학 특화 AI (LLMs For Math)** - 34개 논문

- **쉬운 설명**: 수학 문제를 풀어주는 특별한 AI
- **실생활 예시**: 수학 숙제 도우미, 과학 계산기
- **왜 중요한가**: 단순 암기가 아닌 논리적 사고가 필요한 영역


### 3. **멀티모달 AI (Multi Modal Language Models)** - 60개 논문

- **쉬운 설명**: 글과 사진을 함께 이해하는 AI
- **실생활 예시**: 사진을 보고 설명해주는 AI, 이미지 생성 AI
- **발전 과정**: 텍스트만 → 이미지도 → 동영상까지


### 4. **정보 검색 기술 (Retrieval and Representation Learning)** - 32개 논문

- **쉬운 설명**: 필요한 정보를 빠르고 정확하게 찾는 기술
- **실생활 예시**: 구글 검색, 쇼핑몰 상품 추천
- **핵심 원리**: 의미가 비슷한 것들을 묶어서 관리


### 5. **효율적인 AI 훈련 (Parameter Efficient Fine Tuning)** - 11개 논문

- **쉬운 설명**: 거대한 AI를 적은 비용으로 새로운 일에 적응시키는 기술
- **비유**: 전체 직원을 새로 뽑는 대신, 기존 직원 일부만 재교육하는 것
- **왜 중요한가**: 시간과 비용을 크게 절약


### 6. **이미지 인식 AI의 진화**

- **전통적 방식 (CNNs)** - 21개 논문: 사진을 격자로 나눠서 분석
- **새로운 방식 (Vision Transformers)** - 19개 논문: 사진을 퍼즐 조각처럼 나눠서 분석


### 7. **문서 이해 AI (Document AI)** - 14개 논문

- **쉬운 설명**: 복잡한 문서를 읽고 이해하는 AI
- **실생활 예시**: 계약서 요약, 영수증 정리, PDF 내용 검색
- **특별한 점**: 글자뿐만 아니라 표, 그림의 위치까지 이해


### 8. **AI 훈련용 데이터 (Datasets)** - 19개 논문

- **쉬운 설명**: AI를 가르치기 위한 교재들
- **비유**: 학생에게 좋은 교과서가 필요하듯, AI에게도 좋은 데이터가 필요
- **최신 동향**: 더 다양하고 고품질의 데이터 제작


### 9. **AI 훈련 방법론 (LLM Training)** - 41개 논문

- **쉬운 설명**: AI를 더 똑똑하게 만드는 다양한 교육 방법들
- **핵심 개념**:
    - 기본 훈련 → 특화 훈련 → 인간 피드백 반영
    - 자가 학습, 강화 학습 등 고급 기법들


### 10. **기타 전문 분야들**

- 객체 인식, 이미지 생성, 모델 압축 등


## 📈 AI 발전 타임라인

### 🕰️ **1998-2010년: 딥러닝의 태동**

- 기초적인 이미지 인식 기술 개발
- 컴퓨터가 단순한 패턴을 인식하기 시작


### 🚀 **2011-2016년: 딥러닝 혁명**

- AlexNet, ResNet 등장으로 이미지 인식 성능 급상승
- "AI 겨울" 종료, 본격적인 AI 시대 시작


### 🔥 **2017-2019년: Transformer 시대 개막**

- 2017년 Transformer 논문 → AI 역사의 분기점
- BERT, GPT 등장 → 자연어 처리 혁명
- AI가 맥락을 이해하기 시작


### 🌟 **2020-2022년: 거대 AI 모델 시대**

- GPT-3 → 일반인도 놀랄 만한 성능
- 멀티모달 AI → 텍스트와 이미지 동시 처리
- AI가 창작 영역까지 진입


### 💫 **2023-2024년: ChatGPT 혁명과 대중화**

- ChatGPT 출시 → AI의 일상화
- GPT-4, Claude, Gemini 등 경쟁 심화
- AI가 업무와 교육에 본격 활용


### 🔮 **2025년: 전문화와 효율화**

- 더 작지만 똑똑한 모델들
- 특정 분야에 특화된 AI들
- 실시간 추론과 개인화


## 💡 왜 이 문서가 중요한가요?

### 📖 **종합적인 학습 가이드**

- AI 전 분야의 핵심을 한 번에 파악 가능
- 초보자부터 전문가까지 모두에게 유용


### 🗺️ **AI 발전사의 지도**

- 각 기술이 언제, 왜 등장했는지 이해
- 현재 AI 기술의 배경과 맥락 파악


### 🔍 **실무 적용 가이드**

- 어떤 AI 기술을 언제 사용해야 하는지 판단 도움
- 최신 트렌드와 미래 방향성 제시


### 📚 **평생 학습 자료**

- 새로운 논문이 계속 추가되는 살아있는 문서
- AI 분야 종사자들의 필수 레퍼런스


## 🎯 일반인에게 주는 메시지

**"AI가 어렵고 복잡해 보이지만, 결국은 인간의 문제를 해결하기 위한 도구들의 발전사입니다."**

- 각 기술은 특정한 문제를 해결하기 위해 만들어짐
- 복잡한 수식과 용어 뒤에는 simple한 아이디어가 숨어 있음
- AI의 발전은 인간의 창의성과 끈기의 결과물

이 문서는 AI 분야의 "역사책"이자 "가이드북"으로, IT 전문 지식이 없어도 AI가 어떻게 발전해왔고, 앞으로 어디로 향하고 있는지 이해할 수 있게 도와주는 소중한 자료입니다.

<div style="text-align: center">⁂</div>

[^1]: paste.txt
```

```
<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" class="logo" width="120"/>

# 앞으로는 웹 서비스들의 ui는 채팅창으로 귀결될거라는 말도 있는데 이런 면에 대해서는 혹시 어떤 관점 있으신지 궁금합니다 서비스들의 변화 방향이라던가 개발자의 아키텍처 설계 방향같은면에 대한 생각이 궁금합니다

웹 서비스의 UI가 앞으로 채팅창(대화형 인터페이스) 중심으로 귀결될 것이라는 전망은 최근 AI와 사용자 경험(UX) 혁신 흐름에서 매우 중요한 논의입니다. 이에 대해 다음과 같은 관점과 전망, 그리고 개발자/아키텍처 설계 측면에서의 방향성을 정리할 수 있습니다.

### 1. **채팅 UI의 부상, 그리고 한계**

- **자유도와 유연성**
채팅 인터페이스는 사용자가 자연어로 다양한 요청을 할 수 있어, 기존의 메뉴 기반 UI보다 훨씬 유연하게 서비스를 탐색하고 이용할 수 있습니다. AI 챗봇, Copilot 등에서 이미 표준 인터페이스로 자리잡고 있습니다[^1][^2].
- **직관성의 도전**
하지만, 모든 사용자가 어떤 질문을 해야 할지, 어떻게 요청해야 할지 모르는 '백지 증후군'이 발생할 수 있습니다. 따라서 채팅 UI만으로는 직관성과 효율성을 모두 만족시키기 어렵다는 지적도 있습니다[^3].


### 2. **미래의 서비스 변화 방향**

- **하이브리드 UI의 등장**
채팅창이 중심이 되되, 버튼, 위젯, 추천 액션 등 **구조화된 인터랙티브 컴포넌트**가 결합된 하이브리드 형태가 대세가 될 전망입니다. 예를 들어, 챗봇이 답변과 함께 관련 옵션 버튼, 슬라이더, 위젯 등을 즉석에서 제공해 사용자가 추가 입력 없이 다양한 기능을 바로 실행할 수 있습니다[^3][^1].
- **개인화와 맥락 인식**
AI가 사용자의 관심사, 과거 행동, 현재 맥락을 실시간으로 파악해 맞춤형 제안과 정보를 제공하는 방향으로 진화합니다. 이는 채팅형 UI의 핵심 경쟁력 중 하나입니다[^2][^4].
- **음성·멀티모달 인터페이스**
텍스트 채팅뿐 아니라 음성, 이미지, 파일 등 다양한 입력/출력 방식이 결합된 멀티모달 인터페이스로 확장되고 있습니다[^1].


### 3. **개발자 및 아키텍처 설계 방향**

| 변화 요소 | 설계 방향 및 고려점 |
| :-- | :-- |
| **대화 상태 관리** | 대화 이력, 사용자 맥락, 세션 상태를 효과적으로 저장·관리하는 백엔드 설계 필요[^5]. |
| **동적 UI 합성** | AI가 상황에 따라 버튼, 위젯, 폼 등 UI 컴포넌트를 실시간으로 생성·제공할 수 있는 프론트엔드 구조[^3][^1]. |
| **API/서비스 분리** | 채팅 인터페이스와 백엔드 서비스(검색, 추천, 결제 등) 간의 명확한 분리 및 API 기반 통신[^6][^4]. |
| **확장성과 모듈화** | 마이크로서비스 아키텍처(MSA) 등 유연한 구조로, 다양한 기능 추가와 확장이 용이하도록 설계[^6][^4]. |
| **AI 통합** | 자연어 처리, 추천, 개인화 등 AI 기능을 서비스 핵심에 통합하고, 실시간 데이터 연동 구조 확보[^2][^4]. |
| **접근성 및 반응형 디자인** | 다양한 기기(모바일, 데스크톱)와 상황에 맞는 반응형 UI, 접근성 표준 준수[^7][^8]. |

### 4. **결론 및 전망**

- **채팅 UI는 앞으로도 강력한 트렌드**이지만, 모든 서비스가 완전히 채팅창만으로 귀결되지는 않을 것입니다.
- **채팅형 UI + 인터랙티브 컴포넌트 + 개인화**가 결합된 하이브리드·적응형 인터페이스가 주류가 될 가능성이 높습니다.
- 개발자와 아키텍트는 **대화 상태 관리, 동적 UI 합성, API 기반 서비스 분리, AI 통합, 확장성**을 핵심 설계 원칙으로 삼아야 하며, 사용자 경험과 기술적 유연성의 균형을 고민해야 합니다.

이러한 변화는 단순한 UI의 변화가 아니라, 서비스 구조와 데이터 흐름, 사용자 경험 전체의 혁신으로 이어질 것입니다[^3][^2][^1].

<div style="text-align: center">⁂</div>

[^1]: https://story.pxd.co.kr/1783

[^2]: https://seo.goover.ai/report/202507/go-public-report-ko-72ee8424-49f1-41ab-9864-4a3c7d239079-0-0.html

[^3]: https://yozm.wishket.com/magazine/detail/3121/

[^4]: https://tech.ktcloud.com/267

[^5]: https://bcuts.tistory.com/141

[^6]: https://www.msap.ai/blog/msa-design-how-leverage-ai/

[^7]: https://yozm.wishket.com/magazine/detail/3008/

[^8]: https://brunch.co.kr/@@hd6L/93

[^9]: https://clickup.com/ko/blog/142831/software-engineering-trends

[^10]: https://velog.io/@syub98774/채팅-서비스를-구현하기-전에-채팅-UI를-구현해보자

[^11]: https://sendbird.com/ko/blog/resources-for-modern-chat-app-ui

[^12]: https://sbctech.net/workspace-update/eobdeiteusaelobgegaeseondoenweb-yonggooglechaetingui/

[^13]: https://www.designkits.co.kr/blog/know-how/2025-webdesign-trend

[^14]: https://brunch.co.kr/@dailyuxstory/5

[^15]: https://letspl.me/quest/1427/2025년 UIUX 디자인 트렌드

[^16]: https://brunch.co.kr/@ultra0034/32

[^17]: https://velog.io/@eunsuknoh/wc-project-til-241115

[^18]: https://velog.io/@imyein000/03-ptl06oi5

[^19]: https://www.pxd.co.kr/ko/insights/ai-ui-ux-1

[^20]: https://www.muff.co.kr/news/?bmode=view\&idx=134952446

[^21]: https://brunch.co.kr/@pealpark/13

[^22]: https://ditoday.com/국민-메신저-카카오톡과-라인의-ui·ux-디자인/

[^23]: https://brunch.co.kr/@qnn-na/10

[^24]: https://ditoday.com/kakaotalk-icon-design-changes/

[^25]: https://designcompass.org/2025/01/27/wix-2025-trend/

[^26]: https://velog.io/@wns450/로드맵-회고-및-재작성하기

[^27]: https://insight.infograb.net/blog/2025/02/05/2025-devtrends/

[^28]: https://appmaster.io/ko/blog/2023nyeon-web-gaebal-reideo-sangwi-10dae-teurendeu

[^29]: https://notavoid.tistory.com/72

[^30]: https://www.samsungsds.com/kr/insights/agentic-ai-to-optimize-multi-cloud-environments.html

[^31]: https://junesker.tistory.com/122

[^32]: https://yozm.wishket.com/magazine/detail/2364/

[^33]: https://learn.microsoft.com/ko-kr/azure/architecture/ai-ml/

[^34]: https://brunch.co.kr/@likelion/131

[^35]: https://boottent.com/community/article/20240425103326

[^36]: https://www.f5.com/ko_kr/company/blog/understanding-ai-application-architecture

[^37]: https://dev.mescius.co.kr/bbs/board.php?bo_table=Insight\&wr_id=175\&page=1

[^38]: https://texit.tistory.com/entry/웹-개발자를-위한-최신-트렌드-탐구

[^39]: https://velog.io/@0like/AI-서비스-개발-과정

[^40]: https://sprint.codeit.kr/blog/2025-프론트엔드-개발자-취업-로드맵


```

```
<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" class="logo" width="120"/>

### MCP 서버의 악용 가능성과 보안 이슈

#### 1. 악의적 MCP 서버 및 악성 정보 업로드 가능성

- **누구나 MCP 서버를 직접 만들어 배포할 수 있으며, 검증되지 않은 MCP 서버에 악의적 코드나 정보를 숨겨 배포하는 사례가 실제로 보고되고 있습니다.**
예를 들어, 공격자는 정상적인 도구처럼 보이는 MCP 서버를 만들어 공개 저장소나 개발자 커뮤니티에 업로드할 수 있습니다. 사용자가 이를 신뢰하고 설치하면, 내부적으로 악성 코드를 실행하거나 시스템에 백도어를 설치할 수 있습니다[^1][^2][^3].
- **MCP 서버의 도구 설명이나 프롬프트 템플릿에 악의적 명령을 숨기는 것도 가능합니다.**
예를 들어, 도구 설명에 "특정 단어 입력 시 대화 로그를 외부 서버로 전송" 같은 명령을 숨겨두고, 사용자가 특정 단어를 입력하면 민감한 정보가 유출될 수 있습니다[^3][^4].


#### 2. 주요 보안 이슈

- **명령어/코드 인젝션**
입력값 검증이 미흡한 MCP 서버는 공격자가 임의의 시스템 명령을 실행하게 만들 수 있습니다. 실제로 수많은 MCP 서버가 명령어 인젝션, 경로 탐색, 임의 파일 읽기 등 심각한 취약점을 가지고 있는 것으로 조사되었습니다[^5][^6][^7][^8].
- **프롬프트 인젝션 및 컨텍스트 오염**
악의적 데이터(문서, 티켓 등)를 LLM에 전달해, AI가 의도치 않은 행동(정보 유출, 권한 상승 등)을 하도록 유도할 수 있습니다[^4][^9][^6].
- **과도한 권한 및 인증/인가 미흡**
일부 MCP 서버는 필요 이상의 권한을 부여받아, 공격 시 더 많은 시스템/데이터에 접근할 수 있습니다. 인증·인가가 제대로 구현되지 않으면, 누구나 MCP 서버를 통해 민감 정보에 접근할 수 있습니다[^10][^11][^12].
- **공급망 공격**
MCP 서버 코드 자체에 악성코드가 포함될 수 있으며, 공식 저장소가 없는 경우 신뢰할 수 없는 MCP 서버가 유통될 위험이 큽니다[^1][^12].
- **Shadow MCP(그림자 MCP) 문제**
보안팀의 관리 밖에서 설치된 MCP 서버가 조직 내 보안 사각지대를 만들고, 공격자가 이를 악용해 내부 시스템에 침투할 수 있습니다[^3].


#### 3. MCP 서버가 내 정보를 빼갈 위험

- **실제로 MCP 서버가 내 정보를 빼갈 수 있는 구조적 위험이 존재합니다.**
    - MCP 서버는 다양한 외부 서비스(이메일, 파일, DB 등)에 접근할 수 있는 인증 토큰이나 API 키를 저장합니다. 공격자가 MCP 서버를 탈취하거나 악성 MCP를 설치하면, 이 토큰을 통해 사용자의 여러 서비스 데이터에 접근·유출할 수 있습니다[^11][^9][^2].
    - 악성 MCP 서버 또는 취약한 MCP 서버는 사용자의 파일, 대화 내용, 인증 정보 등을 외부로 전송하거나, 추가 악성코드를 설치할 수 있습니다[^1][^2][^6].
    - 특히, 프롬프트 인젝션·명령어 인젝션 등으로 사용자가 인지하지 못하는 사이에 데이터가 외부로 유출될 수 있습니다[^4][^6].


#### 4. 안전하게 MCP 서버를 사용하려면

- 신뢰할 수 있는 공식 저장소에서만 MCP 서버를 설치하고, 디지털 서명 등 무결성 검증을 반드시 수행해야 합니다[^1][^12].
- MCP 서버의 권한을 최소화하고, 불필요한 시스템/데이터 접근 권한을 제거해야 합니다[^10][^11][^4].
- 입력값 검증, 인증·인가, 로그 모니터링 등 기본적인 보안 조치를 철저히 적용해야 합니다[^4][^3][^12].
- 새로운 MCP 서버나 도구를 도입할 때는 반드시 보안팀의 검토와 승인을 거쳐야 하며, 그림자 MCP 설치를 방지해야 합니다[^3].

**결론:**
MCP 서버는 누구나 만들 수 있고, 악의적으로 악성 정보를 포함하거나 내 정보를 빼가는 데 악용될 수 있습니다. 실제로 다양한 보안 이슈와 악용 사례가 보고되고 있으므로, MCP 서버 사용 시 신뢰성과 보안성을 반드시 검증해야 합니다.

<div style="text-align: center">⁂</div>

[^1]: https://live.paloaltonetworks.com/t5/community-blogs/mcp-security-exposed-what-you-need-to-know-now/ba-p/1227143

[^2]: https://www.catonetworks.com/blog/cato-ctrl-exploiting-model-context-protocol-mcp/

[^3]: https://techcommunity.microsoft.com/blog/microsoftdefendercloudblog/plug-play-and-prey-the-security-risks-of-the-model-context-protocol/4410829

[^4]: https://www.prompt.security/blog/top-10-mcp-security-risks

[^5]: https://equixly.com/blog/2025/03/29/mcp-server-new-security-nightmare/

[^6]: https://www.backslash.security/blog/hundreds-of-mcp-servers-vulnerable-to-abuse

[^7]: https://www.infosecurity-magazine.com/news/mcp-servers-risk-rce-data-leaks/

[^8]: https://www.darkreading.com/cloud-security/hundreds-mcp-servers-ai-models-abuse-rce

[^9]: https://www.upwind.io/feed/unpacking-the-security-risks-of-model-context-protocol-mcp-servers

[^10]: https://techcommunity.microsoft.com/blog/microsoft-security-blog/understanding-and-mitigating-security-risks-in-mcp-implementations/4404667

[^11]: https://www.pillar.security/blog/the-security-risks-of-model-context-protocol-mcp

[^12]: https://www.redhat.com/en/blog/model-context-protocol-mcp-understanding-security-risks-and-controls

[^13]: https://www.trendmicro.com/en_dk/research/25/f/why-a-classic-mcp-server-vulnerability-can-undermine-your-entire-ai-agent.html

[^14]: https://www.backslash.security/blog/top-risks-mcp-servers-ide

[^15]: https://www.trendmicro.com/ko_kr/research/25/f/why-a-classic-mcp-server-vulnerability-can-undermine-your-entire-ai-agent.html

[^16]: https://www.reddit.com/r/mcp/comments/1jr7sfc/mcp_is_a_security_nightmare/

[^17]: https://sysdig.com/blog/why-mcp-server-security-is-critical-for-ai-driven-enterprises/

[^18]: https://www.cyberark.com/resources/threat-research-blog/poison-everywhere-no-output-from-your-mcp-server-is-safe


```

```
<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" class="logo" width="120"/>

# 클로드 데스크탑

**클로드 데스크탑(Claude Desktop)**은 Anthropic의 AI 모델 Claude를 윈도우나 맥 기반 PC에서 직접 사용할 수 있게 해주는 데스크탑 애플리케이션입니다. 이 프로그램은 단순한 챗봇이 아니라, 실제 컴퓨터를 사람처럼 조작할 수 있는 **AI 에이전트**로 동작합니다. 즉, Claude가 컴퓨터 화면을 인식하고, 마우스와 키보드를 제어하며, 파일을 읽고 쓰고, 소프트웨어를 실행하는 등 복잡한 작업을 자동화할 수 있게 해줍니다[^1][^2][^3][^5][^6].

### 주요 특징 및 기능

- **MCP(Model Context Protocol) 기반**: Claude Desktop은 MCP 서버와 안전하게 통신하며, 파일 시스템, 파이썬 실행, 시스템 명령 등 다양한 MCP 서버를 통해 로컬 리소스에 접근하고 도구를 실행할 수 있습니다[^2][^6][^8].
- **파일 시스템 제어**: AI가 사용자의 PC에서 파일을 읽고, 쓰고, 이동할 수 있습니다. 예를 들어, 문서 요약, 파일 정리, 자동 보고서 생성 등이 가능합니다[^2][^5][^7].
- **코드 실행 및 자동화**: 파이썬 등 스크립트 언어를 실행할 수 있어, AI가 직접 프로그램을 작성하고 실행하여 반복 작업이나 데이터 분석, 테스트 자동화 등을 수행할 수 있습니다[^2][^5][^8].
- **화면 인식 및 제어**: Claude는 컴퓨터 화면을 스크린샷으로 인식하고, 마우스 클릭, 키보드 입력 등 실제 사용자처럼 다양한 작업을 수행할 수 있습니다[^1][^3][^5].
- **자연어 명령 지원**: 사용자는 "내 데스크톱의 파일을 정리해 줘", "2023년 매출 데이터를 분석해 줘"처럼 자연어로 명령을 내릴 수 있으며, Claude가 이를 해석해 필요한 작업을 자동으로 처리합니다[^7].
- **다양한 소프트웨어 활용**: 텍스트 편집기, 웹 브라우저, 스프레드시트 등 표준 데스크톱 소프트웨어를 직접 사용할 수 있습니다[^3][^5].
- **보안 및 권한 관리**: Claude가 접근하거나 수정할 수 있는 파일, 명령, 시간 등을 세밀하게 통제할 수 있어 보안과 데이터 보호가 가능합니다[^5][^6].


### 활용 예시

| 활용 분야 | 예시 명령/작업 |
| :-- | :-- |
| 파일 관리 | "내 문서 폴더에 있는 PDF를 모두 요약해줘" |
| 데이터 분석 | "2023년 매출 데이터를 분석해서 보고서로 만들어줘" |
| 소프트웨어 자동화 | "이 스프레드시트 데이터를 웹 양식에 자동 입력해줘" |
| 개발/테스트 | "이 파이썬 코드를 실행해서 결과를 보여줘" |
| 반복 업무 자동화 | "매일 아침 이메일 첨부 파일을 지정 폴더로 저장해줘" |

### 설치 및 사용

- 인터넷에서 **Claude Desktop**을 검색해 설치할 수 있으며, 설치 후 MCP 서버(파일 시스템, 파이썬 실행, 시스템 명령 등)를 구성하면 AI가 로컬 컴퓨터 자원에 접근할 수 있습니다[^2][^8].
- 실제로는 보안 및 시스템 권한, 데이터 보호 이슈를 항상 염두에 두고 사용해야 합니다[^5][^7].

**클로드 데스크탑**은 기존의 AI 챗봇과 달리, 실제 데스크탑 환경에서 사람처럼 다양한 작업을 자동화할 수 있는 차세대 AI 에이전트 플랫폼입니다.

<div style="text-align: center">⁂</div>

[^1]: https://www.magicaiprompts.com/docs/claude/claude-computer-use-ai-agent-era/

[^2]: https://irepublic.tistory.com/7891163

[^3]: https://fornewchallenge.tistory.com/entry/🤖Claude-Computer-Use-사용-가이드-컴퓨터를-사람처럼-사용하는-AI

[^4]: https://www.reddit.com/r/ClaudeAI/comments/1jiffk6/why_bother_installing_claude_for_desktop/?tl=ko

[^5]: https://www.unite.ai/ko/why-ai-developers-are-buzzing-about-claude-3-5s-computer-use-feature/

[^6]: https://wikidocs.net/268822

[^7]: https://seo.goover.ai/report/202503/go-public-report-ko-50008600-8be9-4b48-acbc-06b53a5e37d0-0-0.html

[^8]: https://www.magicaiprompts.com/docs/claude/how-to-use-mcp/

[^9]: https://datasciencebeehive.tistory.com/182

[^10]: https://marcus-story.tistory.com/148

```
```
<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" class="logo" width="120"/>

# 컨텍스트 엔지니어링에 대해

**컨텍스트 엔지니어링(Context Engineering)**은 AI, 특히 대형 언어모델(LLM)이 단순히 질문에 답하는 수준을 넘어, 실제 과업을 성공적으로 수행할 수 있도록 **전체 정보, 도구, 구조, 상태 등 모든 맥락(Context)을 체계적으로 설계·관리·제공하는 전략적 방법론**입니다[^1][^2][^3][^4].

### 기존 프롬프트 엔지니어링과의 차이

| 구분 | 프롬프트 엔지니어링 | 컨텍스트 엔지니어링 |
| :-- | :-- | :-- |
| 초점 | 효과적인 질문/지시문 작성 | 과업 수행 전체 환경 설계 |
| 범위 | 단일 입력 텍스트 | 대화 이력, 외부 데이터, 도구 등 전체 맥락 |
| 방식 | 정적 구성 | 동적·실시간 정보, 도구 호출 등 |
| 목적 | 원하는 답 유도 | 정확하고 실행 가능한 결과 생성 |
| 주요 기법 | Zero-shot, Few-shot 등 | RAG, Tool Calling, 상태 관리 등 |

### 컨텍스트 엔지니어링의 주요 요소

- **시스템 프롬프트**: 모델의 역할, 규칙, 말투 등 행동 지침[^1][^5][^6][^3].
- **사용자 프롬프트**: 사용자의 실시간 요청[^1][^5][^6].
- **대화 히스토리/상태**: 이전 대화 내용, 최근 상호작용 정보[^1][^5][^6][^3].
- **장기 메모리**: 과거 프로젝트, 사용자 선호, 요약 등 장기 정보[^1][^5][^6][^3].
- **외부 정보(RAG)**: 실시간 문서, DB, API 등에서 가져온 최신 정보[^1][^5][^2][^6].
- **도구 및 함수 호출**: 외부 API, 계산기, 캘린더 등 사용 가능한 도구 목록과 사용법[^1][^5][^2][^6][^4].
- **출력 포맷 정의**: JSON, 표 등 결과의 구조화 방식[^1][^5][^6][^3].
- **글로벌 상태/컨텍스트**: 여러 단계 작업에서 공유되는 정보[^6].


### 컨텍스트 엔지니어링의 핵심 전략

- **전체 시스템적 접근**: 단일 프롬프트가 아닌, LLM 호출 전후의 모든 정보를 통합·관리하는 시스템 설계[^1][^5][^7][^3][^4].
- **동적 맥락 조립**: 사용자의 요청, 실시간 데이터, 도구 결과 등을 작업 목적에 맞게 선별·요약·구조화하여 LLM에 전달[^5][^7][^4].
- **신호-잡음 비 관리**: 과제 해결에 꼭 필요한 정보만 선별, 불필요한 데이터는 배제[^4].
- **도구 및 외부 시스템 통합**: API, DB, 코드 실행 등 다양한 외부 리소스와의 연동 및 결과 통합[^2][^6][^4].
- **출력 구조화**: 결과를 명확하고 일관된 포맷으로 반환하여 후속 처리가 용이하도록 설계[^1][^3].
- **상태 및 메모리 관리**: 컨텍스트 윈도우 한계를 극복하기 위해 요약, 계층적 메모리, 온디맨드 리트리벌 등 다양한 기법 활용[^4].
- **엔드투엔드 검증 및 개선**: 전체 파이프라인의 성능을 실험하고 피드백 기반으로 반복 개선[^4].


### 왜 중요한가?

- **현대 AI 에이전트의 성공/실패는 모델 성능보다 컨텍스트의 질에 좌우**됩니다[^5][^7].
- 실제 비즈니스 과업(예: 일정 관리, 이메일 작성, 데이터 분석 등)을 자동화하려면, LLM이 상황과 목적을 정확히 이해할 수 있도록 맥락을 정교하게 설계해야 합니다[^2][^3].


### 요약

컨텍스트 엔지니어링은 단순한 프롬프트 설계를 넘어서, LLM이 실제 환경과 목적을 이해하고, 필요한 정보·도구·상태를 동적으로 조합하여 **실질적인 문제 해결 능력**을 갖추도록 만드는 **AI 시스템 설계의 핵심 역량**입니다[^1][^5][^2][^7][^6][^3][^4].

<div style="text-align: center">⁂</div>

[^1]: https://digitalbourgeois.tistory.com/1543

[^2]: https://www.aimizing.ai/blog/250702-context-engineering

[^3]: https://marcus-story.tistory.com/209

[^4]: https://tilnote.io/pages/6865e2254b4cd555fb94f5ea

[^5]: https://www.philschmid.de/context-engineering

[^6]: https://www.llamaindex.ai/blog/context-engineering-what-it-is-and-techniques-to-consider

[^7]: https://news.hada.io/topic?id=21752

[^8]: https://digitaltransformation.co.kr/왜-지금-컨텍스트-엔지니어링context-engineering인가-프롬프트-엔/

[^9]: https://www.linkedin.com/posts/emollick_the-hottest-discussion-in-ai-is-about-context-activity-7343723250171977729-STux

[^10]: https://www.threads.com/@unclejobs.ai/post/DLw3xs9JBUw/context는-언제나-중요한데-api를-활용해서-agent를-만들거나-서비스-제작할-때-multi-agent와-연계해서-context-engi

[^11]: https://www.youtube.com/watch?v=5w9KiIbei1c

[^12]: https://ai-pro.org/learn-ai/articles/why-context-engineering-is-redefining-how-we-build-ai-systems/

[^13]: https://www.marktechpost.com/2025/07/06/what-is-context-engineering-in-ai-techniques-use-cases-and-why-it-matters/

[^14]: https://peterica.tistory.com/956

[^15]: https://velog.io/@cosmo_numm/AI-%ED%94%84%EB%A1%AC%ED%94%84%ED%8A%B8-%EC%97%94%EC%A7%80%EB%8B%88%EC%96%B4%EB%A7%81%EC%BB%A8%ED%85%8D%EC%8A%A4%ED%8A%B8-%ED%99%9C%EC%9A%A9

[^16]: https://hyper.ai/kr/headlines/e037f02b6a53e0a2573c30e78d87775b

[^17]: https://www.youtube.com/watch?v=CeZPsKo1nXw

[^18]: https://www.youtube.com/watch?v=ioOHXt7wjhM

[^19]: https://boristane.com/blog/context-engineering/

[^20]: https://github.com/coleam00/context-engineering-intro

```
