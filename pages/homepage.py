import streamlit as st
import pandas as pd
from datetime import datetime
import os
import requests
st.title("🎌 Anime Streaming Platform")


# ==========================
# LOAD CLEAN DATA
# ==========================
ANIME_FILE = "clean_anime.parquet"
LOG_FILE = "logs.csv"
if "page" not in st.session_state:
    st.session_state.page = 1


st.subheader("🔥 Recommended For You")


def get_anime_image(name):
    url = f"https://api.jikan.moe/v4/anime?q={name}&limit=1"
    try:
        r = requests.get(url, timeout=5)
        data = r.json()

        # kiểm tra kết quả
        if "data" in data and len(data["data"]) > 0:
            return data["data"][0]["images"]["jpg"]["image_url"]
    except:
        pass
    
    # fallback nếu không tìm thấy
    return "https://picsum.photos/300/400"
@st.cache_data
def fetch_image_cached(name):
    return get_anime_image(name)

anime = pd.read_parquet(ANIME_FILE)

# đảm bảo cột image_url có tồn tại
if "image_url" not in anime.columns:
    anime["image_url"] = "https://via.placeholder.com/300x400?text=No+Image"

# Tạo file log nếu chưa có
if not os.path.exists(LOG_FILE):
    pd.DataFrame(columns=["user_id", "anime_id", "action", "timestamp"]).to_csv(LOG_FILE, index=False)


# ==========================
# LOG FUNCTION
# ==========================
def log_action(user_id, anime_id, action):
    timestamp = datetime.now().strftime("%d/%m/%Y %H:%M")
    new_row = pd.DataFrame([{
        "user_id": user_id,
        "anime_id": anime_id,
        "action": action,
        "timestamp": timestamp
    }])
    new_row.to_csv(LOG_FILE, mode="a", header=False, index=False)


# ==========================
# STATE
# ==========================
if "selected_movie" not in st.session_state:
    st.session_state.selected_movie = None


# ==========================
# UI – LIST VIEW
# ==========================
def show_movie_list():
    # Chọn số phim mỗi trang
    movies_per_page = st.selectbox(
        "Số phim mỗi trang:", [10, 20, 30, 40, 50], index=1
    )

    total_movies = len(anime)
    total_pages = (total_movies - 1) // movies_per_page + 1

    # Đảm bảo page nằm trong phạm vi
    current_page = st.session_state.get("page", 1)
    current_page = max(1, min(current_page, total_pages))
    st.session_state.page = current_page

    # Lấy data của trang hiện tại
    start = (current_page - 1) * movies_per_page
    end = start + movies_per_page
    current_movies = anime.iloc[start:end]

    # In trạng thái trang
    st.write(f"Trang {current_page}/{total_pages}")

    # Hiển thị dạng grid 5 cột
    cols = st.columns(5)
    for i, row in current_movies.iterrows():
        col = cols[i % 5]
        with col:
            # st.image(row["image_url"], width = "stretch")
            # img_url = get_anime_image(row["name"])
            # st.image(img_url, width = "stretch")
            st.write(f"**{row['name']}**")

            if st.button("Xem phim", key=f"btn_{row['anime_id']}"):
                st.session_state.selected_movie = row["anime_id"]
                st.rerun()

    # ================================
    # 🚀 PAGINATION DẠNG SỐ
    # ================================
    st.write("---")
    st.subheader("Trang")

    pagination = st.container()
    with pagination:
        cols = st.columns(10)

        # First page <<
        if cols[0].button("⏮"):
            st.session_state.page = 1
            st.rerun()

        # Previous page <
        if cols[1].button("◀"):
            if current_page > 1:
                st.session_state.page -= 1
                st.rerun()

        # Hiển thị 5 trang xung quanh current
        page_range = 5
        start_page = max(1, current_page - page_range // 2)
        end_page = min(total_pages, start_page + page_range - 1)

        btn_index = 2
        for p in range(start_page, end_page + 1):
            if p == current_page:
                if cols[btn_index].button(f"[{p}]"):
                    pass  # không làm gì
            else:
                if cols[btn_index].button(str(p)):
                    st.session_state.page = p
                    st.rerun()
            btn_index += 1

        # Next page >
        if cols[7].button("▶"):
            if current_page < total_pages:
                st.session_state.page += 1
                st.rerun()

        # Last page >>
        if cols[8].button("⏭"):
            st.session_state.page = total_pages
            st.rerun()

# ==========================
# UI – WATCH PAGE
# ==========================
def show_movie_detail(anime_id):
    movie = anime[anime["anime_id"] == anime_id].iloc[0]

    st.title(f"🎬 {movie['name']}")

    col1, col2 = st.columns([1, 2])

    with col1:
        st.image(movie["image_url"], width = "stretch")

        st.write(f"**Thể loại:** {movie.get('genre', 'N/A')}")
        st.write(f"**Rating:** ⭐ {movie.get('rating', 'N/A')}")
        st.write(f"**Số tập:** {movie.get('episodes', 'N/A')}")

        # Các nút hành động
        if st.button("📺 Watch Now"):
            log_action(1, anime_id, "watch")
            st.success("Đã lưu vào lịch sử xem!")

        if st.button("❤️ Favorite"):
            log_action(1, anime_id, "favorite")
            st.success("Đã thêm vào danh sách yêu thích!")

        if st.button("👆 Click"):
            log_action(1, anime_id, "click")
            st.success("Đã ghi click!")

        if st.button("⬅️ Quay lại Danh sách"):
            st.session_state.selected_movie = None
            st.rerun()

    with col2:
        st.subheader("Mô tả phim")
        st.write(movie.get("description", "Chưa có mô tả cho anime này."))

        st.subheader("▶️ Trailer / Video")
        st.video("https://www.youtube.com/watch?v=OBfz-b79U8w")  # sửa link nếu muốn


# ==========================
# MAIN ROUTER
# ==========================
if st.session_state.selected_movie is None:
    show_movie_list()
else:
    show_movie_detail(st.session_state.selected_movie)
