
git init

git config --global user.name
git config --global user.email

git add <filename>
git add .

git commit -m '<message>'
<!-- 지금 TIL은 remote add origin 할 필요 없음 -> clone 했기 때문 -->
git remote add origin <URL>

git remote add origin main

git status

git clone <URL>

```md
# 질문 1.
any() 함수와 or: 앞이 True면 뒤를 평가하지 않고 즉시 True 반환이 닮은 것 같아
네, 맞아요!
any() 함수와 or 연산자의 동작 방식은 매우 닮았습니다.
둘 다 **"앞에서 True가 나오면 즉시 True를 반환하고, 뒤는 평가하지 않는다"**는 단축평가(Short-circuit Evaluation) 패턴을 따릅니다.

예시로 비교해 보기
1. or 연산자
python
a = True
b = some_expensive_function()  # 호출되지 않음
result = a or b  # a가 True이므로 b는 평가하지 않고 result는 True
2. any() 함수
python
lst = [True, False, some_expensive_function()]  # 세 번째 값은 평가되지 않음
result = any(lst)  # 앞에서 True를 만나면 바로 True 반환
동작 원리
or 연산자: 왼쪽 값이 True면 오른쪽은 아예 평가하지 않음.

any() 함수: 반복 가능한 객체에서 앞에서 True를 만나면 바로 True 반환, 남은 값들은 확인하지 않음.

결론
or와 any() 모두 True를 만나면 즉시 종료하는 효율적인 패턴을 사용합니다.

차이점은 or는 두 개의 피연산자(표현식) 사이에서, **any()**는 여러 값(이터러블)에서 동작한다는 점입니다.

이처럼 단축평가는 파이썬의 효율성과 성능을 높여주는 중요한 개념입니다.

실제로 any([a, b, c])는 a or b or c와 논리적으로 완전히 같습니다!
```