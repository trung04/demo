import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from data_manager import load_data, preprocess_missing_values, delete_invalid_ratings, preprocess_duplicate, merge_data, build_tfidf

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
# with tab1:
#     st.subheader("📈 Histogram phân bố Rating")

#     fig, ax = plt.subplots(figsize=(8, 5))
#     sns.histplot(data=rating_clean, x="rating", bins=20, kde=True, color="skyblue", ax=ax)
#     ax.set_title("Phân bố Rating", fontsize=14, fontweight="bold")
#     ax.set_xlabel("Rating")
#     ax.set_ylabel("Tần suất")
#     st.pyplot(fig)

# ============================
# TAB 2: TOP ANIME
# ============================
# with tab2:
#     st.subheader("🏆 Top Anime theo Rating trung bình")

#     top_n = st.slider("Chọn số lượng top:", 5, 30, 15)

#     top_anime = (
#         rating_clean_anime.sort_values("rating", ascending=False)
#         .head(top_n)
#         .reset_index(drop=True)
#     )

#     st.dataframe(top_anime, width="stretch")

#     fig, ax = plt.subplots(figsize=(12, 6))
#     bars = ax.bar(top_anime["name"], top_anime["rating"], color=sns.color_palette("tab20", top_n))

#     for bar, rating in zip(bars, top_anime["rating"]):
#         ax.text(
#             bar.get_x() + bar.get_width() / 2,
#             bar.get_height() - 0.4,
#             f"{rating:.2f}",
#             ha="center",
#             color="black",
#             bbox=dict(facecolor="orange", edgecolor="black", boxstyle="round,pad=0.3")
#         )

#     plt.xticks(rotation=90)
#     ax.set_ylabel("Rating")
#     ax.set_title("Top Anime theo Rating", fontsize=14, fontweight="bold")
#     st.pyplot(fig)

# # ============================
# # TAB 3: PHÂN TÍCH GENRE
# # ============================
# with tab3:
#     st.subheader("🎭 Tần suất thể loại Anime")

#     genre_exploded = anime["genre"].dropna().str.split(", ").explode()
#     genre_count = genre_exploded.value_counts()

#     genre_df = pd.DataFrame([genre_count.values], columns=genre_count.index)
#     st.dataframe(genre_df, width="stretch")

#     st.subheader("☁️ WordCloud Genre")

#     wc_text = " ".join(genre_exploded)
#     wordcloud = WordCloud(width=900, height=400, background_color="white").generate(wc_text)

#     fig, ax = plt.subplots(figsize=(12, 6))
#     ax.imshow(wordcloud, interpolation="bilinear")
#     ax.axis("off")
#     st.pyplot(fig)

# # ============================
# # TAB 4: HEATMAP
# # ============================
# with tab4:
#     st.subheader("🔥 Heatmap Tương Quan")

#     corr = merged[["user_rating", "anime_avg_rating", "members"]].corr()

#     fig, ax = plt.subplots(figsize=(6, 4))
#     sns.heatmap(corr, annot=True, cmap="coolwarm", ax=ax)
#     st.pyplot(fig)

# # ============================
# # TAB 5: RECOMMENDATION SYSTEM
# # ============================
# with tab5:
#     st.subheader("🤖 Hệ thống gợi ý Anime")

#     st.info("Chọn một anime để xem các gợi ý tương tự")

#     anime_list = rating_clean_anime["name"].values
#     selected = st.selectbox("🎬 Chọn một anime:", anime_list)

#     st.write(f"👉 Gợi ý cho **{selected}** sẽ hiển thị tại đây.")
