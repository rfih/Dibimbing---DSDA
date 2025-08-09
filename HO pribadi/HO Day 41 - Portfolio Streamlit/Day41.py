# Day 41 Portfolio Streamlit App

import streamlit as st
import pandas as pd
import numpy as np
import pickle
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta


# set konfigurasi halaman
st.set_page_config(
    page_title="Dashboard Analisisi Penjualan",
    # page_icon=":bar_chart:",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -- fungsi untuk memuat data --
@st.cache_data
def load_data():
    return pd.read_csv("data/data_dummy_retail_store.csv")

# load data penjualan
df_sales = load_data()
df_sales.columns = df_sales.columns.str.lower().str.replace(' ', '_') # mengubah nama kolom menjadi lowercase dan mengganti spasi dengan underscore
df_sales['tanggal_pesanan'] = pd.to_datetime(df_sales['tanggal_pesanan'])

# load model -- nanti

# judul dashboard
st.title("Dashboard Analisis Penjualan Toko Online 33B")
st.markdown("Dashboard ini digunakan untuk menganalisis data penjualan dari toko online 33B. Data yang digunakan adalah data dummy yang dibuat untuk keperluan pembelajaran.")

st.markdown("-------")

pilihan_halaman = st.sidebar.selectbox(
    "Pilih Halaman",
    ("Overview Dashboard", "Prediksi Penjualan")
)

# filter global (muncul untuk halaman overview dashboard)
if pilihan_halaman == "Overview Dashboard":
    st.sidebar.markdown("### Filter Dashboard")
    min_date = df_sales['tanggal_pesanan'].min().date()
    max_date = df_sales['tanggal_pesanan'].max().date()

    date_range = st.sidebar.date_input(
        "Pilih Rentang Tanggal",
        value=(min_date,max_date),
        min_value=min_date,
        max_value=max_date
    )

    if len(date_range) == 2:
        start_date_filter = pd.to_datetime(date_range[0])
        end_date_filter = pd.to_datetime(date_range[1])
        filtered_df = df_sales[(df_sales['tanggal_pesanan'] >= start_date_filter) &
                               (df_sales['tanggal_pesanan'] <= end_date_filter)]
    else: 
        # kalau filter date-nya belum tuntas
        filtered_df = df_sales 
    
    # filter berdasarkan wilayah 
    selected_regions = st.sidebar.multiselect(
        "Pilih Wilayah:",
        options=df_sales['wilayah'].unique().tolist(),
        default=df_sales['wilayah'].unique().tolist()
    )

    filtered_df = filtered_df[filtered_df['wilayah'].isin(selected_regions)]

    # filter berdasarkan kategori produk
    selected_categories = st.sidebar.multiselect(
        "Pilih Kategori Produk:",
        options=df_sales['kategori'].unique().tolist(),
        default=df_sales['kategori'].unique().tolist()
    )

    filtered_df = filtered_df[filtered_df['kategori'].isin(selected_categories)]
else: # kalau tidak ada filter filter
    filtered_df = df_sales.copy()

# --- halaman utama overview dashboard ---
if pilihan_halaman == "Overview Dashboard":
    # metrik utama
    st.subheader("Ringkasan Pertama Penjualan")

    col1, col2, col3, col4 = st.columns(4)

    total_sales = filtered_df['total_penjualan'].sum()
    total_orders = filtered_df['orderid'].nunique()
    avg_order_value = total_sales / total_orders if total_orders > 0 else 0
    total_products_sold = filtered_df['jumlah'].sum()

    with col1:
        st.metric("Total Penjualan", value=f"Rp {total_sales:,.2f}")
    with col2:
        st.metric("Total Pesanan", value=f"{total_orders:,}")
    with col3:
        st.metric("Rata-rata Nilai Pesanan", value=f"Rp {avg_order_value:,.2f}")
    with col4:
        st.metric("Total Produk Terjual", value=f"{total_products_sold:,}")


    st.markdown("-------")
    # tren penjualan/line chart
    st.subheader("Tren Penjualan Bulanan")
    sales_by_month = filtered_df.groupby('bulan')['total_penjualan'].sum()

    fig_monthly_sales = px.line(
        sales_by_month,
        x= sales_by_month.index,
        y='total_penjualan',
        markers=True,
        hover_name = sales_by_month.index
    )

    st.plotly_chart(fig_monthly_sales)

    st.markdown("-------")

    col_vis1, col_vis2 = st.columns(2)

    with col_vis1:
        st.write("### Top 10 Produk Terlaris")

        top_products_sold = filtered_df.groupby('produk')['total_penjualan'].sum().nlargest(10).reset_index()

        # bar chart
        fig_top_products = px.bar(
            top_products_sold,
            x='total_penjualan',
            y='produk',
            title="Top 10 Produk Terlaris",
            labels={'produk': 'Produk', 'total_penjualan': 'Total Penjualan'},
            text='total_penjualan'
        )   

        st.plotly_chart(fig_top_products)

    with col_vis2:
        st.write("### Distribusi Penjualan per Kategori")

        sales_by_category = filtered_df.groupby('kategori')['total_penjualan'].sum().reset_index()

        fig_category_pie = px.pie(
            sales_by_category,
            values='total_penjualan',
            names='kategori',
            title="Distribusi Penjualan per Kategori",
            hole=0.3
        )

        st.plotly_chart(fig_category_pie)

    # penjualan berdasarkan metode bayar dan wilayan (pakai tabs)

    st.subheader("Performa Penjualan Lebih Detail")
    tab1, tab2 = st.tabs(["Metode Pembayaran", "Penjualan per Wilayah"])

    sales_by_payment = filtered_df.groupby('metode_pembayaran')['total_penjualan'].sum().reset_index()  

    # membuat chart payment method
    with tab1:
        fig_payment_method = px.bar(
            sales_by_payment,
            x='metode_pembayaran',
            y='total_penjualan',
            title="Penjualan Berdasarkan Metode Pembayaran",
            labels={'metode_pembayaran': 'Metode Pembayaran', 'total_penjualan': 'Total Penjualan'},
            text='total_penjualan',
            color='metode_pembayaran'
        )

        st.plotly_chart(fig_payment_method, use_container_width=True)

    # membuat chart wilayah
    sales_by_region = filtered_df.groupby('wilayah')['total_penjualan'].sum().reset_index()

    with tab2:
        fig_sales_by_region = px.bar(
            sales_by_region,
            x='wilayah',
            y='total_penjualan',
            title="Penjualan per Wilayah",
            labels={'wilayah': 'Wilayah', 'total_penjualan': 'Total Penjualan'},
            text='total_penjualan',
            color='wilayah'
        )

        st.plotly_chart(fig_sales_by_region, use_container_width=True)