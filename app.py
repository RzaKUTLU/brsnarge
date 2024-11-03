import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
import io
import xlsxwriter
from datetime import timedelta

# SQLite veritabanı bağlantısı
conn = sqlite3.connect('siparisler.db')

# Siparişler tablosunu oluştur
def create_table():
    conn.execute('''
    CREATE TABLE IF NOT EXISTS siparisler (
        id INTEGER PRIMARY KEY,
        tarih TEXT,
        isim TEXT,
        restoran TEXT,
        yemek TEXT,
        fiyat REAL,
        not_ TEXT
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
        worksheet.set_column('F:F', 30)  # Not sütunu

        # Fiyat sütununa format uygula
        worksheet.set_column('E:E', 12, para_format)

    return output.getvalue()

[... rest of your existing code until the order placement section ...]

    if st.button("Sipariş Ver") and isim:
        # Yeni siparişi veritabanına ekle
        conn.execute('''
            INSERT INTO siparisler (tarih, isim, restoran, yemek, fiyat, not_) 
            VALUES (?, ?, ?, ?, ?, ?)''', 
            ((datetime.now() + timedelta(hours=3)).strftime("%Y-%m-%d %H:%M"), 
             isim, secilen_restoran, secilen_yemek, fiyat, not_girisi))
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

# Uygulamayı kapatırken veritabanı bağlantısını kapat
conn.close()
