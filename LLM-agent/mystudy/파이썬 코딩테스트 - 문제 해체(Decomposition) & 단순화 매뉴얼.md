<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" class="logo" width="120"/>

# 파이썬 코딩테스트 - 문제 해체(Decomposition) \& 단순화 매뉴얼

## 0. 한눈에 보는 핵심

잘하는 사람은 **① 문제를 오해하지 않고, ② 큰 문제를 쪼개어, ③ 가장 단순한 해법부터 검증**한다.
아래 매뉴얼은 이 세 가지를 파이썬 문법·도구와 연결해 **재현 가능한 6-Step 루틴**으로 정리한 것이다.

## 1. STEP-BY-STEP 루틴

| 단계 | 질문/행동 | 산출물 | 설명 \& 근거 |
| :-- | :-- | :-- | :-- |
| 1. **Clarify (문제 해석)** | 입력·출력·제약·엣지케이스를 재진술 | `# 요구사항` 주석 | 문제를 그대로 코드 주석으로 옮기면 *오독 방지 + 사고 기록* 효과[^1][^2] |
| 2. **Examples (사례 작성)** | 정상·엣지·반례 3종 | 리스트 형태의 테스트 | 손으로 예시를 만들면 숨은 조건을 빠르게 찾는다[^3][^4] |
| 3. **Constraints \& Brute-Force** | 최대 N, 시간·메모리 한도 확인→가장 직관적 풀이 작성 | 복잡도 추정 | **먼저** 느린 해법을 말해 두면 이후 최적화가 쉬워진다[^5][^6] |
| 4. **Decompose \& Plan** | 하위 함수를 MECE 원칙으로 분할 | 의사코드(pseudocode) | 기능별로 `helper()`를 설계하면 실수·재사용 모두 줄어든다[^7][^8] |
| 5. **Code in Pythonic Way** | 표준 라이브러리·내장 함수를 우선 사용 | 동작하는 코드 | `enumerate`, `collections.Counter`, `heapq` 등은 구현 시간을 대폭 단축[^9][^10][^11] |
| 6. **Test → Optimize → Explain** | 단계 2의 사례 + 추가 랜덤 케이스 | 통과 여부 \& 복잡도 분석 | 통과 후 `O(N log N)`→`O(N)` 개선 가능 여부를 설명하면 가산점[^12][^13] |

## 2. 문제를 잘게 쪼개는 4가지 원칙

1. **입력 단위 → 출력 단위 매핑**
    - 예) *그룹 애너그램*: (문자열) → (해시값) → (딕셔너리 그룹)[^6]
2. **MECE 분할** (*Mutually Exclusive, Collectively Exhaustive*)
    - 중복 없이 빠짐없이 단계화하면 테스트 케이스가 자연히 떠오른다[^8].
3. **두 단계 모델**
    - ① *데이터 준비* ② *질문에 답하기* 로 나누면 대부분의 문제를 포괄할 수 있다.
    - 예) *K번째 수*: ① 정렬 ② 인덱스 추출.
4. **시간 ↔ 공간 교환법**
    - 해시(Map), 캐시, 프리컴퓨테이션으로 속도를 얻는 대신 메모리를 쓰는 패턴을 기억해두면 대부분의 최적화 질문에 대응 가능[^14][^2].

## 3. 파이썬 전용 “단순화 레버”

| 필요 작업 | 파이썬 한 줄 도구 | 의미 \& 사용처 |
| :-- | :-- | :-- |
| 빈도 세기 | `Counter(iter)` | 문자열/배열 빈도 비교 |
| 기본값 dict | `defaultdict(list)` | 그래프·그룹핑 |
| 정렬 기준 | `sorted(seq, key=...)` | 커스텀 우선순위 |
| 메모리 절약 | 제너레이터 `(x for x in seq)` | 큰 입력 스트림[^10] |
| 두 변수 스왑 | `a, b = b, a` | in-place 연산 간결화 |
| 인덱스+값 반복 | `for i, v in enumerate(seq)` | FizzBuzz·DP 테이블 등[^9] |
| 최소/최대 k개 | `heapq.nsmallest(k, seq)` | 최빈값·Top-K 문제 |

## 4. 실전 예시: “문자열 내 가장 긴 팰린드롬”

```python
def longest_palindrome(s: str) -> str:
    # 1) 요구사항 정리
    # 입력: 비어있지 않은 문자열 s(길이 ≤ 2 000)
    # 출력: 가장 긴 회문 문자열, 여럿이면 아무거나
    
    # 2) 예시
    # s = "babad" → "bab" or "aba"
    # s = "cbbd" → "bb"
    
    # 3) Brute-Force: 모든 부분문자열 검사 → O(N³)
    
    # 4) Decompose
    #  - expand(center): 양쪽으로 확장해 회문 길이 반환
    def expand(l, r):
        while l >= 0 and r < len(s) and s[l] == s[r]:
            l -= 1; r += 1
        return l + 1, r          # 최종 좌우 인덱스
    
    # 5) 코드
    best = (0, 1)
    for i in range(len(s)):
        for l, r in (expand(i, i), expand(i, i+1)):
            if r - l > best[^1] - best[^0]:
                best = (l, r)
    return s[best[^0]:best[^1]]
```

*복잡도* $O(N^{2})$ → 추가 캐싱 없이 최적(문자열 길이 2 000이면 4 백만 루프 미만).

위 구조는 **① 요구사항 주석화 → ② 예시 → ③ 단순 해법 표기 → ④ helper 분할 → ⑤ 깔끔한 파이썬 구문**의 전형적 흐름이다[^2][^4].

## 5. 훈련 전략

### 5-Day Drill

Day 1 : **Clarify 연습** – 랜덤 문제를 10분간 “한국어→주석”으로만 변환.
Day 2 : **Brute-Force만 코딩** – 최적화 금지, 동작만 확인.
Day 3 : **MECE 분해** – 복습 문제 3개를 단계별 표로 풀어보기.
Day 4 : **Pythonic 리팩터링** – Day 2 코드에 내장함수·라이브러리 삽입.
Day 5 : **모의 인터뷰** – 친구/AI에게 단계 1→6을 말로 설명하며 라이브 코딩[^14][^13].

### 체크리스트 (인터뷰/온라인 저지 공용)

1. 입출력 유형을 소리 내어 확인했는가?
2. 최소 2개의 엣지케이스를 먼저 적었는가?
3. 가장 단순한 해법의 복잡도를 계산했는가?
4. 하위 함수/모듈 이름이 기능을 설명하는가?
5. 내장 함수를 쓸 수 있는 부분을 놓치지 않았는가?
6. 제출 전 모든 테스트를 함수로 자동화했는가?

## 6. 결론

**문제를 “정확히 읽고-쪼개고-단순화”하는 6-Step 루틴**에 파이썬 내장 도구를 결합하면,
① 사고 과정이 명료해지고 ② 구현 시간이 짧아지며 ③ 디버깅 포인트가 구조화된다.
꾸준히 루틴을 반복해 체득하면 어떤 난이도의 코딩테스트도 체계적으로 접근할 수 있다.

<div style="text-align: center">⁂</div>

[^1]: https://dev.to/liaowow/5-step-strategy-you-can-use-for-your-next-coding-interview-2kd9

[^2]: https://www.designgurus.io/answers/detail/how-to-solve-coding-interview-problems

[^3]: https://www.freecodecamp.org/news/problem-solving-and-technical-interview-prep/

[^4]: https://www.youtube.com/watch?v=YUuBOey6ElU

[^5]: https://dev.to/calebgcc/follow-these-steps-to-ace-your-next-coding-interview-3j6l

[^6]: https://www.techinterviewhandbook.org/coding-interview-techniques/

[^7]: https://algocademy.com/blog/why-problem-decomposition-is-the-most-underrated-skill-in-coding-interviews/

[^8]: https://www.linkjob.ai/interview-questions/palantir-decomposition-interview/

[^9]: https://heicodersacademy.com/blog/stand-out-python-coding-interview/

[^10]: https://www.kdnuggets.com/2023/03/7-mustknow-python-tips-coding-interviews.html

[^11]: https://www.geeksforgeeks.org/must-know-things-to-clear-your-python-coding-interview/

[^12]: https://www.youtube.com/watch?v=Q4C3ZRJLnac

[^13]: https://dev.to/dan_starner/steps-towards-problem-solving-in-a-technical-interview-41pb

[^14]: https://www.designgurus.io/answers/detail/advanced-coding-drills-for-improving-problem-decomposition-skills

[^15]: https://www.ask.com/news/unlocking-success-essential-tips-nailing-python-interview-questions

[^16]: https://www.datacamp.com/blog/top-python-interview-questions-and-answers

[^17]: https://www.finalroundai.com/blog/how-to-ace-the-palantir-decomposition-interview-a-comprehensive-preparation-guide

[^18]: https://www.youtube.com/watch?v=IslCQszgr4I

[^19]: https://www.sitepoint.com/tackle-python-interview/

[^20]: https://www.reddit.com/r/cscareerquestionsEU/comments/17c7xwd/interview_preparation_system_decomposition/

