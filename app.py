import streamlit as st
import sqlite3
import pandas as pd
from datetime import date

st.set_page_config(page_title="KasirKu", page_icon="🛒")

# ===== DATABASE =====
db = sqlite3.connect("kasir.db", check_same_thread=False)
db.execute("""CREATE TABLE IF NOT EXISTS transaksi(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tanggal TEXT, produk TEXT, jumlah INTEGER,
    harga INTEGER, pembayaran TEXT)""")
db.commit()

# ===== LOGIN =====
if "login" not in st.session_state:
    st.session_state.login = False

if not st.session_state.login:
    st.title("🛒 KasirKu")
    st.subheader("Login")
    user = st.text_input("Username")
    pw = st.text_input("Password", type="password")

    if st.button("Masuk"):
        if user == "admin" and pw == "1234":
            st.session_state.login = True
            st.rerun()
        else:
            st.error("Username/password salah.")

    st.info("Username: admin | Password: 1234")
    st.stop()

# ===== MENU =====
st.sidebar.title("🛒 KasirKu")
menu = st.sidebar.radio("Menu", ["Home", "Dashboard", "Input Transaksi"])

if st.sidebar.button("Logout"):
    st.session_state.login = False
    st.rerun()

# ===== HOME =====
if menu == "Home":
    st.title("🏠 Dashboard Minimarket")
    st.write("Selamat datang di aplikasi KasirKu.")
    st.write("Aplikasi ini digunakan untuk mencatat transaksi dan melihat penjualan.")

    st.success("✅ Sistem siap digunakan")

# ===== DASHBOARD =====
elif menu == "Dashboard":
    st.title("📊 Dashboard")

    data = pd.read_sql("SELECT * FROM transaksi", db)

    if data.empty:
        st.warning("Belum ada transaksi.")
    else:
        # Filter tanggal
        data["tanggal"] = pd.to_datetime(data["tanggal"])
        mulai = st.date_input("Dari tanggal", date.today())
        akhir = st.date_input("Sampai tanggal", date.today())

        data = data[
            (data["tanggal"].dt.date >= mulai) &
            (data["tanggal"].dt.date <= akhir)
        ]

        omzet = int((data["jumlah"] * data["harga"]).sum())
        transaksi = len(data)
        barang = int(data["jumlah"].sum())

        a, b, c = st.columns(3)
        a.metric("💰 Omzet", f"Rp {omzet:,}".replace(",", "."))
        b.metric("🧾 Transaksi", transaksi)
        c.metric("📦 Barang Terjual", barang)

        st.subheader("Produk Terlaris")
        produk = data.groupby("produk")["jumlah"].sum().sort_values(ascending=False)
        st.bar_chart(produk.head(5))

        st.subheader("Metode Pembayaran")
        bayar = data.groupby("pembayaran")["jumlah"].sum()
        st.bar_chart(bayar)

        st.subheader("Data Transaksi")
        st.dataframe(data, use_container_width=True)

        # Download laporan sederhana
        laporan = data.to_csv(index=False)
        st.download_button(
            "⬇️ Download Laporan",
            laporan,
            "laporan_transaksi.csv",
            "text/csv"
        )

# ===== INPUT =====
elif menu == "Input Transaksi":
    st.title("➕ Input Transaksi")

    with st.form("transaksi"):
        produk = st.text_input("Nama Produk")
        jumlah = st.number_input("Jumlah", min_value=1, value=1)
        harga = st.number_input("Harga Satuan", min_value=0, value=1000)
        pembayaran = st.selectbox(
            "Pembayaran",
            ["Tunai", "QRIS", "Transfer"]
        )

        simpan = st.form_submit_button("💾 Simpan")

    if simpan:
        if produk == "":
            st.error("Nama produk harus diisi.")
        else:
            db.execute(
                """INSERT INTO transaksi
                (tanggal,produk,jumlah,harga,pembayaran)
                VALUES (?,?,?,?,?)""",
                (str(date.today()), produk, jumlah, harga, pembayaran)
            )
            db.commit()
            st.success("✅ Transaksi berhasil disimpan!")

st.caption("KasirKu - Tugas Dashboard Minimarket")
