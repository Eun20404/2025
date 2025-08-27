import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import datetime

st.set_page_config(page_title="📚 나만의 독서 일기장", layout="wide")

st.markdown(
    """
    <style>
    /* ------------------------------
       전체 앱 배경 & 기본 글자
    ------------------------------ */
    .stApp {
        background-image: url("https://images.unsplash.com/photo-1521587760476-6c12a4b040da?w=1200&auto=format&fit=crop&q=80&ixlib=rb-4.1.0"); /* 도서관 이미지 */
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        position: relative;
        color: #ffffff !important;  /* 기본 글자색 = 흰색 */
    }

    /* 배경 위 반투명 레이어 */
    .stApp::before {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background-color: rgba(0, 0, 0, 0.4);
        z-index: 0;
    }
    .stApp > div {
        position: relative;
        z-index: 1;
    }

    /* ------------------------------
       제목 (h1~h6)
    ------------------------------ */
    h1, h2, h3, h4, h5, h6 {
        color: #ffffff !important;
    }

    /* ------------------------------
       입력칸 제목 (label)
    ------------------------------ */
    label, .stTextInput label, .stDateInput label, 
    .stSelectbox label, .stFileUploader label {
        color: #ffffff !important;
    }

    /* ------------------------------
       데이터프레임 테이블
    ------------------------------ */
    .stDataFrame {
        background: rgba(0, 0, 0, 0.5);
        border-radius: 10px;
        padding: 10px;
    }
    .stDataFrame thead th, .stDataFrame tbody td {
        color: #ffffff !important;
    }

    /* ------------------------------
       버튼 스타일
    ------------------------------ */
    /* 모든 버튼 기본 */
    .stButton>button, .stDownloadButton>button, 
    .stFileUploader>button, .stForm button {
        border-radius: 8px;
        padding: 0.5em 1em;
        transition: 0.3s;
        font-weight: bold;
    }

    /* 추가하기 & 삭제 같은 일반 버튼 → 검정색 */
    .stForm button, .stButton>button {
        background-color: #000000 !important;
        color: #ffffff !important;
        border: 1px solid #000000 !important;
    }
    .stForm button:hover, .stButton>button:hover {
        background-color: #222222 !important;
        border: 1px solid #ffffff !important;
    }

    /* 다운로드 & 업로드 버튼 → 투명 배경 + 흰색 테두리 */
    .stDownloadButton>button, .stFileUploader>button {
        color: #ffffff !important;
        border: 1px solid #ffffff !important;
        background: transparent !important;
    }
    .stDownloadButton>button:hover, .stFileUploader>button:hover {
        background: rgba(255, 255, 255, 0.2) !important;
    }

    /* ------------------------------
       알림 메시지 (info, warning, success 등)
    ------------------------------ */
    .stAlert, .stAlert div, .stAlert span {
        color: #ffffff !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- 초기 세션 상태 ---
if "books" not in st.session_state:
    st.session_state["books"] = pd.DataFrame(
        columns=["title", "authors", "publisher", "publishedDate", "categories"]
    )

# --- 책 기록 입력 ---
st.header("📖 나만의 독서 일기장")
with st.form("book_form", clear_on_submit=True):  # ✅ 제출 후 자동 초기화
    title = st.text_input("책 제목")
    authors = st.text_input("저자 (여러 명은 ,로 구분)")
    publisher = st.text_input("출판사")
    published_date = st.date_input("출간일", value=datetime.date.today())  # ✅ 오늘 날짜 기본값
    categories = st.text_input("장르 (여러 개면 ,로 구분)")

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

# --- 저장된 책 목록 ---
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
    st.info("아직 저장된 책이 없습니다. 위 입력창에서 책을 추가해 보세요!")

# --- 분석 ---
if not st.session_state["books"].empty:
    st.header("📊 독서 데이터 분석")
    edited = st.session_state["books"].copy()

    # 출간연도 추출
    edited["year"] = pd.to_datetime(edited["publishedDate"], errors="coerce").dt.year

    # 1. 연도별 독서량 추이
    st.subheader("📈 연도별 독서량 추이")
    year_count = edited["year"].value_counts().sort_index()
    fig, ax = plt.subplots()
    year_count.plot(kind="bar", ax=ax)
    ax.set_xlabel("Publication year")   # ✅ 가로축
    ax.set_ylabel("Number of books read")  # ✅ 세로축
    st.pyplot(fig)

    # 2. 저자 TOP 10
    st.subheader("👩‍💻 저자 TOP 10")
    authors_series = edited["authors"].fillna("").apply(
        lambda s: [a.strip() for a in s.split(",") if a.strip()]
    ).explode()
    top_authors = authors_series.value_counts().head(10)
    st.bar_chart(top_authors)
