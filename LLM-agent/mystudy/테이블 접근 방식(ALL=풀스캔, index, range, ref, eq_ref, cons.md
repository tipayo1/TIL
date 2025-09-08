<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" class="logo" width="120"/>

# 테이블 접근 방식(ALL=풀스캔, index, range, ref, eq_ref, const 에 대한 설명과 차이

MySQL에서 **EXPLAIN** 실행 계획의 `type` 컬럼에 나타나는 테이블 접근 방식(ALL, index, range, ref, eq_ref, const 등)은 데이터베이스가 테이블에서 데이터를 어떻게 읽는지 보여주는 매우 중요한 지표입니다. 각 방식의 의미와 차이는 다음과 같습니다.


| 접근 방식 | 설명 | 특징 및 성능 |
| :-- | :-- | :-- |
| **ALL** | **풀스캔(Full Table Scan)**. 테이블의 모든 행을 처음부터 끝까지 순차적으로 읽음 | 인덱스를 사용하지 않음. 테이블이 클수록 매우 느림. 최적화 필요[^5][^4] |
| **index** | **인덱스 풀스캔(Full Index Scan)**. 인덱스 전체를 처음부터 끝까지 순차적으로 읽음 | 인덱스를 사용하지만, 조건이 없어 인덱스 전체를 읽음. ALL보다는 빠르지만 비효율적일 수 있음[^5][^4] |
| **range** | **범위 스캔(Range Scan)**. 인덱스를 사용해 WHERE 조건의 범위(>, <, BETWEEN 등)에 해당하는 값만 읽음 | 인덱스를 활용해 필요한 범위만 읽으므로 효율적. 조건에 따라 성능 차이 있음[^4][^5] |
| **ref** | **비고유 인덱스 탐색**. 인덱스에서 하나의 값에 대해 여러 행이 매칭될 수 있음 | 보통 외래키나 일반 인덱스 조건에서 사용. 효율적이나, 여러 행이 반환될 수 있음[^2][^4] |
| **eq_ref** | **고유 또는 기본키 인덱스 탐색**. 조인 시 한 행만 매칭됨 | 가장 효율적인 조인 방식. PK/UK(Primary/Unique Key)로 조인할 때 사용[^2][^4] |
| **const** | **상수 테이블 접근**. 쿼리 실행 시 단 한 행만 읽음 | WHERE 조건이 PK/UK 등으로 완전히 결정될 때 사용. 매우 빠름[^4] |

### 추가 설명

- **ALL**: 인덱스가 없거나, WHERE 조건이 인덱스를 활용하지 못할 때 발생. 테이블 전체를 읽으므로 성능 저하의 원인[^5][^4].
- **index**: 인덱스 전체를 순차적으로 읽지만, 실제 테이블 데이터는 읽지 않음. 인덱스만으로 필요한 컬럼을 모두 가져올 때 사용[^4].
- **range**: 예를 들어, `WHERE age > 30`처럼 범위 조건이 있을 때 인덱스를 활용해 일부만 읽음[^4].
- **ref**: 외래키나 비고유 인덱스(UNIQUE가 아닌 일반 인덱스)로 조인할 때, 여러 행이 매칭될 수 있음[^2][^4].
- **eq_ref**: 조인 키가 PK/UK 등으로 한 행만 매칭될 때. 예를 들어, `ON a.id = b.id`에서 둘 다 PK/UK일 때[^2][^4].
- **const**: WHERE 조건이 PK/UK로 한 행만 지정될 때. 예: `WHERE id = 1`[^4].

> **type의 순서는 const → eq_ref → ref → range → index → ALL 순으로 성능이 좋음**[^4].

**실무에서는 type이 ALL이나 index로 나온다면, WHERE/ON 조건에 인덱스를 추가하거나 쿼리 구조를 개선해 ref, eq_ref, const 등 상위 접근 방식을 유도하는 것이 성능 최적화의 핵심입니다.**

<div style="text-align: center">⁂</div>

[^1]: https://aurumguide.tistory.com/162

[^2]: https://hoestory.tistory.com/57

[^3]: https://inpa.tistory.com/entry/MYSQL-📚-JOIN-조인-그림으로-알기쉽게-정리

[^4]: https://0soo.tistory.com/235

[^5]: https://land-turtler.tistory.com/134

[^6]: https://velog.io/@ch200203/인덱스-접근방식의-이해

[^7]: https://extbrain.tistory.com/116

[^8]: https://dbaant.tistory.com/63

[^9]: https://hyunseo-fullstackdiary.tistory.com/417

