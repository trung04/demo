import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import streamlit as st
import numpy as np
import os
# hàm tải dữ liệu
@st.cache_data
def load_data():
    anime = pd.read_parquet("anime.parquet")
    rating = pd.read_parquet("rating.parquet")
    return rating, anime

# hàm tiền xử lý dữ liệu anime
@st.cache_data
def preprocess_missing_values(anime):
    anime = anime[~np.isnan(anime["rating"])]
    anime["genre"] = anime["genre"].fillna(anime["genre"].mode()[0])
    anime["type"] = anime["type"].fillna(anime["type"].mode()[0])
    anime["combined"] = (
        anime["genre"].str.replace(",", " ", regex=False) + " " +
        anime["type"]
    )
    return anime

# hàm loại bỏ đánh giá không hợp lệ
@st.cache_data
def delete_invalid_ratings(rating):
    rating_clean = rating[rating["rating"] != -1]
    return rating_clean

# hàm loại bỏ dữ liệu trùng lặp
@st.cache_data
def preprocess_duplicate(anime,rating):
    anime_clean = anime.drop_duplicates(subset=["anime_id"])
    rating_clean = rating.drop_duplicates()
    return anime_clean, rating_clean

# hàm hợp dữ liệu rating và anime
@st.cache_data
def merge_data(rating_clean, anime_clean):
    merged = rating_clean.merge(anime_clean, on="anime_id", how="inner")
    merged = merged.rename(columns={
        "rating_x": "user_rating",
        "rating_y": "anime_avg_rating",
        "name": "anime_name",
        "genre": "anime_genre"
    })
    return merged

# hàm xây dựng TF-IDF và ma trận cosine similarity  
@st.cache_resource
def build_tfidf(anime_cb):
    tfidf = TfidfVectorizer(stop_words="english")
    tfidf_matrix = tfidf.fit_transform(anime_cb["combined"])
    cosine_sim = cosine_similarity(tfidf_matrix)
    return tfidf, tfidf_matrix, cosine_sim