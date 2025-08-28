import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import datetime

# -------------------------------
# 🔹 기본 설정
# -------------------------------
st.set_page_config(page_title="📚 독서 기록 & 분석 앱", layout="wide")

# --- 세션 초기화 (❗ KeyError 방지)
if "books" not in st.session_state:
    st.session_state["books"] = pd.DataFrame(
        columns=["title", "authors", "publisher", "publishedDate", "categories", "review"]
    )

# -------------------------------
# 🔹 스타일 (글자만 노르스름 톤)
# -------------------------------
st.markdown(
    """
    <style>
    /* 배경 이미지는 그대로 */
    .stApp {
        background-image: url("https://images.unsplash.com/photo-1588580000645-4562a6d2c839?w=600&auto=format&fit=crop&q=60&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8MTJ8fCVFQiU4RiU4NCVFQyU4NCU5QyVFQSVCNCU4MHxlbnwwfHwwfHx8MA%3D%3D");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }

    /* 글자 노르스름 톤 */
    h1, h2, h3, h4, h5, h6, p, label, span, div, .stMarkdown {
        color: #FFF8DC !important;  /* Cornsilk 톤 */
    }

    /* 입력칸 (투명 배경 + 검정 글씨) */
    input, textarea, select {
        background-color: rgba(255, 255, 255, 0.8) !important;
        color: black !important;
    }

    /* 데이터프레임 글자 */
    .stDataFrame div {
        color: #FFF8DC !important;
    }

    /* 버튼 (검정 + 노르스름 글씨) */
    button {
        background-color: black !important;
        color: #FFF8DC !important;
        border-radius: 8px !important;
        border: none !important;
        padding: 0.5em 1em !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# -------------------------------
# 🔹 책 기록 입력
# -------------------------------
st.header("📖 나만의 독서 일기장")

with st.form("book_form", clear_on_submit=True):  
    title = st.text_input("책 제목")
    authors = st.text_input("저자 (여러 명은 ,로 구분)")
    publisher = st.text_input("출판사")
    published_date = st.date_input("출간일", value=datetime.date.today())
    categories = st.text_input("장르 (여러 개면 ,로 구분)")
    review = st.text_area("✍ 한 줄 평")  # ✅ 추가된 부분

    submitted = st.form_submit_button("추가하기")
    if submitted:
        new_row = {
            "title": title,
            "authors": authors,
            "publisher": publisher,
            "publishedDate": str(published_date),
            "categories": categories,
            "review": review,
        }
        st.session_state["books"] = pd.concat(
            [st.session_state["books"], pd.DataFrame([new_row])],
            ignore_index=True
        )
        st.success(f"✅ '{title}' 저장됨!")

# -------------------------------
# 🔹 저장된 책 목록
# -------------------------------
st.header("📚 저장된 책 목록")

if not st.session_state["books"].empty:
    st.dataframe(st.session_state["books"], use_container_width=True)

    # 📥 CSV 다운로드 (utf-8-sig → 글자 깨짐 방지)
    csv = st.session_state["books"].to_csv(index=False).encode("utf-8-sig")
    st.download_button("📥 CSV 다운로드", csv, "books.csv", "text/csv")

    # 📤 CSV 업로드
    uploaded_file = st.file_uploader("📤 CSV 불러오기", type=["csv"])
    if uploaded_file is not None:
        st.session_state["books"] = pd.read_csv(uploaded_file)
        st.success("✅ CSV 불러오기 완료!")

    # 🗑️ 책 삭제 기능
    st.subheader("🗑️ 책 삭제하기")
    book_list = st.session_state["books"]["title"].tolist()
    book_to_delete = st.selectbox("삭제할 책 선택", [""] + book_list)
    if st.button("삭제"):
        if book_to_delete:
            st.session_state["books"] = st.session_state["books"][
                st.session_state["books"]["title"] != book_to_delete
            ]
            st.success(f"✅ '{book_to_delete}' 삭제됨!")
        else:
            st.warning("⚠️ 삭제할 책을 선택하세요.")

else:
    st.info("📌 아직 저장된 책이 없습니다. 위 입력창에서 책을 추가해 보세요!")  

# -------------------------------
# 🔹 분석
# -------------------------------
if not st.session_state["books"].empty:
    st.header("📊 독서 데이터 분석")
    edited = st.session_state["books"].copy()

    # 출간연도 추출
    edited["year"] = pd.to_datetime(edited["publishedDate"], errors="coerce").dt.year

    col1, col2 = st.columns(2)

    # 1. 연도별 독서량 추이
    with col1:
        st.subheader("📈 Books per Year")
        year_count = edited["year"].value_counts().sort_index()
        fig, ax = plt.subplots(figsize=(5, 3))  # ✅ 크기 줄임
        year_count.plot(kind="bar", ax=ax)
        ax.set_xlabel("Year")
        ax.set_ylabel("Books Read")
        st.pyplot(fig)

    # 2. 저자 TOP 10
    with col2:
        st.subheader("👩‍💻 Top 10 Authors")
        authors_series = edited["authors"].fillna("").apply(
            lambda s: [a.strip() for a in s.split(",") if a.strip()]
        ).explode()
        top_authors = authors_series.value_counts().head(10)
        fig, ax = plt.subplots(figsize=(5, 3))  # ✅ 크기 줄임
        top_authors.plot(kind="barh", ax=ax)
        ax.set_xlabel("Number of Books")
        ax.set_ylabel("Author")
        st.pyplot(fig)
