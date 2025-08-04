# 🎯 오늘 학습한 핵심 내용 TIL

# 🧩 데이터 분석 핵심 요약 노트 (with Pandas)

## 1. 그룹화와 집계 (groupby, agg)  
**목적:** 고객, 상품 등 특정 기준으로 묶어 통계 계산  

```python
# 고객별 총 구매액, 평균 구매액, 구매횟수
df.groupby('고객ID')['구매액'].agg(['sum', 'mean', 'count'])

# 고객별 구매액과 할인률에 여러 집계 함수 적용
df.groupby('고객ID').agg({
    '구매액': ['sum', 'mean'],
    '할인률': ['mean', 'max']
})
```

## 2. 사용자 정의 집계 함수  
**목적:** 기본 함수 외 직접 계산 로직을 넣고 싶을 때  

```python
def 할인총액(price):
    return (price * df.loc[price.index, '할인률']).sum()

df.groupby('고객ID')['구매액'].agg(할인총액)
```

## 3. 그룹별 순위와 누적 계산  
**목적:** 부서 내 순위, 누적 합계, 비율 계산 등  

```python
# 부서별 실적 순위 (1위가 높은 점수)
df['부서순위'] = df.groupby('부서')['월별실적'].rank(method='dense', ascending=False)

# 누적 실적 계산
df['누적합계'] = df.groupby('부서')['월별실적'].cumsum()

# 기여도 = 개인 실적 / 부서 전체 실적
df['부서총합'] = df.groupby('부서')['월별실적'].transform('sum')
df['기여도'] = df['월별실적'] / df['부서총합']
```

## 4. 시계열 분석  
**목적:** 날짜 컬럼에서 유용한 시간 정보 추출하여 분석  

```python
df['주문년월'] = df['주문일자'].dt.strftime('%Y-%m')
df['요일'] = df['주문일자'].dt.day_name()
df['주'] = df['주문일자'].dt.isocalendar().week
```

## 5. 시각화 (Matplotlib / Seaborn)  
**목적:** 분석 결과를 시각적으로 표현  

```python
# 카테고리별 매출 시각화
df.groupby('카테고리')['매출액'].sum().plot(kind='bar')

# 지역 x 카테고리별 매출 히트맵
pivot = df.groupby(['지역', '카테고리'])['매출액'].sum().unstack()
sns.heatmap(pivot, annot=True, fmt='.0f', cmap='YlGnBu')
```

## 6. 데이터 병합 (merge)  
**목적:** 서로 다른 테이블 간 연결 (SQL JOIN과 유사)  

```python
# 상품 정보와 주문 데이터를 상품ID 기준으로 병합
pd.merge(orders, products, on='상품ID', how='left')

# 컬럼 이름 다르면 left_on, right_on 사용
pd.merge(orders, customers, left_on='고객ID', right_on='ID')
```

## 7. 고유값 분석 (nunique)  
**목적:** 고객이 구매한 상품/카테고리 다양성 분석  

```python
df.groupby('고객ID').agg({
    '매출액': ['sum', 'count'],
    '상품ID': 'nunique',     # 구매한 상품 종류 수
    '카테고리': 'nunique'    # 구매한 카테고리 수
})
```

## 8. 매출 트렌드 분석  
**목적:** 시간에 따른 매출 추이 파악  

```python
# 월별 매출 추이
df.groupby('주문년월')['매출액'].sum().plot(marker='o')

# 주별 증감률 계산
weekly = df.groupby(['주문년월', '주'])['매출액'].sum().reset_index()
weekly['매출증감률'] = weekly['매출액'].pct_change().fillna(0)
```
