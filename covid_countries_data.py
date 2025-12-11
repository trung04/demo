import requests
import pandas as pd
url = "https://disease.sh/v3/covid-19/countries"

try:
    response = requests.get(url)
    response.raise_for_status()  # kiểm tra lỗi HTTP
    data = response.json()
    print(f"✅ Lấy dữ liệu thành công! Tổng số quốc gia: {len(data)}")
except Exception as e:
    print("❌ Lỗi khi lấy dữ liệu:", e)
    data = []

# =========================
# 2️⃣ CHUẨN HÓA & TIỀN XỬ LÝ DỮ LIỆU
# =========================
if data:
    df = pd.json_normalize(data)
    
    # Chọn các cột chính
    columns = ['country', 'cases', 'todayCases', 'deaths', 'todayDeaths', 
               'recovered', 'active', 'critical', 'casesPerOneMillion', 
               'deathsPerOneMillion', 'population', 
               'countryInfo.lat', 'countryInfo.long']
    pd.set_option('future.no_silent_downcasting', True)

    df = df.drop(columns=['updated'])
    df = df.fillna(0)
    # 3️⃣ TẠO CỘT ĐẶC TRƯNG MỚI
    df['mortality_rate'] = (df['deaths'] / df['cases'].replace(0, pd.NA)) * 100
    df['recovery_rate'] = (df['recovered'] / df['cases'].replace(0, pd.NA)) * 100
    df['cases_per_million'] = df['cases'] / (df['population'].replace(0, pd.NA) / 1e6)
    df = df.fillna(0)
    # 4️⃣ XUẤT RA FILE CSV
    output_file = "covid19_global_processed.csv"
    df.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"📁 Dữ liệu đã được lưu thành công vào file: {output_file}")
    # Hiển thị 5 dòng đầu tiên để kiểm tra
    print(df.head())

else:
    print("⚠️ Không có dữ liệu để xử lý.")


    