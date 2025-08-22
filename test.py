import streamlit as st
import pandas as pd
import requests
import matplotlib.pyplot as plt
from wordcloud import WordCloud

# 책 데이터 저장용 CSV
BOOKS_FILE = "books.csv"

# CSV 불러오기
def load_data():
    try:
        return pd.read_csv(BOOKS_FILE)
    except:
        return pd.DataFrame(columns=["제목", "저자", "출판사", "출간연도", "장르", "읽은날짜", "별점", "메모"])

def save_data(df):
    df.to_csv(BOOKS_FILE, index=False)

# 책 검색 (Google Books API)
def search_book(title):
    url = f"https://www.googleapis.com/books/v1/volumes?q={title}"
    response = requests.get(url)
    data = response.json()
    if "items" in data:
        book = data["items"][0]["volumeInfo"]
        return {
            "제목": book.get("title", ""),
            "저자": ", ".join(book.get("authors", [])),
            "출판사": book.get("publisher", ""),
            "출간연도": book.get("publishedDate", "")[:4],
            "장르": ", ".join(book.get("categories", [])) if "categories" in book else ""
        }
    return None

# Streamlit UI
st.title("📚 독서 기록 & 분석 앱")

df = load_data()

# 책 추가하기
st.header("책 추가하기")
title = st.text_input("책 제목을 입력하세요")
if st.button("검색"):
    book_info = search_book(title)
    if book_info:
        st.write(book_info)
        date = st.date_input("읽은 날짜")
        rating = st.slider("별점", 0, 5, 3)
        memo = st.text_area("메모")
        if st.button("저장"):
            new_entry = {**book_info, "읽은날짜": date, "별점": rating, "메모": memo}
            df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
            save_data(df)
            st.success("저장 완료!")
    else:
        st.warning("책을 찾을 수 없습니다.")

# 독서 기록 보기
st.header("내 독서 기록")
st.dataframe(df)

# -------------------------------
# 📊 분석 & 시각화
# -------------------------------
if not df.empty:
    st.header("📈 독서 분석")

    # 1. 연도별 독서량 추이
    if "읽은날짜" in df.columns:
        df["읽은날짜"] = pd.to_datetime(df["읽은날짜"], errors="coerce")
        df["연도"] = df["읽은날짜"].dt.year

        yearly_count = df["연도"].value_counts().sort_index()

        st.subheader("연도별 독서량 추이")
        fig, ax = plt.subplots()
        yearly_count.plot(kind="bar", ax=ax)
        ax.set_xlabel("연도")
        ax.set_ylabel("읽은 책 수")
        st.pyplot(fig)

    # 2. 장르 분포
    if "장르" in df.columns and df["장르"].notnull().any():
        genres = df["장르"].dropna().str.split(",")
        genres = [g.strip() for sublist in genres for g in sublist]  # flatten
        genre_series = pd.Series(genres).value_counts()

        st.subheader("장르 분포")
        fig, ax = plt.subplots()
        genre_series.plot(kind="pie", autopct='%1.1f%%', ax=ax)
        ax.set_ylabel("")
        st.pyplot(fig)

        # 3. 워드클라우드 (장르 기반)
        st.subheader("가장 많이 읽은 장르 워드클라우드")
        wordcloud = WordCloud(width=800, height=400, background_color="white", colormap="Dark2").generate(" ".join(genres))
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.imshow(wordcloud, interpolation="bilinear")
        ax.axis("off")
        st.pyplot(fig)
