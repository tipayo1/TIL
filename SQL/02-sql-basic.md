# 🎯 오늘 학습한 핵심 내용 TIL

# 📊 MySQL 기초 - SELECT, WHERE, 정렬, 데이터 타입, 문자열 함수 TIL

## 🎯 오늘 배운 내용
- SELECT 문의 완전한 구조와 실행 순서
- WHERE 절의 다양한 조건식과 연산자
- ORDER BY를 활용한 정렬과 LIMIT/OFFSET
- 데이터 타입 선택 기준과 특징
- 문자열 함수를 활용한 데이터 가공

## 📚 핵심 개념 요약

### SELECT 기본 구조
```sql
SELECT 컬럼명 
FROM 테이블명 
WHERE 조건 
ORDER BY 정렬기준 
LIMIT 개수 OFFSET 개수;
```

## 🔍 WHERE 조건식

### 비교 연산자

| 연산자 | 의미 | 예시 |
|--------|------|------|
| `=` | 같음 | `name = 'kim'` |
| `<>`, `!=` | 다름 | `id <> 1` |
| `>`, `>=` | 크거나 같음 | `id >= 2` |
| ` 20 AND id  65` |

### 특수 연산자

| 연산자 | 사용법 | 예시 |
|--------|--------|------|
| `BETWEEN` | 범위 검색 | `id BETWEEN 1 AND 3` |
| `IN` | 목록 검색 | `name IN ('kim', 'lee')` |
| `LIKE` | 패턴 매칭 | `email LIKE '%test.com'` |
| `IS NULL` | NULL 검사 | `email IS NULL` |
| `IS NOT NULL` | NOT NULL 검사 | `email IS NOT NULL` |

### LIKE 패턴 문자
- **`%`**: 0개 이상의 임의 문자
- **`_`**: 정확히 1개의 임의 문자

### 논리 연산자

```sql
-- AND: 모든 조건 만족
SELECT * FROM member WHERE name = 'kim' AND id >= 2;

-- OR: 하나 이상 조건 만족
SELECT * FROM member WHERE name = 'kim' OR name = 'lee';

-- NOT: 조건의 반대
SELECT * FROM member WHERE NOT name = 'kim';
```

## 📊 ORDER BY (정렬)

```sql
-- 기본 정렬 (오름차순)
SELECT * FROM member ORDER BY name;
SELECT * FROM member ORDER BY name ASC;

-- 내림차순 정렬
SELECT * FROM member ORDER BY created_at DESC;

-- 다중 컬럼 정렬 (우선순위: name → id)
SELECT * FROM member ORDER BY name ASC, id DESC;
```

## 📋 주요 데이터 타입

### 문자열 타입

| 타입 | 특징 | 사용 예시 |
|------|------|-----------|
| `CHAR(n)` | 고정 길이 | 주민번호, 우편번호 |
| `VARCHAR(n)` | 가변 길이 | 이름, 이메일 |
| `TEXT` | 긴 문자열 (~65KB) | 게시글 내용 |

> 💡 **참고 자료**: [당근 테크 블로그 - VARCHAR vs TEXT](https://medium.com/daangn/varchar-vs-text-230a718a22a1)

### 숫자 타입

| 타입 | 크기 | 사용 예시 |
|------|------|-----------|
| `INT` | 4바이트 | ID, 개수 |
| `FLOAT` | 4바이트 소수 | 점수, 비율 |
| `DECIMAL(m,d)` | 정확한 소수 | 금액, 정밀 계산 |

### 날짜 타입

| 타입 | 형식 | 사용 예시 |
|------|------|-----------|
| `DATE` | YYYY-MM-DD | 생년월일 |
| `DATETIME` | YYYY-MM-DD HH:MM:SS | 정확한 시점 |

## 🔤 문자열 함수

| 함수 | 기능 | 예시 | 결과 |
|------|------|------|------|
| `LENGTH(str)` | 문자열 길이 | `LENGTH('hello')` | `5` |
| `CONCAT(str1, str2, ...)` | 문자열 연결 | `CONCAT('A', 'B')` | `'AB'` |
| `UPPER(str)` | 대문자 변환 | `UPPER('hello')` | `'HELLO'` |
| `LOWER(str)` | 소문자 변환 | `LOWER('HELLO')` | `'hello'` |
| `SUBSTRING(str, pos, len)` | 부분 문자열 | `SUBSTRING('hello', 2, 3)` | `'ell'` |
| `REPLACE(str, old, new)` | 문자열 치환 | `REPLACE('hello', 'l', 'x')` | `'hexxo'` |
| `LEFT(str, len)` | 왼쪽부터 n글자 | `LEFT('hello', 3)` | `'hel'` |
| `RIGHT(str, len)` | 오른쪽부터 n글자 | `RIGHT('hello', 3)` | `'llo'` |
| `LOCATE(substr, str)` | 부분문자열 위치 | `LOCATE('ll', 'hello')` | `3` |
| `TRIM(str)` | 앞뒤 공백 제거 | `TRIM(' hello ')` | `'hello'` |

## 💡 실무 활용 예시

### 이메일에서 사용자명 추출
```sql
SELECT
    email,
    SUBSTRING(email, 1, LOCATE('@', email) - 1) AS username
FROM member
WHERE email IS NOT NULL;
```

### 회원 정보 표시 형식 만들기
```sql
SELECT CONCAT(name, '(', email, ')') AS member_info 
FROM member;
```

### 검색 조건 조합
```sql
-- 이름에 '수'가 포함되고 이메일이 gmail인 회원
SELECT * FROM member
WHERE name LIKE '%수%'
    AND email LIKE '%gmail%';
```

### 페이지네이션 구현
```sql
-- 2페이지 (한 페이지당 10개)
SELECT * FROM member 
ORDER BY created_at DESC 
LIMIT 10 OFFSET 10;
```

### NULL 안전 처리
```sql
-- IFNULL로 NULL 대체
SELECT name, IFNULL(email, 'No Email') AS email_display
FROM member;

-- CASE WHEN으로 조건부 처리
SELECT name,
    CASE 
        WHEN email IS NOT NULL 
        THEN SUBSTRING(email, 1, LOCATE('@', email) - 1)
        ELSE 'No Email'
    END AS username
FROM member;
```

## ⚠️ 주의사항

### NULL 처리
```sql
-- ❌ 잘못된 방법
WHERE email = NULL

-- ✅ 올바른 방법
WHERE email IS NULL
```

### 성능 고려사항
- **문자열 함수**: 대량 데이터에서는 성능 고려 필요
- **ORDER BY**: 성능에 영향을 미침, LIMIT과 OFFSET을 적절히 사용
- **LIKE 패턴**: 앞에 `%`가 오면 인덱스 사용 불가

### 데이터 타입 선택
- **VARCHAR vs TEXT**: 길이가 예측 가능하면 VARCHAR 사용
- **FLOAT vs DECIMAL**: 정확한 계산이 필요하면 DECIMAL 사용
- **CHAR vs VARCHAR**: 길이가 고정이면 CHAR, 가변이면 VARCHAR

## 🎯 핵심 포인트

> ✅ **WHERE 절이 데이터 필터링의 핵심**
> 
> ✅ **ORDER BY로 원하는 순서로 정렬**
> 
> ✅ **데이터 타입 선택이 성능과 저장공간에 영향**
> 
> ✅ **문자열 함수로 데이터 가공 및 변환**
> 
> ✅ **조건 조합으로 복잡한 검색 구현**
> 
> ✅ **NULL 처리는 IS NULL/IS NOT NULL 사용**
> 
> ✅ **LIMIT/OFFSET으로 페이지네이션 구현**

## 📝 내일 학습 계획
- [ ] 집계 함수 (COUNT, SUM, AVG, MAX, MIN)
- [ ] GROUP BY와 HAVING 절
- [ ] JOIN을 활용한 테이블 연결
- [ ] 서브쿼리 기초
- [ ] 인덱스와 성능 최적화

*학습 날짜: 2025.07.01*

# Query

## lecture
```sql
-- 07-where.sql

-- SELECT 컬럼 
-- FROM 테이블 
-- WHERE 조건  

-- ODER BY 정렬기준 
-- LIMIT 개수

USE lecture;
DROP TABLE students;
CREATE TABLE students (
	-- id INT PK AI
    id INT AUTO_INCREMENT PRIMARY KEY,
    -- name 20자
    name VARCHAR(20),
    -- age INT
    age INT
);

DESC students;

INSERT INTO students (name, age) VALUES
('유 태영', 50),
('이 재필', 30),
('김 창휘', 20),
('오 창희', 25),
('공 형규', 33),
('권 태형', 18),
('유 창준', 45),
('하 준서', 10),
('이 제웅', 88),
('박 용호', 67);

SELECT * FROM students;

SELECT * FROM students WHERE name='유 창준';
SELECT * FROM students WHERE age >= 20; -- 이상
SELECT * FROM students WHERE age > 20; -- 초과
SELECT * FROM students WHERE id <> 1; -- 해당 조건 여집합, 해당 조건이 아닌
SELECT * FROM students WHERE id != 1; -- 해당 조건이 아닌

SELECT * FROM students WHERE age BETWEEN 20 AND 40; -- 이상 이하

SELECT * FROM students WHERE id IN (1, 3, 5, 7);

-- 문자열 패턴 (% -> 있을수도, 없을수도 있다. _ -> 정확히 개수만큼 글자가 있다.)
-- 이 씨만 찾기
SELECT * FROM students WHERE name LIKE '이%';
-- '창' 글자가 들어가는 사람, 앞이든 뒤든 가운데든 '창' 글자가 오는
SELECT * FROM students WHERE name LIKE '%창%';
-- 이름이 정확히 3글자인 유씨
SELECT * FROM students WHERE name LIKE '유 __';
--
```

```sql
-- 08-orderby.sql
USE lecture;
-- 특정 컬럼을 기준으로 정렬함
-- ASC 오름차순 | DESC 내림차순 

SELECT * FROM students;

-- 이름 ㄱㄴㄷ 순으로 정렬
SELECT * FROM students ORDER BY name;
SELECT * FROM students ORDER BY name ASC; -- 위와 결과 동일
SELECT * FROM students ORDER BY name DESC; -- 

-- 테이블 구조 변경 -> 컬럼 추가 -> grade VARCHAR(1) -> 기본값으로 'B'
ALTER TABLE students ADD COLUMN grade VARCHAR(1) DEFAULT 'B';
SELECT * FROM students;
-- 데이터 변경. 9명 -> id 1~3 -> A | id 8~10 -> C
UPDATE students SET grade = 'A' WHERE id BETWEEN 1 AND 3;
UPDATE students SET grade = 'C' WHERE id BETWEEN 7 AND 10;
SELECT * FROM students;

-- 다중 컬럼 정렬 -> 앞에 말한게 우선 정렬
SELECT * FROM students ORDER BY
age ASC,
grade DESC;

SELECT * FROM students ORDER BY
grade DESC,
age ASC;

-- 나이가 40 미만인 학생들 중에서 학점순 - 나이 많은순 으로 상위 5명 뽑기 
SELECT * FROM students 
WHERE age < 40
ORDER BY grade, age DESC
LIMIT 5
;
 
```

```sql
-- 09-datatype.sql

USE lecture;
-- DROP TABLE dt_demo;
CREATE TABLE dt_demo (
	id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(20) NOT NULL,
    nickname VARCHAR(20),
    birth DATE,
	score FLOAT, -- FLOAT(4, 2)실수 총 4자리, 소수점은 2자리만
	salary DECIMAL(20, 3),
    description TEXT,
    is_active BOOL DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
)
;

DESC dt_demo;

-- INSERT INTO dt_demo (name, nickname, birth, score, salary, description)


INSERT INTO dt_demo (name, nickname, birth, score, salary, description)
VALUES
('김철수', 'kim', '1995-01-01', 88.75, 3500000.50, '우수한 학생입니다.'),
('이영희', 'lee', '1990-05-15', 92.30, 4200000.00, '성실하고 열심히 공부합니다.'),
('박민수', 'park', '1988-09-09', 75.80, 2800000.75, '기타 사항 없음'),
('유태영', 'yu', '2002-07-01', 71.23, 8400000, '학생이 아님')
;

SELECT * FROM dt_demo;

-- 80점 이상만 조회
SELECT * FROM dt_demo WHERE score > 80; 
-- DESCRIption 에 '학생'이라는 말이 없는 사람
SELECT * FROM dt_demo WHERE description NOT LIKE '%학생%';
-- 00년 이전 출생자만 조회
SELECT * FROM dt_demo WHERE birth < '2000-01-01';


```

```sql
-- 10-str-func.sql
USE lecture;
SELECT * FROM dt_demo;
-- 길이
SELECT length('hello sql');
SELECT name, length(name) FROM dt_demo; -- 한글 바이트 수 (이제는 안씀)
SELECT nickname, length(nickname) FROM dt_demo; -- 영어 바이트 수 (ㅇ)
SELECT name, char_length(name) FROM dt_demo; -- 한글 바이트 수를 한글 단위에 맞게 (ㅇ)
SELECT name, char_length(name) AS 이름길이 FROM dt_demo; -- AS: 가상칼럼 네이밍 
 
-- 연결
SELECT concat('hello', 'sql', '!!');
SELECT concat(name, '(', score, ')') AS info FROM dt_demo; 

-- 대소문자 변환
SELECT
	nickname,
    upper(nickname) AS UN,
    lower(nickname) AS LN
FROM dt_demo;

-- 부분 문자열
SELECT substring('hello sql!', 2, 4);
SELECT LEFT('hello sql!', 5);
SELECT RIGHT('hello sql!', 5);

SELECT
	description,
    CONCAT(
		SUBSTRING(description, 1, 5), '...'			
	) AS intro,
    CONCAT(
		LEFT(description, 3),
        '...',
        RIGHT(description, 3)
    ) AS summary
    
FROM dt_demo;

-- 문자열 치환
SELECT REPLACE('a@test.com', 'a', 'A');
SELECT 
	description,
    REPLACE(description, '학생', '**') AS secret
FROM dt_demo;

-- 동적 추출 (원하는 글자의 위치를 확인 후 그 이전/이후를 추출하기
SELECT LOCATE('@', 'username@gmail.com');  -- username@gmail.com 에서 @이 등장하는 순서(숫자)

SELECT
  description,
  SUBSTRING(description, 1, LOCATE('학생', description) - 1) AS '학생설명'
FROM dt_demo;

-- 공백 없애기
SELECT TRIM('    what??     ');
```

# practice

```sql
-- p04.sql

USE practice;

SELECT * FROM userinfo;

INSERT INTO userinfo (nickname, phone, email) VALUES
('김철수', '01112345378', 'kim@test'),
('이영희', NULL, 'lee@gmail'),
('박민수', '01612345637', NULL),
('최영수', '01745367894', 'choi@naver.com');

-- id 가 3 이상
SELECT * FROM userinfo WHERE id >= 3;
-- email 이 gmail.com, naver.com 이런 특정 도메인으로 끝나는 사용자들
SELECT * FROM userinfo WHERE email LIKE '%gmail.com' OR email LIKE '%naver.com';
-- 이름이 김철수, 박민수 2명 뽑기
SELECT * FROM userinfo WHERE nickname IN ('김철수', '박민수');
-- 이메일이 비어있는(NULL) 사람들
SELECT * FROM userinfo WHERE email IS NULL;
SELECT * FROM userinfo WHERE email IS NOT NULL;
-- 이름에 수 글자가 들어간 사람들
SELECT * FROM userinfo WHERE nickname LIKE '%수%';
-- 핸드폰 번호 010으로 시작하는 사람들
SELECT * FROM userinfo WHERE phone LIKE '010%';
-- 이름에 'e' 가 있고, 폰번호 010, gmail 쓰는 사람
SELECT * FROM userinfo WHERE nickname LIKE '%e%' AND phone LIKE '010%' AND email LIKE '%gmail.com';
-- 성이 김/이 둘 중 하나인데 gmail 씀
SELECT * FROM userinfo WHERE (nickname LIKE '김%' OR nickname LIKE '이%') AND email LIKE '%gmail.com';
```

```sql
-- p05.sql

USE practice;
SHOW TABLES;
SELECT * FROM userinfo;

ALTER TABLE userinfo ADD COLUMN age INT DEFAULT 20;
UPDATE userinfo SET age=30 WHERE id BETWEEN 1 AND 5;

-- 이름 오름차순 상위 3명
SELECT * 
FROM userinfo 
ORDER BY nickname ASC
LIMIT 3
;
-- email gmail 인 사람들 나이순으로 정렬 
SELECT * 
FROM userinfo 
WHERE email LIKE '%gmail.com'
ORDER BY age DESC
;
-- 나이 많은사람들 중에 핸드폰 번호 오름차순 3명의 이름, 폰번, 나이만 확인
SELECT nickname, phone, age 
FROM userinfo 
ORDER BY age DESC, phone ASC
LIMIT 3 

;

-- 이름 오름차순 인데 가장 이름이 빠른사람 1명은 제외하고 3명만 조회 
SELECT * 
FROM userinfo 
ORDER BY nickname ASC
LIMIT 3 
OFFSET 1
;
```

```sql
-- p06.sql

USE practice;

SELECT * FROM userinfo;

-- 별명 길이 확인
SELECT nickname, char_length(nickname) FROM userinfo;

-- 별명 과 email 을 '-' 로 합쳐서 info 별칭(Alias) - AS 로 확인해 보기
SELECT concat(nickname, '-', email) AS info FROM userinfo;

-- 별명 은 모두 대문자로, email은 모두 소문자로 확인
SELECT upper(nickname), lower(email) FROM userinfo;

-- email 에서 gmail.com 을 naver.com 으로 모두 new_email 별칭 추출
SELECT email, replace(email, 'gmail.com', 'naver.com') AS new_email FROM userinfo;

-- email 앞에 붙은 단어만 username 컬럼 으로 확인 
SELECT email, substring(email, 1, locate('@', email)-1) AS username FROM userinfo;

-- (추가 과제 -> email 이 NULL 인 경우 'No Mail' 이라고 표시
-- sove1.
SELECT email, ifnull(email, 'No Mail') FROM userinfo;

-- solve2.
SELECT
	email,
    CASE
		WHEN email is NOT NULL
        THEN SUBSTRING(email, 1, LOCATE('@', email) - 1)
        ELSE 'NO Mail :('
		END AS username
FROM userinfo;
```

