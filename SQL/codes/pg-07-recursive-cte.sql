-- -- pg-07-recursive-cte.sql

-- CREATE TABLE employees (
--     employee_id INTEGER PRIMARY KEY,
--     employee_name VARCHAR(100) NOT NULL,
--     manager_id INTEGER REFERENCES employees(employee_id),
--     department VARCHAR(50),
--     position VARCHAR(50),
--     salary DECIMAL(10),
--     hire_date DATE,
--     level INTEGER
-- );

-- -- 조직도 데이터 삽입 (4단계 계층)
-- INSERT INTO employees VALUES
-- -- CEO (1단계)
-- (1, 'CEO 김대표', NULL, '경영진', 'CEO', 150000000, '2020-01-01', 1),
-- -- 이사급 (2단계)
-- (2, '이사 박영업', 1, '영업본부', '이사', 120000000, '2020-03-01', 2),
-- (3, '이사 최개발', 1, '개발본부', '이사', 120000000, '2020-03-01', 2),
-- (4, '이사 정마케팅', 1, '마케팅본부', '이사', 110000000, '2020-04-01', 2),
-- (5, '이사 한인사', 1, '인사본부', '이사', 110000000, '2020-04-01', 2),
-- -- 부장급 (3단계)
-- (6, '부장 김영업1', 2, '영업1팀', '부장', 90000000, '2020-06-01', 3),
-- (7, '부장 이영업2', 2, '영업2팀', '부장', 90000000, '2020-06-01', 3),
-- (8, '부장 박프론트', 3, '프론트엔드팀', '부장', 95000000, '2020-07-01', 3),
-- (9, '부장 최백엔드', 3, '백엔드팀', '부장', 95000000, '2020-07-01', 3),
-- (10, '부장 정마케팅', 4, '마케팅팀', '부장', 85000000, '2020-08-01', 3),
-- (11, '부장 한인사', 5, '인사팀', '부장', 85000000, '2020-08-01', 3),
-- -- 팀장급 (4단계)
-- (12, '팀장 김영업A', 6, '영업1팀', '팀장', 70000000, '2021-01-01', 4),
-- (13, '팀장 이영업B', 6, '영업1팀', '팀장', 70000000, '2021-01-01', 4),
-- (14, '팀장 박영업C', 7, '영업2팀', '팀장', 70000000, '2021-01-01', 4),
-- (15, '팀장 최영업D', 7, '영업2팀', '팀장', 70000000, '2021-01-01', 4),
-- (16, '팀장 정프론트', 8, '프론트엔드팀', '팀장', 75000000, '2021-02-01', 4),
-- (17, '팀장 한백엔드', 9, '백엔드팀', '팀장', 75000000, '2021-02-01', 4),
-- (18, '팀장 김마케팅', 10, '마케팅팀', '팀장', 65000000, '2021-03-01', 4),
-- (19, '팀장 이인사', 11, '인사팀', '팀장', 65000000, '2021-03-01', 4),
-- -- 사원급 (5단계)
-- (20, '사원 박영업1', 12, '영업1팀', '사원', 45000000, '2021-06-01', 5),
-- (21, '사원 최영업2', 12, '영업1팀', '사원', 45000000, '2021-06-01', 5),
-- (22, '사원 김영업3', 13, '영업1팀', '사원', 45000000, '2021-06-01', 5),
-- (23, '사원 이영업4', 14, '영업2팀', '사원', 45000000, '2021-07-01', 5),
-- (24, '사원 정영업5', 15, '영업2팀', '사원', 45000000, '2021-07-01', 5),
-- (25, '사원 한프론트1', 16, '프론트엔드팀', '사원', 50000000, '2021-08-01', 5),
-- (26, '사원 박프론트2', 16, '프론트엔드팀', '사원', 50000000, '2021-08-01', 5),
-- (27, '사원 최백엔드1', 17, '백엔드팀', '사원', 50000000, '2021-09-01', 5),
-- (28, '사원 김백엔드2', 17, '백엔드팀', '사원', 50000000, '2021-09-01', 5),
-- (29, '사원 이마케팅', 18, '마케팅팀', '사원', 40000000, '2021-10-01', 5),
-- (30, '사원 정인사', 19, '인사팀', '사원', 40000000, '2021-10-01', 5);

-- SELECT * FROM employees;


-- Recursive - 재귀

WITH RECURSIVE numbers AS (
	-- 초기값
	SELECT 1 as num
	--
	UNION ALL
	-- 재귀 부분
	SELECT num + 1
	FROM numbers
	WHERE num < 10
)
SELECT * FROM numbers;


WITH RECURSIVE calender AS (
	-- 1/1 은 제공
	SELECT '2024-01-01'::DATE as 날짜
	UNION ALL
	SELECT (날짜 + INTERVAL'1 day')::DATE
	FROM calender
	WHERE 날짜 < '2024-01-31'::DATE
)
SELECT
	날짜
FROM calender;

-- 대표부터 전체 조직도 확인
WITH RECURSIVE org_chart AS (
	SELECT
		employee_id,
		employee_name,
		manager_id,
		department,
		1 AS 레벨,
		employee_name::text AS 조직구조
	FROM employees
	WHERE manager_id is NULL  -- 대표 찾기
	UNION ALL
	SELECT
		e.employee_id,
		e.employee_name,
		e.manager_id,
		e.department,
		oc.레벨 + 1,  -- 2
		(oc.조직구조 || '>>' || e.employee_name)::text
	FROM employees e
	INNER JOIN org_chart oc ON e.manager_id=oc.employee_id  -- 박영업 내 상사인 사람들
)
SELECT 
  	*
FROM org_chart
ORDER BY 레벨;

-- 특정 인물을 첫줄에 배치 -> 해당 인물을 기준으로 부하 직원 확인하기
WITH RECURSIVE org_chart AS (
	SELECT
		employee_id,
		employee_name,
		manager_id,
		department,
		level,
		employee_name::text AS 조직구조
	FROM employees
	WHERE employee_name = '부장 김영업1'
	UNION ALL
	SELECT
		e.employee_id,
		e.employee_name,
		e.manager_id,
		e.department,
		e.level,
		(oc.조직구조 || '>>' || e.employee_name)::text
	FROM employees e
	INNER JOIN org_chart oc ON e.manager_id=oc.employee_id
)
SELECT 
  	*
FROM org_chart
ORDER BY level;
