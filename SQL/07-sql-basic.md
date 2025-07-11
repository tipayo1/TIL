# 🎯 오늘 학습한 핵심 내용 TIL

# 🔍 MySQL EXPLAIN 기본 사용법 \& 인덱스 성능 분석

## 📖 MySQL EXPLAIN 문법

```sql
USE lecture;

-- 1. 기본 EXPLAIN
EXPLAIN
SELECT * FROM sales WHERE total_amount > 500000;

-- 2. EXPLAIN EXTENDED (MySQL 5.1+)
EXPLAIN EXTENDED
SELECT * FROM sales WHERE total_amount > 500000;
SHOW WARNINGS;  -- 추가 정보 확인

-- 3. EXPLAIN FORMAT=JSON (MySQL 5.6+)
EXPLAIN FORMAT=JSON
SELECT * FROM sales WHERE total_amount > 500000;

-- 4. 실제 실행 통계 (MySQL 8.0+)
EXPLAIN ANALYZE
SELECT * FROM sales WHERE total_amount > 500000;
```


## 🗂️ MySQL EXPLAIN 결과 구조

```sql
EXPLAIN
SELECT c.customer_name, s.product_name, s.total_amount
FROM customers c
INNER JOIN sales s ON c.customer_id = s.customer_id
WHERE c.customer_type = 'VIP';
```

| id | select_type | table | type | possible_keys | key | key_len | ref | rows | Extra |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| 1 | SIMPLE | c | ALL | PRIMARY | NULL | NULL | NULL | 50 | Using where |
| 1 | SIMPLE | s | ref | customer_id | cust_id | 12 | c.id | 2 | NULL |

## 🆚 MySQL vs PostgreSQL EXPLAIN 비교

### 출력 형태 차이

| 측면 | MySQL (테이블 형태) | PostgreSQL (트리 형태) |
| :-- | :-- | :-- |
| 출력 형태 | 테이블 | 트리 |
| 정보 밀도 | 간결함 | 상세함 |
| 가독성 | 초보자 친화적 | 전문가 친화적 |

### 정보 표현 방식 차이

#### MySQL EXPLAIN 주요 컬럼

- **id**: SELECT 식별자 (중첩 쿼리에서 순서)
- **select_type**: 쿼리 유형 (SIMPLE, PRIMARY, SUBQUERY, DERIVED 등)
- **table**: 참조되는 테이블명
- **type**: 조인/조회 타입
    - system, const, eq_ref, ref, range, index, ALL (성능: const > eq_ref > ref > range > index > ALL)
- **possible_keys**: 사용할 수 있는 인덱스
- **key**: 실제 사용 인덱스
- **key_len**: 인덱스 길이
- **ref**: 조인 시 비교 컬럼
- **rows**: 검사 예상 행 수
- **Extra**: 추가 정보 (Using where, Using index, Using temporary, Using filesort 등)


#### PostgreSQL 방식

- 트리 구조로 출력
- 비용 정보: `cost=0.42..8.45`
- 예상 반환 행 수: `rows=1`
- 행당 평균 바이트: `width=89`
- 실제 실행 시간: `actual time=0.123..0.125` (ANALYZE 시)
- 노드 실행 횟수: `loops=1`


## 🔧 MySQL EXPLAIN 실전 분석

### 1. 인덱스 사용 확인

```sql
EXPLAIN
SELECT * FROM sales WHERE total_amount > 500000;
```

- **나쁜 결과**: type: ALL (전체 테이블 스캔), Extra: Using where
- **좋은 결과**: type: range (범위 스캔), key: idx_total_amount


### 2. 조인 성능 확인

```sql
EXPLAIN
SELECT c.customer_name, COUNT(s.id)
FROM customers c
LEFT JOIN sales s ON c.customer_id = s.customer_id
GROUP BY c.customer_name;
```

- type: ALL → 인덱스 필요
- Extra: Using temporary → 메모리 부족
- Extra: Using filesort → 정렬 최적화 필요


## 🏗️ MySQL 성능 최적화 패턴

### 1. 인덱스 없는 상태

```sql
EXPLAIN SELECT * FROM sales WHERE customer_id = 'C001';
-- type: ALL, rows: 120 (전체 스캔)
```


### 2. 인덱스 생성 후

```sql
ALTER TABLE sales ADD INDEX idx_customer_id (customer_id);
EXPLAIN SELECT * FROM sales WHERE customer_id = 'C001';
-- type: ref, rows: 3 (인덱스 사용)
```


### 3. 복합 인덱스 활용

```sql
EXPLAIN SELECT * FROM sales
WHERE customer_id = 'C001' AND order_date >= '2024-01-01';

-- 단일 인덱스: type: ref, Extra: Using where
-- 복합 인덱스 생성 후: type: range, 더 효율적
ALTER TABLE sales ADD INDEX idx_customer_date (customer_id, order_date);
```


## 🎯 MySQL vs PostgreSQL EXPLAIN 요약

| 기능/측면 | MySQL | PostgreSQL |
| :-- | :-- | :-- |
| 출력 형태 | 테이블 | 트리 |
| 정보 밀도 | 간결 | 매우 상세 |
| 실제 실행 통계 | 8.0+ 일부 지원 | 기본 지원 |
| 메모리 정보 | 제한적 | BUFFERS 옵션 |
| 출력 형식 | TEXT, JSON | TEXT, JSON, YAML, XML |

- **MySQL**: type 컬럼 중심, Extra 정보로 추가 최적화 포인트 확인
- **PostgreSQL**: cost와 실제 시간 중심, 비용이 높은 노드 및 실제 시간 확인


## 📊 인덱싱 완전 정복

### 🎯 인덱스 성능 개선 결과 요약

#### 💥 극적 성능 향상 사례

1. **단일 고객 검색 (customer_id)**
    - 인덱스 없음: 100만 개 행 검사 → 느림
    - 인덱스 있음: 필요한 행만 검사 → 매우 빠름
2. **범위 검색 (amount)**
    - 인덱스 없음: 전체 테이블 스캔 → 느림
    - 인덱스 있음: 범위 내 데이터만 검사 → 빠름
3. **복합 조건 검색 (region + amount)**
    - 단일 인덱스: 한 조건만 인덱스 사용 → 보통
    - 복합 인덱스: 모든 조건 인덱스 사용 → 매우 빠름

## 🏗️ 인덱스 종류별 성능 특성

### 🌳 B-Tree 인덱스

- **특징**: 책의 목차처럼 계층적 구조
- **최적 용도**: 범위 검색, 정렬 작업, 부분 일치 검색

| 검색 유형 | 성능 | 지원 여부 |
| :-- | :-- | :-- |
| 정확 일치 (=) | ⭐⭐⭐⭐ | ✅ |
| 범위 검색 (>, <, BETWEEN) | ⭐⭐⭐⭐⭐ | ✅ |
| 정렬 (ORDER BY) | ⭐⭐⭐⭐⭐ | ✅ |
| 부분 일치 (LIKE 'ABC%') | ⭐⭐⭐⭐ | ✅ |

### \#️⃣ Hash 인덱스

- **특징**: 해시태그처럼 정확한 값으로 바로 접근
- **최적 용도**: 정확한 일치 검색만

| 검색 유형 | 성능 | 지원 여부 |
| :-- | :-- | :-- |
| 정확 일치 (=) | ⭐⭐⭐⭐⭐ | ✅ |
| 범위 검색 (>, <, BETWEEN) | ❌ | ❌ |
| 정렬 (ORDER BY) | ❌ | ❌ |
| 부분 일치 (LIKE 'ABC%') | ❌ | ❌ |

## ⚡ 성능 비교 실례

### 정확 일치 검색

```sql
SELECT * FROM users WHERE email = 'user@example.com';
```

| 인덱스 종류 | 검색 속도 | 메모리 사용량 |
| :-- | :-- | :-- |
| B-Tree 인덱스 | 매우 빠름 ⭐⭐⭐⭐ | 보통 |
| Hash 인덱스 | 초고속 ⭐⭐⭐⭐⭐ | 적음 |

### 범위 검색

```sql
SELECT * FROM orders WHERE order_date >= '2024-01-01' AND order_date <= '2024-01-31';
```

| 인덱스 종류 | 검색 속도 | 지원 여부 |
| :-- | :-- | :-- |
| B-Tree 인덱스 | 매우 빠름 ⭐⭐⭐⭐⭐ | ✅ |
| Hash 인덱스 | 불가능 ❌ | ❌ |

## 🎯 실무 적용 가이드

### B-Tree 인덱스를 선택해야 하는 경우

- 날짜 범위 검색
- 가격 범위 검색
- 정렬이 필요한 경우
- 부분 일치 검색
- 대부분의 일반적인 검색


### Hash 인덱스를 선택해야 하는 경우

- 로그인 시스템: 이메일 정확 일치
- 상품 코드 검색: 정확한 코드만
- 사용자 ID 검색: 정확한 ID만
- 메모리 효율이 중요한 경우
- ❌ 범위 검색이 필요한 경우는 부적합


## 📈 성능 향상 패턴 분석

### 가장 큰 성능 향상

- 고유값이 많은 컬럼 (고선택도): customer_id, email, 주문번호
- 자주 검색되는 컬럼: 상품명, 사용자명, 날짜
- 범위 검색이 많은 컬럼: 가격, 날짜, 수량


### 상대적으로 작은 성능 향상

- 고유값이 적은 컬럼 (저선택도): 성별, 지역, 상태값
- 자주 변경되는 컬럼: 재고수량, 최종수정일


## 🎯 실무 적용 가이드

### 반드시 인덱스를 만들어야 하는 경우

1. **로그인 시스템**
    - WHERE email = 'user@example.com' AND password = 'hashed_password'
    - Hash 인덱스 권장 (정확 일치만 필요)
    - B-Tree 인덱스도 가능 (복합 조건)
2. **고객 주문 조회**
    - WHERE customer_id = 'CUST-12345'
    - B-Tree 인덱스 권장 (정렬 필요 가능)
    - Hash 인덱스도 가능 (정확 일치만 필요)
3. **날짜 범위 검색**
    - WHERE order_date >= '2024-01-01' AND order_date <= '2024-01-31'
    - B-Tree 인덱스 필수 (Hash는 범위 검색 불가)

## 🤔 인덱스 종류 선택 기준

### B-Tree 인덱스 (90% 이상)

- 다양한 검색 패턴 예상
- 범위 검색 필요
- 정렬 필요
- 부분 일치 검색 필요
- **확실하지 않으면 B-Tree 선택**


### Hash 인덱스 (10% 미만)

- 정확한 일치 검색만
- 메모리 효율이 매우 중요
- 최대 성능이 필요한 특수한 경우
- 보안상 정확한 매칭만 허용


## 🚀 성능 개선 효과 요약

- **사용자 경험 개선**: 3초 → 1초 미만
- **시스템 자원 절약**: CPU 사용률 80% → 20%, 메모리 사용량 감소
- **확장성 확보**: 데이터 증가에도 성능 저하 최소화, 동시 사용자 처리량 증가


## 📊 성능 향상 수치 정리

| 검색 유형 | 인덱스 전 | B-Tree 후 | Hash 후 | 최적 선택 |
| :-- | :-- | :-- | :-- | :-- |
| 단일 정확 검색 | 매우 느림 | 매우 빠름 ⭐⭐⭐⭐⭐ | 초고속 ⭐⭐⭐⭐⭐ | Hash 우세 |
| 범위 검색 | 느림 | 매우 빠름 ⭐⭐⭐⭐⭐ | 불가능 ❌ | B-Tree 필수 |
| 복합 조건 검색 | 느림 | 매우 빠름 ⭐⭐⭐⭐⭐ | 제한적 ⭐⭐ | B-Tree 우세 |
| 정렬 포함 검색 | 매우 느림 | 매우 빠름 ⭐⭐⭐⭐⭐ | 불가능 ❌ | B-Tree 필수 |

## 💡 핵심 메시지

> **인덱스는 검색 성능을 혁신적으로 개선시키는 데이터베이스의 핵심 도구**

### 🏆 성공적인 인덱스 설계 4원칙

1. 실제 쿼리 패턴 분석이 가장 중요
2. 적절한 인덱스 종류 선택 (B-Tree vs Hash)
3. 적절한 컬럼 선택과 순서 배치
4. 지속적인 모니터링과 최적화

## 🤝 간단한 선택 가이드

- **확실하지 않으면 → B-Tree 선택**
- **정확한 일치 검색만 → Hash 고려**
- **범위 검색 필요 → B-Tree 필수**

<div style="text-align: center">⁂</div>

[^1]: https://hoestory.tistory.com/57

[^2]: https://yenbook.tistory.com/95

[^3]: https://zzang9ha.tistory.com/436

[^4]: https://dextto.tistory.com/229

[^5]: https://jeongchul.tistory.com/799

[^6]: https://haemanlee.tistory.com/26

[^7]: https://snowple.tistory.com/377

[^8]: https://velog.io/@bcj0114/RDB-인덱스-4-MySQL-EXPLAIN-사용법

[^9]: https://kukim.tistory.com/128



```md
# 🎯오늘 학습한 핵심 내용 TIL2

## 1. 복합 인덱스에서 컬럼 순서의 중요성
복합 인덱스의 컬럼 순서는 인덱스 성능에 큰 영향을 미침.

자주 사용되는 컬럼과 선택도(고유값 비율)가 높은 컬럼을 앞에 배치하는 것이 일반적.

WHERE 절에서 사용되는 컬럼 순서대로 인덱스를 구성하면 효율적.

## 2. 선택도(Selectivity)와 카디널리티(Cardinality)
선택도: 특정 컬럼의 고유값 수가 전체 행에서 차지하는 비율(%)
→ 선택도가 높을수록 데이터 검색 시 필터링 효과가 커져 인덱스 성능이 향상됨.

카디널리티: 컬럼의 고유값(Unique Value) 개수
→ 카디널리티가 높을수록 인덱스 스캔 범위가 줄어들어 성능이 좋아짐.

용어	의미	인덱스 설계 시 효과
선택도	고유값 비율(%)	높을수록 성능 향상
카디널리티	고유값 개수(Unique Value Count)	높을수록 성능 향상
## 3. WHERE/ORDER BY 절과 인덱스 컬럼 순서
WHERE 절:
인덱스 컬럼을 앞쪽부터 순서대로 사용할 때 인덱스 효율이 높아짐.

ORDER BY 절:
인덱스 컬럼 순서와 일치하게 정렬 조건을 줄 때 인덱스 효과를 볼 수 있음.

## 4. UPDATE 빈도와 인덱스 설계
인덱스 컬럼으로 자주 변경되는 컬럼을 선택하면 인덱스 업데이트 비용이 증가해 성능 저하 가능.

실제 사용 빈도와 성능 요구사항을 고려하여 인덱스를 설계해야 함.

## 5. 예시
sql
SELECT
    COUNT(DISTINCT region) AS 고유지역수,  -- 카디널리티
    COUNT(*) AS 전체행수,
    ROUND(COUNT(DISTINCT region) * 100 / COUNT(*), 2) AS 선택도
FROM large_orders;  -- 선택도 0.0007%
위 쿼리는 region 컬럼의 카디널리티와 선택도를 계산하는 예시.

선택도가 0.0007%로 매우 낮은 경우, 인덱스의 필터링 효과가 적을 수 있음.

## 6. 실무 설계 시 주의사항
복합 인덱스는 무분별하게 많이 생성하지 말고, 실제 쿼리 패턴과 성능 요구사항을 고려해 필요한 컬럼 위주로 구성.

데이터베이스 시스템의 특성과 인덱스 구조를 이해하고, 최적의 컬럼 순서를 결정할 것.

요약:
복합 인덱스 설계 시, 자주 사용되고 선택도/카디널리티가 높은 컬럼을 앞에 두는 것이 일반적으로 성능에 유리하다.
WHERE/ORDER BY 절에서의 사용 패턴과 UPDATE 빈도도 반드시 고려해야 한다.
```

```sql
-- pg-01-datatype.sql

SELECT version();

SHOW shared_buffers;
SHOW work_mem;
SHOW maintenance_work_mem;

CREATE TABLE datatype_demo(
	-- mysql에도 있음 이름이 다를 수는 있다
	id SERIAL PRIMARY KEY,
	name VARCHAR(100) NOT NULL,
	age INTEGER,
	salary NUMERIC(12, 2),
	is_active BOOLEAN DEFAULT TRUE,
	created_at TIMESTAMP DEFAULT NOW(),
	-- postgresql 특화 타입
	tags TEXT[], -- 배열
	metadata JSONB, -- JSON binary 타입
	ip_address INET, -- IP 주소 저장 전용
	location POINT, -- 기하학 점(x, y)
	salary_range INT4RANGE -- 범위
);

INSERT INTO datatype_demo (
    name, age, salary, tags, metadata, ip_address, location, salary_range
) VALUES
(
    '김철수',
    30,
    5000000.50,
    ARRAY['개발자', 'PostgreSQL', '백엔드'],        -- 배열
    '{"department": "IT", "skills": ["SQL", "Python"], "level": "senior"}'::JSONB,  -- JSONB
    '192.168.1.100'::INET,                         -- IP 주소
    POINT(37.5665, 126.9780),                      -- 서울 좌표
    '[3000000,7000000)'::INT4RANGE                 -- 연봉 범위
),
(
    '이영희',
    28,
    4500000.00,
    ARRAY['디자이너', 'UI/UX'],
    '{"department": "Design", "skills": ["Figma", "Photoshop"], "level": "middle"}'::JSONB,
    '10.0.0.1'::INET,
    POINT(35.1796, 129.0756),                      -- 부산 좌표
    '[4000000,6000000)'::INT4RANGE
);

SELECT * FROM datatype_demo;

-- 배열(tags)
SELECT
	name,
	tags,
	tags[1] AS first_tag,
	'PostgreSQL' = ANY(tags) AS pg_dev
FROM datatype_demo;
-- JSONB(metadata)
SELECT
	name,
	metadata,
	metadata->>'department' AS 부서, -- text
	metadata->'skills' AS 능력 --jsonb
FROM datatype_demo;

SELECT 
	name, 
	metadata->>'department' AS 부서
FROM datatype_demo
WHERE metadata @> '{"level":"senior"}';

-- 범위(salary_range)
SELECT
	name,
	salary,
	salary_range,
	salary::INT <@ salary_range AS 연봉범위,
	-- UPPER(salary_range), -- 상한선
	-- LOWER(salary_range) -- 하한선
	UPPER(salary_range) - LOWER(salary_range) AS 연봉폭
FROM datatype_demo;

-- 좌표값(location)
SELECT
	name,
	location,
	location[0] AS 위도,
	location[1] AS 경도,
	POINT(37.505027, 127.005011) <-> location AS 고터거리
FROM datatype_demo;
```

```sql
-- pg-02-large-dataset.sql

-- 숫자 생성
SELECT generate_series(1,10);

-- 날짜 생성
SELECT generate_series(
	'2024-01-01'::date,
	'2024-12-31'::date,
	'1 day'::interval
);

-- 시간 생성
SELECT generate_series(
	'2024-01-01 00:00:00'::timestamp,
	'2024-01-01 23:59:59'::timestamp,
	'1 hour'::interval
);


CREATE TABLE large_orders AS
SELECT
    generate_series(1, 1000000) AS order_id,
    -- 고객 ID (랜덤)
    'CUST-' || LPAD((floor(random() * 50000) + 1)::text, 6, '0') AS customer_id,
    -- 제품 ID (랜덤)
    'PROD-' || LPAD((floor(random() * 10000) + 1)::text, 5, '0') AS product_id,
    -- 주문 금액 (랜덤)
    (random() * 1000000 + 1000)::NUMERIC(12,2) AS amount,
    -- 주문 날짜 (2023-2024년 랜덤)
    (DATE '2023-01-01' + (floor(random() * 730))::int) AS order_date,
    -- 지역 (배열에서 랜덤 선택)
    (ARRAY['서울', '부산', '대구', '인천', '광주', '대전', '울산'])[
        CEIL(random() * 7)::int
    ] AS region,
    -- 카테고리 태그 (배열)
    CASE
        WHEN random() < 0.3 THEN ARRAY['전자제품', '인기상품']
        WHEN random() < 0.6 THEN ARRAY['의류', '패션']
        WHEN random() < 0.8 THEN ARRAY['생활용품', '필수품']
        ELSE ARRAY['식품', '신선식품']
    END AS category_tags,
    -- 주문 세부 정보 (JSONB)
    jsonb_build_object(
        'payment_method',
        (ARRAY['카드', '현금', '계좌이체', '포인트'])[CEIL(random() * 4)::int],
        'delivery_fee',
        CASE WHEN random() < 0.5 THEN 0 ELSE 3000 END,
        'is_express',
        random() < 0.3,
        'discount_rate',
        (random() * 20)::int
    ) AS order_details,
    -- 생성 시간
    NOW() AS created_at;

-- 생성된 데이터 확인
SELECT COUNT(*) FROM large_orders;

-- 데이터 샘플 확인
SELECT * FROM large_orders LIMIT 5;


-- 고객 데이터 생성
CREATE TABLE large_customers AS
SELECT 
    'CUST-' || LPAD(generate_series(1, 100000)::text, 6, '0') AS customer_id,
    -- 랜덤 이름 생성
    (ARRAY['김', '이', '박', '최', '정', '강', '조', '윤', '장', '임'])[CEIL(random() * 10)::int] ||
    (ARRAY['철수', '영희', '민수', '지은', '우진', '소영', '현우', '예은', '도윤', '서연'])[CEIL(random() * 10)::int] 
    AS customer_name,
    -- 나이 (20-80세)
    (20 + random() * 60)::int AS age,
    -- 고객 타입
    CASE 
        WHEN random() < 0.1 THEN 'VIP'
        WHEN random() < 0.3 THEN '골드'
        WHEN random() < 0.6 THEN '실버'
        ELSE '일반'
    END AS customer_type,
    -- 가입일
    (DATE '2020-01-01' + (random() * 1460)::int) AS join_date,
    -- 선호 카테고리 (배열로 간단하게)
    CASE 
        WHEN random() < 0.2 THEN ARRAY['전자제품']
        WHEN random() < 0.4 THEN ARRAY['의류']
        WHEN random() < 0.6 THEN ARRAY['생활용품']
        WHEN random() < 0.8 THEN ARRAY['식품']
        WHEN random() < 0.9 THEN ARRAY['전자제품', '의류']
        ELSE ARRAY['생활용품', '식품']
    END AS preferred_categories,
    -- 연락 방식
    (ARRAY['email', 'sms', 'push', 'none'])[CEIL(random() * 4)::int] AS communication_preference,
    -- 적립 포인트
    (random() * 10000)::int AS loyalty_points,
    -- 추가 정보 (JSONB)
    jsonb_build_object(
        'last_login', (now() - (random() * interval '365 days'))::date,
        'total_orders', (random() * 100)::int,
        'is_premium', random() < 0.3
    ) AS additional_info;

-- 생성 확인
SELECT COUNT(*) FROM large_customers;

-- 데이터 샘플 확인
SELECT 
    customer_id,
    customer_name,
    customer_type,
    preferred_categories,
    communication_preference,
    loyalty_points,
    additional_info
FROM large_customers 
LIMIT 10;

-- 배열 검색 테스트
SELECT COUNT(*) 
FROM large_customers 
WHERE '전자제품' = ANY(preferred_categories);

-- JSONB 검색 테스트
SELECT COUNT(*) 
FROM large_customers 
WHERE additional_info @> '{"is_premium": true}';-- pg-02-large-dataset.sql

-- 숫자 생성
SELECT generate_series(1,10);

-- 날짜 생성
SELECT generate_series(
	'2024-01-01'::date,
	'2024-12-31'::date,
	'1 day'::interval
);

-- 시간 생성
SELECT generate_series(
	'2024-01-01 00:00:00'::timestamp,
	'2024-01-01 23:59:59'::timestamp,
	'1 hour'::interval
);


CREATE TABLE large_orders AS
SELECT
    generate_series(1, 1000000) AS order_id,
    -- 고객 ID (랜덤)
    'CUST-' || LPAD((floor(random() * 50000) + 1)::text, 6, '0') AS customer_id,
    -- 제품 ID (랜덤)
    'PROD-' || LPAD((floor(random() * 10000) + 1)::text, 5, '0') AS product_id,
    -- 주문 금액 (랜덤)
    (random() * 1000000 + 1000)::NUMERIC(12,2) AS amount,
    -- 주문 날짜 (2023-2024년 랜덤)
    (DATE '2023-01-01' + (floor(random() * 730))::int) AS order_date,
    -- 지역 (배열에서 랜덤 선택)
    (ARRAY['서울', '부산', '대구', '인천', '광주', '대전', '울산'])[
        CEIL(random() * 7)::int
    ] AS region,
    -- 카테고리 태그 (배열)
    CASE
        WHEN random() < 0.3 THEN ARRAY['전자제품', '인기상품']
        WHEN random() < 0.6 THEN ARRAY['의류', '패션']
        WHEN random() < 0.8 THEN ARRAY['생활용품', '필수품']
        ELSE ARRAY['식품', '신선식품']
    END AS category_tags,
    -- 주문 세부 정보 (JSONB)
    jsonb_build_object(
        'payment_method',
        (ARRAY['카드', '현금', '계좌이체', '포인트'])[CEIL(random() * 4)::int],
        'delivery_fee',
        CASE WHEN random() < 0.5 THEN 0 ELSE 3000 END,
        'is_express',
        random() < 0.3,
        'discount_rate',
        (random() * 20)::int
    ) AS order_details,
    -- 생성 시간
    NOW() AS created_at;

-- 생성된 데이터 확인
SELECT COUNT(*) FROM large_orders;

-- 데이터 샘플 확인
SELECT * FROM large_orders LIMIT 5;


-- 고객 데이터 생성
CREATE TABLE large_customers AS
SELECT 
    'CUST-' || LPAD(generate_series(1, 100000)::text, 6, '0') AS customer_id,
    -- 랜덤 이름 생성
    (ARRAY['김', '이', '박', '최', '정', '강', '조', '윤', '장', '임'])[CEIL(random() * 10)::int] ||
    (ARRAY['철수', '영희', '민수', '지은', '우진', '소영', '현우', '예은', '도윤', '서연'])[CEIL(random() * 10)::int] 
    AS customer_name,
    -- 나이 (20-80세)
    (20 + random() * 60)::int AS age,
    -- 고객 타입
    CASE 
        WHEN random() < 0.1 THEN 'VIP'
        WHEN random() < 0.3 THEN '골드'
        WHEN random() < 0.6 THEN '실버'
        ELSE '일반'
    END AS customer_type,
    -- 가입일
    (DATE '2020-01-01' + (random() * 1460)::int) AS join_date,
    -- 선호 카테고리 (배열로 간단하게)
    CASE 
        WHEN random() < 0.2 THEN ARRAY['전자제품']
        WHEN random() < 0.4 THEN ARRAY['의류']
        WHEN random() < 0.6 THEN ARRAY['생활용품']
        WHEN random() < 0.8 THEN ARRAY['식품']
        WHEN random() < 0.9 THEN ARRAY['전자제품', '의류']
        ELSE ARRAY['생활용품', '식품']
    END AS preferred_categories,
    -- 연락 방식
    (ARRAY['email', 'sms', 'push', 'none'])[CEIL(random() * 4)::int] AS communication_preference,
    -- 적립 포인트
    (random() * 10000)::int AS loyalty_points,
    -- 추가 정보 (JSONB)
    jsonb_build_object(
        'last_login', (now() - (random() * interval '365 days'))::date,
        'total_orders', (random() * 100)::int,
        'is_premium', random() < 0.3
    ) AS additional_info;

-- 생성 확인
SELECT COUNT(*) FROM large_customers;

-- 데이터 샘플 확인
SELECT 
    customer_id,
    customer_name,
    customer_type,
    preferred_categories,
    communication_preference,
    loyalty_points,
    additional_info
FROM large_customers 
LIMIT 10;

-- 배열 검색 테스트
SELECT COUNT(*) 
FROM large_customers 
WHERE '전자제품' = ANY(preferred_categories);

-- JSONB 검색 테스트
SELECT COUNT(*) 
FROM large_customers 
WHERE additional_info @> '{"is_premium": true}';
```


```sql
-- pg-03-explain-analyze.sql

-- 실행 계획을 보자
EXPLAIN
SELECT * FROM large_customers WHERE customer_type = 'VIP';

-- Seq Scan on large_customers  (cost=0.00 .. 3746.00 rows=10013 width=159byte)
-- cost = 점수(낮을수록 좋음) / rows * width = 총 메모리 사용량
-- Filter: (customer_type = 'VIP'::text)

-- 실행 + 통계
EXPLAIN ANALYZE
SELECT * FROM large_customers WHERE customer_type = 'VIP';

-- Seq Scan on large_customers  (cost=0.00..3746.00 rows=10013 width=159) 
-- 인덱스 없고
-- 테이블 대부분의 행을 읽어야 하고
-- 순차 스캔이 빠를 때

-- Explain 옵션들

-- 버퍼 사용량 포함
EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM large_customers WHERE loyalty_points > 8000;

-- 상세 정보 포함
EXPLAIN (ANALYZE, VERBOSE, BUFFERS)
SELECT * FROM large_customers WHERE loyalty_points > 8000;

-- JSON 형태
EXPLAIN (ANALYZE, VERBOSE, BUFFERS, FORMAT JSON)
SELECT * FROM large_customers WHERE loyalty_points > 8000;


-- 진단 (Score is too high)
EXPLAIN ANALYZE
SELECT
	c.customer_name,
	COUNT(o.order_id)
FROM large_customers c
LEFT JOIN large_orders o ON c.customer_name = o.customer_id  -- 잘못된 JOIN 조건
GROUP BY c.customer_name;

-- 3. 메모리 부족
EXPLAIN (ANALYZE, BUFFERS)
SELECT customer_id, array_agg(order_id)
FROM large_orders
GROUP BY customer_id;
```


```sql
-- pg-04-index.sql

-- 인덱스 조회
SELECT
	tablename,
	indexname,
	indexdef
FROM pg_indexes
WHERE tablename IN ('large_orders', 'large_customers');

ANALYZE large_orders;
ANALYZE large_customers;

-- 실제 운영에서는 X (캐시 날리기)
SELECT pg_stat_reset();

EXPLAIN ANALYZE
SELECT * FROM large_orders
WHERE customer_id='CUST-25000.';  -- 36000 / 163ms

EXPLAIN ANALYZE
SELECT * FROM large_orders
WHERE amount BETWEEN 800000 AND 1000000;  -- 46296 / 192.534ms

EXPLAIN ANALYZE
SELECT * FROM large_orders
WHERE   -- 14310 / 132.375ms
	region='서울' AND amount > 500000 AND order_date >= '2024-07-08';

EXPLAIN ANALYZE
SELECT * FROM large_orders
WHERE region = '서울'
ORDER BY amount DESC  -- 39823 / 157.941ms
LIMIT 100;  


CREATE INDEX idx_orders_customer_id ON large_orders(customer_id);
CREATE INDEX idx_orders_amount ON large_orders(amount);
CREATE INDEX idx_orders_region ON large_orders(region);


EXPLAIN ANALYZE
SELECT * FROM large_orders
WHERE customer_id='CUST-25000.';  -- 4.54 / 0.134 ms

EXPLAIN ANALYZE
SELECT amount FROM large_orders
WHERE amount BETWEEN 900000 AND 930000;  -- 1130 / 170.352ms

EXPLAIN ANALYZE
SELECT COUNT(*) FROM large_orders WHERE region='서울';  -- 100ms


-- 복합 인덱스
CREATE INDEX idx_orders_region_amount ON large_orders(region, amount);

EXPLAIN ANALYZE
SELECT * FROM large_orders
WHERE region = '서울' AND amount > 800000;  -- 247ms -> 129ms


CREATE INDEX idx_orders_id_order_date ON large_orders(customer_id, order_date);

EXPLAIN ANALYZE
SELECT * FROM large_orders 
WHERE customer_id = 'CUST-25000.'   -- 0.204ms -> 0.08ms
  AND order_date >= '2024-07-01'
ORDER BY order_date DESC;

-- 복합 인덱스 순서의 중요도

CREATE INDEX idx_orders_region_amount ON large_orders(region, amount);
CREATE INDEX idx_orders_amount_region ON large_orders(amount, region);

SELECT 
    indexname,
    pg_size_pretty(pg_relation_size(indexname::regclass)) AS index_size
FROM pg_indexes 
WHERE tablename = 'large_orders' 
  AND indexname LIKE '%region%amount%' OR indexname LIKE '%amount%region%'
ORDER BY indexname;

-- Index 순서 가이드라인

-- 고유값 비율
SELECT
	COUNT(DISTINCT region) AS 고유지역수,
	COUNT(*) AS 전체행수,
	ROUND(COUNT(DISTINCT region) * 100 / COUNT(*), 2) AS 선택도
FROM large_orders;  -- 0.0007%

SELECT
	COUNT(DISTINCT amount) AS 고유금액수,
	COUNT(*) AS 전체행수
FROM large_orders;  -- 선택도 99%

SELECT
	COUNT(DISTINCT customer_id) AS 고유고객수,
	COUNT(*) AS 전체행수
FROM large_orders;  -- 선택도 13.6%
```


```sql
-- pg-05-various-index.sql

-- Data Structureㄴ (Graph, Tree, List, Hash...)

-- B-Tree 인덱스 생성
CREATE INDEX <index_name> ON <table_name>(<col_name>)
-- 범위 검색 BTWEEN, >, <
-- 정렬 ORDER BY
-- 부분 일치 LIKE

-- Hash 인덱스
CREATE INDEX <index_name> ON <table_name> USING HASH(<col>)
-- 정확한 일치 검색 =
-- 범위 x, 정렬 x


-- 부분 인덱스
CREATE INDEX <index_name> ON <table_name>(<col_name>)
WHERE 조건 = 'blah'

-- 특정 조건의 데이터만 자주 검색
-- 공간/비용 모두 절약

-- 인덱스를 사용하지 않음

-- 함수 사용
SELECT * FROM users WHERE UPPER(name) = 'JOHN'

-- 타입 변환(숫자=>문자)
SELECT * FROM users WHERE age = '25' -- age는 숫자인데 문자를 넣음

-- 앞쪽 와일드카드
SELECT * FROM users WHERE LIKE = '%김' -- like -> 앞쪽 와일드카드

-- 부정 조건
SELECT * FROM users WHERE age != 25;

-- 해결 방법
-- 함수 기반 인덱싱
CREATE INDEX <name> ON users(UPPER(name))

-- 타입 잘 쓰기
SELECT * FROM users WHERE age != 25;

-- 전체 텍스트 검색 인덱스 고려

-- 부정조건 -> 범위조건 
SELECT * FROM users WHERE age < 25 OR age > 25;

-- 인덱스는 검색성능 + | 저장공간 - (저장공간늘어남) | 수정성능 -
-- 실제 쿼리 패턴을 분석 -> 인덱스 설계
-- 성능 측정 = 실제 데이터
```

```
# TIL+
```