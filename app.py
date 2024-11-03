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

# Restoranları sakla
if 'restoranlar' not in st.session_state:
    st.session_state.restoranlar = {
        'Nazar Petrol': {
            'Adana Dürüm': 170,
            'Adana Porsiyon': 240,
            'Tavuk Dürüm': 155,
            'Kanat Porsiyon': 200,
            'Tavuk Porsiyon': 150,
            'Yarım Tavuk': 130,
            'Yarım Çeyrek Tavuk': 150,
            'Bütün Ekmek Tavuk': 170,
            'Ciğer Dürüm': 170,
            'Ciğer Porsiyon': 240,
            'Et Dürüm': 190,
            'Et Porsiyon': 270,
            'Köfte Porsiyon': 240,
            'Yarım Köfte': 170,
            'Yarım Çeyrek Köfte': 170,
            'Bütün Köfte': 190,
            'Kapalı Pide': 90,
            'Lahmacun': 80,
            'Açık Kıymalı': 170,
            'Açık Kaşarlı': 180,
            'Açık Karışık': 220,
            'Açık Sucuklu': 230,
            'Açık Pastırmalı': 230,
            'Açık Beyaz Peynirli': 190,
            'Kapalı Beyaz Peynirli': 170,
            'Yağlı': 140,
            'Extra Lavaş': 10,
            'Extra Yumurta': 10,
            'Extra Kaşar': 25,
            'Çoban Salata': 30,
            'Ezme': 20,
            'Patlıcan Salatası': 50,
            'Tropicana M. Suyu': 35,
            '2.5 Lt Kola': 70,
            '1 Lt Kola': 50,
            'Kutu Kola': 35,
            'Şalgam': 30,
            'Şişe Kola': 50,
            '1 Lt Fanta': 50,
            '2.5 Lt Fanta': 70,
            'Kutu Fanta': 30,
            'Sprite': 30,
            'Şişe Zero': 40,
            'Türk Kahvesi': 40,
            'Su': 5,
            'Çay': 10,
            'Ice Tea Şeftali': 35,
            'Açık Ayran': 35,
            'Ayran Pet': 35,
            'Ayran Şişe': 35,
            'Portakal Suyu': 35,
            'Künefe': 85,
            'Sütlaç': 75,
            'Katmer': 75
            # ... diğer yemekler
        },
        'Çalıkuşu Kirazlık': {
            'Tavuk Dürüm Ç.lavaş Döner(100gr)': 160,
            'Tavuk Dürüm Döner(50gr)': 80,
            'Et Dürüm Döner': 140,
            'Pepsi kola kutu': 40,
            'Kola': 30,
            'Ayran': 25,
            'Ice tea şeftali': 40
        }
    }

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
