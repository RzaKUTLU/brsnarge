import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
import io
import xlsxwriter
import os

# Initialize connection.
def init_db():
    # Ensure the database directory exists
    db_dir = "data"
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)
    
    db_path = os.path.join(db_dir, "siparisler.db")
    return sqlite3.connect(db_path, check_same_thread=False)

# Create connection object in session state
if 'conn' not in st.session_state:
    st.session_state.conn = init_db()

# Create tables function
def create_table():
    try:
        cursor = st.session_state.conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS siparisler (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tarih TEXT NOT NULL,
            isim TEXT NOT NULL,
            restoran TEXT NOT NULL,
            yemek TEXT NOT NULL,
            fiyat REAL NOT NULL,
            not_ TEXT
        )
        ''')
        st.session_state.conn.commit()
    except sqlite3.Error as e:
        st.error(f"Veritabanı hatası: {e}")
    finally:
        cursor.close()

# Excel download function
def to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Siparişler', index=False)
        workbook = writer.book
        worksheet = writer.sheets['Siparişler']

        # Format settings
        para_format = workbook.add_format({'num_format': '#,##0.00 ₺'})
        tarih_format = workbook.add_format({'num_format': 'dd/mm/yyyy hh:mm'})

        # Column widths
        worksheet.set_column('A:A', 20)  # Tarih
        worksheet.set_column('B:B', 15)  # İsim
        worksheet.set_column('C:C', 15)  # Restoran
        worksheet.set_column('D:D', 20)  # Yemek
        worksheet.set_column('E:E', 12, para_format)  # Fiyat
        worksheet.set_column('F:F', 30)  # Not

    return output.getvalue()

# Page config
st.set_page_config(page_title="Borsan Ar-Ge Yemek Sipariş Sistemi", layout="wide")

# Initialize session state for restaurants
if 'restoranlar' not in st.session_state:
    st.session_state.restoranlar = {
        'Nazar Petrol': {
            'Adana Dürüm': 170,
            'Adana Porsiyon': 240,
            # ... (rest of the menu items remain the same)
        },
        'Çalıkuşu Kirazlık': {
            'Tavuk Dürüm Ç.lavaş Döner(100gr)': 160,
            'Tavuk Dürüm Döner(50gr)': 80,
            # ... (rest of the menu items remain the same)
        }
    }

# Create tables
create_table()

# Title
st.title("🍽️ Borsan Ar-Ge Yemek Sipariş Sistemi")

# Sidebar - Restaurant Management
with st.sidebar:
    st.header("Restoran Yönetimi")

    # Add new restaurant
    new_restaurant = st.text_input("Yeni Restoran")
    if st.button("Restoran Ekle") and new_restaurant:
        if new_restaurant not in st.session_state.restoranlar:
            st.session_state.restoranlar[new_restaurant] = {}
            st.success(f"{new_restaurant} başarıyla eklendi!")
        else:
            st.error("Bu restoran zaten mevcut!")

    # Add menu items
    st.subheader("Menü Yönetimi")
    restaurant_select = st.selectbox("Restoran Seçin", options=list(st.session_state.restoranlar.keys()))

    new_item = st.text_input("Yemek")
    new_price = st.number_input("Fiyat (TL)", min_value=0, value=0)

    if st.button("Menüye Ekle") and new_item and new_price > 0:
        st.session_state.restoranlar[restaurant_select][new_item] = new_price
        st.success(f"{new_item} menüye eklendi!")

# Main page - Order placement
col1, col2 = st.columns([2, 1])

with col1:
    st.header("Sipariş Ver")

    # Order form
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
        try:
            cursor = st.session_state.conn.cursor()
            cursor.execute('''
                INSERT INTO siparisler (tarih, isim, restoran, yemek, fiyat, not_) 
                VALUES (?, ?, ?, ?, ?, ?)
                ''', 
                ((datetime.now() + timedelta(hours=3)).strftime("%Y-%m-%d %H:%M"), 
                 isim, secilen_restoran, secilen_yemek, fiyat, not_girisi))
            st.session_state.conn.commit()
            st.success("Siparişiniz alındı!")
        except sqlite3.Error as e:
            st.error(f"Sipariş kaydedilirken bir hata oluştu: {e}")
        finally:
            cursor.close()

# Order display
with col2:
    st.header("Günlük Siparişler")
    try:
        # Read orders from database
        df = pd.read_sql_query('''
            SELECT tarih, isim, restoran, yemek, fiyat, not_
            FROM siparisler
            WHERE DATE(tarih) = DATE('now', '+3 hours')
            ORDER BY tarih DESC
        ''', st.session_state.conn)

        if not df.empty:
            # Person-based totals
            st.subheader("Kişi Bazlı Toplam")
            kisi_bazli = df.groupby('isim')['fiyat'].sum().reset_index()
            st.dataframe(kisi_bazli)

            # Excel download buttons
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
                excel_kisi_data = to_excel(kisi_bazli)
                st.download_button(
                    label="📥 Kişi Bazlı Toplamları İndir",
                    data=excel_kisi_data,
                    file_name=f'kisi_toplamlari_{datetime.now().strftime("%Y%m%d")}.xlsx',
                    mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )
        else:
            st.info("Bugün için henüz sipariş bulunmamaktadır.")
    except sqlite3.Error as e:
        st.error(f"Siparişler yüklenirken bir hata oluştu: {e}")
