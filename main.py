# Import library
import streamlit as st
import pandas as pd
from datetime import datetime

# Import fungsi dari config.py
from config import *


@st.cache_data
def convert_df_to_csv(_df):
    return _df.to_csv(index=False).encode('utf-8')

# Set konfigurasi halaman dashboard
st.set_page_config("Dashboard", page_icon="📊", layout="wide")  # Judul, ikon, tata letak lebar


# Fungsi tampilkan tabel + export CSV
def tabelCustomers_dan_export():
    try:
        result_customers = view_customers()
    except Exception as e:
        st.error(f"Gagal mengambil data pelanggan: {e}")
        return

    df_customers = pd.DataFrame(result_customers, columns=[
        "customer_id", "name", "email", "phone", "address", "birthdate",
    ])

    if not df_customers.empty:
        # Hitung usia dari birthdate
        df_customers['birthdate'] = pd.to_datetime(df_customers['birthdate'])
        df_customers['Age'] = (datetime.now() - df_customers['birthdate']).dt.days // 365
    else:
        st.info("Tidak ada data pelanggan untuk ditampilkan.")
        return

    # Hitung jumlah pelanggan
    total_customers = df_customers.shape[0]

    # Tampilkan metrik
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="📦 Total Pelanggan", value=total_customers, delta="Semua Data")

    # Sidebar: Filter Rentang Usia
    st.sidebar.header("Filter Rentang Usia")
    min_age = int(df_customers['Age'].min())
    max_age = int(df_customers['Age'].max())
    age_range = st.sidebar.slider(
        "Pilih Rentang Usia",
        min_value=min_age,
        max_value=max_age,
        value=(min_age, max_age)
    )

    # Terapkan filter usia
    filtered_df = df_customers[df_customers['Age'].between(*age_range)]

    # Tampilkan tabel pelanggan
    st.markdown("### 📋 Tabel Data Pelanggan")

    showdata = st.multiselect(
        "Pilih Kolom Pelanggan yang Ditampilkan",
        options=filtered_df.columns,
        default=["customer_id", "name", "email", "phone", "address", "birthdate", "Age"]
    )

    st.dataframe(filtered_df[showdata], use_container_width=True)

    csv = convert_df_to_csv(filtered_df[showdata])
    st.download_button(
        label="⬇️ Download Data Pelanggan sebagai CSV",
        data=csv,
        file_name='data_pelanggan.csv',
        mime='text/csv'
    )

# Sidebar untuk memilih tampilan
st.sidebar.success("Pilih Tabel:")
if st.sidebar.checkbox("Tampilkan Pelanggan"):
    tabelCustomers_dan_export()


# --------------------
# Produk
# --------------------
def tabelProducts_dan_export():
    try:
        result_products = view_products()
    except Exception as e:
        st.error(f"Gagal mengambil data produk: {e}")
        return

    df_products = pd.DataFrame(result_products, columns=[
        "product_id", "name", "description", "price", "stock"
    ])

    total_products = df_products.shape[0]
    total_stock = int(df_products['stock'].sum()) if not df_products.empty else 0
    avg_price = float(df_products['price'].mean()) if not df_products.empty else 0.0

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="📦 Total Produk", value=total_products)
    with col2:
        st.metric(label="🏷️ Rata‑rata Harga", value=f"{avg_price:,.2f}")
    with col3:
        st.metric(label="📚 Total Stok", value=total_stock)

    st.markdown("### 🧾 Tabel Produk")
    st.dataframe(df_products, use_container_width=True)

    # Visual: top 10 produk berdasarkan stok
    if not df_products.empty:
        top_stock = df_products.sort_values('stock', ascending=False).head(10).set_index('name')
        st.markdown("### 🔢 Top 10 Produk (Stok)")
        st.bar_chart(top_stock['stock'])

    csv = convert_df_to_csv(df_products)
    st.download_button("⬇️ Download Data Produk sebagai CSV", data=csv, file_name='data_products.csv', mime='text/csv')


if st.sidebar.checkbox("Tampilkan Produk"):
    tabelProducts_dan_export()


# --------------------
# Orders
# --------------------
def tabelOrders_dan_export():
    try:
        result_orders = view_orders_with_customers()
    except Exception as e:
        st.error(f"Gagal mengambil data orders: {e}")
        return

    df_orders = pd.DataFrame(result_orders, columns=[
        "order_id", "order_date", "total_amount", "customer_name", "phone"
    ])

    if not df_orders.empty:
        df_orders['order_date'] = pd.to_datetime(df_orders['order_date'])

    total_orders = df_orders.shape[0]
    total_revenue = float(df_orders['total_amount'].sum()) if not df_orders.empty else 0.0
    avg_order = float(df_orders['total_amount'].mean()) if not df_orders.empty else 0.0

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="🧾 Total Orders", value=total_orders)
    with col2:
        st.metric(label="💰 Total Revenue", value=f"{total_revenue:,.2f}")
    with col3:
        st.metric(label="📈 Rata‑rata Order", value=f"{avg_order:,.2f}")

    st.markdown("### 📅 Orders")
    st.dataframe(df_orders, use_container_width=True)

    # Revenue over time (monthly)
    if not df_orders.empty:
        df_time = df_orders.set_index('order_date').resample('M')['total_amount'].sum()
        st.markdown("### 📊 Pendapatan per Bulan")
        st.line_chart(df_time)

    csv = convert_df_to_csv(df_orders)
    st.download_button("⬇️ Download Data Orders sebagai CSV", data=csv, file_name='data_orders.csv', mime='text/csv')


if st.sidebar.checkbox("Tampilkan Orders"):
    tabelOrders_dan_export()


# --------------------
# Order Details
# --------------------
def tabelOrderDetails_dan_export():
    try:
        result_od = view_order_details_with_info()
    except Exception as e:
        st.error(f"Gagal mengambil data order_details: {e}")
        return

    df_od = pd.DataFrame(result_od, columns=[
        "order_detail_id", "order_id", "order_date", "customer_id", "customer_name",
        "product_id", "product_name", "unit_price", "quantity", "subtotal", "order_total", "phone"
    ])

    if not df_od.empty:
        df_od['order_date'] = pd.to_datetime(df_od['order_date'])

    total_items = df_od.shape[0]
    total_revenue = float(df_od['subtotal'].sum()) if not df_od.empty else 0.0

    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="🔢 Total Order Details", value=total_items)
    with col2:
        st.metric(label="💵 Revenue (Detail)", value=f"{total_revenue:,.2f}")

    st.markdown("### 🧾 Order Details")
    st.dataframe(df_od, use_container_width=True)

    # Top products by quantity
    if not df_od.empty:
        top_products = df_od.groupby('product_name')['quantity'].sum().sort_values(ascending=False).head(10)
        st.markdown("### 🔝 Top Produk berdasarkan Quantity")
        st.bar_chart(top_products)

    csv = convert_df_to_csv(df_od)
    st.download_button("⬇️ Download Data Order Details sebagai CSV", data=csv, file_name='data_order_details.csv', mime='text/csv')


if st.sidebar.checkbox("Tampilkan Order Details"):
    tabelOrderDetails_dan_export()