# 🎯 07-Python-basic

# 📚 Python OOP 요약 노트

## 🔸 객체(Object)란?

Python에서 모든 것은 객체입니다.
모든 객체는 다음 3가지 구성 요소를 가집니다:

*   **타입(type):** 어떤 연산자/조작이 가능한가?
*   **속성(attribute):** 어떤 상태(데이터)를 가지는가?
*   **조작법(method):** 어떤 동작을 수행할 수 있는가?

## 🔸 객체 지향 프로그래밍(OOP)

객체(object)를 중심으로 프로그램을 구성하는 패러다임.
절차 중심 프로그래밍과는 달리, 객체 간 상호작용 중심입니다.

**장점:**
*   직관성
*   재사용성
*   변경 용이성

## 🔸 클래스(Class)와 인스턴스(Instance)

### 📌 클래스

*   객체의 설계도.
*   `class` 키워드를 통해 정의.
*   클래스명은 PascalCase 사용 권장.

```python
class Person:
    """사람 클래스"""
```

### 📌 인스턴스

*   클래스를 통해 생성된 구체적 객체.
*   `클래스()`로 생성.

```python
p1 = Person()
```

## 🔸 속성(Attribute)과 메서드(Method)

| 타입   | 속성 예시 | 메서드 예시            |
| :----- | :-------- | :--------------------- |
| `str`  | 없음      | `.capitalize()`, `.split()` |
| `list` | 없음      | `.append()`, `.sort()` |
| `dict` | 없음      | `.keys()`, `.items()`  |

*   **속성:** 객체의 상태/데이터 → `객체.속성`
*   **메서드:** 객체의 동작/기능 → `객체.메서드()`

## 🔸 인스턴스 변수 vs 클래스 변수

| 구분         | 인스턴스 변수              | 클래스 변수                            |
| :----------- | :------------------------- | :------------------------------------- |
| 정의 위치    | `__init__()` 또는 외부       | 클래스 내부                            |
| 공유 여부    | 개별 인스턴스마다 별도 존재 | 모든 인스턴스가 공유                   |
| 접근 방법    | `self.변수명`              | `클래스.변수명` 또는 `인스턴스.변수명` |

## 🔸 메서드 종류

### ✅ 인스턴스 메서드

`self`를 첫 인자로 받음

```python
class MyClass:
    def method(self):
        # ...
```

### ✅ 클래스 메서드

`@classmethod` 데코레이터와 `cls` 인자 사용

```python
class MyClass:
    @classmethod
    def method(cls):
        # ...
```

### ✅ 스태틱 메서드

`@staticmethod` 데코레이터 사용, `self`/`cls` 인자 없음

```python
class MyClass:
    @staticmethod
    def method():
        # ...
```

## 🔸 생성자 & 소멸자

### ✅ 생성자: `__init__(self, ...)`

인스턴스 생성 시 자동 호출

```python
class MyClass:
    def __init__(self, name):
        self.name = name
```

### ✅ 소멸자: `__del__(self)`

인스턴스 삭제 시 자동 호출

## 🔸 매직 메서드 (Magic Methods)

`__xxx__` 형태의 메서드. 특정 연산자나 함수 호출 시 자동 실행됩니다.

**예시:**

| 메서드    | 설명             |
| :-------- | :--------------- |
| `__str__` | `print()` 출력 내용 지정 |
| `__eq__`  | `==` 비교         |
| `__gt__`  | `>` 비교          |
| `__add__` | `+` 연산 정의      |

## 🔸 네임스페이스 (Namespace)

*   **속성 탐색 순서:** 인스턴스 → 클래스
*   **변수 탐색:** LEGB (Local → Enclosing → Global → Built-in)

## 🔸 상속 (Inheritance)

기존 클래스(부모)의 속성과 메서드를 자식 클래스에서 재사용.

```python
class Student(Person):
    def __init__(self, name, age, score):
        super().__init__(name, age) # 부모 클래스의 __init__ 호출
        self.score = score
```

### `super()` 사용

*   부모 클래스의 메서드 호출에 사용됩니다.

### `isinstance()`, `issubclass()`

*   객체/클래스 간 관계를 확인합니다.

## 🔸 OOP의 4대 핵심 원칙

*   **추상화(Abstraction):** 공통된 특징만 표현 (예: `Person` → `Student`, `Teacher` 상속)
*   **상속(Inheritance):** 코드 재사용
*   **다형성(Polymorphism):** 같은 이름의 메서드가 상황에 따라 다르게 동작
*   **캡슐화(Encapsulation):** 내부 구현은 감추고, 필요한 기능만 노출

## 🔸 예제: Circle 클래스

```python
class Circle:
    pi = 3.1415 # 클래스 변수

    def __init__(self, r):
        self.r = r # 인스턴스 변수

    def get_area(self):
        return round(self.pi * self.r ** 2, 3) # 인스턴스 메서드
```