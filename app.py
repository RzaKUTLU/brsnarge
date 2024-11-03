import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
import io
import xlsxwriter

# SQLite veritabanı bağlantısı
conn = sqlite3.connect('siparisler.db')

# Siparişler tablosunu oluştur
def create_table():
    conn.execute('''
    CREATE TABLE IF NOT EXISTS siparisler (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tarih TEXT,
        isim TEXT,
        restoran TEXT,
        yemek TEXT,
        fiyat REAL,
        notlar TEXT
    )
    ''')
    conn.execute('''
    CREATE TABLE IF NOT EXISTS restoranlar (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        isim TEXT UNIQUE
    )
    ''')
    conn.execute('''
    CREATE TABLE IF NOT EXISTS menuler (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        restoran_id INTEGER,
        yemek TEXT,
        fiyat REAL,
        FOREIGN KEY (restoran_id) REFERENCES restoranlar(id)
    )
    ''')
    conn.commit()

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
        tarih_format = workbook.add_format({'num_format': 'dd/mm/yyyy hh:mm'})

        # Sütun genişliklerini ayarla
        worksheet.set_column('A:A', 20)  # Tarih sütunu
        worksheet.set_column('B:B', 10)  # İsim sütunu
        worksheet.set_column('C:C', 10)  # Restoran sütunu
        worksheet.set_column('D:D', 15)  # Yemek sütunu
        worksheet.set_column('E:E', 12)  # Fiyat sütunu
        worksheet.set_column('F:F', 12)  # Notlar sütunu

        # Fiyat sütununa format uygula
        worksheet.set_column('E:E', 12, para_format)

    return output.getvalue()

# Sayfa yapılandırması
st.set_page_config(page_title="Borsan Ar-Ge Yemek Sipariş Sistemi", layout="wide")

# Restoranları ve menüleri yükle
def load_restaurants_and_menus():
    restoranlar_df = pd.read_sql_query('SELECT * FROM restoranlar', conn)
    menuler_df = pd.read_sql_query('SELECT * FROM menuler', conn)

    restoranlar = {row['isim']: {} for index, row in restoranlar_df.iterrows()}
    for index, row in menuler_df.iterrows():
        restoran = restoranlar_df.loc[restoranlar_df['id'] == row['restoran_id']]
        if not restoran.empty:
            restoran_isim = restoran.iloc[0]['isim']
            restoranlar[restoran_isim][row['yemek']] = row['fiyat']

    return restoranlar

if 'restoranlar' not in st.session_state:
    st.session_state.restoranlar = load_restaurants_and_menus()

# Başlık
st.title("🍽️ Borsan Ar-Ge Yemek Sipariş Sistemi")

# Sidebar - Yeni Restoran ve Menü Ekleme
with st.sidebar:
    st.header("Restoran Yönetimi")

    # Yeni restoran ekleme
    new_restaurant = st.text_input("Yeni Restoran")
    if st.button("Restoran Ekle") and new_restaurant:
        try:
            conn.execute('INSERT INTO restoranlar (isim) VALUES (?)', (new_restaurant,))
            conn.commit()
            st.session_state.restoranlar[new_restaurant] = {}
            st.success(f"{new_restaurant} başarıyla eklendi!")
        except sqlite3.IntegrityError:
            st.error("Bu restoran zaten mevcut!")

    # Mevcut restorana yemek ekleme
    st.subheader("Menü Yönetimi")
    restaurant_select = st.selectbox("Restoran Seçin", options=list(st.session_state.restoranlar.keys()))

    new_item = st.text_input("Yemek")
    new_price = st.number_input("Fiyat (TL)", min_value=0, value=0)

    if st.button("Menüye Ekle") and new_item and new_price > 0:
        restoran_id = pd.read_sql_query('SELECT id FROM restoranlar WHERE isim = ?', (restaurant_select,)).iloc[0]['id']
        conn.execute('INSERT INTO menuler (restoran_id, yemek, fiyat) VALUES (?, ?, ?)', (restoran_id, new_item, new_price))
        conn.commit()
        st.session_state.restoranlar[restaurant_select][new_item] = new_price
        st.success(f"{new_item} menüye eklendi!")

# Ana sayfa - Sipariş verme
col1, col2 = st.columns([2, 1])

with col1:
    st.header("Sipariş Ver")

    # Kullanıcı bilgileri ve sipariş formu
    isim = st.text_input("Adınız")
    secilen_restoran = st.selectbox("Restoran", options=list(st.session_state.restoranlar.keys()))

    if secilen_restoran:
        secilen_yemek = st.selectbox(
            "Yemek",
            options=list(st.session_state.restoranlar[secilen_restoran].keys())
        )

        if secilen_yemek:
            fiyat = st.session_state.restoranlar[secilen_restoran][secilen_yemek]
            st.write(f"Fiyat: {fiyat} TL")

    not_girisi = st.text_input("Not (isteğe bağlı)")

    if st.button("Sipariş Ver") and isim:
        # Yeni siparişi veritabanına ekle
        conn.execute('''
            INSERT INTO siparisler (tarih, isim, restoran, yemek, fiyat, notlar) 
            VALUES (?, ?, ?, ?, ?, ?)''', 
            ((datetime.now() + timedelta(hours=3)).strftime("%Y-%m-%d %H:%M"), isim, secilen_restoran, secilen_yemek, fiyat, not_girisi))
        conn.commit()
        st.success("Siparişiniz alındı!")

# Siparişleri görüntüleme
with col2:
    st.header("Günlük Siparişler")
    # Veritabanından tüm siparişleri oku
    df = pd.read_sql_query('SELECT * FROM siparisler', conn)

    if not df.empty:
        # Kişi bazlı toplam tutarlar
        st.subheader("Kişi Bazlı Toplam")
        kisi_bazli = df.groupby('isim')['fiyat'].sum().reset_index()
        st.dataframe(kisi_bazli)

        # Excel indirme butonları
        col_a, col_b = st.columns(2)

        with col_a:
            # Tüm siparişlerin Excel'i
            excel_data = to_excel(df)
            st.download_button(
                label="📥 Tüm Siparişleri İndir",
                data=excel_data,
                file_name=f'siparisler_{datetime.now().strftime("%Y%m%d")}.xlsx',
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )

        with col_b:
            # Kişi bazlı toplamların Excel'i
            excel_data_summary = to_excel(kisi_bazli)
            st.download_button(
                label="📥 Özeti İndir",
                data=excel_data_summary,
                file_name=f'siparis_ozeti_{datetime.now().strftime("%Y%m%d")}.xlsx',
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )

        # Tüm siparişler
        st.subheader("Tüm Siparişler")
        st.dataframe(df)

        # Toplam tutar
        toplam_tutar = df['fiyat'].sum()
        st.metric("Toplam Tutar", f"{toplam_tutar} TL")

        # Siparişleri temizleme butonu
        if st.button("Siparişleri Temizle"):
            conn.execute('DELETE FROM siparisler')
            conn.commit()
            st.success("Tüm siparişler temizlendi!")
            st.experimental_rerun()
    else:
        st.info("Henüz sipariş bulunmamaktadır.")
