# SQL 기초

# 📊 MySQL 데이터베이스 기초 - 1일차 TIL

## 🎯 오늘 배운 내용
- 데이터베이스 기본 개념과 종류
- DDL vs DML 차이점과 활용
- 테이블 생성 및 관리
- 데이터 조작 기본 명령어
- 제약조건과 데이터 타입

## 📚 데이터베이스 핵심 개념

### 데이터베이스 종류

#### **RDBMS** (가장 널리 사용)
- MySQL
- PostgreSQL  
- Oracle
- SQLite
- MariaDB

#### **NoSQL**
- Document DB
- Key-Value DB
- Graph DB

### 스키마(Schema)
> **정의**: 데이터베이스의 구조와 제약조건을 정의한 설계도

**포함 요소**
- 테이블 구조
- 데이터 타입
- 제약조건
- 관계 정의

## ⚖️ DDL vs DML

| 구분 | DDL | DML |
|------|-----|-----|
| **목적** | 데이터베이스 구조 정의/변경 | 데이터 조작 |
| **대상** | 테이블, 데이터베이스, 스키마 | 데이터(행) |
| **주요 명령어** | `CREATE`, `ALTER`, `DROP` | `INSERT`, `SELECT`, `UPDATE`, `DELETE` |
| **실행 결과** | 구조 변경 | 데이터 변경 |

## 🗄️ 데이터베이스 관리 (DDL)

### 데이터베이스 기본 명령어

```sql
-- 데이터베이스 생성
CREATE DATABASE database_name;

-- 데이터베이스 선택
USE database_name;

-- 데이터베이스 목록 조회
SHOW DATABASES;

-- 데이터베이스 삭제 (안전하게)
DROP DATABASE IF EXISTS database_name;
```

## 📋 테이블 관리 (DDL)

### 테이블 생성

```sql
CREATE TABLE table_name (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(30) NOT NULL,
    email VARCHAR(50) UNIQUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### 테이블 구조 확인

```sql
-- 테이블 목록 조회
SHOW TABLES;

-- 테이블 구조 확인
DESC table_name;
```

### 테이블 구조 변경

```sql
-- 컬럼 추가
ALTER TABLE table_name ADD COLUMN column_name datatype;

-- 컬럼 이름 + 데이터 타입 수정
ALTER TABLE table_name CHANGE COLUMN old_name new_name datatype;

-- 컬럼 데이터 타입만 수정
ALTER TABLE table_name MODIFY COLUMN column_name datatype;

-- 컬럼 삭제
ALTER TABLE table_name DROP COLUMN column_name;
```

### 테이블 삭제

```sql
DROP TABLE IF EXISTS table_name;
```

## 📝 데이터 조작 (DML)

### INSERT - 데이터 입력

```sql
-- 단일 행 입력
INSERT INTO table_name (column1, column2) 
VALUES (value1, value2);

-- 다중 행 입력
INSERT INTO table_name (column1, column2) VALUES
    (value1, value2),
    (value3, value4),
    (value5, value6);
```

### SELECT - 데이터 조회

```sql
-- 전체 조회
SELECT * FROM table_name;

-- 특정 컬럼 조회
SELECT column1, column2 FROM table_name;

-- 조건부 조회
SELECT * FROM table_name WHERE condition;
```

### UPDATE - 데이터 수정

```sql
UPDATE table_name 
SET column1 = value1 
WHERE condition;
```

### DELETE - 데이터 삭제

```sql
DELETE FROM table_name 
WHERE condition;
```

## 🔐 주요 제약조건

### PRIMARY KEY
```sql
id INT AUTO_INCREMENT PRIMARY KEY
```
- **목적**: 각 행의 고유 식별자
- **특징**: 중복 불가, NULL 불가, 테이블당 1개

### NOT NULL
```sql
name VARCHAR(30) NOT NULL
```
- **목적**: 필수 입력 강제
- **특징**: 빈 값 입력 불가

### UNIQUE
```sql
email VARCHAR(50) UNIQUE
```
- **목적**: 중복 값 방지
- **특징**: 중복 불가, NULL 허용, 여러 개 가능

### DEFAULT
```sql
status VARCHAR(10) DEFAULT 'active',
created_at DATETIME DEFAULT CURRENT_TIMESTAMP
```
- **목적**: 기본값 자동 입력
- **특징**: 값 미입력 시 기본값 사용

### AUTO_INCREMENT
```sql
id INT AUTO_INCREMENT PRIMARY KEY
```
- **목적**: 숫자 자동 증가
- **특징**: 주로 PRIMARY KEY와 함께 사용

## 📊 주요 데이터 타입

| 타입 | 설명 | 예시 |
|------|------|------|
| `INT` | 정수 | `age INT` |
| `VARCHAR(n)` | 가변 문자열 | `name VARCHAR(50)` |
| `TEXT` | 긴 문자열 | `content TEXT` |
| `DATE` | 날짜 | `birth_date DATE` |
| `DATETIME` | 날짜+시간 | `created_at DATETIME` |

## ⚠️ 주의사항

### 안전한 쿼리 작성

```sql
-- ❌ 위험 (모든 데이터 영향)
UPDATE users SET status = 'inactive';
DELETE FROM users;

-- ✅ 안전 (조건 지정)
UPDATE users SET status = 'inactive' WHERE id = 1;
DELETE FROM users WHERE status = 'deleted';
```

### WHERE 절이 필수인 상황
- **UPDATE**: 특정 데이터만 수정
- **DELETE**: 특정 데이터만 삭제  
- **SELECT**: 조건에 맞는 데이터만 조회

### IF EXISTS 활용
```sql
-- 에러 방지
DROP TABLE IF EXISTS table_name;
DROP DATABASE IF EXISTS database_name;
```

## 🎯 핵심 포인트

> ✅ **DDL로 구조를 만들고, DML로 데이터를 다룬다**
> 
> ✅ **스키마는 데이터베이스의 설계도**
> 
> ✅ **제약조건은 데이터 무결성 보장**
> 
> ✅ **WHERE 절은 안전한 데이터 조작의 핵심**
> 
> ✅ **PRIMARY KEY + AUTO_INCREMENT는 기본 패턴**
> 
> ✅ **DEFAULT + CURRENT_TIMESTAMP로 자동 시간 입력**

## 📝 내일 학습 계획
- [ ] 조건부 조회 심화 (WHERE, LIKE, IN, BETWEEN)
- [ ] 정렬과 제한 (ORDER BY, LIMIT)
- [ ] 집계 함수 기초 (COUNT, SUM, AVG)
- [ ] 그룹화 (GROUP BY, HAVING)

*학습 날짜: 2025.07.01*

# Query

## lecture
```sql
-- 00-test.sql

-- ctrl + Enter

SELECT version();
```

```sql
-- 01-createdb.sql

-- db 생성
CREATE DATABASE sample_db;
-- db 확인
SHOW DATABASES;
-- db 삭제
DROP DATABASE sample_db;

-- lecture, practice 생성 후 확인
CREATE DATABASE lecture;
CREATE DATABASE practice;
SHOW DATABASES;
-- DB 사용
USE lecture;
```

```sql
-- 02-create-table.sql
USE lecture;

-- 테이블 생성
CREATE TABLE sample (
	name VARCHAR(30),
    age int
);

-- 테이블 삭제
DROP TABLE sample;
 
 -- 테이블 확인
SHOW TABLES;

CREATE TABLE members ( -- 테이블 명: members 생성
	id INT AUTO_INCREMENT PRIMARY KEY, -- 회원 고유번호 (정수, 자동증가)
	name VARCHAR(30) NOT NULL, -- 이름(필수 입력)
    email VARCHAR(100) UNIQUE, -- 이메일(중복 불가능)
    join_date DATE DEFAULT(CURRENT_DATE) -- 가입일(기본값-오늘)
    
);

SHOW TABLES;

-- members 테이블을 상세히 확인 (Describe)
DESC members;
```

```sql
-- 03-insert.sql

USE lecture;
DESC members;

-- 데이터 입력
INSERT INTO members (name) VALUES ('유태영');
INSERT INTO members (name, email) VALUES ('김재석', 'kim@a.com');

-- 여러줄, (col1, col2) 순서 잘 맞추기!
INSERT INTO members (email, name) VALUES 
('lee@a.com', '이재필'), 
('park@a.com', '박지수');

-- 데이터 전체 조회 (Read)
SELECT * FROM members;
-- 단일 데이터 조회 (*->모든 컬럼)
SELECT * FROM members WHERE id=1;
```

```sql
-- 04-update-delete.sql

SELECT * FROM members;
INSERT INTO members(name) VALUES ('익명');

UPDATE members SET name='홍길동', email='hong@a.com' WHERE id=7;
-- 원치 않는 케이스 (name이 같으면 동시 수정)
UPDATE members SET name='No name' WHERE name='유태영';

-- DELETE(데이터 삭제)
DELETE FROM members WHERE id=8;
-- 테이블 모든 데이터 삭제 (위험)
DELETE FROM members;
```

```sql
-- 05-select.sql
USE lecture;

-- 모든 컬럼, 모든 조건
SELECT * FROM members;

-- 모든 컬럼, id 3
SELECT * FROM members WHERE id=3;

-- 이름 | 이메일, 모든 조건
SELECT name, email FROM members;

-- 이름, 이름=홍길동
SELECT name FROM members WHERE name= '홍길동';

```

```sql
-- 06-alter.sql

USE lecture;

DESC members;

-- 테이블 스키마(컬럼 구조) 변경

-- 컬럼 추가
ALTER TABLE members ADD COLUMN age INT NOT NULL DEFAULT 20;
ALTER TABLE members ADD COLUMN address VARCHAR(100) DEFAULT '미입력';

-- 컬럼 이름 + 데이터 타입 수정
ALTER TABLE members CHANGE COLUMN address juso VARCHAR(100);
-- 컬럼 데이터 타입 수정
ALTER TABLE members MODIFY COLUMN juso VARCHAR(50);
-- 컬럼 삭제
ALTER TABLE members DROP COLUMN age;

SELECT * FROM members;
```

# practice

```sql
-- p01.sql

-- 1. practice db 사용
-- 2. userinfo 테이블 생성
	-- id PK, auto inc, int
    -- nickname: 글자 20자 까지, 필수 입력
    -- phone 글자 11 글자 까지, 중복 방지
    -- reg_date 날짜, 기본값(오늘 날짜)
    
-- 3. desc로 테이블 정보 확인
USE practice;
CREATE TABLE userinfo (
	id INT AUTO_INCREMENT PRIMARY KEY,
    nickname VARCHAR(20) NOT NULL,
    phone VARCHAR(11) UNIQUE,
    reg_date DATE DEFAULT(current_date)
    
);
SHOW TABLES;
DESC userinfo;
```

```sql
-- p02.sql

-- practice db 이동
USE practice;
-- userinfo 테이블에 진행 (p01 실습에서 진행했던 테이블)
DESC userinfo;
-- 데이터 5건 넣기 (별명, 핸드폰) -> 별명 bob 을 포함하세요 C
INSERT INTO userinfo(nickname, phone) VALUES 
('ant', 01011112222),
('bob', 01022223333),
('cat', 01033334444),
('dog', 01044445555),
('eli', 01055556666);

-- 전체 조회 (중간중간 계속 실행하면서 모니터링) R
SELECT * FROM userinfo;
-- id가 3 인 사람 조회 R
SELECT * FROM userinfo WHERE id=3;
-- 별명이 bob 인 사람 조회 R
SELECT * FROM userinfo WHERE nickname='bob';
-- 별명이 bob 인 사람의 핸드폰 번호를 01099998888 로 수정 (id로 수정) U
UPDATE userinfo SET phone=01099998888 WHERE id=2;
-- 별명이 bob 인 사람 삭제 (id로 수정) D
DELETE FROM userinfo WHERE id=2; 
```

```sql
-- p03.sql

-- practice db 사용
USE practice;
-- 스키마 확인 & 데이터 확인 (주기적으로)
DESC userinfo;
SELECT * FROM userinfo;
-- userinfo 에 email 컬럼 추가 40글자 제한, 기본값은 ex@gmail.com
ALTER TABLE userinfo ADD COLUMN email VARCHAR(40) DEFAULT 'ex@gmail.com';
-- nickname 길이제한 100자로 늘리기
ALTER TABLE userinfo MODIFY COLUMN nickname VARCHAR(100);
-- reg_date 컬럼 삭제
ALTER TABLE userinfo DROP COLUMN reg_date;
-- 실제 한명의 email 을 수정하기
UPDATE userinfo SET email='ant@gmail.com' WHERE id=1;
```

# 2주간 배울 SQL(관계형DB) 개관
```md
1주차 - 기본(MYSQL)
2주차 - 중급(PostgreSQL)
```
# 배운점
```md
- SQL은 데이터베이스, DB, DBMS

- DDL은 Column, DML은 Raw를 조작한다.

- Query: 데이터베이스에게 질문하는 것

- Strict: 약속

- *:모든 칼럼

- WHERE: 조건

- DB모델링**

- CRUD****: 모든 프로그램은 이것을 벗어날 수 없다
```
# 질문
```md
DB의 종류에 관한 설명 중 Document DB가 JSON을 쓰는걸 알게 되었는데 현재 MCP가 JSON확장자를 쓰고 있다 그렇다면 Document DB가 MCP가 중요해진 현재 AI환경에서도 활용도가 높아졌을까?
```

