import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import datetime

# -------------------------------
# 🔹 스타일 (CSS)
# -------------------------------
st.markdown(
    """
    <style>
    .stApp {
        background-image: url("https://images.unsplash.com/photo-1521587760476-6c12a4b040da?w=1200&auto=format&fit=crop&q=80&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8Mnx8JUVCJThGJTg0JUVDJTg0JTlDJUVBJUI0JTgwfGVufDB8fDB8fHww");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        position: relative;
        color: #fdf5e6 !important;
    }
    .stApp::before {
        content: "";
        position: absolute;
        top: 0; left: 0; right: 0; bottom: 0;
        background-color: rgba(0, 0, 0, 0.45);
        z-index: 0;
    }
    .stApp > div { position: relative; z-index: 1; }

    /* 제목 */
    h1, h2, h3, h4, h5, h6 { color: #ffe4b5 !important; }

    /* 입력칸 라벨 */
    label, .stTextInput label, .stDateInput label, 
    .stSelectbox label, .stFileUploader label {
        color: #fdf5e6 !important;
    }

    /* 입력칸 자체 스타일 */
    .stTextInput>div>div>input, 
    .stDateInput>div>div>input,
    .stTextArea>div>textarea,
    .stSelectbox>div>div {
        background-color: rgba(255, 248, 220, 0.1) !important;  /* Cornsilk 톤 반투명 */
        color: #fdf5e6 !important;   /* 아이보리 글자 */
        border: 1px solid #ffe4b5 !important;  /* 따뜻한 노랑 테두리 */
        border-radius: 6px;
    }
    .stTextInput>div>div>input:focus,
    .stDateInput>div>div>input:focus,
    .stTextArea>div>textarea:focus,
    .stSelectbox>div>div:focus {
        border: 1px solid #fffaf0 !important;  /* 포커스 시 더 밝은색 */
        background-color: rgba(255, 228, 181, 0.15) !important;
    }

    /* 데이터 테이블 */
    .stDataFrame thead th, .stDataFrame tbody td { color: #fdf5e6 !important; }

    /* 버튼 */
    .stForm button, .stButton>button {
        background-color: #2f2f2f !important;
        color: #fffaf0 !important;
        border: 1px solid #ffe4b5 !important;
    }
    .stForm button:hover, .stButton>button:hover {
        background-color: #444444 !important;
        border: 1px solid #fdf5e6 !important;
    }

    /* 다운로드/업로드 버튼 */
    .stDownloadButton>button, .stFileUploader>button {
        color: #fdf5e6 !important;
        border: 1px solid #ffe4b5 !important;
        background: transparent !important;
    }
    .stDownloadButton>button:hover, .stFileUploader>button:hover {
        background: rgba(255, 228, 181, 0.2) !important;
    }

    /* 알림 메시지 */
    .stAlert, .stAlert div, .stAlert span, .stAlert * {
        color: #fdf5e6 !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)
# -------------------------------
# 🔹 책 기록 입력
# -------------------------------
st.header("📖 나만의 독서 일기장")
with st.form("book_form", clear_on_submit=True):  # ✅ 제출 후 자동 초기화
    title = st.text_input("책 제목")
    authors = st.text_input("저자 (여러 명은 ,로 구분)")
    publisher = st.text_input("출판사")
    published_date = st.date_input("출간일", value=datetime.date.today())  # ✅ 오늘 날짜 기본값
    categories = st.text_input("장르 (여러 개면 ,로 구분)")
    review = st.text_input("짧은 한 줄평 ✍️")  # ✅ 추가된 입력 칸

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

    # 📥 CSV 다운로드
    csv = st.session_state["books"].to_csv(index=False).encode("utf-8")
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
# 🔹 독서 데이터 분석
# -------------------------------
if not st.session_state["books"].empty:
    st.header("📊 독서 데이터 분석")
    edited = st.session_state["books"].copy()

    # 출간연도 추출
    edited["year"] = pd.to_datetime(edited["publishedDate"], errors="coerce").dt.year

    # ✅ 두 그래프를 나란히 배치
    col1, col2 = st.columns(2)

    # 1. 연도별 독서량 추이
    with col1:
        st.subheader("📈 연도별 독서량 추이")
        year_count = edited["year"].value_counts().sort_index()
        fig, ax = plt.subplots(figsize=(5, 3))  # ✅ 크기 줄임
        year_count.plot(kind="bar", ax=ax)
        ax.set_xlabel("Publication year")
        ax.set_ylabel(Number of books")
        st.pyplot(fig)

    # 2. 저자 TOP 10
    with col2:
        st.subheader("👩‍💻 저자 TOP 10")
        authors_series = edited["authors"].fillna("").apply(
            lambda s: [a.strip() for a in s.split(",") if a.strip()]
        ).explode()
        top_authors = authors_series.value_counts().head(10)
        fig, ax = plt.subplots(figsize=(5, 3))  # ✅ 크기 줄임
        top_authors.plot(kind="barh", ax=ax)
        ax.set_xlabel("Number of books")
        ax.set_ylabel("Author")
        st.pyplot(fig)
