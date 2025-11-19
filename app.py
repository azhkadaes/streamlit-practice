import streamlit as st
import pandas as pd 
import matplotlib as plt

st.title("Aplikasi visualisasi ")
st.write("welkom")

data = pd.DataFrame(data= {
    "Kampanye": ["Kampanye A", "Kampanye B", "Kampanye C"],
    "Total Donasi (juta)": [50, 70, 200],
})

st.subheader("Data Kampanye donasi")
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.title("Aplikasi visualisasi")
st.write("welkom")

# Sample campaign data
data = pd.DataFrame({
    "Kampanye": ["Kampanye A", "Kampanye B", "Kampanye C"],
    "Total Donasi (jt)": [50, 70, 200],
})

st.subheader("Data Kampanye donasi")
st.dataframe(data)

st.bar_chart(data.set_index("Kampanye"))
st.line_chart(data.set_index("Kampanye"))

fig, ax = plt.subplots()
ax.bar(data["Kampanye"], data["Total Donasi (jt)"], color="green")
ax.set_ylabel("Donasi (jt)")
st.pyplot(fig)

# Visualization selector
tipe = st.selectbox("Pilih visualisasi", ["bar", "pie", "line", "doughnut"])

if tipe == "bar":
    st.bar_chart(data.set_index("Kampanye"))
elif tipe == "line":
    st.line_chart(data.set_index("Kampanye"))
elif tipe in ("pie", "doughnut"):
    fig, ax = plt.subplots()
    ax.pie(data["Total Donasi (jt)"], labels=data["Kampanye"], autopct='%1.1f%%')
    if tipe == "doughnut":
        centre_circle = plt.Circle((0, 0), 0.70, fc='white')
        fig.gca().add_artist(centre_circle)
    st.pyplot(fig)

# Filter slider
nilai = st.slider("Tampilkan data donasi minimum:", 0, 500, 150)
st.dataframe(data[data["Total Donasi (jt)"] >= nilai])

# Map data
data_peta = pd.DataFrame({
    'lokasi': ['Balikpapan', 'Samboja', 'Mahakam'],
    'lat': [-1.27, -1.10, -0.50],
    'lon': [116.83, 117.00, 117.25]
})

st.map(data_peta)

#Dashboard
st.title("Dashboard Donasi Lingkungan")

data = pd.DataFrame(data={
    "Kampanye": ["Mangrove Balikpapan","Pantai Samboja", "Delta Mahakam"],
    "Donasi": [120,85, 60],
    "Target": [150, 100, 90]
})

kampanye = st.selectbox("Pilih kampanye:", data["Kampanye"])
row = data[data["Kampanye"] == kampanye].iloc[0]

st.metric("donasi saat ini", f"{row['Donasi']} juta", delta=row['Donasi'] - row['Target'])
st.progress(row['Donasi'] / row['Target'])

fig, ax = plt.subplots()
ax.bar(data["Kampanye"], data["Donasi"], color="green")
ax.set_ylabel("donasi(jt)")
st.pyplot(fig)

st.image("image.png", caption="Kegiatan penanaman")
st.markdown(""" ### Tujuan nya bagus """)