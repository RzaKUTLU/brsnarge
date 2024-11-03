import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
import io
import xlsxwriter

# Veritabanı bağlantısı fonksiyonu
def get_connection():
    return sqlite3.connect('siparisler.db')

# Siparişler tablosunu oluştur
def create_table():
    conn = get_connection()
    conn.execute('''
    CREATE TABLE IF NOT EXISTS siparisler (
        id INTEGER PRIMARY KEY,
        tarih TEXT,
        isim TEXT,
        restoran TEXT,
        yemek TEXT,
        fiyat REAL,
        not TEXT
    )
    ''')
    conn.commit()
    conn.close()

# Tabloyu yeniden oluşturmak için fonksiyon
def reset_table():
    conn = get_connection()
    conn.execute('DROP TABLE IF EXISTS siparisler')
    create_table()
    conn.close()

create_table()

# Excel indirme fonksiyonu
def to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Siparişler', index=False)
        workbook = writer.book
        worksheet = writer.sheets['Siparişler']

        # Format ayarları
        para_format = workbook.add_format({'num_format': '#,##0.00 ₺'})
        worksheet.set_column('A:A', 20)  # Tarih sütunu
        worksheet.set_column('B:B', 10)  # İsim sütunu
        worksheet.set_column('C:C', 10)  # Restoran sütunu
        worksheet.set_column('D:D', 15)  # Yemek sütunu
        worksheet.set_column('E:E', 12, para_format)  # Fiyat sütunu

    return output.getvalue()

# Sayfa yapılandırması
st.set_page_config(page_title="Borsan Ar-Ge Yemek Sipariş Sistemi", layout="wide")

# Restoranları sakla
if 'restoranlar' not in st.session_state:
    st.session_state.restoranlar = {
        'Nazar Petrol': {
           'Adana Dürüm': 170,
           'Adana Porsiyon': 240,
           'Tavuk Dürüm': 155,
           # ... (diğer yemekler)
        },
        'Çalıkuşu Kirazlık': {
            'Tavuk Dürüm Ç.lavaş Döner(100gr)': 160,
            'Tavuk Dürüm Döner(50gr)': 80,
            'Et Dürüm Döner': 140,
            # ... (diğer yemekler)
        }
    }

# Başlık
st.title("🍽️ Borsan Ar-Ge Yemek Sipariş Sistemi")

# Sidebar - Yeni Restoran ve Menü Ekleme
with st.sidebar:
    st.header("Restoran Yönetimi")
    new_restaurant = st.text_input("Yeni Restoran")
    if st.button("Restoran Ekle") and new_restaurant:
        if new_restaurant not in st.session_state.restoranlar:
            st.session_state.restoranlar[new_restaurant] = {}
            st.success(f"{new_restaurant} başarıyla eklendi!")
        else:
            st.error("Bu restoran zaten mevcut!")

    st.subheader("Menü Yönetimi")
    restaurant_select = st.selectbox("Restoran Seçin", options=list(st.session_state.restoranlar.keys()))
    new_item = st.text_input("Yemek")
    new_price = st.number_input("Fiyat (TL)", min_value=0, value=0)
    if st.button("Menüye Ekle") and new_item and new_price > 0:
        st.session_state.restoranlar[restaurant_select][new_item] = new_price
        st.success(f"{new_item} menüye eklendi!")

# Ana sayfa - Sipariş verme
col1, col2 = st.columns([2, 1])

with col1:
    st.header("Sipariş Ver")
    isim = st.text_input("Adınız")
    secilen_restoran = st.selectbox("Restoran", options=list(st.session_state.restoranlar.keys()))

    if secilen_restoran:
        secilen_yemek = st.selectbox("Yemek", options=list(st.session_state.restoranlar[secilen_restoran].keys()))
        if secilen_yemek:
            fiyat = st.session_state.restoranlar[secilen_restoran][secilen_yemek]
            st.write(f"Fiyat: {fiyat} TL")

    not_girisi = st.text_input("Not (isteğe bağlı)")

    if st.button("Sipariş Ver") and isim:
        try:
            conn = get_connection()
            conn.execute('''
                INSERT INTO siparisler (tarih, isim, restoran, yemek, fiyat, not) 
                VALUES (?, ?, ?, ?, ?, ?)''', 
                ((datetime.now() + timedelta(hours=3)).strftime("%Y-%m-%d %H:%M"), isim, secilen_restoran, secilen_yemek, fiyat, not_girisi))
            conn.commit()
            conn.close()
            st.success("Siparişiniz alındı!")
        except sqlite3.OperationalError as e:
            st.error(f"OperationalError: {e}")

# Siparişleri görüntüleme
with col2:
    st.header("Günlük Siparişler")
    conn = get_connection()
    df = pd.read_sql_query('SELECT * FROM siparisler', conn)
    conn.close()

    if not df.empty:
        st.subheader("Kişi Bazlı Toplam")
        kisi_bazli = df.groupby('isim')['fiyat'].sum().reset_index()
        st.dataframe(kisi_bazli)

        col_a, col_b = st.columns(2)
        with col_a:
            excel_data = to_excel(df)
            st.download_button(
                label="📥 Tüm Siparişleri İndir",
                data=excel_data,
                file_name=f'siparisler_{datetime.now().strftime("%Y%m%d")}.xlsx',
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )

        with col_b:
            excel_data_summary = to_excel(kisi_bazli)
            st.download_button(
                label="📥 Özeti İndir",
                data=excel_data_summary,
                file_name=f'siparis_ozeti_{datetime.now().strftime("%Y%m%d")}.xlsx',
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )

        st.subheader("Tüm Siparişler")
        st.dataframe(df)

        toplam_tutar = df['fiyat'].sum()
        st.metric("Toplam Tutar", f"{toplam_tutar} TL")

        if st.button("Siparişleri Temizle"):
            conn = get_connection()
            conn.execute('DELETE FROM siparisler')
            conn.commit()
            conn.close()
            st.success("Tüm siparişler temizlendi!")
            st.experimental_rerun()
    else:
        st.info("Henüz sipariş bulunmamaktadır.")
