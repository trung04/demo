import streamlit as st
import pandas as pd
import os 
from datetime import datetime

st.title("History")


LOG_FILE = "logs.csv"
if not os.path.exists(LOG_FILE):
    pd.DataFrame(columns=["user_id", "movie_id", "action", "timestamp"]).to_csv(LOG_FILE, index=False)

def log_interaction(user_id, movie_id, action):
    timestamp = datetime.now().strftime("%d/%m/%Y %H:%M")
    new_row = pd.DataFrame([{
        "user_id": user_id,
        "movie_id": movie_id,
        "action": action,
        "timestamp": timestamp
    }])
    new_row.to_csv(LOG_FILE, mode="a", header=False, index=False)

    st.success(f"Logged: {user_id}, {movie_id}, {action}, {timestamp}")
# Nhập thông tin
if st.button("Click me"):
   log_interaction(2, 3, "view")


# Hiển thị file log
st.write("📄 Current Logs:")
st.dataframe(pd.read_csv(LOG_FILE))