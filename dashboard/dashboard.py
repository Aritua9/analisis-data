import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

day_df = pd.read_csv("dataset/day.csv")
hour_df = pd.read_csv("dataset/hour.csv")


day = day_df.copy()

day['dteday'] = pd.to_datetime(day['dteday'])

season_mapping_reverse = {'Spring': 1, 'Summer': 2, 'Fall': 3, 'Winter': 4}
day['season'] = day['season'].map(season_mapping_reverse).fillna(day['season']).astype(int)

season_map = {
    1: 'Spring',
    2: 'Summer',
    3: 'Fall',
    4: 'Winter'
}

day['season'] = day['season'].map(season_map)

st.sidebar.header("Filter Data")
min_date = day["dteday"].min()
max_date = day["dteday"].max()
 
with st.sidebar:

    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Rentang Waktu',min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )
selected_season = st.sidebar.selectbox("Pilih Musim", ['All'] + sorted(day['season'].unique()))
holiday_mapping = {"All": "All", "Iya": 1, "Tidak": 0}
selected_holiday = st.sidebar.selectbox("Hari Libur", list(holiday_mapping.keys()))

filtered_day = day[(day['dteday'] >= pd.to_datetime(start_date)) & (day['dteday'] <= pd.to_datetime(end_date))]

if selected_season != 'All':
    filtered_day = filtered_day[filtered_day['season'] == selected_season]
if selected_holiday != 'All':
    filtered_day = filtered_day[filtered_day['holiday'] == holiday_mapping[selected_holiday]]

filtered_day = filtered_day.copy()
season_labels = {1: 'Spring', 2: 'Summer', 3: 'Fall', 4: 'Winter'}
day['season'] = day['season'].map(season_labels)

st.title("📊 Bike Sharing Dashboard")
# Hitung statistik per season
df_stat = filtered_day.groupby('season')['cnt'].agg(['sum', 'count', 'mean']).round(2).reset_index()
df_stat = df_stat.rename(columns={'sum': 'total_users', 'count': 'total_days', 'mean': 'avg_users_per_day'})

# Urutkan berdasarkan rata-rata pengguna
df_stat = df_stat.sort_values(by='avg_users_per_day', ascending=False)


season_colors = {
    'Spring': 'yellow',
    'Summer': 'magenta',
    'Fall': 'purple',
    'Winter': 'pink'
}

# Ambil warna berdasarkan musim yang tampil di grafik
colors = [season_colors[season] for season in df_stat['season']]

# Plot
plt.figure(figsize=(8, 5))
bars = plt.bar(df_stat['season'], df_stat['avg_users_per_day'], color=colors)

# Tambah label di atas bar
for bar in bars:
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2., height,
             f'{int(height):,}', ha='center', va='bottom')

# Styling
plt.title("The Impact of Seasons on Bike Usage", pad=10,fontsize=20)
plt.xlabel("Season")
plt.ylabel("Average Users per Day")
plt.grid(axis='y', linestyle='--', alpha=0.5)
plt.tight_layout()
st.pyplot(plt)

# Ganti label hari: 0 -> Hari Biasa, 1 -> Hari Libur
# Ganti label hari: 0 -> Hari Biasa, 1 -> Hari Libur (pada data yang difilter)
filtered_day['holiday_label'] = filtered_day['holiday'].map({0: 'Hari Biasa', 1: 'Hari Libur'})

# Hitung statistik per kategori holiday
df_stat = filtered_day.groupby('holiday_label')['cnt'].agg(
    total_users='sum', total_days='count', avg_users_per_day='mean'
).round(2).reset_index()

# Mapping warna untuk Hari Biasa dan Hari Libur
holiday_colors = {
    'Hari Biasa': 'lightblue',
    'Hari Libur': 'blue'
}

# Ambil warna berdasarkan label yang tampil di df_stat
colors = [holiday_colors[label] for label in df_stat['holiday_label']]

# Plot
plt.figure(figsize=(10, 6))
bars = plt.bar(df_stat['holiday_label'], df_stat['avg_users_per_day'], color=colors)

# Tambah label nilai di atas bar
for bar in bars:
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2., height,
             f'{int(height):,}', ha='center', va='bottom')

# Styling
plt.title("Comparison of Average Bike Users on Weekdays and Holidays", pad=10,fontsize=20)
plt.ylabel("Average Users per Day")
plt.grid(axis='y', linestyle='--', alpha=0.5)

# Info tambahan di bawah
# Cek total hari untuk masing-masing kategori dengan aman
hari_biasa = df_stat.loc[df_stat["holiday_label"] == "Hari Biasa", "total_days"]
hari_libur = df_stat.loc[df_stat["holiday_label"] == "Hari Libur", "total_days"]

# Ambil nilainya, atau 0 kalau tidak ada
hari_biasa_total = int(hari_biasa.values[0]) if not hari_biasa.empty else 0
hari_libur_total = int(hari_libur.values[0]) if not hari_libur.empty else 0

# Tampilkan info tambahan di bawah grafik
plt.figtext(0.02, -0.01,
            f'Total Days:\nWeekdays: {hari_biasa_total} days\n'
            f'Holidays: {hari_libur_total} days',
            fontsize=8)


plt.tight_layout()
st.pyplot(plt)