# 🎯 03-Python-basic

# 🔷 데이터 구조 (Data Structure)

> 데이터를 **효율적으로 구성·저장·관리**하기 위한 형식

## 📚 종류

- **순서 있음**  
  `문자열(str)`, `리스트(list)`, `튜플(tuple)`
- **순서 없음**  
  `셋(set)`, `딕셔너리(dict)`

## 📌 문자열 (String)
- **특징**: `immutable`, `ordered`, `iterable`

### 문자열 탐색 및 검증
- `.find(x)`, `.index(x)` : x의 위치 반환 (없으면 -1 / 오류)
- `.startswith(x)`, `.endswith(x)` : 접두/접미어 확인
- `.isalpha()`, `.isspace()`, `.isdigit()` 등: 구성 확인

### 문자열 변경
- `.replace(old, new[, count])`: 치환
- `.strip([chars])`, `.lstrip()`, `.rstrip()`: 공백/문자 제거
- `.split([sep])`: 분할 → 리스트
- `'sep'.join(iterable)`: 구분자로 문자열 결합
- 대소문자: `.capitalize()`, `.title()`, `.upper()`, `.lower()`, `.swapcase()`

## 📌 리스트 (List)
- **특징**: `mutable`, `ordered`, `iterable`

### 값 추가 및 삭제
- `.append(x)`: 맨 끝에 추가
- `.extend(iterable)`: 여러 개 추가
- `.insert(i, x)`: i번째에 삽입
- `.remove(x)`: 첫 x 제거
- `.pop([i])`: i번째 제거 및 반환 (default 마지막)
- `.clear()`: 모두 삭제

### 탐색 및 정렬
- `.index(x)`, `.count(x)`: 위치 / 개수 확인
- `.sort(key=, reverse=)`: 원본 정렬
- `sorted(list)`: 정렬 (원본 유지)
- `.reverse()`: 원본 뒤집기

## 📌 튜플 (Tuple)
- **특징**: `immutable`, `ordered`, `iterable`
- `.index(x)`: 위치 반환
- `.count(x)`: 개수 반환

## 📌 셋 (Set)
- **특징**: `mutable`, `unordered`, `iterable`
- `.add(x)`, `.update(iterable)`: 요소 추가
- `.remove(x)`: x 제거 (없으면 오류)
- `.discard(x)`: x 제거 (없어도 오류 없음)

## 📌 딕셔너리 (Dictionary)
- **특징**: `mutable`, `unordered`, `iterable` (Key:Value)

### 조회
- `dict[key]`: key로 접근 (없으면 오류)
- `.get(key[, default])`: 기본값 반환
- `.setdefault(key[, default])`: 없으면 추가 후 반환

### 추가 및 삭제
- `.pop(key[, default])`: 삭제 및 반환
- `.update(other)`: 병합/갱신

## 🧠 얕은 복사 vs 깊은 복사

**🔹 Immutable 데이터:** 값만 복사됨  
```python
a = 20
b = a
b = 10  # a 영향 없음
```

**🔹 Mutable 데이터**  
- 할당: 같은 객체를 바라봄 (`a is b → True`)
- 얕은 복사: 객체는 다르나 내부 객체는 공유  
  `b = a[:]`, `b = list(a)`
- 깊은 복사: 내부 객체까지 모두 복제  
  ```python
  from copy import deepcopy
  a = [1, 2, ['a', 'b']]
  b = deepcopy(a)
  ```

> 각 자료구조 별로 `.dir()`로 메서드 확인, `help()`로 자세한 설명 확인 가능

