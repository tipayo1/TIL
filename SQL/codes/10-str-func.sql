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