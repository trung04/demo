import requests
import pandas as pd
import numpy as np
from pprint import pprint
# ===============================
# 1️⃣ LẤY DỮ LIỆU COVID-19 TOÀN CẦU
# ===============================
url = "https://disease.sh/v3/covid-19/historical/all?lastdays=all"
response = requests.get(url)
data = response.json()
# ===============================
# 2️⃣ CHUẨN HÓA DỮ LIỆU
# ===============================
# Chuyển dữ liệu thành DataFrame
df = pd.DataFrame({
    "date": list(data["cases"].keys()),
    "cases": list(data["cases"].values()),
    "deaths": list(data["deaths"].values()),
    "recovered": list(data["recovered"].values())
})

# Chuyển kiểu dữ liệu cho cột ngày
df["date"] = pd.to_datetime(df["date"], format="%m/%d/%y")

# Sắp xếp theo thời gian
df = df.sort_values("date").reset_index(drop=True)
print(df.head())
# # ===============================
# # 3️⃣ XỬ LÝ DỮ LIỆU THIẾU
# # ===============================
# # Điền giá trị thiếu bằng 0, chuyển kiểu dữ liệu phù hợp
df = df.fillna(0).infer_objects(copy=False)

# # ===============================
# # 4️⃣ TẠO CỘT ĐẶC TRƯNG MỚI
# # ===============================
df["daily_cases"] = df["cases"].diff().fillna(0)
df["daily_deaths"] = df["deaths"].diff().fillna(0)
df["daily_recovered"] = df["recovered"].diff().fillna(0)

# # Tỷ lệ tử vong và hồi phục (trên tổng ca mắc)
df["mortality_rate"] = np.where(df["cases"] > 0, df["deaths"] / df["cases"] * 100, 0)
df["recovery_rate"] = np.where(df["cases"] > 0, df["recovered"] / df["cases"] * 100, 0)

# # ===============================
# # 5️⃣ XUẤT FILE CSV
# # ===============================
df.to_csv("test.csv", index=False)
print("✅ Dữ liệu đã được xử lý và lưu vào 'covid19_global_processed.csv'")
print(df.head())

