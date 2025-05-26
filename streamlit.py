import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load Data
day_df = pd.read_csv('day_clean.csv')
hour_df = pd.read_csv('hour_clean.csv')
day_df['dteday'] = pd.to_datetime(day_df['dteday'])
hour_df['dteday'] = pd.to_datetime(hour_df['dteday'])

# Gabungkan
combined_df = pd.merge(hour_df, day_df, on='dteday', suffixes=('_hour', '_day'))

# Sidebar
st.sidebar.image('logo/sepeda.png', use_column_width=True)
st.sidebar.header('Filter Interaktif')

tahun_range = st.sidebar.slider('Pilih Rentang Tahun', 2011, 2012, (2011, 2012))

musim_pilihan = st.sidebar.multiselect(
    'Pilih Musim',
    options=[1, 2, 3, 4],
    default=[1, 2, 3, 4],
    format_func=lambda x: {
        1: 'Musim Semi',
        2: 'Musim Panas',
        3: 'Musim Gugur',
        4: 'Musim Dingin'
    }[x]
)

workingday_filter = st.sidebar.multiselect(
    'Pilih Tipe Hari',
    options=[0, 1],
    default=[0, 1],
    format_func=lambda x: 'Hari Libur' if x == 0 else 'Hari Kerja'
)

weathersit_filter = st.sidebar.multiselect(
    'Pilih Kondisi Cuaca',
    options=[1, 2, 3],
    default=[1, 2, 3],
    format_func=lambda x: {
        1: 'Cerah / Sedikit Awan',
        2: 'Mendung / Kabut',
        3: 'Hujan Ringan / Salju Ringan'
    }[x]
)

# Filter
filtered_day = day_df[
    (day_df['dteday'].dt.year.between(tahun_range[0], tahun_range[1])) &
    (day_df['season'].isin(musim_pilihan)) &
    (day_df['workingday'].isin(workingday_filter)) &
    (day_df['weathersit'].isin(weathersit_filter))
]

filtered_combined = combined_df[
    (combined_df['dteday'].dt.year.between(tahun_range[0], tahun_range[1])) &
    (combined_df['season_day'].isin(musim_pilihan)) &
    (combined_df['workingday_day'].isin(workingday_filter)) &
    (combined_df['weathersit_day'].isin(weathersit_filter))
]

st.title('Dashboard Penyewaan Sepeda')

# Visualisasi 1
st.subheader('Rata-rata Penyewaan Sepeda: Musim Panas vs Musim Dingin')
try:
    season_filtered = filtered_day[filtered_day['season'].isin([2, 4])]
    fig1, ax1 = plt.subplots(figsize=(8, 5))
    sns.barplot(data=season_filtered, x='season', y='cnt', hue='yr',
                palette='Set2', ci=None, ax=ax1)
    ax1.set_title('Musim Panas vs Musim Dingin (2011–2012)')
    ax1.set_xlabel('Musim')
    ax1.set_ylabel('Rata-rata Penyewaan')
    ax1.set_xticklabels(['Musim Panas', 'Musim Dingin'])
    ax1.legend(title='Tahun', labels=['2011', '2012'])
    st.pyplot(fig1)
except:
    pass

# Visualisasi 2
st.subheader('Distribusi Penyewaan Sepeda')
try:
    fig2, ax2 = plt.subplots(figsize=(8, 5))
    sns.violinplot(data=season_filtered, x='season', y='cnt', hue='yr',
                   split=True, palette=['#3A6EA5', '#A52A2A'], ax=ax2)
    ax2.set_title('Distribusi Penyewaan Sepeda per Musim')
    ax2.set_xlabel('Musim')
    ax2.set_ylabel('Jumlah Penyewaan')
    ax2.set_xticklabels(['Musim Panas', 'Musim Dingin'])
    handles, labels = ax2.get_legend_handles_labels()
    ax2.legend(handles, ['2011', '2012'], title='Tahun')
    st.pyplot(fig2)
except:
    pass

# Visualisasi 3
st.subheader('Proporsi Penyewaan Hari Kerja vs Libur')
try:
    workday_counts = filtered_combined.groupby('workingday_day')[['registered_day', 'casual_day']].sum()
    total_work = workday_counts.loc[1].sum()
    total_libur = workday_counts.loc[0].sum()
    fig3, ax3 = plt.subplots()
    ax3.pie([total_work, total_libur],
            labels=['Hari Kerja', 'Hari Libur'],
            colors=['#2E8B57', '#A52A2A'],
            autopct='%1.1f%%',
            startangle=90)
    ax3.set_title('Persentase Penyewaan Hari Kerja vs Libur')
    st.pyplot(fig3)
except:
    pass

# Visualisasi 4
st.subheader('Sebaran Penyewaan Hari Kerja vs Libur')
try:
    fig4, ax4 = plt.subplots(figsize=(8, 5))
    sns.stripplot(data=filtered_day, x='workingday', y='cnt', hue='yr',
                  dodge=True, palette='Set1', alpha=0.6, jitter=True, ax=ax4)
    ax4.set_xticklabels(['Hari Libur', 'Hari Kerja'])
    ax4.set_title('Sebaran Penyewaan per Hari')
    ax4.legend(title='Tahun', labels=['2011', '2012'])
    st.pyplot(fig4)
except:
    pass

# Visualisasi 5
st.subheader('Rata-rata Penyewaan Hari Kerja vs Libur')
try:
    fig5, ax5 = plt.subplots(figsize=(8, 5))
    sns.pointplot(data=filtered_day, x='workingday', y='cnt', hue='yr',
                  palette=['#3A6EA5', '#A52A2A'], markers=['o', 's'],
                  linestyles=['-', '--'], ax=ax5)
    ax5.set_xticklabels(['Hari Libur', 'Hari Kerja'])
    ax5.set_title('Rata-rata Penyewaan Sepeda')
    ax5.legend(title='Tahun', labels=['2011', '2012'])
    st.pyplot(fig5)
except:
    pass

# Visualisasi 6 & 7: Clustering
st.subheader('Segmentasi Hari Berdasarkan Aktivitas Penyewaan')
try:
    clustering_df = filtered_day.copy()
    q_low = clustering_df['cnt'].quantile(0.33)
    q_high = clustering_df['cnt'].quantile(0.66)

    def assign_cluster(cnt):
        if cnt < q_low:
            return 'Sepi'
        elif cnt < q_high:
            return 'Normal'
        else:
            return 'Sibuk'

    clustering_df['cluster'] = clustering_df['cnt'].apply(assign_cluster)
    cluster_summary = clustering_df.groupby('cluster')[['cnt', 'temp', 'hum', 'windspeed']].mean().round(2)

    fig6, ax6 = plt.subplots(figsize=(8, 5))
    sns.barplot(x=cluster_summary.index, y=cluster_summary['cnt'], palette='viridis', ax=ax6)
    ax6.set_title('Rata-rata Penyewaan Sepeda per Cluster')
    st.pyplot(fig6)

    fig7, ax7 = plt.subplots(figsize=(8, 5))
    sns.heatmap(cluster_summary[['temp', 'hum', 'windspeed']], annot=True, cmap='YlGnBu', fmt='.2f', ax=ax7)
    ax7.set_title('Rata-rata Lingkungan per Cluster')
    st.pyplot(fig7)
except:
    pass
