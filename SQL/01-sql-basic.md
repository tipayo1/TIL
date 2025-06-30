# SQL 기초

## 테이블 생성

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