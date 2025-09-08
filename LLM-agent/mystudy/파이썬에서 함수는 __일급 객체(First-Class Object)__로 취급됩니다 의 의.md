<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" class="logo" width="120"/>

# 파이썬에서 함수는 **일급 객체(First-Class Object)**로 취급됩니다 의 의미

파이썬에서 함수는 **일급 객체(First-Class Object)**로 취급된다는 말의 뜻은, 함수가 숫자, 문자열, 리스트 등과 마찬가지로 **다음의 세 가지 조건을 만족하는 “일반적인 값”처럼 다뤄진다**는 의미입니다[^1][^2][^3][^4][^5][^6]:

1. **변수나 데이터 구조(리스트, 딕셔너리 등)에 할당할 수 있다.**
⇒ 예를 들어, 어떤 함수 `func`를 다른 변수에 할당해서 사용할 수 있습니다.

```python
def greet(name):
    return f'Hello, {name}!'
my_func = greet
print(my_func('Python'))  # Hello, Python!
```

2. **함수의 인자로 전달할 수 있다.**
⇒ 함수 자체를 또 다른 함수에 인자로 넘길 수 있습니다.

```python
def call_func(func, value):
    return func(value)
print(call_func(greet, 'World'))  # Hello, World!
```

3. **함수의 반환값으로 사용할 수 있다.**
⇒ 함수가 다른 함수(내부 함수)를 반환할 수 있습니다.

```python
def outer():
    def inner():
        return 'Inner!'
    return inner
result = outer()
print(result())  # Inner!
```


이러한 특징 때문에 **함수를 값처럼 자유롭게 전달, 저장, 반환**할 수 있고,
파이썬은 고차 함수(map, filter 등), 콜백 함수, 클로저, 데코레이터 등 다양한 프로그래밍 패턴을 손쉽게 사용할 수 있습니다[^1][^2][^3][^4][^6].
즉, *“함수를 변수처럼 사용할 수 있고, 함수도 다른 값들과 똑같이 취급된다”*는 것이
함수가 일급 객체라는 의미입니다.

<div style="text-align: center">⁂</div>

[^1]: https://tibetsandfox.tistory.com/8

[^2]: https://amazelimi.tistory.com/entry/Python-일급객체First-Class-Object란-LIM

[^3]: https://developshrimp.com/entry/Python-일급-함수-정의와-특징

[^4]: https://wikidocs.net/232976

[^5]: https://kukuta.tistory.com/323

[^6]: https://hyeo-noo.tistory.com/283

[^7]: https://velog.io/@cataiden/python-first-class-obj

[^8]: https://victoria-k.tistory.com/entry/4-객체로서의-함수-일급-함수와-고위함수-데코레이터와-클로저

[^9]: https://panda5176.tistory.com/21

[^10]: https://inpa.tistory.com/entry/CS-👨‍💻-일급-객체first-class-object

