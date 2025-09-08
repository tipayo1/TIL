try:
    with open(__file__, "r", encoding="utf-8") as f:
        # 파일 내용을 읽고 그대로 출력합니다.
        code = str(f.read())
except Exception as e:
    print(f"파일을 읽는 중 오류가 발생했습니다: {e}")

print(code)
