import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os
from datetime import datetime

CSV_FILE = "books.csv"

# CSV 불러오기 (없으면 새로 생성)
if os.path.exists(CSV_FILE):
    df = pd.read_csv(CSV_FILE)
else:
    df = pd.DataFrame(columns=["title", "author", "publisher", "year", "genre"])

st.title("📚 독서 기록 & 분석 앱")

# ------------------------------
# 입력창 (폼 사용 → 저장 후 자동 초기화)
# ------------------------------
with st.form("book_form", clear_on_submit=True):
    title = st.text_input("책 제목")
    author = st.text_input("저자")
    publisher = st.text_input("출판사")

    # ✅ 출간연도 선택 (1900 ~ 현재 연도)
    current_year = datetime.now().year
    year = st.number_input("출간 연도", min_value=1900, max_value=current_year, value=current_year, step=1)

    genre = st.text_input("장르")

    submitted = st.form_submit_button("저장하기")

if submitted:
    new_row = pd.DataFrame([{
        "title": title,
        "author": author,
        "publisher": publisher,
        "year": int(year),
        "genre": genre
    }])
    df = pd.concat([df, new_row], ignore_index=True)
    df.to_csv(CSV_FILE, index=False)  # ✅ CSV에 저장
    st.success(f"'{title}' 저장 완료!")

# ------------------------------
# 저장된 책 목록 출력
# ------------------------------
st.subheader("📖 저장된 책 목록")
st.dataframe(df)

# ------------------------------
# 통계 분석
# ------------------------------
if not df.empty:
    st.subheader("📊 독서 데이터 분석")

    c1, c2 = st.columns(2)
    with c1:
        st.metric("총 책 권수", len(df))
    with c2:
        st.metric("고유 저자 수", df["author"].fillna("").nunique())

    # 연도별 독서 추이
    if "year" in df.columns and df["year"].notna().any():
        st.markdown("**연도별 독서 추이**")
        year_counts = df["year"].value_counts().sort_index()
        fig, ax = plt.subplots()
        year_counts.plot(kind="bar", ax=ax)
        ax.set_xlabel("출간 연도")
        ax.set_ylabel("읽은 권수")
        st.pyplot(fig)

    # 장르 분포
    if "genre" in df.columns and df["genre"].notna().any():
        st.markdown("**장르별 분포**")
        genre_counts = df["genre"].value_counts()
        fig, ax = plt.subplots()
        genre_counts.plot(kind="barh", ax=ax)
        ax.set_xlabel("읽은 권수")
        ax.set_ylabel("장르")
        st.pyplot(fig)
