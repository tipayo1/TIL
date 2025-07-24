# 🎯 04-05-Python-basic

# 함수(Function) I 요약

### 🔹 함수의 개념  
특정 기능을 수행하는 코드 묶음  
`def` 키워드로 정의하고, `return`으로 결과를 반환함

### 🔹 함수 사용 이유  
- **가독성**: 코드를 더 명확하게 작성 가능  
- **재사용성**: 중복 없이 반복 사용 가능  
- **유지보수 용이**: 기능별로 분리되어 수정이 쉬움

### 🔹 함수 기본 구조
```python
def function_name(매개변수):
    # 함수 내용
    return 반환값
```

### 🔹 함수 호출
```python
function_name(전달인자)
```

## 📌 함수의 구성 요소

### 🔹 입력 (Input)  
- **매개변수(Parameter)**: 함수 정의 시 입력값을 받는 변수  
- **전달인자(Argument)**: 함수 호출 시 전달하는 실제 값

### 🔹 출력 (Output)  
- `return` 문으로 반환 (반드시 한 개 객체 반환)

## 📌 함수 인자 종류

1. **위치 인자 (Positional Arguments)**  
   순서대로 전달되는 인자

2. **기본 인자 값 (Default Arguments)**  
   인자를 전달하지 않으면 기본값 사용  
   ```python
   def greeting(name='익명'):
       return f'{name}, 안녕?'
   ```

3. **키워드 인자 (Keyword Arguments)**  
   매개변수 이름을 지정하여 인자 전달  
   ```python
   greeting(name='철수', age=20)
   ```

4. **가변 위치 인자 (*args)**  
   개수가 정해지지 않은 위치 인자를 튜플 형태로 받음  
   ```python
   def my_max(*args):
       # 여러 값 중 최대값 찾기
   ```

5. **가변 키워드 인자 (**kwargs)**  
   키워드 인자를 딕셔너리 형태로 받음  
   ```python
   def my_dict(**kwargs):
       return kwargs
   ```

## 📌 함수와 스코프(Scope)

### 🔹 스코프 종류  
- **Local (L)**: 함수 내부  
- **Enclosed (E)**: 함수 안의 함수  
- **Global (G)**: 모듈 전체  
- **Built-in (B)**: 파이썬 내장 영역  

**LEGB Rule**: 이름 검색 순서

### 🔹 변수 수명주기  
- Local → Global → Built-in 순서로 참조  
- 지역 변수는 함수 호출 시 생성, 종료 시 소멸

### 🔹 전역 변수 접근  
- 함수 내부에서 전역 변수 변경 시 `global` 키워드 필요  
- 중첩 함수에서 바깥 함수의 변수 변경 시 `nonlocal` 사용

## 📌 재귀 함수 (Recursive Function)

### 🔹 개념  
함수 내부에서 자기 자신을 호출하는 함수

### 🔹 예시: 팩토리얼 함수
```python
def factorial(n):
    if n == 1:
        return 1
    return n * factorial(n - 1)
```