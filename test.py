import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud

st.set_page_config(page_title="📚 독서 기록 & 분석 앱", layout="wide")

# 초기 세션 상태 설정
if "books" not in st.session_state:
    st.session_state["books"] = pd.DataFrame(columns=["title", "authors", "publisher", "publishedDate", "categories"])

# 입력값 초기화 함수
def reset_inputs():
    for key in ["title", "authors", "publisher", "categories", "published_date"]:
        if key in st.session_state:
            del st.session_state[key]

# --- 입력 폼 ---
st.header("📖 책 기록하기")
with st.form("book_form"):
    title = st.text_input("책 제목", key="title")
    authors = st.text_input("저자 (여러 명은 ,로 구분)", key="authors")
    publisher = st.text_input("출판사", key="publisher")
    published_date = st.date_input("출간일", key="published_date")
    categories = st.text_input("장르 (여러 개면 ,로 구분)", key="categories")

    submitted = st.form_submit_button("추가하기")
    if submitted:
        new_row = {
            "title": title,
            "authors": authors,
            "publisher": publisher,
            "publishedDate": str(published_date),
            "categories": categories,
        }
        st.session_state["books"] = pd.concat(
            [st.session_state["books"], pd.DataFrame([new_row])],
            ignore_index=True
        )
        st.success(f"✅ '{title}' 저장됨!")
        reset_inputs()
        st.experimental_rerun()

# --- 저장된 책 목록 ---
st.header("📚 저장된 책 목록")
if not st.session_state["books"].empty:
    st.dataframe(st.session_state["books"], use_container_width=True)

    # CSV 다운로드
    csv = st.session_state["books"].to_csv(index=False).encode("utf-8")
    st.download_button("📥 CSV 다운로드", csv, "books.csv", "text/csv")

    # CSV 업로드
    uploaded_file = st.file_uploader("📤 CSV 불러오기", type=["csv"])
    if uploaded_file is not None:
        st.session_state["books"] = pd.read_csv(uploaded_file)
        st.success("✅ CSV 불러오기 완료!")

else:
    st.info("아직 저장된 책이 없습니다. 위 입력창에서 책을 추가해 보세요!")

# --- 분석 ---
if not st.session_state["books"].empty:
    st.header("📊 독서 데이터 분석")
    edited = st.session_state["books"]

    # 출간연도 추출
    edited["year"] = pd.to_datetime(edited["publishedDate"], errors="coerce").dt.year

    # 1. 연도별 독서량 추이
    st.subheader("📈 연도별 독서량 추이")
    year_count = edited["year"].value_counts().sort_index()
    fig, ax = plt.subplots()
    year_count.plot(kind="bar", ax=ax)
    ax.set_xlabel("출간연도")
    ax.set_ylabel("읽은 책 수")
    st.pyplot(fig)

    # 2. 저자 TOP
    st.subheader("👩‍💻 저자 TOP")
    authors_series = edited["authors"].fillna("").apply(
        lambda s: [a.strip() for a in s.split(",") if a.strip()]
    ).explode()
    top_authors = authors_series.value_counts().head(10)
    st.bar_chart(top_authors)

    # 3. 장르 워드클라우드
    st.subheader("🎨 가장 많이 읽은 장르 워드클라우드")
    categories_series = edited["categories"].fillna("").apply(
        lambda s: [c.strip() for c in s.split(",") if c.strip()]
    ).explode()
    text = " ".join(categories_series.dropna())

    if text.strip():
        wc = WordCloud(width=800, height=400, background_color="white").generate(text)
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.imshow(wc, interpolation="bilinear")
        ax.axis("off")
        st.pyplot(fig)
    else:
        st.info("장르 데이터가 부족합니다.")
