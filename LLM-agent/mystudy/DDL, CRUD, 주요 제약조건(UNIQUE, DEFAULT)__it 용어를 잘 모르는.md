<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" class="logo" width="120"/>

# DDL, CRUD, 주요 제약조건(UNIQUE, DEFAULT)

it 용어를 잘 모르는 사람에게 쉽게 풀어 설명해줘

IT 용어를 처음 접하는 분들을 위해 데이터베이스의 기본 개념들을 쉽게 설명드리겠습니다. 데이터베이스는 마치 거대한 디지털 창고와 같다고 생각하시면 됩니다.

## **DDL (Data Definition Language) - 데이터 정의어**

DDL은 **"데이터를 담는 상자를 정의하는 언어"**라고 생각하시면 됩니다[^1_1]. 마치 집을 짓기 전에 설계도를 그리는 것과 같습니다.

**DDL의 주요 역할:**

- **테이블 생성**: 새로운 데이터 저장 공간을 만드는 것
- **테이블 변경**: 기존 저장 공간의 구조를 수정하는 것
- **테이블 삭제**: 더 이상 필요 없는 저장 공간을 제거하는 것

예를 들어, 학생 정보를 저장할 테이블을 만든다면, "학번, 이름, 전공" 같은 항목들을 미리 정의하는 것이 DDL의 역할입니다[^1_1].

## **CRUD - 데이터 관리의 기본 4가지 작업**

CRUD는 **"Create, Read, Update, Delete"**의 줄임말로, 데이터를 다루는 가장 기본적인 4가지 작업을 의미합니다[^1_2][^1_3]. 일상생활로 비유하면 다음과 같습니다:

**Create (생성)**: 새로운 데이터를 추가하는 것

- 예시: 새로운 학생 정보를 등록하기

**Read (읽기)**: 저장된 데이터를 조회하는 것

- 예시: 특정 학생의 성적을 확인하기

**Update (수정)**: 기존 데이터를 변경하는 것

- 예시: 학생의 연락처 정보를 업데이트하기

**Delete (삭제)**: 데이터를 제거하는 것

- 예시: 졸업한 학생의 정보를 삭제하기

CRUD는 거의 모든 시스템에서 사용되는 가장 기본적인 개념입니다[^1_2]. 예를 들어, 인스타그램에서 사진을 올리고(Create), 피드를 보고(Read), 게시물을 수정하고(Update), 삭제하는(Delete) 모든 행동이 CRUD에 해당합니다.

## **주요 제약조건 - 데이터의 규칙**

제약조건은 데이터베이스에 저장되는 정보가 올바른 형태를 유지하도록 하는 **"규칙"**입니다[^1_4]. 마치 도서관에서 책을 정리하는 규칙과 같습니다.

### **UNIQUE 제약조건**

UNIQUE는 **"중복을 허용하지 않는"** 규칙입니다[^1_5][^1_4].

**특징:**

- 같은 값이 두 번 들어갈 수 없음
- 하나의 테이블에 여러 개 만들 수 있음
- NULL(빈 값)은 허용됨[^1_5]

**실생활 예시:**

- 주민등록번호: 모든 사람이 서로 다른 번호를 가져야 함
- 이메일 주소: 같은 이메일로 여러 계정을 만들 수 없음
- 학번: 한 학교에서 같은 학번을 가진 학생이 두 명일 수 없음


### **DEFAULT 제약조건**

DEFAULT는 **"기본값"**을 설정하는 규칙입니다. 사용자가 특별히 값을 입력하지 않으면 미리 정해둔 값이 자동으로 들어갑니다.

**실생활 예시:**

- 회원가입 시 국가를 선택하지 않으면 자동으로 "대한민국"으로 설정
- 주문 상태를 입력하지 않으면 자동으로 "주문접수"로 설정
- 가입일을 입력하지 않으면 자동으로 "오늘 날짜"로 설정

이러한 제약조건들은 데이터의 **무결성**을 보장합니다[^1_4]. 즉, 잘못된 정보나 중복된 정보가 들어가는 것을 방지하여 데이터베이스를 깔끔하고 정확하게 유지하는 역할을 합니다.

<div style="text-align: center">⁂</div>

[^1_1]: https://bears-paw.tistory.com/entry/SQL-DDL-DML-DCL-이란-무엇일까-간단정리

[^1_2]: https://idkim97.github.io/2022-08-17-CRUD란/

[^1_3]: https://f-lab.kr/insight/understanding-crud-operations

[^1_4]: https://yeobi27.tistory.com/278

[^1_5]: https://backshren20.tistory.com/102

[^1_6]: https://jay-din.tistory.com/342

[^1_7]: https://lab.wallarm.com/what/crud-생성-읽기-업데이트-및-삭제/?lang=ko

[^1_8]: https://aurumguide.tistory.com/11

[^1_9]: https://hee611.tistory.com/28

[^1_10]: https://velog.io/@yenicall/MySQL-기초-DDL-과정


---

# 오늘 배울 SQL 내용이야

DDL, CRUD, 주요 제약조건(UNIQUE, DEFAULT)

it 용어를 잘 모르는 사람에게 쉽게 풀어 설명해줘

오늘 배울 SQL 내용을 IT 초보자도 쉽게 이해할 수 있도록 설명드리겠습니다. SQL은 데이터베이스라는 거대한 디지털 창고를 관리하는 언어라고 생각하시면 됩니다.

## **DDL (Data Definition Language) - 데이터 정의어**

DDL은 **"데이터를 담는 상자를 정의하는 언어"**입니다[^2_1]. 마치 새로운 집을 짓기 전에 설계도를 그리는 것과 같은 역할을 합니다.

**DDL의 주요 기능:**

- **테이블 생성**: 새로운 데이터 저장 공간을 만드는 것
- **테이블 변경**: 기존 저장 공간의 구조를 수정하는 것
- **테이블 삭제**: 더 이상 필요 없는 저장 공간을 제거하는 것

예를 들어, 학생 정보를 저장할 테이블을 만든다면 "학번, 이름, 전공" 같은 항목들을 미리 정의하는 것이 DDL의 역할입니다[^2_1]. 테이블과 같은 데이터 구조를 정의하는데 사용되며 생성, 변경, 삭제하는데 사용되는 언어입니다[^2_1].

## **CRUD - 데이터 관리의 기본 4가지 작업**

CRUD는 **"Create, Read, Update, Delete"**의 줄임말로, 데이터를 다루는 가장 기본적인 4가지 작업을 의미합니다[^2_2]. 거의 모든 시스템에 적용되는 가장 기본이 되는 개념입니다[^2_2].

**Create (생성)**: 새로운 데이터를 추가하는 것

- 예시: 새로운 학생 정보를 등록하기
- 데이터베이스에 새로운 레코드를 추가하는 작업[^2_2]

**Read (읽기)**: 저장된 데이터를 조회하는 것

- 예시: 특정 학생의 성적을 확인하기
- 데이터베이스에서 저장된 데이터를 검색하고 읽어오는 작업[^2_2]

**Update (수정)**: 기존 데이터를 변경하는 것

- 예시: 학생의 연락처 정보를 업데이트하기
- 데이터베이스에서 기존 레코드를 수정하는 작업[^2_2]

**Delete (삭제)**: 데이터를 제거하는 것

- 예시: 졸업한 학생의 정보를 삭제하기
- 데이터베이스에서 레코드를 삭제하는 작업[^2_2]

CRUD는 소프트웨어 개발에서 데이터를 처리하는 기본적인 네 가지 작업으로, 대부분의 애플리케이션에서 필수적으로 구현되어야 하는 기능입니다[^2_3]. 예를 들어, 인스타그램에서 사진을 올리고(Create), 피드를 보고(Read), 게시물을 수정하고(Update), 삭제하는(Delete) 모든 행동이 CRUD에 해당합니다.

## **주요 제약조건 - 데이터의 규칙**

제약조건은 데이터베이스에 저장되는 정보가 올바른 형태를 유지하도록 하는 **"규칙"**입니다. 마치 도서관에서 책을 정리하는 규칙과 같습니다.

### **UNIQUE 제약조건**

UNIQUE 제약조건은 **"중복을 허용하지 않는"** 규칙입니다[^2_4]. 해당 컬럼에 들어가는 값이 유일해야 한다는 의미로, 중복 값을 허용하지 않습니다[^2_5].

**UNIQUE의 특징:**

- 테이블의 두 행이 고유한 것으로 선언된 열에 대해 동일한 값을 가질 수 없음[^2_4]
- 하나의 테이블에 여러 개의 UNIQUE 제약조건을 만들 수 있음
- NULL 값은 허용됨[^2_5]

**실생활 예시:**

- 주민등록번호: 모든 사람이 서로 다른 번호를 가져야 함
- 이메일 주소: 같은 이메일로 여러 계정을 만들 수 없음
- 학번: 한 학교에서 같은 학번을 가진 학생이 두 명일 수 없음

UNIQUE 제약조건은 데이터 정확성을 보장하고, 고유성 요구 사항을 위반하는 데이터가 입력되는 것을 방지하여 데이터 오류를 방지하는 데 도움이 됩니다[^2_4].

### **DEFAULT 제약조건**

DEFAULT 제약조건은 **"기본값"**을 설정하는 규칙입니다[^2_6]. 테이블의 열에 대한 기본값을 지정하는 데 사용되며, 새 행을 삽입할 때 열에 대해 명시적으로 값을 지정하지 않으면 기본값이 대신 사용됩니다[^2_6].

**DEFAULT의 특징:**

- 사용자가 특별히 값을 입력하지 않으면 미리 정해둔 값이 자동으로 들어감
- 기본값은 상수, 리터럴 값 또는 표현식일 수 있음[^2_6]
- 값은 할당된 열의 데이터 유형과 일치해야 함[^2_6]

**실생활 예시:**

- 회원가입 시 국가를 선택하지 않으면 자동으로 "대한민국"으로 설정
- 주문 상태를 입력하지 않으면 자동으로 "주문접수"로 설정
- 가입일을 입력하지 않으면 자동으로 "오늘 날짜"로 설정

이러한 제약조건들은 데이터의 **무결성**을 보장합니다. 즉, 잘못된 정보나 중복된 정보가 들어가는 것을 방지하여 데이터베이스를 깔끔하고 정확하게 유지하는 역할을 합니다.

<div style="text-align: center">⁂</div>

[^2_1]: https://bears-paw.tistory.com/entry/SQL-DDL-DML-DCL-이란-무엇일까-간단정리

[^2_2]: https://idkim97.github.io/2022-08-17-CRUD란/

[^2_3]: https://f-lab.kr/insight/understanding-crud-operations

[^2_4]: https://data-science-diary.tistory.com/58

[^2_5]: https://sumingkk.tistory.com/32

[^2_6]: https://data-science-diary.tistory.com/62

[^2_7]: https://jay-din.tistory.com/342

[^2_8]: https://velog.io/@yenicall/MySQL-기초-DDL-과정

[^2_9]: https://hee611.tistory.com/28

[^2_10]: https://acetes-mate.tistory.com/64


---

# 샤티아 나델라

사티아 나델라(Satya Narayana Nadella)는 1967년 3월 24일 인도 하이데라바드에서 태어난 마이크로소프트의 현 CEO로, 마이크로소프트를 세계에서 가장 가치 있는 기업 중 하나로 변모시킨 **"공감의 리더십"**으로 유명한 인물입니다[^3_1].

## **초기 생애와 교육**

나델라는 어린 시절 크리켓 선수를 꿈꾸던 소년이었습니다[^3_5]. 15세에 부모님이 사준 컴퓨터를 조립해보면서 컴퓨터에 대한 꿈을 가지기 시작했고, 인도에서 전기공학을 전공한 후 미국으로 유학을 떠났습니다[^3_5]. 위스콘신-밀워키 대학에서 전산학 학사를, 시카고 대학에서 MBA 학위를 받았습니다[^3_6].

## **마이크로소프트 입사와 경력**

### **초기 경력**

나델라는 썬마이크로시스템즈에서 사회생활을 시작한 후, **1992년 마이크로소프트에 입사**했습니다[^3_2][^3_5]. 그는 썬이 자체 칩, 운영 체제, 소프트웨어 도구를 직접 개발하는 풀스택 시스템 회사였던 반면, 마이크로소프트가 외부 개발자들과 협업하여 다양한 제품과 기술을 개발할 수 있는 플랫폼 회사를 지향한다는 점에서 마이크로소프트의 미래를 확신했습니다[^3_4].

### **주요 성과**

처음에는 윈도우NT 제작 부서에서 일하다가 비즈니스 솔루션 그룹의 책임자로 자리를 옮겼습니다[^3_5]. 2008년부터는 스티브 발머의 권유로 마이크로소프트의 검색엔진 **Bing 업무를 담당**하며 시장에 성공적으로 안착시켰습니다[^3_5].

가장 큰 성과는 **클라우드 서비스 분야**에서 나타났습니다. 엔터프라이즈\&클라우드 사업부 부사장을 맡으면서 클라우드 서비스의 영향력을 일찍 내다본 그는 **오피스365**를 출시하고, 윈도우 전용 클라우드였던 윈도 애저를 모든 운영체제 기반의 퍼블릭 클라우드인 **애저(Azure)**로 전환시켰습니다[^3_5].

## **CEO 취임과 변화**

### **어려운 출발**

**2014년 2월 마이크로소프트의 3번째 CEO**로 취임했을 때, 회사는 매우 어려운 상황이었습니다[^3_2][^3_5]. 모바일 시장에서 애플과 구글에 밀려 있었고, 블룸버그는 "아무도 MS의 CEO가 되고 싶어하지 않는다"고 비꼬기도 했습니다[^3_5]. 외부 언론들은 그의 임명을 "후퇴(fall back)"라고 혹평했습니다[^3_5].

### **혁신적 변화**

나델라는 마이크로소프트의 체질을 근본적으로 바꿨습니다. **"클라우드 퍼스트, 모바일 퍼스트"**를 외치며 기존 윈도우 중심의 사업모델에서 클라우드와 모바일 중심으로 전환했습니다[^3_5]. 그는 자기만족에 빠진 회사 분위기를 송두리째 흔들며 개혁을 단행했습니다[^3_5].

## **리더십 철학**

나델라의 리더십은 **"공감(empathy)"**을 핵심으로 합니다[^3_1][^3_7]. 그는 "공감 능력이 리더의 가장 중요한 덕목이라고 생각한다. 공감 능력은 자신이 이끄는 구성원들의 자신감을 키우기 때문이다"라고 말했습니다[^3_1].

마이크로소프트의 문화적 기반에 대해서도 독특한 관점을 가지고 있습니다. 빌 게이츠와 폴 앨런의 원래 비전인 **'소프트웨어 공장'** 개념을 중심으로, 단일 제품이나 기술에 집착하지 않는 문화를 형성했다고 설명합니다[^3_4].

## **현재와 미래**

나델라의 리더십 하에 마이크로소프트는 **2018년 3년 만에 구글의 모기업인 알파벳 시가총액을 뛰어넘는** 놀라운 부활을 이뤘습니다[^3_5]. 그는 현재도 AI와 양자컴퓨팅의 결합 등 미래 기술에 대한 장기적 투자를 지속하고 있으며, 호기심 중심의 연구 조직인 마이크로소프트 리서치(MSR)를 통해 혁신을 추진하고 있습니다[^3_3].

2017년에는 자신의 경험과 철학을 담은 저서 **"Hit Refresh"**를 출간하기도 했습니다[^3_2].

<div style="text-align: center">⁂</div>

[^3_1]: https://www.businesspost.co.kr/BP?command=article_view\&num=343724

[^3_2]: https://ko.wikipedia.org/wiki/사티아_%EB%82%98%EB%8D%B8%EB%9D%BC

[^3_3]: https://blog.naver.com/mynameisdj/223771086675

[^3_4]: https://maily.so/seanlee/posts/vpzl6e5mzk9

[^3_5]: https://cidermics.com/contents/detail/1601

[^3_6]: https://www.bizhankook.com/bk/article/16075

[^3_7]: https://www.hbrkorea.com/article/view/atype/di/category_id/1_1/article_no/637

[^3_8]: https://www.aitimes.kr/news/articleView.html?idxno=34810


---

# 커서와 마이크로 소프트

커서는 마이크로소프트 윈도우 운영체제에서 사용자 인터페이스의 핵심 요소 중 하나로, 마우스나 트랙패드 같은 포인팅 디바이스의 위치를 화면에 표시하는 작은 그래픽 요소입니다[^4_1]. 마이크로소프트는 윈도우 시스템에서 커서를 관리하고 제어하기 위한 포괄적인 API와 기능들을 제공하고 있습니다.

## **윈도우에서의 커서 시스템**

마이크로소프트 윈도우는 **Win32 API**를 통해 개발자들이 커서를 다룰 수 있는 다양한 기능을 제공합니다[^4_1]. 시스템은 마우스의 움직임에 따라 자동으로 커서의 위치를 업데이트하며, 커서가 가리키는 창과 연결된 커서 디자인을 자동으로 다시 그립니다[^4_2].

### **주요 커서 관리 기능**

마이크로소프트는 커서 관리를 위한 다양한 함수들을 제공합니다:

**위치 제어**: **GetCursorPos**와 **SetCursorPos** 함수를 통해 커서의 현재 화면 좌표를 가져오고 원하는 위치로 이동시킬 수 있습니다[^4_3][^4_2].

**모양 제어**: **GetCursor**와 **SetCursor** 함수를 사용하여 현재 커서의 핸들을 검색하고 커서의 모양을 변경할 수 있습니다[^4_3][^4_2].

**표시/숨김**: **ShowCursor** 함수는 내부 카운터를 사용하여 커서를 표시하거나 숨길 수 있으며, 카운터가 0 이상일 때만 커서가 화면에 표시됩니다[^4_3][^4_2].

## **커서 생성과 사용자 정의**

마이크로소프트는 개발자들이 **표준 커서**와 **사용자 정의 커서**를 모두 활용할 수 있도록 지원합니다[^4_4]. 표준 모래시계 커서는 `LoadCursor(NULL, IDC_WAIT)`로 간단히 로드할 수 있으며, 사용자 정의 커서는 리소스 파일에서 `LoadCursor(hinst, MAKEINTRESOURCE(240))`와 같은 방식으로 불러올 수 있습니다[^4_4].

더 나아가 **CreateCursor** 함수를 사용하면 런타임에 완전히 새로운 커서를 생성할 수도 있습니다[^4_4]. 이때 AND 마스크와 XOR 마스크를 정의하여 커서의 모양과 투명도를 세밀하게 제어할 수 있습니다.

## **고급 커서 기능**

### **커서 제한**

**ClipCursor** 함수를 통해 커서를 화면의 특정 사각형 영역으로 제한할 수 있습니다[^4_1][^4_3]. 이는 모달 대화상자에서 사용자가 다른 창과 상호작용하는 것을 방지하고 싶을 때 유용합니다.

### **커서 서비스**

마이크로소프트는 **OLE DB용 커서 서비스**도 제공합니다[^4_5]. 이는 데이터셋에 대한 클라이언트 계층과 중간 계층 캐시를 제공하며, 스마트 동기화 기능을 구현하여 네트워크 트래픽을 크게 줄이면서도 데이터 동기화에 대한 완전한 제어를 제공합니다.

마이크로소프트의 커서 시스템은 단순한 포인터 표시를 넘어서 사용자 경험을 향상시키고 개발자에게 유연한 제어 기능을 제공하는 포괄적인 솔루션으로 발전해왔습니다.

<div style="text-align: center">⁂</div>

[^4_1]: https://learn.microsoft.com/ko-kr/windows/win32/menurc/cursors

[^4_2]: https://learn.microsoft.com/ko-kr/windows/win32/menurc/about-cursors

[^4_3]: https://learn.microsoft.com/en-us/windows/win32/menurc/about-cursors

[^4_4]: https://learn.microsoft.com/ko-kr/windows/win32/menurc/using-cursors

[^4_5]: https://learn.microsoft.com/en-us/previous-versions/windows/desktop/ms722707(v=vs.85)

[^4_6]: https://apps.microsoft.com/detail/9nblggh4xjl7

[^4_7]: https://eacl.tistory.com/342

[^4_8]: https://answers.microsoft.com/ko-kr/windows/forum/all/윈도우/3dc5ed7e-5ab7-4e72-bbfb-465f9dfb8c2a

[^4_9]: https://www.microsoft.com/en-us/research/video/pointing-intelligent-environments-worldcursor-2/

[^4_10]: https://www.cursor.com


---

# 커서는 마이크로소프트가 매입했는가

제공된 검색 결과에는 마이크로소프트가 커서(Cursor)라는 회사나 기술을 매입했다는 정보가 포함되어 있지 않습니다. 검색 결과는 주로 마우스의 역사와 마이크로소프트의 마우스 개발, 그리고 윈도우 시스템의 커서 기능에 대한 내용만 다루고 있습니다.

마이크로소프트는 1983년에 최초로 상용화에 성공한 'Microsoft Mouse'를 출시했으며[^5_1][^5_3], 이는 MS워드와 호환되는 최초의 사용 마우스였습니다[^5_1]. 당시 200달러에 판매되었던 이 제품은 마우스의 대중화에 중요한 역할을 했습니다[^5_3].

1990년대에는 마이크로소프트가 인텔리마우스(IntelliMouse)를 개발하여 스크롤 휠을 도입하는 등 마우스 기술 개선에 기여했습니다[^5_2]. 또한 마이크로소프트는 윈도우 운영체제에서 커서를 관리하고 제어하기 위한 포괄적인 API와 기능들을 제공하고 있습니다[^5_8].

하지만 "커서"라는 이름의 특정 회사나 기술을 마이크로소프트가 인수했다는 내용은 현재 제공된 검색 결과에서는 확인할 수 없습니다.

<div style="text-align: center">⁂</div>

[^5_1]: https://blog.naver.com/mousestory/10181992719

[^5_2]: https://alpenglow92.tistory.com/entry/마우스의-역사에-대해서-알아보자

[^5_3]: https://news.samsungdisplay.com/7330

[^5_4]: https://blog.naver.com/crabbyreview/221390615993

[^5_5]: https://learn.microsoft.com/ko-kr/shows/history/history-of-microsoft-1988

[^5_6]: https://www.kmjournal.net/news/articleView.html?idxno=1179

[^5_7]: https://www.toolify.ai/ko/ai-news-kr/95-3349039

[^5_8]: https://learn.microsoft.com/ko-kr/windows/win32/menurc/cursors


---

# 프로그래밍 프로그램 커서와 마이크로 소프트

프로그래밍에서 **커서(Cursor)**는 마이크로소프트가 개발한 AI 기반 코드 에디터로, 기존의 Visual Studio Code를 기반으로 하여 인공지능 기능을 대폭 강화한 혁신적인 개발 도구입니다[^6_1]. 하지만 마이크로소프트가 커서를 직접 매입했다는 정보는 없으며, 커서는 **Anysphere Inc**라는 독립적인 응용 연구소에서 개발되고 있습니다[^6_1].

## **커서(Cursor) 프로그램의 개요**

커서는 Windows, macOS, Linux에서 사용할 수 있는 독점 소프트웨어로, 개발자의 생산성을 향상시키기 위해 고급 인공지능 기능을 코딩 환경에 직접 통합한 통합 개발 환경입니다[^6_1]. Visual Studio Code의 포크 버전으로 제작되어 기존 확장 프로그램과 설정을 그대로 사용할 수 있으면서도 AI 기능이 추가되었습니다[^6_1].

## **주요 기능과 특징**

### **AI 기반 코드 생성**

커서는 **자연어 명령**을 통해 코드를 생성할 수 있습니다[^6_1]. 개발자가 평범한 영어로 원하는 기능을 설명하면, 커서가 해당 코드를 자동으로 생성해줍니다. 예를 들어 "AWS SQS에서 메시지를 폴링하는 Python 함수를 작성해줘"라고 요청하면, 클라이언트 설정과 메시지 검색 로직을 포함한 완전한 함수를 생성합니다[^6_2].

### **스마트 코드 완성과 리팩토링**

커서는 단순한 자동완성을 넘어서 **복잡한 다중 라인 코드 구조**를 제안하고 리팩토링을 수행합니다[^6_1]. 루프를 리스트 컴프리헨션으로 변환하거나, 복잡한 조건문을 단순화하고, 사용하지 않는 변수를 제거하는 등의 코드 개선 작업을 자동으로 수행할 수 있습니다[^6_2].

### **코드베이스 인덱싱과 쿼리**

커서는 **전체 코드베이스를 인덱싱**하여 자연어로 쿼리할 수 있는 기능을 제공합니다[^6_1]. 이를 통해 개발자는 프로젝트 전체의 맥락을 이해하고 관련 코드를 쉽게 찾을 수 있습니다.

## **기술적 기반**

커서는 여러 AI 모델을 활용합니다[^6_2]:

- **GPT-4**와 **GPT-4 Turbo**
- **Claude**
- 자체 개발한 **"cursor-small"** 모델 (GPT-4보다 빠르지만 기능은 제한적)

사용자는 필요에 따라 이러한 모델들 사이를 전환할 수 있으며, 커서의 AI는 실시간으로 협업하면서 프로젝트의 맥락을 이해하고 정교한 코드 생성 및 편집을 제공합니다[^6_2].

## **마이크로소프트와의 관계**

마이크로소프트는 커서를 직접 매입하지 않았지만, 커서가 **Visual Studio Code를 기반**으로 만들어졌다는 점에서 간접적인 연관성이 있습니다[^6_1]. 커서는 VS Code의 모든 기능을 유지하면서 AI 기능을 추가한 형태로, 기존 VS Code 사용자들이 쉽게 전환할 수 있도록 설계되었습니다.

마이크로소프트는 자체적으로 다양한 **커서 관리 API**를 제공하고 있습니다. Win32 API를 통해 개발자들이 커서의 위치를 제어하고(`GetCursorPos`, `SetCursorPos`), 모양을 변경하고(`SetCursor`), 표시/숨김을 관리할 수 있는(`ShowCursor`) 기능들을 제공합니다[^6_3][^6_4].

## **업계 영향력**

커서는 Samsung, Replicate, Midjourney, Shopify, Perplexity 등 주요 기업의 엔지니어들이 사용하고 있으며[^6_2], 8세 아이가 45분 만에 챗봇을 구축할 수 있을 정도로 접근성이 뛰어나다는 평가를 받고 있습니다[^6_2]. 이는 소프트웨어 개발의 미래를 보여주는 혁신적인 도구로 인식되고 있습니다.

<div style="text-align: center">⁂</div>

[^6_1]: https://en.wikipedia.org/wiki/Cursor_(code_editor)

[^6_2]: https://daily.dev/blog/cursor-ai-everything-you-should-know-about-the-new-ai-code-editor-in-one-place

[^6_3]: https://learn.microsoft.com/ko-kr/windows/win32/api/winuser/nf-winuser-showcursor

[^6_4]: https://learn.microsoft.com/en-us/dotnet/desktop/winforms/input-mouse/how-to-manage-cursor-pointer

[^6_5]: https://jwprogramming.tistory.com/76

[^6_6]: https://learn.microsoft.com/ko-kr/dotnet/api/system.windows.forms.cursor?view=netframework-4.8

[^6_7]: https://learn.microsoft.com/ko-kr/dotnet/api/system.windows.forms.cursor?view=netframework-2.0

[^6_8]: https://learn.microsoft.com/en-us/windows/win32/menurc/using-cursors

[^6_9]: https://blog.naver.com/mousestory/10181992719

[^6_10]: https://www.10bestdesign.com/blog/history-of-the-mouse-cursor-we-know-and-love-today/

[^6_11]: https://learn.microsoft.com/en-us/dotnet/api/system.windows.forms.control.cursorchanged?view=windowsdesktop-9.0

[^6_12]: https://blog.naver.com/agapeuni/223854206375?fromRss=true\&trackingCode=rss

[^6_13]: https://news.samsungdisplay.com/7330

[^6_14]: https://en.wikipedia.org/wiki/Cursor_(user_interface)

[^6_15]: https://rh-cp.tistory.com/50

[^6_16]: https://learn.microsoft.com/ko-kr/sql/relational-databases/cursors?view=sql-server-ver17

[^6_17]: https://alpenglow92.tistory.com/entry/마우스의-역사에-대해서-알아보자

[^6_18]: https://www.lenovo.com/kr/ko/glossary/what-is-curser/

[^6_19]: https://justgo-developer.tistory.com/144

[^6_20]: https://rlagofls33.tistory.com/36

[^6_21]: https://blog.naver.com/PostView.nhn?isHttpsRedirect=true\&blogId=salinokl\&logNo=221453265426

[^6_22]: https://learn.microsoft.com/ko-kr/SQL/odbc/reference/develop-app/mixed-cursors?view=azure-sqldw-latest

[^6_23]: https://www.cursor.com

[^6_24]: https://www.cursor.com/downloads

[^6_25]: https://kr.aving.net/news/articleView.html?idxno=62504

[^6_26]: https://en.wikipedia.org/wiki/Cursor_(databases)

[^6_27]: https://cplusplus.com/forum/windows/215525/

[^6_28]: https://gizmodo.com/20-years-ago-microsoft-changed-how-we-mouse-forever-1834274151

[^6_29]: https://devblogs.microsoft.com/oldnewthing/20061121-15/?p=28943


---

# 커서는 원래 마이크로소프트가 개발한 것인가?

마소가 산게 아닌가?

커서(Cursor)는 마이크로소프트가 원래 개발한 것이 아니며, 마이크로소프트가 인수한 것도 아닙니다.

## **커서의 실제 개발사**

커서는 **Anysphere Inc**라는 독립적인 응용 연구소에서 개발된 AI 기반 코드 에디터입니다[^7_1]. 이 회사는 2022년에 설립되었으며, MIT 출신인 Michael Truell, Sualeh Asif, Arvid Lunnemark, Aman Sanger가 공동 창립했습니다[^7_2].

## **마이크로소프트와의 관계**

커서는 **Visual Studio Code의 포크 버전**으로 제작되었습니다[^7_1][^7_3]. 즉, 마이크로소프트의 오픈소스 코드 에디터인 VS Code를 기반으로 하여 AI 기능을 추가한 독립적인 제품입니다. VS Code가 오픈소스이기 때문에 누구나 이를 기반으로 새로운 제품을 만들 수 있습니다[^7_4].

## **인수 시도와 현재 상황**

흥미롭게도 **OpenAI가 커서를 인수하려고 시도했지만 실패**했습니다[^7_5]. 커서는 독립성을 유지하기를 원했고, 현재 약 **100억 달러 가치평가로 자금 조달**을 진행 중입니다[^7_5]. 커서의 연간 반복 수익(ARR)은 약 3억 달러에 달하며, 평균적으로 2개월마다 두 배씩 성장하고 있습니다[^7_5].

## **다른 커서 회사와의 혼동**

검색 결과에는 2019년에 **DataRobot이 인수한 "Cursor"**라는 다른 회사가 나타납니다[^7_6][^7_7]. 이는 데이터 협업 플랫폼을 제공하는 완전히 다른 회사로, 현재 인기 있는 AI 코드 에디터 커서와는 별개의 기업입니다.

따라서 현재 유명한 AI 코드 에디터 커서는 마이크로소프트가 개발하거나 인수한 것이 아니라, Anysphere라는 독립 스타트업이 VS Code를 기반으로 개발한 제품입니다.

<div style="text-align: center">⁂</div>

[^7_1]: https://en.wikipedia.org/wiki/Cursor_(code_editor)

[^7_2]: https://www.linkedin.com/posts/ai-market-watch_cursor-integrates-ai-into-the-coding-process-activity-7277090290312589333-DooH

[^7_3]: https://www.etcentric.org/new-ai-coding-app-cursor-gains-following-and-60m-in-funds/

[^7_4]: https://www.reddit.com/r/vscode/comments/1kjioho/why_is_microsoft_okay_with_cursor_and_windsurf/

[^7_5]: https://techcrunch.com/2025/04/22/why-openai-wanted-to-buy-cursor-but-opted-for-the-fast-growing-windsurf/

[^7_6]: https://www.biia.com/datarobot-acquires-cursor/

[^7_7]: https://aithority.com/machine-learning/datarobot-acquires-data-collaboration-platform-cursor/

[^7_8]: https://www.linkedin.com/posts/analytics-india-magazine_at-a-time-when-ai-is-reshaping-the-software-activity-7302976201642409985-fsGo

[^7_9]: https://techfundingnews.com/code-wars-openais-3b-bid-for-windsurf-puts-cursor-microsoft-and-anthropic-on-alert/

[^7_10]: https://www.linkedin.com/posts/aaditsh_heres-how-microsoft-quietly-took-the-lead-activity-7328441220580507649-uFj2

[^7_11]: https://www.cursor.com

[^7_12]: https://www.lennysnewsletter.com/p/the-rise-of-cursor-michael-truell

[^7_13]: https://www.linkedin.com/posts/svpino_prediction-microsoft-will-acquire-cursor-activity-7235399810982252544-6z0p

[^7_14]: https://www.datarobot.com/newsroom/press/datarobot-acquires-data-collaboration-platform-cursor/

[^7_15]: https://daily.dev/blog/cursor-ai-everything-you-should-know-about-the-new-ai-code-editor-in-one-place

[^7_16]: https://www.unite.ai/cursor-ai-rockets-to-9-9-billion-valuation-with-massive-900-million-raise/

[^7_17]: https://www.cursor.com/changelog

[^7_18]: https://www.youtube.com/watch?v=1-WnkSFFxmM

[^7_19]: https://ainativedev.io/news/microsofts-going-to-war

[^7_20]: https://www.productmarketfit.tech/p/how-did-cursor-grow-so-fast-1m-to


---

# 크롬에서 검색할 때 자꾸 야후가 뜨는 경우

크롬에서 검색할 때 자꾸 야후가 뜨는 현상은 주로 **브라우저 하이재커(Browser Hijacker)**라는 악성 소프트웨어 때문에 발생합니다[^8_1][^8_2]. 이는 야후 자체의 문제가 아니라 악성 프로그램이 브라우저 설정을 무단으로 변경하여 발생하는 문제입니다[^8_2].

## **주요 원인들**

### **브라우저 하이재커**

가장 흔한 원인으로, 악성 소프트웨어가 브라우저를 감염시켜 검색 엔진을 야후로 강제 변경합니다[^8_1][^8_2]. 이런 악성 프로그램은 보통 의심스러운 다운로드, 팝업 광고, 또는 악성 브라우저 확장 프로그램을 통해 설치됩니다[^8_2].

### **악성 확장 프로그램**

최근에 설치한 확장 프로그램이 브라우저 설정을 변경할 수 있습니다[^8_2][^8_3]. 사용자들은 "canislupusbaileyi"와 같은 악성 확장 프로그램이나 하이재킹된 Honey 확장 프로그램 때문에 문제가 발생했다고 보고했습니다[^8_3].

### **보안 소프트웨어**

McAfee와 같은 안티바이러스 소프트웨어가 기본 검색 엔진을 야후로 변경하는 경우도 있습니다[^8_3].

## **해결 방법**

### **1단계: 기본 검색 엔진 설정 변경**

크롬 우상단의 세 점 메뉴를 클릭하고 **설정 > 검색 엔진 > 검색 엔진 및 사이트 검색 관리**로 이동합니다[^8_4][^8_5]. 기본 검색 엔진에서 구글이나 원하는 검색 엔진을 선택하고, 야후가 있다면 삭제합니다[^8_4][^8_3].

### **2단계: 의심스러운 확장 프로그램 제거**

크롬 메뉴에서 **도구 더보기 > 확장 프로그램**으로 이동하여 설치된 확장 프로그램을 확인합니다[^8_2][^8_5]. 인식할 수 없거나 의심스러운 확장 프로그램은 즉시 제거합니다[^8_2][^8_5].

### **3단계: 전체 시스템 검사**

Norton과 같은 신뢰할 수 있는 안티바이러스 소프트웨어로 전체 시스템 검사를 실행하여 악성 프로그램을 탐지하고 제거합니다[^8_5]. 단순히 브라우저 설정을 초기화하는 것만으로는 근본적인 해결이 되지 않기 때문입니다[^8_5].

### **4단계: 브라우저 설정 초기화**

위의 방법들로도 해결되지 않으면 크롬 설정을 완전히 초기화하여 하이재커가 만든 변경사항을 되돌립니다[^8_2][^8_5].

## **예방 방법**

앞으로 이런 문제를 방지하려면 의심스러운 웹사이트에서 소프트웨어를 다운로드하지 않고, 팝업 광고를 클릭하지 않으며, 확장 프로그램을 설치할 때 신중하게 검토해야 합니다[^8_2]. 또한 정기적인 안티바이러스 검사를 통해 시스템을 보호하는 것이 중요합니다[^8_5].

<div style="text-align: center">⁂</div>

[^8_1]: https://support.google.com/websearch/thread/171272941/my-browser-keeps-changing-to-yahoo-and-its-really-pissing-me-off-so-fix-it-please

[^8_2]: https://vpnpro.com/best-antivirus-software/how-to-remove-yahoo-search-from-chrome/

[^8_3]: https://www.reddit.com/r/chrome/comments/15kyyrl/pc_chrome_google_chrome_keeps_changing_to_yahoo/

[^8_4]: https://support.google.com/chrome/thread/255167346/yahoo-search-engine

[^8_5]: https://www.wizcase.com/blog/how-to-remove-yahoo-redirect-from-chrome/

[^8_6]: https://nordvpn.com/blog/why-does-my-search-engine-keep-changing-to-yahoo/

[^8_7]: https://support.google.com/chrome/thread/315541128/issue-with-default-search-engine-automatically-changing

[^8_8]: https://www.youtube.com/watch?v=MpVZftw0I3A

[^8_9]: https://www.reddit.com/r/chrome/comments/1h3l1s2/understanding_the_browser_search_hijack_malware/

[^8_10]: https://www.yahoo.com/tech/remove-yahoo-search-google-chrome-181514660.html

[^8_11]: https://support.google.com/chrome/thread/235426739/how-to-stop-yahoo-from-being-the-default-search-enginer

[^8_12]: https://www.clrn.org/why-does-my-chrome-search-engine-keep-changing-to-yahoo/

[^8_13]: https://www.clrn.org/how-do-i-stop-yahoo-from-hijacking-my-browser-chrome/

[^8_14]: https://www.reddit.com/r/techsupport/comments/o8bpln/how_do_i_get_rid_of_the_yahoo_search_function_on/

[^8_15]: https://www.youtube.com/watch?v=ucZgZVfoePE

[^8_16]: https://www.youtube.com/watch?v=B5KMzu9jG_U

[^8_17]: https://www.safetydetectives.com/blog/how-to-remove-yahoo-redirect-from-chrome/

[^8_18]: https://www.youtube.com/watch?v=aght-sAWyr0


---

# x86 x64 차이

x86과 x64는 컴퓨터 프로세서의 **아키텍처(설계 방식)**를 나타내는 용어로, 가장 큰 차이는 **비트 수**에 있습니다. x86은 32비트, x64는 64비트 아키텍처를 의미합니다[^9_1].

## **기본 개념**

**x86 아키텍처**는 1978년 인텔의 8086 프로세서에서 유래된 32비트 기반 설계입니다[^9_5]. **x64 아키텍처**는 AMD에서 2003년에 개발한 64비트 확장 아키텍처로, 정식 명칭은 x86-64 또는 AMD64입니다[^9_1][^9_8].

## **주요 차이점**

### **메모리 처리 능력**

x86은 최대 **4GB의 메모리**만 인식할 수 있는 반면, x64는 이론적으로 **16엑사바이트**까지 처리 가능합니다[^9_1][^9_5]. 이는 x86의 32비트 주소 공간(2³² = 4,294,967,296 바이트)과 x64의 64비트 주소 공간(2⁶⁴ 바이트)의 차이 때문입니다[^9_1].

### **레지스터 크기와 개수**

x86은 32비트 레지스터(EAX, EBX 등)를 사용하지만, x64는 64비트 레지스터(RAX, RBX 등)로 확장되었습니다[^9_5]. 또한 x64는 8개의 추가 일반 레지스터(R8~R15)를 제공하여 더 효율적인 데이터 처리가 가능합니다[^9_5].

### **데이터 처리 성능**

x86은 한 번에 4바이트(32비트) 데이터를 처리하는 반면, x64는 8바이트(64비트) 데이터를 동시에 처리할 수 있어 **더 빠른 연산 속도**를 제공합니다[^9_5].

## **호환성**

x64 아키텍처는 **하위 호환성**을 유지합니다[^9_3][^9_6]. 즉, 64비트 시스템에서도 32비트 프로그램을 실행할 수 있습니다. 64비트 윈도우에서 32비트 프로그램은 "C:\Program Files (x86)\" 폴더에 설치되고, 64비트 프로그램은 "C:\Program Files\" 폴더에 설치됩니다[^9_1].

## **실제 사용에서의 차이**

### **소프트웨어 설치**

- **x86 프로그램**: 32비트 프로그램으로, 메모리 사용량이 제한적
- **x64 프로그램**: 64비트 프로그램으로, 더 많은 메모리 활용 가능


### **성능 차이**

x64는 더 큰 메모리 공간, 추가 레지스터, 확장된 명령어 집합(SSE2, AVX 등)을 통해 **벡터 연산과 병렬 처리**에서 뛰어난 성능을 보입니다[^9_5].

## **현재 상황**

현재 대부분의 데스크톱과 서버는 x64 아키텍처를 사용하고 있으며, AMD의 애슬론, 셈프론, 페넘 시리즈와 인텔의 코어 i3, i5, i7 등이 모두 x86-64 아키텍처를 기반으로 합니다[^9_1]. 이 기술의 원천은 AMD가 보유하고 있으며, 인텔은 2004년 AMD와 라이선스 협약을 통해 이 기술을 사용하게 되었습니다[^9_1].

<div style="text-align: center">⁂</div>

[^9_1]: https://blog.naver.com/PostView.nhn?blogId=mumasa\&logNo=221049608979

[^9_2]: https://blog.naver.com/PostView.naver?blogId=cjs0308cjs\&logNo=223242935705

[^9_3]: https://ts2ree.tistory.com/355

[^9_4]: https://velog.io/@480/이제는-개발자도-CPU-아키텍처를-구분해야-합니다

[^9_5]: https://ko.ittrip.xyz/c/c-lang-x86-x86_64-differences

[^9_6]: https://www.lenovo.com/kr/ko/glossary/x86/

[^9_7]: https://moonsonghada.tistory.com/36

[^9_8]: https://ko.wikipedia.org/wiki/X86-64

[^9_9]: https://www.reddit.com/r/asm/comments/121zq4c/what_is_the_difference_between_intel_x8664_and/?tl=ko


---

# Manipulation 어근을 나눠 단어를 이해하기 쉽게 접근

"Manipulation"이라는 단어를 어근별로 나누어 쉽게 이해해보겠습니다.

## **어근 분석**

**Manipulation = Manu + pul + ation**

### **Manu (손)**

- 라틴어 "manus"에서 유래
- "손"을 의미하는 어근
- 관련 단어: manual(수동의), manufacture(제조하다), manuscript(원고)


### **Pul (채우다, 가득하게 하다)**

- 라틴어 "plere"에서 유래된 "pul"
- "채우다, 가득하게 하다"의 의미
- 관련 단어: populate(인구를 채우다), replenish(다시 채우다)


### **-ation (명사 접미사)**

- 동작이나 상태를 나타내는 명사형 접미사
- "~하는 행위, ~한 상태"를 의미


## **단어의 의미 형성 과정**

**Manu (손) + pul (채우다) + ation (행위)**
= **"손으로 가득 채우는 행위"**
= **"손으로 다루는 행위"**
= **"조작, 조종"**

## **의미의 확장**

### **물리적 의미**

- 손으로 물건을 다루고 조작하는 것
- 기계나 도구를 손으로 조작하는 것


### **추상적 의미**

- 사람의 마음이나 상황을 교묘하게 조종하는 것
- 정보나 데이터를 의도적으로 변경하는 것


## **관련 단어들**

**같은 어근을 가진 단어들:**

- **Manipulate** (동사): 조작하다, 조종하다
- **Manipulator** (명사): 조작하는 사람, 조종자
- **Manipulative** (형용사): 조작적인, 교묘한

**Manu 어근 단어들:**

- **Manual**: 손으로 하는, 설명서
- **Manufacture**: 손으로 만들다 → 제조하다
- **Manicure**: 손톱 관리
- **Emancipate**: 손에서 벗어나게 하다 → 해방시키다

이렇게 어근을 분석하면 "manipulation"이 원래 "손으로 무언가를 다루는 행위"에서 시작되어 현재의 "조작, 조종"이라는 의미로 발전했음을 알 수 있습니다.

---

# 스키마

스키마(Schema)는 **데이터베이스의 구조와 제약조건에 관한 전반적인 명세를 기술한 것**으로, 쉽게 말해 데이터베이스 내에 어떤 구조로 데이터가 저장되는지를 나타내는 데이터베이스의 설계도라고 할 수 있습니다[^11_1].

## **스키마의 기본 개념**

스키마는 **메타데이터(데이터에 대한 데이터)**의 집합으로, 다음과 같은 요소들을 포함합니다[^11_2]:

- **개체(Entity)**: 데이터로 표현하려는 객체 (예: 학생, 과목)
- **속성(Attribute)**: 개체의 특성을 나타내는 요소 (예: 이름, 학번, 성적)
- **관계(Relationship)**: 개체 간의 연관성 (예: 학생과 과목 간의 "수강" 관계)
- **제약조건**: 데이터가 유지해야 할 규칙들


## **스키마의 주요 특징**

스키마는 **데이터 사전(Data Dictionary)**에 저장되며, 시간에 따라 불변인 특성을 가집니다[^11_1][^11_3]. 또한 현실 세계의 특정 부분을 표현하기 위해 특정 데이터 모델을 이용하여 만들어집니다[^11_2].

## **스키마의 3계층 구조**

데이터베이스 스키마는 사용자의 관점에 따라 3단계로 구분됩니다[^11_4]:

### **외부 스키마 (External Schema)**

- **사용자 뷰**라고도 불리며, 개별 사용자나 응용 프로그래머가 필요로 하는 데이터베이스의 논리적 구조를 정의합니다[^11_5]
- 하나의 데이터베이스에 여러 개의 외부 스키마가 존재할 수 있으며, **서브 스키마**라고도 합니다[^11_5]
- 사용자나 응용프로그램이 데이터베이스에 접근할 수 있는 **인터페이스 역할**을 합니다[^11_5]


### **개념 스키마 (Conceptual Schema)**

- 데이터베이스의 **전체적인 논리적 구조**를 나타내며, 조직 전체의 관점에서 데이터베이스를 정의한 것입니다[^11_4]
- **DBA(데이터베이스 관리자)**에 의해 구성되며, 데이터베이스당 **하나만 존재**합니다[^11_6]
- 모든 응용 프로그램이나 사용자들이 필요로 하는 데이터를 종합한 조직 전체의 데이터베이스입니다[^11_5]


### **내부 스키마 (Internal Schema)**

- **물리적 저장장치의 관점**에서 본 데이터베이스 구조로, 실제 데이터가 저장되는 물리적 구조를 정의합니다[^11_4]
- 저장 데이터 항목의 표현방법, 내부 레코드의 물리적 순서, 인덱스 유무 등을 명세합니다[^11_6]
- **시스템 프로그래머나 시스템 설계자**가 보는 관점의 스키마입니다[^11_6]


## **스키마의 역할과 중요성**

스키마는 다음과 같은 중요한 역할을 수행합니다[^11_7]:

- **데이터 구조 정의**: 데이터베이스 내의 모든 데이터 구조를 명확하게 정의
- **데이터 무결성 유지**: 제약 조건과 규칙을 설정하여 데이터의 정확성 보장
- **데이터베이스 관리**: 개발자나 DBA가 데이터 구조를 설계하고 유지보수할 수 있도록 지원

스키마는 데이터베이스의 **"청사진"**으로서 데이터가 다른 테이블이나 데이터 모델과 어떻게 관련될 수 있는지 설명하지만, 실제 데이터는 포함하지 않습니다[^11_8]. 이러한 스키마 설계 과정을 **데이터 모델링**이라고도 합니다[^11_8].

<div style="text-align: center">⁂</div>

[^11_1]: https://jwprogramming.tistory.com/47

[^11_2]: https://iingang.github.io/posts/DB-schema/

[^11_3]: https://code-lab1.tistory.com/114

[^11_4]: https://minimax95.tistory.com/entry/데이터베이스-구성-요소와-스키마-개념-정리

[^11_5]: https://star7sss.tistory.com/815

[^11_6]: https://velog.io/@msung99/데이터베이스와-스키마Schema

[^11_7]: https://www.devkobe24.com/DB/2024-10-17-schema.html

[^11_8]: https://www.ibm.com/kr-ko/topics/database-schema

[^11_9]: https://blog.naver.com/renee1009/40137140604

[^11_10]: https://velog.io/@chlvlftn22/스키마-Schema

[^11_11]: https://blog.skby.net/데이터베이스-스키마schema/

[^11_12]: https://brunch.co.kr/@@9T8i/11

[^11_13]: https://cyyyummy.tistory.com/18

[^11_14]: https://y-oni.tistory.com/75

[^11_15]: https://www.youtube.com/watch?v=ho42XWNCKY8

[^11_16]: https://wallyyoucandoit.tistory.com/34

[^11_17]: https://grit1972.tistory.com/entry/스키마-이론-인지심리학의-흥미로운-세계

[^11_18]: https://ykcb.tistory.com/entry/데이터베이스-스키마의-개념-특징

[^11_19]: https://velog.io/@loocia1910/개인-프로젝트-DB-스키마-작성

[^11_20]: https://www.hedleyonline.com/ko/blog/스키마/

[^11_21]: https://fomaios.tistory.com/entry/Database-스키마Schema란-feat-외부-스키마개념-스키마내부-스키마

[^11_22]: https://ko.wikipedia.org/wiki/스키마

[^11_23]: https://velog.io/@hiy7030/DB-스키마Scehma

[^11_24]: https://blog.naver.com/tntbyj/221917402075

[^11_25]: https://seohee-ha.tistory.com/208

[^11_26]: https://lifeinsights.co.kr/entry/교육심리학의-인지론-중-스키마-이론의-개념과-그-역할


---

# Abacus ai

Abacus.AI는 **"세계 최초의 AI 슈퍼 어시스턴트"**를 표방하는 샌프란시스코 기반의 클라우드 기반 인공지능 플랫폼으로, 기업들이 AI 시스템과 에이전트를 구축하고 배포할 수 있도록 지원하는 종합적인 데이터 사이언스 및 MLOps 플랫폼입니다[^12_1][^12_2].

## **회사 개요**

Abacus.AI는 원래 Reality Engines라는 이름으로 시작되었으며, 현재 CEO는 Bindu Reddy입니다[^12_3]. 이 회사는 Eric Schmidt(구글 CEO), Ram Shriram(전 아마존 임원), Jerry Yang(야후 공동창립자) 등 기술계 유명 인사들의 개인 투자와 함께 Coatue, Index Partners, Decibel Ventures 등으로부터 총 **4,050만 달러의 투자**를 받았습니다[^12_3].

## **주요 제품**

### **ChatLLM Teams**

GPT-4o, GPT-o1, Claude Sonnet, Haiku 3.5, Llama 3 등 **최첨단 LLM 모델들에 대한 접근**을 제공합니다[^12_1]. 문서 분석, 코드 생성 및 편집, 이미지 생성 등의 기능을 포함하여 다양한 비즈니스 요구사항에 대한 솔루션을 제공합니다[^12_1].

### **Abacus.AI Enterprise**

비즈니스의 **"AI 두뇌"** 역할을 하며, 프로세스 자동화, 예측, 개인화 등을 담당합니다[^12_1]. AI 에이전트 구축 기능과 개인화된 프로모션이나 판매 예측 같은 맞춤형 AI 도구를 제공합니다[^12_1].

## **핵심 기능**

### **자동화된 AI 개발**

**신경 아키텍처 검색(Neural Architecture Search)** 기술을 사용하여 딥러닝 프로그램이 주어진 작업에 최적화된 신경망 아키텍처를 자동으로 찾아줍니다[^12_3]. 이는 사람이 직접 아키텍처를 설계할 필요 없이 푸시 버튼 방식으로 AI 프로그램을 훈련, 테스트, 배포할 수 있게 해줍니다[^12_3].

### **포괄적인 AI 도구**

- **개인화**: 고객 맞춤형 추천 시스템
- **예측**: 이탈 예측, 시계열 예측
- **자연어 처리**: 감정 분석, 언어 생성
- **이상 탐지**: 사기 탐지, 보안
- **Vision AI**: 이미지 업로드 및 자동 라벨링[^12_1][^12_4]


### **실시간 처리**

실시간 데이터 파이프라인을 지원하여 스트리밍 데이터의 실시간 시각화와 예측 분석을 제공합니다[^12_4].

## **모듈형 서비스**

Abacus.AI는 **"Abacus.ai Deconstructed"**라는 이름으로 모듈형 서비스를 제공합니다[^12_3]:

- **모델 호스팅 및 모니터링**: 자체 개발 모델이나 기존 모델을 호스팅하고 모니터링
- **편향 제거**: 머신러닝 모델에서 연령, 성별, 인종 편향을 제거
- **Feature Store**: 모델을 위한 데이터 준비 및 스테이징 시설[^12_3]


## **성과와 현황**

Abacus.AI는 **Fortune 500 기업들**에 의해 채택되었으며, 주요 지표에서 **5-20%의 개선**을 달성했다고 보고되고 있습니다[^12_5]. 플랫폼의 MLOps 인프라는 사용자들이 다른 플랫폼보다 **10배 빠르게 시장에 진출**할 수 있도록 지원합니다[^12_2].

2025년 7월 기준으로 **370만 방문자**를 기록하며 **7.5% 증가**를 보였는데, 이는 5월에 출시된 **Deep Agent** 기능과 저렴한 올인원 AI 기능들이 기여한 것으로 분석됩니다[^12_5].

스탠포드와 MIT 등 명문대 출신의 AI 과학자와 ML 엔지니어들로 구성된 팀을 보유하고 있으며, NeurIPS 컨퍼런스에서 신경 아키텍처 검색과 신경망 편향 제거에 관한 연구 논문을 발표하는 등 딥러닝 과학 분야의 기초 연구도 수행하고 있습니다[^12_3].

<div style="text-align: center">⁂</div>

[^12_1]: https://originality.ai/blog/abacus-ai-review

[^12_2]: https://serp.ai/tools/abacus/

[^12_3]: https://www.zdnet.com/article/ai-startup-abacus-ai-nabs-22-million-in-series-b-funding-to-automate-creation-of-deep-learning-models/

[^12_4]: https://www.gate2ai.com/tools/developer-tools/abacus-ai

[^12_5]: https://aipure.ai/products/abacus-ai/features

[^12_6]: https://abacus.ai

[^12_7]: https://x.com/abacusai

[^12_8]: https://www.forbes.com/companies/abacusai/

[^12_9]: https://www.reddit.com/r/ChatGPTPro/comments/1erepsl/any_opinions_on_abacusai/

[^12_10]: https://gptonline.ai/abacus/


---

# GPT-4o, GPT-o1, Claude Sonnet, Haiku 3.5, Llama 3 등 최첨단 LLM 모델들에 대한 접근을 제공합니다

위의 내용처럼 perplexity도 여러 llm엔진에 대한 접근을 제공하는데
어떤 경로로 어떻게 계약을 체결해서 고객에게 제공되는지 과정이 궁금해

Perplexity가 여러 LLM 엔진에 대한 접근을 제공하는 과정은 **"Frenemies(프레너미) 전략"**이라고 불리는 독특한 비즈니스 모델을 통해 이루어집니다.

## **Perplexity의 LLM 통합 전략**

Perplexity는 다른 AI 회사들과 달리 **최고의 모델을 만드는 것보다 최고의 인터페이스가 되는 것**에 집중했습니다[^13_1]. 경쟁사들이 모델 우위를 위해 싸우는 동안, Perplexity는 조용히 연결된 LLM 생태계의 제어판을 구축하고 있습니다[^13_1].

### **통합된 모델들**

현재 Perplexity 플랫폼에서 제공되는 주요 모델들은 다음과 같습니다:

- **GPT-4o, GPT-o1** (OpenAI)
- **Claude Sonnet, Haiku 3.5** (Anthropic)
- **Llama 3** (Meta)
- **Gemini** (Google)
- **Grok** (xAI)
- **Sonar** (Perplexity 자체 모델)


## **계약 체결 과정**

### **API 파트너십 모델**

Perplexity는 각 AI 회사들과 **API 접근 계약**을 체결합니다. 이는 통합이 아닌 **동등한 파트너로서의 관계**를 의미합니다[^13_1]. 각 모델 제공업체는 Perplexity 플랫폼 내에서 자신들의 모델을 옵션으로 제공하게 됩니다.

### **수익 공유 구조**

Perplexity는 **Publishers' Program**에서 보여준 것처럼 수익 공유 모델을 활용합니다[^13_2][^13_3]. 사용자가 특정 모델을 사용할 때 발생하는 수익의 일부를 해당 모델 제공업체와 공유하는 방식으로 운영됩니다.

## **고객 제공 과정**

### **통합 플랫폼 제공**

고객들은 Perplexity 하나의 인터페이스를 통해 여러 LLM 모델에 접근할 수 있습니다. 이는 **ChatLLM Teams** 서비스를 통해 제공되며[^13_2], 사용자는 필요에 따라 다양한 모델 간을 전환할 수 있습니다.

### **API 접근**

Perplexity는 **PPLX API**를 통해 개발자들에게도 이러한 다중 모델 접근을 제공합니다[^13_4][^13_5]. 개발자들은 `@ai-sdk/perplexity` 모듈을 통해 이러한 기능을 자신들의 애플리케이션에 통합할 수 있습니다[^13_5].

## **전략적 이점**

### **사용자 선택권 극대화**

Perplexity의 이 전략은 **"사용자 선택권을 궁극적인 파워 플레이로 만드는 것"**입니다[^13_1]. 사용자들은 특정 작업에 가장 적합한 모델을 선택할 수 있으며, Perplexity는 이러한 선택의 중심에 위치하게 됩니다.

### **생태계 중앙화**

경쟁사들을 **"테넌트(임차인)"**로 만들면서 Perplexity는 LLM 생태계의 중앙화를 이루고 있습니다[^13_1]. 이는 단순히 가장 똑똑한 모델이 되는 것보다 **가장 똑똑한 인터페이스**가 되는 전략입니다[^13_1].

이러한 접근 방식을 통해 Perplexity는 AI 웹의 **"프론트 도어"** 역할을 하며, 사용자들이 가장 많이 상호작용하는 레이어이자 궁극적으로 승리하는 레이어로 자리매김하고 있습니다[^13_1].

<div style="text-align: center">⁂</div>

[^13_1]: https://avenuez.com/blog/perplexitys-frenemies-strategy-integrates-competitor-llms/

[^13_2]: https://www.perplexity.ai/hub/blog/introducing-the-perplexity-publishers-program

[^13_3]: https://www.techtarget.com/searchenterpriseai/news/366599602/Perplexity-AI-revenue-share-model-appeases-publishers

[^13_4]: https://www.perplexity.ai/hub/blog/introducing-pplx-online-llms

[^13_5]: https://sdk.vercel.ai/providers/ai-sdk-providers/perplexity

[^13_6]: https://opentools.ai/news/nvidia-and-perplexity-forge-alliance-to-develop-sovereign-llms-in-eu-and-middle-east

[^13_7]: https://startupnews.fyi/2023/11/29/perplexity-ai-introduces-new-online-llms-for-real-time-information-access/

[^13_8]: https://www.perplexity.ai/hub/legal/terms-of-service

[^13_9]: https://www.linkedin.com/pulse/breaking-search-framework-perplexity-ai-your-knowledge-engine-deqlc

[^13_10]: https://paperswithcode.com/paper/pack-of-llms-model-fusion-at-test-time-via


---

# 토픽

빅테크기업
인공지능(AI)
모빌리티
푸드테크
헬스케어
리테일/커머스
스타트업
정보보안
미디어/엔터테인먼트
SaaS/클라우드
핀테크/에듀테크
제조/하드웨어
전체 기사 보기
투자
CEO 플레이북
더밀크 TV
최신비디오
혁신원정대
인자기(사람,돈,기술 이야기)
크리스의 뉴욕 시그널
더밀크 아카데미
더웨이브/트렌드쇼
밸리토크
리서치
이벤트
CES
2025
전체기사
비디오
역사 및 개요
필드 가이드
CES2025 with TheMiilk
로그인
회원가입
Search
미국대전환
FDA
AI AGENT
미국의 AI 행정 혁명 ... FDA, AI '엘사' 직접 개발, 도입 완료
reporter-profile
권순우
2025.06.26 00:59 PDT

북마크 하기

미국의 AI 행정 혁명 ... FDA, AI '엘사' 직접 개발, 도입 완료
(출처 : Genspark)
[미국대전환] AI 행정 혁명
예산 4% 삭감 앞두고 전격 도입... AI로 심사 속도 3일에서 6분으로 줄여
왜 신약 하나 승인까지 10년이나 걸려야 하는가?에 의문.
FDA 내부 칸막이(사일로) 심각. AI 도입으로 행정 비효율 획기적 전환 시도.
공공부문 AI 혁신 더 빨라질 듯... 일자리 감축, 교육 시스템 보완 등 과제

미국이 경제 및 산업 전 영역에서 AI 대전환(AI Transformation)을 진행하고 있는 가운데 미국에서도 대표적 '규제 기관'으로 인식되는 미 식품의약국(FDA)가 생성AI 기술 도입에 박차를 가하고 있다. AI 에이전트로 규제 심사의 속도를 높이겠다는 것. 전체 미국내 공무원 조직에 까지 확산될지 주목된다.

FDA는 자체 개발한 AI 에이전트 '엘사(Elsa)'를 예정보다 크게 앞당겨서 6월 말 내로 전사적인 AI 도입을 완료하겠다고 발표했다.

미국 FDA의 엘사(Evidentiary Learning and Synthesis Agent, Elsa)는 대형 언어 모델(LLM)인 GPT-4 기반으로 FDA가 직접 개발한 AI 도구다. 지난 6월 2일 공식적으로 출시된 엘사는 FDA 내부의 고보안 고브클라우드(GovCloud) 환경에서 설계·구축됐으며 과학적 검토자와 현장 조사관 등 다양한 FDA 직원들이 복잡한 데이터 집약적 업무를 효율적으로 처리할 수 있도록 지원한다.

FDA는 '엘사'가 이미 임상 프로토콜 검토와 과학적 평가, 점검 우선순위 선정 등 다양한 분야에서 활용되고 있다고 밝혔다.

마틴 마카리 FDA 국장(커미셔너, 최고책임자)는 성명에서 “시범 운영을 성공적으로 마쳤다"면서 "6월 30일까지 전사적인 AI 도입을 목표로 삼았다”고 밝혔다. 또 "심사관들이 더 빠르고 정확하게 규제 결정을 내릴 수 있을 것"이라고 기대감을 내비쳤다.

회원가입 후 뷰스레터를
주 3회 무료로 받아보세요!
단순 뉴스 서비스가 아닌 세상과 산업의 종합적인 관점(Viewpoints)을 전달드립니다. 뷰스레터는 주 3회(월, 수, 금) 보내드립니다.

회원가입 하기
더밀크가 엄선한 리포트

더밀크 AIR 15호: 이제는 AI-able 시대
기업 고객을 위한 프리미엄 보고서: A.I.R.

더밀크 AIR 15호: 이제는 AI-able 시대

자세히 보기
더밀크 AIR 14호: 구글이 돌아왔다… AI, 꿈을 현실로
기업 고객을 위한 프리미엄 보고서: A.I.R.

더밀크 AIR 14호: 구글이 돌아왔다… AI, 꿈을 현실로

자세히 보기
[GTC 특집] 엔비디아, 왕조시대를 선언하다
기업 고객을 위한 프리미엄 보고서: A.I.R.

[GTC 특집] 엔비디아, 왕조시대를 선언하다

자세히 보기
회사소개
자주 묻는 질문
더밀크 기업구독 안내
더밀크 리서치 서비스 안내
이용약관
개인정보처리방침

2905 Homestead Rd,
Santa Clara, CA 95051
© The Miilk. All rights reserved.

---

위 기사의 내용을 it용어를 모르는사람이 이해하기 쉽게 풀어설명해ㅜ저

미국 정부 기관인 FDA(식품의약국)가 AI를 활용해 업무 혁신을 이뤄낸 사례를 쉽게 설명드리겠습니다.

## **FDA가 뭐하는 곳인가요?**

FDA는 미국에서 **음식과 약을 안전하게 관리하는 정부 기관**입니다. 새로운 약이 나오면 "이 약이 정말 안전한지, 효과가 있는지"를 꼼꼼히 검사해서 승인해주는 곳이에요. 마치 **"약의 품질검사소"** 같은 역할을 합니다.

## **기존에 어떤 문제가 있었나요?**

### **너무 오래 걸리는 심사**

- 새로운 약 하나를 승인받는데 **10년**이나 걸렸습니다
- 서류 검토만 해도 **2-3일**씩 소요되었습니다
- 약이 필요한 환자들은 그동안 기다려야 했죠


### **복잡한 업무**

FDA 직원들은 매일 엄청난 양의 서류를 읽고, 요약하고, 분석해야 했습니다. 마치 도서관 사서가 하루에 수백 권의 책을 정리해야 하는 것과 같았어요.

## **'엘사(Elsa)'가 뭔가요?**

**엘사는 FDA가 직접 만든 AI 비서**입니다. 정식 이름은 "Evidentiary Learning and Synthesis Agent"인데, 쉽게 말하면 **"증거를 학습하고 정리해주는 AI 도우미"**라는 뜻입니다.

### **엘사가 하는 일**

- **서류 읽기**: 복잡한 의학 문서를 빠르게 읽고 이해
- **요약하기**: 긴 보고서를 짧게 정리해서 핵심만 추려냄
- **부작용 분석**: 약의 부작용 사례들을 정리하고 분석
- **우선순위 정하기**: 어떤 검사를 먼저 해야 할지 판단


## **얼마나 빨라졌나요?**

가장 놀라운 변화는 **속도**입니다:

- **기존**: 서류 검토에 2-3일 소요
- **엘사 도입 후**: 같은 작업을 **6분**에 완료

이는 마치 손으로 계산하던 것을 계산기로 하게 된 것과 같은 혁신입니다.

## **어떻게 안전하게 만들었나요?**

### **보안 시스템**

엘사는 **"고브클라우드(GovCloud)"**라는 정부 전용 보안 시스템에서 작동합니다. 이는 마치 **은행 금고처럼 보안이 철저한 컴퓨터 환경**이라고 생각하시면 됩니다.

### **기밀 보호**

- 제약회사들이 제출한 비밀 연구 자료는 AI 학습에 사용하지 않음
- 모든 정보가 FDA 내부에서만 처리됨
- 외부로 정보가 새어나갈 위험을 차단


## **왜 이런 변화가 중요한가요?**

### **환자들에게 도움**

약 승인이 빨라지면 **새로운 치료법을 더 빨리 받을 수 있습니다**. 특히 희귀병이나 암 환자들에게는 시간이 생명과 직결되기 때문입니다.

### **비용 절약**

AI 도입으로 **예산도 절약**되었습니다. 마틴 마카리 FDA 국장은 "예정보다 빠르고 예산보다 적게 들었다"고 발표했습니다.

### **정부 혁신의 시작**

FDA의 성공 사례가 다른 정부 기관들에도 확산될 가능성이 높습니다. 이는 **"AI 정부"**의 시작을 알리는 신호로 해석됩니다.

## **앞으로 어떻게 될까요?**

FDA는 엘사가 **"AI 시대의 시작"**이라고 표현했습니다. 앞으로 더 많은 정부 업무에 AI가 도입되어 **더 빠르고 정확한 공공서비스**를 제공할 것으로 예상됩니다.

이는 마치 **"디지털 정부"**로의 전환을 의미하며, 시민들은 더 나은 서비스를 더 빠르게 받을 수 있게 될 것입니다.

<div style="text-align: center">⁂</div>

[^14_1]: https://www.fda.gov/news-events/press-announcements/fda-launches-agency-wide-ai-tool-optimize-performance-american-people

[^14_2]: https://www.themiilk.com/articles/a63b0bad7

[^14_3]: https://www.techtarget.com/pharmalifesciences/news/366625270/FDA-launches-gen-AI-Elsa-to-support-clinical-regulatory-tasks

[^14_4]: https://www.fastcompany.com/91345171/new-ai-tool-food-drug-administration-promises-speed-up-scientific-reviews

[^14_5]: https://babl.ai/fda-launches-ai-tool-elsa-to-streamline-operations-and-boost-efficiency/

[^14_6]: https://www.drugdiscoverytrends.com/why-fdas-elsa-ai-tool-was-inevitable-and-just-the-beginning/

[^14_7]: https://uk.moyens.net/ai/fda-unveils-generative-ai-tool-elsa-ahead-of-schedule/

[^14_8]: https://www.vcsolutions.com/blog/fda-elsa-ai-transforming-drug-approval-efficiency/

[^14_9]: https://www.linkedin.com/posts/fda_today-the-fda-launched-elsa-a-generative-activity-7335385222651265024-hTqY

[^14_10]: https://insider.thefdagroup.com/p/fda-elsa-ai-inspections


---

# 본문 바로가기

주간조선
구독
주요뉴스
정치
경제
생활
사회
세계
IT
랭킹
주간조선PICK 안내
살 안 찌고 단맛만 내는 '완벽한 설탕' 만든다
입력2025.06.23. 오전 5:00 기사원문
27
29
본문 요약봇
텍스트 음성 변환 서비스 사용하기
글자 크기 변경하기
SNS 보내기
인쇄하기
photo 게티이미지
photo 게티이미지

사람은 본능적으로 단맛을 좋아한다. 포도당이 우리 몸의 기본 에너지원이기에, 우리가 단맛을 느낄 수 있다는 점을 에너지원을 감각하는 역량으로 볼 수도 있다. 이를 적나라하게 보여주는 게 단맛을 섭취했을 때 뇌가 보이는 반응이다. 뇌는 단맛을 느낄 때마다 도파민을 분비해 행복감을 만든다. 사람이 단맛에 탐닉하게 되는 근본적 이유다.

그렇지만 현대에 와선 이 본능이 해가 되고 있어 문제다. 다수의 현대인은 이미 필요한 에너지보다 훨씬 많은 열량을 섭취하고 있다. 그런데 단맛이 주는 행복감 탓에 열량을 과잉 섭취하는 일이 잦아지면 비만과 당뇨병 같은 대사질환을 불러올 수밖에 없다. 혹자는 이를 영화 '아가씨'의 명대사를 빌려 이렇게 표현하기도 했다. 내 인생을 망치러 온 나의 구원자, 설탕이라고.

단맛은 즐기고 싶지만, 살이 찌고 싶진 않다는 욕망은 모순적이다. 원래라면 그리스 비극과 같은 파국을 맞는 게 정상이지만, 인류는 기어코 열량은 없이 단맛만 느껴지는 인공감미료(甘味料)를 개발하는 데 성공했다. 설탕보다 훨씬 더 달지만, 열량은 거의 없으니 말 그대로 책임 없는 쾌락이다. 인공감미료의 개발 덕분에 제로칼로리 탄산음료, 저당 아이스크림, 무설탕 과자 같은 게 출시될 수 있었다. 그런데 인공감미료나 설탕과 같은 자연 당(糖)의 미묘한 맛 차이를 섬세하게 구별해내는 사람들도 있다. 인공감미료가 단맛을 내긴 하나, 설탕과 완벽히 일치되는 단맛을 만드는 건 아니라서다. 그렇다면 이걸 개량할 방법은 없을까. 안타깝게도 최근까지는 그럴 수단이 없었다.

우연히 찾아낸 인공감미료

세계 최초의 인공감미료인 사카린을 찾아낸 실험은 애초에 '감미료 개발'이 목적이 아니었다. 19세기 말 러시아 화학자 콘스탄틴 팔베르크(Constantin Fahlberg)는 콜타르 합성 실험을 마친 뒤 손을 씻지 않은 채 식사를 하다 빵이 이상하리만큼 달다는 사실을 눈치챘다. 손에 남아 있던 화학물질이 원인임을 깨달은 그는 곧장 실험실로 돌아가 합성물 몇 가지를 직접 맛보았고, 그중 하나가 설탕보다 훨씬 강한 단맛을 낸다는 것을 확인했다. 팔베르크가 조금만 더 위생적이었더라면, 혹은 손으로 빵을 집어먹는 문화권 사람이 아니었다면, 사카린은 세상 밖으로 나오지 못했을지도 모른다.

이후 등장한 시클라메이트, 아스파탐, 아세설팜칼륨 같은 인공감미료도 사정은 비슷했다. 대부분은 정교한 설계가 아니라 실험 과정에서 우연히 얻어 걸린 부산물이었다. 설탕 분자의 구조를 모방하거나 쓴맛 수용체를 피하는 쪽으로 약간의 합리적 추론이 더해지긴 했지만, 혀에서 단맛을 감지하는 수용체 구조를 제대로 모른 채 진행한 연구는 열쇠 구멍에 들어간다는 이유로 철사부터 이쑤시개까지 마구잡이로 끼워보는 수준이었다.

이렇게 찾은 물질들이다 보니 단맛은 나지만 뒷맛이 씁쓸하거나, 가열하면 성분이 분해되거나, 일부 감미료는 건강 이상이나 발암 가능성과 관련해 논란에 휩싸이기도 했다. 정밀한 설계가 아닌 시행착오의 산물이라는 점에서, 감미료는 여전히 '경험'의 영역에 가까웠다.

그러나 최근 이 단맛 감각의 메커니즘을 근본적으로 바꿔놓을 연구 결과가 나왔다. 미국 컬럼비아대의 연구팀은 최근 사람의 혀에 존재하는 단맛 감지 수용체의 3차원 구조를 원자 단위로 규명하는 데 성공했다. 연구팀은 극저온 전자현미경(cryo-EM)을 이용해 단맛을 느끼게 하는 단백질 복합체가 어떤 형태로 구성되어 있는지를 정밀하게 관찰했다. 이 단백질은 두 개의 서로 다른 부품이 짝을 이뤄 작동하는 구조인데, 그중 하나는 감미료 분자를 꾹 잡아주는 '포획 역할'을, 다른 하나는 그 포획 과정을 도와주는 '보조 역할'을 한다.

연구진은 감미료 분자가 이 수용체의 어느 위치에 결합하는지를 밝혀냈고, 특정 부위의 구조가 조금만 바뀌어도 단맛 신호가 전달되지 않는다는 사실도 확인했다. 예컨대 단맛 수용체 내부의 특정 아미노산 하나만 바꿔도 감미료에 대한 반응이 사라지는 것이다. 올해 나온 연구를 통해서야 드디어 단맛은 추상적인 관능이 아니라, 물리적이고 예측 가능한 반응의 영역에 들어선 셈이다.

드디어 열린 인공감미료 맞춤 설계 시대

이처럼 단맛 수용체의 구조가 명확하게 드러나면서 감미료 개발 역시 전혀 다른 국면을 맞게 됐다. 이제는 실험실에서 무작위로 물질을 섞어보는 대신, 컴퓨터 시뮬레이션을 통해 수용체 구조에 꼭 들어맞는 분자를 설계하고 시험할 수 있게 된 것이다.

기존의 대표적 인공감미료인 수크랄로스나 아스파탐을 살펴보자. 수크랄로스는 설탕보다 600배 이상 강한 단맛을 내면서도 열에 잘 견디기 때문에 제빵이나 가열 조리에도 널리 쓰인다. 그렇지만 특유의 이질적 맛을 감지하는 소비자가 많다. 아스파탐의 경우 단맛의 질감이 설탕과 가장 유사하다는 평가를 받지만, 열에 약해 청량음료 정도에나 쓰인다. 이처럼 기존 감미료는 쓰임새에 따라 강점이 다르지만, 뒷맛이나 열 안정성, 개인차 반응 등에서 각각의 한계를 지녀왔다. 하지만 이제는 이러한 단점을 이론적으로 예측하고 피할 수 있는 분자 수준의 설계 기반이 마련된 셈이니, 단점을 극복한 차세대 감미료의 개발은 훨씬 더 빠르고 정교하게 이루어질 수 있다.

더 나아가 사람마다 단맛을 느끼는 강도가 조금씩 다른 이유도 이 연구를 통해 설명할 수 있다. 사람의 유전자는 누구나 조금씩 다르고, 단맛 수용체 역시 그 유전자에 따라 미세한 차이가 있다. 이런 유전적 차이는 감미료에 대한 반응성에도 영향을 준다. 같은 음료를 마셔도 어떤 사람은 너무 달게 느끼고, 다른 사람은 싱겁게 느끼는 이유가 바로 여기에 있다. 이제는 이런 개인차를 고려해 맞춤형 감미료를 개발하는 것도 가능해질 전망이다.

2025년 6월 현재까지 맛 수용체 구조가 완전히 파악된 건, 단맛 외에는 쓴맛과 신맛, 짠맛이 전부다. 아직도 '감칠맛' 수용체는 연구가 진행 중이며, 그 외의 새로운 맛 수용체로 제시되는 것들은 실재 여부도 파악하지 못한 상태다. 특히나 음식의 가장 중요한 요인 중 하나인 향(香)을 인식하는 후각 수용체는 미각 수용체와 달리 실질적 무지 상태에 가깝다. 인공향료 개발이 인공감미료보다 더 어려운 이유다. 그렇지만 충분히 긴 시간이 흐른 뒤엔 후각 수용체의 구조 역시 차례로 파악될 테고, 나중엔 미각 신호와 후각 신호를 동시에 자극하는 강렬한 감미료와 향료 조합도 개발될 수 있다. 그때가 오면 맛과 향을 즐기고 음식은 뱉어버렸다던 로마 귀족 체험을 일반 서민들도 누릴 수 있을지도 모른다.

박한슬 약사·‘숫자한국’ 저자

Copyright ⓒ 주간조선. All rights reserved. 무단 전재 및 재배포 금지.

이 기사는 언론사에서 IT 섹션으로 분류했습니다.
주간조선
구독

메인에서 바로 보는 언론사 편집 뉴스 지금 바로 구독해보세요!

주간조선 주요뉴스
해당 언론사에서 선정하며 언론사 페이지(아웃링크)로 이동해 볼 수 있습니다.
李 대통령, 나토 정상회의 불참... 트럼프와 만남 또 밀리나
'도북자' 김민석 옹호 나선 민주 "탈북민 비하 프레임"
이란 "美 공습은 국제법 위반… 핵 활동 못 멈춰"
李 대통령, 오늘 여야 지도부와 오찬… 김용태·송언석 참석
트럼프 "이란 핵 시설 3곳 공격... 안전하게 귀환 중"

이 기사를 추천합니다
쏠쏠정보
9
흥미진진
4
공감백배
10
분석탁월
2
후속강추
2
주간조선 언론사홈 바로가기
주간조선이 이 기사의 댓글 정책을 결정합니다.

댓글29MY댓글
댓글 상세 현황
현재 댓글 24작성자 삭제 5규정 미준수 0
댓글 쓰기
댓글 입력
댓글을 입력해주세요
댓글 정렬 옵션 선택
순공감순	최신순	공감비율순	답글순	과거순
BEST댓글 운영 기준 안내안내 레이어 보기
클린봇이 악성댓글을 감지합니다.
설정
프로필 이미지
ally****
옵션 열기
인공감미료 회사 리베이트 기사
2025.06.23. 08:10
답글0공감/비공감공감16비공감3
프로필 이미지
mir7****
옵션 열기
천연감미료 스테비아를 먹으면 되지 왜 인공감미료를 광고해 주고 그러냐?
2025.06.23. 12:21
답글0공감/비공감공감12비공감2
프로필 이미지
park****
옵션 열기
스테비아 라고 지금도 있지 않아?
2025.06.23. 08:50
답글1공감/비공감공감10비공감1
프로필 이미지
redi****
옵션 열기
열량없는 제품이 나온다해도 혀가 단맛에 길들여지는 부작용이 생기므로 그냥 덜 먹도록 노력하는 게 상책!
2025.06.23. 09:12
답글0공감/비공감공감8비공감1
프로필 이미지
gisu****
옵션 열기
건강을 위해 안 먹는것이 좋아요.
2025.06.23. 20:59
답글0공감/비공감공감1비공감0
댓글 더보기
주간조선 헤드라인더보기
李 국정수행 '긍정 59.7%'... 민주 50.6%, 국힘 30.0%[리얼미터]

1시간전

서울 신림동서 흉기 난동... 용의자는 투신 후 사망

2시간전

'예스 24 사태'로 본 랜섬웨어의 진화

4시간전

스마일게이트 권혁빈의 8조원대 세기의 이혼 소송

5시간전

일상생활 근본 뒤흔드는 일론 머스크의 '로보택시'

6시간전

안철수 "李 대통령과 김경수… 러브버그처럼 전과자끼리 붙어"

1시간전

네이버 AI 뉴스 알고리즘
뉴스 추천 알고리즘이 궁금하다면?

주간조선 랭킹 뉴스
오전 9시~10시까지 집계한 결과입니다.
더보기
많이 본
댓글 많은

함께 볼만한 뉴스
안내
이전 뉴스들 보기
1
5
다음 뉴스들 보기
함께 볼만한 프리미엄 유료 안내

이전 콘텐츠들 보기
1
3
다음 콘텐츠들 보기
구독
로그아웃  전체서비스  서비스안내  오류신고  고객센터  기사배열 책임자 : 김수향 청소년 보호 책임자 : 이정규
각 언론사가 직접 콘텐츠를 편집합니다. ⓒ 주간조선
이 콘텐츠의 저작권은 저작권자 또는 제공처에 있으며, 이를 무단 이용하는 경우 저작권법 등에 따라 법적 책임을 질 수 있습니다.
NAVER

---

위 기사 내용은 전문용어를 모르는 사람에게 쉽게 풀어 설명

이 기사는 **"완벽한 인공 설탕"**을 만들 수 있게 된 과학적 발견에 대한 내용입니다. IT 전문용어를 모르는 분들도 쉽게 이해할 수 있도록 설명드리겠습니다.

## **왜 인공 설탕이 필요한가요?**

사람은 본능적으로 **단맛을 좋아**합니다. 단맛을 느끼면 뇌에서 **도파민**이라는 행복 호르몬이 나와서 기분이 좋아지기 때문입니다. 하지만 설탕을 너무 많이 먹으면 **비만과 당뇨병**이 생기는 문제가 있습니다.

그래서 과학자들은 **"칼로리는 없지만 단맛은 나는"** 인공감미료를 개발했습니다. 제로콜라나 무설탕 과자에 들어가는 것들이 바로 이런 인공감미료입니다.

## **기존 인공감미료의 문제점**

지금까지 나온 인공감미료들은 **우연히 발견**된 것들이 대부분이었습니다.

### **사카린의 발견 이야기**

19세기 말, 러시아 화학자가 실험을 마치고 **손을 씻지 않은 채** 빵을 먹었는데, 빵이 이상하게 달았습니다. 손에 묻은 화학물질 때문이었는데, 이것이 바로 세계 최초의 인공감미료 **사카린**이 된 것입니다.

### **기존 인공감미료의 한계**

- **뒷맛이 쓰거나 이상함**: 설탕과 완전히 같은 맛이 나지 않음
- **열에 약함**: 요리할 때 사용하기 어려움
- **건강 논란**: 일부는 암을 유발할 수도 있다는 의심을 받음

이런 문제들이 생긴 이유는 **"왜 단맛이 나는지"**를 정확히 모른 채 **시행착오**로만 만들었기 때문입니다.

## **혁신적인 발견: 단맛의 비밀을 풀다**

최근 미국 컬럼비아대 연구팀이 **혀에서 단맛을 느끼는 부분의 정확한 구조**를 밝혀냈습니다.

### **단맛 수용체란?**

혀에는 **"단맛 수용체"**라는 것이 있습니다. 이는 마치 **자물쇠와 열쇠** 관계와 같습니다:

- **자물쇠**: 혀의 단맛 수용체
- **열쇠**: 설탕이나 인공감미료 분자

설탕 분자가 이 수용체에 **딱 맞게 들어가면** 뇌에 "달다!"는 신호가 전달됩니다.

### **극저온 전자현미경의 활용**

연구팀은 **극저온 전자현미경**이라는 첨단 장비를 사용했습니다. 이는 **원자 하나하나까지 볼 수 있는 매우 강력한 현미경**으로, 단맛 수용체의 **3차원 구조**를 정확히 파악할 수 있게 해줍니다.

## **이 발견이 가져올 변화**

### **맞춤형 인공감미료 설계**

이제는 **컴퓨터로 시뮬레이션**해서 단맛 수용체에 **완벽하게 맞는 분자**를 설계할 수 있습니다. 마치 **자물쇠를 보고 정확한 열쇠를 만드는 것**과 같습니다.

### **개인 맞춤형 감미료**

사람마다 유전자가 다르기 때문에 **단맛을 느끼는 정도도 다릅니다**. 같은 음료를 마셔도 어떤 사람은 너무 달게, 어떤 사람은 싱겁게 느끼는 이유입니다.

이제는 **개인의 유전자에 맞는 맞춤형 감미료**도 만들 수 있게 될 것입니다.

### **완벽한 설탕 대체재**

앞으로 만들어질 새로운 인공감미료는:

- **설탕과 똑같은 맛**: 이상한 뒷맛 없음
- **열에 강함**: 요리와 제빵에도 사용 가능
- **안전함**: 부작용 없이 설계 가능


## **미래 전망**

현재는 **단맛, 쓴맛, 신맛, 짠맛**의 구조만 밝혀졌습니다. 아직 **감칠맛**이나 **향**을 느끼는 부분은 연구 중입니다.

하지만 시간이 지나면 **모든 맛과 향**을 인공적으로 완벽하게 재현할 수 있게 될 것입니다. 그때가 되면 **"맛은 즐기되 칼로리는 섭취하지 않는"** 완전한 음식도 가능해질 것입니다.

이는 마치 고대 로마 귀족들이 **"맛만 보고 음식을 뱉어버렸던"** 것처럼, 일반인들도 **맛의 즐거움만 순수하게 누릴 수 있는** 시대가 올 수도 있다는 의미입니다.

---

# SK하이닉스가 연일 신고가를 기록하고 있어.

HBM 시장이 확대되고 있고, 레거시급 메모리 역시 수급 불균형으로 가격이 오르고 있어서 주가가 안 오를 수가 없어.
주가 차트를 봤더니 1년 최저치 대비 102%가 올랐어.
업황을 함께 공유하고 있는 미국의 마이크론도 비슷해.
최저치 대비 106% 정도 올랐네.
삼성전자는 어떨까?
4만 원대까지 떨어졌던 지난 연말 최저치 대비 21%가 올랐어.
하지만 최고치에 비하면 31%가 떨어진 수준이야.
같은 반도체를 만들고 있고, 반도체 3사 중 매출이 가장 높은 삼성전자만 왜 혼자 따돌림을 당하는 걸까?
아주 간단하게 말하자면 삼성전자가 반도체를 제대로 만들지 못해서 그래.
이러고 끝내면 다들 짜증을 낼 테니 조금만 더 이야기할게.
삼성전자는 이달에도 엔비디아로부터 HBM3E 퀄을 받는 데 실패했어.
빨라야 9월에나 다시 결과가 나올 테고, 행여 그때 성공하더라도 공급할 수 있는 양은 많지 않을 거야.
그때쯤이면 시장의 수요는 HBM4로 천천히 넘어가기 시작할 테니까.
세 회사 중 삼성전자만 HBM4 개발을 하지 못한 상태야.
삼성전자의 HBM 시장 점유율은 갈수록 떨어진다는 말이지.
그럼, 메모리는 그렇다 치고 파운드리는 회복의 여지가 있지 않을까? 미국 테일러 팹의 투자도 다시 시작한다고 하니 말이야.
응, 아냐.
파운드리는 나의 생산 능력이 중요한 게 아니라 고객사가 찾아 주느냐가 더 중요해.
삼성 파운드리를 선택한 세계적인 IT 업체가 하나라도 있어? 없어.
왜? 파운드리를 한다면서 고객사의 경쟁 제품을 만드는 등 여러 가지 이유가 있지만 결정적인 이유는 수율이 제대로 안 나와서 그래.
세계 1등 타이틀 차지하겠다고 무리하게 4나노, 3나노, 2나노, 1.4나노 등으로 미세 공정을 개발하긴 했지만 실제 거기서 생산되는 제품의 수율은 끔찍한 정도이고, 발열을 비롯한 품질 이슈도 많아.
1.4나노로 웨이퍼 하나에서 양품 10개 겨우 건지는 것보다는 3나노로 양품 100개 건지는 게 고객사 입장에서는 훨씬 나은 선택이거든.
인텔이 1.8나노급 공정을 개발하고 시제품을 만들어 냈다고 발표해도 주가가 아직 그 지경인 건 미세화가 진행될수록 최첨단 기술 개발이 중요한 게 아니라 최고 품질의 기술 개발이 더 중요해졌기 때문이야.
뒤늦게 삼성전자도 1.4나노 개발 대신 2나노와 4나노의 수율 향상에 더 집중하겠다고 이야기하더라고.
맨날 삼성전자에 날을 세우고 있지만 나라고 삼성전자가 저 모양 저 꼴인 게 좋겠어?
시가총액의 15%를 차지하는 삼성전자가 SK하이닉스만큼만 올라 줘도 종합주가지수 4,000은 금방 가능할 거야.
지켜보는 나는 삼성전자가 잘되기를 바라는데, 정작 삼성전자는 잘할 생각을 안 하니까 답답하단 말이야.
이유가 뭘까?
불법과 탈세를 통해 그 자리를 차지한 재벌 3세 이재용 때문이지.
윤석열에서 이재명으로 바뀌었는데 바로 종합주가지수 3천을 뛰어 넘잖아.
이재용이 그 자리에서 물러 나기만 해도 삼성전자는 퀀텀 점프를 하게 될 거야.
이재용에 관한 이야기는 다음에 더 자세하게 할게.

---

위 내용을 전문용어를 잘 모르는 사람에게 쉽게 풀어 설명

최근 반도체 회사들의 주가 상황을 쉽게 설명드리겠습니다.

## **반도체 회사들의 주가 성과**

**SK하이닉스**와 **마이크론(미국 회사)**은 요즘 매우 잘 나가고 있습니다. 두 회사 모두 주가가 1년 전 최저점보다 **100% 이상** 올랐어요. 즉, 주식 가격이 두 배 이상 뛴 것입니다.

반면 **삼성전자**는 같은 기간 동안 **21%**만 올랐습니다. 세 회사 모두 반도체를 만드는데, 왜 삼성전자만 뒤처지고 있을까요?

## **HBM이 뭔가요?**

**HBM**은 "High Bandwidth Memory"의 줄임말로, **"초고속 메모리"**라고 생각하시면 됩니다. 인공지능(AI) 작업에 꼭 필요한 특별한 메모리로, 마치 **"슈퍼카의 엔진"** 같은 역할을 합니다.

요즘 AI 붐으로 인해 HBM에 대한 수요가 폭증하고 있어서, 이를 잘 만드는 회사들의 주가가 크게 오르고 있습니다.

## **삼성전자의 문제점들**

### **HBM 품질 문제**

삼성전자는 **엔비디아**라는 중요한 고객사로부터 **품질 인증을 받지 못했습니다**. 엔비디아는 AI 칩을 만드는 세계 1위 회사인데, 이 회사가 "삼성의 HBM은 품질이 부족하다"고 판정한 것입니다.

마치 **자동차 부품을 만들었는데 완성차 업체에서 "이 부품은 품질이 안 좋아서 못 쓰겠다"**고 거절당한 상황과 같습니다.

### **파운드리 사업의 어려움**

**파운드리**는 **"반도체 대행 제작 서비스"**입니다. 다른 회사가 설계한 반도체를 대신 만들어주는 사업이에요.

삼성전자는 **수율(良品率) 문제**를 겪고 있습니다. 수율이란 **"제품을 100개 만들었을 때 정상적으로 작동하는 제품의 개수"**를 의미합니다.

예를 들어:

- **1.4나노 공정**: 웨이퍼 하나에서 정상 제품 10개만 나옴
- **3나노 공정**: 웨이퍼 하나에서 정상 제품 100개 나옴

고객 입장에서는 당연히 **더 많은 정상 제품이 나오는 3나노**를 선호하게 됩니다.

## **나노 공정이란?**

**나노 공정**은 반도체를 얼마나 **정밀하게** 만드는지를 나타내는 단위입니다. 숫자가 작을수록 더 정밀하고 고성능이지만, 만들기가 매우 어려워집니다.

마치 **"연필로 글씨를 쓰는 것"**과 **"머리카락 굵기의 1만분의 1로 글씨를 쓰는 것"**의 차이라고 생각하시면 됩니다.

삼성전자는 **"세계 1등"**이 되려고 너무 성급하게 최첨단 공정을 개발했지만, 정작 **품질과 수율**에서 문제가 생긴 상황입니다.

## **왜 이런 일이 생겼을까?**

### **기술적 문제**

- **품질 관리 부족**: 최첨단 기술 개발에만 집중하고 품질 향상을 소홀히 함
- **수율 개선 실패**: 정상 제품이 나오는 비율이 너무 낮음
- **고객사 신뢰 상실**: 품질 문제로 인해 주요 고객들이 다른 회사를 선택


### **경영 방식의 문제**

글쓴이는 삼성전자의 경영진, 특히 **이재용 부회장의 경영 방식**에도 문제가 있다고 지적하고 있습니다. 기술 개발보다는 다른 부분에 너무 신경을 쓰고 있다는 비판입니다.

## **결론**

**SK하이닉스**와 **마이크론**은 고품질의 HBM을 안정적으로 생산해서 AI 붐의 수혜를 받고 있지만, **삼성전자**는 품질 문제로 인해 시장에서 뒤처지고 있는 상황입니다.

마치 **"같은 빵집 3곳 중에서 2곳은 맛있는 빵을 만들어 손님이 몰리는데, 1곳은 빵이 자꾸 타서 손님이 오지 않는"** 상황과 비슷합니다.

삼성전자가 이 문제들을 해결한다면 주가도 크게 오를 수 있을 것으로 예상되지만, 현재로서는 기술적, 경영적 개선이 시급한 상황입니다.

<div style="text-align: center">⁂</div>

---

# 오늘 Claude Code로 해보니 너무 잘하네요

1. (깃헙 url 주고서) “전체 커밋 로그를 분석해서 개발 추정 시간을 산출해줘 상세 내용은 일자별로 표로 정리해줘. |일자|시간대|커밋 수|개발작업 추청시간 (분)|커밋내용요약|”
추정 시간은 대화를 통해 좀 더 조정했습니다.
그리로 의미있는 결과가 나오길래
2. “동일한 방법으로 개발 추정시간 분석하는 스크립트 작성해줘. 요약은 OpenAI API 연동해서 처리해줘“
3. “앞서 만든 스크립트를 참고해서 깃헙 URL 목록 파일을 제공하면 모든 저장소를 분석해서 파일로 저장하는 스크립크 작성해줘”
4. 분석결과 파일을 토대로 (ppt or report or webpage) 만들어줘
혹시나 Claude Code가 산으로 가면 /clear 처리하고 다시 시작합니다
평소 커밋 메시지를 잘 작성했다면 꽤 그럴싸한 결과가 나옵니다 ex) 어떤 기능들이 언제 개발되었는지 파악 가능
AI나 Claude Code로 커밋메시지 작성합니다
제가 가장 많이 쓰는 문구
“변경사항 커밋하고 푸시해줘”

---

위 개발과정에 대해서 it용어를 잘 모르는 사람이 이해하기 쉽게 풀어 설명

이 개발 과정을 일반인도 이해하기 쉽게 설명드리겠습니다.

## **Claude Code가 뭔가요?**

**Claude Code**는 AI가 프로그래밍을 도와주는 도구입니다. 마치 **"코딩을 도와주는 똑똑한 비서"**라고 생각하시면 됩니다. 사람이 "이런 프로그램을 만들어줘"라고 요청하면, AI가 직접 코드를 작성해줍니다.

## **전체 과정을 쉽게 설명**

### **1단계: 깃헙 분석 요청**

**깃헙(GitHub)**은 **"개발자들의 작업 일기장"**같은 곳입니다. 개발자가 프로그램을 수정할 때마다 **"커밋"**이라는 기록을 남깁니다.

**커밋**은 **"오늘 이런 작업을 했습니다"**라는 작업 기록이에요. 예를 들어:

- "로그인 기능 추가함"
- "버그 수정함"
- "새로운 화면 만들었음"

글쓴이는 Claude에게 **"이 깃헙 주소를 보고, 전체 작업 기록을 분석해서 개발에 얼마나 시간이 걸렸는지 계산해줘"**라고 요청했습니다.

결과는 표로 정리되었어요:

- 날짜별로 언제 작업했는지
- 몇 시에 작업했는지
- 몇 개의 작업을 했는지
- 대략 몇 분 정도 걸렸을지 추정
- 어떤 작업을 했는지 요약


### **2단계: 자동화 프로그램 제작**

첫 번째 분석이 잘 나오자, 글쓴이는 **"이런 분석을 자동으로 해주는 프로그램을 만들어줘"**라고 요청했습니다.

**OpenAI API 연동**이란 **ChatGPT의 기능을 프로그램에서 사용할 수 있게 연결하는 것**입니다. 마치 **"프로그램이 ChatGPT에게 질문해서 답을 받아오는 것"**과 같습니다.

### **3단계: 대량 분석 프로그램**

이번에는 **"깃헙 주소 목록 파일을 주면, 여러 개의 프로젝트를 한 번에 분석해주는 프로그램"**을 만들어달라고 했습니다.

예를 들어:

- 프로젝트 A 분석 → 결과 파일 저장
- 프로젝트 B 분석 → 결과 파일 저장
- 프로젝트 C 분석 → 결과 파일 저장


### **4단계: 보고서 제작**

마지막으로 분석 결과를 보기 좋게 **파워포인트나 웹페이지, 보고서**로 만들어달라고 요청했습니다.

## **주요 용어 설명**

### **커밋(Commit)**

**"작업 저장"**이라고 생각하시면 됩니다. 개발자가 코드를 수정한 후 **"오늘 이런 작업을 했다"**고 기록을 남기는 것입니다.

### **푸시(Push)**

**"작업 결과를 서버에 업로드"**하는 것입니다. 마치 **"내 컴퓨터에서 작업한 파일을 클라우드에 저장"**하는 것과 같습니다.

### **API**

**"프로그램끼리 대화하는 방법"**입니다. 예를 들어 내 프로그램이 ChatGPT에게 **"이 텍스트를 요약해줘"**라고 요청하고 답을 받아오는 것입니다.

### **/clear**

Claude와의 대화를 **"처음부터 다시 시작"**하는 명령어입니다. 마치 **"대화 내용을 모두 지우고 새로 시작"**하는 것과 같습니다.

## **이 과정의 장점**

### **자동화의 힘**

사람이 수작업으로 하면 몇 시간 걸릴 일을 **몇 분 만에 자동으로** 처리할 수 있게 되었습니다.

### **정확한 분석**

커밋 메시지를 잘 작성해두면 **"언제, 어떤 기능을, 얼마나 시간을 들여 개발했는지"**를 정확히 파악할 수 있습니다.

### **프로젝트 관리**

이런 분석을 통해 **"이 프로젝트는 총 몇 시간이 걸렸는지"**, **"어떤 기능 개발이 가장 오래 걸렸는지"** 등을 알 수 있어서 향후 프로젝트 계획을 세우는 데 도움이 됩니다.

결국 이 과정은 **"AI를 활용해서 개발 작업을 분석하고 자동화하는 스마트한 방법"**을 보여주는 사례라고 할 수 있습니다.

---

# 코난 테크놀로지의 신뢰성

코난테크놀로지의 신뢰성을 다각도로 분석해보겠습니다.

## **기술적 신뢰성**

### **검증된 기술력**

코난테크놀로지는 **25년간의 축적된 기술 경험**을 보유하고 있으며, 2,900곳 이상의 기업에서 솔루션 파트너로 선택되었습니다[^18_1]. 3,400회 이상의 프로젝트 경험을 통해 고품질 솔루션을 공급해왔습니다.

### **품질 인증**

- **GS 품질인증 1등급** 획득[^18_2]
- **클라우드 서비스 보안인증** 취득으로 정부 및 공공기관의 안전한 서비스 도입 가능[^18_2]
- 독립적인 테스트베드 구축으로 검증된 인프라 운영[^18_2]


### **자체 개발 역량**

국내 최초 일반·추론 통합 모델인 **'코난 LLM ENT-11'**을 개발하여 DeepSeek-R1을 능가하는 성능을 저사양 GPU에서도 안정적으로 제공합니다[^18_1]. 스탠퍼드대 에코시스템 그래프에 등재된 한국산 파운데이션 모델을 보유하고 있습니다[^18_3].

## **고객 신뢰성**

### **공공기관 도입 실적**

- **국세청**: 홈택스 대국민 챗봇 서비스 운영[^18_2]
- **국방부, 행정안전부, 국회사무처**: 생성형 AI 서비스 구축[^18_3]
- **경찰청**: 콜센터 및 통합검색시스템 구축[^18_4][^18_5]
- **한국남부발전, 한국중부발전**: 전력 공기업 도입[^18_3]


### **민간 기업 신뢰**

- **KB국민은행**: 15년간 장기 유지 고객사로 6개 업무 시스템에 도입[^18_4][^18_5]
- **SK하이닉스**: 시스템 활용도와 업무 효율성 향상[^18_2]
- **한화손해보험, 신한라이프, KB증권**: 금융권 광범위 도입[^18_3]


## **경영 신뢰성의 우려사항**

### **재무적 불안정성**

2023년 기준으로 **매출 244억원 대비 영업손실 109억원**을 기록하여 매출대비 적자율이 45%에 달합니다[^18_6]. 2022년 40억원에서 2023년 109억원으로 적자가 2배 이상 확대되었습니다.

### **공약 이행 문제**

상장 당시 제시한 목표 대비 실적이 크게 부족합니다[^18_6]:

- **2023년 목표**: 매출 357억원, 영업이익 85억원
- **2023년 실제**: 매출 244억원, 영업손실 109억원
- 목표 대비 매출 113억원, 영업이익 195억원 부족


### **높은 인건비 비율**

전체 매출에서 직원 급여가 차지하는 비중이 **69.7%**에 달하여 수익성 구조에 부담을 주고 있습니다[^18_6].

## **종합 평가**

### **기술적 신뢰성: 높음**

- 25년간의 검증된 기술력과 풍부한 프로젝트 경험
- 정부 품질인증 및 보안인증 취득
- 자체 개발 LLM 모델의 우수한 성능


### **고객 신뢰성: 높음**

- 국가기관 및 대기업의 지속적인 도입
- 장기 고객사들의 신뢰 관계 유지
- 다양한 산업 분야에서의 검증된 성과


### **경영 신뢰성: 주의 필요**

- 지속적인 적자 확대와 높은 인건비 비율
- 상장 시 공약 대비 실적 부족
- 단기적 수익성 개선 필요

**결론적으로** 코난테크놀로지는 **기술력과 고객 신뢰도 측면에서는 높은 신뢰성**을 보이지만, **재무적 안정성 측면에서는 개선이 필요한 상황**입니다. 기업과의 장기적 파트너십을 고려할 때는 기술적 역량과 함께 재무 건전성도 종합적으로 검토하는 것이 바람직합니다.

<div style="text-align: center">⁂</div>

[^18_1]: https://www.konantech.com

[^18_2]: https://www.etnews.com/20241120000008

[^18_3]: https://konantech.com/pr/press?number=3585\&pn=\&stype2=\&sfi=\&sword=

[^18_4]: https://www.aitimes.com/news/articleView.html?idxno=163082

[^18_5]: https://konantech.com/pr/press?number=3192\&pn=\&stype2=\&sfi=\&sword=

[^18_6]: https://m.ddaily.co.kr/page/view/2024032416285923654

[^18_7]: https://zdnet.co.kr/view/?no=20250613100624

[^18_8]: https://www.aitimes.com/news/articleView.html?idxno=170026

[^18_9]: https://blog.conan.io/2023/10/03/backup-sources-feature.html

[^18_10]: https://www.reddit.com/r/cpp_questions/comments/t9f6lt/how_much_opinionated_is_conan_really/


---

# 서버란 무엇인지 it용어를 모르는 사람에게 쉽게 설명

서버는 쉽게 말해 **"컴퓨터들의 우체국"** 또는 **"정보를 나눠주는 도우미"**라고 생각하면 됩니다.

## **서버의 기본 역할**

인터넷이나 회사 네트워크에서 여러 사람이 동시에 정보를 주고받을 때, 서버는 그 정보를 저장하고 요청하는 사람들에게 필요한 데이터를 전달해주는 역할을 합니다.

## **일상생활 속 서버의 예시**

### **웹사이트 접속**

우리가 인터넷에서 웹사이트에 접속할 때, 그 웹사이트의 정보는 서버라는 컴퓨터에 저장되어 있습니다. 우리가 웹사이트 주소를 입력하면, 서버가 그 정보를 찾아서 우리 컴퓨터로 보내줍니다.

### **다양한 서비스**

서버는 이메일을 보내거나, 파일을 저장하거나, 게임을 할 때 다른 사람들과 연결해주는 등 다양한 일을 합니다.

## **쉬운 비유로 이해하기**

서버를 **도서관**에 비유하면 이해하기 쉽습니다:

- **도서관**: 책들을 보관하고 정리해두는 곳
- **사서**: 사람들이 원하는 책을 찾아서 빌려주는 역할
- **서버**: 정보를 보관하고, 사람들이 요청하면 그 정보를 찾아서 전달해주는 역할

또는 **식당**에 비유할 수도 있습니다:

- **주방**: 음식을 준비하고 보관하는 곳
- **웨이터**: 손님의 주문을 받고 음식을 가져다주는 역할
- **서버**: 데이터를 준비하고, 사용자의 요청을 받아 정보를 전달해주는 역할

쉽게 말해, 서버는 여러 사람이 정보를 공유하고 소통할 수 있도록 도와주는 **"중앙 컴퓨터"**라고 생각하면 됩니다.

<div style="text-align: center">⁂</div>

---

# Fireplexity에 대해 알려줘

Fireplexity는 **오픈소스 AI 검색 엔진**으로, Perplexity의 클론 버전을 개발자들이 직접 구축하고 호스팅할 수 있도록 만든 도구입니다[^20_1].

## **Fireplexity의 핵심 개념**

Fireplexity는 기존 검색 엔진의 한계를 극복하기 위해 개발되었습니다. 일반적인 검색 엔진이 단순히 링크 목록을 제공하는 것과 달리, **실시간으로 웹페이지를 탐색하고 AI가 직접 답변을 생성**해주는 차세대 검색 도구입니다[^20_2].

## **주요 기능**

### **실시간 웹 검색**

Firecrawl의 고속 웹 스크래핑 API를 기반으로 현재 시점의 웹페이지를 직접 탐색하여 최신 데이터를 수집합니다[^20_2][^20_3].

### **AI 기반 응답 생성**

GPT-4o-mini 모델을 활용하여 자연스럽고 빠른 스트리밍 응답을 제공합니다. 사용자는 OpenAI 호환 엔드포인트로 다른 모델로도 교체할 수 있습니다[^20_3][^20_1].

### **출처 기반 응답**

모든 응답은 관련 웹페이지 링크와 함께 제공되어 정보의 신뢰성을 보장합니다. 사용자는 인용 부분에 마우스를 올리면 즉시 출처를 미리볼 수 있습니다[^20_2][^20_1].

### **실시간 주식 데이터**

TradingView 차트를 자동으로 연동하여 180개 이상의 기업에 대한 주가 등 금융 정보를 시각화합니다[^20_3][^20_1].

### **스마트 후속 질문**

AI가 사용자의 다음 질문을 예측해 제안함으로써 탐색의 흐름을 자연스럽게 이어갑니다[^20_2][^20_3].

## **기술적 구조**

### **Firecrawl API의 역할**

Fireplexity의 핵심 엔진은 Firecrawl입니다. 이는 웹사이트의 HTML 구조를 분석하여 필요한 정보를 실시간으로 추출하는 스크래핑 API로, JavaScript 렌더링을 처리하고 안정적으로 콘텐츠를 수집합니다[^20_2][^20_1].

### **스마트 콘텐츠 선택**

단순한 키워드 검색을 넘어서 알고리즘이 콘텐츠의 관련성을 점수화하고 페이지에서 가장 중요한 정보를 찾아냅니다[^20_1].

### **기술 스택**

- **Firecrawl**: 웹 스크래핑 API
- **Next.js 15**: React 프레임워크
- **OpenAI**: GPT-4o-mini
- **Vercel AI SDK**: 스트리밍
- **TradingView**: 주식 차트[^20_3]


## **사용 방법**

### **빠른 시작**

```bash
git clone https://github.com/mendableai/fireplexity.git
cd fireplexity
npm install
```


### **API 키 설정**

```bash
cp .env.example .env.local
```

`.env.local` 파일에 다음을 추가:

```
FIRECRAWL_API_KEY=fc-your-api-key
OPENAI_API_KEY=sk-your-api-key
```


### **실행**

```bash
npm run dev
```

http://localhost:3000에서 접속 가능합니다[^20_3].

## **Fireplexity의 장점**

### **5분 내 배포 가능**

빠르게 실행 가능한 답변 엔진을 제공합니다[^20_1].

### **벤더 종속성 없음**

오픈소스로 제공되어 개발자가 코드에 완전히 접근할 수 있고 자신만의 방향으로 개발할 수 있습니다[^20_1].

### **실시간 인텔리전스**

신뢰할 수 있는 웹 스크래핑을 통해 최적의 콘텐츠를 지능적으로 선택하고 인용과 함께 답변을 합성합니다[^20_1].

## **활용 분야**

Fireplexity는 내부 지식 베이스 구축, 전문화된 연구 도구 제작, 도메인별 맞춤형 답변 엔진 구축 등 다양한 용도로 활용할 수 있습니다. 개발자들이 자신만의 니치 분야에 특화된 AI 검색 경험을 구축하고자 할 때 특히 유용합니다[^20_1].

현재 GitHub에서 90개의 스타를 받으며 활발히 개발되고 있으며, tools.firecrawl.dev/fireplexity에서 라이브 데모를 체험할 수 있습니다[^20_3].

<div style="text-align: center">⁂</div>

[^20_1]: https://www.firecrawl.dev/blog/introducing-fireplexity-open-source-answer-engine

[^20_2]: https://digitalbourgeois.tistory.com/1509

[^20_3]: https://github.com/mendableai/fireplexity

[^20_4]: https://www.firecrawl.dev/blog

[^20_5]: https://digitalbourgeois.tistory.com/1508

[^20_6]: https://informationstoryz.tistory.com/entry/Perplexity

[^20_7]: https://digitalbourgeois.tistory.com/1511

[^20_8]: https://crevate.com/ai/여러-개의-인공지능을-다-써서-찾아주는-perplexity/

[^20_9]: https://www.saramin.co.kr/zf_user/company-info/view/csn/R0c2TzAzckQyNFFORGM5NFEwa2MwQT09/company_nm/(%EC%A3%BC)%EB%B9%84%EB%A7%88%EC%9D%B4%ED%94%84%EB%A0%8C%EC%A6%88

[^20_10]: https://www.saramin.co.kr/zf_user/company-info/view/csn/WEhiUExLTVZpWjlkYzU0QkZXV0lHQT09/company_nm/(%EC%A3%BC)%ED%94%84%EB%A6%AC%EC%9C%8C%EB%A6%B0


---

# sql에서 desc는 무엇의 약자이고 무슨 뜻인가

SQL에서 **desc**는 두 가지 의미로 사용됩니다:

## **1. Descending (내림차순 정렬)**

**desc**는 **"descending"의 약자**로, 데이터를 **내림차순으로 정렬**할 때 사용됩니다.

**사용 예시:**

```sql
SELECT * FROM students ORDER BY score DESC;
```

이 쿼리는 학생들의 점수를 높은 점수부터 낮은 점수 순으로 정렬합니다.

**정렬 순서:**

- **ASC (ascending)**: 오름차순 (1, 2, 3... 또는 A, B, C...)
- **DESC (descending)**: 내림차순 (3, 2, 1... 또는 Z, Y, X...)


## **2. Describe (테이블 구조 설명)**

일부 데이터베이스 관리 시스템(DBMS)에서는 **테이블의 구조를 보여주는 명령어**로도 사용됩니다.

**사용 예시:**

```sql
DESC table_name;
```

또는

```sql
DESCRIBE table_name;
```

이 명령어를 실행하면 테이블의 **컬럼명, 데이터 타입, 제약조건** 등의 정보를 확인할 수 있습니다.

따라서 SQL에서 **desc**는 문맥에 따라 **"descending(내림차순)"** 또는 **"describe(설명)"**의 약자로 사용됩니다.

<div style="text-align: center">⁂</div>

---

# 현재 깃헙에서 가장 핫한 ai 프로그램 또는 ai 응용 프로그램은 어떤게 있어?

2025년 현재 깃헙에서 가장 주목받고 있는 AI 프로그램들을 소개해드리겠습니다.

## **1. STORM - 협업형 AI 지식 탐색 도구**

스탠포드 OVAL Lab에서 개발한 **STORM**은 위키피디아 스타일의 글을 처음부터 생성하는 혁신적인 LLM 시스템입니다[^22_1]. 인터넷 검색과 질문 기반 탐색을 결합하여 동적으로 글을 작성하며, **Co-STORM** 확장을 통해 인간과 AI가 협업할 수 있는 환경을 제공합니다.

## **2. All-Hands-AI (OpenHands \& OpenOperator)**

**완전 자율적인 AI 에이전트**로, 코드 작성, 명령어 실행, 웹 브라우징을 인간 수준의 자율성으로 수행할 수 있습니다[^22_2]. 소프트웨어 개발 분야에서 혁신적인 도구로 주목받고 있습니다.

## **3. vLLM - 초고속 LLM 추론 라이브러리**

UC 버클리에서 시작되어 현재 커뮤니티 주도로 개발되는 **vLLM**은 대형 언어 모델의 추론과 서빙을 위한 메모리 효율적이고 매우 빠른 라이브러리입니다[^22_2].

## **4. Open WebUI MCP - AI 도구 통합 플랫폼**

MCP 도구를 OpenAPI 호환 HTTP 서버로 변환하는 **프록시 서버**로, AI 기반 앱을 구축하는 개발자들이 MCP 기반 도구를 표준 RESTful OpenAPI 인터페이스와 쉽게 연결할 수 있게 해줍니다[^22_3].

## **5. Unbody - "AI의 Supabase"**

**AI 네이티브 소프트웨어**를 구축할 수 있는 모듈형 백엔드 플랫폼입니다[^22_3]. 단순한 데이터 처리를 넘어 지식을 실제로 이해하고 추론할 수 있는 소프트웨어 개발을 지원합니다.

## **6. OWL - 멀티 에이전트 협업 시스템**

CAMEL-AI 프레임워크를 기반으로 구축된 **OWL**은 여러 전문화된 AI 에이전트가 브라우저, 터미널, 함수 호출, MCP 도구를 통해 협력할 수 있게 해줍니다[^22_3]. GAIA 벤치마크에서 오픈소스 리더보드 1위(58.18점)를 기록했습니다.

## **7. MindsDB - AI 네이티브 쿼리 엔진**

데이터 소스에 연결하여 **자연어로 질문에 답할 수 있는** AI 네이티브 쿼리 엔진입니다[^22_2]. 연합 쿼리와 파인튜닝을 위해 구축되었습니다.

## **8. Model Context Protocol (MCP)**

Anthropic이 지원하는 **"LLM용 USB-C"**라고 불리는 표준 프로토콜로, LLM 앱을 외부 데이터 및 도구와 연결하기 위한 오픈 사양입니다[^22_2].

## **주목할 만한 특징들**

이러한 프로젝트들의 공통점은:

- **멀티 에이전트 협업** 기능
- **실시간 웹 연동** 및 자동화
- **개발자 친화적인 API** 제공
- **오픈소스 기반**의 커뮤니티 주도 개발

2025년 AI 프로젝트 트렌드는 단일 AI 모델을 넘어서 **여러 AI 에이전트가 협력하는 시스템**과 **개발자가 쉽게 통합할 수 있는 플랫폼** 중심으로 발전하고 있습니다.

<div style="text-align: center">⁂</div>

[^22_1]: https://opencv.org/blog/top-github-projects-jan-2025/

[^22_2]: https://www.youtube.com/watch?v=uFsP4KvAAMA

[^22_3]: https://github.blog/open-source/maintainers/from-mcp-to-multi-agents-the-top-10-open-source-ai-projects-on-github-right-now-and-why-they-matter/

[^22_4]: https://github.com/Projects-Developer/Top-30-Artificial-Intelligence-Project-Ideas-in-2025

[^22_5]: https://www.aixploria.com/en/category/github-project-ai/

[^22_6]: https://dev.to/therealmrmumba/my-fav-open-source-github-tools-2025-as-a-developer-2o6b

[^22_7]: https://github.com/topics/artificial-intelligence-projects

[^22_8]: https://github.com/joylarkin/Awesome-AI-Market-Maps

[^22_9]: https://www.youtube.com/watch?v=6SOs1Mxqfqo

[^22_10]: https://dev.to/leamsigc/top-10-trending-github-repositories-january-2025-1f24


---

# sql crud

SQL에서 CRUD는 데이터베이스의 가장 기본적인 4가지 데이터 처리 작업을 의미합니다[^23_1].

## **CRUD의 의미**

**CRUD**는 다음 네 가지 작업의 첫 글자를 따서 만든 용어입니다[^23_1][^23_2]:

- **C**reate (생성)
- **R**ead (읽기)
- **U**pdate (갱신)
- **D**elete (삭제)


## **SQL 명령어와의 대응**

각 CRUD 작업은 다음과 같은 SQL 명령어로 구현됩니다[^23_1][^23_3]:


| CRUD | 작업 | SQL 명령어 |
| :-- | :-- | :-- |
| Create | 생성 | INSERT |
| Read | 읽기 | SELECT |
| Update | 갱신 | UPDATE |
| Delete | 삭제 | DELETE |

## **각 작업의 구체적인 예시**

### **Create (생성) - INSERT**

새로운 데이터를 테이블에 추가합니다[^23_2]:

```sql
INSERT INTO Users (username, password, email) 
VALUES ('john_doe', 'password123', 'john@example.com');
```


### **Read (읽기) - SELECT**

데이터베이스에서 데이터를 조회합니다[^23_2]:

```sql
SELECT * FROM Users WHERE username = 'john_doe';
```


### **Update (갱신) - UPDATE**

기존 데이터를 수정합니다[^23_2]:

```sql
UPDATE Users SET email = 'john_new@example.com' 
WHERE username = 'john_doe';
```


### **Delete (삭제) - DELETE**

데이터를 삭제합니다[^23_2]:

```sql
DELETE FROM Users WHERE username = 'john_doe';
```


## **CRUD의 중요성**

CRUD는 **거의 모든 시스템에 적용되는 가장 기본이 되는 개념**입니다[^23_4]. 다음과 같은 이유로 중요합니다[^23_2]:

- **데이터 관리**: 응용 프로그램이 데이터를 효율적으로 관리하고 유지할 수 있게 함
- **기본 기능**: 대부분의 데이터 중심 응용 프로그램의 기반이 됨
- **유연성**: 데이터를 동적으로 생성, 조회, 수정, 삭제할 수 있게 함
- **표준화**: 데이터 조작에 대한 표준화된 접근 방식을 제공


## **실제 활용 예시**

개발 현장에서는 다음과 같이 사용됩니다[^23_4]:

- "댓글 CRUD 구현해주세요" → 댓글 작성, 조회, 수정, 삭제 기능 모두 구현
- "게시글 CRUD 완료했습니다" → 게시글의 모든 기본 기능이 구현됨

CRUD는 데이터베이스를 다루는 모든 개발자가 반드시 알아야 하는 핵심 개념으로, 이 네 가지 작업을 통해 데이터의 전체 생명 주기를 관리할 수 있습니다[^23_2].

<div style="text-align: center">⁂</div>

[^23_1]: https://ko.wikipedia.org/wiki/CRUD

[^23_2]: https://itrh.tistory.com/entry/데이터베이스-CRUD-란

[^23_3]: https://wdkong.com/blog/it/db/mysql-mariadb-crud/

[^23_4]: https://idkim97.github.io/2022-08-17-CRUD란/

[^23_5]: https://savvy0402.tistory.com/27

[^23_6]: https://miny-genie.tistory.com/273

[^23_7]: https://velog.io/@windfall0369/데이터베이스-CRUD

[^23_8]: https://velog.io/@wijoonwu/SQL-CRUD-정리

[^23_9]: https://kr98gyeongim.tistory.com/5

[^23_10]: https://lgphone.tistory.com/85


---

# sql에서 프라이머리키는 삭제하면 다시 생성이 불가능한가

아니요, SQL에서 프라이머리키(Primary Key)를 삭제해도 **다시 생성이 가능**합니다.

## **프라이머리키 삭제와 재생성 과정**

### **1단계: 프라이머리키 삭제**

```sql
ALTER TABLE table_name DROP CONSTRAINT constraint_name;
```

또는 제약조건 이름을 모르는 경우:

```sql
ALTER TABLE table_name DROP PRIMARY KEY;
```


### **2단계: 프라이머리키 재생성**

```sql
ALTER TABLE table_name ADD CONSTRAINT PK_table_name PRIMARY KEY (column_name);
```


## **실제 예시**

**삭제:**

```sql
ALTER TABLE employees DROP CONSTRAINT PK_employees;
```

**재생성:**

```sql
ALTER TABLE employees ADD CONSTRAINT PK_employees PRIMARY KEY (employee_id);
```


## **주의사항**

### **운영 환경에서의 고려사항**

- **서버 다운 불필요**: 대부분의 경우 서버를 내리지 않고도 실행 가능
- **성능 영향**: 프라이머리키 삭제 시 클러스터드 인덱스도 함께 삭제되어 쿼리 성능에 일시적 영향
- **외래키 참조**: 다른 테이블에서 외래키로 참조하고 있다면 먼저 외래키를 삭제해야 함


### **대용량 테이블의 경우**

- 500만 건 이상의 대용량 테이블에서는 작업 시간이 오래 걸릴 수 있음
- 인덱스 재구성으로 인한 시스템 부하 발생 가능


## **AUTO_INCREMENT 값 재설정**

프라이머리키를 재생성할 때 AUTO_INCREMENT 값도 함께 재설정할 수 있습니다:

```sql
-- MySQL의 경우
ALTER TABLE table_name AUTO_INCREMENT = 1;

-- SQL Server의 경우  
DBCC CHECKIDENT(table_name, RESEED, 0);
```


## **결론**

프라이머리키는 삭제 후 **언제든지 재생성이 가능**하며, 이는 데이터베이스 설계 변경이나 성능 최적화 시 자주 사용되는 작업입니다. 다만 운영 환경에서는 성능과 참조 무결성을 고려하여 신중하게 진행해야 합니다.

<div style="text-align: center">⁂</div>

[^24_1]: https://stackoverflow.com/questions/32861336/can-we-drop-and-recreate-primary-key-in-sql-server-table-production-environmen

[^24_2]: https://www.youtube.com/watch?v=79sifTONEKw

[^24_3]: https://www.youtube.com/watch?v=g61GYm5f0ZA

[^24_4]: https://codingsight.com/primary-keys-in-sql-server/

[^24_5]: https://learn.microsoft.com/en-us/sql/relational-databases/tables/delete-primary-keys?view=sql-server-ver17

[^24_6]: https://docs.snowflake.com/en/sql-reference/constraints-drop

[^24_7]: https://stackoverflow.com/questions/6972275/resetting-the-primary-key-to-1-after-deleting-all-the-data/46715778

[^24_8]: https://stackoverflow.com/questions/253522/do-numerical-primary-keys-of-deleted-records-in-a-database-get-reused-for-future

[^24_9]: https://dba.stackexchange.com/questions/177688/can-i-reorganize-a-primary-key-after-deleting-some-rows

[^24_10]: https://stackoverflow.com/questions/26568324/drop-and-recreate-primary-key-on-an-sql-server-temporary-table/26568445


---

# sql에서 특정 순서의 프라이머리키는 삭제하면 다시 똑같은 번호로 재생성이 불가능한가

SQL에서 **AUTO_INCREMENT 프라이머리키**의 경우, 특정 번호를 삭제하면 **기본적으로는 동일한 번호로 자동 재생성이 불가능**합니다. 하지만 **수동으로 재설정하면 가능**합니다.

## **AUTO_INCREMENT의 기본 동작**

AUTO_INCREMENT 프라이머리키는 다음과 같은 특성을 가집니다:

- 삭제된 레코드의 번호는 **자동으로 재사용되지 않음**
- 항상 **마지막 최대값보다 큰 다음 번호**를 생성
- 중간에 삭제된 번호는 **빈 공간으로 남음**


## **예시 상황**

```sql
-- 1, 2, 3, 4, 5 번호가 있는 상태에서
DELETE FROM users WHERE id = 3;

-- 새로운 레코드 추가 시
INSERT INTO users (name) VALUES ('새 사용자');
-- 결과: id = 6 (3이 아닌 6번으로 생성됨)
```


## **동일 번호로 재생성하는 방법**

### **방법 1: AUTO_INCREMENT 값 재설정**

```sql
-- 3번을 다시 사용하고 싶다면
ALTER TABLE users AUTO_INCREMENT = 3;
INSERT INTO users (name) VALUES ('새 사용자');
-- 결과: id = 3으로 생성됨
```


### **방법 2: 직접 번호 지정**

```sql
-- AUTO_INCREMENT 컬럼에 직접 값 삽입
INSERT INTO users (id, name) VALUES (3, '새 사용자');
```


## **주의사항**

### **데이터 무결성 위험**

- 삭제된 번호를 재사용하면 **외래키 참조 문제** 발생 가능
- 기존 로그나 연관 데이터와의 **일관성 문제** 발생 가능


### **운영 환경에서의 고려사항**

- AUTO_INCREMENT 재설정은 **전체 테이블에 영향**을 줄 수 있음
- **동시성 문제**로 인한 중복 키 오류 가능성


## **결론**

특정 순서의 프라이머리키를 삭제하면 **기본적으로는 동일한 번호로 자동 재생성이 불가능**하지만, AUTO_INCREMENT 값을 수동으로 재설정하거나 직접 번호를 지정하면 **동일한 번호로 재생성이 가능**합니다. 다만 데이터 무결성과 일관성을 고려하여 신중하게 사용해야 합니다.

<div style="text-align: center">⁂</div>

---

# 왜 재생성이 불가능하게 설계되었는가

AUTO_INCREMENT가 삭제된 번호를 재사용하지 않도록 설계된 이유는 **데이터 무결성과 시스템 안정성을 보장하기 위함**입니다.

## **주요 설계 이유들**

### **1. 참조 무결성 보호**

삭제된 ID를 재사용하면 **외래키 참조 관계에서 심각한 문제**가 발생할 수 있습니다[^26_1]. 예를 들어:

- 사용자 ID 3번이 삭제된 후 새로운 사용자가 3번을 받으면
- 기존에 3번 사용자와 연결된 주문, 댓글, 로그 등이 새로운 사용자와 연결됨
- 이는 **데이터의 일관성을 심각하게 훼손**


### **2. 동시성 문제 해결**

여러 클라이언트가 동시에 데이터를 삽입할 때 **중복 키 오류를 방지**하기 위함입니다[^26_1]. 만약 삭제된 번호를 재사용한다면:

- 여러 클라이언트가 같은 삭제된 번호를 동시에 사용하려 할 수 있음
- 복잡한 동기화 메커니즘이 필요해짐
- 성능 저하와 데드락 위험 증가


### **3. 감사 추적(Audit Trail) 보장**

**로그와 감사 기록의 일관성**을 유지하기 위함입니다:

- 삭제된 ID가 재사용되면 과거 로그 기록과 혼동 발생
- 시스템 복구나 데이터 추적 시 문제 발생
- 규정 준수(Compliance) 요구사항 위반 가능성


### **4. 시스템 단순성과 성능**

**단순하고 빠른 ID 생성**을 위함입니다[^26_2]:

- 마지막 최대값에서 1만 증가시키면 되므로 매우 빠름
- 삭제된 번호를 추적하고 관리하는 복잡한 로직 불필요
- B-tree 인덱스에서 **순차적 삽입으로 인한 성능 최적화**[^26_2]


### **5. 데이터베이스 엔진의 내부 최적화**

MySQL InnoDB 같은 엔진은 **순차적 증가하는 PK를 전제로 최적화**되어 있습니다[^26_4]:

- 클러스터드 인덱스가 물리적으로 정렬된 상태 유지
- 페이지 분할 최소화로 성능 향상
- 인덱스 재구성 비용 절약[^26_2]


## **비즈니스적 고려사항**

### **보안과 예측 가능성**

연속된 번호는 **데이터 규모 추정을 어렵게 만듭니다**[^26_3]:

- 삭제로 인한 번호 공백이 실제 데이터 수를 숨김
- 경쟁사가 비즈니스 규모를 정확히 파악하기 어려움


### **확장성 고려**

**샤딩이나 파티셔닝 시 유리**합니다[^26_2]:

- 시간 순서대로 정렬된 데이터로 분할 기준 명확
- 오래된 데이터와 최신 데이터 구분 용이


## **결론**

AUTO_INCREMENT가 삭제된 번호를 재사용하지 않는 설계는 **"단순함이 복잡함을 이긴다"**는 원칙의 결과입니다. 약간의 저장 공간을 포기하는 대신 **데이터 무결성, 성능, 안정성**이라는 훨씬 중요한 가치들을 보장하는 현명한 설계 선택입니다.

만약 정말로 연속된 번호가 필요하다면, 별도의 **논리적 순서 번호**를 관리하는 것이 물리적 PK를 재사용하는 것보다 안전한 접근법입니다.

<div style="text-align: center">⁂</div>

[^26_1]: https://velog.io/@jadenkim5179/Primary-Key-AUTOINCREMENT를-사용하는-이유

[^26_2]: https://systemdata.tistory.com/84

[^26_3]: https://americanopeople.tistory.com/378

[^26_4]: https://hodongman.github.io/2019/01/14/Database-PK를-사용해야-하는-이유.html

[^26_5]: https://stir.tistory.com/294

[^26_6]: https://rachel0115.tistory.com/entry/PK-생성-전략-선택하기

[^26_7]: https://ssdragon.tistory.com/162

[^26_8]: https://statuscode.tistory.com/143

[^26_9]: https://www.devkobe24.com/DB/2025-02-06-auto-increment-2.html

[^26_10]: https://vocozone.tistory.com/39


---

# -- p02.sql

-- practice db 이동
USE practice;
-- userinfo 테이블에 진행 (p01 실습에서 진행했던 테이블)
DESC userinfo;
-- 데이터 5건 넣기 (별명, 핸드폰) -> 별명 bob 을 포함하세요 C
INSERT INTO userinfo(nickname, phone) VALUES
('ant', 01011112222),
('bob', 01022223333),
('cat', 01033334444),
('dog', 01044445555),
('eli', 01055556666);

-- 전체 조회 (중간중간 계속 실행하면서 모니터링) R
SELECT * FROM userinfo;
-- id가 3 인 사람 조회 R
SELECT * FROM userinfo WHERE id=3;
-- 별명이 bob 인 사람 조회 R
SELECT * FROM userinfo WHERE nickname='bob';
-- 별명이 bob 인 사람의 핸드폰 번호를 01099998888 로 수정 (id로 수정) U
UPDATE userinfo SET phone=01099998888 WHERE id=2;
UPDATE userinfo SET phone='01055556666' WHERE id=5;
-- 별명이 bob 인 사람 삭제 (id로 수정) D
DELETE FROM userinfo WHERE id=6;

위 상황에서 지워진  id=2 의 bob파일이 update 가능하다
어째서 삭제된 파일이 수정가능한걸까

코드 분석 결과를 보면, 실제로는 **id=2인 bob이 삭제되지 않았기 때문**입니다.

## **문제 상황 분석**

### **실제 실행된 쿼리**

```sql
-- bob을 삭제하려고 했지만
DELETE FROM userinfo WHERE id=6;  -- id=6을 삭제함
```


### **의도했던 쿼리**

```sql
-- 실제로는 이렇게 실행되어야 했음
DELETE FROM userinfo WHERE id=2;  -- bob의 실제 id는 2번
```


## **왜 이런 일이 발생했는가**

### **데이터 삽입 순서**

```sql
INSERT INTO userinfo(nickname, phone) VALUES 
('ant', 01011112222),    -- id=1
('bob', 01022223333),    -- id=2 ← bob의 실제 id
('cat', 01033334444),    -- id=3
('dog', 01044445555),    -- id=4
('eli', 01055556666);    -- id=5
```


### **잘못된 삭제 쿼리**

- **의도**: bob(id=2)을 삭제하려고 함
- **실제**: `DELETE FROM userinfo WHERE id=6;` 실행
- **결과**: id=6은 존재하지 않으므로 **아무것도 삭제되지 않음**


## **결론**

**id=2인 bob은 전혀 삭제되지 않았기 때문에** UPDATE가 가능한 것입니다.

### **올바른 삭제 방법**

```sql
-- bob을 실제로 삭제하려면
DELETE FROM userinfo WHERE id=2;
-- 또는
DELETE FROM userinfo WHERE nickname='bob';
```

이는 SQL에서 흔히 발생하는 실수로, **WHERE 조건을 잘못 지정**하여 의도한 레코드가 삭제되지 않은 경우입니다. 삭제된 레코드는 당연히 수정할 수 없지만, 이 경우는 애초에 삭제가 되지 않았기 때문에 수정이 가능한 것입니다.

<div style="text-align: center">⁂</div>

---

# -- p02.sql

-- practice db 이동
USE practice;
-- userinfo 테이블에 진행 (p01 실습에서 진행했던 테이블)
DESC userinfo;
-- 데이터 5건 넣기 (별명, 핸드폰) -> 별명 bob 을 포함하세요 C
INSERT INTO userinfo(nickname, phone) VALUES
('ant', 01011112222),
('bob', 01022223333),
('cat', 01033334444),
('dog', 01044445555),
('eli', 01055556666);

-- 전체 조회 (중간중간 계속 실행하면서 모니터링) R
SELECT * FROM userinfo;
-- id가 3 인 사람 조회 R
SELECT * FROM userinfo WHERE id=3;
-- 별명이 bob 인 사람 조회 R
SELECT * FROM userinfo WHERE nickname='bob';
-- 별명이 bob 인 사람의 핸드폰 번호를 01099998888 로 수정 (id로 수정) U
UPDATE userinfo SET phone=01099998888 WHERE id=2;
UPDATE userinfo SET phone='01055556666' WHERE id=5;
-- 별명이 bob 인 사람 삭제 (id로 수정) D
DELETE FROM userinfo WHERE id=2;

===

위 상황에서 지워진 id=2 의 bob파일이 update 가능하다
어째서 삭제된 파일이 수정가능한걸까

코드를 다시 자세히 분석해보니, **실행 순서**에 문제가 있습니다.

## **실제 실행 순서 분석**

### **1. 데이터 삽입**

```sql
INSERT INTO userinfo(nickname, phone) VALUES 
('ant', 01011112222),    -- id=1
('bob', 01022223333),    -- id=2
('cat', 01033334444),    -- id=3
('dog', 01044445555),    -- id=4
('eli', 01055556666);    -- id=5
```


### **2. UPDATE가 DELETE보다 먼저 실행됨**

```sql
-- 이 UPDATE가 먼저 실행됨
UPDATE userinfo SET phone=01099998888 WHERE id=2;  -- bob 수정됨

-- 그 다음에 DELETE가 실행됨  
DELETE FROM userinfo WHERE id=2;  -- bob 삭제됨
```


## **왜 UPDATE가 가능했는가**

**UPDATE 실행 시점**에는 **아직 bob(id=2)이 삭제되지 않았기 때문**입니다.

### **시간 순서로 정리하면:**

1. **INSERT**: bob(id=2) 생성됨
2. **UPDATE**: bob(id=2)의 phone을 수정함 ✅ (이때는 아직 존재함)
3. **DELETE**: bob(id=2)를 삭제함 ✅

## **만약 순서를 바꾸면?**

```sql
-- 만약 이 순서로 실행했다면
DELETE FROM userinfo WHERE id=2;  -- bob 먼저 삭제
UPDATE userinfo SET phone=01099998888 WHERE id=2;  -- ❌ 오류 발생
```

이 경우 UPDATE는 **"0 rows affected"** 메시지가 나오며 실제로는 아무것도 수정되지 않습니다.

## **결론**

**삭제된 레코드는 수정할 수 없습니다.** 하지만 이 경우는 **UPDATE가 DELETE보다 먼저 실행되었기 때문에** 수정이 가능했던 것입니다. SQL 스크립트에서는 **명령어가 위에서 아래로 순차적으로 실행**되므로, 실행 순서가 매우 중요합니다.

실제로 삭제 후에 수정을 시도하면 다음과 같은 결과를 볼 수 있습니다:

```
Query OK, 0 rows affected (0.00 sec)
Rows matched: 0  Changed: 0  Warnings: 0
```


---

# Query OK, 0 rows affected (0.00 sec)

Rows matched: 0  Changed: 0  Warnings: 0

위와 같은 결과는 수정은 안되었지만 녹색이 뜨네

맞습니다! 이는 MySQL의 **정상적인 동작 방식**입니다.

## **왜 녹색(성공)으로 표시되는가**

### **쿼리 실행 자체는 성공**

- SQL 문법이 올바름
- 데이터베이스 연결 정상
- 테이블과 컬럼이 존재함
- **쿼리 실행 과정에서 오류가 없음**


### **"0 rows affected"의 의미**

- **오류가 아닌 정상적인 결과**
- "조건에 맞는 데이터가 없어서 수정할 게 없었다"는 의미
- 시스템 관점에서는 **성공적으로 처리된 작업**


## **MySQL의 결과 표시 방식**

### **녹색 (성공)**

```sql
Query OK, 0 rows affected (0.00 sec)
Rows matched: 0  Changed: 0  Warnings: 0
```

- 쿼리 실행 성공
- 단지 조건에 맞는 데이터가 없었을 뿐


### **빨간색 (오류)**

```sql
ERROR 1146 (42S02): Table 'practice.userinfo2' doesn't exist
```

- 문법 오류, 테이블 없음, 권한 없음 등


## **실제 비교 예시**

### **정상 케이스 (녹색)**

```sql
UPDATE userinfo SET phone='123' WHERE id=999;  -- 존재하지 않는 ID
-- 결과: Query OK, 0 rows affected (녹색)
```


### **오류 케이스 (빨간색)**

```sql
UPDATE userinfo2 SET phone='123' WHERE id=1;   -- 존재하지 않는 테이블
-- 결과: ERROR 1146 (42S02): Table doesn't exist (빨간색)
```


## **개발자가 주의할 점**

이런 특성 때문에 개발할 때는 **affected rows를 확인**해야 합니다:

- **0 rows affected**: 실제로는 아무것도 변경되지 않음
- **1 rows affected**: 정상적으로 1건 수정됨

따라서 **"녹색 = 성공"이지만 "실제 데이터 변경 = 0건"**인 상황입니다. MySQL은 쿼리 실행 자체의 성공/실패와 실제 데이터 변경 여부를 구분해서 표시하는 것입니다.

---

# -- userinfo 에 email 컬럼 추가 40글자 제한, 중복 안됨, 기본값은 ex@gmail.com

ALTER TABLE userinfo ADD COLUMN email VARCHAR(40) UNIQUE DEFAULT 'ex@gmail.com';

뭐가 문제인지 수정방안을 알려줘

이 ALTER TABLE 문에는 **UNIQUE 제약조건과 DEFAULT 값이 충돌하는 문제**가 있습니다.

## **문제점 분석**

### **핵심 문제**

- **UNIQUE 제약조건**: 모든 값이 고유해야 함
- **DEFAULT 값**: 모든 새 레코드에 동일한 값('ex@gmail.com') 할당
- **결과**: 두 번째 레코드부터 중복 값으로 인한 오류 발생


### **오류 상황**

```sql
-- 첫 번째 INSERT는 성공
INSERT INTO userinfo(nickname, phone) VALUES ('user1', '01011111111');
-- email = 'ex@gmail.com' (기본값)

-- 두 번째 INSERT는 실패
INSERT INTO userinfo(nickname, phone) VALUES ('user2', '01022222222');
-- ERROR: Duplicate entry 'ex@gmail.com' for key 'email'
```


## **수정 방안**

### **방안 1: DEFAULT 값을 NULL로 변경 (권장)**

```sql
ALTER TABLE userinfo ADD COLUMN email VARCHAR(40) UNIQUE DEFAULT NULL;
```

- UNIQUE 제약조건에서 NULL은 중복으로 간주되지 않음
- 여러 레코드가 NULL 값을 가질 수 있음


### **방안 2: UNIQUE 제약조건 제거**

```sql
ALTER TABLE userinfo ADD COLUMN email VARCHAR(40) DEFAULT 'ex@gmail.com';
```

- 중복은 허용하되 기본값 유지
- 나중에 필요시 UNIQUE 제약조건 추가 가능


### **방안 3: DEFAULT 값 없이 UNIQUE만 적용**

```sql
ALTER TABLE userinfo ADD COLUMN email VARCHAR(40) UNIQUE;
```

- 기본값 없이 UNIQUE 제약조건만 적용
- INSERT 시 반드시 email 값을 명시해야 함


### **방안 4: 기존 테이블에 이미 데이터가 있는 경우**

```sql
-- 1단계: DEFAULT 없이 컬럼 추가
ALTER TABLE userinfo ADD COLUMN email VARCHAR(40);

-- 2단계: 기존 데이터에 고유한 값 설정
UPDATE userinfo SET email = CONCAT('user', id, '@gmail.com');

-- 3단계: UNIQUE 제약조건 추가
ALTER TABLE userinfo ADD CONSTRAINT uk_email UNIQUE (email);
```


## **권장 해결책**

**방안 1**을 권장합니다:

```sql
ALTER TABLE userinfo ADD COLUMN email VARCHAR(40) UNIQUE DEFAULT NULL;
```

**이유:**

- NULL 값은 UNIQUE 제약조건에 위배되지 않음
- 이후 실제 이메일 주소로 업데이트 가능
- 데이터 무결성 유지
- 유연한 데이터 입력 가능

이렇게 하면 새로운 레코드를 추가할 때 email을 지정하지 않으면 NULL이 들어가고, 명시적으로 이메일을 입력하면 중복 검사가 이루어집니다.

---

# Skip to main contentSkip to footer

Claude
API
Solutions
Research
Commitments
Learn
News
Try Claude
Product
Build and share AI-powered apps with Claude
2025년 6월 26일
●
2 min read
A minimalist illustration on an orange background showing a black line-drawn hand gripping a white classical architectural column.
Today, we’re introducing the ability to build, host, and share interactive AI-powered apps directly in the Claude app. Now developers can iterate faster on their AI apps without worrying about the complexity and cost of scaling for a growing audience.

Build and host Claude-powered apps
Here’s what we built: Claude can now create artifacts that interact with Claude through an API— turning these artifacts into AI-powered apps, where the economics actually work for sharing.

When someone uses your Claude-powered app:

They authenticate with their existing Claude account
Their API usage counts against their subscription, not yours
You pay nothing for their usage
No one needs to manage API keys
Claude writes real code that orchestrates complex AI functionality. You can see it, modify it, and share it freely.

Community ideas
Early users have already used interactive artifacts to build:

AI-powered games with NPCs that remember conversations and adapt to player choices
Learning tools that adjust to individual skill levels and provide personalized tutoring
Data analysis apps where users upload CSVs and ask follow-up questions in natural language
Writing assistants that help with everything from scripts to technical documentation
Agent workflows that orchestrate multiple Claude calls for complex tasks
Getting started
Start building in the Claude app by enabling this new interactive capability. Simply describe what you want to create, and Claude will write the code for you.

As you work together, Claude can debug and improve its own code based on your feedback. Once your app is ready, you can share it instantly through a link—no deployment process needed. Claude takes care of the technical details like prompt engineering, error handling, and orchestration logic, allowing you to focus entirely on bringing your idea to life.

What you can do:

Use a Claude API within your artifacts
Process files and create rich UIs with React
See, fork, and customize any artifact
Current limitations:

No external API calls (yet)
No persistent storage
Limited to a text-based completion API
This capability is available in beta to Free, Pro, and Max plan users.

News

Introducing the Anthropic Economic Futures Program
Jun 27, 2025

News

How People Use Claude for Support, Advice, and Companionship
Jun 27, 2025

News

Turn ideas into interactive AI-powered apps
Jun 26, 2025

Product
Claude overview
Claude Code
Claude team plan
Claude enterprise plan
Claude education plan
Download Claude apps
Claude.ai pricing plans
Claude.ai login
API Platform
API overview
Developer docs
Claude in Amazon Bedrock
Claude on Google Cloud's Vertex AI
Pricing
Console login
Research
Research overview
Economic Index
Claude models
Claude Opus 4
Claude Sonnet 4
Claude Haiku 3.5
Commitments
Transparency
Responsible scaling policy
Security and compliance
Solutions
AI agents
Coding
Customer support
Learn
Anthropic Academy
Customer stories
Engineering at Anthropic
MCP Integrations
Explore
About us
Become a partner
Careers
Events
News
Startups program
Help and security
Status
Availability
Support center
Terms and policies
Privacy choices
Privacy policy
Responsible disclosure policy
Terms of service - consumer
Terms of service - commercial
Usage policy
© 2025 Anthropic PBC

위 내용에 대해서 it용어를 모르는 사람이 이해하기 쉽게 풀어 설명

Claude에서 새롭게 출시한 기능을 IT 용어를 모르는 분들도 쉽게 이해할 수 있도록 설명드리겠습니다.

## **Claude 앱 빌더란 무엇인가요?**

Claude 앱 빌더는 **"AI를 활용한 앱을 누구나 쉽게 만들고 공유할 수 있게 해주는 도구"**입니다. 마치 **"AI 비서가 있는 레고 블록"**처럼, 복잡한 프로그래밍 지식 없이도 원하는 기능을 설명하면 Claude가 직접 앱을 만들어줍니다.

## **어떻게 작동하나요?**

### **1단계: 아이디어 설명**

"게임을 만들고 싶어요" 또는 "학습 도구를 만들고 싶어요"라고 Claude에게 말하면 됩니다.

### **2단계: Claude가 앱 제작**

Claude가 자동으로 **코드를 작성**하고 **앱을 만들어**줍니다. 마치 **"건축가가 설계도를 그리고 집을 지어주는 것"**과 같습니다.

### **3단계: 즉시 공유**

완성된 앱을 **링크 하나**로 다른 사람들과 바로 공유할 수 있습니다.

## **혁신적인 비용 구조**

### **기존 방식의 문제점**

- 앱을 만든 사람이 모든 사용 비용을 부담해야 함
- 사용자가 많아질수록 제작자의 부담 급증
- 결과적으로 무료 공유가 어려움


### **Claude의 새로운 방식**

- **앱 사용자가 자신의 Claude 계정으로 로그인**
- **사용 비용은 각자 자신의 구독료에서 차감**
- **앱 제작자는 비용 부담 없음**

이는 마치 **"카페에서 각자 자신의 커피값을 내는 것"**과 같은 개념입니다.

## **실제 활용 사례들**

### **AI 게임**

- 플레이어와 대화를 기억하는 **똑똑한 게임 캐릭터**
- 플레이어의 선택에 따라 **스토리가 바뀌는 게임**


### **맞춤형 학습 도구**

- 개인의 **실력에 맞춰 문제 난이도 조절**
- **1:1 과외 선생님**처럼 개별 지도


### **데이터 분석 앱**

- **엑셀 파일을 업로드**하면 자동으로 분석
- **일반 언어로 질문**하면 데이터에서 답을 찾아줌


### **글쓰기 도우미**

- 대본, 기술 문서, 창작 등 **다양한 글쓰기 지원**
- **개인 맞춤형 문체와 스타일** 제안


## **기술적 장점들**

### **복잡한 관리 불필요**

- **API 키 관리**: 복잡한 인증 코드 관리 불필요
- **서버 운영**: 컴퓨터 서버 관리 불필요
- **배포 과정**: 앱을 인터넷에 올리는 복잡한 과정 불필요


### **실시간 개선**

- Claude가 **자신이 만든 코드를 스스로 수정**
- 사용자 피드백을 받아 **즉시 개선**


## **현재 제한사항**

### **외부 연결 불가**

아직은 **다른 웹사이트나 서비스와 연결** 불가능

### **저장 공간 없음**

**데이터를 영구적으로 저장**하는 기능 없음

### **텍스트 중심**

주로 **글자 기반 기능**만 지원 (이미지, 동영상 처리 제한적)

## **누가 사용할 수 있나요?**

**무료, 프로, 맥스 플랜** 사용자 모두 **베타 버전**으로 사용 가능합니다. 베타 버전이란 **"시험 운영 중인 새로운 기능"**이라는 의미입니다.

## **왜 혁신적인가요?**

### **진입 장벽 제거**

- 프로그래밍을 모르는 사람도 **AI 앱 제작 가능**
- 복잡한 기술 지식 불필요


### **경제적 부담 해결**

- 앱 제작자가 **사용자 증가를 걱정할 필요 없음**
- **무료 공유 문화** 활성화 가능


### **즉시 실행**

- 아이디어에서 **실제 작동하는 앱까지 몇 분 내 완성**
- **테스트와 개선이 실시간**으로 가능


## **결론**

Claude 앱 빌더는 **"AI 시대의 파워포인트"**라고 할 수 있습니다. 파워포인트가 누구나 쉽게 프레젠테이션을 만들 수 있게 해준 것처럼, Claude 앱 빌더는 누구나 쉽게 **AI 기능이 있는 앱을 만들고 공유**할 수 있게 해주는 도구입니다.

이는 단순히 새로운 기능이 아니라, **AI 앱 개발과 공유의 패러다임을 완전히 바꾸는 혁신**이라고 할 수 있습니다.

<div style="text-align: center">⁂</div>

---

# ALTER TABLE userinfo DROP COLUMN reg_date;

위 명령어를 사용했는데 파란색이 체크되지만
Query OK, 0 rows affected (0.00 sec)
Rows matched: 0  Changed: 0  Warnings: 0이런 식으로 아무것도 영향 받지 않았다고 뜬다면

이는 **완전히 정상적인 동작**입니다! 전혀 문제가 없습니다.

## **왜 "0 rows affected"가 나타나는가**

### **DDL vs DML의 차이**

- **DDL (Data Definition Language)**: 테이블 **구조**를 변경 (CREATE, ALTER, DROP)
- **DML (Data Manipulation Language)**: 테이블 **데이터**를 변경 (INSERT, UPDATE, DELETE)

`ALTER TABLE DROP COLUMN`은 **DDL 명령어**로, **테이블 구조만 변경**하고 **데이터 행(row)에는 직접적인 영향을 주지 않습니다**.

### **"rows affected"의 의미**

- **rows affected**: 실제 데이터 행이 변경된 개수
- 컬럼 삭제는 **구조 변경**이므로 데이터 행 변경 개수는 0개
- 하지만 **컬럼과 그 안의 모든 데이터는 실제로 삭제됨**


## **정상 동작 확인 방법**

### **테이블 구조 확인**

```sql
DESC userinfo;
```

실행하면 `reg_date` 컬럼이 **사라진 것을 확인**할 수 있습니다.

### **다른 DDL 명령어들도 동일**

```sql
ALTER TABLE userinfo ADD COLUMN new_col VARCHAR(50);
-- 결과: Query OK, 0 rows affected

CREATE TABLE test_table (id INT);
-- 결과: Query OK, 0 rows affected
```


## **결론**

**파란색 체크 + "0 rows affected" = 성공적으로 완료됨**

- ✅ 명령어 실행 성공
- ✅ `reg_date` 컬럼 삭제 완료
- ✅ 해당 컬럼의 모든 데이터도 함께 삭제됨
- ✅ 테이블 구조 변경 완료

이는 MySQL의 정상적인 메시지 표시 방식이며, 컬럼이 성공적으로 삭제되었음을 의미합니다.

<div style="text-align: center">⁂</div>

---

# 개발공부를 하면서 기억보다 기록으로 남기는 좋은 방법은 무엇이 있을까

개발 공부를 효과적으로 기록하고 관리하는 방법들을 소개해드리겠습니다.

## **디지털 노트 도구 활용**

### **Obsidian - "제2의 뇌" 구축**

Obsidian은 개발자들에게 특히 추천되는 노트 도구입니다[^33_1]. 핵심 장점은:

- **내부 링크 연결**: 개념들 간의 관계를 시각적으로 연결
- **그래프 뷰**: 지식의 연결망을 그래프로 시각화
- **마크다운 지원**: 코드 블록과 문서 작성에 최적화
- **1,000개 이상의 플러그인**: 다양한 기능 확장 가능


### **기타 디지털 도구들**

- **Notion/Airtable**: 데이터베이스 형태로 학습 내용 체계화[^33_2]
- **Google Sheets/Excel**: 간단한 진도 관리와 체크리스트
- **GitHub**: 코드와 함께 README 파일로 학습 기록


## **효과적인 노트 작성 전략**

### **선별적 기록의 원칙**

모든 것을 기록하지 말고 **USE 기준**을 적용하세요[^33_1]:

- **U**nimportant (중요하지 않은 것)
- **S**elf-explanatory (자명한 것)
- **E**asy to memorize (쉽게 외울 수 있는 것)

이런 내용들은 기록하지 않고, **3년 후에도 유용할 개념들**만 선별해서 기록합니다.

### **질문 중심의 기록법**

단순히 "Virtual DOM이 Real DOM보다 빠르다"라고 기록하는 대신:

- **질문**: "왜 Virtual DOM이 Real DOM보다 빠른가?"
- **답변**: 자신의 언어로 이해한 내용 작성
- **연관 개념**: Virtual DOM, Real DOM 각각에 대한 별도 노트 생성[^33_1]


## **학습 진도 관리 시스템**

### **Trello를 활용한 칸반 보드**

소프트웨어 개발자들이 실제로 사용하는 방법입니다[^33_3]:

- **Ideas**: 배우고 싶은 것들
- **Up Next**: 다음에 학습할 내용
- **In Progress**: 현재 학습 중
- **Done**: 완료된 학습
- **Graveyard**: 포기하거나 보류된 내용


### **학습 저널 작성**

정기적인 반성과 기록을 위한 구조화된 접근법[^33_4]:

- **날짜와 주제**: 언제, 무엇을 학습했는지
- **학습 목표**: 무엇을 달성하려 했는지
- **핵심 내용**: 실제로 배운 것
- **반성**: 어떻게 개선할 수 있는지


## **코드 중심의 기록법**

### **코드 내 주석 활용**

학습 초기에는 코드 자체에 \#주석으로 빠른 메모를 남기는 것이 효과적입니다[^33_5]. 이는 실제 코딩과 학습을 동시에 진행할 수 있게 해줍니다.

### **코드 스니펫 컬렉션**

자주 사용하는 코드 패턴들을 정리해서 **검색 가능한 형태**로 저장합니다[^33_5]:

- 유용한 함수들
- 자주 사용하는 라이브러리 사용법
- 문제 해결 패턴들


## **문서화 모범 사례 적용**

### **마크다운 활용**

개발 문서 작성의 표준인 마크다운을 사용하여[^33_6]:

- 구조화된 헤딩으로 내용 정리
- 코드 블록으로 예제 포함
- 리스트와 표를 활용한 정보 정리


### **API 문서 스타일 적용**

새로 배운 함수나 라이브러리를 API 문서처럼 정리[^33_6]:

- **목적**: 무엇을 하는 함수인가
- **매개변수**: 어떤 입력을 받는가
- **반환값**: 무엇을 돌려주는가
- **사용 예시**: 실제 코드 예제


## **실천을 위한 핵심 원칙**

### **이론보다 실습 중심**

"3년 후에도 유용할 개념"에 집중하고, **실제 문제 해결 과정에서 학습**하는 것이 가장 효과적입니다[^33_1]. 너무 많은 이론적 내용에 매몰되지 말고 **직접 코딩하면서 배우세요**.

### **정기적 업데이트와 복습**

- 학습 기록을 **정기적으로 업데이트**
- 이전 기록들을 **주기적으로 복습**
- 새로운 경험과 **기존 지식을 연결**


### **검색 가능한 형태로 저장**

미래의 자신이 쉽게 찾을 수 있도록 **태그, 카테고리, 키워드**를 활용하여 체계적으로 정리하는 것이 중요합니다[^33_5].

이러한 방법들을 조합하여 자신만의 학습 기록 시스템을 구축하면, 개발 공부의 효율성을 크게 높일 수 있습니다.

<div style="text-align: center">⁂</div>

[^33_1]: https://www.youtube.com/watch?v=IpKG5YX003U

[^33_2]: https://thecodingbus.info/how-to-build-a-learning-progress-tracker/

[^33_3]: https://www.youtube.com/watch?v=J8dsxPSafAE

[^33_4]: https://www.open.edu/openlearn/mod/oucontent/view.php?id=51386\&section=6.1

[^33_5]: https://www.reddit.com/r/learnprogramming/comments/uix9uh/what_is_the_best_way_to_take_notes_while_learning/

[^33_6]: https://www.hatica.io/blog/code-documentation-practices/

[^33_7]: https://www.linkedin.com/advice/3/what-best-techniques-staying-organized-software-zgiwc

[^33_8]: https://www.reddit.com/r/learnprogramming/comments/mumrgn/how_to_plan_and_build_a_programming_project_a/

[^33_9]: https://www.itransition.com/software-development/methodologies

[^33_10]: https://github.com/JoaoTeixeira13/learning-progress-tracker


---

# lf crlf

LF와 CRLF는 **줄바꿈을 표현하는 서로 다른 방식**으로, 운영체제마다 다른 표준을 사용합니다.

## **기본 개념**

### **CR (Carriage Return)**

- **의미**: 커서를 현재 줄의 맨 앞으로 이동
- **코드**: `\r` (ASCII 13, 0x0D)
- **유래**: 타자기에서 캐리지를 왼쪽 끝으로 밀어주는 동작


### **LF (Line Feed)**

- **의미**: 커서를 다음 줄로 이동
- **코드**: `\n` (ASCII 10, 0x0A)
- **유래**: 타자기에서 종이를 한 줄 위로 올리는 동작


### **CRLF (Carriage Return + Line Feed)**

- **의미**: CR과 LF를 조합한 줄바꿈
- **코드**: `\r\n`
- **크기**: 2바이트 (CR 1바이트 + LF 1바이트)


## **운영체제별 사용 현황**

| 운영체제 | 줄바꿈 방식 | 표현 |
| :-- | :-- | :-- |
| Windows | CRLF | `\r\n` |
| Linux/Unix | LF | `\n` |
| macOS (현재) | LF | `\n` |
| 구형 Mac OS | CR | `\r` |

## **왜 이런 차이가 생겼나?**

### **타자기 시대의 유산**

과거 타자기에서는 새로운 줄로 이동하기 위해 **두 가지 동작**이 필요했습니다:

1. **Carriage Return**: 캐리지를 왼쪽 끝으로 이동
2. **Line Feed**: 종이를 한 줄 올려서 다음 줄로 이동

초기 컴퓨터들이 이 방식을 그대로 채택했고, 운영체제마다 다른 선택을 하면서 현재의 차이가 생겼습니다.

## **개발에서의 문제점**

### **협업 시 발생하는 이슈**

```bash
# Git에서 자주 보는 경고 메시지
warning: LF will be replaced by CRLF in main.css
```

- Windows 개발자와 Mac/Linux 개발자가 협업할 때 발생
- **같은 파일이지만 줄바꿈 방식이 달라** Git에서 변경사항으로 인식
- 실제로는 내용이 같지만 **불필요한 커밋**이 생성될 수 있음


### **파일 크기 차이**

- **CRLF**: 줄바꿈마다 2바이트 사용
- **LF**: 줄바꿈마다 1바이트 사용
- 줄바꿈이 많은 파일에서는 **파일 크기가 2배 차이** 날 수 있음


## **해결 방법**

### **VS Code에서 설정 변경**

VS Code 하단에 **"LF" 또는 "CRLF"** 표시를 클릭하여 변경 가능합니다.

### **Git 설정으로 자동 변환**

```bash
# Windows에서 체크아웃 시 CRLF로, 커밋 시 LF로 변환
git config --global core.autocrlf true

# Mac/Linux에서 체크아웃은 그대로, 커밋 시 LF로 변환  
git config --global core.autocrlf input

# 자동 변환 비활성화
git config --global core.autocrlf false
```


### **명령어로 변환**

```bash
# Windows 파일을 Unix 형식으로 변환
dos2unix filename.txt

# Unix 파일을 Windows 형식으로 변환  
unix2dos filename.txt
```


## **권장사항**

### **LF 사용 권장**

대부분의 개발 도구와 코딩 컨벤션에서 **LF 사용을 권장**합니다:

- **Prettier**: LF 사용 권고
- **ESLint**: CRLF 금지 규칙 제공
- **파일 크기 절약**: 더 작은 파일 크기
- **크로스 플랫폼 호환성**: 모든 운영체제에서 지원


### **일관성 유지**

팀 내에서 **하나의 줄바꿈 방식으로 통일**하여 불필요한 충돌을 방지하는 것이 중요합니다.

현재는 대부분의 개발 환경에서 **LF를 표준**으로 사용하고 있으며, Windows에서도 대부분의 개발 도구들이 LF를 잘 지원하므로 **LF 사용을 권장**합니다.

<div style="text-align: center">⁂</div>

[^34_1]: https://velog.io/@dev_yong/CRLF%EC%99%80-LF%EC%B0%A8%EC%9D%B4%EC%9D%98-%EC%9D%B4%ED%95%B4

[^34_2]: https://dev.to/pranjal-barnwal/understanding-line-break-types-cr-lf-lf-and-cr-3lg2

[^34_3]: https://peerlist.io/sunny/articles/why-does-a-new-line-need-two-characters

[^34_4]: https://codeyarns.com/tech/2020-09-23-types-of-line-endings.html

[^34_5]: https://stackoverflow.com/questions/1552749/difference-between-cr-lf-lf-and-cr-line-break-types

[^34_6]: https://thequickadvisor.com/what-is-the-difference-between-cr-and-crlf/

[^34_7]: https://brunch.co.kr/@hongjyoun/97

[^34_8]: https://www.reddit.com/r/git/comments/a8zpr0/what_does_lf_will_be_replaced_by_crlf_mean/

[^34_9]: https://kr.mathworks.com/matlabcentral/answers/296554-how-to-differentiate-between-n-and-cr-lf-when-reading-in-text-files-in-matlab

[^34_10]: https://unix.stackexchange.com/questions/745620/how-to-deal-with-crlf-cr-line-endings

