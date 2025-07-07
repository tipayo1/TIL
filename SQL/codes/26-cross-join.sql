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