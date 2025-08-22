from __future__ import annotations
st.metric("총 권수", len(edited))
with stats2:
st.metric("고유 저자 수", edited["authors"].fillna("").apply(lambda s: [a.strip() for a in s.split(",") if a.strip()] ).explode().nunique())
with stats3:
pages = pd.to_numeric(edited["pageCount"], errors="coerce").dropna()
st.metric("총 페이지", int(pages.sum()) if len(pages) else 0)
with stats4:
this_year = str(datetime.today().year)
st.metric("올해 읽은 책", int((edited["date_read"].fillna("").str.startswith(this_year)).sum()))


st.markdown("---")


# -----------------------------
# 분석 대시보드
# -----------------------------
st.subheader("📈 분석 대시보드")


if st.session_state.library.empty:
st.info("데이터가 있어야 분석할 수 있어요. 위에서 책을 추가해 주세요.")
else:
df = st.session_state.library.copy()
df["date_read_parsed"] = pd.to_datetime(df["date_read"], errors="coerce")


st.markdown("#### 📊 월별 독서량 추이")
only_12 = st.toggle("최근 12개월만 보기", value=True)
ts = (
df.dropna(subset=["date_read_parsed"])
.assign(month=lambda x: x["date_read_parsed"].dt.to_period("M").dt.to_timestamp())
.groupby("month").size().rename("count").reset_index()
.sort_values("month")
)
if only_12 and not ts.empty:
cutoff = datetime.today() - relativedelta(months=11)
ts = ts[ts["month"] >= cutoff.replace(day=1)]


if ts.empty:
st.write(":grey[표시할 데이터가 없어요.]")
else:
fig1, ax1 = plt.subplots()
ax1.plot(ts["month"], ts["count"], marker="o")
ax1.set_xlabel("월")
ax1.set_ylabel("권수")
ax1.set_title("월별 읽은 권수")
ax1.grid(True, linestyle=":", alpha=0.4)
st.pyplot(fig1, use_container_width=True)


st.markdown("---")


st.markdown("#### ☁️ 장르/카테고리 워드클라우드")
cats = df["categories"].dropna().astype(str)
tokens: List[str] = []
for c in cats:
parts = [p.strip() for p in c.replace("/", ",").split(",") if p.strip()]
tokens.extend(parts)
if not tokens:
st.write(":grey[장르 정보가 없어 워드클라우드를 만들 수 없어요.]")
else:
freq = pd.Series(tokens).value_counts().to_dict()
wc = WordCloud(width=1000, height=500, background_color="white")
wc.generate_from_frequencies(freq)
fig2, ax2 = plt.subplots(figsize=(10,5))
ax2.imshow(wc, interpolation="bilinear")
ax2.axis("off")
st.pyplot(fig2, use_container_width=True)


st.markdown("---")


st.markdown("#### 🏷️ 가장 많이 읽은 저자/출판사")
top_n = st.slider("TOP N", 3, 15, 5, key="topn")


c1, c2 = st.columns(2)
with c1:
    st.markdown("**저자 TOP**")
    if "Author" in df.columns:
        top_authors = (
            df["Author"]
            .dropna()
            .str.split(",")
            .explode()
            .str.strip()
            .value_counts()
            .head(10)
        )
        st.bar_chart(top_authors)

with c2:
    st.markdown("**출판사 TOP**")
    if "Publisher" in df.columns:
        top_publishers = (
            df["Publisher"]
            .dropna()
            .str.split(",")
            .explode()
            .str.strip()
            .value_counts()
            .head(10)
        )
        st.bar_chart(top_publishers)

