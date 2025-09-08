<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" class="logo" width="120"/>

# 위의 sql학습을 RAG 파이프라인 설계 운영 능력에 연결시키고 싶어 연습문제나 예시를 만들어줘

SQL 학습을 RAG 파이프라인 설계·운영 능력과 연결할 수 있는 **실전 연습문제 및 예시**를 아래와 같이 제안합니다.
이 문제들은 실제로 랭체인(LangChain) 기반 RAG 시스템을 구축할 때 필요한 SQL 활용 역량을 자연스럽게 키워주도록 설계되었습니다.

## 1. **기본 데이터 검색 및 필터링**

**문제 1**
고객 데이터베이스에서 최근 1년 이내에 가입한 고객 중, 이메일이 `gmail.com` 또는 `naver.com`으로 끝나는 고객의 이름과 이메일을 조회하세요.

```sql
SELECT customer_name, email
FROM customers
WHERE join_date >= DATE_SUB(CURDATE(), INTERVAL 1 YEAR)
  AND (email LIKE '%gmail.com' OR email LIKE '%naver.com');
```

*활용 포인트: WHERE, 날짜 함수, LIKE, OR*

## 2. **집계 및 그룹화**

**문제 2**
각 지역(region)별로 지난 달(예: 2025-06) 동안 발생한 주문 건수와 총 매출액을 구하세요.

```sql
SELECT region, COUNT(*) AS 주문건수, SUM(total_amount) AS 총매출액
FROM sales
WHERE DATE_FORMAT(order_date, '%Y-%m') = '2025-06'
GROUP BY region;
```

*활용 포인트: GROUP BY, 집계 함수, 날짜 포맷*

## 3. **JOIN을 활용한 정보 통합**

**문제 3**
VIP 고객의 이름, 등급, 최근 주문일, 최근 주문 금액을 한 번에 조회하세요.

```sql
SELECT c.customer_name, c.customer_type, MAX(s.order_date) AS 최근주문일, MAX(s.total_amount) AS 최근주문금액
FROM customers c
JOIN sales s ON c.customer_id = s.customer_id
WHERE c.customer_type = 'VIP'
GROUP BY c.customer_id, c.customer_name, c.customer_type;
```

*활용 포인트: JOIN, GROUP BY, 집계 함수, 조건 검색*

## 4. **서브쿼리와 조건부 집계**

**문제 4**
평균 주문 금액보다 높은 주문만 조회하고, 해당 주문의 고객 이름과 주문 금액을 출력하세요.

```sql
SELECT c.customer_name, s.total_amount
FROM sales s
JOIN customers c ON s.customer_id = c.customer_id
WHERE s.total_amount > (SELECT AVG(total_amount) FROM sales);
```

*활용 포인트: 서브쿼리, JOIN, 비교 연산*

## 5. **실제 RAG 파이프라인과의 연결 예시**

- **실제 RAG 시스템에서는**
    - 사용자의 자연어 질문(예: "지난달 서울 지역 매출이 가장 높은 고객을 알려줘")이 들어오면,
    - LLM이 위와 같은 SQL 쿼리를 자동 생성하거나, 미리 작성된 템플릿에 값을 채워 넣어 데이터를 검색합니다[^1][^2][^3][^4].
    - 검색된 결과(예: 고객명, 금액 등)는 LLM의 답변 생성에 직접 활용됩니다.


## 6. **연습문제(실전형)**

- **문제 5**
"2025년 상반기(1~6월) 동안 전자제품을 3건 이상 구매한 고객의 이름과 총 구매액을 출력하라."

```sql
SELECT c.customer_name, SUM(s.total_amount) AS 총구매액
FROM customers c
JOIN sales s ON c.customer_id = s.customer_id
WHERE s.category = '전자제품'
  AND s.order_date BETWEEN '2025-01-01' AND '2025-06-30'
GROUP BY c.customer_id, c.customer_name
HAVING COUNT(*) >= 3;
```

*활용 포인트: JOIN, GROUP BY, HAVING, 날짜 범위*

## 7. **추가 심화 예시**

- **문제 6**
"최근 3개월간 주문이 없는 고객을 찾아 이름과 연락처를 출력하라."

```sql
SELECT c.customer_name, c.contact
FROM customers c
LEFT JOIN sales s ON c.customer_id = s.customer_id
  AND s.order_date >= DATE_SUB(CURDATE(), INTERVAL 3 MONTH)
WHERE s.id IS NULL;
```

*활용 포인트: LEFT JOIN, NULL 조건, 날짜 함수*

### **이런 연습을 통해 얻게 되는 실제 역량**

- **실제 RAG 파이프라인에서 필요한 데이터 추출, 전처리, 통계, 조건부 분석 쿼리를 직접 설계**할 수 있습니다.
- **랭체인 RAG**와 연동 시, LLM이 자동 생성한 쿼리를 검증·최적화하거나, 복잡한 질문에 맞는 쿼리 템플릿을 직접 설계할 수 있습니다[^1][^2][^3][^4].
- **파이프라인 자동화**: 위와 같은 쿼리들이 랭체인 워크플로우에서 자동 실행되어, LLM이 신뢰할 수 있는 정형 데이터를 받아 자연어 답변을 생성하는 데 핵심적인 역할을 합니다.

**실전 Tip:**

- 실제 RAG 시스템을 설계할 때는, 위와 같은 SQL 쿼리들이 LLM과의 연결고리 역할을 하며, 데이터 정확도와 응답 품질을 좌우합니다.
- 연습문제를 직접 풀고, 쿼리 결과를 LLM 프롬프트에 넣어 답변을 생성해보면, RAG 파이프라인의 전체 흐름을 체험할 수 있습니다.

<div style="text-align: center">⁂</div>

[^1]: https://www.reddit.com/r/LocalLLaMA/comments/1bdqy5l/rag_pipeline_to_select_sql_table_for_nl2sql/

[^2]: https://huggingface.co/learn/cookbook/en/rag_with_sql_reranker

[^3]: https://www.chitika.com/rag-sql-database-integration/

[^4]: https://python.langchain.com/docs/tutorials/sql_qa/

[^5]: 02-sql-basic.md

[^6]: 03-sql-basic.md

[^7]: 04-sql-basic.md

[^8]: 01-sql-basic.md

[^9]: https://www.llamaindex.ai/blog/combining-text-to-sql-with-semantic-search-for-retrieval-augmented-generation-c60af30ec3b

[^10]: https://www.janeasystems.com/blog/sql-to-rag-pipeline

[^11]: https://www.youtube.com/watch?v=L1o1VPVfbb0

[^12]: https://blog.fabric.microsoft.com/en-GB/blog/ai-ready-apps-build-rag-data-pipeline-from-azure-blob-storage-to-sql-database-in-microsoft-fabric-within-minutes/

[^13]: https://www.youtube.com/watch?v=5LIfSpr3GDM

[^14]: https://blog.fabric.microsoft.com/en/blog/ai-ready-apps-build-rag-data-pipeline-from-azure-blob-storage-to-sql-database-in-microsoft-fabric-within-minutes?ft=All

