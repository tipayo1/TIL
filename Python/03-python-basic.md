# 🎯 03-Python-basic

# ✅ 파이썬 제어문(Control Statement)

파이썬에서 코드 흐름을 제어하는 대표적인 방법은 **조건문, 반복문, 반복 제어문**이 있습니다.

## 🔹 조건문 (Conditional Statements)

### 1. if 문 기본 구조
```python
if 조건:
    실행문
elif 조건:
    실행문
else:
    실행문
```
- 조건식은 **True/False**로 평가됨  
- `elif`, `else`는 선택적으로 사용  
- **코드 블록은 반드시 들여쓰기(보통 4칸)**로 구분

### 2. 조건 표현식 (삼항 연산자)
```python
result = '양수' if num > 0 else '음수'
```
- 조건에 따라 값을 선택할 때 한 줄로 표현

### 3. 중첩 조건문
```python
if 조건1:
    if 조건2:
        실행문
```
- if문 안에 또 if문(중첩 if) 작성 가능

### 4. 사용 예시
```python
num = int(input())
if num % 2 == 0:
    print("짝수")
else:
    print("홀수")
```

## 🔹 반복문 (Loops)

### 1. while 문
```python
while 조건:
    실행문
```
- 조건이 **True인 동안** 반복 실행  
- 반드시 **종료 조건** 필요 (무한 루프 주의!)

### 2. for 문
```python
for 변수 in 반복가능한객체:
    실행문
```
- 문자열, 리스트, range 등 **iterable** 객체 순회  
- 딕셔너리 순회: `dict.keys()`, `dict.values()`, `dict.items()`
- **enumerate()**를 쓰면 인덱스와 값을 동시에 사용할 수 있음

#### ⏩ 예시
```python
for char in "안녕!":
    print(char)

i = 1
while i  **Tip.**  
>  
> - 들여쓰기는 파이썬 문법에서 매우 중요합니다!  
> - 조건문, 반복문, 함수 등 블록 구조에서는 **항상 들여쓰기**를 잊지 마세요.
> - 코드를 꼭 코드블록(백틱 3개 \`\`\`)으로 감싸 읽기 쉽게 만드세요.

