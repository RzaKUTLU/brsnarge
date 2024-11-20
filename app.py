import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
import io
import xlsxwriter
import os

# Veritabanı dosyasının konumunu belirle
DB_PATH = 'siparisler.db'

# SQLite veritabanı bağlantısı
def get_db_connection():
    try:
        return sqlite3.connect(DB_PATH)
    except sqlite3.Error as e:
        st.error(f"Veritabanı bağlantı hatası: {e}")
        return None

# Siparişler tablosunu oluştur
def create_table(conn):
    try:
        conn.execute('''
        CREATE TABLE IF NOT EXISTS siparisler (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tarih TEXT,
            isim TEXT,
            restoran TEXT,
            yemek TEXT,
            adet INTEGER,
            birim_fiyat REAL,
            toplam_fiyat REAL,
            notlar TEXT
        )
        ''')
        conn.commit()
    except sqlite3.Error as e:
        st.error(f"Tablo oluşturma hatası: {e}")

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
        worksheet.set_column('B:B', 15)  # İsim sütunu
        worksheet.set_column('C:C', 15)  # Restoran sütunu
        worksheet.set_column('D:D', 15)  # Yemek sütunu
        worksheet.set_column('E:E', 10)  # Adet sütunu
        worksheet.set_column('F:F', 12)  # Birim Fiyat sütunu
        worksheet.set_column('G:G', 12)  # Toplam Fiyat sütunu
        worksheet.set_column('H:H', 12)  # Notlar sütunu

        # Fiyat sütunlarına format uygula
        worksheet.set_column('F:G', 12, para_format)

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
            'Lahmacun': 80,
            # Diğer menü öğeleri...
        },
        'Çalıkuşu Kirazlık': {
            'Tavuk Dürüm Ç.lavaş Döner(100gr)': 160,
            'Lahmacun': 70,
            # Diğer menü öğeleri...
        }
    }

# Veritabanı bağlantısını al ve tabloyu oluştur
conn = get_db_connection()
if conn:
    create_table(conn)

# Başlık
st.title("🍽️ Borsan Ar-Ge Yemek Sipariş Sistemi")

# Sidebar - Yeni Restoran ve Menü Ekleme
with st.sidebar:
    st.header("Restoran Yönetimi")

    # Yeni restoran ekleme
    new_restaurant = st.text_input("Yeni Restoran")
    if st.button("Restoran Ekle") and new_restaurant:
        if new_restaurant not in st.session_state.restoranlar:
            st.session_state.restoranlar[new_restaurant] = {}
            st.success(f"{new_restaurant} başarıyla eklendi!")
        else:
            st.error("Bu restoran zaten mevcut!")

    # Mevcut restorana yemek ekleme
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

    # Kullanıcı bilgileri ve sipariş formu
    isim = st.text_input("Adınız")
    secilen_restoran = st.selectbox("Restoran", options=list(st.session_state.restoranlar.keys()))

    if secilen_restoran:
        secilen_yemek = st.selectbox(
            "Yemek",
            options=list(st.session_state.restoranlar[secilen_restoran].keys())
        )

        if secilen_yemek:
            birim_fiyat = st.session_state.restoranlar[secilen_restoran][secilen_yemek]
            adet = st.number_input("Adet", min_value=1, value=1)
            toplam_fiyat = birim_fiyat * adet
            st.write(f"Birim Fiyat: {birim_fiyat} TL")
            st.write(f"Toplam Fiyat: {toplam_fiyat} TL")

    not_girisi = st.text_input("Not (isteğe bağlı)")

    if st.button("Sipariş Ver") and isim and secilen_yemek and conn:
        try:
            # Yeni siparişi veritabanına ekle
            conn.execute('''
                INSERT INTO siparisler (tarih, isim, restoran, yemek, adet, birim_fiyat, toplam_fiyat, notlar) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', 
                ((datetime.now() + timedelta(hours=3)).strftime("%Y-%m-%d %H:%M"), 
                 isim, secilen_restoran, secilen_yemek, adet, birim_fiyat, toplam_fiyat, not_girisi))
            conn.commit()
            st.success("Siparişiniz alındı!")
        except sqlite3.Error as e:
            st.error(f"Sipariş kaydedilemedi: {e}")

# Siparişleri görüntüleme
with col2:
    st.header("Günlük Siparişler")
    
    # Veritabanından tüm siparişleri oku
    if conn:
        try:
            df = pd.read_sql_query('SELECT * FROM siparisler', conn)

            if not df.empty:
                # Kişi bazlı toplam tutarlar
                st.subheader("Kişi Bazlı Toplam")
                kisi_bazli = df.groupby('isim').agg({
                    'adet': 'sum', 
                    'toplam_fiyat': 'sum'
                }).reset_index()
                kisi_bazli.columns = ['İsim', 'Toplam Adet', 'Toplam Tutar']
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
                
                # Sipariş ID'lerini içeren bir dropdown oluştur
                selected_order_id = st.selectbox("Silmek için sipariş ID'sini seçin", options=df['id'].tolist())

                if st.button("Sil"):
                    if selected_order_id:
                        try:
                            conn.execute('DELETE FROM siparisler WHERE id = ?', (selected_order_id,))
                            conn.commit()
                            st.success(f"{selected_order_id} ID'li sipariş silindi!")
                            st.experimental_rerun()
                        except sqlite3.Error as e:
                            st.error(f"Sipariş silinemedi: {e}")
                    else:
                        st.warning("Silmek için bir sipariş seçmelisiniz.")

                # Tüm siparişleri göster
                st.dataframe(df[['id', 'tarih', 'isim', 'restoran', 'yemek', 'adet', 'birim_fiyat', 'toplam_fiyat', 'notlar']])

                # Toplam tutar ve toplam adet
                toplam_tutar = df['toplam_fiyat'].sum()
                toplam_adet = df['adet'].sum()
                col_toplam_tutar, col_toplam_adet = st.columns(2)
                
                with col_toplam_tutar:
                    st.metric("Toplam Tutar", f"{toplam_tutar} TL")
                
                with col_toplam_adet:
                    st.metric("Toplam Adet", f"{toplam_adet}")

                # Siparişleri temizleme butonu
                if st.button("Siparişleri Temizle"):
                    try:
                        conn.execute('DELETE FROM siparisler')
                        conn.commit()
                        st.success("Tüm siparişler temizlendi!")
                        st.experimental_rerun()
                    except sqlite3.Error as e:
                        st.error(f"Siparişler temizlenemedi: {e}")
            else:
                st.info("Henüz sipariş bulunmamaktadır.")
        except sqlite3.Error as e:
            st.error(f"Siparişler görüntülenemedi: {e}")
    else:
        st.error("Veritabanı bağlantısı kurulamadı.")

# Uygulama kapandığında veritabanı bağlantısını kapat
if conn:
    conn.close()
