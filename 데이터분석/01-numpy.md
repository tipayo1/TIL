# 🎯 오늘 학습한 핵심 내용 TIL

# D1 NumPy 기초 - 1일차 요약노트

## 1. 데이터 분석 소개

- **데이터 분석**: 데이터에서 유용한 정보와 인사이트를 추출하는 과정  
- **데이터 기반 의사결정**: 현대 비즈니스의 핵심 요소  
- **해결 문제**: 트렌드 파악, 이상 감지, 고객 이해, 비용 절감, 새로운 가치 창출  

## 2. 데이터 분석 프로세스

1. 문제 정의 : 명확한 질문과 목표 설정  
2. 데이터 수집 : 관련 데이터 확보  
3. 데이터 전처리 : 정제, 변환, 통합  
4. 탐색적 분석 (EDA) : 패턴 및 관계 발견  
5. 모델링 및 분석 : 통계/머신러닝 적용  
6. 결과 해석 및 커뮤니케이션 : 인사이트 도출 및 공유  

## 3. 파이썬 데이터 분석 라이브러리

- NumPy: 수치 계산, 다차원 배열  
- Pandas: 데이터 조작 및 분석  
- Matplotlib / Seaborn: 시각화  
- SciPy: 과학 계산  
- Scikit-learn: 머신러닝  

## 4. NumPy 기초

### NumPy 개요

- NumPy = Numerical Python의 약자  
- 특징: 빠른 연산 속도, 메모리 효율성, 다차원 배열 지원  
- 핵심 데이터 구조 : `ndarray`  

### 리스트와 NumPy 배열 비교

| 항목       | 리스트                         | NumPy 배열                   |
|------------|-------------------------------|-----------------------------|
| 데이터 타입 | 서로 다른 데이터 타입 저장 가능   | 동일한 데이터 타입 저장       |
| 크기       | 동적 크기                      | 고정 크기                    |
| 연산 속도  | 느림                          | 빠름                        |

### 배열 생성 예제

```python
import numpy as np

# 기본 배열 생성
arr = np.array([1, 2, 3, 4, 5])

# 특수 배열 생성
zeros = np.zeros(5)                # [0. 0. 0. 0. 0.]
ones = np.ones((2, 3))             # 2x3 행렬, 모든 값이 1
full = np.full(5, 7)               # [7 7 7 7 7]

# 시퀀스 배열
arange = np.arange(0, 10, 2)       # [0 2 4 6 8]
linspace = np.linspace(0, 1, 5)    # [0.  0.25 0.5  0.75 1.]

# 난수 배열
random = np.random.rand(3, 3)      # 0~1 균등분포 난수
```

### 배열 속성

```python
print(arr.shape)  # 배열 형태 (튜플)
print(arr.ndim)   # 차원 수
print(arr.size)   # 총 요소 수
print(arr.dtype)  # 배열 데이터 타입
```

### 배열 재구성

```python
arr = np.arange(12)
reshaped = arr.reshape(3, 4)   # 3x4 행렬 변형

flat = reshaped.flatten()      # 평탄화 (복사본)
flat_view = reshaped.ravel()   # 평탄화 (뷰)
```

## 5. 인덱싱과 슬라이싱

### 기본 인덱싱

```python
# 1차원 배열
arr = np.array([10, 20, 30, 40, 50])
print(arr[0])     # 10 (첫 번째 요소)
print(arr[-1])    # 50 (마지막 요소)

# 2차원 배열
arr_2d = np.array([[1, 2, 3],
                   [4, 5, 6],
                   [7, 8, 9]])
print(arr_2d[0, 0])  # 1 (첫 번째 행, 첫 번째 열)
print(arr_2d[1, 2])  # 6 (두 번째 행, 세 번째 열)
```

### 슬라이싱

```python
# 1차원 슬라이싱
arr = np.array([0,1,2,3,4,5,6,7,8,9])
print(arr[2:5])   # [2 3 4]
print(arr[:5])    # [0 1 2 3 4]
print(arr[5:])    # [5 6 7 8 9]
print(arr[::2])   # [0 2 4 6 8]

# 2차원 슬라이싱
print(arr_2d[:2])       # 처음 두 행
print(arr_2d[:, 1:3])   # 모든 행의 두 번째와 세 번째 열
print(arr_2d[1:3, 0:2]) # 2~3행, 1~2열 부분
```

### 고급 인덱싱

```python
arr = np.array([1, 2, 3, 4, 5])
mask = arr > 3
print(arr[mask])           # [4 5]
print(arr[arr % 2 == 0])   # [2 4] (짝수만)

indices = np.array([1, 3, 4])
print(arr[indices])        # [2 4 5]
```

## 6. NumPy 배열 연산

### 기본 산술 연산

```python
a = np.array([1, 2, 3])
b = np.array([4, 5, 6])

print(a + b)    # [5 7 9]
print(a - b)    # [-3 -3 -3]
print(a * b)    # [4 10 18]
print(a / b)    # [0.25 0.4 0.5]
print(a ** 2)   # [1 4 9]
```

### 브로드캐스팅

- 정의: 크기가 다른 배열 간에도 자동으로 연산이 가능하도록 작은 배열을 확장  
- 규칙  
  1) 차원이 다르면 작은 배열 앞에 1을 추가  
  2) 형태가 같거나 한쪽이 1이면 호환 가능  
  3) 위 조건을 만족하지 않으면 오류 발생  

```python
arr = np.array([1, 2, 3])
print(arr + 10)  # [11 12 13]

matrix = np.array([[1, 2, 3], [4, 5, 6]])
row_vec = np.array([10, 20, 30])
print(matrix + row_vec)
# [[11 22 33]
#  [14 25 36]]
```

### 주요 연산 함수

```python
arr = np.array([1, 2, 3, 4, 5])

# 수학 함수
print(np.sqrt(arr))    # 제곱근
print(np.exp(arr))     # 지수 함수
print(np.sin(arr))     # 사인 함수

# 집계 함수
print(np.sum(arr))     # 합계
print(np.mean(arr))    # 평균
print(np.min(arr))     # 최소값
print(np.max(arr))     # 최대값
print(np.std(arr))     # 표준편차
```

## 7. 배열 결합 및 분할

```python
a = np.array([1, 2, 3])
b = np.array([4, 5, 6])

# 결합
print(np.concatenate([a, b]))  # [1 2 3 4 5 6]
print(np.vstack([a, b]))       # [[1 2 3]
                              #  [4 5 6]]

# 분할
arr = np.arange(10)
print(np.split(arr, 2))        # [array([0 1 2 3 4]), array([5 6 7 8 9])]
print(np.split(arr, [3, 7]))   # [array([0 1 2]), array([3 4 5 6]), array([7 8 9])]
```

## 8. 브로드캐스팅 심화

### 이점

- 코드 간결성: 복잡한 루프 대신 간결한 연산 가능  
- 메모리 효율성: 실제 큰 배열 생성 없이 연산  
- 성능: 벡터화된 연산으로 속도 향상  

### 예제

```python
matrix = np.array([[1, 2, 3],
                   [4, 5, 6],
                   [7, 8, 9]])
row_vec = np.array([10, 20, 30])
col_vec = np.array([[100], [200], [300]])

# 행 벡터 브로드캐스팅 : 각 행에 더함
print(matrix + row_vec)
# [[11 22 33]
#  [14 25 36]
#  [17 28 39]]

# 열 벡터 브로드캐스팅 : 각 열에 더함
print(matrix + col_vec)
# [[101 102 103]
#  [204 205 206]
#  [307 308 309]]
```

### 실용적인 응용

```python
data = np.array([[1, 2, 3],
                 [4, 5, 6],
                 [7, 8, 9]])
mean = np.mean(data, axis=0)  # 열별 평균
std = np.std(data, axis=0)    # 열별 표준편차
normalized = (data - mean) / std  # 정규화

points = np.random.rand(5, 2)  # 5개의 2D 점
diff = points[:, np.newaxis, :] - points[np.newaxis, :, :]
distances = np.sqrt(np.sum(diff ** 2, axis=2))  # 점간 거리 계산
```

## 9. NumPy 실전 응용

### 데이터 분석

```python
scores = np.array([
    [88, 92, 75],
    [90, 87, 66],
    [67, 89, 82],
    [95, 78, 89],
    [78, 85, 94]
])

student_means = np.mean(scores, axis=1)  # 학생별 평균
subject_means = np.mean(scores, axis=0)  # 과목별 평균
rankings = np.argsort(student_means)[::-1]  # 내림차순 인덱스 (성적 순위)
```

### 시뮬레이션 및 통계

```python
flips = np.random.binomial(1, 0.5, 1000)  # 동전 던지기 1000회 시뮬레이션
heads = np.sum(flips)                      # 앞면 횟수
print(f"앞면 비율: {heads/1000:.2f}")

dice = np.random.randint(1, 7, (100, 2))   # 100번 2개 주사위 던지기
sums = np.sum(dice, axis=1)                # 각 주사위 합
print(f"합이 7인 확률: {np.mean(sums == 7):.2f}")
```

### 선형대수 연산

```python
A = np.array([[1, 2], [3, 4]])
B = np.array([[5, 6], [7, 8]])

C = np.matmul(A, B)  # 행렬 곱 (또는 A @ B)
print(C)

A_inv = np.linalg.inv(A)  # 역행렬
print(A_inv)

eigenvalues, eigenvectors = np.linalg.eig(A)  # 고유값과 고유벡터
print(eigenvalues)
print(eigenvectors)
```

## 10. 종합 요약

- **핵심 개념**  
  - NumPy ndarray: 효율적인 다차원 수치 배열  
  - 벡터화된 연산: 루프 없이 전체 배열에 연산 적용  
  - 브로드캐스팅: 다른 크기의 배열 간 연산 자동 확장  
  - 인덱싱/슬라이싱: 배열의 특정 요소 접근  
  - 집계 함수: 합계, 평균, 표준편차 등  

- **활용 분야**  
  - 데이터 전처리 : 결측치/이상치 처리, 정규화  
  - 통계 분석 : 기술통계, 상관관계, 가설검정  
  - 머신러닝 : 특성 공학, 모델 입력 준비  
  - 과학 계산 : 물리, 공학, 금융 모델링  
  - 이미지 처리 : 필터링, 변환, 특성 추출  

- **실무 팁**  
  - 메모리 효율 : 적절한 데이터 타입 사용 (np.int32, np.float32)  
  - 뷰(view) vs 복사본(copy) : 연산 시 의도치 않은 데이터 변경 주의  
  - 브로드캐스팅 이해 : 복잡한 연산 전에 형태 호환성 확인  
  - 벡터화 활용 : 가능한 한 반복문 대신 NumPy 내장 함수 사용  

## 11. axis 관련

### 핵심 개념

- axis는 "축 번호"이지, "행"이나 "열" 자체가 아님!  
- 즉, 어느 축을 기준으로 연산할 것인지 의미  

### 2차원 배열 예제

```python
import numpy as np

arr = np.array([[1, 2, 3],
                [4, 5, 6]])
print(arr.shape)  # (2, 3)

# axis=0: 행 방향(세로 ↓ 방향) — 같은 열끼리 연산
# axis=1: 열 방향(가로 → 방향) — 같은 행끼리 연산

print(np.sum(arr, axis=0))  # [5 7 9] (같은 열끼리 합)
print(np.sum(arr, axis=1))  # [6 15] (같은 행끼리 합)
```

### 이해 팁

| axis 번호 | 기준 축  | 연산 방향               | 비유          |
|:---------:|---------|------------------------|---------------|
| 0         | 행 인덱스 | 열 단위 연산 (세로줄 기준) | 세로 방향(↓)   |
| 1         | 열 인덱스 | 행 단위 연산 (가로줄 기준) | 가로 방향(→)   |

- 흔히 axis=0을 “행을 선택”으로 혼동하는데, 실제로는 “같은 열끼리” 연산을 의미함.  
- axis=1은 “같은 행끼리” 연산을 뜻함.