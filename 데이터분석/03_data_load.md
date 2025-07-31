```markdown
# 🎯 오늘 학습한 핵심 내용 TIL

# 📂 파일 로드 및 저장 (CSV)

### 텍스트 인코딩 주의
- EUC-KR, UTF-8 등 인코딩을 지정하지 않으면 한글 깨짐 가능성 있음.

---

## 파일 직접 열기
```
with open('./namsan.csv', encoding='EUC-KR') as f:
    print(f.readline())
```

---

## pandas로 불러오기
```
import pandas as pd

df = pd.read_csv('./namsan.csv', encoding='EUC-KR', dtype={'ISBN': str, '세트 ISBN': str})
```

---

## 저장
```
df.to_csv('./test.csv', encoding='utf-8', index=False)
```

---

# ❓ 결측치 처리

## ✅ 확인
```
df.isna()            # True/False 확인
df.isna().sum()      # 컬럼별 결측치 개수
df.isna().mean() * 100  # 컬럼별 결측치 비율(%)
```

## ✅ 마스킹
```
mask_has_na = df.isna().any(axis=1)  # 결측치가 있는 행 마스크
mask_no_na = df.notna().all(axis=1)  # 결측치가 없는 행 마스크

df[mask_has_na]   # 결측치 있는 행만 추출
df[mask_no_na]    # 결측치 없는 행만 추출
```

## ✅ 시각화
```
import seaborn as sns
import matplotlib.pyplot as plt

sns.heatmap(df.isna(), cmap='viridis', cbar=False)
plt.show()

df.isna().sum().plot(kind='bar')
plt.show()
```

## ✅ 결측치 삭제
```
df.dropna()                        # 결측치 있는 모든 행 삭제
df.dropna(subset=['이름', '성별'])   # 특정 열 기준 결측치 행 삭제
df.dropna(axis=1)                  # 결측치 있는 열 삭제
```

## ✅ 결측치 채우기
```
df.fillna(0)  # 모든 결측치 0으로 채우기

# 컬럼별로 다른 값으로 채우기
df.fillna({'이름': '익명', '급여': df['급여'].mean()})

# 앞/뒤 행 값으로 채우기
df.ffill()  # forward fill
df.bfill()  # backward fill
```

## ✅ 보간법 (interpolation)
```
df.interpolate(method='linear')  # 선형 보간 (시간 무시)
df.interpolate(method='time')    # 시간 보간 (인덱스가 datetime이어야 함)
```

---

# 🔠 문자열 처리 & 타입 변환

## ✅ 문자열 메서드
```
df['이메일'].str.upper()                         # 대문자 변환
df['이메일'].str.contains('gmail')               # 특정 문자열 포함 여부
df['전화번호'].str.replace('-', '').str.replace(' ', '')  # 특수문자 및 공백 제거
```

## ✅ 문자열 추출 및 분할
```
df['이메일'].str.extract(r'@([^.]+)')            # 도메인만 추출
df['이메일'].str.split('@', expand=True)         # 사용자명, 도메인 분리하여 DataFrame으로 반환
```

## ✅ 타입 변환
```
df['정수형'] = df['정수형'].astype(int)
df['실수형'] = df['실수형'].astype(float)
df['불리언'] = df['불리언'].astype(bool)
df['날짜'] = pd.to_datetime(df['날짜'])

# 변환 실패 시 NaN 처리
pd.to_numeric(df['혼합형'], errors='coerce')

# 변환 실패 시 원래 데이터 유지
pd.to_numeric(df['혼합형'], errors='ignore')
```

---

# 🧱 열(Column) 처리

## ✅ 열 삭제
```
df.drop('비고', axis=1)                 # 단일 열 삭제
df.drop(['비고', '임시데이터'], axis=1) # 여러 열 삭제
```

## ✅ 열 이름 변경
```
df.rename(columns={'국어점수': '국어'})  # 특정 열 이름 변경
df.columns = ['국어', '영어', '수학', ... ]  # 전체 열 이름 일괄 변경
```

## ✅ 열 추가
```
df['총점'] = df[['국어', '영어', '수학']].sum(axis=1)
df['성적등급'] = pd.cut(df['평균'], bins=[0, 70, 80,=['D', 'C', 'B', 'A'])
```

---

# 📊 행(Row) 처리

## ✅ 행 삭제
```
df.drop(0)             # 인덱스가 0인 행 삭제
df.drop([0,   # 여러 행 삭제
df.dropna()            # 결측치 있는 행 삭제
df.drop_duplicates()   # 중복된 행 삭제
```

## ✅ 행 필터링 및 정렬
```
df_filtered = df[df['나이'] < 30]                 # 조건에 맞는 행 필터링
df_sorted = df.sort_values('급여', ascending=False)  # 급여 내림차순 정렬

df_sorted.reset_index(drop=True)                   # 인덱스 재설정 (기존 인덱스 삭제)
```
```