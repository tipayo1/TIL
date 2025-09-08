<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" class="logo" width="120"/>

# 쿼리 앞에 EXPLAIN을 붙이는 것을 활용하는 상황과 잘 사용하는 방법

쿼리 앞에 **EXPLAIN**을 붙여 실행하는 것은 데이터베이스가 해당 쿼리를 실제로 어떻게 처리할지, 즉 **실행 계획(Execution Plan)**을 미리 확인하는 방법입니다. 이를 활용하는 상황과 잘 사용하는 방법은 아래와 같습니다.

### EXPLAIN을 활용하는 상황

- **쿼리 성능이 느릴 때**
    - 쿼리가 예상보다 오래 걸리거나, 서버 부하가 높을 때 실행 계획을 확인해 병목 지점을 찾을 수 있습니다[^1][^4].
- **인덱스 사용 여부를 확인하고 싶을 때**
    - 내가 의도한 인덱스가 실제로 사용되고 있는지, 혹은 인덱스가 무시되고 전체 테이블 스캔이 발생하는지 확인할 수 있습니다[^3][^4][^5].
- **JOIN, 서브쿼리 등 복잡한 쿼리 구조의 최적화가 필요할 때**
    - 여러 테이블을 조인하거나, 서브쿼리가 포함된 쿼리에서 각 테이블이 어떤 방식으로 접근되는지 확인할 수 있습니다[^3][^4].
- **새로운 인덱스 생성 또는 쿼리 구조 변경 전후의 효과를 비교할 때**
    - 인덱스를 추가하거나 쿼리 구조를 바꾼 뒤, EXPLAIN으로 실행 계획이 어떻게 달라졌는지 비교해볼 수 있습니다[^1][^4][^5].


### EXPLAIN을 잘 사용하는 방법

1. **쿼리 앞에 EXPLAIN 붙이기**

```sql
EXPLAIN SELECT ... FROM ... WHERE ...;
```

    - 원하는 쿼리 앞에 EXPLAIN을 붙여 실행하면, 테이블 접근 방식, 인덱스 사용 여부, 예상 처리 행 수 등 다양한 정보를 볼 수 있습니다[^1][^3][^5].
2. **실행 계획의 주요 항목 해석**
    - **type**: 테이블 접근 방식(ALL=풀스캔, index, range, ref, eq_ref, const 등). `ALL`은 성능 저하 신호, `const`, `eq_ref`는 가장 빠름[^4][^5].
    - **key/possible_keys**: 실제 사용된 인덱스와 후보 인덱스.
    - **rows**: DB가 예측한 처리 행 수. 값이 크면 성능 저하 가능성.
    - **Extra**: Using index, Using where, Using temporary, Using filesort 등 추가 작업 여부. Using temporary/filesort는 성능 저하 신호[^4].
    - **select_type**: 쿼리 구조(SIMPLE, PRIMARY, SUBQUERY, DERIVED 등)[^4].
3. **문제점 파악 및 튜닝**
    - `type`이 ALL(풀스캔)이면, WHERE/ON 절에 인덱스를 추가하거나 쿼리 구조를 개선합니다.
    - `Extra`에 Using temporary, Using filesort가 자주 등장하면 GROUP BY, ORDER BY, DISTINCT 등을 재검토합니다.
    - 예상 처리 행(`rows`)이 과다하면, 조건을 더 세분화하거나 인덱스를 추가합니다[^4][^5].
4. **EXPLAIN ANALYZE 활용**
    - MySQL 8.0 이상에서는 `EXPLAIN ANALYZE`로 실제 실행 비용과 반복자별 상세 실행 정보를 확인할 수 있습니다[^1].

### 실무 예시

```sql
EXPLAIN SELECT e.name, d.dept_name
FROM employee e
LEFT JOIN department d ON e.dept_id = d.dept_id
WHERE d.location = '서울';
```

- 결과에서 type이 ALL, key가 NULL이면 인덱스 미사용 → 인덱스 추가 필요
- rows 값이 크면 WHERE 조건, 인덱스 점검

**정리**
EXPLAIN은 쿼리 성능 개선, 인덱스 활용 확인, 조인 및 서브쿼리 구조 분석, 쿼리 튜닝 효과 검증 등 다양한 상황에서 활용됩니다. 주요 항목(type, key, rows, Extra 등)을 해석해 문제점을 찾고, 인덱스 추가·쿼리 구조 개선 등으로 성능을 최적화하는 데 필수적인 도구입니다[^1][^3][^4][^5].

<div style="text-align: center">⁂</div>

[^1]: https://hoestory.tistory.com/57

[^2]: https://datarian.io/blog/postgresql-using-explain

[^3]: https://2day-is-seonday.tistory.com/entry/MySQL-Explain-실행계획-사용법-및-분석

[^4]: https://coor.tistory.com/50

[^5]: https://mutpp.tistory.com/entry/EXPLAIN-사용-방법

[^6]: https://kukim.tistory.com/128

[^7]: https://velog.io/@jeong_hun_hui/MySQL%EC%97%90%EC%84%9C-Explain%EC%9D%84-%EC%9D%B4%EC%9A%A9%ED%95%98%EC%97%AC-%EC%8B%A4%ED%96%89-%EA%B3%84%ED%9A%8D-%EB%B6%84%EC%84%9D%ED%95%98%EA%B8%B0

[^8]: https://thalals.tistory.com/349

[^9]: https://zzang9ha.tistory.com/436

