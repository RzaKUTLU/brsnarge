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
        conn = sqlite3.connect(DB_PATH)
        return conn
    except sqlite3.Error as e:
        st.error(f"Veritabanı bağlantı hatası: {e}")
        return None

# Siparişler tablosunu oluştur veya yeniden oluştur
def create_table(conn):
    try:
        # Varolan tabloyu sil
        conn.execute('DROP TABLE IF EXISTS siparisler')
        
        # Yeni tablo oluştur
        conn.execute('''
        CREATE TABLE siparisler (
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

# Diğer fonksiyonlar ve kod aynı kalacak (önceki örnekteki gibi)
# Sadece create_table fonksiyonu değiştirildi

# Ana script kısmında veritabanı bağlantısı ve tablo oluşturma
conn = get_db_connection()
if conn:
    create_table(conn)

# Geri kalan kod önceki örnekle aynı
