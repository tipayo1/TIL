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