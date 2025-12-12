import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from data_manager import load_data, preprocess_missing_values, delete_invalid_ratings, preprocess_duplicate, merge_data, build_tfidf
import altair as alt
import os

st.set_page_config(page_title="Anime Analytics Dashboard", layout="wide")

# ============================
# 1. LOAD DATA
# ============================
rating, anime = load_data()

# ============================
# 1. HEADER
# ============================
st.title("🎌 Anime Analytics Dashboard")
st.caption("✨ Phân tích, trực quan hóa và gợi ý anime dựa trên dữ liệu người dùng")

# ============================
# 2. LÀM SẠCH DỮ LIỆU
# ============================
st.header("🛠️ Làm sạch và chuẩn bị dữ liệu")

colA, colB = st.columns(2)

with colA:
    st.subheader("🔍 Thiếu dữ liệu - Anime")
    missing_anime = anime.isna().sum()
    missing_anime = pd.DataFrame({"Tên cột": anime.columns, "Số lượng thiếu": missing_anime.values})
    st.dataframe(missing_anime, width="stretch")

with colB:
    st.subheader("🔍 Thiếu dữ liệu - Rating")
    missing_rating = rating.isna().sum()
    missing_rating = pd.DataFrame({"Tên cột": rating.columns, "Số lượng thiếu": missing_rating.values})
    st.dataframe(missing_rating, width="stretch")

# # Xử lý dữ liệu
anime = preprocess_missing_values(anime)
after_missing = pd.DataFrame({"Tên cột": anime.columns, "Số lượng thiếu": anime.isna().sum().values})

st.subheader("⚙️ Sau khi xử lý Missing values")
st.dataframe(after_missing, width="stretch")

# Invalid Ratings
rating = delete_invalid_ratings(rating)

# # Duplicate
st.subheader("🧹 Loại bỏ dữ liệu trùng lặp")
before_dup = len(rating)
before_dup_anime = len(anime)
anime_clean,rating_clean = preprocess_duplicate(anime,rating)
after_dup = len(rating_clean)
after_dup_anime = len(anime_clean)


st.success(f"✔ Đã loại {before_dup - after_dup} dòng trùng trong rating.")
st.success(f"✔ Đã loại {before_dup_anime - after_dup_anime} dòng trùng trong anime.")

st.subheader("🔍 Vector hóa dữ liệu IF-IDF")
# # Tạo văn bản kết hợp (genre + type)


# # TF-IDF vectorizer
tfidf, tfidf_matrix = build_tfidf(anime_clean)
sample_tfidf = pd.DataFrame(
    tfidf_matrix[:10, :20].toarray(),
    columns=tfidf.get_feature_names_out()[:20],
    index=anime_clean["name"][:10]
)
st.dataframe(sample_tfidf)


# # ============================
# # 3. GỘP DỮ LIỆU
# # ============================
st.header("📌 Dữ liệu sau khi gộp")
merged = merge_data(rating_clean, anime_clean)
st.dataframe(merged.head(), width="stretch")

# # ============================
# # 4. DASHBOARD
# # ============================
st.header("📊 Phân tích & Trực quan hóa")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈 Phân bố Rating",
    "🏆 Top Anime",
    "🎭 Phân tích Genre",
    "🔥 Heatmap",
    "🤖 Hệ thống gợi ý"
])

# ============================
# TAB 1: PHÂN BỐ RATING
# ============================
with tab1:
    st.subheader("📈 Histogram phân bố Rating")
    chart = (
        alt.Chart(anime_clean)
        .mark_bar(opacity=0.9)
        .encode(
            x=alt.X("rating:Q", bin=alt.Bin(maxbins=20), title="Rating"),
            y=alt.Y("count()", title="Tần suất"),
            tooltip=[
                alt.Tooltip("count()", title="Số lượng"),
                alt.Tooltip("rating:Q", title="Khoảng rating", bin=True)
            ],
        )
        .properties(width="container", height=350, title="Phân bố Rating (Altair)")
    )

    st.altair_chart(chart, width="stretch")

# ============================
# TAB 2: TOP ANIME
# ============================
with tab2:
    st.subheader("🏆 Top Anime theo Rating trung bình")

    top_n = st.slider("Chọn số lượng top:", 5, 30, 15)

    top_anime = (
        anime_clean.sort_values("rating", ascending=False)
        .head(top_n)
        .reset_index(drop=True)
    )
    order = top_anime["name"].tolist()



    st.dataframe(top_anime, width="stretch")

    # Mỗi bar một màu
    top_anime["color_id"] = top_anime.index.astype(str)
    order = top_anime["name"].tolist()
    # Biểu đồ chính
    bars = (
    alt.Chart(top_anime)
    .mark_bar(cornerRadiusTopLeft=6, cornerRadiusTopRight=6)
    .encode(
        x=alt.X("name:N", sort=order),
        y=alt.Y("rating:Q"),
        color=alt.Color("color_id:N", legend=None)
    )
)

    text = (
        alt.Chart(top_anime)
        .mark_text(align="center", baseline="bottom", dy=-4)
        .encode(
            x=alt.X("name:N", sort=order),
            y="rating:Q",
            text="rating:Q"
        )
    )

    # Layer + config
    final_chart = (
        (bars + text)
        .properties(width="container", height=450)
        .configure_view(strokeWidth=0)
        .configure_axis(grid=False)
    )

    st.altair_chart(final_chart, width="stretch")

# # ============================
# # TAB 3: PHÂN TÍCH GENRE
# # ============================
with tab3:
    st.subheader("🎭 Tần suất thể loại Anime")

    # Tách từng genre
    genre_exploded = anime["genre"].dropna().str.split(", ").explode()
    # Đếm tần suất
    genre_count = genre_exploded.value_counts().reset_index()
    genre_count.columns = ["genre", "count"]
    # Chuyển thành format hàng ngang
    genre_row = genre_count.set_index("genre").T

    st.dataframe(genre_row, width="stretch")
    
    

   
    st.subheader("📊 Phân bố thể loại Anime (Altair Bar Chart)")

    chart_bar = (
        alt.Chart(genre_count)
        .mark_bar(cornerRadiusTopLeft=6, cornerRadiusTopRight=6)
        .encode(
            x=alt.X("genre:N", sort="-y", title="Thể loại"),
            y=alt.Y("count:Q", title="Tần suất"),
            color=alt.Color("genre:N", legend=None)
        )
        .properties(width="container", height=400)
    )

    st.altair_chart(chart_bar, width="stretch")
    st.subheader("☁️ WordCloud thể loại Anime")
    # Tạo WordCloud
    genre_text = " ".join(genre_exploded.tolist())
    wordcloud = WordCloud(width=800, height=400, background_color="white").generate(genre_text)
    # Hiển thị WordCloud
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.imshow(wordcloud, interpolation="bilinear")
    ax.axis("off")
    st.pyplot(fig)
    


# # ============================
# # TAB 4: HEATMAP
# # ============================
with tab4:
    st.subheader("🔥 Heatmap Tương Quan")

    corr = merged[["user_rating", "anime_avg_rating", "members"]].corr()

    plt.style.use("seaborn-v0_8")

    fig, ax = plt.subplots(figsize=(7, 5))

    sns.heatmap(
        corr,
        annot=True,
        cmap="coolwarm",
        linewidths=2,        # đường kẻ rõ hơn
        linecolor="white",
        annot_kws={"size": 13, "weight": "bold"},
        cbar_kws={"shrink": 0.7, "aspect": 20},
        square=True
    )

    ax.set_title("Correlation Heatmap", fontsize=16, fontweight="bold", pad=15)

    st.pyplot(fig)

# # ============================
# # TAB 5: RECOMMENDATION SYSTEM
# # ============================
# with tab5:
#     st.subheader("🤖 Hệ thống gợi ý Anime")

#     st.info("Chọn một anime để xem các gợi ý tương tự")

#     anime_list = anime_clean["name"].values
#     selected = st.selectbox("🎬 Chọn một anime:", anime_list)

#     st.write(f"👉 Gợi ý cho **{selected}** sẽ hiển thị tại đây.")
