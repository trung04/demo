# =======================================================
# 📊 PHÂN TÍCH DỮ LIỆU COVID-19 TOÀN CẦU – DASHBOARD 12 BIỂU ĐỒ
# =======================================================

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import folium
from wordcloud import WordCloud
import os, warnings

warnings.filterwarnings("ignore")
sns.set(style="whitegrid")

# ===================== 1️⃣ ĐỌC DỮ LIỆU =====================
df1 = pd.read_csv("covid_countries_data.csv")
df2 = pd.read_csv("covid19_global_processed.csv")

os.makedirs("dashboard", exist_ok=True)

# ===================== 2️⃣ HISTOGRAM - BOX - VIOLIN =====================
plt.figure(figsize=(16,5))

plt.subplot(1,3,1)
sns.histplot(df1['cases'], bins=30, kde=True, color='skyblue')
plt.title('📦 Phân bố số ca mắc (Histogram)')
plt.xlabel('Số ca mắc'); plt.ylabel('Tần suất')

plt.subplot(1,3,2)
sns.boxplot(y=df1['deaths'], color='lightcoral')
plt.title('⚰️ Phân bố số ca tử vong (Boxplot)')
plt.ylabel('Số ca tử vong')

plt.subplot(1,3,3)
sns.violinplot(y=df1['recovered'], color='lightgreen')
plt.title('💚 Phân bố số ca hồi phục (Violin Plot)')
plt.ylabel('Số ca hồi phục')

plt.tight_layout()
plt.savefig("dashboard/1_hist_box_violin.png", dpi=300)
plt.close()

# ===================== 3️⃣ LINE CHART =====================
fig_line = go.Figure()
fig_line.add_trace(go.Scatter(x=df2['date'], y=df2['cases'],
                              mode='lines', name='Ca mắc',
                              line=dict(color='orange', width=2)))
fig_line.add_trace(go.Scatter(x=df2['date'], y=df2['deaths'],
                              mode='lines', name='Ca tử vong',
                              line=dict(color='red', width=2)))
fig_line.update_layout(
    title='📈 Diễn biến COVID-19 toàn cầu theo thời gian',
    xaxis_title='Thời gian',
    yaxis_title='Số ca',
    template='plotly_white',
    hovermode='x unified'
)
fig_line.write_html("dashboard/2_line.html", include_plotlyjs='cdn', full_html=False)

# ===================== 4️⃣ AREA CHART =====================
fig_area = px.area(df2, x='date', y='daily_cases',
                   title='🌊 Số ca mắc mới COVID-19 toàn cầu theo thời gian',
                   color_discrete_sequence=['#3366CC'])
fig_area.write_html("dashboard/3_area.html", include_plotlyjs='cdn', full_html=False)

# ===================== 5️⃣ SCATTER + HỒI QUY =====================
df_scatter1 = df1[['casesPerOneMillion','deathsPerOneMillion']].dropna()
fig_scatter1 = px.scatter(df_scatter1, x='casesPerOneMillion', y='deathsPerOneMillion',
                          trendline='ols', title='📉 Hồi quy: Ca tử vong/M vs Ca mắc/M')
fig_scatter1.write_html("dashboard/4_scatter1.html", include_plotlyjs='cdn', full_html=False)

# ===================== 6️⃣ SCATTER 2 (CA MẮC / NGÀY) =====================
df2['daily_cases'] = pd.to_numeric(df2['daily_cases'], errors='coerce')
df2['daily_deaths'] = pd.to_numeric(df2['daily_deaths'], errors='coerce')
fig_scatter2 = px.scatter(df2, x='daily_cases', y='daily_deaths', trendline='ols',
                          title='🧮 Hồi quy: Ca tử vong/ngày vs Ca mắc/ngày',
                          color_discrete_sequence=['#00CC96'])
fig_scatter2.write_html("dashboard/5_scatter2.html", include_plotlyjs='cdn', full_html=False)

# ===================== 7️⃣ HEATMAP TƯƠNG QUAN =====================
corr = df1[['cases','deaths','recovered','active','tests']].corr()
fig_heatmap = px.imshow(corr, text_auto=True, color_continuous_scale='RdYlGn',
                        title='🔥 Ma trận tương quan giữa các biến COVID-19')
fig_heatmap.write_html("dashboard/6_heatmap.html", include_plotlyjs='cdn', full_html=False)

# ===================== 8️⃣ TREEMAP =====================
df = df1.dropna(subset=['continent','cases'])
fig_treemap = px.treemap(df, path=['continent','country'], values='cases',
                         color='cases', color_continuous_scale='Reds',
                         title='🌍 Treemap - Ca mắc theo châu lục & quốc gia')
fig_treemap.write_html("dashboard/7_treemap.html", include_plotlyjs='cdn', full_html=False)

# ===================== 9️⃣ SUNBURST =====================
fig_sunburst = px.sunburst(df, path=['continent','country'], values='recovered',
                           color='recovered', color_continuous_scale='Greens',
                           title='☀️ Sunburst - Ca hồi phục theo châu lục & quốc gia')
fig_sunburst.write_html("dashboard/8_sunburst.html", include_plotlyjs='cdn', full_html=False)

# ===================== 🔟 BẢN ĐỒ PLOTLY =====================
fig_map = px.scatter_geo(df, locations="countryInfo.iso3", color="continent",
                         hover_name="country", size="cases",
                         projection="natural earth",
                         title="🗺️ Bản đồ COVID-19 toàn cầu – Phân bố ca mắc",
                         color_discrete_sequence=px.colors.qualitative.Bold)
fig_map.write_html("dashboard/9_plotly_map.html", include_plotlyjs='cdn', full_html=False)

# ===================== 1️⃣1️⃣ BẢN ĐỒ FOLIUM =====================
m = folium.Map(location=[20, 0], zoom_start=2, tiles='cartodbpositron')
for _, row in df.iterrows():
    if pd.notna(row['countryInfo.lat']) and pd.notna(row['countryInfo.long']):
        folium.CircleMarker(
            location=[row['countryInfo.lat'], row['countryInfo.long']],
           
            radius=max(2, row['cases'] / 1_000_000),
            color='crimson',
            fill=True,
            fill_opacity=0.6,
            popup=f"{row['country']}: {row['cases']:,} ca"
        ).add_to(m)
m.save("dashboard/10_folium_map.html")

# ===================== 1️⃣2️⃣ WORDCLOUD =====================
word_freq = dict(zip(df1['country'], df1['cases']))
wordcloud = WordCloud(width=1000, height=600,
                      background_color='white', colormap='Reds',
                      max_words=150).generate_from_frequencies(word_freq)
wordcloud_path = "dashboard/11_wordcloud.png"
wordcloud.to_file(wordcloud_path)

# ===================== 🧠 TỰ ĐỘNG KỂ CHUYỆN DỮ LIỆU =====================
total_cases = df1['cases'].sum()
total_deaths = df1['deaths'].sum()
total_recovered = df1['recovered'].sum()
death_rate = (total_deaths / total_cases) * 100 if total_cases > 0 else 0

story = f"""
<div class='story'>
  <h2>🧭 Tóm tắt dữ liệu COVID-19 toàn cầu</h2>
  <p>Tính đến nay, toàn thế giới đã ghi nhận <b>{total_cases:,.0f}</b> ca mắc COVID-19,
  trong đó có <b>{total_deaths:,.0f}</b> ca tử vong và <b>{total_recovered:,.0f}</b> ca hồi phục.
  Tỷ lệ tử vong trung bình trên toàn cầu là <b>{death_rate:.2f}%</b>.</p>
  <p>Dashboard dưới đây sẽ giúp bạn quan sát sự phân bố, diễn biến và mối tương quan
  giữa các chỉ số COVID-19 theo thời gian và khu vực.</p>
</div>
"""

# ===================== 🌐 XUẤT DASHBOARD HTML TỔNG HỢP =====================
dashboard_html = f"""
<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="utf-8">
  <title>📊 Dashboard COVID-19 Toàn Cầu – 12 Biểu Đồ Tổng Hợp</title>
  <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap" rel="stylesheet">
  <style>
    body {{
      font-family: 'Poppins', sans-serif;
      background: linear-gradient(135deg, #f5f7fa, #c3cfe2);
      margin: 0; color: #222;
    }}
    header {{
      background: linear-gradient(to right, #667eea, #764ba2);
      color: white; text-align: center;
      padding: 40px 20px;
      box-shadow: 0 2px 12px rgba(0,0,0,0.1);
    }}
    header h1 {{ font-size: 36px; margin-bottom: 8px; }}
    header p {{ font-size: 17px; opacity: 0.9; }}
    .story {{
      background: #fff; border-radius: 16px;
      box-shadow: 0 4px 18px rgba(0,0,0,0.06);
      max-width: 1000px; margin: 30px auto; padding: 25px;
      font-size: 17px; line-height: 1.6;
    }}
    .container {{
      max-width: 1200px; margin: 40px auto; padding: 0 20px;
    }}
    .card {{
      background: #fff; border-radius: 16px;
      box-shadow: 0 4px 18px rgba(0,0,0,0.06);
      padding: 24px 28px; margin-bottom: 40px;
    }}
    h2 {{ color: #333; font-size: 22px; }}
    iframe {{
      width: 100%; height: 550px;
      border: none; border-radius: 10px; margin-top: 10px;
    }}
    img {{
      width: 100%; border-radius: 10px;
      box-shadow: 0 2px 8px rgba(0,0,0,0.1); margin-top: 10px;
    }}
    footer {{
      text-align: center; padding: 20px;
      font-size: 13px; color: #666;
      margin-top: 50px;
    }}
  </style>
</head>
<body>
  <header>
    <h1>📊 Dashboard COVID-19 Toàn Cầu</h1>
    <p>Phân tích toàn diện: từ phân bố, diễn biến, hồi quy, tương quan đến bản đồ và từ khoá.</p>
  </header>

  {story}

  <div class="container">

    <section class="card">
      <h2>📦 Phân bố dữ liệu (Histogram, Boxplot, Violin)</h2>
      <img src="1_hist_box_violin.png" alt="Histogram-Box-Violin">
    </section>

    <section class="card">
      <h2>📈 Diễn biến COVID-19 theo thời gian</h2>
      <iframe src="2_line.html"></iframe>
      <iframe src="3_area.html"></iframe>
    </section>

    <section class="card">
      <h2>📉 Hồi quy và mối tương quan</h2>
      <iframe src="4_scatter1.html"></iframe>
      <iframe src="5_scatter2.html"></iframe>
      <iframe src="6_heatmap.html"></iframe>
    </section>

    <section class="card">
      <h2>🌍 Phân bố theo châu lục & quốc gia</h2>
      <iframe src="7_treemap.html"></iframe>
      <iframe src="8_sunburst.html"></iframe>
    </section>

    <section class="card">
      <h2>🗺️ Bản đồ COVID-19 toàn cầu</h2>
      <iframe src="9_plotly_map.html"></iframe>
      <iframe src="10_folium_map.html" height="600"></iframe>
    </section>

    <section class="card">
      <h2>☁️ WordCloud – Quốc gia theo số ca mắc</h2>
      <img src="11_wordcloud.png" alt="WordCloud COVID-19">
    </section>
  </div>

  <footer>
    🦠 Báo cáo COVID-19 | Dữ liệu: <a href="https://disease.sh" target="_blank">disease.sh API</a>
  </footer>
</body>
</html>
"""

# Ghi file HTML dashboard
with open("dashboard/index.html", "w", encoding="utf-8") as f:
    f.write(dashboard_html)

print("✅ Đã tạo dashboard đầy đủ 12 biểu đồ tại: dashboard/index.html")
