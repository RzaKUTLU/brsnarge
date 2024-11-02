import streamlit as st
import pandas as pd
from datetime import datetime
import io
import os

# CSV file path
CSV_FILE = 'siparisler.csv'

# Ensure the CSV file exists
if not os.path.exists(CSV_FILE):
    pd.DataFrame(columns=['Tarih', 'İsim', 'Restoran', 'Yemek', 'Fiyat']).to_csv(CSV_FILE, index=False)

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
        worksheet.set_column('D:D', 20)  # Yemek sütunu
        worksheet.set_column('E:E', 12)  # Fiyat sütunu

        # Fiyat sütununa format uygula
        worksheet.set_column('E:E', 12, para_format)

    return output.getvalue()

# Sayfa yapılandırması
st.set_page_config(page_title="Ben Borsan Yemek Sipariş Sistemi", layout="wide")

# Restoranlar ve siparişler
if 'restoranlar' not in st.session_state:
    st.session_state.restoranlar = {
        'Pide Salonu': {
            'Kıymalı Pide': 120,
            'Kaşarlı Pide': 110,
            'Kuşbaşılı Pide': 130,
            'Kola': 30,
            'Ayran': 20
        },
        'Kebapçı': {
            'Adana Kebap': 160,
            'Urfa Kebap': 150,
            'Lahmacun': 50,
            'Kola': 30,
            'Ayran': 20
        },
        'Ev Yemekleri': {
            'Kuru Fasulye': 80,
            'Pilav': 40,
            'Mercimek Çorbası': 35,
            'Kola': 30,
            'Ayran': 20
        }
    }

# Başlık
st.title("🍽️ Ben Borsan Yemek Sipariş Sistemi")

# Sidebar - Yeni Restoran ve Menü Ekleme
with st.sidebar:
    st.header("Restoran Yönetimi")

    new_restaurant = st.text_input("Yeni Restoran Adı")
    if st.button("Restoran Ekle") and new_restaurant:
        if new_restaurant not in st.session_state.restoranlar:
            st.session_state.restoranlar[new_restaurant] = {}
            st.success(f"{new_restaurant} başarıyla eklendi!")
        else:
            st.error("Bu restoran zaten mevcut!")

    # Mevcut restorana yemek ekleme
    st.subheader("Menü Yönetimi")
    restaurant_select = st.selectbox("Restoran Seçin", options=list(st.session_state.restoranlar.keys()))

    new_item = st.text_input("Yemek Adı")
    new_price = st.number_input("Fiyat (TL)", min_value=0, value=0)

    if st.button("Menüye Ekle") and new_item and new_price > 0:
        st.session_state.restoranlar[restaurant_select][new_item] = new_price
        st.success(f"{new_item} menüye eklendi!")

# Ana sayfa - Sipariş verme
col1, col2 = st.columns([2, 1])

with col1:
    st.header("Sipariş Ver")

    isim = st.text_input("Adınız", max_chars=15)
    secilen_restoran = st.selectbox("Restoran", options=list(st.session_state.restoranlar.keys()))

    if secilen_restoran:
        secilen_yemek = st.selectbox("Yemek", options=list(st.session_state.restoranlar[secilen_restoran].keys()))

        if secilen_yemek:
            fiyat = st.session_state.restoranlar[secilen_restoran][secilen_yemek]
            st.write(f"Fiyat: {fiyat} TL")

            if st.button("Sipariş Ver") and isim:
                yeni_siparis = {
                    'Tarih': datetime.now().strftime("%Y-%m-%d %H:%M"),
                    'İsim': isim,
                    'Restoran': secilen_restoran,
                    'Yemek': secilen_yemek,
                    'Fiyat': fiyat
                }
                # Siparişi CSV'ye ekle
                df = pd.read_csv(CSV_FILE)
                df = df.append(yeni_siparis, ignore_index=True)
                df.to_csv(CSV_FILE, index=False)

                st.success("Siparişiniz alındı!")

# Siparişleri görüntüleme
with col2:
    st.header("Günlük Siparişler")
    df = pd.read_csv(CSV_FILE)

    if not df.empty:
        # Kişi bazlı toplam tutarlar
        st.subheader("Kişi Bazlı Toplam")
        kisi_bazli = df.groupby('İsim')['Fiyat'].sum().reset_index()
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
        toplam_tutar = df['Fiyat'].sum()
        st.metric("Toplam Tutar", f"{toplam_tutar} TL")
    else:
        st.info("Henüz sipariş bulunmamaktadır.")
