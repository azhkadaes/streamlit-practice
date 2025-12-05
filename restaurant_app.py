import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import io
import pydeck as pdk

# Restaurant dashboard (Warung Nasi Padang)
# - Membuat dataset contoh menu
# - Menyediakan beberapa visualisasi (bar, pie, line, area) dan peta
# - Menghasilkan laporan PDF multi-halaman dari grafik-grafik tersebut


@st.cache_data
def make_menu_dataset():

    # Buat dataset contoh untuk Warung Nasi Padang.

    # Mengembalikan `pandas.DataFrame` dengan kolom:
    # - item, price, sold_month, rating, lat, lon, revenue

    # Fungsi ini diberi cache melalui `@st.cache_data` agar tidak dihitung
    # ulang setiap interaksi UI kecuali cache invalidated.

    # Warung Nasi Padang - 10 menu items
    items = [
        "Rendang", "Dendeng Balado", "Gulai Ayam", "Sambal Ijo", "Gulai Kikil",
        "Perkedel", "Sate Padang", "Sayur Nangka", "Ayam Pop", "Paru Goreng"
    ]
    prices = [45000, 35000, 30000, 8000, 32000, 8000, 25000, 12000, 28000, 10000]
    sold = [120, 80, 95, 200, 70, 150, 60, 90, 110, 180]  # units sold in month
    rating = [4.8, 4.6, 4.5, 4.1, 4.4, 4.0, 4.3, 4.2, 4.5, 3.9]
    # Coordinates around Balikpapan central area
    lat = [-1.267, -1.268, -1.266, -1.265, -1.269, -1.270, -1.271, -1.264, -1.262, -1.263]
    lon = [116.832, 116.835, 116.829, 116.828, 116.834, 116.836, 116.838, 116.831, 116.830, 116.833]

    df = pd.DataFrame({
        "item": items,
        "price": prices,
        "sold_month": sold,
        "rating": rating,
        "lat": lat,
        "lon": lon,
    })
    df["revenue"] = df["price"] * df["sold_month"]
    return df


@st.cache_data
def convert_df_to_csv(_df):
   
    # Konversi DataFrame ke CSV bytes (utf-8) untuk diunduh lewat Streamlit.

    # Input: `_df` (pandas.DataFrame)
    # Output: bytes CSV siap dipakai di `st.download_button`.
   
    return _df.to_csv(index=False).encode("utf-8")


def create_chart(kind, df):
    
    # Buat matplotlib Figure untuk tipe chart tertentu berdasarkan `df`.

    # Parameter:
    # - kind: salah satu dari "Bar - Revenue", "Pie - Share", "Line - Top 3 Trend", atau default (area)
    # - df: DataFrame yang berisi kolom minimal `item`, `revenue`, dan/atau `sold_month`

    # Mengembalikan (fig, title, explanation) — objek figure, judul, dan teks penjelasan singkat.
    
    fig, ax = plt.subplots(figsize=(8, 4.5))
    if kind == "Bar - Revenue":
        ax.bar(df["item"], df["revenue"], color="#2b8cbe")
        ax.set_ylabel("Revenue (IDR)")
        ax.set_xticklabels(df["item"], rotation=45, ha="right")
        title = "Revenue per Menu"
        explanation = "Bar chart menunjukkan kontribusi pendapatan tiap menu."
    elif kind == "Pie - Share":
        ax.pie(df["revenue"], labels=df["item"], autopct="%1.1f%%")
        title = "Komposisi Revenue"
        explanation = "Pie chart menunjukkan persentase kontribusi pendapatan tiap menu."
    elif kind == "Line - Top 3 Trend":
        top3 = df.sort_values("revenue", ascending=False).head(3)["item"].tolist()
        days = pd.date_range(end=pd.Timestamp.today(), periods=14)
        sim = pd.DataFrame(index=days)
        for it in top3:
            base = int(df.loc[df["item"] == it, "sold_month"].values[0] / 14)
            sim[it] = np.clip(base + np.random.randint(-2, 5, size=len(days)).cumsum(), 0, None)
        for col in sim.columns:
            ax.plot(sim.index, sim[col], marker="o", label=col)
        ax.set_ylabel("Simulated Daily Sales")
        ax.legend()
        title = "Simulasi Tren Harian - Top 3"
        explanation = "Line chart simulasi untuk tiga menu teratas berdasarkan revenue."
    else:
        ax.fill_between(df["item"], df["sold_month"], color="#fb9a99", alpha=0.6)
        ax.plot(df["item"], df["sold_month"], marker="o", color="#fb9a99")
        ax.set_ylabel("Jumlah Terjual (bulan)")
        ax.set_xticklabels(df["item"], rotation=45, ha="right")
        title = "Volume Orders per Menu"
        explanation = "Area chart menunjukkan volume pesanan per menu (bulanan)."

    fig.suptitle(title)
    fig.tight_layout(rect=[0, 0.03, 1, 0.95])
    return fig, title, explanation


def build_pdf_report(df):
    
    # Bangun file PDF (bytes) berisi cover, langkah, dan tiap chart sebagai halaman.

    # Alur:
    # - Buat `PdfPages` pada buffer memori
    # - Tambahkan halaman cover (teks)
    # - Tambahkan halaman instruksi/langkah
    # - Untuk setiap jenis chart: render chart ke PNG sementara, lalu masukkan ke halaman PDF

    # Kembalian: bytes PDF siap diunduh.
  
    buf = io.BytesIO()
    with PdfPages(buf) as pdf:
        # Cover
        fig = plt.figure(figsize=(8.5, 11))
        fig.clf()
        fig.text(0.5, 0.7, "Laporan Warung Nasi Padang", ha="center", fontsize=20, weight="bold")
        fig.text(0.5, 0.62, "10 menu populer", ha="center", fontsize=12)
        fig.text(0.1, 0.44, "\nLaporan ini berisi visualisasi (bar, pie, line, area)\ndan ringkasan data menu Warung Nasi Padang.", fontsize=10)
        pdf.savefig(fig)
        plt.close(fig)

        # Steps
        fig = plt.figure(figsize=(8.5, 11))
        fig.clf()
        steps = [
            "1. Siapkan dataset menu (item, price, sold_month, rating, lat, lon).",
            "2. Gunakan filter untuk memilih subset menu.",
            "3. Pilih visualisasi lalu interpretasikan hasil.",
            "4. Ekspor laporan PDF berisi grafik dan penjelasan.",
        ]
        fig.text(0.1, 0.9, "Langkah-langkah:", fontsize=14, weight="bold")
        y = 0.82
        for s in steps:
            fig.text(0.1, y, s, fontsize=10)
            y -= 0.06
        pdf.savefig(fig)
        plt.close(fig)

        # Charts
        kinds = ["Bar - Revenue", "Pie - Share", "Line - Top 3 Trend", "Area - Orders"]
        for k in kinds:
            fig, title, explanation = create_chart(k, df)
            tmp = io.BytesIO()
            fig.savefig(tmp, format="png", bbox_inches='tight')
            plt.close(fig)
            tmp.seek(0)
            img = plt.imread(tmp)
            fig2 = plt.figure(figsize=(8.5, 11))
            ax = fig2.add_subplot(111)
            ax.axis('off')
            ax.imshow(img)
            fig2.text(0.1, 0.05, explanation, fontsize=10)
            fig2.suptitle(title)
            pdf.savefig(fig2)
            plt.close(fig2)

    buf.seek(0)
    return buf.getvalue()


def main():
    # Main app: susun layout Streamlit, tampilkan metrik, tabel, filter, visualisasi, peta, dan tombol ekspor.
    

    # Page configuration and header
    st.set_page_config(page_title="Warung Nasi Padang Dashboard", layout="wide")
    # optional image: ensure file exists in working dir if used
    try:
        st.image("pdg.png", caption="Warung Nasi Padang")
    except Exception:
        # If image missing, continue silently
        pass
    st.title("Dashboard Warung Nasi Padang")
    st.markdown("""
     Dashboard ini menampilkan analisis menu, penjualan, dan lokasi untuk Warung Nasi Padang. Gunakan filter untuk mengeksplor menu, lihat metrik utama, dan pilih visualisasi.
    """)

    # Load dataset (cached)
    df = make_menu_dataset()

    # --- Metrics: ringkasan cepat
    total_revenue = df["revenue"].sum()
    total_items = df["sold_month"].sum()
    avg_price = df["price"].mean()

    c1, c2, c3 = st.columns([2, 1, 1])
    with c1:
        st.subheader("Statistics")
        st.markdown("Overall penjualan dan revenue")
    with c2:
        st.metric("Total Revenue", f"Rp {total_revenue:,.0f}")
    with c3:
        st.metric("Total Orders (bulan)", f"{total_items}")

    st.markdown("---")

    # --- Layout: kiri = tabel + filter, spacer kecil, kanan = visualisasi
    left, spacer, right = st.columns((1, 0.1, 2))
    with left:
        st.subheader("Daftar Menu")
        # Tampilkan tabel yang sudah diformat
        st.dataframe(df.style.format({"price": "Rp {:,.0f}", "revenue": "Rp {:,.0f}"}))
        csv = convert_df_to_csv(df)
        st.download_button("⬇️ Download CSV", data=csv, file_name="menu_padang.csv", mime="text/csv")

        # Filter untuk mempermudah analisis subset
        st.subheader("Filter")
        pmin, pmax = int(df["price"].min()), int(df["price"].max())
        price_range = st.slider("Rentang harga", pmin, pmax, (pmin, pmax))
        sold_min = int(df["sold_month"].min())
        sold_max = int(df["sold_month"].max())
        sold_filter = st.slider("Minimal terjual (bulan)", sold_min, sold_max, sold_min)

    with right:
        st.subheader("Visualisasi")
        chart_choice = st.selectbox("Pilih chart", ["Bar - Revenue", "Pie - Share", "Line - Top 3 Trend", "Area - Orders", "Map"])

        # Terapkan filter
        filtered = df[(df["price"] >= price_range[0]) & (df["price"] <= price_range[1]) & (df["sold_month"] >= sold_filter)]

        if filtered.empty:
            st.info("Tidak ada data sesuai filter.")
        else:
            if chart_choice == "Map":
                # Map: gunakan pydeck untuk peta interaktif
                st.markdown("**Peta lokasi (Balikpapan)**")
                mid_lat = filtered["lat"].mean()
                mid_lon = filtered["lon"].mean()
                layer = pdk.Layer(
                    "ScatterplotLayer",
                    data=filtered,
                    get_position='[lon, lat]',
                    get_radius=200,
                    get_fill_color=[255, 140, 0],
                    pickable=True,
                )
                # Tooltip menggunakan placeholder kolom dari DataFrame
                tooltip = {"html": "<b>{item}</b><br/>Revenue: Rp {revenue}", "style": {"color": "white"}}
                deck = pdk.Deck(
                    initial_view_state=pdk.ViewState(latitude=mid_lat, longitude=mid_lon, zoom=12, pitch=0),
                    layers=[layer],
                    tooltip=tooltip,
                )
                st.pydeck_chart(deck)
                st.caption("Klik titik untuk melihat nama menu dan revenue (tooltip).")
            else:
                # Non-map charts: render matplotlib figure yang dikembalikan create_chart
                fig, title, explanation = create_chart(chart_choice, filtered)
                st.pyplot(fig)
                st.markdown(f"**{title}**")
                st.write(explanation)

    # Footer / about
    st.markdown("---")
    st.header("Tentang")
    st.markdown(
        
        # Dashboard Menu Warung Nasi Padang

        # Aplikasi ini membantu pemilik warung memahami performa menu: harga, jumlah terjual, revenue, dan lokasi.

        # Pilih rentang harga dan minimal terjual, lalu pilih visualisasi di sebelah kanan. Gunakan tombol download untuk CSV atau PDF.
        
    )

    # PDF export button
    st.markdown("## Ekspor Laporan PDF")
    if st.button("Generate PDF Report"):
        with st.spinner("Membuat PDF…"):
            pdf = build_pdf_report(df)
            st.success("Selesai — unduh laporan")
            st.download_button("Download PDF", data=pdf, file_name="report_warung_padang.pdf", mime="application/pdf")


if __name__ == "__main__":
    main()
