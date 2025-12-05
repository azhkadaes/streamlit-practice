"""Streamlit dashboard for multicultural recipe analytics."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from config import (
    ingredient_count_per_recipe,
    ingredient_count_stats_by_cuisine,
    ingredient_usage_distribution,
    recipe_category_count_by_cuisine,
    recipe_count_by_cuisine,
    recipe_count_by_diet,
    recipe_overview_with_ingredient_count,
    recipe_share_by_diet,
    top_ingredients,
)


st.set_page_config(
    page_title="Multicultural Recipe Dashboard",
    page_icon="🍲",
    layout="wide",
)

st.title("🍲 Multicultural Recipe Dashboard")
st.caption(
    "Insights tentang persebaran resep, ingredient, dan diet berdasarkan data "
    "`multicultural_recipe`. Gunakan panel kiri untuk mengatur parameter."
)


# ---------------------------------------------------------------------------
# Utility helpers
# ---------------------------------------------------------------------------


def _df_or_empty(loader, *, empty_message: str):
    """Run loader (already cached) and convert to DataFrame with graceful errors."""

    try:
        data = loader()
    except RuntimeError as exc:
        st.error(f"Tidak bisa memuat data: {exc}")
        return pd.DataFrame()

    df = pd.DataFrame(data)
    if df.empty:
        st.info(empty_message)
    return df


@st.cache_data(show_spinner=False)
def get_recipe_count_by_cuisine_df():
    return pd.DataFrame(recipe_count_by_cuisine())


@st.cache_data(show_spinner=False)
def get_recipe_category_count_by_cuisine_df():
    return pd.DataFrame(recipe_category_count_by_cuisine())


@st.cache_data(show_spinner=False)
def get_ingredient_usage_distribution_df():
    return pd.DataFrame(ingredient_usage_distribution())


@st.cache_data(show_spinner=False)
def get_ingredient_count_per_recipe_df():
    return pd.DataFrame(ingredient_count_per_recipe())


@st.cache_data(show_spinner=False)
def get_ingredient_count_stats_by_cuisine_df():
    return pd.DataFrame(ingredient_count_stats_by_cuisine())


@st.cache_data(show_spinner=False)
def get_recipe_count_by_diet_df():
    return pd.DataFrame(recipe_count_by_diet())


@st.cache_data(show_spinner=False)
def get_recipe_share_by_diet_df():
    return pd.DataFrame(recipe_share_by_diet())


@st.cache_data(show_spinner=False)
def get_recipe_overview_df():
    return pd.DataFrame(recipe_overview_with_ingredient_count())


@st.cache_data(show_spinner=False)
def get_top_ingredients_df(limit: int):
    return pd.DataFrame(top_ingredients(limit))


def df_to_csv(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False).encode("utf-8")


# Sidebar controls ---------------------------------------------------------

st.sidebar.header("Pengaturan")
top_n = st.sidebar.slider("Top ingredients", min_value=5, max_value=30, value=10, step=1)
show_tables = st.sidebar.checkbox("Tampilkan tabel detail", value=True)

# Main tabs ---------------------------------------------------------------
tab_cuisine, tab_ingredient, tab_diet = st.tabs([
    "Cuisine Insights",
    "Ingredient Insights",
    "Diet Insights",
])

# ---------------------------------------------------------------------------
# Cuisine tab
# ---------------------------------------------------------------------------

with tab_cuisine:
    st.subheader("Jumlah Resep per Cuisine")
    cuisine_df = _df_or_empty(
        get_recipe_count_by_cuisine_df,
        empty_message="Belum ada data resep untuk ditampilkan.",
    )
    if not cuisine_df.empty:
        fig = px.bar(
            cuisine_df,
            x="cuisine",
            y="recipe_count",
            text_auto=True,
            title="Total Resep per Cuisine",
            color="recipe_count",
            color_continuous_scale="Sunset",
        )
        fig.update_layout(showlegend=False, xaxis_title="Cuisine", yaxis_title="Jumlah Resep")
        st.plotly_chart(fig, use_container_width=True)
        st.caption("Visual ini menyoroti cuisine mana yang memiliki jumlah resep terbanyak sehingga mudah menentukan fokus eksplorasi.")
        csv = df_to_csv(cuisine_df)
        st.download_button("⬇️ Unduh data cuisine", csv, "recipe_per_cuisine.csv", "text/csv")

    st.divider()
    st.subheader("Jumlah Kategori Resep per Cuisine")
    category_df = _df_or_empty(
        get_recipe_category_count_by_cuisine_df,
        empty_message="Belum ada data kategori untuk cuisine.",
    )
    if not category_df.empty:
        fig = px.bar(
            category_df,
            x="cuisine",
            y="category_count",
            text_auto=True,
            hover_data={"recipe_count": True},
            title="Banyaknya Kategori Course per Cuisine",
            color="category_count",
            color_continuous_scale="Teal",
        )
        fig.update_layout(
            xaxis_title="Cuisine",
            yaxis_title="Jumlah Kategori",
        )
        st.plotly_chart(fig, use_container_width=True)
        st.caption("Bar chart membantu melihat keberagaman kategori hidangan di tiap cuisine.")
        if show_tables:
            st.dataframe(category_df, use_container_width=True)

# ---------------------------------------------------------------------------
# Ingredient tab
# ---------------------------------------------------------------------------

with tab_ingredient:
    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader(f"Top {top_n} Ingredients yang Sering Dipakai")
        top_ing_df = _df_or_empty(
            lambda: get_top_ingredients_df(top_n),
            empty_message="Belum ada data ingredient.",
        )
        if not top_ing_df.empty:
            fig = px.bar(
                top_ing_df,
                x="ingredient_name",
                y="usage_count",
                text_auto=True,
                title="Ingredient Paling Populer",
                color="usage_count",
                color_continuous_scale="Bluered_r",
            )
            fig.update_layout(xaxis_title="Ingredient", yaxis_title="Jumlah Penggunaan")
            st.plotly_chart(fig, use_container_width=True)
            st.caption("Daftar ini menunjukkan ingredient yang paling sering muncul sehingga layak dijadikan stok prioritas.")
    with col_b:
        st.subheader("Distribusi Penggunaan Ingredient di Resep")
        usage_df = _df_or_empty(
            get_ingredient_usage_distribution_df,
            empty_message="Belum ada data penggunaan ingredient.",
        )
        if not usage_df.empty:
            fig = px.scatter(
                usage_df,
                x="recipe_count",
                y="total_usage",
                hover_name="ingredient_name",
                title="Hubungan jumlah resep vs total penggunaan",
                color="total_usage",
                color_continuous_scale="Turbo",
            )
            fig.update_layout(
                xaxis_title="Jumlah Resep yang Menggunakan",
                yaxis_title="Total Penggunaan di Semua Resep",
            )
            st.plotly_chart(fig, use_container_width=True)
            st.caption("Semakin ke kanan dan atas, semakin dominan ingredient tersebut di banyak resep.")

    st.divider()
    st.subheader("Jumlah Ingredient per Resep")
    per_recipe_df = _df_or_empty(
        get_ingredient_count_per_recipe_df,
        empty_message="Belum ada data jumlah ingredient tiap resep.",
    )
    if not per_recipe_df.empty:
        fig = px.histogram(
            per_recipe_df,
            x="ingredient_count",
            nbins=15,
            title="Distribusi Jumlah Ingredient per Resep",
            color_discrete_sequence=["#f39c12"],
        )
        fig.update_layout(xaxis_title="Jumlah Ingredient", yaxis_title="Jumlah Resep")
        st.plotly_chart(fig, use_container_width=True)
        st.caption("Histogram ini membantu memahami kompleksitas rata-rata resep (sedikit vs banyak ingredient).")
        if show_tables:
            st.dataframe(per_recipe_df, use_container_width=True)

    st.divider()
    st.subheader("Statistik Ingredient per Cuisine")
    stats_df = _df_or_empty(
        get_ingredient_count_stats_by_cuisine_df,
        empty_message="Belum ada statistik ingredient per cuisine.",
    )
    if not stats_df.empty:
        fig = px.bar(
            stats_df,
            x="cuisine",
            y="avg_ingredient_per_recipe",
            text_auto=".2f",
            title="Rata-rata Ingredient per Resep per Cuisine",
            color="avg_ingredient_per_recipe",
            color_continuous_scale="Viridis",
        )
        fig.update_layout(xaxis_title="Cuisine", yaxis_title="Rata-rata Ingredient")
        st.plotly_chart(fig, use_container_width=True)
        st.caption("Bandingkan kompleksitas tiap cuisine untuk melihat mana yang cenderung kaya bumbu.")
        if show_tables:
            st.dataframe(stats_df, use_container_width=True)

# ---------------------------------------------------------------------------
# Diet tab
# ---------------------------------------------------------------------------

with tab_diet:
    st.subheader("Jumlah Resep per Tipe Diet")
    diet_df = _df_or_empty(
        get_recipe_count_by_diet_df,
        empty_message="Belum ada data diet untuk resep.",
    )
    if not diet_df.empty:
        total_recipes = int(diet_df["recipe_count"].sum())
        st.metric("Total Resep", f"{total_recipes}")
        fig = px.bar(
            diet_df,
            x="diet",
            y="recipe_count",
            text_auto=True,
            title="Total Resep per Diet",
            color="recipe_count",
            color_continuous_scale="Plasma",
        )
        fig.update_layout(xaxis_title="Diet", yaxis_title="Jumlah Resep")
        st.plotly_chart(fig, use_container_width=True)
        st.caption("Gunakan chart ini untuk melihat diet mana yang paling banyak variasi resepnya.")
        if show_tables:
            st.dataframe(diet_df, use_container_width=True)

    st.divider()
    st.subheader("Pembagian Resep per Diet")
    share_df = _df_or_empty(
        get_recipe_share_by_diet_df,
        empty_message="Belum ada data persentase diet.",
    )
    if not share_df.empty:
        fig = px.pie(
            share_df,
            names="diet",
            values="recipe_count",
            title="Persentase Resep per Diet",
            hole=0.4,
        )
        fig.update_traces(textposition="inside", textinfo="percent+label")
        st.plotly_chart(fig, use_container_width=True)
        st.caption("Diagram donat menekankan proporsi kontribusi tiap diet terhadap keseluruhan koleksi resep.")
        if show_tables:
            st.dataframe(share_df, use_container_width=True)

    st.divider()
    st.subheader("Ringkasan Resep + Ingredient Count")
    overview_df = _df_or_empty(
        get_recipe_overview_df,
        empty_message="Belum ada ringkasan resep.",
    )
    if not overview_df.empty and show_tables:
        st.dataframe(overview_df, use_container_width=True)
        csv = df_to_csv(overview_df)
        st.download_button("⬇️ Download ringkasan resep", csv, "recipe_overview.csv", "text/csv")
        st.caption("Tabel detail ini merangkum kategori lengkap resep plus jumlah ingredient untuk analisis mendalam.")


# st.sidebar.caption(
#     "Pastikan variabel lingkungan database (PGHOST, PGPORT, PGUSER, \n"
#     "PGPASSWORD, PGDATABASE) sudah diisi sebelum menjalankan dashboard."
# )
