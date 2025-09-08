<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" class="logo" width="120"/>

# 5-Day SQL Skill-Up Roadmap for a DB-Backed RAG Pipeline

> 목표: 5일 동안 **“LLM ↔ SQL ↔ RAG”** 전 과정을 이해하고, 현업 수준으로 쿼리·성능·보안·모니터링을 설계·운영할 수 있는 실력을 확보한다.


| Day | 핵심 테마 | 구체적 학습·실습 과제 | 완수 기준 (Checkpoint) |
| :-- | :-- | :-- | :-- |
| 1 | 관계형 스키마 \& 기본 질의 | 1. ER 다이어그램 → DDL 작성<br>2. `SELECT / WHERE / ORDER BY / LIMIT` 실습<br>3. SQLite 또는 Postgres에 샘플 **sales·customers** 스키마 구축 | -  모든 테이블·컬럼에 주석 작성<br>-  자연어 요구사항을 기본 SQL로 변환 |
| 2 | 집계·JOIN·인덱스 기초 | 1. `JOIN`, `GROUP BY`, `HAVING`, 집계 함수<br>2. **EXPLAIN** 으로 실행계획 읽기[^1][^2]<br>3. 단일·복합 인덱스 설계 원칙 학습[^3][^4][^5] | -  3 초 미만으로 “지역·월별 매출 TOP 3” 쿼리 실행<br>-  인덱스 전후 실행계획 비교 캡처 |
| 3 | 고급 질의 \& LangChain 통합 | 1. 서브쿼리, 윈도 함수, CTE<br>2. View·Materialized View 활용<br>3. LangChain `SQLDatabaseChain` 으로 Text-to-SQL 구축[^6][^7][^8][^9] | -  LLM이 생성한 쿼리 자동 실행 후 결과를 자연어로 반환<br>-  실패 쿼리 로그 수집 |
| 4 | 보안·가드레일·성능 최적화 | 1. Row-Level Security·권한 설계[^10][^11]<br>2. LangChain `QuerySQLCheckerTool` 적용해 쿼리 검증[^12][^13][^14]<br>3. 파티셔닝·캐시·LIMIT 가드<br>4. 인덱스 재구성·VACUUM/ANALYZE | -  민감 컬럼 뷰로 마스킹<br>-  잘못된 LLM 쿼리 100% 차단 |
| 5 | 미니 프로젝트: DB-기반 RAG | 1. 벡터 DB 없이 **DB-Retrieval QA** 체인 구성 (SQL → 답변)<br>2. 품질 평가: `golden question` 20개로 정확도 측정<br>3. 모니터링 대시보드(쿼리 latency·오류율·토큰 사용) 구축 | -  정확도 ≥ 90%, 평균 지연 ≤ 2 초<br>-  SLA 알림 트리거 설정 |

## 필수 개념 \& 실전 팁

1. **스키마 메타데이터 주입**
    - 테이블/컬럼 설명과 샘플 행을 LLM 프롬프트에 포함하면 Text-to-SQL 정확도가 크게 향상[^6][^7].
2. **EXPLAIN → 인덱스 최적화 루프**
    - 실행계획에서 Full Scan·Filesort 감지 후 인덱스·쿼리 재설계[^1][^2][^3].
3. **LLM 가드레일**
    - `sql_db_query_checker` 연결로 NOT IN NULL·잘못된 JOIN 등 자동 교정[^12].
    - DB 계정은 읽기 전용, DDL 차단.
4. **Row-Level Security (RLS)**
    - 멀티테넌트 서비스라면 사용자별 행 필터 정책을 작성해 데이터 유출 방지[^10][^11].
5. **성능·품질 모니터링 지표**
    - 쿼리 Latency, Row Count, 정확도, 토큰 사용량을 Prometheus·Grafana로 수집 → 주간 리포트.
6. **쿼리 템플릿 라이브러리**
    - “최근 X 개월 미구매 고객”, “Top K 매출 상품” 등 고성능 패턴을 뷰/스토어드 프로시저로 고정해 LLM이 호출하도록 설계.

## 학습 자료 셀프 체크리스트

- [ ] LangChain SQL 튜토리얼 소스코드 실행[^6][^7][^9]
- [ ] EXPLAIN 출력 해석과 인덱스 개선 실습[^1][^2]
- [ ] RLS 정책 예제 따라 하기 (Postgres 기준)[^10][^11]
- [ ] Query Checker로 잘못된 쿼리 자동 수정 확인[^12][^13][^14]

5일 동안 집중적으로 위 과정을 완주하면, **“LLM 자동 SQL 생성과 실행 → 검증·최적화·보안·모니터링”**까지 아우르는 RAG 파이프라인 DB 전문가의 핵심 역량을 확보할 수 있다.

<div style="text-align: center">⁂</div>

[^1]: https://docs.oracle.com/cd/B19306_01/server.102/b14211/ex_plan.htm

[^2]: https://dev.mysql.com/doc/refman/8.2/en/execution-plan-information.html

[^3]: https://ai2sql.io/sql-indexing-best-practices-speed-up-your-queries

[^4]: https://milvus.io/ai-quick-reference/how-do-indexes-improve-sql-query-performance

[^5]: https://www.cockroachlabs.com/blog/sql-performance-best-practices/

[^6]: https://velog.io/@mo_ongh/MySQL%EA%B3%BC-%EC%97%B0%EB%8F%99%ED%95%9C-SQLDatabaseChain%EC%82%AC%EC%9A%A9%EB%B2%95

[^7]: https://wikidocs.net/234019

[^8]: https://python.langchain.com/api_reference/experimental/sql/langchain_experimental.sql.base.SQLDatabaseChain.html

[^9]: https://velog.io/@soysoy1125/LLM-Day-22-Text-to-SQL-RAG-시스템-구현

[^10]: https://neon.com/postgresql/postgresql-administration/postgresql-row-level-security

[^11]: https://www.crunchydata.com/blog/row-level-security-for-tenants-in-postgres

[^12]: https://sj-langchain.readthedocs.io/en/latest/tools/langchain.tools.sql_database.tool.QuerySQLCheckerTool.html

[^13]: https://python.langchain.com/api_reference/community/tools/langchain_community.tools.spark_sql.tool.QueryCheckerTool.html

[^14]: https://python.langchain.com/api_reference/community/tools/langchain_community.tools.sql_database.tool.QuerySQLCheckerTool.html

[^15]: https://api.python.langchain.com/en/latest/sql/langchain_experimental.sql.base.SQLDatabaseChain.html

[^16]: https://docs.oracle.com/cd/E11882_01/server.112/e41573/ex_plan.htm

[^17]: https://rfriend.tistory.com/834

[^18]: https://coronasdk.tistory.com/1478

[^19]: https://www.cockroachlabs.com/docs/stable/row-level-security

[^20]: https://learn.microsoft.com/en-us/sql/relational-databases/performance/execution-plans?view=sql-server-ver17

